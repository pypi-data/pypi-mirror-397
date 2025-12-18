"""
动态执行器刷新线程：
- 每隔固定周期扫描 rpa_projects/app/services/**/main.py
- 发现带 @service(id="...", name="...") 的 Service 后，动态注册对应 executorName
- fingerprint 变化时上报到服务端（让后端可选且可调度）
"""

from __future__ import annotations

import os
import threading
import time
from pathlib import Path
from typing import Optional

from executor.logger import logger
from executor import repo_snapshots
from executor.service_registry import (
    ServiceScanner,
    compute_fingerprint,
    build_thin_wrapper_job_method,
    get_defaults_from_env,
    resolve_executor_name_conflicts,
)

from snailjob.exec import ExecutorManager


class DynamicExecutorRefresher:
    def __init__(self, interval_seconds: int = 60):
        self.interval_seconds = max(5, int(interval_seconds))
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._scanner = ServiceScanner()
        self._last_fingerprint: Optional[str] = None

    def start(self, daemon: bool = True) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(
            target=self._run_loop,
            name="DynamicExecutorRefresher",
            daemon=daemon,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def run_once(self) -> bool:
        """
        执行一次扫描+注册+（必要时）上报。
        Returns: 是否发生 fingerprint 变化
        """
        branch, workspace_root = get_defaults_from_env()
        workspace_root_path = Path(workspace_root).resolve()

        # 1) 定期更新 RPA 代码快照（失败不影响后续扫描/注册）
        # 说明：Git URL / Token 仍由环境变量提供（与 PlaywrightExecutorConfig 保持一致）
        git_url = os.getenv("GIT_REPO_URL", "")
        git_token = os.getenv("GIT_TOKEN", "")
        if git_url:
            repo_snapshots.try_update(
                workspace_root=workspace_root_path,
                git_url=git_url,
                git_token=git_token,
                branch=branch,
            )

        # 2) 扫描始终基于 current 快照（真实路径）
        try:
            _, repo_root = repo_snapshots.resolve_current_snapshot(workspace_root_path)
        except Exception as e:
            logger.LOCAL.warning(f"[动态执行器] current 快照不可用，跳过本轮扫描: {e}")
            return False

        descriptors = self._scanner.scan(repo_root)
        # 正常情况下 service_id 可保证唯一；若发生冲突则去重避免覆盖
        descriptors = resolve_executor_name_conflicts(descriptors)
        fingerprint = compute_fingerprint(descriptors)

        changed = fingerprint != self._last_fingerprint
        if not changed:
            # 即使 executor 列表未变化，也允许清理旧快照（引用计数为 0 且非 current）
            try:
                repo_snapshots.cleanup(workspace_root=workspace_root_path, keep_min=2)
            except Exception as e:
                logger.LOCAL.warning(f"[动态执行器] 快照清理异常（忽略）: {e}")
            return False

        # 动态注册/更新
        for d in descriptors:
            wrapper = build_thin_wrapper_job_method(
                executor_name=d.executor_name,
                service_folder=d.service_folder,
                default_branch=branch,
                default_workspace_root=workspace_root,
            )
            ExecutorManager.register_or_update(wrapper)

        # 上报到服务端（让后端可见且可调度）
        ExecutorManager.register_executors_to_server()
        self._last_fingerprint = fingerprint

        logger.LOCAL.info(
            f"[动态执行器] 已刷新并上报: count={len(descriptors)}, fingerprint={fingerprint}"
        )

        # 3) 清理旧快照（引用计数为 0 且非 current）
        # 保留最近 2 个快照作为兜底
        try:
            repo_snapshots.cleanup(workspace_root=workspace_root_path, keep_min=2)
        except Exception as e:
            logger.LOCAL.warning(f"[动态执行器] 快照清理异常（忽略）: {e}")

        return True

    def _run_loop(self) -> None:
        logger.LOCAL.info(
            f"[动态执行器] 刷新线程启动: interval={self.interval_seconds}s"
        )
        while not self._stop_event.is_set():
            try:
                self.run_once()
            except Exception as e:
                logger.LOCAL.warning(f"[动态执行器] 刷新异常: {e}")
            finally:
                # 分段 sleep，便于 stop 更快生效
                for _ in range(self.interval_seconds):
                    if self._stop_event.is_set():
                        break
                    time.sleep(1)


