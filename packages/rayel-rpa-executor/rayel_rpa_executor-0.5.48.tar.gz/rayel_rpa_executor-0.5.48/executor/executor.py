"""Playwright 执行器主模块"""

import asyncio
import json
from pathlib import Path
from typing import Any

import snailjob as sj

from .config import PlaywrightExecutorConfig
from .env_manager import EnvManager
from .exceptions import (
    DependencyInstallError,
    ExecutorError,
    RequirementNotFoundError,
    ScriptExecutionError,
)
from .logger import logger
from .response import ExecutorResponse
from . import repo_snapshots
from .script_runner import ScriptRunner


@sj.job("PlaywrightExecutor")
def playwright_executor(args: sj.JobArgs) -> sj.ExecuteResult:
    """
    Playwright 通用执行器

    参数格式（job_params）:
    {
        "service_folder": "demo_service",  // 只需写子文件夹名，自动拼接为 app/services/demo_service
        "branch": "main",  // 可选，默认 main
        "workspace_root": "/workspace",  // 可选，默认 /workspace
        "extra_params": {  // 可选，传递给 run() 方法的额外参数
            "env": "test",
            "target_url": "https://example.com"
        }
    }

    环境变量配置（必需）:
    - GIT_REPO_URL: Git 仓库地址（如 https://github.com/org/project.git）
    - GIT_TOKEN: Git Token（用于仓库认证）

    注意:
    - service_folder 参数只需要写子文件夹名称（如：demo_service）
    - 系统会自动拼接父目录 app/services/，最终路径为：app/services/demo_service

    Returns:
        ExecuteResult: 执行成功或失败的结果
    """
    result = None
    lease = None
    try:
        # ========== 1. 解析参数 ==========
        # 设置 job_id 和 task_batch_id 到上下文，后续所有日志自动带前缀
        logger.set_job_and_task_batch_id(job_id=args.job_id, task_batch_id=args.task_batch_id)

        logger.REMOTE.info("🚀 执行器已连接")

        # ========== 2. 创建配置 ==========
        params = _parse_job_params(args.job_params)
        config = _create_config(params)

        logger.REMOTE.info(f"任务详情: ...\n"
            f"📁 需求文件夹: {config.service_folder}\n"
            f"📂 需求文件夹完整路径: {config.get_service_path()}\n"
            f"🌿 Git 分支: {config.git_branch}\n"
            f"📦 args: {vars(args)}"
        )

        # ========== 3. 固定当前代码快照（lease） ==========
        # 说明：执行语义 A（执行时刻 current）：
        # - 任务开始时解析 `{workspace_root}/rpa_projects` symlink 并固定到真实快照目录
        # - 任务执行期间刷新线程切换 current 不影响本任务
        logger.REMOTE.info("步骤 1/3: 代码快照获取 开始")
        lease = repo_snapshots.acquire(
            workspace_root=config.workspace_root,
            git_url=config.git_url,
            git_token=config.git_token,
            branch=config.git_branch,
        )
        # 固定 repo_root，后续 EnvManager/ScriptRunner 全程使用该快照目录
        config.git_repo_dir = lease.repo_root

        # ========== 4. 环境管理：创建虚拟环境、安装依赖 ==========
        logger.REMOTE.info("步骤 2/3: 虚拟环境管理 开始")
        env_manager = EnvManager(config)
        env_manager.ensure_environment()

        # ========== 5. 执行脚本（方法调用） ==========
        logger.REMOTE.info("步骤 3/3: 执行脚本 开始")
        script_runner = ScriptRunner(config)
        site_packages_paths = env_manager.get_site_packages_paths()

        success, result = script_runner.run_main_script(
            site_packages_paths=site_packages_paths,
            job_id=args.job_id,
            task_batch_id=args.task_batch_id,
            extra_params=params.get("extra_params"),
        )

        # ========== 6. 判断执行结果 ==========
        if success:
            logger.REMOTE.info("✅ 执行成功")
            # 使用 ExecutorResponse 包装结果
            response = ExecutorResponse(message="执行成功", data=result)
            logger.REMOTE.info(f"流程返回结果: {response}")
            return sj.ExecuteResult.success(result=response)
        else:
            logger.REMOTE.error(f"❌ 执行失败: {result}")
            # 使用 ExecutorResponse 包装失败结果
            response = ExecutorResponse(message="执行失败", data=result if result else "执行失败")
            logger.REMOTE.info(f"流程返回结果: {response}")
            return sj.ExecuteResult.failure(result=response)

    except RequirementNotFoundError as e:
        import traceback
        logger.REMOTE.error(f"❌ 需求不存在: {e}, 错误详情: \n{traceback.format_exc()}")
        response = ExecutorResponse(message=f"需求不存在：{e}, 错误详情: \n{traceback.format_exc()}", data=result)
        return sj.ExecuteResult.failure(result=response)
    except DependencyInstallError as e:
        import traceback
        logger.REMOTE.error(f"❌ 依赖安装失败: {e}, 错误详情: \n{traceback.format_exc()}")
        response = ExecutorResponse(message=f"依赖安装失败：{e}, 错误详情: \n{traceback.format_exc()}", data=result)
        return sj.ExecuteResult.failure(result=response)
    except asyncio.CancelledError as e:
        import traceback
        logger.REMOTE.error(f"❌ 任务被中断: {e}, 错误详情: \n{traceback.format_exc()}")
        response = ExecutorResponse(message=f"任务被中断：{e}, 错误详情: \n{traceback.format_exc()}", data=result)
        return sj.ExecuteResult.failure(result=response)
    except ScriptExecutionError as e:
        import traceback
        logger.REMOTE.error(f"❌ 执行失败: {e}, 错误详情: \n{traceback.format_exc()}")
        # 优先使用异常携带的 data，否则使用 result 变量
        error_data = e.data if hasattr(e, 'data') and e.data is not None else result
        response = ExecutorResponse(message=f"执行失败: {e}, 错误详情: \n{traceback.format_exc()}", data=error_data)
        return sj.ExecuteResult.failure(result=response)
    except ExecutorError as e:
        import traceback    
        logger.REMOTE.error(f"❌ 执行器错误: {e}, 错误详情: \n{traceback.format_exc()}")
        response = ExecutorResponse(message=f"执行器错误: {e}, 错误详情: \n{traceback.format_exc()}", data=result)
        return sj.ExecuteResult.failure(result=response)
    except Exception as e:
        import traceback
        logger.REMOTE.error(f"❌ 未知错误: {e}, 错误详情: \n{traceback.format_exc()}")
        response = ExecutorResponse(message=f"未知错误: {e}, 错误详情: \n{traceback.format_exc()}", data=result)
        return sj.ExecuteResult.failure(result=response)
    finally:
        # 释放快照租约（引用计数 -1）
        if lease is not None:
            try:
                repo_snapshots.release(lease)
            except Exception:
                # 释放失败不影响任务结果
                pass


def _parse_job_params(job_params: Any) -> dict:
    """解析任务参数"""
    try:
        if isinstance(job_params, str):
            params = json.loads(job_params)
        else:
            params = job_params

        # 验证必填参数
        required_fields = ["service_folder"]
        for field in required_fields:
            if field not in params:
                raise ValueError(f"缺少必填参数: {field}")

        return params

    except json.JSONDecodeError as e:
        raise ValueError(f"任务参数 JSON 解析失败: {str(e)}")


def _create_config(params: dict) -> PlaywrightExecutorConfig:
    """根据参数创建配置对象"""
    return PlaywrightExecutorConfig(
        git_url="",  # 从环境变量读取
        git_token="",  # 从环境变量读取
        git_branch=params.get("branch", "main"),
        workspace_root=Path(params.get("workspace_root", "./workspace")),
        service_folder=params["service_folder"],
    )