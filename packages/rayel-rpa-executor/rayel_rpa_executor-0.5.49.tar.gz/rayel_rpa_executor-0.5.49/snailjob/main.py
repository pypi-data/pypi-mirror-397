import threading
import time
import sys

from snailjob.config import get_snailjob_settings
from snailjob.exec import ExecutorManager
from snailjob.grpc import run_grpc_server
from snailjob.rpc import send_heartbeat
from snailjob.metrics_server import start_metrics_server
from snailjob.log import SnailLog
from snailjob.outbox import start_reporter, start_log_reporter_async

# 全局配置实例
settings = get_snailjob_settings()


class HeartbeatTask:
    """心跳发送任务"""

    def __init__(self) -> None:
        self._thread = threading.Thread(target=self._send_heartbeats, daemon=True)
        self.event = threading.Event()

    def _send_heartbeats(self):
        while not self.event.is_set():
            send_heartbeat()
            time.sleep(28)

    def run(self):
        self._thread.start()


def client_main():
    SnailLog.LOCAL.info(f"load config success ->\n{settings}")

    """客户端主函数"""
    # 启动Prometheus metrics服务器
    metrics_server = start_metrics_server(settings)
    # 启动执行结果 outbox 上报器（后台线程）
    # 重要：outbox 初始化可能遇到 sqlite 文件锁/IO 异常，绝不能阻塞心跳与注册流程
    def _bootstrap_outbox_reporter():
        try:
            start_reporter()
        except Exception as e:
            SnailLog.LOCAL.error(f"OUTBOX_BOOTSTRAP_FAILED err={type(e).__name__}:{e}")

    threading.Thread(
        target=_bootstrap_outbox_reporter,
        name="snailjob-outbox-bootstrap",
        daemon=True,
    ).start()

    # 启动日志 outbox 上报器（仅消费本地持久化队列，不会增加 DB 写入；用于重启后补偿）
    start_log_reporter_async()
    
    heartbeat_task = HeartbeatTask()
    heartbeat_task.run()
    ExecutorManager.register_executors_to_server()

    run_grpc_server(settings.snail_host_port)
