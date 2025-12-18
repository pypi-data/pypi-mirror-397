"""
通用操作包装器工具
提供重试、日志记录、错误处理等通用功能，可用于任意函数或方法
支持同步和异步函数
"""
import asyncio
import time
import traceback
import inspect
from typing import Optional, Callable
from enum import Enum
from functools import wraps
from executor.logger import logger

# 默认配置常量
DEFAULT_TIMEOUT = 15000  # 默认超时时间（毫秒）


class ErrorStrategy(Enum):
    """异常处理策略"""
    RAISE = "raise"      # 抛出异常
    IGNORE = "ignore"    # 忽略异常
    RETRY = "retry"      # 重试


class ActionConfig:
    """操作配置类"""
    
    def __init__(
        self,
        timeout: Optional[float] = DEFAULT_TIMEOUT / 1000,           # 超时时间（秒）
        wait_before: float = 0,                     # 执行前等待（秒）
        wait_after: float = 0,                      # 执行后等待（秒）
        error_strategy: ErrorStrategy = ErrorStrategy.RAISE,  # 异常策略
        retry_times: int = 2,                       # 重试次数
        retry_interval: float = 1.0,                # 重试间隔（秒）
        ignore_exceptions: tuple = (Exception,),    # 忽略的异常类型
    ):
        self.timeout = timeout
        self.wait_before = wait_before
        self.wait_after = wait_after
        self.error_strategy = error_strategy
        self.retry_times = retry_times
        self.retry_interval = retry_interval
        self.ignore_exceptions = ignore_exceptions
    
    def merge(self, **kwargs) -> 'ActionConfig':
        """合并配置，返回新的配置对象"""
        params = {
            'timeout': kwargs.get('timeout', self.timeout),
            'wait_before': kwargs.get('wait_before', self.wait_before),
            'wait_after': kwargs.get('wait_after', self.wait_after),
            'error_strategy': kwargs.get('error_strategy', self.error_strategy),
            'retry_times': kwargs.get('retry_times', self.retry_times),
            'retry_interval': kwargs.get('retry_interval', self.retry_interval),
            'ignore_exceptions': kwargs.get('ignore_exceptions', self.ignore_exceptions),
        }
        return ActionConfig(**params)


# 全局默认配置
GLOBAL_DEFAULT_CONFIG = ActionConfig()


def _get_config_and_desc(func, args, kwargs, action_name, description):
    """
    辅助函数：提取配置和描述
    """
    # 尝试获取基准配置
    base_config = GLOBAL_DEFAULT_CONFIG
    
    # 检查第一个参数是否为 self 且有 default_config 属性
    if args:
        self_obj = args[0]
        if hasattr(self_obj, 'default_config') and isinstance(self_obj.default_config, ActionConfig):
            base_config = self_obj.default_config

    # 提取配置参数
    timeout = kwargs.pop('timeout', None)
    wait_before = kwargs.pop('wait_before', None)
    wait_after = kwargs.pop('wait_after', None)
    error_strategy = kwargs.pop('error_strategy', None)
    retry_times = kwargs.pop('retry_times', None)
    retry_interval = kwargs.pop('retry_interval', None)
    # description 已经在闭包中处理或者这里再次提取
    
    # 合并配置
    cfg = base_config.merge(
        timeout=timeout,
        wait_before=wait_before if wait_before is not None else base_config.wait_before,
        wait_after=wait_after if wait_after is not None else base_config.wait_after,
        error_strategy=error_strategy or base_config.error_strategy,
        retry_times=retry_times if retry_times is not None else base_config.retry_times,
        retry_interval=retry_interval if retry_interval is not None else base_config.retry_interval,
    )
    
    # 确定超时时间（转为毫秒）
    timeout_ms = int((cfg.timeout or (DEFAULT_TIMEOUT / 1000)) * 1000)
    
    # 构建描述
    name = action_name or func.__name__
    desc_arg = ""
    if args:
        effective_args = args[1:] if (len(args) > 0 and hasattr(args[0], 'default_config')) else args
        if effective_args:
            desc_arg = str(effective_args[0])
    
    desc = description or (desc_arg if desc_arg else name)
    
    return cfg, timeout_ms, name, desc


def _log_start(name, desc, cfg):
    """辅助函数：记录开始日志"""
    param_info = []
    if cfg.timeout:
        param_info.append(f"timeout={cfg.timeout}s")
    if cfg.wait_before > 0:
        param_info.append(f"wait_before={cfg.wait_before}s")
    if cfg.wait_after > 0:
        param_info.append(f"wait_after={cfg.wait_after}s")
    if cfg.error_strategy != ErrorStrategy.RAISE:
        param_info.append(f"strategy={cfg.error_strategy.value}")
    if cfg.retry_times > 0:
        param_info.append(f"retry={cfg.retry_times}")
    
    params_str = f" [{', '.join(param_info)}]" if param_info else ""
    logger.REMOTE.info(f"[{name}][开始] {desc}{params_str}")


def _log_success(name, desc, attempt, elapsed):
    """辅助函数：记录成功日志"""
    elapsed_str = f"{elapsed:.2f}s"
    if attempt > 0:
        logger.REMOTE.info(f"[{name}][成功] 重试成功 (第{attempt + 1}次尝试, 耗时{elapsed_str}) - {desc}")
    else:
        logger.REMOTE.info(f"[{name}][成功] 操作完成 (耗时{elapsed_str}) - {desc}")


def _log_retry(name, attempt, max_attempts, elapsed, max_retry_interval, e, desc):
    """辅助函数：记录重试/失败日志"""
    error_type = type(e).__name__
    error_msg = str(e)
    if len(error_msg) > 200:
        error_msg = error_msg[:200] + "..."
    
    logger.REMOTE.warning(
        f"[{name}][失败] 第{attempt}/{max_attempts}次尝试失败 "
        f"(耗时{elapsed:.2f}s) - {desc}\n"
        f"  └─ 异常类型: {error_type}\n"
        f"  └─ 异常信息: {error_msg}"
    )
    
    if attempt < max_attempts:
         logger.REMOTE.info(
            f"[{name}][重试] {max_retry_interval}s 后进行第{attempt + 1}次重试 "
            f"(剩余{max_attempts - attempt}次机会)"
        )


def _handle_final_failure(name, desc, start_time, last_exception, cfg):
    """辅助函数：处理最终失败"""
    if not last_exception:
        return None
        
    elapsed = time.time() - start_time
    error_type = type(last_exception).__name__
    error_msg = str(last_exception)
    
    if cfg.error_strategy == ErrorStrategy.IGNORE:
        logger.REMOTE.warning(
            f"[{name}][忽略] 操作失败但已忽略 (耗时{elapsed:.2f}s) - {desc}\n"
            f"  └─ 异常类型: {error_type}\n"
            f"  └─ 异常信息: {error_msg}"
        )
        return None
    elif cfg.error_strategy == ErrorStrategy.RAISE:
        logger.REMOTE.error(
            f"[{name}][异常] 操作失败，抛出异常 (耗时{elapsed:.2f}s) - {desc}\n"
            f"  └─ 异常类型: {error_type}\n"
            f"  └─ 异常信息: {error_msg}"
        )
        logger.REMOTE.debug(f"[{name}][堆栈]\n{traceback.format_exc()}")
        raise last_exception
    else:  # RETRY 但已达到最大重试次数
        logger.REMOTE.error(
            f"[{name}][异常] 重试{cfg.retry_times}次后仍失败 (总耗时{elapsed:.2f}s) - {desc}\n"
            f"  └─ 异常类型: {error_type}\n"
            f"  └─ 异常信息: {error_msg}"
        )
        logger.REMOTE.debug(f"[{name}][堆栈]\n{traceback.format_exc()}")
        raise last_exception


def action_wrapper(action_name: str = None):
    """
    操作包装器装饰器（支持同步和异步）
    自动处理日志、等待、异常、重试等通用逻辑
    """
    def decorator(func: Callable) -> Callable:
        
        is_coroutine = inspect.iscoroutinefunction(func)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            description = kwargs.pop('description', None)
            cfg, timeout_ms, name, desc = _get_config_and_desc(func, args, kwargs, action_name, description)
            
            _log_start(name, desc, cfg)
            
            if cfg.wait_before > 0:
                await asyncio.sleep(cfg.wait_before)
            
            attempt = 0
            max_attempts = (cfg.retry_times + 1) if cfg.error_strategy == ErrorStrategy.RETRY else 1
            last_exception = None
            start_time = time.time()
            
            while attempt < max_attempts:
                try:
                    # 检查timeout参数支持
                    sig = inspect.signature(func)
                    call_kwargs = kwargs.copy()
                    if 'timeout' in sig.parameters:
                        call_kwargs['timeout'] = timeout_ms
                    
                    result = await func(*args, **call_kwargs)
                    
                    if cfg.wait_after > 0:
                        await asyncio.sleep(cfg.wait_after)
                    
                    elapsed = time.time() - start_time
                    _log_success(name, desc, attempt, elapsed)
                    return result
                    
                except Exception as e:
                    last_exception = e
                    attempt += 1
                    elapsed = time.time() - start_time
                    
                    # 判断是否继续
                    should_retry = (
                        attempt < max_attempts and 
                        cfg.error_strategy == ErrorStrategy.RETRY
                    )
                    
                    # 记录日志
                    if should_retry or attempt == max_attempts:
                         _log_retry(name, attempt, max_attempts, elapsed, cfg.retry_interval, e, desc)

                    if should_retry:
                        await asyncio.sleep(cfg.retry_interval)
                        continue
                    else:
                        break
            
            return _handle_final_failure(name, desc, start_time, last_exception, cfg)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            description = kwargs.pop('description', None)
            cfg, timeout_ms, name, desc = _get_config_and_desc(func, args, kwargs, action_name, description)
            
            _log_start(name, desc, cfg)
            
            if cfg.wait_before > 0:
                time.sleep(cfg.wait_before)
            
            attempt = 0
            max_attempts = (cfg.retry_times + 1) if cfg.error_strategy == ErrorStrategy.RETRY else 1
            last_exception = None
            start_time = time.time()
            
            while attempt < max_attempts:
                try:
                    # 检查timeout参数支持
                    sig = inspect.signature(func)
                    call_kwargs = kwargs.copy()
                    if 'timeout' in sig.parameters:
                        call_kwargs['timeout'] = timeout_ms
                    
                    result = func(*args, **call_kwargs)
                    
                    if cfg.wait_after > 0:
                        time.sleep(cfg.wait_after)
                    
                    elapsed = time.time() - start_time
                    _log_success(name, desc, attempt, elapsed)
                    return result
                    
                except Exception as e:
                    last_exception = e
                    attempt += 1
                    elapsed = time.time() - start_time
                    
                    should_retry = (
                        attempt < max_attempts and 
                        cfg.error_strategy == ErrorStrategy.RETRY
                    )
                    
                    if should_retry or attempt == max_attempts:
                        _log_retry(name, attempt, max_attempts, elapsed, cfg.retry_interval, e, desc)
                        
                    if should_retry:
                        time.sleep(cfg.retry_interval)
                        continue
                    else:
                        break
            
            return _handle_final_failure(name, desc, start_time, last_exception, cfg)

        return async_wrapper if is_coroutine else sync_wrapper
        
    return decorator
