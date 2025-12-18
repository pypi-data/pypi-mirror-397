import atexit
import logging
import logging.handlers
import os
import pathlib
import queue
import sys
import threading
import time
import traceback
from typing import Any, List, Optional

from snailjob.config import get_snailjob_settings
from snailjob.ctx import SnailContextManager
from snailjob.schemas import JobLogTask, TaskLogFieldDTO, StatusEnum

BASE_DIR = pathlib.Path(os.getcwd()).resolve()

# 全局配置实例
settings = get_snailjob_settings()


class SnailHttpHandler(logging.Handler):
    """基于时间滑动窗口、队列缓存的日期处理器，用于远程上报日志"""

    # 日志格式转换规则
    RECORD_MAPPINGS = (
        ("time_stamp", lambda r: str(int(r.created * 1000))),
        ("level", lambda r: r.levelname),
        ("thread", lambda r: r.threadName),
        ("message", lambda r: r.msg),
        ("location", lambda r: f"{r.module}:{r.funcName}:{r.lineno}"),
        ("throwable", lambda r: SnailHttpHandler._format_exc_info(r.exc_info)),
    )

    def __init__(self, capacity=1000, interval=5, batch_size=100):
        super().__init__()
        self.interval = interval
        self.batch_size = batch_size
        self.capacity = capacity
        self.buffer = queue.Queue(capacity)
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.shutdown_event = threading.Event()
        self.worker_thread.start()

    def emit(self, record):
        try:
            dto = SnailHttpHandler._transform(record)
            # 非阻塞写入，满了就丢弃，避免阻塞业务线程
            self.buffer.put_nowait(dto)
        except queue.Full:
            # 记录丢弃到本地，不做阻塞
            sys.stderr.write(f"SnailJob Log queue full, dropping log. capacity:{self.capacity} interval:{self.interval} batch_size:{self.batch_size}\n")

    def _worker(self):
        """后台单线程 flush worker"""
        batch = []
        last_flush = time.time()

        while not self.shutdown_event.is_set():
            try:
                # 等待 interval 秒，如果拿不到则 flush
                timeout = self.interval - (time.time() - last_flush)
                item = self.buffer.get(timeout=max(0.1, timeout))
                batch.append(item)
            except queue.Empty:
                pass

            now = time.time()
            # 触发发送的两个条件：
            # 1. 达到批次大小限制 (避免包过大)
            # 2. 达到时间间隔限制 (保证实时性)
            if len(batch) >= self.batch_size or (batch and now - last_flush >= self.interval):
                self._safe_send(batch)
                batch = []
                last_flush = now

        # 退出前的扫尾：发送剩余的 batch
        if batch:
            self._safe_send(batch)

        # 尽力消费队列中剩余的日志
        remaining_items = []
        while not self.buffer.empty():
            try:
                remaining_items.append(self.buffer.get_nowait())
                if len(remaining_items) >= self.batch_size:
                    self._safe_send(remaining_items)
                    remaining_items = []
            except queue.Empty:
                break
        if remaining_items:
            self._safe_send(remaining_items)

    def _safe_send(self, items):
        try:
            from .rpc import send_batch_log_report
            # 临时打的日志
            status = send_batch_log_report(items)
            # 临时打的日志
            if status == StatusEnum.YES:
                return
            sys.stderr.write(f"[SnailJob] Log report failed with status: {status}\n")
        except Exception as e:
            sys.stderr.write(f"[SnailJob] Log report failed: {e}\n")

        # 直连失败：进入 outbox 队列持久化补偿
        try:
            from .outbox import enqueue_log_batch

            enqueue_log_batch(items)
        except Exception as e3:
            sys.stderr.write(f"[SnailJob] Log outbox enqueue failed: {type(e3).__name__}:{e3}\n")

    def close(self):
        self.shutdown_event.set()
        if self.worker_thread.is_alive():
            # Wait longer for potential retries to complete
            self.worker_thread.join(timeout=15)
        super().close()

    def _format_exc_info(exc_info: Any) -> Optional[str]:
        if exc_info is None:
            return None
        etype, value, tb = exc_info
        errors = traceback.format_exception(etype, value, tb)
        # 删除当前函数(execute_wrapper)的调用栈
        errors.pop(1)
        return "\n".join(errors)

    @staticmethod
    def _transform(record: logging.LogRecord) -> JobLogTask:
        """转换日志结构

        Args:
            record (logging.LogRecord): logging标准日志结构

        Returns:
            JobLogTask: SnailJob 服务器日志格式
        """

        field_list: List[TaskLogFieldDTO] = []
        for key, mapper in SnailHttpHandler.RECORD_MAPPINGS:
            assert callable(mapper), "Mapper is not callable"
            field_list.append(TaskLogFieldDTO(name=key, value=mapper(record)))
        field_list.append(TaskLogFieldDTO(name="host", value=settings.snail_host_ip))
        field_list.append(TaskLogFieldDTO(name="port", value=str(settings.snail_host_port)))

        # 兼容：某些场景（例如进程启动早期、非任务线程）没有设置 contextvar
        try:
            log_context = SnailContextManager.get_log_context()
            job_id = log_context.jobId
            task_batch_id = log_context.taskBatchId
            task_id = log_context.taskId
        except LookupError:
            job_id = 0
            task_batch_id = 0
            task_id = 0
        job_log_task = JobLogTask(
            logType="JOB",
            namespaceId=settings.snail_namespace,
            groupName=settings.snail_group_name,
            realTime=int(time.time() * 1000),
            fieldList=field_list,
            jobId=job_id,
            taskBatchId=task_batch_id,
            taskId=task_id,
        )

        return job_log_task

    def _send(self, items: List[JobLogTask]):
        """推送日志到远程服务器

        Args:
            items (List[JobLogTask]): 日志元素
        """
        # 延迟import, 解决循环依赖
        from .rpc import send_batch_log_report

        send_batch_log_report(items)

    def _start_timer(self):
        """启动时间滑动窗口定时器"""

        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(self.interval, self.flush)
        self.timer.start()


class SnailLog:
    """Snail Job 日志门面"""

    LOCAL = logging.getLogger("SnailJob Local Logger")
    REMOTE = logging.getLogger("SnailJob Remote Logger")

    @staticmethod
    def config_loggers():
        # 全局日志格式化器
        formatter = logging.Formatter(settings.snail_log_format)

        # 创建日志目录
        (BASE_DIR / settings.snail_log_local_filename).resolve().parent.mkdir(
            parents=True, exist_ok=True
        )
        # handler: 文件
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=BASE_DIR / settings.snail_log_local_filename,
            when="d",
            backupCount=settings.snail_log_local_backup_count,
        )
        file_handler.setFormatter(formatter)

        # handler: 控制台
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)

        # handler: http
        http_handler = SnailHttpHandler(
            capacity=settings.snail_log_remote_buffer_size,
            interval=settings.snail_log_remote_interval,
            batch_size=settings.snail_log_remote_batch_size
        )
        # 程序退出时关闭 handler
        atexit.register(lambda: http_handler.close())

        SnailLog.REMOTE.setLevel(settings.snail_log_level)
        SnailLog.REMOTE.parent = None
        SnailLog.REMOTE.addHandler(file_handler)
        SnailLog.REMOTE.addHandler(http_handler)
        SnailLog.REMOTE.addHandler(stream_handler)

        SnailLog.LOCAL.setLevel(settings.snail_log_level)
        SnailLog.LOCAL.parent = None
        SnailLog.LOCAL.addHandler(file_handler)
        SnailLog.LOCAL.addHandler(stream_handler)


# 配置日志
SnailLog.config_loggers()
