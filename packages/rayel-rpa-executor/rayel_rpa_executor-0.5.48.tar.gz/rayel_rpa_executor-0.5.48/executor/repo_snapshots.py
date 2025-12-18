"""
RPA 代码快照管理（快照目录 + current symlink + 引用计数）。

目标：
- 更新线程在后台构建新快照目录，成功后原子切换 `{workspace_root}/rpa_projects` symlink。
- 任务执行时只在开始读取 current，并固定到真实快照目录（lease），避免执行期间版本撕裂。
- 旧快照仅在引用计数为 0 且非 current 时清理。
"""

from __future__ import annotations

import contextlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from executor.logger import logger
from executor.git_manager import (
    snapshot_archive_export,
    snapshot_ensure_mirror_repo,
    snapshot_fetch_branch,
    snapshot_rev_parse,
)

try:
    import fcntl  # type: ignore
except Exception:  # pragma: no cover
    fcntl = None


SNAPSHOT_COMMIT_FILE = ".snapshot_commit"


@dataclass(frozen=True)
class RepoLease:
    workspace_root: Path
    commit: str
    repo_root: Path  # 真实快照目录路径


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


@contextlib.contextmanager
def _file_lock(lock_file: Path):
    """
    进程级文件锁（同机多进程/多线程安全）。
    - Linux / macOS: 使用 flock
    - 其他平台：退化为无锁（当前执行器主要部署在 Linux/macOS）
    """
    _ensure_dir(lock_file.parent)
    f = open(lock_file, "a+")
    try:
        if fcntl is not None:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        try:
            if fcntl is not None:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass
        try:
            f.close()
        except Exception:
            pass


def _is_ssh_url(git_url: str) -> bool:
    return git_url.startswith(("git@", "ssh://"))


def _inject_token_to_url(git_url: str, git_token: str) -> str:
    """
    将 token 注入到 HTTPS Git URL。
    - GitHub: https://{token}@github.com/...
    - GitLab: https://oauth2:{token}@gitlab.com/...
    """
    if not git_url.startswith(("https://", "http://")):
        return git_url
    if not git_token:
        return git_url

    is_github = "github.com" in git_url.lower()
    if is_github:
        if git_url.startswith("https://"):
            return git_url.replace("https://", f"https://{git_token}@")
        return git_url.replace("http://", f"http://{git_token}@")

    if git_url.startswith("https://"):
        return git_url.replace("https://", f"https://oauth2:{git_token}@")
    return git_url.replace("http://", f"http://oauth2:{git_token}@")


def _run(cmd: list[str], cwd: Optional[Path] = None, timeout: int = 300) -> subprocess.CompletedProcess:
    """
    执行子进程，失败抛异常（由上层捕获并降级）。
    """
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        check=True,
    )


def _git_url_for_fetch(git_url: str, git_token: str) -> str:
    if _is_ssh_url(git_url):
        return git_url
    return _inject_token_to_url(git_url, git_token)


def _write_snapshot_commit(snapshot_dir: Path, commit: str) -> None:
    (snapshot_dir / SNAPSHOT_COMMIT_FILE).write_text(commit + "\n", encoding="utf-8")


def _read_snapshot_commit(snapshot_dir: Path) -> str:
    p = snapshot_dir / SNAPSHOT_COMMIT_FILE
    if p.exists():
        return p.read_text(encoding="utf-8", errors="ignore").strip()
    # 兜底：如果目录本身是一个 git repo
    try:
        return _run(["git", "rev-parse", "HEAD"], cwd=snapshot_dir, timeout=30).stdout.strip()
    except Exception:
        return "unknown"


def _archive_export(mirror_dir: Path, commit: str, target_dir: Path) -> None:
    snapshot_archive_export(mirror_dir, commit, target_dir)
    _write_snapshot_commit(target_dir, commit)


def _revs_dir(workspace_root: Path) -> Path:
    return workspace_root / ".rpa_projects_revs"


def _refs_dir(workspace_root: Path) -> Path:
    return workspace_root / ".rpa_projects_refs"


def _ref_lock_file(workspace_root: Path) -> Path:
    return _refs_dir(workspace_root) / ".lock"


def _ref_file(workspace_root: Path, commit: str) -> Path:
    return _refs_dir(workspace_root) / f"{commit}.json"


def _load_ref_state(workspace_root: Path, commit: str) -> dict:
    p = _ref_file(workspace_root, commit)
    if not p.exists():
        return {"refcount": 0, "last_used_at": 0}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"refcount": 0, "last_used_at": 0}


def _save_ref_state(workspace_root: Path, commit: str, state: dict) -> None:
    _ensure_dir(_refs_dir(workspace_root))
    p = _ref_file(workspace_root, commit)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, p)


def _inc_ref(workspace_root: Path, commit: str) -> int:
    with _file_lock(_ref_lock_file(workspace_root)):
        st = _load_ref_state(workspace_root, commit)
        st["refcount"] = int(st.get("refcount", 0)) + 1
        st["last_used_at"] = int(time.time())
        _save_ref_state(workspace_root, commit, st)
        return st["refcount"]


def _dec_ref(workspace_root: Path, commit: str) -> int:
    with _file_lock(_ref_lock_file(workspace_root)):
        st = _load_ref_state(workspace_root, commit)
        st["refcount"] = max(0, int(st.get("refcount", 0)) - 1)
        st["last_used_at"] = int(time.time())
        _save_ref_state(workspace_root, commit, st)
        return st["refcount"]


def _ensure_current_is_symlink(workspace_root: Path, current_link: Path) -> None:
    """
    初始化/迁移：
    - 如果 current_link 不存在：由刷新线程/任务路径后续创建。
    - 如果 current_link 是目录（历史 clone 目录）：不在这里做 destructive 操作；
      由 initialize_from_existing_dir() 处理迁移。
    """
    if not current_link.exists():
        return
    if current_link.is_symlink():
        return
    # 是普通目录：留给迁移函数显式处理
    return


def _snapshot_lock_file(workspace_root: Path) -> Path:
    return workspace_root / ".rpa_projects_snapshot.lock"


def initialize_from_existing_dir(workspace_root: Path) -> None:
    """
    首次迁移：把 `{workspace_root}/rpa_projects` 从“目录”变成“symlink 指向快照”。
    - 不会删除旧目录：会备份到 `.tmp/` 下。
    - 如果已是 symlink，直接返回。
    """
    current_link = workspace_root / "rpa_projects"
    with _file_lock(_snapshot_lock_file(workspace_root)):
        if not current_link.exists():
            return
        if current_link.is_symlink():
            return
        if not current_link.is_dir():
            return

        # 读取当前目录的 commit（要求是一个 git repo）
        try:
            commit = _run(["git", "rev-parse", "HEAD"], cwd=current_link, timeout=30).stdout.strip()
        except Exception as e:
            logger.LOCAL.warning(f"[快照] 迁移失败：现有 rpa_projects 不是 git repo 或无法读取 commit: {e}")
            return

        revs = _revs_dir(workspace_root)
        snapshot_dir = revs / commit
        if not snapshot_dir.exists():
            logger.LOCAL.info(f"[快照] 迁移现有目录为快照: commit={commit[:8]}")
            # 用现有 repo 直接 archive 导出，避免把 .git 带入快照
            _ensure_dir(workspace_root / ".tmp")
            with tempfile.TemporaryDirectory(dir=str(workspace_root / ".tmp")) as td:
                tmp_out = Path(td) / "export"
                _ensure_dir(tmp_out)
                # 使用当前目录执行 git archive
                import tarfile

                proc = subprocess.Popen(
                    ["git", "archive", "--format=tar", commit],
                    cwd=str(current_link),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                assert proc.stdout is not None
                with tarfile.open(fileobj=proc.stdout, mode="r|") as tf:
                    tf.extractall(path=str(tmp_out))
                stderr = (proc.stderr.read() if proc.stderr else b"").decode("utf-8", errors="ignore")
                code = proc.wait(timeout=300)
                if code != 0:
                    raise RuntimeError(f"git archive 失败: {stderr}")

                _write_snapshot_commit(tmp_out, commit)
                _ensure_dir(revs)
                os.replace(tmp_out, snapshot_dir)

        # 备份旧目录
        backup = workspace_root / ".tmp" / f"rpa_projects_legacy_{int(time.time())}"
        _ensure_dir(backup.parent)
        shutil.move(str(current_link), str(backup))
        logger.LOCAL.info(f"[快照] 已备份旧 rpa_projects 到: {backup}")

        # 创建 symlink 指向快照
        _atomic_switch_symlink(current_link, snapshot_dir)
        logger.LOCAL.info(f"[快照] current 已切换到快照: {snapshot_dir}")


def _atomic_switch_symlink(current_link: Path, target_dir: Path) -> None:
    """
    原子切换 symlink：current_link -> target_dir
    """
    _ensure_dir(current_link.parent)
    tmp_link = current_link.parent / f".rpa_projects_tmp_{os.getpid()}_{int(time.time()*1000)}"
    # 重要：symlink 目标必须是“对 link 所在目录正确可解析”的路径。
    # 如果传入如 "workspace/.rpa_projects_revs/..." 这种相对路径，
    # symlink 会被解析为 "workspace/workspace/..." 导致断链。
    os.symlink(str(target_dir.resolve()), str(tmp_link))
    os.replace(str(tmp_link), str(current_link))


def resolve_current_snapshot(workspace_root: Path) -> Tuple[str, Path]:
    """
    返回 (commit, repo_root_real_path)
    - repo_root_real_path 是实际快照目录路径（非 symlink）。
    """
    workspace_root = workspace_root.resolve()
    current_link = workspace_root / "rpa_projects"
    _ensure_current_is_symlink(workspace_root, current_link)

    # 注意：Path.exists() 会跟随 symlink；如果 symlink 断链会返回 False。
    if not os.path.lexists(current_link):
        raise FileNotFoundError(f"current 不存在: {current_link}")

    # Path.resolve() 会解析 symlink
    real_root = current_link.resolve()
    commit = _read_snapshot_commit(real_root)
    return commit, real_root


def acquire(
    *,
    workspace_root: Path,
    git_url: Optional[str] = None,
    git_token: str = "",
    branch: str = "main",
) -> RepoLease:
    """
    获取当前快照租约（refcount +1），并返回固定 repo_root。
    - 若 current 尚未初始化且提供了 git_url，则会尝试构建一次并切换（失败则抛出）。
    """
    workspace_root = workspace_root.resolve()
    initialize_from_existing_dir(workspace_root)

    # 如果 current 不存在，尝试初始化
    current_link = workspace_root / "rpa_projects"
    if not current_link.exists():
        if not git_url:
            raise FileNotFoundError(f"current 不存在且未提供 git_url: {current_link}")
        # 直接尝试更新一次
        changed = try_update(workspace_root=workspace_root, git_url=git_url, git_token=git_token, branch=branch)
        if not changed and not current_link.exists():
            raise FileNotFoundError(f"无法初始化 current: {current_link}")

    commit, repo_root = resolve_current_snapshot(workspace_root)
    ref = _inc_ref(workspace_root, commit)
    logger.LOCAL.debug(f"[快照] acquire: commit={commit[:8]} refcount={ref} repo_root={repo_root}")
    return RepoLease(workspace_root=workspace_root, commit=commit, repo_root=repo_root)


def release(lease: RepoLease) -> None:
    ref = _dec_ref(lease.workspace_root, lease.commit)
    logger.LOCAL.debug(f"[快照] release: commit={lease.commit[:8]} refcount={ref}")


def try_update(*, workspace_root: Path, git_url: str, git_token: str = "", branch: str = "main") -> bool:
    """
    尝试更新到远端最新 commit：
    - 成功构建新快照并切换 current：返回 True
    - 远端无变化/失败：返回 False（失败仅记录日志，不抛出）
    """
    try:
        workspace_root = workspace_root.resolve()
        initialize_from_existing_dir(workspace_root)
        with _file_lock(_snapshot_lock_file(workspace_root)):
            mirror = snapshot_ensure_mirror_repo(workspace_root, git_url, git_token)
            snapshot_fetch_branch(mirror, git_url, git_token, branch)
            remote_commit = snapshot_rev_parse(mirror, f"origin/{branch}")

            revs = _revs_dir(workspace_root)
            _ensure_dir(revs)
            snapshot_dir = revs / remote_commit
            if not snapshot_dir.exists():
                # 构建新快照：先导出到临时目录，成功后原子 rename 到最终目录
                _ensure_dir(workspace_root / ".tmp")
                with tempfile.TemporaryDirectory(dir=str(workspace_root / ".tmp")) as td:
                    tmp_out = Path(td) / "export"
                    _archive_export(mirror, remote_commit, tmp_out)
                    os.replace(tmp_out, snapshot_dir)
                logger.LOCAL.info(f"[快照] 新快照已构建: commit={remote_commit[:8]} dir={snapshot_dir}")

            # 切换 current（如果已经是该 commit 则跳过）
            current_link = workspace_root / "rpa_projects"
            if current_link.exists() and current_link.is_symlink():
                current_real = current_link.resolve()
                current_commit = _read_snapshot_commit(current_real)
                if current_commit == remote_commit:
                    return False

            _atomic_switch_symlink(current_link, snapshot_dir)
            logger.LOCAL.info(f"[快照] current 已原子切换: commit={remote_commit[:8]}")
            return True
    except Exception as e:
        logger.LOCAL.warning(f"[快照] 更新失败（忽略，不影响任务）: {e}")
        return False


def cleanup(*, workspace_root: Path, keep_min: int = 2) -> int:
    """
    清理旧快照（引用计数为 0 且不是 current），至少保留 keep_min 个快照。
    Returns: 删除的快照数量
    """
    keep_min = max(1, int(keep_min))
    workspace_root = workspace_root.resolve()
    try:
        current_commit, _ = resolve_current_snapshot(workspace_root)
    except Exception:
        current_commit = "unknown"

    revs = _revs_dir(workspace_root)
    if not revs.exists():
        return 0

    # 按目录 mtime 排序，保留最新 keep_min 个
    snapshots = [p for p in revs.iterdir() if p.is_dir()]
    snapshots.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    protected = {current_commit}
    protected_dirs = set(snapshots[:keep_min])

    deleted = 0
    with _file_lock(_ref_lock_file(workspace_root)):
        for snap in snapshots:
            commit = snap.name
            if commit in protected:
                continue
            if snap in protected_dirs:
                continue
            st = _load_ref_state(workspace_root, commit)
            if int(st.get("refcount", 0)) > 0:
                continue
            try:
                shutil.rmtree(snap)
                deleted += 1
                logger.LOCAL.info(f"[快照] 已清理旧快照: commit={commit[:8]} dir={snap}")
            except Exception as e:
                logger.LOCAL.warning(f"[快照] 清理失败（忽略）: {snap} err={e}")
    return deleted



