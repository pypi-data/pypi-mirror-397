"""脚本执行模块"""

import asyncio
import contextvars
import importlib.util
import inspect
import sys
import threading
from pathlib import Path
from typing import List, Optional

import snailjob as sj

from .config import PlaywrightExecutorConfig
from .exceptions import ScriptExecutionError
from .logger import logger


class ScriptRunner:
    """脚本执行器（通过方法调用）"""

    def __init__(self, config: PlaywrightExecutorConfig):
        self.config = config
        self.service_path = config.get_service_path()
        self._result: any = None  # 可以是任意类型的返回值
        self._exception: Optional[Exception] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None  # 保存事件循环引用
        self._task: Optional[asyncio.Task] = None  # 保存异步任务引用

    def run_main_script(
        self, site_packages_paths: List[str], job_id: int, task_batch_id: int, extra_params: dict = None
    ) -> tuple[bool, any]:
        """
        动态导入 main.py 并调用 run() 方法

        Args:
            site_packages_paths: 虚拟环境的 site-packages 路径列表
            job_id: 任务ID（用于日志追溯）
            task_batch_id: 任务批次ID（用于中断检测）
            extra_params: 传递给 run() 方法的额外参数

        Returns:
            tuple[bool, any]: (是否成功, 返回值)
                - 成功: (True, run() 的返回值)
                - 失败: (False, 错误信息或 None)
        """
        main_py = self.service_path / "main.py"

        if not main_py.exists():
            raise ScriptExecutionError(f"main.py 不存在: {main_py}")

        logger.LOCAL.debug(f"准备执行脚本: {main_py}")

        # 保存原始 sys.path
        original_sys_path = sys.path.copy()

        try:
            # 修改 sys.path，添加虚拟环境和需求文件夹路径
            self._setup_python_path(site_packages_paths)

            # 动态导入 main.py 模块
            module = self._import_main_module(main_py)

            # 验证 Service 类存在
            if not hasattr(module, "Service"):
                raise ScriptExecutionError(f"main.py 中未找到 Service 类: {main_py}")

            service_class = getattr(module, "Service")

            # 实例化服务
            service_instance = service_class()

            # 在独立线程中执行 Service 的 _run_with_context 方法，支持中断检测
            success, result = self._execute_with_timeout(
                run_func=service_instance._run_with_context, job_id=job_id, task_batch_id=task_batch_id, extra_params=extra_params or {}
            )
            
            return success, result
        except asyncio.CancelledError:
            raise  
        except Exception:
            raise

        finally:
            # 恢复原始 sys.path
            sys.path = original_sys_path
            logger.LOCAL.debug(f"已恢复 sys.path")

    def _setup_python_path(self, site_packages_paths: List[str]) -> None:
        """
        设置 Python 路径

        优先级（从高到低）:
            1. 虚拟环境的 site-packages
            2. 业务逻辑文件夹路径
            3. Git 仓库根目录
        """
        # 1. 添加虚拟环境的 site-packages（放在前面，优先级高）
        for path in reversed(site_packages_paths):
            if path not in sys.path:
                sys.path.insert(0, path)
                logger.LOCAL.debug(f"添加到 sys.path: {path}")

        # 2. 添加业务逻辑文件夹路径（让 main.py 可以导入同目录的其他模块）
        service_path_str = str(self.service_path)
        if service_path_str not in sys.path:
            sys.path.insert(0, service_path_str)
            logger.LOCAL.debug(f"添加到 sys.path: {service_path_str}")

        # 3. 添加 Git 仓库根目录（让 main.py 可以导入通用工具类）
        repo_path_str = str(self.config.git_repo_dir)
        if repo_path_str not in sys.path:
            sys.path.insert(0, repo_path_str)
            logger.LOCAL.debug(f"添加到 sys.path: {repo_path_str}")

    def _import_main_module(self, main_py_path: Path):
        """动态导入 main.py 模块"""
        try:
            # 使用 importlib.util 动态导入模块
            # 模块名需要唯一，避免缓存冲突
            module_name = (
                f"playwright_service_{self.config.service_folder.replace('/', '_').replace('.', '_')}"
            )

            logger.LOCAL.debug(f"导入模块: {module_name} from {main_py_path}")

            spec = importlib.util.spec_from_file_location(module_name, main_py_path)
            if spec is None or spec.loader is None:
                raise ScriptExecutionError(f"无法加载模块: {main_py_path}")

            module = importlib.util.module_from_spec(spec)

            # 将模块添加到 sys.modules（避免重复导入）
            sys.modules[module_name] = module

            # 执行模块
            spec.loader.exec_module(module)

            logger.LOCAL.debug(f"模块导入成功: {module_name}")
            return module

        except Exception as e:
            raise ScriptExecutionError(f"导入 main.py 失败: {str(e)}")

    def _execute_with_timeout(
        self, run_func, job_id: int, task_batch_id: int, extra_params: dict
    ) -> tuple[bool, any]:
        """
        在独立线程中执行 run() 方法，支持中断检测
        
        自动检测并支持同步和异步函数：
        - 同步函数：直接调用
        - 异步函数：在新的事件循环中运行

        注意:
            Python 线程无法强制终止，如果脚本长时间运行，
            建议在需求方的 run() 方法中也定期检查中断信号
        
        Returns:
            tuple[bool, any]: (是否成功, 返回值/错误信息)
        """
        self._result = None
        self._exception = None
        self._loop = None
        self._task = None
        
        # 检查是否是异步函数
        is_async = inspect.iscoroutinefunction(run_func)
        if is_async:
            logger.LOCAL.debug("检测到异步 run() 函数，将在新事件循环中执行")
        else:
            logger.LOCAL.debug("检测到同步 run() 函数")

        # 复制当前线程的 context，用于在新线程中继承（解决 ContextVar 跨线程问题）
        ctx = contextvars.copy_context()

        def target():
            """线程执行目标"""
            try:
                if is_async:
                    # 异步函数：在新的事件循环中运行
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    self._loop = loop  # 保存循环引用，用于中断
                    try:
                        # 创建任务而不是直接 run_until_complete
                        coro = run_func(job_id=job_id, task_batch_id=task_batch_id, extra_params=extra_params)
                        task = loop.create_task(coro)
                        self._task = task  # 保存任务引用，用于中断
                        result = loop.run_until_complete(task)
                        self._result = result
                    except asyncio.CancelledError:
                        logger.LOCAL.warning("异步任务被取消")
                        self._exception = Exception("任务被中断")
                    except Exception as e:
                        self._exception = e
                    finally:
                        # 正确清理事件循环：取消所有待处理任务，确保事件循环关闭，防止内存泄漏
                        try:
                            # 获取所有待处理的任务
                            pending = asyncio.all_tasks(loop)
                            if pending:
                                logger.LOCAL.debug(f"清理 {len(pending)} 个待处理的异步任务")
                                # 取消所有任务
                                for pending_task in pending:
                                    pending_task.cancel()
                                # 等待取消完成（忽略 CancelledError）
                                loop.run_until_complete(
                                    asyncio.gather(*pending, return_exceptions=True)
                                )
                        except Exception as cleanup_error:
                            logger.LOCAL.warning(f"清理异步任务时出错: {cleanup_error}")
                        finally:
                            # 关闭事件循环
                            try:
                                loop.run_until_complete(loop.shutdown_asyncgens())
                            except Exception:
                                pass
                            loop.close()
                            self._loop = None
                            self._task = None
                else:
                    # 同步函数：直接调用
                    result = run_func(job_id=job_id, task_batch_id=task_batch_id, extra_params=extra_params)
                    self._result = result
            except Exception as e:
                self._exception = e

        # 创建并启动线程（在复制的 context 中运行）
        thread = threading.Thread(target=lambda: ctx.run(target), daemon=True)
        thread.start()

        # 等待线程完成（带中断检测）
        check_interval = 1  # 每秒检查一次

        # 永远循环，只有在中断信号或线程完成时才退出
        while thread.is_alive():
            # 检查是否有中断信号
            if sj.ThreadPoolCache.event_is_set(task_batch_id):
                logger.LOCAL.warning("检测到任务中断信号")
                
                # 如果是异步任务，尝试取消它
                if is_async and self._loop is not None and self._task is not None:
                    logger.LOCAL.debug("尝试取消异步任务...")
                    try:
                        # 使用线程安全的方式在事件循环中取消任务
                        self._loop.call_soon_threadsafe(self._task.cancel)
                        logger.LOCAL.debug("已发送取消信号到异步任务")
                    except Exception:
                        pass
                else:
                    logger.LOCAL.warning(
                        "同步任务中断需要脚本自行检查（建议在脚本中使用 sj.ThreadPoolCache.event_is_set 检查）"
                    )
                
                # 继续等待一段时间让脚本有机会响应
                thread.join(timeout=10)
                if thread.is_alive():
                    logger.LOCAL.error("脚本未响应中断信号，任务可能仍在后台运行")
                raise asyncio.CancelledError()

            thread.join(timeout=check_interval)

        # 检查异常
        if self._exception is not None:
            # 如果原异常是 ScriptExecutionError 且携带了 data，则保留 data
            if isinstance(self._exception, ScriptExecutionError) and hasattr(self._exception, 'data'):
                raise ScriptExecutionError(self._exception, data=self._exception.data)
            else:
                raise ScriptExecutionError(self._exception)

        # 正常执行完成，返回结果（可以是任意类型，包括 None）
        return True, self._result

