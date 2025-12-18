import json
import time
from typing import Any

import grpc

from snailjob.config import get_snailjob_settings
from snailjob.grpc import snailjob_pb2, snailjob_pb2_grpc
from snailjob.log import SnailLog
from snailjob.schemas import SnailJobRequest, StatusEnum

# 全局配置实例
settings = get_snailjob_settings()


def send_to_server(uri: str, payload: Any, job_name: str) -> StatusEnum:
    """发送请求到程服务器（手动实现重试机制）"""
    request = SnailJobRequest.build(args=[payload])

    # 重试配置
    max_attempts = settings.snail_grpc_client_max_attempts
    per_request_timeout = settings.snail_grpc_client_timeout / max_attempts
    initial_backoff = 0.5  # 初始退避时间（秒）
    max_backoff = 2.0  # 最大退避时间（秒）
    backoff_multiplier = 2  # 退避倍数

    # 配置客户端 channel 选项（移除自动重试配置，改用手动重试）
    channel_options = [
        ('grpc.keepalive_time_ms', 30000),  # 30秒发送一次keepalive
        ('grpc.keepalive_timeout_ms', 5000),  # 5秒keepalive超时
        ('grpc.keepalive_permit_without_calls', True),
        ('grpc.http2.max_pings_without_data', 0),
        ('grpc.http2.min_time_between_pings_ms', 10000),
        ('grpc.http2.min_ping_interval_without_data_ms', 300000),  # 5分钟
    ]

    SnailLog.LOCAL.debug(
        f"{job_name}开始: reqId={request.reqId}, "
        f"单次超时={per_request_timeout:.1f}秒, 最大尝试={max_attempts}次"
    )

    # 手动实现重试逻辑
    last_error = None
    backoff = initial_backoff

    for attempt in range(1, max_attempts + 1):
        try:
            attempt_start = time.time()

            with grpc.insecure_channel(
                    f"{settings.snail_server_host}:{settings.snail_server_port}",
                    options=channel_options
            ) as channel:
                # 等待 channel 就绪（最多等待 per_request_timeout 秒）
                grpc.channel_ready_future(channel).result(timeout=per_request_timeout)

                stub = snailjob_pb2_grpc.UnaryRequestStub(channel)
                req = snailjob_pb2.GrpcSnailJobRequest(
                    reqId=request.reqId,
                    metadata=snailjob_pb2.Metadata(
                        uri=uri,
                        headers=settings.snail_headers,
                    ),
                    body=json.dumps([payload]),
                )

                # 单次请求超时
                response = stub.unaryRequest(req, timeout=per_request_timeout)

                attempt_duration = time.time() - attempt_start

                assert request.reqId == response.reqId, "reqId 不一致的!"

                if response.status == StatusEnum.YES:
                    if attempt > 1:
                        SnailLog.LOCAL.info(
                            f"{job_name}成功(第{attempt}次尝试): reqId={request.reqId}, "
                            f"耗时={attempt_duration:.2f}秒"
                        )
                    else:
                        SnailLog.LOCAL.info(f"{job_name}成功: reqId={request.reqId}")

                    try:
                        SnailLog.LOCAL.debug(f"data={payload.model_dump(mode='json')}")
                    except Exception:
                        SnailLog.LOCAL.debug(f"data={payload}")
                else:
                    SnailLog.LOCAL.error(f"{job_name}失败: {response.message}")

                return response.status

        except grpc.RpcError as ex:
            error_code = ex.code()
            error_details = ex.details()
            attempt_duration = time.time() - attempt_start

            # 判断是否应该重试
            should_retry = error_code in [
                grpc.StatusCode.UNAVAILABLE,
                grpc.StatusCode.DEADLINE_EXCEEDED,
                grpc.StatusCode.UNKNOWN,
            ]

            if should_retry and attempt < max_attempts:
                SnailLog.LOCAL.warning(
                    f"{job_name}第{attempt}次尝试失败: reqId={request.reqId}, "
                    f"错误码={error_code}, 耗时={attempt_duration:.2f}秒, "
                    f"将在{backoff:.1f}秒后重试"
                )
                time.sleep(backoff)
                backoff = min(backoff * backoff_multiplier, max_backoff)
            else:
                # 最后一次尝试或不可重试的错误
                if error_code == grpc.StatusCode.DEADLINE_EXCEEDED:
                    SnailLog.LOCAL.error(
                        f"gRPC请求超时(已重试{attempt}次): {job_name}, reqId={request.reqId}, "
                        f"单次超时={per_request_timeout:.1f}秒, 总耗时={attempt_duration:.2f}秒, "
                        f"错误详情={error_details}"
                    )
                elif error_code == grpc.StatusCode.UNAVAILABLE:
                    SnailLog.LOCAL.error(
                        f"gRPC服务不可用(已重试{attempt}次): {job_name}, reqId={request.reqId}, "
                        f"服务器={settings.snail_server_host}:{settings.snail_server_port}, "
                        f"错误详情={error_details}"
                    )
                else:
                    SnailLog.LOCAL.error(
                        f"gRPC请求失败(已重试{attempt}次): {job_name}, reqId={request.reqId}, "
                        f"错误码={error_code}, 错误详情={error_details}"
                    )
                break

        except Exception as ex:
            # 其他异常（如 channel_ready 超时）
            attempt_duration = time.time() - attempt_start
            if attempt < max_attempts:
                SnailLog.LOCAL.warning(
                    f"{job_name}第{attempt}次尝试异常: reqId={request.reqId}, "
                    f"异常={type(ex).__name__}: {str(ex)}, 耗时={attempt_duration:.2f}秒, "
                    f"将在{backoff:.1f}秒后重试"
                )
                time.sleep(backoff)
                backoff = min(backoff * backoff_multiplier, max_backoff)
            else:
                SnailLog.LOCAL.error(
                    f"gRPC请求异常(已重试{attempt}次): {job_name}, reqId={request.reqId}, "
                    f"异常={type(ex).__name__}: {str(ex)}"
                )
                break

    return StatusEnum.NO
