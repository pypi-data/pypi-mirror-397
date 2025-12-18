"""
Playwright RPA 执行器 - FastAPI 应用

基于 FastAPI + APScheduler 的现代化执行器架构：
- FastAPI: 提供健康检查和监控接口
- APScheduler: 管理浏览器池定时清理任务
- SnailJob: 分布式任务调度

使用方式:
    # 本地运行
    python main.py
    # 或
    uvicorn main:app --host 0.0.0.0 --port 8000

    # Docker 运行
    docker run -e GIT_TOKEN=xxx snail-job-playwright

    # Docker Compose
    docker-compose up -d
"""
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI

from snailjob import ExecutorManager, client_main
from executor import executor
from executor.logger import logger
from executor.refresh_thread import DynamicExecutorRefresher
from routes.download import router as download_router


# 创建 FastAPI 应用
app = FastAPI(
    title="Playwright RPA Executor",
    description="基于 SnailJob 的 Playwright 自动化执行器"
)

# 注册路由
app.include_router(download_router)


@app.get("/health")
async def health():
    """详细健康检查"""
    return {"status": "ok"}

@app.get("/debug/threads")
async def dump_threads():
    """
    DEBUG专用: 打印当前所有活跃线程的堆栈信息
    用于排查线程泄露问题
    """
    import sys
    import traceback
    from fastapi.responses import PlainTextResponse
    
    thread_dump = []
    frames = sys._current_frames()
    
    thread_dump.append(f"Total Threads: {len(frames)}")
    thread_dump.append("=" * 60)
    
    for thread_id, frame in frames.items():
        thread_dump.append(f"\n>> Thread ID: {thread_id}")
        # 获取除了 debug 线程之外的堆栈
        stack = "".join(traceback.format_stack(frame))
        thread_dump.append(stack)
        thread_dump.append("-" * 40)
        
    return PlainTextResponse("\n".join(thread_dump))


def start_fastapi():
    """在后台线程启动 FastAPI 服务"""
    import uvicorn
    # 禁用 uvicon 的信号处理，避免干扰主线程
    # 禁用 uvicorn 的日志配置，避免关闭我们自己的 logging handlers
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info", loop="asyncio", log_config=None)
    server = uvicorn.Server(config)
    # 覆盖 install_signal_handlers 为空操作，让主线程处理信号
    server.install_signal_handlers = lambda: None
    server.run()


if __name__ == "__main__":
    logger.LOCAL.info("=" * 60)
    logger.LOCAL.info("🚀 Playwright RPA 执行器服务启动 (Native Mode)")
    
    # 1. 注册执行器，暂不需要注册，因为通过动态执行器刷新线程扫描rpa_projects/app/services/**/main.py 里带 @service(id="...", name="...") 的 Service 类，并生成可用于动态注册的执行器描述信息。
    # ExecutorManager.register(executor.playwright_executor)
    # logger.LOCAL.info("✅ 执行器已注册")

    # 1.1 启动动态执行器刷新（后台线程），并立即扫描一次
    try:
        refresher = DynamicExecutorRefresher(interval_seconds=60)
        refresher.run_once()
        refresher.start()
        logger.LOCAL.info("✅ 动态执行器刷新已启动")
    except Exception as e:
        logger.LOCAL.warning(f"⚠️ 动态执行器刷新启动失败（不影响主流程）: {e}")
    
    # 2. 启动 FastAPI 监控服务（后台线程）
    fastapi_thread = threading.Thread(target=start_fastapi, daemon=True, name="FastAPI-Server")
    fastapi_thread.start()
    logger.LOCAL.info(f"✅ 监控服务已启动: http://0.0.0.0:8000")

    # 3. 启动 SnailJob 客户端（主线程阻塞运行）
    logger.LOCAL.info("✅ SnailJob 客户端正在启动...")
    logger.LOCAL.info("=" * 60)
    
    try:
        client_main()
    except KeyboardInterrupt:
        logger.LOCAL.info("🛑 接收到退出信号")
    except Exception as e:
        logger.LOCAL.error(f"❌ 客户端异常退出: {e}")