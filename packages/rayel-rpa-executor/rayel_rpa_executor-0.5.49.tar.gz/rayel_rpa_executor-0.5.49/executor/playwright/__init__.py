"""
Playwright 核心模块 - 提供给业务项目使用

包含：
- logger: 日志管理（统一接口）
- BrowserManager: 统一浏览器管理（浏览器池+自动清理）
- LoginManager: 统一登录管理（解决并发登录冲突）
- BasePage: 页面对象基类（POM模式）
- BaseService: 业务服务基类
"""

# 从executor根目录导入统一的logger
from executor.logger import logger, _job_context_var
from .browser_manager import BrowserManager, EnvironmentDetector, UserAgent
from .browser_manager_cdp import BrowserCDPManager
from .login_manager import (
    LoginManager,
    LoginStatus,
    LoginResult,
    login_with_retry
)
__all__ = [
    # 日志
    'logger',
    '_job_context_var',  # 上下文变量（供内部使用）
    
    # 浏览器管理
    'BrowserManager',
    'BrowserCDPManager',
    'EnvironmentDetector',
    'UserAgent',
    
    # 登录管理
    'LoginManager',
    'LoginStatus',
    'LoginResult',
    'login_with_retry',
    ]