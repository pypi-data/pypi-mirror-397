"""
Git 快照构建工具（方案2：快照目录 + current symlink）。

说明：
- 本文件仅保留快照构建需要的 git 操作封装，供 `executor/repo_snapshots.py` 调用。
"""

from __future__ import annotations

import shutil
import subprocess
import tarfile
import time
from pathlib import Path

from .exceptions import GitOperationError
from .logger import logger


def snapshot_is_ssh_url(git_url: str) -> bool:
    return git_url.startswith(("git@", "ssh://"))


def snapshot_inject_token_to_url(git_url: str, git_token: str) -> str:
    """
    将 token 注入到 Git URL 中（仅用于 HTTPS URL）
    - GitHub: https://{token}@github.com/org/project.git
    - GitLab: https://oauth2:{token}@gitlab.com/org/project.git
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


def snapshot_git_url_for_fetch(git_url: str, git_token: str) -> str:
    if snapshot_is_ssh_url(git_url):
        return git_url
    return snapshot_inject_token_to_url(git_url, git_token)


def snapshot_run_git(cmd: list[str], cwd: Path, timeout: int = 300) -> subprocess.CompletedProcess:
    """
    执行 git 命令（用于快照构建线程），失败抛出 GitOperationError。
    """
    try:
        logger.LOCAL.debug(f"[快照Git] 执行命令: {' '.join(cmd)} cwd={cwd}")
        return subprocess.run(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=True,
        )
    except subprocess.TimeoutExpired as e:
        raise GitOperationError(f"Git 命令超时({timeout}s): {' '.join(cmd)}") from e
    except subprocess.CalledProcessError as e:
        raise GitOperationError(f"Git 命令失败: {' '.join(cmd)} stderr={e.stderr}") from e
    except Exception as e:
        raise GitOperationError(f"Git 命令异常: {e}") from e


def snapshot_ensure_mirror_repo(workspace_root: Path, git_url: str, git_token: str) -> Path:
    """
    确保本地 mirror 仓库存在（用于 fetch + archive）。
    目录：{workspace_root}/.rpa_projects_mirror
    """
    mirror_dir = workspace_root / ".rpa_projects_mirror"
    git_dir = mirror_dir / ".git"
    if mirror_dir.exists() and git_dir.exists():
        return mirror_dir

    mirror_dir.parent.mkdir(parents=True, exist_ok=True)
    if mirror_dir.exists():
        backup = workspace_root / ".tmp" / f"rpa_projects_mirror_backup_{int(time.time())}"
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(mirror_dir), str(backup))
        logger.LOCAL.warning(f"[快照Git] mirror 目录异常，已备份到: {backup}")

    auth_url = snapshot_git_url_for_fetch(git_url, git_token)
    logger.LOCAL.info("[快照Git] 初始化 mirror 仓库（首次 clone）")
    # mirror 仓库只用于 fetch/读对象，不需要 checkout
    try:
        subprocess.run(
            ["git", "clone", "--no-checkout", "--depth", "1", auth_url, str(mirror_dir)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=600,
            check=True,
        )
    except Exception as e:
        raise GitOperationError(f"初始化 mirror 仓库失败: {e}") from e
    return mirror_dir


def snapshot_fetch_branch(mirror_dir: Path, git_url: str, git_token: str, branch: str) -> None:
    auth_url = snapshot_git_url_for_fetch(git_url, git_token)
    # 更新 origin URL（token 可能变更）
    try:
        snapshot_run_git(["git", "remote", "set-url", "origin", auth_url], cwd=mirror_dir, timeout=60)
    except Exception:
        pass
    snapshot_run_git(["git", "fetch", "origin", branch, "--depth=1"], cwd=mirror_dir, timeout=120)


def snapshot_rev_parse(mirror_dir: Path, ref: str) -> str:
    return snapshot_run_git(["git", "rev-parse", ref], cwd=mirror_dir, timeout=30).stdout.strip()


def snapshot_archive_export(mirror_dir: Path, commit: str, target_dir: Path) -> None:
    """
    `git archive` 导出指定 commit 到 target_dir（纯工作树，无 .git）。
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(
        ["git", "archive", "--format=tar", commit],
        cwd=str(mirror_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.stdout is not None
    try:
        with tarfile.open(fileobj=proc.stdout, mode="r|") as tf:
            tf.extractall(path=str(target_dir))
        stderr = (proc.stderr.read() if proc.stderr else b"").decode("utf-8", errors="ignore")
        code = proc.wait(timeout=300)
        if code != 0:
            raise GitOperationError(f"git archive 失败: {stderr}")
    finally:
        try:
            if proc.poll() is None:
                proc.kill()
        except Exception:
            pass

