from __future__ import annotations

import json
import random
import string
from typing import Dict, Optional

from dotenv import load_dotenv
from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

SNAIL_VERSION = "0.1.3"


class SnailJobSettings(BaseSettings):
    """Snail Job 配置类，基于 Pydantic Settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 服务器配置
    snail_server_host: str = Field(default="127.0.0.1", description="服务器主机地址")
    snail_server_port: int = Field(default=17888, description="服务器端口")  # 改为 int

    # 客户端配置
    snail_version: str = Field(default=SNAIL_VERSION, frozen=True, description="客户端版本")
    snail_host_ip: str = Field(default="127.0.0.1", description="客户端主机IP")
    snail_host_port: int = Field(default=17889, description="客户端端口")
    snail_namespace: str = Field(default="764d604ec6fc45f68cd92514c40e9e1a", description="命名空间")
    snail_group_name: str = Field(default="snail_job_demo_group", description="组名")
    snail_token: str = Field(default="SJ_Wyz3dmsdbDOkDujOTSSoBjGQP1BMsVnj", description="认证令牌")
    snail_labels: str = Field(default="env:dev,app:demo", description="标签配置")

    # 日志配置
    snail_log_level: str = Field(default="INFO", description="日志级别")
    snail_log_format: str = Field(
        default="%(asctime)s | %(name)-22s | %(levelname)-8s | %(message)s", description="日志格式"
    )
    snail_log_remote_interval: int = Field(default=5, gt=0, description="远程日志上报间隔(秒)")
    snail_log_remote_buffer_size: int = Field(default=1000, gt=0, description="远程日志缓冲区大小(超过会全部丢弃)")
    snail_log_remote_batch_size: int = Field(default=50, gt=0, description="远程日志上报间隔总量窗口期(设置太大影响上报性能)")
    snail_log_local_filename: str = Field(default="log/snailjob.log", description="本地日志文件名")
    snail_log_local_backup_count: int = Field(default=60, ge=0, description="本地日志备份数量")

    # 系统配置
    executor_type_python: str = Field(default="2", frozen=True, description="Python执行器类型")
    # deprecated
    system_version: str = Field(default=SNAIL_VERSION, frozen=True, description="系统版本")
    root_map: str = Field(default="ROOT_MAP", description="根映射")

    # Prometheus监控配置
    snail_prometheus_enabled: bool = Field(default=True, description="是否启用Prometheus监控")
    snail_prometheus_port: int = Field(default=8020, description="Prometheus metrics端口")
    snail_prometheus_host: str = Field(default="0.0.0.0", description="Prometheus metrics主机地址")
    snail_prometheus_path: str = Field(default="/actuator/prometheus", description="Prometheus metrics路径")

    # gRPC配置
    snail_grpc_client_max_attempts: int = Field(default=4, gt=0, description="最大重试次数")
    snail_grpc_client_timeout: int = Field(default=10, gt=0, description="gRPC客户端请求超时时间(秒)")
    snail_grpc_server_max_workers: int = Field(default=10, gt=0, description="gRPC服务端线程池最大工作线程数")
    snail_grpc_server_keepalive_time: int = Field(default=30, gt=0, description="gRPC服务端keepalive时间(秒)")
    snail_grpc_server_keepalive_timeout: int = Field(default=5, gt=0, description="gRPC服务端keepalive超时时间(秒)")
    snail_grpc_server_keepalive_permit_without_calls: bool = Field(default=True, description="gRPC服务端允许无调用的keepalive")
    snail_grpc_server_max_connection_idle: int = Field(default=300, gt=0, description="gRPC服务端最大连接空闲时间(秒)")
    snail_grpc_server_max_connection_age: int = Field(default=3600, gt=0, description="gRPC服务端最大连接存活时间(秒)")

    # outbox 配置（执行结果可靠上报）
    outbox_db_path: str = Field(
        default="data/outbox/dispatch_results.db",
        description="执行结果 outbox 的 SQLite DB 文件路径",
    )
    outbox_reporter_workers: int = Field(default=2, gt=0, description="后台结果上报 worker 数")
    outbox_retry_base_seconds: float = Field(default=1.0, gt=0, description="结果上报重试退避基数(秒)")
    outbox_retry_max_seconds: float = Field(default=60.0, gt=0, description="结果上报重试退避上限(秒)")
    outbox_max_report_age_seconds: int = Field(
        default=3600, gt=0, description="单条结果允许的最长上报窗口(秒)，超过则放弃上报"
    )
    outbox_sqlite_timeout_seconds: float = Field(
        default=1.0, gt=0, description="outbox sqlite 等待锁的最大时间(秒)，避免启动卡死"
    )
    outbox_wait_ack_poll_seconds: float = Field(
        default=0.5, gt=0, description="等待结果上报 ACK 的轮询间隔(秒)"
    )

    # 日志 outbox（批量日志可靠上报）
    log_outbox_db_path: str = Field(
        default="data/outbox/log_batches.db",
        description="日志批量上报 outbox 的 SQLite DB 文件路径",
    )
    log_outbox_reporter_workers: int = Field(default=2, gt=0, description="后台日志上报 worker 数")
    log_outbox_retry_base_seconds: float = Field(default=1.0, gt=0, description="日志上报重试退避基数(秒)")
    log_outbox_retry_max_seconds: float = Field(default=60.0, gt=0, description="日志上报重试退避上限(秒)")
    log_outbox_max_report_age_seconds: int = Field(
        default=3600, gt=0, description="单条日志批次允许的最长上报窗口(秒)，超过则放弃"
    )
    log_outbox_sqlite_timeout_seconds: float = Field(
        default=1.0, gt=0, description="日志 outbox sqlite 等待锁的最大时间(秒)，避免阻塞"
    )
    outbox_monitor_interval_seconds: int = Field(
        default=30,
        ge=0,
        description="结果 outbox 队列监控日志间隔(秒)，0 表示关闭",
    )
    log_outbox_monitor_interval_seconds: int = Field(
        default=30,
        ge=0,
        description="日志 outbox 队列监控日志间隔(秒)，0 表示关闭",
    )
    outbox_keep_latest_acked: int = Field(
        default=0,
        ge=0,
        description="结果 outbox 已完成(acked/ack_failed)记录保留最近 N 条，0 表示不保留",
    )
    outbox_clear_acked_max_delete: int = Field(
        default=1000,
        ge=0,
        description="结果 outbox 单次清理最多删除条数（防止长事务）",
    )
    log_outbox_keep_latest_acked: int = Field(
        default=0,
        ge=0,
        description="日志 outbox 已完成(acked/ack_failed)记录保留最近 N 条，0 表示不保留",
    )
    log_outbox_clear_acked_max_delete: int = Field(
        default=1000,
        ge=0,
        description="日志 outbox 单次清理最多删除条数（防止长事务）",
    )
    outbox_vacuum_interval_seconds: int = Field(
        default=3600,
        ge=0,
        description="结果 outbox 定期 VACUUM 间隔(秒)，0 表示关闭（注意：VACUUM 有锁/IO 开销）",
    )
    log_outbox_vacuum_interval_seconds: int = Field(
        default=3600,
        ge=0,
        description="日志 outbox 定期 VACUUM 间隔(秒)，0 表示关闭（注意：VACUUM 有锁/IO 开销）",
    )
    outbox_vacuum_sqlite_timeout_seconds: float = Field(
        default=5.0,
        gt=0,
        description="VACUUM sqlite 连接超时(秒)，避免被锁时长时间阻塞",
    )

    @field_validator("snail_log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """验证日志级别"""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"日志级别必须是以下之一: {valid_levels}")
        return v.upper()

    @field_validator("snail_labels")
    @classmethod
    def validate_labels(cls, v: str) -> str:
        """验证标签格式"""
        if not v:
            return v
        for item in v.split(","):
            if ":" not in item:
                raise ValueError(f"标签格式错误: '{item}'，应为 'key:value' 格式")
        return v

    _host_id: Optional[str] = None

    @computed_field
    @property
    def snail_host_id(self) -> str:
        """生成的主机ID，只生成一次"""
        if self._host_id is None:
            self._host_id = "py-" + "".join(random.choice(string.digits) for _ in range(7))
        return self._host_id

    @computed_field
    @property
    def label_dict(self) -> Dict[str, str]:
        """解析标签字典"""
        labels = {}
        for item in self.snail_labels.split(","):
            if ":" in item:
                key, value = item.split(":", 1)
                labels[key.strip()] = value.strip()
        labels["state"] = "up"
        return labels

    @computed_field
    @property
    def snail_headers(self) -> Dict[str, str]:
        """生成请求头"""
        return {
            "host-id": self.snail_host_id,
            "host-ip": self.snail_host_ip,
            "version": self.snail_version,
            "host-port": str(self.snail_host_port),
            "namespace": self.snail_namespace,
            "group-name": self.snail_group_name,
            "token": self.snail_token,
            "content-type": "application/json",
            "executor-type": self.executor_type_python,
            "system-version": self.system_version,
            "web-port": str(self.snail_prometheus_port)
            # "label": json.dumps(self.label_dict),
        }


# 全局配置实例 - 延迟初始化
_settings: SnailJobSettings | None = None


def get_snailjob_settings() -> SnailJobSettings:
    """获取配置实例，支持延迟初始化

    Returns:
        SnailJobSettings: 配置实例
    """
    global _settings
    if _settings is None:
        load_dotenv()
        _settings = SnailJobSettings()
    return _settings


def configure_settings(**kwargs) -> SnailJobSettings:
    """配置设置，允许用户自定义配置

    Args:
        **kwargs: 配置参数

    Returns:
        SnailJobSettings: 新的配置实例

    Example:
        >>> from snailjob.config import configure_settings
        >>> settings = configure_settings(snail_server_host="192.168.1.100")
    """
    global _settings
    _settings = SnailJobSettings(**kwargs)
    return _settings
