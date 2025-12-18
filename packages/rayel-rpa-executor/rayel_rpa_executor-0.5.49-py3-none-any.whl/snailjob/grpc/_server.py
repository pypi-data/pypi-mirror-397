import json
import time
from concurrent import futures

import grpc

from snailjob.config import get_snailjob_settings
from snailjob.grpc import snailjob_pb2, snailjob_pb2_grpc
from snailjob.log import SnailLog
from snailjob.metrics import get_metrics
from snailjob.schemas import DispatchJobRequest, StopJobRequest, StatusEnum

# 获取配置
settings = get_snailjob_settings()

SLEEP_SECONDS = 60


class SnailJobServicer(snailjob_pb2_grpc.UnaryRequestServicer):
    def unaryRequest(
        self,
        request: snailjob_pb2.GrpcSnailJobRequest,
        _: grpc.RpcContext,
    ) -> snailjob_pb2.GrpcResult:
        # 监控打点
        metrics = get_metrics()
        metrics.record_rpc_request()

        if request.metadata.uri == "/job/dispatch/v1":
            return SnailJobServicer.dispatch(request)
        elif request.metadata.uri == "/job/stop/v1":
            return SnailJobServicer.stop(request)
        elif request.metadata.uri == "/job/idle/v1":
            return SnailJobServicer.idle(request)
        elif request.metadata.uri == "/sync/node/metadata":
            return SnailJobServicer.registry_node_metadata(request)
        else:
            # 注意：必须返回 GrpcResult，返回 None 会导致 gRPC 报 Failed to serialize response
            return snailjob_pb2.GrpcResult(
                reqId=request.reqId,
                status=StatusEnum.NO,
                message=f"unknown uri: {request.metadata.uri}",
                data="null",
            )

    @staticmethod
    def dispatch(request: snailjob_pb2.GrpcSnailJobRequest):
        from .. import ExecutorManager

        args = json.loads(request.body)
        dispatchJobRequest = DispatchJobRequest(**args[0])
        result = ExecutorManager.dispatch(dispatchJobRequest)
        return snailjob_pb2.GrpcResult(
            reqId=request.reqId,
            status=result.status,
            message=result.message,
            data=json.dumps(result.data),
        )

    @staticmethod
    def stop(request: snailjob_pb2.GrpcSnailJobRequest):
        from .. import ExecutorManager

        args = json.loads(request.body)
        stopJobRequest = StopJobRequest(**args[0])
        ExecutorManager.stop(stopJobRequest)
        return snailjob_pb2.GrpcResult(
            reqId=request.reqId,
            status=1,
            message="",
            data="true",
        )

    @staticmethod
    def idle(request: snailjob_pb2.GrpcSnailJobRequest):
        """
        判断客户端是否空闲：
        - 线程池缓存数量为 0 即空闲（与服务端约定一致）
        """
        from .. import ExecutorManager, ThreadPoolCache

        _ = request  # body 为占位参数，忽略即可
        # 优先使用运行中任务计数（更实时）；否则回退到线程池缓存数量判定
        idle = ExecutorManager.is_idle(is_print=True) or ThreadPoolCache.get_thread_pool_size() == 0
        return snailjob_pb2.GrpcResult(
            reqId=request.reqId,
            status=1,
            message="",
            data="true" if idle else "false",
        )

    @staticmethod
    def registry_node_metadata(request: snailjob_pb2.GrpcSnailJobRequest):
        from .. import ExecutorManager
        ExecutorManager.registry_node_metadata_to_server()
        return snailjob_pb2.GrpcResult(
            reqId=request.reqId,
            status=1,
            message="",
            data="true",
        )


def run_grpc_server(port: int):
    """运行客户端服务器

    Args:
        host (str): 主机 (IP, 域名)
        port (int): 服务端口
    """
    # 创建线程池执行器
    thread_pool = futures.ThreadPoolExecutor(
        thread_name_prefix="snail-job-server",
        max_workers=settings.snail_grpc_server_max_workers
    )
    
    # 配置服务端选项
    server_options = [
        # Keepalive 配置
        ('grpc.keepalive_time_ms', settings.snail_grpc_server_keepalive_time * 1000),
        ('grpc.keepalive_timeout_ms', settings.snail_grpc_server_keepalive_timeout * 1000),
        ('grpc.keepalive_permit_without_calls', settings.snail_grpc_server_keepalive_permit_without_calls),
        # 连接超时配置
        ('grpc.max_connection_idle_ms', settings.snail_grpc_server_max_connection_idle * 1000),
        ('grpc.max_connection_age_ms', settings.snail_grpc_server_max_connection_age * 1000),
        ('grpc.max_connection_age_grace_ms', 10000),  # 连接关闭宽限时间 10秒
        # HTTP/2 配置
        ('grpc.http2.max_pings_without_data', 0),
        ('grpc.http2.min_time_between_pings_ms', 10000),
        ('grpc.http2.min_ping_interval_without_data_ms', 300000),  # 5分钟
    ]
    
    server = grpc.server(thread_pool, options=server_options)

    # todo 这里添加 GRPC服务端线程池 监控
    #     GRPC_SERVER_POOL_ACTIVE("grpc_server_pool_active", new String[]{}, MetricsType.GAUGE),
    #     GRPC_SERVER_POOL_SIZE("grpc_server_pool_size", new String[]{}, MetricsType.GAUGE),
    #     GRPC_SERVER_POOL_QUEUE_SIZE("grpc_server_pool_queue_size", new String[]{}, MetricsType.GAUGE),
    _start_grpc_server_pool_monitoring(thread_pool)

    snailjob_pb2_grpc.add_UnaryRequestServicer_to_server(SnailJobServicer(), server)
    server.add_insecure_port(f"0.0.0.0:{port}")
    server.start()
    try:
        while True:
            time.sleep(SLEEP_SECONDS)
    except KeyboardInterrupt:
        SnailLog.LOCAL.info("KeyboardInterrupt, 退出程序")
        server.stop(0)


def _start_grpc_server_pool_monitoring(thread_pool):
    """启动gRPC服务器线程池监控"""
    import threading
    
    def monitor_grpc_server_pool():
        """监控gRPC服务器线程池"""
        while True:
            try:
                metrics = get_metrics()
                
                # 获取线程池状态
                active_threads = len(thread_pool._threads) if hasattr(thread_pool, '_threads') else 0
                max_workers = thread_pool._max_workers if hasattr(thread_pool, '_max_workers') else 0
                queue_size = thread_pool._work_queue.qsize() if hasattr(thread_pool, '_work_queue') else 0
                
                # 更新gRPC服务器线程池指标
                metrics.set_grpc_server_pool_metrics(active_threads, max_workers, queue_size)
                
                time.sleep(5)  # 每5秒更新一次
            except Exception as e:
                SnailLog.LOCAL.debug(f"gRPC server pool monitoring error: {e}")
                time.sleep(10)  # 出错时延长间隔
    
    # 启动监控线程
    monitor_thread = threading.Thread(target=monitor_grpc_server_pool, daemon=True, name="grpc-server-pool-monitor")
    monitor_thread.start()
