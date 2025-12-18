"""虚拟环境管理模块

使用 uv 进行依赖管理，提供极速安装和智能冲突解决能力。
"""

import hashlib
import os
import subprocess
import time
import fcntl
from pathlib import Path
from typing import List, Optional
from contextlib import contextmanager

from .config import PlaywrightExecutorConfig
from .exceptions import DependencyInstallError, RequirementNotFoundError
from .logger import logger


class EnvManager:
    """虚拟环境管理器"""

    def __init__(self, config: PlaywrightExecutorConfig):
        self.config = config
        self.venv_path = config.get_venv_path()
        self.service_path = config.get_service_path()
        
        # 并发控制 - 使用配置中的 workspace_root
        self._lock_dir = config.venvs_dir / ".locks"
        self._ensure_lock_dir()
        
        # 启动时清理可能的残留锁文件
        self._cleanup_startup_locks()

    def _ensure_lock_dir(self) -> None:
        """确保锁文件目录存在"""
        try:
            self._lock_dir.mkdir(parents=True, exist_ok=True)
            logger.LOCAL.debug(f"锁文件目录已准备: {self._lock_dir}")
        except Exception as e:
            logger.LOCAL.warning(f"创建锁文件目录失败: {e}")

    def _cleanup_startup_locks(self) -> None:
        """启动时清理所有可能的残留锁文件"""
        try:
            # 清理环境锁目录中的所有锁文件
            if self._lock_dir.exists():
                for lock_file in self._lock_dir.glob("*.lock"):
                    try:
                        venv_name = lock_file.stem
                        self._cleanup_orphaned_locks(venv_name)
                    except Exception as e:
                        logger.LOCAL.warning(f"[启动清理] 清理环境锁失败 {lock_file}: {e}")
            
            # 清理uv相关锁文件
            self._cleanup_lock_files()
            logger.LOCAL.debug("[启动清理] 残留锁文件清理完成")
            
        except Exception as e:
            logger.LOCAL.warning(f"[启动清理] 启动锁清理异常: {e}")

    @contextmanager
    def _venv_lock(self):
        """虚拟环境操作的文件系统锁（增强异常安全，修正并发竞争条件）"""
        venv_name = self.config.get_venv_name()
        lock_file_path = self._lock_dir / f"{venv_name}.lock"
        lock_file = None
        
        logger.LOCAL.debug(f"[并发控制] 请求环境锁: {venv_name}")
        
        try:
            # 1. 使用 a+ 模式打开，避免在获取锁之前截断文件内容（破坏锁信息）
            # 不要使用 'w' 模式，因为 'w' 会在获取锁之前清空文件！
            lock_file = open(lock_file_path, 'a+')
            
            try:
                # 2. 获取独占锁（阻塞直到获得）
                # flock 是基于文件描述符的，如果进程崩溃，OS会自动释放锁
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                
                # 3. 获得锁后，检查并记录被谁占用（仅用于调试日志，实际安全性由 flock 保证）
                # 我们可以读取文件头看看之前是谁（可选），然后覆盖它
                
                # 4. 更新锁文件内容（标记当前持有者）
                lock_file.seek(0)
                lock_file.truncate()
                lock_file.write(f"{os.getpid()}\n{time.time()}\n")
                lock_file.flush()
                
                logger.LOCAL.debug(f"[并发控制] 已获得环境锁: {venv_name} (PID: {os.getpid()})")
                
                yield
                
            except Exception as e:
                logger.LOCAL.error(f"[并发控制] 锁保护的操作失败: {e}")
                raise
            finally:
                # 5. 释放锁
                # 注意：不要在 finally 中删除 (unlink) 锁文件！
                # 如果删除了文件，其他正在等待该文件描述符的进程将获得一个“孤儿锁”，
                # 而新来的进程会创建一个新文件，导致两个进程并行执行！这是严重的 Race Condition。
                # 这里的 close() 会自动释放 flock。
                logger.LOCAL.debug(f"[并发控制] 释放环境锁: {venv_name}")
                if lock_file:
                    try:
                        # 清空内容再关闭？不，保留内容有助于调试谁最后持有锁
                        lock_file.close()
                    except:
                        pass
                
        except (IOError, OSError) as e:
            logger.LOCAL.error(f"[并发控制] 锁文件操作失败: {e}")
            raise DependencyInstallError(f"无法获得环境锁: {e}")

    def _cleanup_orphaned_locks(self, venv_name: str) -> None:
        """
        检查锁状态（不再执行删除操作）
        
        由于采用了标准的 flock 机制，我们不再需要通过检查 PID 来删除文件。
        如果持有锁的进程崩溃，OS 会释放文件锁，后续进程可以直接获得锁。
        此函数现在主要用于输出调试日志，帮助用户理解等待原因。
        """
        lock_file_path = self._lock_dir / f"{venv_name}.lock"
        
        if not lock_file_path.exists():
            return
        
        try:
            content = lock_file_path.read_text().strip().split('\n')
            if len(content) >= 2:
                pid = int(content[0])
                msg = f"[并发控制] 当前锁文件记录持有者 PID={pid}"
                
                if self._is_process_alive(pid):
                     msg += " (进程运行中)"
                else:
                     msg += " (进程已结束，锁可能已由OS释放)"
                
                logger.LOCAL.debug(msg)

        except Exception:
            pass # 仅用于日志，忽略任何错误

    def _is_process_alive(self, pid: int) -> bool:
        """检查指定PID的进程是否还存在"""
        try:
            # 发送信号0检查进程是否存在（不会杀死进程）
            os.kill(pid, 0)
            return True
        except OSError:
            return False
        except Exception:
            return False

    def ensure_environment(self) -> None:
        """
        确保虚拟环境存在且依赖已安装（分层架构，并发安全）

        流程:
            1. 验证业务逻辑文件夹和 main.py 存在
            2. 获取文件系统锁（防止并发冲突）
            3. 确保共享基础环境存在
            4. 创建 service overlay 环境
            5. 安装 service 特定依赖
        """
        # 1. 验证业务逻辑文件夹
        self._validate_service_folder()

        # 2. 使用文件系统锁保护并发操作
        with self._venv_lock():
            # 3. 确保共享基础环境存在
            self._ensure_base_environment()
            
            # 4. 检查 service overlay 环境是否就绪
            if self._is_overlay_environment_ready():
                logger.LOCAL.debug(f"[分层环境] Overlay 环境已就绪: {self.venv_path}")
                return
            
            # 5. 创建/更新 overlay 环境
            self._create_overlay_venv()
            
            # 6. 安装 service 特定依赖
            self._install_service_specific_dependencies()

    def _validate_service_folder(self) -> None:
        """验证业务逻辑文件夹和 main.py 是否存在"""
        if not self.service_path.exists():
            raise RequirementNotFoundError(f"业务逻辑文件夹不存在: {self.service_path}")

        main_py = self.service_path / "main.py"
        if not main_py.exists():
            raise RequirementNotFoundError(f"main.py 不存在: {main_py}")

        logger.LOCAL.debug(f"业务逻辑文件夹验证通过: {self.service_path}")

    def _is_environment_ready(self) -> bool:
        """
        检查环境是否完全就绪（虚拟环境 + 依赖）
        
        用于双重检查模式：获得锁后快速判断是否可以跳过所有操作
        
        Returns:
            True: 环境完全就绪，可以跳过所有操作
            False: 需要进行环境创建或依赖安装
        """
        try:
            # 1. 检查虚拟环境是否存在且有效
            if not self._is_venv_valid():
                logger.LOCAL.debug("[环境检查] 虚拟环境无效")
                return False
            
            # 2. 检查依赖是否为最新（MD5校验）
            requirements_files = self._get_requirements_files()
            if not requirements_files:
                logger.LOCAL.debug("[环境检查] 无依赖文件，环境就绪")
                return True
            
            current_md5 = self._calculate_requirements_md5(requirements_files)
            cached_md5 = self._get_cached_md5()
            
            if current_md5 == cached_md5:
                logger.LOCAL.debug("[环境检查] 依赖文件未变化且虚拟环境有效，环境完全就绪")
                return True
            else:
                logger.LOCAL.debug(f"[环境检查] 依赖文件有变化: {cached_md5} -> {current_md5}")
                return False
                
        except Exception as e:
            logger.LOCAL.warning(f"[环境检查] 检查过程异常，将执行完整流程: {e}")
            return False

    def _is_venv_valid(self) -> bool:
        """检查虚拟环境是否存在且有效"""
        if not self.venv_path.exists():
            return False
        
        # 检查关键文件是否存在
        python_path = self.venv_path / "bin" / "python"
        if not python_path.exists():
            logger.LOCAL.warning(f"虚拟环境Python解释器不存在: {python_path}")
            return False
        
        # 检查 site-packages 目录
        site_packages = self.get_site_packages_paths()
        if not site_packages:
            logger.LOCAL.warning("虚拟环境site-packages目录不存在")
            return False
            
        return True

    def _create_venv(self) -> None:
        """创建虚拟环境（使用 uv）"""
        process = None
        try:
            self.venv_path.parent.mkdir(parents=True, exist_ok=True)

            # 使用 uv 创建虚拟环境（速度更快）
            cmd = ["uv", "venv", str(self.venv_path), "--python", "3.12"]
            logger.LOCAL.debug(f"执行命令: {' '.join(cmd)}")

            # 使用 Popen 以便在超时时正确清理
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                close_fds=True
            )
            
            stdout, stderr = process.communicate(timeout=60)

            if process.returncode != 0:
                raise DependencyInstallError(f"创建虚拟环境失败: {stderr}")

            logger.LOCAL.debug("虚拟环境创建成功（使用 uv）")

        except subprocess.TimeoutExpired:
            raise DependencyInstallError("创建虚拟环境超时（60秒）")
        
        except Exception as e:
            raise DependencyInstallError(f"创建虚拟环境异常: {str(e)}")
            
        finally:
            if process:
                # 🛡️ 终极防御：无条件尝试回收进程
                try:
                    if process.poll() is None:
                        try:
                            process.kill()
                        except Exception:
                            pass
                    
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.wait()
                except Exception:
                    pass

    def _ensure_dependencies(self) -> None:
        """确保依赖已安装且是最新的（增强MD5校验，并发安全）"""
        requirements_files = self._get_requirements_files()

        if not requirements_files:
            logger.LOCAL.debug("[依赖管理] 未找到 pyproject.toml 文件，跳过依赖安装")
            return

        # 计算当前 requirements 文件的 MD5
        current_md5 = self._calculate_requirements_md5(requirements_files)
        logger.LOCAL.debug(f"[依赖管理] 当前依赖MD5: {current_md5}")

        # 获取缓存的 MD5
        cached_md5 = self._get_cached_md5()
        logger.LOCAL.debug(f"[依赖管理] 缓存依赖MD5: {cached_md5}")

        if current_md5 == cached_md5:
            logger.LOCAL.debug("[依赖管理] 依赖文件未变化（MD5一致），跳过安装")
            return

        # 安装依赖
        logger.LOCAL.debug(f"[依赖管理] 依赖文件有变化，开始安装... ({len(requirements_files)}个配置文件)")
        
        install_success = True
        for i, req_file in enumerate(requirements_files, 1):
            try:
                logger.LOCAL.debug(f"[依赖管理] 安装进度 {i}/{len(requirements_files)}: {req_file.name}")
                self._install_requirements(req_file)
            except Exception as e:
                install_success = False
                logger.LOCAL.error(f"[依赖管理] 安装失败 {req_file.name}: {e}")
                raise

        # 更新 MD5 缓存（仅在全部安装成功后）
        if install_success:
            self._save_md5_cache(current_md5)
            logger.LOCAL.debug("[依赖管理] 所有依赖安装完成，MD5缓存已更新")
        else:
            logger.LOCAL.error("[依赖管理] 依赖安装失败，未更新MD5缓存")

    def _get_requirements_files(self) -> List[Path]:
        """
        获取需要安装的依赖配置文件列表

        优先级:
            1. 根目录的 pyproject.toml（通用依赖）
            2. 业务逻辑文件夹的 pyproject.toml（业务特定依赖）
        """
        files = []

        # 1. 根目录的 pyproject.toml
        root_pyproject = self.config.git_repo_dir / "pyproject.toml"
        if root_pyproject.exists():
            files.append(root_pyproject)
            logger.LOCAL.debug(f"发现根目录依赖文件: {root_pyproject}")

        # 2. 业务逻辑文件夹的 pyproject.toml
        service_pyproject = self.service_path / "pyproject.toml"
        if service_pyproject.exists():
            files.append(service_pyproject)
            logger.LOCAL.debug(f"发现业务目录依赖文件: {service_pyproject}")

        return files

    def _calculate_requirements_md5(self, files: List[Path]) -> str:
        """计算多个依赖配置文件的联合 MD5"""
        md5_hash = hashlib.md5()

        for file in sorted(files, key=lambda x: str(x)):  # 排序确保顺序一致
            with open(file, "rb") as f:
                md5_hash.update(f.read())

        return md5_hash.hexdigest()

    def _get_cached_md5(self) -> Optional[str]:
        """获取缓存的 MD5 值"""
        md5_file = self._get_md5_cache_file()

        if not md5_file.exists():
            return None

        try:
            return md5_file.read_text().strip()
        except Exception:
            return None

    def _save_md5_cache(self, md5: str) -> None:
        """保存 MD5 缓存"""
        md5_file = self._get_md5_cache_file()
        md5_file.parent.mkdir(parents=True, exist_ok=True)
        md5_file.write_text(md5)

    def _get_md5_cache_file(self) -> Path:
        """获取 MD5 缓存文件路径"""
        venv_name = self.config.get_venv_name()
        return self.config.md5_cache_dir / f"{venv_name}.md5"

    def _cleanup_lock_files(self) -> None:
        """清理可能的 uv 锁文件（增强异常处理）"""
        cleanup_targets = [
            (self.venv_path / ".lock", "虚拟环境锁文件"),
            (Path.home() / ".cache" / "uv" / ".lock", "uv全局缓存锁"),
            (Path("/tmp") / "uv.lock", "uv临时锁文件"),  # 额外的可能锁位置
        ]
        
        for lock_file, description in cleanup_targets:
            try:
                if lock_file.exists():
                    # 检查锁文件是否可以安全删除
                    if self._can_safely_remove_lock(lock_file):
                        lock_file.unlink()
                        logger.LOCAL.debug(f"[锁清理] 已清理{description}: {lock_file}")
                    else:
                        logger.LOCAL.warning(f"[锁清理] {description}可能被其他进程使用，跳过: {lock_file}")
            except (OSError, IOError) as e:
                logger.LOCAL.warning(f"[锁清理] 清理{description}失败: {e}")
            except Exception as e:
                logger.LOCAL.error(f"[锁清理] 清理{description}异常: {e}")

    def _can_safely_remove_lock(self, lock_file: Path) -> bool:
        """检查锁文件是否可以安全删除"""
        try:
            # 尝试以非阻塞方式获得锁，如果成功说明没有其他进程在使用
            with open(lock_file, 'r') as f:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    return True  # 成功获得锁，说明可以安全删除
                except BlockingIOError:
                    return False  # 锁被占用，不能删除
        except Exception:
            return True  # 如果无法检查，默认允许删除

    def _install_requirements(self, config_file: Path) -> None:
        """安装指定的依赖配置文件（仅使用 uv，启用硬链接优化）"""
        python_path = self.venv_path / "bin" / "python"
        
        # 清理可能的锁文件
        self._cleanup_lock_files()
        
        # 设置环境变量
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        
        # 使用 uv 安装（带重试机制）
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                cmd_uv = [
                    "uv", "pip", "install",
                    "-v",
                    "--python", str(python_path),
                    "-e", str(config_file.parent),
                    "--index-url", "https://pypi.tuna.tsinghua.edu.cn/simple",
                    "--extra-index-url", "https://mirrors.aliyun.com/pypi/simple/",
                ]
                
                logger.LOCAL.debug(f"[依赖安装] 尝试 {attempt}/{max_retries}: {config_file}")
                logger.LOCAL.debug(f"[依赖安装] uv命令: {' '.join(cmd_uv)}")
                
                self._run_install_command(cmd_uv, env, timeout=600)
                logger.LOCAL.debug(f"✅ [uv] 依赖安装成功: {config_file}")
                return
                
            except Exception as e:
                if attempt < max_retries:
                    wait_seconds = 5
                    logger.LOCAL.warning(f"⚠️ [uv] 第{attempt}次安装失败，{wait_seconds}秒后重试: {e}")
                    time.sleep(wait_seconds)
                else:
                    logger.LOCAL.error(f"❌ [uv] 所有重试均失败: {e}")
                    logger.LOCAL.error(f"💡 提示: 请检查网络连接和 pyproject.toml 配置")
                    raise DependencyInstallError(f"uv 安装失败({config_file}): {str(e)}")

    def _run_install_command(self, cmd: List[str], env: dict, timeout: int) -> None:
        """执行安装命令并支持实时日志"""
        process = None
        try:
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                close_fds=True  # 强制关闭非必要的文件描述符
            )
            
            if process.stdout:
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        logger.LOCAL.debug(f"[install] {line}")
            
            return_code = process.wait(timeout=timeout)
            
            if return_code != 0:
                raise Exception(f"命令退出码非零: {return_code}")
                
        except subprocess.TimeoutExpired:
            raise Exception(f"命令执行超时 (>{timeout}s)")
        
        except Exception as e:
            raise
            
        finally:
            if process:
                # 🛡️ 终极防御：无条件尝试回收进程
                try:
                    if process.poll() is None:
                        try:
                            process.kill()
                        except Exception:
                            pass
                    
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.wait()
                except Exception:
                    pass

    def get_site_packages_paths(self) -> List[str]:
        """
        获取虚拟环境的 site-packages 路径

        用于动态导入时添加到 sys.path

        Returns:
            存在的 site-packages 路径列表
        """
        python_version = self.config.get_python_version()

        site_packages_paths = [
            str(self.venv_path / "lib" / python_version / "site-packages"),
            str(self.venv_path / "lib64" / python_version / "site-packages"),  # 兼容某些系统
        ]

        # 只返回存在的路径
        existing_paths = [p for p in site_packages_paths if Path(p).exists()]

        if not existing_paths:
            logger.LOCAL.warning(f"未找到 site-packages 目录: {site_packages_paths}")

        return existing_paths

    def _ensure_base_environment(self) -> None:
        """确保共享基础环境存在且最新"""
        base_venv_path = self.config.get_base_venv_path()
        
        # 获取根目录依赖文件
        root_pyproject = self.config.git_repo_dir / "pyproject.toml"
        if not root_pyproject.exists():
            logger.LOCAL.warning("[分层环境] 根目录无 pyproject.toml，跳过基础环境")
            return
        
        # 计算根目录依赖的 MD5
        current_base_md5 = self._calculate_requirements_md5([root_pyproject])
        cached_base_md5 = self._get_base_cached_md5()
        
        # 检查是否需要更新基础环境
        if base_venv_path.exists() and current_base_md5 == cached_base_md5:
            logger.LOCAL.debug("[分层环境] 基础环境已是最新")
            return
        
        # 创建/更新基础环境
        logger.LOCAL.info("[分层环境] 创建/更新共享基础环境...")
        
        if not base_venv_path.exists():
            # 创建基础环境
            try:
                subprocess.run(
                    ["uv", "venv", str(base_venv_path), "--python", "3.12"],
                    check=True,
                    timeout=60,
                    capture_output=True,
                    text=True
                )
                logger.LOCAL.debug(f"[分层环境] 基础环境创建成功: {base_venv_path}")
            except subprocess.CalledProcessError as e:
                raise DependencyInstallError(f"创建基础环境失败: {e.stderr}")
        
        # 安装根目录依赖到基础环境
        base_python = base_venv_path / "bin" / "python"
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        
        cmd = [
            "uv", "pip", "install",
            "-v",
            "--python", str(base_python),
            "-e", str(root_pyproject.parent),
            "--index-url", "https://pypi.tuna.tsinghua.edu.cn/simple",
            "--extra-index-url", "https://mirrors.aliyun.com/pypi/simple/",
        ]
        
        try:
            logger.LOCAL.debug(f"[分层环境] 安装基础依赖: {' '.join(cmd)}")
            self._run_install_command(cmd, env, timeout=600)
            logger.LOCAL.info("[分层环境] 基础环境依赖安装完成")
        except Exception as e:
            raise DependencyInstallError(f"安装基础环境依赖失败: {e}")
        
        # 保存基础环境 MD5
        self._save_base_md5(current_base_md5)
        logger.LOCAL.info("[分层环境] 基础环境创建完成")

    def _get_base_cached_md5(self) -> Optional[str]:
        """获取基础环境缓存的 MD5"""
        md5_file = self.config.get_base_md5_file()
        if not md5_file.exists():
            return None
        try:
            return md5_file.read_text().strip()
        except Exception:
            return None

    def _save_base_md5(self, md5: str) -> None:
        """保存基础环境 MD5"""
        md5_file = self.config.get_base_md5_file()
        md5_file.parent.mkdir(parents=True, exist_ok=True)
        md5_file.write_text(md5)

    def _create_overlay_venv(self) -> None:
        """创建继承基础环境的 overlay 环境"""
        base_python = self.config.get_base_venv_path() / "bin" / "python"
        
        if not base_python.exists():
            raise DependencyInstallError(f"基础环境 Python 不存在: {base_python}")
        
        # 删除旧的 overlay 环境（如果存在）
        if self.venv_path.exists():
            import shutil
            logger.LOCAL.debug(f"[分层环境] 删除旧的 overlay 环境: {self.venv_path}")
            shutil.rmtree(self.venv_path)
        
        # 创建新的 overlay 环境（继承基础环境）
        try:
            subprocess.run(
                [
                    "uv", "venv", str(self.venv_path),
                    "--python", str(base_python),
                    "--system-site-packages",  # 关键：继承基础环境的包
                ],
                check=True,
                timeout=60,
                capture_output=True,
                text=True
            )
            logger.LOCAL.debug(f"[分层环境] Overlay 环境创建成功: {self.venv_path}")
        except subprocess.CalledProcessError as e:
            raise DependencyInstallError(f"创建 overlay 环境失败: {e.stderr}")

    def _install_service_specific_dependencies(self) -> None:
        """安装 service 特定依赖（排除根目录已有的）"""
        service_pyproject = self.service_path / "pyproject.toml"
        
        if not service_pyproject.exists():
            logger.LOCAL.debug("[分层环境] Service 无特定依赖配置文件")
            return
        
        # 检查 service 是否有实际依赖
        try:
            import tomli
        except ImportError:
            # Python 3.11+ 使用内置的 tomllib
            try:
                import tomllib as tomli
            except ImportError:
                logger.LOCAL.warning("[分层环境] 无法导入 tomli/tomllib，跳过依赖检查")
                # 直接尝试安装
                self._install_requirements(service_pyproject)
                return
        
        try:
            with open(service_pyproject, "rb") as f:
                data = tomli.load(f)
            
            deps = data.get("project", {}).get("dependencies", [])
            if not deps:
                logger.LOCAL.debug("[分层环境] Service 依赖列表为空")
                return
            
            # 安装 service 特定依赖
            logger.LOCAL.info(f"[分层环境] 安装 service 特定依赖: {len(deps)} 个")
            self._install_requirements(service_pyproject)
            
        except Exception as e:
            logger.LOCAL.warning(f"[分层环境] 解析 service pyproject.toml 失败: {e}")
            # 仍然尝试安装
            self._install_requirements(service_pyproject)

    def _is_overlay_environment_ready(self) -> bool:
        """检查 overlay 环境是否就绪"""
        if not self.venv_path.exists():
            return False
        
        # 检查 pyvenv.cfg 是否包含 system-site-packages
        pyvenv_cfg = self.venv_path / "pyvenv.cfg"
        if not pyvenv_cfg.exists():
            return False
        
        try:
            content = pyvenv_cfg.read_text()
            if "include-system-site-packages = true" not in content:
                logger.LOCAL.warning("[分层环境] Overlay 环境配置异常，需重建")
                return False
        except Exception as e:
            logger.LOCAL.warning(f"[分层环境] 读取 pyvenv.cfg 失败: {e}")
            return False
        
        # 检查 service 依赖是否需要更新
        service_pyproject = self.service_path / "pyproject.toml"
        if not service_pyproject.exists():
            return True  # 无特定依赖，环境就绪
        
        current_md5 = self._calculate_requirements_md5([service_pyproject])
        cached_md5 = self._get_cached_md5()
        
        return current_md5 == cached_md5