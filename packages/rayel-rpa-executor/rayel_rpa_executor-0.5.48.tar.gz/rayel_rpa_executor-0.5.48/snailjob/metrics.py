"""
Prometheus metrics collection module for Snail Job
"""
from __future__ import annotations

from prometheus_client import (
    Counter,
    Gauge,
    REGISTRY,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST, Summary,
)
import psutil


class SnailJobMetrics:
    """Snail Job Prometheus metrics collector"""

    def __init__(self, registry: CollectorRegistry = None):
        """Initialize metrics collector
        
        Args:
            registry: Prometheus registry to use, defaults to default registry
        """
        self.registry = registry or REGISTRY
        
        # 执行线程池缓存监控 (对应Java的job_thread_pool_cache)
        self.job_thread_pool_cache = Gauge(
            'job_thread_pool_cache',
            'Thread pool cache metrics',
            ['application'],  # metric_type: active, size, queue_size
            registry=self.registry
        )
        
        # 任务执行时长监控 (对应Java的job_task_client_execution_duration)
        self.job_task_client_execution_duration = Summary(
            'job_task_client_execution_duration',
            'Job task client execution duration in seconds',
            ['job_id', 'application'],
            registry=self.registry
        )
        
        # 任务调度结果错误监控 (对应Java的job_dispatch_result_error)
        self.job_dispatch_result_error = Counter(
            'job_dispatch_result_error',
            'Total number of job dispatch result errors',
            ['job_id', 'application'],
            registry=self.registry
        )
        
        # RPC请求总数监控 (对应Java的rpc_request_total)
        self.rpc_request_total = Counter(
            'rpc_request_total',
            'Total number of RPC requests',
            ['application'],
            registry=self.registry
        )
        
        # gRPC服务器线程池监控 (对应Java的GRPC_SERVER_POOL_*)
        self.grpc_server_pool_active = Gauge(
            'grpc_server_pool_active',
            'Number of active threads in gRPC server pool',
            ['application'],
            registry=self.registry
        )
        
        self.grpc_server_pool_size = Gauge(
            'grpc_server_pool_size',
            'Total number of threads in gRPC server pool',
            ['application'],
            registry=self.registry
        )
        
        self.grpc_server_pool_queue_size = Gauge(
            'grpc_server_pool_queue_size',
            'Number of queued tasks in gRPC server pool',
            ['application'],
            registry=self.registry
        )

        # 进程CPU使用率监控
        self.system_cpu_usage = Gauge(
            'system_cpu_usage',
            'Current process CPU usage percentage',
            ['application'],
            registry=self.registry
        )

        # 系统1分钟平均负载监控
        self.system_load_average_1m = Gauge(
            'system_load_average_1m',
            'System 1-minute load average',
            ['application'],
            registry=self.registry
        )

    def set_thread_pool_cache(self, value: int) -> None:
        """Set thread pool cache metrics"""
        self.job_thread_pool_cache.labels(
            application = "snailjob"
        ).set(value)
    
    def record_job_execution_duration(self, job_id: str, duration: float) -> None:
        """Record job execution duration"""
        self.job_task_client_execution_duration.labels(
            job_id=job_id,
            application="snailjob"
        ).observe(duration)
    
    def record_dispatch_result_error(self, job_id: str) -> None:
        """Record job dispatch result error"""
        self.job_dispatch_result_error.labels(
            job_id=job_id,
            application="snailjob"
        ).inc()
    
    def record_rpc_request(self) -> None:
        """Record RPC request"""
        self.rpc_request_total.labels(
            application="snailjob"
        ).inc()
    
    def set_grpc_server_pool_metrics(self, active: int, size: int, queue_size: int) -> None:
        """Set gRPC server pool metrics"""
        self.grpc_server_pool_active.labels(
            application="snailjob"
        ).set(active)
        self.grpc_server_pool_size.labels(
            application="snailjob"
        ).set(size)
        self.grpc_server_pool_queue_size.labels(
            application="snailjob"
        ).set(queue_size)

    def update_system_metrics(self) -> None:
        """Update system metrics (CPU usage and load average)"""
        try:
            # 更新进程CPU使用率
            process = psutil.Process()
            cpu_percent = process.cpu_percent(interval=1) / psutil.cpu_count()
            self.system_cpu_usage.labels(application="snailjob").set(cpu_percent / 100)
            
            # 更新系统1分钟平均负载
            load_avg = psutil.getloadavg()[0]  # 获取1分钟负载
            self.system_load_average_1m.labels(application="snailjob").set(load_avg)
            
        except Exception as e:
            # 如果获取系统指标失败，设置为0
            self.system_cpu_usage.labels(application="snailjob").set(0)
            self.system_load_average_1m.labels(application="snailjob").set(0)

    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        return generate_latest(self.registry).decode('utf-8')

    def get_content_type(self) -> str:
        """Get content type for metrics response"""
        return CONTENT_TYPE_LATEST


# Global metrics instance
_metrics_instance: SnailJobMetrics = None


def get_metrics() -> SnailJobMetrics:
    """Get the global metrics instance"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = SnailJobMetrics()
    return _metrics_instance


def configure_metrics(registry: CollectorRegistry = None) -> SnailJobMetrics:
    """Configure metrics with custom registry
    
    Args:
        registry: Custom Prometheus registry
        
    Returns:
        SnailJobMetrics: Configured metrics instance
    """
    global _metrics_instance
    _metrics_instance = SnailJobMetrics(registry)
    return _metrics_instance
