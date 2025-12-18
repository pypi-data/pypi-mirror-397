"""
服务基类模块

定义所有业务服务需要继承的基类，提供统一的 run 方法接口。
并提供统一的 Service 元信息装饰器：@service(id="...", name="...")。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, Callable


def service(*, id: str, name: str) -> Callable:
    """
    业务 Service 元信息装饰器（推荐统一从 executor 顶层导入：from executor import BaseService, service）。

    设计目标：
    - id：稳定且唯一的标识（必填，例如 HR-000001）
    - name：展示名称（必填，支持中文）
    """

    if not isinstance(id, str) or not id.strip():
        raise ValueError("service 装饰器参数 id 必须为非空字符串")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("service 装饰器参数 name 必须为非空字符串")

    def decorator(cls):
        # 仅供运行时调试/自省；执行器动态注册扫描使用 AST，不依赖该属性
        setattr(cls, "__service_id__", id.strip())
        setattr(cls, "__service_name__", name.strip())
        return cls

    return decorator


class BaseService(ABC):
    """
    业务服务基类

    所有业务服务都需要继承此类，实现 run 方法。
    执行器会实例化此类并调用 _run_with_context 方法。
    """

    def __init__(self):
        """初始化服务"""
        self.browser = None

    @asynccontextmanager
    async def use_browser_manager(self, manager_class=None, **kwargs):
        """
        使用 BrowserManager 的上下文管理器（自动管理实例属性）

        自动将 BrowserManager 实例赋值给 self.browser，
        在异常处理时可以直接使用 self._build_error_data() 而无需传参。
        """
        # 默认使用 BrowserCDPManager
        if manager_class is None:
            from executor.playwright import BrowserCDPManager

            manager_class = BrowserCDPManager

        async with manager_class(**kwargs) as browser:
            self.browser = browser
            yield browser

    def _set_job_context(self, job_id: int, task_batch_id: int):
        """设置日志上下文"""
        try:
            from executor.logger import _job_context_var

            _job_context_var.set((job_id, task_batch_id))
        except ImportError:
            pass

    async def _run_with_context(self, job_id: int, task_batch_id: int, extra_params: dict = None) -> Any:
        """带日志上下文的运行方法"""
        self._set_job_context(job_id, task_batch_id)
        return await self.run(job_id, task_batch_id, extra_params)

    @abstractmethod
    async def run(self, job_id: int, task_batch_id: int, extra_params: dict = None) -> Any:
        """执行业务逻辑的抽象方法"""
        raise NotImplementedError


