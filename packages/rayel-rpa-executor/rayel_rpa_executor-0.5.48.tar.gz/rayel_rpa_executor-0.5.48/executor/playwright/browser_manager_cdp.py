import os
import platform
import asyncio
import subprocess
import socket
import time
import inspect
from pathlib import Path
from typing import Literal, Optional, Tuple, Union, TYPE_CHECKING, List
from enum import Enum
from playwright.async_api import async_playwright, Browser, Playwright, BrowserContext

from executor.logger import logger, _job_context_var


# 延迟导入避免循环依赖
if TYPE_CHECKING:
    from executor.playwright.base_page import BasePage

# ============================================
# 登录状态持久化配置
# ============================================
DEFAULT_STORAGE_STATE_FILE = "auth_state.json"  # 默认登录状态文件名


class UserAgent(Enum):
    """预定义的User-Agent常量"""
    CHROME_WINDOWS = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    CHROME_MAC = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    CHROME_LINUX = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    IPHONE_13 = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    IPAD = "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    ANDROID = "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"



class EnvironmentDetector:
    """环境检测器"""
    
    @staticmethod
    def is_docker() -> bool:
        """检测是否在Docker容器内运行"""
        if os.path.exists('/.dockerenv'):
            return True
        try:
            with open('/proc/1/cgroup', 'r') as f:
                return 'docker' in f.read()
        except Exception:
            pass
        if os.getenv('DOCKER_CONTAINER'):
            return True
        return False
    
    @staticmethod
    def get_os() -> str:
        return platform.system().lower()
    
    @staticmethod
    def get_chrome_path() -> Optional[str]:
        """
        获取本地Chrome路径（非Playwright自带）- CDP模式需要
        
        Returns:
            str: Chrome可执行文件路径，如果未找到返回None
        """
        system = platform.system()
        
        if system == "Darwin":  # macOS
            return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        elif system == "Linux":
            # 尝试多个可能的路径
            paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser",
            ]
            for path in paths:
                if os.path.exists(path):
                    return path
        elif system == "Windows":
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
            for path in paths:
                if os.path.exists(path):
                    return path
        
        return None


class BrowserCDPManager:
    """浏览器管理器 - CDP模式 + 非池化设计 + storage_state 持久化登录"""
    
    def __init__(
        self,
        # CDP特有配置
        debug_port: int = 9222,                                             # CDP调试端口
        browser_type: Optional[Literal["chrome", "chromium"]] = None,      # 浏览器类型（None为自动选择）
        user_data_dir: Optional[str] = None,                                # 用户数据目录
        # 浏览器配置
        headless: Optional[bool] = None,                                    # 是否使用无头模式（None时根据环境自动判断）
        user_agent: Union[UserAgent, str, None] = UserAgent.CHROME_WINDOWS, # User-Agent配置
        storage_state: Optional[str] = None,                                # 存储状态文件路径
        # Context配置
        record_video: bool = False,                                         # 是否录制视频
        record_trace: bool = False,                                         # 是否记录trace
        block_resources: Optional[list] = None,                             # 资源阻止列表 [".png", "ads", "*.js", "**/analytics/*"] 支持扩展名/关键字/通配符
        # 存储配置
        videos_dir: Optional[str] = None,                                   # 录屏保存目录
        traces_dir: Optional[str] = None,                                   # Trace保存目录
        # 其他Playwright Context参数
        **context_kwargs
    ):
        # Playwright 实例（每次任务独立）
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        
        # CDP特有配置
        self.debug_port = debug_port
        self.browser_process: Optional[subprocess.Popen] = None  # CDP浏览器进程
        self.chromium_path: Optional[str] = None  # 浏览器可执行文件路径
        self._browser_type = browser_type  # 浏览器类型（chrome/chromium）
        
        # 用户数据目录（CDP模式必需，避免与现有Chrome实例冲突）
        if user_data_dir:
            self.user_data_dir = user_data_dir
        else:
            # 自动生成临时目录
            import tempfile
            self.user_data_dir = os.path.join(
                tempfile.gettempdir(), 
                f"playwright_cdp_{debug_port}"
            )
            # 确保目录存在
            os.makedirs(self.user_data_dir, exist_ok=True)
        
        # 任务状态
        self._task_pages: List = []  # 当前任务创建的页面
        self._trace_started: bool = False  # Trace是否已启动
        
        # Context配置
        self.record_video = record_video
        self.record_trace = record_trace
        self.block_resources = block_resources or []                        # 资源阻止列表
        self.viewport = {"width": 1920, "height": 1080}                     # 默认视口大小
        self.locale = "zh-CN"                                               # 默认语言环境
        self.timezone_id = "Asia/Shanghai"                                  # 默认时区
        
        # User-Agent配置
        if isinstance(user_agent, UserAgent):
            self.user_agent = user_agent.value
        elif isinstance(user_agent, str):
            self.user_agent = user_agent
        else:
            self.user_agent = None
        
        # 环境检测
        self.is_docker = EnvironmentDetector.is_docker()
        self.os_type = EnvironmentDetector.get_os()

        self.project_root = self._find_project_root()
        
        # storage_state 配置（持久化登录）
        if storage_state:
            # 用户指定了完整路径
            self.storage_state_path = storage_state
        else:   
            # 使用默认路径
            if self.is_docker:
                storage_dir = "/app/data/storage_states"
            else:
                storage_dir = os.path.join(self.project_root, "data", "storage_states")
            os.makedirs(storage_dir, exist_ok=True)
            self.storage_state_path = os.path.join(storage_dir, DEFAULT_STORAGE_STATE_FILE)
        
        # 其他Context参数
        self.context_kwargs = context_kwargs
        
        # 确定headless模式
        if headless is None:
            self.headless = self.is_docker
        else:
            self.headless = headless
        
        # 录屏保存目录
        if videos_dir is None:
            if self.is_docker:
                self.videos_dir = "/app/data/videos"
            else:
                self.videos_dir = os.path.join(self.project_root, "data", "videos")
        else:
            self.videos_dir = videos_dir
        
        # Trace保存目录
        if traces_dir is None:
            if self.is_docker:
                self.traces_dir = "/app/data/traces"
            else:
                self.traces_dir = os.path.join(self.project_root, "data", "traces")
        else:
            self.traces_dir = traces_dir
        
        os.makedirs(self.videos_dir, exist_ok=True)
        os.makedirs(self.traces_dir, exist_ok=True)
        
        # 预生成统一任务标识（确保 trace 和 video 使用相同的 标识）
        self._task_flag = self._generate_task_flag()
        self._video_file_name = f"video_{self._task_flag}.zip"
        self._trace_file_name = f"trace_{self._task_flag}.zip"
        
        # 记录最近的Context产生的文件（trace和video zip）
        self._last_context_files = {
            "trace_path": None,
            "video_path": None
        }
        
        logger.REMOTE.info(f"浏览器初始化: ...\n" + 
            "  └─ 任务标识: {self._task_flag}\n" + 
            "  └─ 运行环境: {'Docker' if self.is_docker else '本地'}\n" + 
            "  └─ 操作系统: {self.os_type}\n" + 
            "  └─ 浏览器模式: CDP (debug_port={self.debug_port})\n" + 
            "  └─ 用户数据目录: {self.user_data_dir}\n  " + 
            "  └─ 无头模式: {self.headless}\n" + 
            "  └─ 开启录屏: {self.record_video}\n" + 
            "    └─ 录屏文件名: {self._video_file_name}\n" if self.record_video else "" + 
            "    └─ 保存目录: {self.videos_dir}\n" if self.record_video else "" + 
            "  └─ 开启Trace: {self.record_trace}\n" + 
            "    └─ Trace文件名: {self._trace_file_name}\n" if self.record_trace else "" + 
            "    └─ 保存目录: {self.traces_dir}\n" if self.record_trace else "" + 
            "  └─ 资源阻止: {bool(self.block_resources)}\n" + 
            ("    └─ 规则: " + str(self.block_resources) + "\n" if self.block_resources else "") + 
            "  └─ 登录状态: {self.storage_state_path}\n" +
            "    └─ 检测到已保存的登录状态\n" if os.path.exists(self.storage_state_path) else ""
        )
    
    def _get_launch_args(self) -> list:
        """根据环境生成浏览器启动参数 - CDP模式"""
        args = [
            # CDP特有参数
            f"--remote-debugging-port={self.debug_port}",
            
            # 基础参数
            "--no-first-run",
            "--no-default-browser-check",
            "--window-position=0,0",
            f"--window-size={self.viewport['width']},{self.viewport['height']}",
            
            # 反自动化检测参数
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--exclude-switches=enable-automation",
            "--disable-extensions",
            
            # 隐私和安全参数
            "--disable-component-extensions-with-background-pages",
            "--disable-default-apps",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection",
            "--disable-popup-blocking",
            
            # 性能优化参数
            "--disable-hang-monitor",
            "--disable-prompt-on-repost",
            "--disable-sync",
            "--metrics-recording-only",
            "--no-service-autorun",
            "--password-store=basic",
            "--disable-background-networking",
            
            # 下载和安全浏览
            "--disable-save-password-bubble",
            "--safebrowsing-disable-download-protection",
            "--disable-client-side-phishing-detection",
            "--safebrowsing-disable-auto-update",
            "--disable-features=SafeBrowsingEnhanced",
        ]
        
        # 用户数据目录
        if self.user_data_dir:
            args.append(f"--user-data-dir={self.user_data_dir}")
        
        # Docker环境特殊参数
        if self.is_docker:
            args.extend([
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-software-rasterizer",
            ])
        
        # 无头模式
        if self.headless:
            args.append("--headless=new")
        
        return args
    
    async def _initialize(self):
        """初始化浏览器路径 - CDP模式"""
        # 1. 确定浏览器类型（如果用户未指定）
        if not self._browser_type:
            # 自动选择：Docker/Linux优先Chromium，本地优先Chrome
            if self.is_docker or self.os_type == "linux":
                self._browser_type = "chromium"
            else:
                self._browser_type = "chrome"
        
        # 2. 获取浏览器可执行文件路径
        if self._browser_type == "chrome":
            # 使用系统安装的Chrome
            self.chromium_path = EnvironmentDetector.get_chrome_path()
            if not self.chromium_path or not os.path.exists(self.chromium_path):
                logger.LOCAL.warning("未找到系统Chrome，回退到Playwright Chromium")
                self._browser_type = "chromium"
        
        if self._browser_type == "chromium":
            # 使用Playwright自带的Chromium（异步API）
            if not self.playwright:
                self.playwright = await async_playwright().start()
            self.chromium_path = self.playwright.chromium.executable_path
            logger.LOCAL.info(f"使用Playwright Chromium: {self.chromium_path}")
        else:
            logger.LOCAL.info(f"使用系统Chrome: {self.chromium_path}")
    
    def _wait_for_browser_ready(self, timeout: int = 30):
        """等待浏览器CDP端口就绪 - CDP模式"""
        start_time = time.time()
        check_count = 0
        
        while time.time() - start_time < timeout:
            check_count += 1
            
            # 检查进程是否还活着
            if self.browser_process and self.browser_process.poll() is not None:
                # 进程已退出
                logger.LOCAL.error(f"  └─ 浏览器进程已退出 (exit code: {self.browser_process.returncode})")
                raise RuntimeError(f"浏览器进程启动后异常退出 (code: {self.browser_process.returncode})")
            
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex(('127.0.0.1', self.debug_port))
                    if result == 0:
                        logger.LOCAL.info(f"  └─ 浏览器 CDP 端口 {self.debug_port} 已就绪 (第{check_count}次检查)")
                        return True
                    else:
                        if check_count % 10 == 0:  # 每10次检查打印一次日志
                            logger.LOCAL.debug(f"  └─ 等待CDP端口... (第{check_count}次检查, 已经过{int(time.time()-start_time)}秒)")
            except Exception as e:
                if check_count % 10 == 0:
                    logger.LOCAL.debug(f"  └─ 端口检查异常: {e}")
            
            time.sleep(0.5)
        
        raise TimeoutError(f"CDP端口 {self.debug_port} 超时{timeout}秒未就绪（共检查{check_count}次）")
    
    def _start_browser(self):
        """启动浏览器进程 - CDP模式"""
        if self.browser_process:
            logger.LOCAL.warning("浏览器进程已存在")
            return
        
        try:
            # 构建启动命令
            launch_args = self._get_launch_args()
            cmd = [self.chromium_path] + launch_args
            
            # 调试日志：打印启动命令
            logger.LOCAL.debug(f"  └─ 启动命令: {' '.join(cmd[:3])}...")
            
            # 启动浏览器进程（捕获输出以便调试）
            self.browser_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL
            )
            logger.LOCAL.info(f"  └─ 浏览器进程已启动 (PID: {self.browser_process.pid})")
            
            # 等待浏览器 CDP 端口就绪（主动检查，更可靠）
            self._wait_for_browser_ready(timeout=30)
            
        except Exception as e:
            logger.LOCAL.error(f"  └─ 启动浏览器失败: {e}")
            # 如果进程已启动，读取错误输出
            if self.browser_process:
                try:
                    # 非阻塞读取错误输出
                    import select
                    if self.browser_process.stderr:
                        # 设置非阻塞
                        import fcntl
                        flags = fcntl.fcntl(self.browser_process.stderr, fcntl.F_GETFL)
                        fcntl.fcntl(self.browser_process.stderr, fcntl.F_SETFL, flags | os.O_NONBLOCK)
                        
                        stderr_output = self.browser_process.stderr.read()
                        if stderr_output:
                            logger.LOCAL.error(f"  └─ Chrome stderr: {stderr_output.decode('utf-8', errors='ignore')[:500]}")
                except Exception:
                    pass
            raise
    
    
    async def _start_trace_if_needed(self):
        """如果需要且未启动，则启动Trace记录"""
        if self.record_trace and not self._trace_started and self.context:
            trace_path = os.path.join(self.traces_dir, self._trace_file_name)
            
            try:
                # 添加超时保护，防止trace启动卡死
                await asyncio.wait_for(
                    self.context.tracing.start(screenshots=True, snapshots=True, sources=True),
                    timeout=5.0  # 5秒超时
                )
                self._last_context_files["trace_path"] = trace_path
                self._trace_started = True
                logger.LOCAL.debug(f"  └─ Trace记录已开启: {self._trace_file_name}")
            except asyncio.TimeoutError:
                logger.LOCAL.warning(f"⚠️ Trace启动超时(5秒)，跳过trace记录: {self._trace_file_name}")
                self.record_trace = False  # 禁用trace避免后续问题
            except Exception as e:
                logger.LOCAL.warning(f"⚠️ Trace启动失败(5秒)，跳过trace记录: {e}")
                self.record_trace = False  # 禁用trace避免后续问题
    
    
    def _check_port_available(self, port: int) -> bool:
        """检查端口是否可用 - CDP模式"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                return result != 0  # 返回 True 表示端口可用（没有被占用）
        except Exception:
            return True  # 异常时认为可用
    
    def _find_available_port(self, start_port: int = 9222, max_attempts: int = 10) -> int:
        """查找可用的CDP端口 - CDP模式
        
        Args:
            start_port: 起始端口号
            max_attempts: 最大尝试次数
            
        Returns:
            可用的端口号
            
        Raises:
            RuntimeError: 未找到可用端口
        """
        for i in range(max_attempts):
            port = start_port + i
            if self._check_port_available(port):
                return port
        
        raise RuntimeError(f"未找到可用的CDP端口（尝试范围: {start_port}-{start_port + max_attempts - 1}）")
    
    async def start(self):
        """启动浏览器（非池化模式）"""
        if self.context:
            logger.LOCAL.warning("Context已存在，无需重复启动")
            return self
        
        try:
            # 1. 检查CDP端口是否被占用，自动切换到可用端口
            original_port = self.debug_port
            if not self._check_port_available(self.debug_port):
                logger.LOCAL.warning(f"⚠️ CDP端口 {self.debug_port} 已被占用，自动切换到可用端口...")
                self.debug_port = self._find_available_port(start_port=original_port + 1)
                logger.LOCAL.info(f"  └─ 已切换到端口: {self.debug_port}")
                # 更新用户数据目录
                import tempfile
                self.user_data_dir = os.path.join(
                    tempfile.gettempdir(), 
                    f"playwright_cdp_{self.debug_port}"
                )
                os.makedirs(self.user_data_dir, exist_ok=True)
            
            # 2. 获取浏览器路径 - CDP模式
            logger.LOCAL.info("🚀 启动 Playwright...")
            await self._initialize()
            
            # 3. 启动浏览器进程 - CDP模式
            logger.LOCAL.info("🌐 启动浏览器...")
            self._start_browser()
            
            # 4. 连接浏览器 - CDP模式
            if not self.playwright:
                self.playwright = await async_playwright().start()
            
            self.browser = await self.playwright.chromium.connect_over_cdp(
                f"http://localhost:{self.debug_port}"
            )
            
            logger.LOCAL.info(f"  └─ 成功连接到浏览器")
            
            # 5. 构建 Context 配置
            logger.LOCAL.info("📋 创建浏览器 Context...")
            context_options = {
                "viewport": self.viewport,
                "locale": self.locale,
                "timezone_id": self.timezone_id,
                "ignore_https_errors": True,
                "permissions": ["geolocation", "notifications", "clipboard-read", "clipboard-write", "microphone", "camera"],
            }
            
            # User-Agent
            if self.user_agent:
                context_options["user_agent"] = self.user_agent
            
            # 加载 storage_state（如果存在）
            if os.path.exists(self.storage_state_path):
                context_options["storage_state"] = self.storage_state_path
                logger.LOCAL.info(f"📥 加载登录状态: {self.storage_state_path}")
            
            # 录屏配置
            if self.record_video:
                context_options["record_video_dir"] = self.videos_dir
                context_options["record_video_size"] = self.viewport
            
            # 合并用户自定义配置
            context_options.update(self.context_kwargs)
            
            # 6. 创建 Context
            self.context = await self.browser.new_context(**context_options)
            
            # 7. 启动 Trace 记录（如果需要）
            await self._start_trace_if_needed()
            
            logger.REMOTE.info("✅ 浏览器启动成功")
            return self
        
        except Exception as e:
            logger.REMOTE.error(f"❌ 浏览器启动失败: {e}")
            await self._cleanup()
            # 连接失败，停止浏览器进程 - CDP模式
            if self.browser_process:
                try:
                    self.browser_process.terminate()
                    self.browser_process.wait(timeout=5)  # ⚠️ 必须 wait，否则僵尸进程
                except Exception:
                    pass
                finally:
                    self.browser_process = None
            raise
    
    async def connect(self):
        """连接到现有浏览器（CDP模式）"""
        if self.context:
            logger.LOCAL.warning("Context已存在，无需重复连接")
            return self
        
        try:
            # 1. 检查CDP端口是否可连接
            if self._check_port_available(self.debug_port):
                raise ConnectionError(f"CDP端口 {self.debug_port} 不可达，请确保浏览器已启动")
            
            logger.LOCAL.info(f"🔗 连接到现有浏览器 (CDP端口: {self.debug_port})...")
            
            # 2. 启动 Playwright
            if not self.playwright:
                self.playwright = await async_playwright().start()
            
            # 3. 连接浏览器 - CDP模式
            self.browser = await self.playwright.chromium.connect_over_cdp(
                f"http://localhost:{self.debug_port}"
            )
            logger.LOCAL.info(f"  └─ 成功连接到浏览器")
            
            # 4. 构建 Context 配置
            logger.LOCAL.info("📋 创建浏览器 Context...")
            context_options = {
                "viewport": self.viewport,
                "locale": self.locale,
                "timezone_id": self.timezone_id,
                "ignore_https_errors": True,
                "permissions": ["geolocation", "notifications", "clipboard-read", "clipboard-write", "microphone", "camera"],
            }
            
            # User-Agent
            if self.user_agent:
                context_options["user_agent"] = self.user_agent
            
            # 加载 storage_state（如果存在）
            if os.path.exists(self.storage_state_path):
                context_options["storage_state"] = self.storage_state_path
                logger.LOCAL.info(f"📥 加载登录状态: {self.storage_state_path}")
            
            # 录屏配置
            if self.record_video:
                context_options["record_video_dir"] = self.videos_dir
                context_options["record_video_size"] = self.viewport
            
            # 合并用户自定义配置
            context_options.update(self.context_kwargs)
            
            # 5. 创建 Context
            self.context = await self.browser.new_context(**context_options)
            
            # 6. 启动 Trace 记录（如果需要）
            await self._start_trace_if_needed()
            
            logger.LOCAL.info("✅ 成功连接到现有浏览器")
            return self
        
        except Exception as e:
            logger.LOCAL.error(f"❌ 连接浏览器失败: {e}")
            await self._cleanup()
            raise
    
    async def save_login_state(self):
        """保存当前登录状态到 storage_state 文件（登录后调用）"""
        if not self.context:
            raise RuntimeError("必须先调用 start() 初始化浏览器")
        
        try:
            await self.context.storage_state(path=self.storage_state_path)
            logger.LOCAL.info(f"💾 登录状态已保存: {self.storage_state_path}")
        except Exception as e:
            logger.LOCAL.error(f"❌ 保存登录状态失败: {e}")
            raise
    
    def _generate_task_flag(self) -> str:
        """生成统一的任务标识（trace和video都使用此标识）"""
        from datetime import datetime
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S") + f"{now.microsecond // 1000:03d}"
        
        job_context = _job_context_var.get()
        if job_context is not None:
            job_id, task_batch_id = job_context
            if job_id is not None and task_batch_id is not None:
                return f"job-{job_id}_task-{task_batch_id}_{timestamp}"
            elif job_id is not None:
                return f"job-{job_id}_{timestamp}"
        
        return f"task_{timestamp}"
    
    async def _route_abort_configure(self, page):
        """配置页面资源阻止规则"""
        if not self.block_resources:
            return
        
        # 使用单一route处理所有规则
        await page.route(
            "**/*",
            lambda route: self._route_handler(route, self.block_resources)
        )
    
    @staticmethod
    async def _route_handler(route, block_list: list):
        """统一的资源阻止处理器
        
        Args:
            route: Playwright Route对象
            block_list: 阻止列表，支持多种格式：
                - 扩展名：".png", ".jpg" (以.开头)
                - 关键字："ads", "track" (普通字符串)
                - 通配符："*.js", "**/analytics/*" (包含*或?)
        """
        import fnmatch
        
        try:
            url = route.request.url.lower()
            
            # 1. 验证码相关关键字硬编码放行（优先级最高）
            if any(keyword in url for keyword in ["captcha", "verifycode", "verify_code"]):
                await asyncio.wait_for(route.continue_(), timeout=3.0)
                return
            
            # 2. 遍历阻止列表
            url_path = url.split('?')[0]  # 去除查询参数
            
            for item in block_list:
                item_lower = item.lower()
                
                # 扩展名匹配（以.开头）
                if item_lower.startswith('.'):
                    if url_path.endswith(item_lower):
                        await asyncio.wait_for(route.abort(), timeout=3.0)
                        return
                
                # 通配符匹配（包含*或?）
                elif '*' in item or '?' in item:
                    if fnmatch.fnmatch(url_path, item_lower):
                        await asyncio.wait_for(route.abort(), timeout=3.0)
                        return
                
                # 关键字匹配（默认）
                else:
                    if item_lower in url:
                        await asyncio.wait_for(route.abort(), timeout=3.0)
                        return
            
            # 所有规则都不匹配，放行
            await asyncio.wait_for(route.continue_(), timeout=3.0)
        except asyncio.TimeoutError:
            # 超时时静默忽略，避免阻塞页面加载
            logger.LOCAL.debug(f"  └─ 资源路由处理超时(3秒)，跳过: {route.request.url[:100]}")
        except Exception as e:
            # 发生任何异常时尝试放行，避免卡住页面
            logger.LOCAL.debug(f"  └─ 资源路由处理异常，尝试放行: {e}")
            try:
                await asyncio.wait_for(route.continue_(), timeout=1.0)
            except:
                pass  # 最终兜底，避免抛出异常
    
    def _track_page(self, page):
        """
        追踪页面：如果页面不在追踪列表中，则添加并标记
        用于确保所有通过BrowserManager访问的页面都被追踪
        """
        if page not in self._task_pages:
            # 标记页面所属任务
            page._task_owner = self._task_flag
            self._task_pages.append(page)
            logger.LOCAL.debug(f"      └─ 追踪页面（当前任务有 {len(self._task_pages)} 个页面）")
    
    async def new_page(self) -> "BasePage":
        """从当前Context创建新页面（自动包装为BasePage）"""
        from executor.playwright.base_page import BasePage
        
        if not self.context:
            raise RuntimeError("必须先调用 start() 初始化Browser")
        
        page = await self.context.new_page()
        
        # 应用资源阻止配置
        if self.block_resources:
            await self._route_abort_configure(page)
        
        # 追踪页面
        self._track_page(page)
        
        return BasePage(page, browser_manager=self)
    
    async def get_page(
        self,
        url: Optional[str] = None,
        title: Optional[str] = None,
        index: Optional[int] = None,
        url_match: Literal["exact", "contains", "startswith", "endswith", "regex"] = "exact",
        title_match: Literal["exact", "contains", "startswith", "endswith", "regex"] = "exact"
    ) -> "BasePage":
        """
        获取页面实例 - 支持多种选择方式（自动包装为BasePage）
        
        Args:
            url: 根据URL查找页面
            title: 根据标题查找页面
            index: 根据索引获取页面（0-based）
            url_match: URL匹配模式
            title_match: 标题匹配模式
        
        Returns:
            BasePage: BasePage实例
        """
        from executor.playwright.base_page import BasePage
        
        if not self.context:
            raise RuntimeError("必须先调用 start() 初始化Browser")
        
        # 如果没有页面，创建新页面
        if len(self.context.pages) == 0:
            page = await self.context.new_page()
            # 追踪页面
            self._track_page(page)
            return BasePage(page, browser_manager=self)
        
        # 如果没有任何过滤条件，返回最后一个页面
        if url is None and title is None and index is None:
            page = self.context.pages[-1]
            # 追踪页面（可能是其他方式创建的）
            self._track_page(page)
            return BasePage(page, browser_manager=self)
        
        # 如果只指定了索引
        if url is None and title is None and index is not None:
            if 0 <= index < len(self.context.pages):
                page = self.context.pages[index]
                # 追踪页面
                self._track_page(page)
                return BasePage(page, browser_manager=self)
            else:
                raise ValueError(f"索引 {index} 超出范围，当前有 {len(self.context.pages)} 个页面")
        
        # 根据URL和/或标题过滤页面
        matched_pages = []
        
        for i, page in enumerate(self.context.pages):
            # 检查URL匹配
            url_matched = True
            if url is not None:
                page_url = page.url
                url_matched = self._match_string(page_url, url, url_match)
            
            # 检查标题匹配
            title_matched = True
            if title is not None:
                page_title = await page.title()
                title_matched = self._match_string(page_title, title, title_match)
            
            # 如果都匹配，添加到结果
            if url_matched and title_matched:
                matched_pages.append((i, page))
        
        if not matched_pages:
            raise ValueError(
                f"未找到匹配的页面 - "
                f"URL: {url} ({url_match}), "
                f"Title: {title} ({title_match})"
            )
        
        # 如果指定了索引，从匹配结果中获取
        if index is not None:
            if 0 <= index < len(matched_pages):
                page_index, page = matched_pages[index]
                # 追踪页面
                self._track_page(page)
                return BasePage(page, browser_manager=self)
            else:
                raise ValueError(
                    f"匹配索引 {index} 超出范围，找到 {len(matched_pages)} 个匹配页面"
                )
        
        # 否则返回第一个匹配的页面
        page_index, page = matched_pages[0]
        # 追踪页面
        self._track_page(page)
        return BasePage(page, browser_manager=self)
    
    def _match_string(
        self, 
        text: str, 
        pattern: str, 
        match_type: Literal["exact", "contains", "startswith", "endswith", "regex"]
    ) -> bool:
        """字符串匹配辅助方法"""
        import re
        
        if match_type == "exact":
            return text == pattern
        elif match_type == "contains":
            return pattern in text
        elif match_type == "startswith":
            return text.startswith(pattern)
        elif match_type == "endswith":
            return text.endswith(pattern)
        elif match_type == "regex":
            try:
                return bool(re.search(pattern, text))
            except re.error as e:
                logger.LOCAL.warning(f"正则表达式错误: {e}")
                return False
    
    def get_trace_path(self) -> Optional[str]:
        """获取trace文件路径"""
        return "[#download#]" + self._last_context_files.get("trace_path")
    
    def get_video_path(self) -> Optional[str]:
        """获取录屏压缩包路径"""
        return "[#download#]" + self._last_context_files.get("video_path")
        
    async def _cleanup(self):
        """清理任务资源（只处理当前任务的页面，不关闭浏览器）"""
        # 1. 收集当前任务创建的页面的录屏对象引用
        pages_with_videos = []
        if self.context and self.record_video and self._task_pages:
            for page in self._task_pages:
                try:
                    # 检查页面是否已关闭
                    if not page.is_closed() and page.video:
                        pages_with_videos.append((page, page.video))
                except Exception:
                    # 页面可能已经被关闭或失效
                    pass
        
        # 2. 停止Trace并保存（只保存当前任务的trace）
        if self.context and self.record_trace and self._trace_started:
            trace_path = self._last_context_files.get("trace_path")
            if trace_path:
                try:
                    await self.context.tracing.stop(path=trace_path)
                    logger.LOCAL.debug(f"  └─ Trace已保存: {trace_path}")
                    self._trace_started = False
                except Exception as e:
                    logger.LOCAL.warning(f"  └─ 保存Trace时出错: {e}")
        
        # 3. 处理当前任务的录屏文件
        if pages_with_videos:
            try:
                import shutil
                import tempfile
                
                # 创建临时目录存放录屏文件
                temp_dir = tempfile.mkdtemp(prefix="browser_videos_")
                temp_video_files = []
                
                # 创建异步任务列表
                video_tasks = []
                
                # 收集并创建异步视频处理任务
                for idx, (page, video) in enumerate(pages_with_videos):
                    try:
                        # 使用页面真实序号命名（从1开始）
                        new_filename = f"{self._video_file_name}_{idx + 1}.webm"
                        new_path = os.path.join(temp_dir, new_filename)
                        
                        # 1. 先关闭页面（触发视频录制结束）
                        await page.close()
                        
                        # 2. 创建异步视频处理任务（不等待）
                        task = asyncio.create_task(
                            self._process_video_async(video, new_path, new_filename)
                        )
                        video_tasks.append((task, new_path, new_filename))
                        
                    except Exception as e:
                        logger.LOCAL.warning(f"  └─ 处理页面 {idx + 1} 的录屏时出错: {e}")
                
                # 等待所有视频处理任务完成
                for task, new_path, new_filename in video_tasks:
                    try:
                        success = await task
                        if success and os.path.exists(new_path):
                            temp_video_files.append(new_path)
                            logger.LOCAL.debug(f"  └─ 录屏已收集: {new_filename}")
                    except Exception as e:
                        logger.LOCAL.warning(f"  └─ 异步处理录屏 {new_filename} 时出错: {e}")
                
                # 压缩所有录屏到一个zip文件
                if temp_video_files:
                    video_path = os.path.join(self.videos_dir, self._video_file_name)
                    
                    # 使用极致压缩（compresslevel=9）
                    with __import__('zipfile').ZipFile(video_path, 'w', __import__('zipfile').ZIP_DEFLATED, compresslevel=9) as zf:
                        for video_file in temp_video_files:
                            zf.write(video_file, os.path.basename(video_file))
                    
                    self._last_context_files["video_path"] = video_path
                    logger.LOCAL.debug(f"  └─ 录屏已压缩: {len(temp_video_files)} 个文件 -> {self._video_file_name}")
                    
                    # 清理临时目录
                    shutil.rmtree(temp_dir)
            except Exception as e:
                logger.LOCAL.warning(f"    └─ 处理录屏文件时出错: {e}")
        
        # 4. 清空任务页面列表
        self._task_pages.clear()
    
    async def _process_video_async(self, video, new_path: str, new_filename: str) -> bool:
        """
        异步处理视频文件（保存并删除原始文件）
        
        Args:
            video: Playwright Video 对象
            new_path: 新的文件路径
            new_filename: 新的文件名
            
        Returns:
            bool: 成功返回true，失败返回false
        """
        try:
            # 等待视频完全写入后再返回
            await video.save_as(new_path)
            
            # 删除原始随机命名的录屏文件
            await video.delete()
            
            return True
        except Exception as e:
            logger.LOCAL.warning(f"    └─ 异步处理录屏 {new_filename} 失败: {e}")
            return False
        
    
    async def stop(self):
        """停止浏览器并完全清理资源（非池化模式）"""
        logger.LOCAL.info("🧹 清理浏览器资源...")
        
        try:
            # 1. 处理 Trace 和录屏
            await self._cleanup()
        except Exception as e:
            logger.LOCAL.error(f"  └─ 清理 Trace/录屏时出错: {e}")
        
        # 2. 关闭 Context
        if self.context:
            try:
                await self.context.close()
                logger.LOCAL.info("  └─ ✅ Context 已关闭")
            except Exception as e:
                logger.LOCAL.error(f"  └─ 关闭 Context 时出错: {e}")
            finally:
                self.context = None
        
        # 3. 关闭 Browser
        if self.browser:
            try:
                await self.browser.close()
                logger.LOCAL.info("  └─ ✅ Browser 已关闭")
            except Exception as e:
                logger.LOCAL.error(f"  └─ 关闭 Browser 时出错: {e}")
            finally:
                self.browser = None
        
        # 4. 停止 Playwright
        if self.playwright:
            try:
                await self.playwright.stop()
                logger.LOCAL.info("  └─ ✅ Playwright 已停止")
            except Exception as e:
                logger.LOCAL.error(f"  └─ 停止 Playwright 时出错: {e}")
            finally:
                self.playwright = None
        
        # 5. 停止浏览器进程 - CDP模式
        if self.browser_process:
            try:
                self.browser_process.terminate()
                self.browser_process.wait(timeout=5)
                logger.LOCAL.info("  └─ ✅ 浏览器进程已停止")
            except subprocess.TimeoutExpired:
                logger.LOCAL.warning("  └─ 浏览器进程未响应，强制终止")
                try:
                    self.browser_process.kill()
                    self.browser_process.wait(timeout=5)  # ⚠️ 关键：kill 后必须 wait
                except Exception as kill_error:
                    logger.LOCAL.error(f"  └─ 强制终止浏览器进程失败: {kill_error}")
            except Exception as e:
                logger.LOCAL.error(f"  └─ 停止浏览器进程时出错: {e}")
            finally:
                self.browser_process = None
        
        logger.REMOTE.info("✅ 浏览器资源清理完成")
    
    async def __aenter__(self):
        """支持async with语法 - 自动启动浏览器"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """自动清理资源"""
        await self.stop()

    def _find_project_root(
        self,
        marker_files: Tuple[str, ...] = ('setup.py', '.git'),
        start_path: Optional[Path] = None
    ) -> str:
        """
        通过查找标记文件来定位项目根目录
        
        Args:
            marker_files: 用于标识项目根目录的文件或文件夹元组
                        默认查找 setup.py 或 .git 目录
            start_path: 开始搜索的路径，默认为调用此函数的文件所在目录
                    
        Returns:
            str: 项目根目录的绝对路径字符串
            
        Examples:
            >>> # 使用默认标记文件
            >>> root = find_project_root()
            >>> print(root)
            '/Users/username/projects/my-project'
            
            >>> # 使用自定义标记文件
            >>> root = find_project_root(marker_files=('pyproject.toml', '.git'))
            
            >>> # 指定开始搜索的路径
            >>> root = find_project_root(start_path=Path('/some/custom/path'))
        """
        # 确定开始搜索的路径
        if start_path is None:
            # 使用调用者的文件路径
            caller_frame = inspect.currentframe().f_back
            caller_file = caller_frame.f_globals.get('__file__')
            if caller_file:
                current = Path(caller_file).resolve()
            else:
                # 如果无法获取调用者文件，使用当前工作目录
                current = Path.cwd()
        else:
            current = start_path.resolve()
        
        # 向上遍历目录树查找标记文件
        for parent in [current] + list(current.parents):
            if any((parent / marker).exists() for marker in marker_files):
                return str(parent)
        
        # 降级方案：如果没有找到标记文件，返回当前路径的某个父目录
        # 这里假设大多数项目结构不会超过5层深度
        fallback = current
        for _ in range(5):
            if fallback.parent == fallback:  # 已经到达根目录
                break
            fallback = fallback.parent
        
        return str(fallback)

    def _get_project_data_dir(self, subdir: str = '') -> str:
        """
        获取项目的 data 目录路径
        
        Args:
            subdir: data 目录下的子目录名称，如 'videos', 'traces' 等
            
        Returns:
            str: data 目录或其子目录的绝对路径
            
        Examples:
            >>> # 获取 data 目录
            >>> data_dir = get_project_data_dir()
            
            >>> # 获取 data/videos 目录
            >>> videos_dir = get_project_data_dir('videos')
        """
        root = Path(self._find_project_root())
        if subdir:
            return str(root / 'data' / subdir)
        return str(root / 'data')
