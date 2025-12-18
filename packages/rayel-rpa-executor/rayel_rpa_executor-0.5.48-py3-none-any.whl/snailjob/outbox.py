from __future__ import annotations

"""
执行结果 outbox（本地持久化 + 持续重试上报 + ACK 等待）

设计目标：
- 上报失败不丢：落盘后可跨进程重启继续重试
- 结果上报最终一致：后台持续尝试直到服务端 ACK（或达到最大上报窗口放弃）
- must_ack：任务线程可等待指定 taskBatchId 的 ACK（stop 时可提前退出等待）
"""

import logging
import sqlite3
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from persistqueue import Empty, SQLiteAckQueue
from persistqueue.sqlackqueue import AckStatus

from snailjob.config import get_snailjob_settings
from snailjob.rpc import send_batch_log_report, send_dispatch_result
from snailjob.schemas import DispatchJobResult, JobLogTask, StatusEnum


settings = get_snailjob_settings()
LOCAL_LOGGER = logging.getLogger("SnailJob Local Logger")


def _ctx_prefix(job_id: int, task_batch_id: int, task_id: int) -> str:
    """
    统一上下文前缀，便于与现有日志的 “[JobID:x TaskID:y]” 对齐。
    备注：项目里 TaskID 习惯上对应 taskBatchId，因此这里保留同样展示。
    """
    return f"[JobID:{job_id} TaskID:{task_batch_id}]"


def _short(s: str, max_len: int = 200) -> str:
    if s is None:
        return ""
    s = str(s)
    return s if len(s) <= max_len else (s[: max_len - 3] + "...")


def _is_sqlite_file(db_file: Path) -> bool:
    """快速判断文件是否为 SQLite DB（文件头应为 SQLite format 3\\x00）"""
    try:
        if not db_file.exists() or not db_file.is_file():
            return False
        if db_file.stat().st_size == 0:
            return False
        head = db_file.open("rb").read(16)
        return head.startswith(b"SQLite format 3\x00")
    except Exception:
        return False


def _quarantine_db(db_file: Path, reason: str) -> None:
    """
    把疑似损坏/非 sqlite 的文件隔离（改名），避免 worker 一直报错。
    同时尽量隔离 -wal/-shm。
    """
    ts = int(time.time())
    base = str(db_file)
    suffix = f".corrupt.{ts}"
    for p in (
        Path(base),
        Path(base + "-wal"),
        Path(base + "-shm"),
    ):
        if not p.exists():
            continue
        target = Path(str(p) + suffix)
        try:
            p.rename(target)
            LOCAL_LOGGER.warning(
                f"[OUTBOX] 检测到异常DB文件，已隔离 from={p} to={target} reason={reason}"
            )
        except Exception as e:
            LOCAL_LOGGER.error(
                f"[OUTBOX] 隔离失败 path={p} reason={reason} err={type(e).__name__}:{e}"
            )


def _open_sqlite_sanity_check(db_file: Path) -> None:
    """
    通过 sqlite3 打开做一次 sanity check，防止“文件存在但不是 DB”。
    """
    con = sqlite3.connect(str(db_file))
    try:
        con.execute("PRAGMA schema_version;").fetchone()
    finally:
        con.close()


def _vacuum_sqlite(db_path: str, *, timeout_seconds: float) -> None:
    """
    通过 sqlite3 执行 checkpoint + VACUUM，回收 DB 文件体积。
    注意：VACUUM 需要较强锁，可能短暂阻塞读写；因此做成低频+可配置。
    """
    con = sqlite3.connect(db_path, timeout=float(timeout_seconds))
    try:
        # WAL 模式下先做 checkpoint，避免 -wal 无限制膨胀
        try:
            con.execute("PRAGMA wal_checkpoint(TRUNCATE);").fetchall()
        except Exception:
            pass
        # VACUUM 不能在事务里
        con.isolation_level = None
        con.execute("VACUUM;")
    finally:
        con.close()


def _queue_stats(queue: Any) -> dict:
    """
    尽量从 persist-queue 的 SQLiteAckQueue 获取可观测信息：
    - ready: 等待被 worker 取走的数量
    - unack: 已被取走但尚未 ack/nack 的数量（在途）
    - ack_failed: 标记为放弃的数量
    - active: ready + unack（如果可得）
    """
    stats: dict[str, Any] = {}
    try:
        stats["ready"] = int(queue.qsize())
    except Exception:
        pass
    for name in ("unack_count", "ack_failed_count", "acked_count", "ready_count"):
        if hasattr(queue, name):
            try:
                stats[name] = int(getattr(queue, name)())
            except Exception:
                pass
    if hasattr(queue, "active_size"):
        try:
            stats["active"] = int(queue.active_size())
        except Exception:
            pass
    return stats


def _cleanup_acked_records(
    queue: SQLiteAckQueue,
    *,
    keep_latest: int,
    max_delete: int,
    clear_ack_failed: bool = True,
) -> None:
    """
    persist-queue 的 SQLiteAckQueue 默认不会删除 acked 记录，只会标记 status=acked(5)。
    这里做 bounded cleanup，避免 DB 无限增长。
    """
    try:
        acked = int(queue.acked_count())
        failed = int(queue.ack_failed_count()) if clear_ack_failed else 0
        # 触发条件：超过保留阈值（或 keep_latest=0 时，只要存在 acked 就清）
        if keep_latest <= 0:
            if acked <= 0 and failed <= 0:
                return
        else:
            if acked <= keep_latest and failed <= keep_latest:
                return
        queue.clear_acked_data(
            max_delete=max_delete if max_delete > 0 else 1000,
            keep_latest=keep_latest,
            clear_ack_failed=clear_ack_failed,
        )
    except Exception as e:
        LOCAL_LOGGER.warning(f"[OUTBOX] 清理已完成记录失败 err={type(e).__name__}:{e}")


def _sqlite_ack_queue_from_path(
    *,
    configured_path: str,
    default_file_name: str,
    timeout_seconds: float,
) -> tuple[SQLiteAckQueue, str]:
    """
    persist-queue 期望 (dir_path, db_file_name)；
    这里允许用户传入文件路径或目录路径，统一解析。
    """
    p = Path(str(configured_path)).expanduser()
    if p.suffix:
        db_dir = p.parent
        db_file = p.name
    else:
        db_dir = p
        db_file = default_file_name

    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = str((db_dir / db_file).resolve())
    db_path_obj = Path(db_path)

    # 预检：如果文件存在但不是 sqlite，则隔离后重建
    if db_path_obj.exists() and db_path_obj.is_file() and not _is_sqlite_file(db_path_obj):
        _quarantine_db(db_path_obj, reason="file is not sqlite database")

    # 二次校验：sqlite3 打开失败同样隔离（典型报错：file is not a database）
    if db_path_obj.exists() and db_path_obj.is_file():
        try:
            _open_sqlite_sanity_check(db_path_obj)
        except sqlite3.DatabaseError as e:
            _quarantine_db(db_path_obj, reason=f"sqlite open failed: {type(e).__name__}:{e}")
        except Exception:
            # 其他异常不做强制隔离
            pass

    # 创建队列：若首次创建仍失败，再隔离一次并重试 1 次
    try:
        q = SQLiteAckQueue(
            str(db_dir.resolve()),
            db_file_name=db_file,
            timeout=float(timeout_seconds),
            # 需要跨线程使用：reporter worker 在线程中消费同一个队列实例
            multithreading=True,
            auto_commit=True,
            auto_resume=True,
        )
    except sqlite3.DatabaseError as e:
        # 极少数情况下：文件刚被创建但损坏/被污染，直接隔离并重建
        _quarantine_db(db_path_obj, reason=f"sqlite init failed: {type(e).__name__}:{e}")
        q = SQLiteAckQueue(
            str(db_dir.resolve()),
            db_file_name=db_file,
            timeout=float(timeout_seconds),
            multithreading=True,
            auto_commit=True,
            auto_resume=True,
        )
    return q, db_path


def _now() -> float:
    return time.time()


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _backoff_seconds(attempt: int, base: float, cap: float) -> float:
    # attempt 从 1 开始更直观；退避至少 base，最多 cap
    if attempt <= 0:
        attempt = 1
    return _clamp(base * (2 ** (attempt - 1)), base, cap)


@dataclass
class AckWaiter:
    event: threading.Event
    # acked / dropped
    status: Optional[str] = None
    message: str = ""


class AckRegistry:
    """taskBatchId -> waiter（仅用于本进程内等待）"""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._waiters: Dict[int, AckWaiter] = {}

    def get_or_create(self, task_batch_id: int) -> AckWaiter:
        with self._lock:
            w = self._waiters.get(task_batch_id)
            if w is None:
                w = AckWaiter(event=threading.Event())
                self._waiters[task_batch_id] = w
            return w

    def resolve(self, task_batch_id: int, *, status: str, message: str = "") -> None:
        with self._lock:
            w = self._waiters.get(task_batch_id)
            if w is None:
                return
            w.status = status
            w.message = message
            w.event.set()
            # 尽量清理，避免内存增长
            self._waiters.pop(task_batch_id, None)


_ack_registry = AckRegistry()


class DispatchResultOutbox:
    """
    基于 persist-queue 的 SQLiteAckQueue：
    - get() 后标记为 unack；进程崩溃后会 auto_resume 把 unack 恢复为 ready
    - 成功：ack(id)
    - 失败重试：nack(id)（无需 put 回队列，避免重复/丢单）
    """

    def __init__(self) -> None:
        configured = getattr(settings, "outbox_db_path", "data/outbox/dispatch_results.db")
        sqlite_timeout = float(getattr(settings, "outbox_sqlite_timeout_seconds", 1.0))
        self._configured_path = str(configured)
        self._sqlite_timeout = sqlite_timeout
        self._reopen_lock = threading.Lock()
        self.queue, self.db_path = _sqlite_ack_queue_from_path(
            configured_path=str(configured),
            default_file_name="dispatch_results.db",
            timeout_seconds=sqlite_timeout,
        )

    def reopen(self, reason: str) -> None:
        """当 sqlite 报错时自愈重连（可能会丢失尚未 flush 的 in-memory 状态，但 DB 仍在）"""
        with self._reopen_lock:
            LOCAL_LOGGER.error(f"[OUTBOX][RESULT] 触发自愈重连 reason={reason}")
            self.queue, self.db_path = _sqlite_ack_queue_from_path(
                configured_path=self._configured_path,
                default_file_name="dispatch_results.db",
                timeout_seconds=self._sqlite_timeout,
            )

    def enqueue(self, payload: DispatchJobResult) -> None:
        data = payload.model_dump(mode="json")
        item = {
            "job_id": int(payload.jobId),
            "task_id": int(payload.taskId),
            "task_batch_id": int(payload.taskBatchId),
            "payload": data,
            "attempt": 0,
            "last_error": "",
        }
        pqid = self.queue.put(item)
        prefix = _ctx_prefix(int(payload.jobId), int(payload.taskBatchId), int(payload.taskId))
        LOCAL_LOGGER.info(
            f"{prefix} [OUTBOX][RESULT] 已入队等待上报 pqid={pqid} db={self.db_path}"
        )

    def waiter(self, task_batch_id: int) -> AckWaiter:
        return _ack_registry.get_or_create(task_batch_id)

    def mark_acked(self, task_batch_id: int) -> None:
        _ack_registry.resolve(task_batch_id, status="acked", message="")

    def mark_dropped(self, task_batch_id: int, message: str) -> None:
        _ack_registry.resolve(task_batch_id, status="dropped", message=message)


class DispatchResultReporter:
    def __init__(self, outbox: DispatchResultOutbox) -> None:
        self.outbox = outbox
        self._stop_event = threading.Event()
        self._threads: list[threading.Thread] = []
        self._monitor_thread: Optional[threading.Thread] = None

        self.workers = int(getattr(settings, "outbox_reporter_workers", 2))
        self.retry_base = float(getattr(settings, "outbox_retry_base_seconds", 1.0))
        self.retry_cap = float(getattr(settings, "outbox_retry_max_seconds", 60.0))
        # 单条结果允许的最长上报窗口（默认 1 小时）
        self.max_age = float(getattr(settings, "outbox_max_report_age_seconds", 3600))
        self.monitor_interval = int(getattr(settings, "outbox_monitor_interval_seconds", 30))
        self.keep_latest_acked = int(getattr(settings, "outbox_keep_latest_acked", 0))
        self.clear_acked_max_delete = int(getattr(settings, "outbox_clear_acked_max_delete", 1000))
        self.vacuum_interval = int(getattr(settings, "outbox_vacuum_interval_seconds", 1800))
        self.vacuum_timeout = float(getattr(settings, "outbox_vacuum_sqlite_timeout_seconds", 5.0))
        self._last_vacuum_ts = 0.0

    def start(self) -> None:
        if self._threads:
            return
        for i in range(max(1, self.workers)):
            t = threading.Thread(
                target=self._worker_loop,
                name=f"snailjob-dispatch-result-reporter-{i}",
                daemon=True,
            )
            t.start()
            self._threads.append(t)
        LOCAL_LOGGER.info(
            f"[OUTBOX][RESULT] 后台上报线程已启动 workers={len(self._threads)} db={self.outbox.db_path}"
        )
        self._start_monitor()

    def _start_monitor(self) -> None:
        if self.monitor_interval <= 0:
            return
        if self._monitor_thread and self._monitor_thread.is_alive():
            return

        def _loop():
            while not self._stop_event.is_set():
                st = _queue_stats(self.outbox.queue)
                # ready=待处理，unack=在途，ack_failed=放弃
                LOCAL_LOGGER.info(
                    f"[OUTBOX][RESULT] 队列状态 ready={st.get('ready','?')} "
                    f"inflight={st.get('unack_count','?')} dropped={st.get('ack_failed_count','?')} "
                    f"active={st.get('active','?')}"
                )
                # 清理已完成记录，避免 DB 无限增长
                _cleanup_acked_records(
                    self.outbox.queue,
                    keep_latest=self.keep_latest_acked,
                    max_delete=self.clear_acked_max_delete,
                    clear_ack_failed=True,
                )
                # 定期 VACUUM：回收文件体积（低频）
                if self.vacuum_interval > 0:
                    now = _now()
                    if self._last_vacuum_ts <= 0:
                        self._last_vacuum_ts = now
                    elif now - self._last_vacuum_ts >= self.vacuum_interval:
                        try:
                            _vacuum_sqlite(self.outbox.db_path, timeout_seconds=self.vacuum_timeout)
                            LOCAL_LOGGER.info(
                                f"[OUTBOX][RESULT] VACUUM 完成 db={self.outbox.db_path}"
                            )
                        except Exception as e:
                            LOCAL_LOGGER.warning(
                                f"[OUTBOX][RESULT] VACUUM 失败 db={self.outbox.db_path} err={type(e).__name__}:{e}"
                            )
                        self._last_vacuum_ts = now
                time.sleep(self.monitor_interval)

        self._monitor_thread = threading.Thread(
            target=_loop,
            name="snailjob-outbox-result-monitor",
            daemon=True,
        )
        self._monitor_thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _worker_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                raw = self.outbox.queue.get(timeout=1, raw=True)  # type: ignore[arg-type]
            except Empty:
                continue
            except sqlite3.DatabaseError as e:
                # 典型：file is not a database / malformed
                self.outbox.reopen(reason=f"{type(e).__name__}:{e}")
                time.sleep(1)
                continue
            except Exception as e:
                LOCAL_LOGGER.error(f"OUTBOX_WORKER_ERROR err={type(e).__name__}:{e}")
                time.sleep(1)
                continue

            pqid = raw.get("pqid")
            item = raw.get("data") or {}
            ts = float(raw.get("timestamp") or 0.0)

            job_id = int(item.get("job_id") or 0)
            task_batch_id = int(item.get("task_batch_id") or 0)
            task_id = int(item.get("task_id") or 0)
            attempt = int(item.get("attempt") or 0)
            prefix = _ctx_prefix(job_id, task_batch_id, task_id)

            # 1) 超过最大上报窗口：不再尝试上报
            age = _now() - ts if ts else 0.0
            if self.max_age > 0 and ts and age > self.max_age:
                msg = f"结果上报超过最大窗口({int(self.max_age)}s)已放弃"
                try:
                    self.outbox.queue.ack_failed(id=pqid)
                except Exception as e:
                    LOCAL_LOGGER.warning(
                        f"{prefix} [OUTBOX][RESULT] 标记放弃失败 pqid={pqid} err={type(e).__name__}:{e}"
                    )
                self.outbox.mark_dropped(task_batch_id, msg)
                LOCAL_LOGGER.error(
                    f"{prefix} [OUTBOX][RESULT] 放弃上报 pqid={pqid} age={age:.1f}s reason={msg}"
                )
                continue

            # 2) 尝试上报
            try:
                payload_dict = item.get("payload") or {}
                payload = DispatchJobResult(**payload_dict)
                status = send_dispatch_result(payload)
            except Exception as e:
                status = StatusEnum.NO
                item["last_error"] = f"{type(e).__name__}: {e}"
            else:
                if status != StatusEnum.YES:
                    item["last_error"] = f"server_status={status}"

            if status == StatusEnum.YES:
                try:
                    self.outbox.queue.ack(id=pqid)
                except Exception as e:
                    # 理论上很少见：上报成功但本地 ack 失败；下次 resume 会重复上报（可接受）
                    LOCAL_LOGGER.warning(
                        f"{prefix} [OUTBOX][RESULT] 服务端已确认但本地ACK失败 pqid={pqid} err={type(e).__name__}:{e}"
                    )
                self.outbox.mark_acked(task_batch_id)
                LOCAL_LOGGER.info(f"{prefix} [OUTBOX][RESULT] 上报成功并ACK pqid={pqid} attempt={attempt}")
                continue

            # 3) 失败：更新尝试次数、退避，并 nack 回 ready
            attempt += 1
            item["attempt"] = attempt

            try:
                self.outbox.queue.update({"pqid": pqid, "data": item})
            except Exception:
                # 更新失败不影响重试
                pass

            try:
                self.outbox.queue.nack(id=pqid)
            except Exception as e:
                LOCAL_LOGGER.warning(
                    f"{prefix} [OUTBOX][RESULT] nack 失败（可能导致该条暂时无法重试） pqid={pqid} err={type(e).__name__}:{e}"
                )

            backoff = _backoff_seconds(attempt, self.retry_base, self.retry_cap)
            LOCAL_LOGGER.warning(
                f"{prefix} [OUTBOX][RESULT] 上报失败，后台将重试 "
                f"pqid={pqid} attempt={attempt} backoff={backoff:.1f}s err={_short(item.get('last_error',''))}"
            )
            time.sleep(backoff)


class LogBatchOutbox:
    """日志批量上报 outbox（持久化 + ack/nack + 1小时窗口）"""

    def __init__(self) -> None:
        configured = getattr(settings, "log_outbox_db_path", "data/outbox/log_batches.db")
        sqlite_timeout = float(getattr(settings, "log_outbox_sqlite_timeout_seconds", 1.0))
        self._configured_path = str(configured)
        self._sqlite_timeout = sqlite_timeout
        self._reopen_lock = threading.Lock()
        self.queue, self.db_path = _sqlite_ack_queue_from_path(
            configured_path=str(configured),
            default_file_name="log_batches.db",
            timeout_seconds=sqlite_timeout,
        )

    def reopen(self, reason: str) -> None:
        with self._reopen_lock:
            LOCAL_LOGGER.error(f"[OUTBOX][LOG] 触发自愈重连 reason={reason}")
            self.queue, self.db_path = _sqlite_ack_queue_from_path(
                configured_path=self._configured_path,
                default_file_name="log_batches.db",
                timeout_seconds=self._sqlite_timeout,
            )

    def enqueue(self, batch: list[JobLogTask]) -> None:
        # 注意：日志无需 must_ack；这里仅保证“尽力持久化 + 后台补偿”
        primary = batch[0] if batch else None
        primary_job_id = int(primary.jobId) if primary else 0
        primary_task_batch_id = int(primary.taskBatchId) if primary else 0
        primary_task_id = int(primary.taskId) if primary else 0

        # 简短摘要：批次里可能混了多个 taskBatchId（flush 时跨任务聚合）
        try:
            batch_ids = sorted({int(x.taskBatchId) for x in batch})
        except Exception:
            batch_ids = []
        batch_ids_sample = batch_ids[:5]
        batch_ids_more = max(0, len(batch_ids) - len(batch_ids_sample))

        item = {
            "payload": [x.model_dump(mode="json") for x in batch],
            "primary_job_id": primary_job_id,
            "primary_task_batch_id": primary_task_batch_id,
            "primary_task_id": primary_task_id,
            "batch_size": len(batch),
            "task_batch_ids_sample": batch_ids_sample,
            "task_batch_ids_more": batch_ids_more,
            "attempt": 0,
            "last_error": "",
        }
        pqid = self.queue.put(item)
        prefix = _ctx_prefix(primary_job_id, primary_task_batch_id, primary_task_id)
        sample_text = ",".join(str(x) for x in batch_ids_sample) if batch_ids_sample else "-"
        more_text = f"+{batch_ids_more}" if batch_ids_more else ""
        LOCAL_LOGGER.info(
            f"{prefix} [OUTBOX][LOG] 已入队等待上报 pqid={pqid} size={len(batch)} "
            f"taskBatchIds={sample_text}{more_text} db={self.db_path}"
        )


class LogBatchReporter:
    def __init__(self, outbox: LogBatchOutbox) -> None:
        self.outbox = outbox
        self._stop_event = threading.Event()
        self._threads: list[threading.Thread] = []
        self._monitor_thread: Optional[threading.Thread] = None

        self.workers = int(getattr(settings, "log_outbox_reporter_workers", 2))
        self.retry_base = float(getattr(settings, "log_outbox_retry_base_seconds", 1.0))
        self.retry_cap = float(getattr(settings, "log_outbox_retry_max_seconds", 60.0))
        self.max_age = float(getattr(settings, "log_outbox_max_report_age_seconds", 3600))
        self.monitor_interval = int(getattr(settings, "log_outbox_monitor_interval_seconds", 30))
        self.keep_latest_acked = int(getattr(settings, "log_outbox_keep_latest_acked", 1000))
        self.clear_acked_max_delete = int(getattr(settings, "log_outbox_clear_acked_max_delete", 1000))
        self.vacuum_interval = int(getattr(settings, "log_outbox_vacuum_interval_seconds", 1800))
        self.vacuum_timeout = float(getattr(settings, "outbox_vacuum_sqlite_timeout_seconds", 5.0))
        self._last_vacuum_ts = 0.0

    def start(self) -> None:
        if self._threads:
            return
        for i in range(max(1, self.workers)):
            t = threading.Thread(
                target=self._worker_loop,
                name=f"snailjob-log-batch-reporter-{i}",
                daemon=True,
            )
            t.start()
            self._threads.append(t)
        LOCAL_LOGGER.info(
            f"[OUTBOX][LOG] 后台上报线程已启动 workers={len(self._threads)} db={self.outbox.db_path}"
        )
        self._start_monitor()

    def _start_monitor(self) -> None:
        if self.monitor_interval <= 0:
            return
        if self._monitor_thread and self._monitor_thread.is_alive():
            return

        def _loop():
            while not self._stop_event.is_set():
                st = _queue_stats(self.outbox.queue)
                LOCAL_LOGGER.info(
                    f"[OUTBOX][LOG] 队列状态 ready={st.get('ready','?')} "
                    f"inflight={st.get('unack_count','?')} dropped={st.get('ack_failed_count','?')} "
                    f"active={st.get('active','?')}"
                )
                _cleanup_acked_records(
                    self.outbox.queue,
                    keep_latest=self.keep_latest_acked,
                    max_delete=self.clear_acked_max_delete,
                    clear_ack_failed=True,
                )
                if self.vacuum_interval > 0:
                    now = _now()
                    if self._last_vacuum_ts <= 0:
                        self._last_vacuum_ts = now
                    elif now - self._last_vacuum_ts >= self.vacuum_interval:
                        try:
                            _vacuum_sqlite(self.outbox.db_path, timeout_seconds=self.vacuum_timeout)
                            LOCAL_LOGGER.info(
                                f"[OUTBOX][LOG] VACUUM 完成 db={self.outbox.db_path}"
                            )
                        except Exception as e:
                            LOCAL_LOGGER.warning(
                                f"[OUTBOX][LOG] VACUUM 失败 db={self.outbox.db_path} err={type(e).__name__}:{e}"
                            )
                        self._last_vacuum_ts = now
                time.sleep(self.monitor_interval)

        self._monitor_thread = threading.Thread(
            target=_loop,
            name="snailjob-outbox-log-monitor",
            daemon=True,
        )
        self._monitor_thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _worker_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                raw = self.outbox.queue.get(timeout=1, raw=True)  # type: ignore[arg-type]
            except Empty:
                continue
            except sqlite3.DatabaseError as e:
                self.outbox.reopen(reason=f"{type(e).__name__}:{e}")
                time.sleep(1)
                continue
            except Exception as e:
                LOCAL_LOGGER.error(f"LOG_OUTBOX_WORKER_ERROR err={type(e).__name__}:{e}")
                time.sleep(1)
                continue

            pqid = raw.get("pqid")
            item = raw.get("data") or {}
            ts = float(raw.get("timestamp") or 0.0)
            attempt = int(item.get("attempt") or 0)
            primary_job_id = int(item.get("primary_job_id") or 0)
            primary_task_batch_id = int(item.get("primary_task_batch_id") or 0)
            primary_task_id = int(item.get("primary_task_id") or 0)
            batch_size = int(item.get("batch_size") or 0)
            batch_ids_sample = item.get("task_batch_ids_sample") or []
            batch_ids_more = int(item.get("task_batch_ids_more") or 0)
            prefix = _ctx_prefix(primary_job_id, primary_task_batch_id, primary_task_id)

            age = _now() - ts if ts else 0.0
            if self.max_age > 0 and ts and age > self.max_age:
                msg = f"日志上报超过最大窗口({int(self.max_age)}s)已放弃"
                try:
                    self.outbox.queue.ack_failed(id=pqid)
                except Exception as e:
                    LOCAL_LOGGER.warning(
                        f"{prefix} [OUTBOX][LOG] 标记放弃失败 pqid={pqid} err={type(e).__name__}:{e}"
                    )
                LOCAL_LOGGER.error(
                    f"{prefix} [OUTBOX][LOG] 放弃上报 pqid={pqid} age={age:.1f}s reason={msg} size={batch_size}"
                )
                continue

            try:
                payload_dicts = item.get("payload") or []
                payload = [JobLogTask(**d) for d in payload_dicts]
                status = send_batch_log_report(payload)
            except Exception as e:
                status = StatusEnum.NO
                item["last_error"] = f"{type(e).__name__}: {e}"
            else:
                if status != StatusEnum.YES:
                    item["last_error"] = f"server_status={status}"

            if status == StatusEnum.YES:
                try:
                    self.outbox.queue.ack(id=pqid)
                except Exception as e:
                    LOCAL_LOGGER.warning(
                        f"{prefix} [OUTBOX][LOG] 服务端已确认但本地ACK失败 pqid={pqid} err={type(e).__name__}:{e}"
                    )
                sample_text = ",".join(str(x) for x in batch_ids_sample) if batch_ids_sample else "-"
                more_text = f"+{batch_ids_more}" if batch_ids_more else ""
                LOCAL_LOGGER.info(
                    f"{prefix} [OUTBOX][LOG] 上报成功并ACK pqid={pqid} attempt={attempt} "
                    f"size={batch_size} taskBatchIds={sample_text}{more_text}"
                )
                continue

            attempt += 1
            item["attempt"] = attempt
            try:
                self.outbox.queue.update({"pqid": pqid, "data": item})
            except Exception:
                pass
            try:
                self.outbox.queue.nack(id=pqid)
            except Exception as e:
                LOCAL_LOGGER.warning(
                    f"{prefix} [OUTBOX][LOG] nack 失败（可能导致该条暂时无法重试） pqid={pqid} err={type(e).__name__}:{e}"
                )

            backoff = _backoff_seconds(attempt, self.retry_base, self.retry_cap)
            LOCAL_LOGGER.warning(
                f"{prefix} [OUTBOX][LOG] 上报失败，后台将重试 "
                f"pqid={pqid} attempt={attempt} backoff={backoff:.1f}s err={_short(item.get('last_error',''))}"
            )
            time.sleep(backoff)


_outbox_singleton: Optional[DispatchResultOutbox] = None
_reporter_singleton: Optional[DispatchResultReporter] = None
_log_outbox_singleton: Optional[LogBatchOutbox] = None
_log_reporter_singleton: Optional[LogBatchReporter] = None
# 注意：get_* 与 start_* 会互相调用；必须使用可重入锁避免自锁死（deadlock）
_singleton_lock = threading.RLock()


def get_outbox() -> DispatchResultOutbox:
    global _outbox_singleton
    with _singleton_lock:
        if _outbox_singleton is None:
            _outbox_singleton = DispatchResultOutbox()
        return _outbox_singleton


def start_reporter() -> DispatchResultReporter:
    global _reporter_singleton
    with _singleton_lock:
        if _reporter_singleton is None:
            _reporter_singleton = DispatchResultReporter(get_outbox())
            _reporter_singleton.start()
        return _reporter_singleton


def get_log_outbox() -> LogBatchOutbox:
    global _log_outbox_singleton
    with _singleton_lock:
        if _log_outbox_singleton is None:
            _log_outbox_singleton = LogBatchOutbox()
        return _log_outbox_singleton


def start_log_reporter() -> LogBatchReporter:
    global _log_reporter_singleton
    with _singleton_lock:
        if _log_reporter_singleton is None:
            _log_reporter_singleton = LogBatchReporter(get_log_outbox())
            _log_reporter_singleton.start()
        return _log_reporter_singleton


def start_log_reporter_async() -> None:
    """非阻塞启动日志上报 reporter，避免影响主流程/日志线程。"""

    def _run():
        try:
            start_log_reporter()
        except Exception as e:
            LOCAL_LOGGER.error(f"LOG_OUTBOX_BOOTSTRAP_FAILED err={type(e).__name__}:{e}")

    threading.Thread(target=_run, name="snailjob-log-outbox-bootstrap", daemon=True).start()


def enqueue_log_batch(batch: list[JobLogTask]) -> None:
    """把日志批次写入持久化 outbox（若异常则抛出，由调用方决定降级策略）。"""
    start_log_reporter_async()
    get_log_outbox().enqueue(batch)


