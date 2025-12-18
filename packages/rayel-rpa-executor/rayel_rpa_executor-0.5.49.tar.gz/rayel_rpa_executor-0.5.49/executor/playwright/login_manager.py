"""
统一登录管理器 - 支持同账号多Context
解决并发登录冲突和账号状态隔离问题

特性：
1. 同一账号的并发登录自动串行化（账号级别锁）
2. 支持同一账号创建多个独立Context（用于Trace隔离）
3. 不同账号完全隔离（独立Context和storage_state）
4. 自动检测登录状态，避免重复登录
5. 登录状态缓存和复用
6. 线程安全的并发控制
7. 提供通用的登录组件（LoginResult、装饰器等）
"""
import asyncio
import os
import hashlib
import time
import functools
from typing import Dict, Callable, Optional, Any, List
from enum import Enum
from dataclasses import dataclass
import uuid
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from executor.logger import logger


# ==================== 通用登录组件 ====================


class LoginStatus(str, Enum):
    """登录状态"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ALREADY_LOGGED_IN = "already_logged_in"


@dataclass
class LoginResult:
    """登录结果"""
    status: LoginStatus
    message: str
    trace_id: str
    username: str
    system: str
    final_url: Optional[str] = None
    error: Optional[Exception] = None


def login_with_retry(
    retry_times: int = 3,
    retry_delay: float = 2.0,
    timeout: float = 30.0,
):
    """
    登录重试装饰器
    
    提供自动重试、超时控制、详细日志功能
    
    Args:
        retry_times: 重试次数，默认3次
        retry_delay: 重试延迟（秒），默认2.0秒
        timeout: 登录超时（秒），默认30.0秒
        
    Examples:
        @login_with_retry()
        async def my_login(page, username, password, target_url, **kwargs):
            # 登录逻辑
            return LoginResult(...)
            
        @login_with_retry(retry_times=5, timeout=60.0)
        async def my_login(page, username, password, target_url, **kwargs):
            # 登录逻辑
            return LoginResult(...)
    """
    def decorator(login_func: Callable) -> Callable:
        @functools.wraps(login_func)
        async def wrapper(page: Page, username: str, password: str, target_url: str, **kwargs) -> LoginResult:
            trace_id = str(uuid.uuid4())
            system_name = kwargs.get('system_name', login_func.__name__.replace('_login', '').upper())
            
            last_error = None
            
            for attempt in range(1, retry_times + 1):
                try:
                    logger.REMOTE.info(
                        f"[{system_name}] 登录尝试 {attempt}/{retry_times} | "
                        f"用户: {username} | TraceID: {trace_id}"
                    )
                    
                    # 执行登录（带超时控制）
                    result = await asyncio.wait_for(
                        login_func(page, username, password, target_url, **kwargs),
                        timeout=timeout
                    )
                    
                    logger.REMOTE.success(
                        f"[{system_name}] 登录成功 ✓ | "
                        f"用户: {username} | TraceID: {trace_id}"
                    )
                    
                    return result
                    
                except asyncio.TimeoutError:
                    last_error = f"登录超时（{timeout}秒）"
                    logger.REMOTE.warning(
                        f"[{system_name}] 登录超时 ⏱ | "
                        f"尝试 {attempt}/{retry_times} | "
                        f"TraceID: {trace_id}"
                    )
                    
                except PlaywrightTimeoutError as e:
                    last_error = f"页面操作超时: {str(e)}"
                    logger.REMOTE.warning(
                        f"[{system_name}] 页面操作超时 ⏱ | "
                        f"尝试 {attempt}/{retry_times} | "
                        f"TraceID: {trace_id}"
                    )
                    
                except Exception as e:
                    last_error = str(e)
                    logger.REMOTE.error(
                        f"[{system_name}] 登录失败 ✗ | "
                        f"错误: {str(e)} | "
                        f"尝试 {attempt}/{retry_times} | "
                        f"TraceID: {trace_id}"
                    )
                
                # 重试前等待
                if attempt < retry_times:
                    logger.REMOTE.info(f"[{system_name}] 等待 {retry_delay}秒后重试...")
                    await asyncio.sleep(retry_delay)
            
            # 所有重试都失败
            logger.REMOTE.error(
                f"[{system_name}] 登录失败（已重试{retry_times}次）✗ | "
                f"用户: {username} | TraceID: {trace_id}"
            )
            
            return LoginResult(
                status=LoginStatus.FAILED,
                message=last_error or "未知错误",
                trace_id=trace_id,
                username=username,
                system=system_name,
                error=Exception(last_error) if last_error else None
            )
        
        return wrapper
    return decorator


# ==================== LoginManager 类 ====================


class LoginManager:
    """
    统一登录管理器
    
    核心设计：
    - 账号级别的登录锁：确保同一账号的登录操作串行化
    - storage_state持久化：登录一次，可创建多个Context复用
    - 支持两种模式：
      * get_or_create_context(): 复用模式，同一账号只有一个Context
      * login_new_context(): 新建模式，同一账号可以创建多个Context
    """
    
    def __init__(
        self,
        browser_manager,
        storage_state_dir: Optional[str] = None,
        login_timeout: int = 30,
        cache_expire: int = 3600  # 登录状态缓存1小时
    ):
        """
        初始化登录管理器
        
        Args:
            browser_manager: BrowserManager实例
            storage_state_dir: 登录状态存储目录（None时自动选择）
            login_timeout: 登录超时时间（秒）
            cache_expire: 登录状态缓存有效期（秒）
        """
        self.browser = browser_manager
        self.login_timeout = login_timeout
        self.cache_expire = cache_expire
        
        # 确定storage_state存储目录
        if storage_state_dir is None:
            if self.browser.is_docker:
                self.storage_state_dir = "/app/data/auth"
            else:
                self.storage_state_dir = os.path.join(os.getcwd(), "data", "auth")
        else:
            self.storage_state_dir = storage_state_dir
        
        os.makedirs(self.storage_state_dir, exist_ok=True)
        
        # 账号级别的登录锁：{account_id: Lock}
        self._account_locks: Dict[str, asyncio.Lock] = {}
        
        # 账号到Context列表的映射：{account_id: [Context1, Context2, ...]}
        self._account_contexts: Dict[str, List[Any]] = {}
        
        # 账号到storage_state路径的映射：{account_id: path}
        self._account_storage_states: Dict[str, str] = {}
        
        # 全局锁（用于管理_account_locks字典）
        self._global_lock = asyncio.Lock()
        
        # Context计数器（用于生成唯一的context名称）
        self._context_counter = 0
        self._counter_lock = asyncio.Lock()
        
        logger.REMOTE.info("=" * 60)
        logger.REMOTE.info("LoginManager 初始化完成")
        logger.REMOTE.info(f"  存储目录: {self.storage_state_dir}")
        logger.REMOTE.info(f"  登录超时: {self.login_timeout}秒")
        logger.REMOTE.info(f"  缓存时长: {self.cache_expire}秒")
        logger.REMOTE.info("=" * 60)
    
    def _get_account_id(self, system: str, username: str) -> str:
        """
        生成账号唯一标识
        
        Args:
            system: 系统名称（如"boss"、"zjpt"等）
            username: 用户名
            
        Returns:
            账号唯一ID（格式: system_username）
        """
        return f"{system}_{username}"
    
    def _get_storage_state_path(self, account_id: str) -> str:
        """
        获取账号的storage_state文件路径
        
        Args:
            account_id: 账号ID
            
        Returns:
            storage_state文件完整路径
        """
        # 使用hash避免特殊字符问题
        safe_id = hashlib.md5(account_id.encode()).hexdigest()[:16]
        return os.path.join(self.storage_state_dir, f"{account_id}_{safe_id}.json")
    
    async def _get_account_lock(self, account_id: str) -> asyncio.Lock:
        """
        获取或创建账号级别的锁（线程安全）
        
        这个锁确保同一账号的登录操作串行化，避免并发登录冲突
        
        Args:
            account_id: 账号ID
            
        Returns:
            该账号的专属锁
        """
        async with self._global_lock:
            if account_id not in self._account_locks:
                self._account_locks[account_id] = asyncio.Lock()
                logger.REMOTE.debug(f"为账号 [{account_id}] 创建登录锁")
            return self._account_locks[account_id]
    
    def _is_storage_state_valid(self, storage_state_path: str) -> bool:
        """
        检查storage_state文件是否有效（存在且未过期）
        
        Args:
            storage_state_path: storage_state文件路径
            
        Returns:
            是否有效
        """
        if not os.path.exists(storage_state_path):
            return False
        
        # 检查文件修改时间
        file_mtime = os.path.getmtime(storage_state_path)
        current_time = time.time()
        
        if current_time - file_mtime > self.cache_expire:
            logger.REMOTE.info(f"登录状态已过期: {storage_state_path}")
            return False
        
        return True
    
    async def _do_login(
        self,
        account_id: str,
        storage_state_path: str,
        target_url: str,
        username: str,
        password: str,
        login_func: Callable,
        **login_kwargs
    ) -> None:
        """
        执行实际的登录操作（内部方法）
        
        Args:
            account_id: 账号ID
            storage_state_path: storage_state保存路径
            target_url: 目标URL
            username: 用户名
            password: 密码
            login_func: 登录函数
            **login_kwargs: 传递给登录函数的其他参数
            
        Raises:
            TimeoutError: 登录超时
            Exception: 登录失败
        """
        logger.REMOTE.info(f"[{account_id}] 开始执行登录操作...")
        
        # 创建临时context用于登录
        # 为什么使用临时context：
        # 1. 登录成功后需要保存storage_state（cookies等）
        # 2. 保存storage_state后，可以复用到多个新context，避免重复登录
        # 3. 临时context的录屏和trace会记录完整的登录过程，便于调试
        temp_context = await self.browser.create_context(
            custom_name=f"login_{account_id}"  # 设置自定义名称，用于trace和视频文件命名
        )
        temp_page = await temp_context.new_page()
        
        login_success = False  # 标记登录是否成功
        
        try:
            # 执行登录（带超时控制）
            await asyncio.wait_for(
                login_func(temp_page, username, password, target_url, **login_kwargs),
                timeout=self.login_timeout
            )
            
            logger.REMOTE.info(f"[{account_id}] ✓ 登录成功")
            login_success = True
            
            # 保存登录状态
            await temp_context.storage_state(path=storage_state_path)
            logger.REMOTE.info(f"[{account_id}] ✓ 登录状态已保存: {storage_state_path}")
            
            # 更新缓存记录
            self._account_storage_states[account_id] = storage_state_path
            
        except asyncio.TimeoutError:
            logger.REMOTE.error(f"[{account_id}] ✗ 登录超时（{self.login_timeout}秒）")
            raise TimeoutError(f"登录超时（{self.login_timeout}秒）")
        
        except Exception as e:
            logger.REMOTE.error(f"[{account_id}] ✗ 登录失败: {e}")
            raise
        
        finally:
            # 关闭临时context并保存trace和录屏
            # 使用browser.close_context确保自动保存trace和视频
            await temp_page.close()
            result = await self.browser.close_context(temp_context)
            
            # 记录保存的文件路径
            if login_success:
                if result.get("trace_path"):
                    logger.REMOTE.info(f"[{account_id}] ✓ 登录过程Trace已保存: {result['trace_path']}")
                if result.get("video_paths"):
                    for video_path in result["video_paths"]:
                        logger.REMOTE.info(f"[{account_id}] ✓ 登录过程录屏已保存: {video_path}")
    
    async def login_new_context(
        self,
        system: str,
        target_url: str,
        username: str,
        password: str,
        login_func: Callable,
        force_relogin: bool = False,
        **login_kwargs
    ) -> Any:
        """
        创建新的Context（支持同账号多Context）
        
        每次调用都会创建一个新的独立Context，适用于：
        - 需要隔离录制Trace（每个Context独立Trace）
        - 需要并发执行不同的业务流程
        - 需要独立的浏览器环境
        
        注意：
        - 登录操作仍然串行化（同账号只登录一次）
        - 后续Context直接加载storage_state（性能优化）
        - **不会自动创建page**，请手动创建：`page = await context.new_page()`
        
        Args:
            system: 系统名称（如"boss"、"zjpt"）
            target_url: 目标URL（提示信息，实际需要自己跳转）
            username: 用户名
            password: 密码
            login_func: 登录函数，签名为 async def login_func(page, username, password, target_url, **kwargs)
            force_relogin: 是否强制重新登录（忽略缓存）
            **login_kwargs: 传递给login_func的其他参数
            
        Returns:
            context: 新创建的Context对象（已登录状态）
            
        Examples:
            # 同一账号创建3个独立Context
            context1 = await login_manager.login_new_context(
                system="boss",
                target_url="https://boss3g.yeepay.com/nc-boss/",
                username="admin",
                password="123456",
                login_func=boss_login
            )
            page1 = await context1.new_page()
            await page1.goto("https://boss3g.yeepay.com/nc-boss/")
            
            context2 = await login_manager.login_new_context(
                system="boss",
                target_url="https://boss3g.yeepay.com/merchant-boss/",
                username="admin",
                password="123456",
                login_func=boss_login
            )
            page2 = await context2.new_page()
            await page2.goto("https://boss3g.yeepay.com/merchant-boss/")
            # 登录只执行1次，2个Context都是admin账号，但访问不同页面
        """
        # 1. 生成账号ID
        account_id = self._get_account_id(system, username)
        storage_state_path = self._get_storage_state_path(account_id)
        
        logger.REMOTE.info("=" * 60)
        logger.REMOTE.info(f"[{account_id}] 请求创建新Context")
        logger.REMOTE.info(f"  目标URL: {target_url}")
        
        # 2. 获取该账号的专属锁（确保同一账号登录串行化）
        account_lock = await self._get_account_lock(account_id)
        
        async with account_lock:
            logger.REMOTE.info(f"[{account_id}] 获得登录锁")
            
            # 3. 检查是否需要登录
            need_login = (
                force_relogin or 
                not self._is_storage_state_valid(storage_state_path)
            )
            
            if need_login:
                # 需要登录
                await self._do_login(
                    account_id, 
                    storage_state_path,
                    target_url,
                    username,
                    password,
                    login_func,
                    **login_kwargs
                )
            else:
                logger.REMOTE.info(f"[{account_id}] 使用已有登录状态: {storage_state_path}")
        
        # 4. 创建新的Context（加载登录状态）
        # 注意：这里在锁外面创建Context，因为不涉及登录冲突
        # 使用账号ID+唯一编号作为custom_name，确保每个context的trace都是独立的
        async with self._counter_lock:
            self._context_counter += 1
            context_number = self._context_counter
        
        new_context = await self.browser.create_context(
            custom_name=f"{system}_{username}_ctx{context_number}",
            storage_state=storage_state_path
        )
        
        # 5. 记录这个Context
        if account_id not in self._account_contexts:
            self._account_contexts[account_id] = []
        self._account_contexts[account_id].append(new_context)
        
        context_count = len(self._account_contexts[account_id])
        logger.REMOTE.info(f"[{account_id}] ✓ 新Context已创建（当前共有 {context_count} 个Context）")
        logger.REMOTE.info(f"  提示: 请使用 await context.new_page() 创建页面并访问 {target_url}")
        logger.REMOTE.info("=" * 60)
        
        return new_context
    
    async def get_or_create_context(
        self,
        system: str,
        target_url: str,
        username: str,
        password: str,
        login_func: Callable,
        force_relogin: bool = False,
        **login_kwargs
    ) -> Any:
        """
        获取或创建Context（复用模式）
        
        同一账号只创建一个Context，后续请求复用：
        - 首次调用：登录并创建Context
        - 再次调用：直接复用已有Context
        
        注意：
        - **不会自动创建page**，请手动创建：`page = await context.new_page()`
        - 多个任务共享同一个Context时，建议每个任务创建自己的page
        
        适用于：
        - 同一账号的多个并发任务（共享Context）
        - 需要共享登录状态和Cookie
        - 追求性能和资源优化
        
        Args:
            system: 系统名称
            target_url: 目标URL（提示信息，实际需要自己跳转）
            username: 用户名
            password: 密码
            login_func: 登录函数，签名为 async def login_func(page, username, password, target_url, **kwargs)
            force_relogin: 是否强制重新登录
            **login_kwargs: 传递给login_func的其他参数
            
        Returns:
            context: Context对象（可能是已有的或新创建的）
            
        Examples:
            # 10个并发任务复用同一个Context
            async def task(task_id):
                context = await login_manager.get_or_create_context(
                    system="boss",
                    target_url="https://boss3g.yeepay.com/nc-boss/",
                    username="admin",
                    password="123456",
                    login_func=boss_login
                )
                # 每个任务创建自己的page
                page = await context.new_page()
                await page.goto(f"https://boss3g.yeepay.com/nc-boss/?id={task_id}")
                # 执行操作...
                await page.close()  # 用完关闭page
            
            tasks = [task(i) for i in range(10)]
            await asyncio.gather(*tasks)
            # 只登录1次，10个任务共享同一个Context，但各有自己的page
        """
        account_id = self._get_account_id(system, username)
        storage_state_path = self._get_storage_state_path(account_id)
        
        logger.REMOTE.info("=" * 60)
        logger.REMOTE.info(f"[{account_id}] 请求获取或创建Context（复用模式）")
        logger.REMOTE.info(f"  目标URL: {target_url}")
        
        # 获取账号锁
        account_lock = await self._get_account_lock(account_id)
        
        async with account_lock:
            logger.REMOTE.info(f"[{account_id}] 获得登录锁")
            
            # 检查是否已有有效的Context
            if not force_relogin and account_id in self._account_contexts:
                contexts = self._account_contexts[account_id]
                if contexts:
                    context = contexts[0]  # 使用第一个Context
                    
                    # 验证context是否还有效
                    try:
                        # 简单验证：尝试访问context属性
                        _ = context.pages
                        logger.REMOTE.info(f"[{account_id}] ✓ 复用已有Context（共 {len(contexts)} 个Context）")
                        logger.REMOTE.info(f"  提示: 请使用 await context.new_page() 创建页面")
                        logger.REMOTE.info("=" * 60)
                        return context
                    except Exception as e:
                        logger.REMOTE.warning(f"[{account_id}] 已有Context无效: {e}，将重新创建")
                        # 清理无效的Context
                        self._account_contexts[account_id] = []
            
            # 检查是否需要登录
            need_login = (
                force_relogin or 
                not self._is_storage_state_valid(storage_state_path)
            )
            
            if need_login:
                await self._do_login(
                    account_id,
                    storage_state_path,
                    target_url,
                    username,
                    password,
                    login_func,
                    **login_kwargs
                )
            else:
                logger.REMOTE.info(f"[{account_id}] 使用已有登录状态: {storage_state_path}")
            
            # 创建新的Context（使用账号ID+唯一编号作为custom_name）
            async with self._counter_lock:
                self._context_counter += 1
                context_number = self._context_counter
            
            context = await self.browser.create_context(
                custom_name=f"{system}_{username}_ctx{context_number}",
                storage_state=storage_state_path
            )
            
            # 缓存Context
            self._account_contexts[account_id] = [context]
            
            logger.REMOTE.info(f"[{account_id}] ✓ 新Context已创建（复用模式）")
            logger.REMOTE.info(f"  提示: 请使用 await context.new_page() 创建页面并访问 {target_url}")
            logger.REMOTE.info("=" * 60)
            
            return context
    
    def get_context_count(self, system: str, username: str) -> int:
        """
        获取指定账号的Context数量
        
        Args:
            system: 系统名称
            username: 用户名
            
        Returns:
            Context数量
        """
        account_id = self._get_account_id(system, username)
        if account_id in self._account_contexts:
            return len(self._account_contexts[account_id])
        return 0
    
    def get_all_contexts(self, system: str, username: str) -> List[Any]:
        """
        获取指定账号的所有Context
        
        Args:
            system: 系统名称
            username: 用户名
            
        Returns:
            Context列表
        """
        account_id = self._get_account_id(system, username)
        return self._account_contexts.get(account_id, [])
    
    async def close_context(
        self, 
        context, 
        trace_name: Optional[str] = None
    ) -> dict:
        """
        关闭指定Context（自动处理trace）
        
        注意：Trace由BrowserManager自动管理，会根据context的custom_name生成文件名
        
        Args:
            context: 要关闭的Context对象
            trace_name: 自定义Trace文件名（可选）
                - None: 使用BrowserManager自动生成的文件名
                - 字符串: 使用指定的文件名
            
        Returns:
            包含保存的文件信息的字典
            
        Examples:
            # 自动生成trace文件名（基于custom_name）
            await login_manager.close_context(context)
            
            # 使用自定义文件名
            await login_manager.close_context(context, trace_name="my_task")
        """
        # 从跟踪列表中移除
        for account_id, contexts in self._account_contexts.items():
            if context in contexts:
                contexts.remove(context)
                logger.REMOTE.info(f"[{account_id}] 从管理列表中移除Context，剩余 {len(contexts)} 个")
                break
        
        # 调用BrowserManager的方法关闭（自动保存trace和视频）
        result = await self.browser.close_context(context, trace_name)
        logger.REMOTE.info("✓ Context已关闭")
        
        return result
    
    async def close_all_contexts(self, system: str, username: str):
        """
        关闭指定账号的所有Context（并发保存trace）
        
        Args:
            system: 系统名称
            username: 用户名
        """
        account_id = self._get_account_id(system, username)
        
        if account_id not in self._account_contexts:
            logger.REMOTE.info(f"[{account_id}] 没有需要关闭的Context")
            return
        
        contexts = self._account_contexts[account_id].copy()
        logger.REMOTE.info(f"[{account_id}] 开始关闭所有Context（共 {len(contexts)} 个）")
        
        # ✅ 并发关闭所有context
        tasks = [self.close_context(context) for context in contexts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 检查结果
        success_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.REMOTE.warning(f"[{account_id}] 关闭Context {i+1}时出错: {result}")
            else:
                success_count += 1
                logger.REMOTE.info(f"[{account_id}] ✓ 已关闭Context {i+1}/{len(contexts)}")
        
        # 清空列表
        self._account_contexts[account_id] = []
        logger.REMOTE.info(f"[{account_id}] ✓ 所有Context已关闭（成功: {success_count}/{len(contexts)}）")
    
    async def logout(self, system: str, username: str):
        """
        登出指定账号
        
        操作：
        1. 关闭所有Context
        2. 删除storage_state文件
        3. 清理缓存
        
        Args:
            system: 系统名称
            username: 用户名
        """
        account_id = self._get_account_id(system, username)
        logger.REMOTE.info(f"[{account_id}] 开始登出...")
        
        # 1. 关闭所有Context
        await self.close_all_contexts(system, username)
        
        # 2. 删除storage_state文件
        if account_id in self._account_storage_states:
            storage_state_path = self._account_storage_states[account_id]
            try:
                if os.path.exists(storage_state_path):
                    os.remove(storage_state_path)
                    logger.REMOTE.info(f"[{account_id}] ✓ 已删除登录状态文件: {storage_state_path}")
            except Exception as e:
                logger.REMOTE.warning(f"[{account_id}] 删除storage_state文件时出错: {e}")
            del self._account_storage_states[account_id]
        
        # 3. 清理锁
        if account_id in self._account_locks:
            del self._account_locks[account_id]
        
        logger.REMOTE.info(f"[{account_id}] ✓ 登出完成")
    
    async def clear_all(self):
        """清理所有登录状态和Context（自动保存所有trace）"""
        logger.REMOTE.info("=" * 60)
        logger.REMOTE.info("开始清理所有登录状态...")
        
        # 关闭所有Context（直接调用BrowserManager，自动保存trace）
        await self.browser.close_all_contexts()
        
        # 清空所有缓存
        self._account_contexts.clear()
        self._account_storage_states.clear()
        self._account_locks.clear()
        
        logger.REMOTE.info("✓ 所有登录状态已清理")
        logger.REMOTE.info("=" * 60)
    
    def get_stats(self) -> dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            "total_accounts": len(self._account_contexts),
            "total_contexts": sum(len(ctxs) for ctxs in self._account_contexts.values()),
            "accounts": {}
        }
        
        for account_id, contexts in self._account_contexts.items():
            stats["accounts"][account_id] = {
                "context_count": len(contexts),
                "has_storage_state": account_id in self._account_storage_states
            }
        
        return stats
    
    def print_stats(self):
        """打印统计信息"""
        stats = self.get_stats()
        
        print("\n" + "=" * 60)
        print("LoginManager 统计信息")
        print("=" * 60)
        print(f"总账号数: {stats['total_accounts']}")
        print(f"总Context数: {stats['total_contexts']}")
        print("-" * 60)
        
        if stats['accounts']:
            for account_id, info in stats['accounts'].items():
                print(f"账号: {account_id}")
                print(f"  Context数量: {info['context_count']}")
                print(f"  登录状态: {'✓ 已保存' if info['has_storage_state'] else '✗ 未保存'}")
                print("-" * 60)
        else:
            print("暂无账号信息")
        
        print("=" * 60 + "\n")

