import threading
import time
import queue
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Callable, Dict, Optional, Union

from snailjob.config import get_snailjob_settings
from snailjob.args import WfContext, build_args
from snailjob.ctx import SnailContextManager
from snailjob.deco import MapExecutor, MapReduceExecutor
from snailjob.err import SnailJobError
from snailjob.log import SnailLog
from snailjob.metrics import get_metrics
from snailjob.rpc import register_executors, send_dispatch_result, send_dispatch_start, registry_node_metadata
from snailjob.schemas import (
    DispatchJobRequest,
    ExecuteResult,
    ExecutorTypeEnum,
    JobExecutor,
    JobExecutorInfo,
    JobTaskTypeEnum,
    MapReduceStageEnum,
    Result,
    StatusEnum,
    StopJobRequest, NodeMetadataRequest,
)
from snailjob.utils import build_dispatch_result
from snailjob.outbox import get_outbox

# 全局配置实例
settings = get_snailjob_settings()


class ThreadPoolCache:
    """线程池执行器缓存"""

    _cache_thread_pool: Dict[int, ThreadPoolExecutor] = {}
    _cache_events: Dict[int, threading.Event] = {}
    _cache_expire_time: Dict[int, float] = {}  # 记录每个线程池的过期时间（时间戳）
    _lock = threading.RLock()
    _monitor_thread: Optional[threading.Thread] = None
    _monitor_interval: int = 5  # 监控间隔：5秒

    @staticmethod
    def create_thread_pool(task_batch_id: int, parallel_num: int, executor_timeout: int) -> ThreadPoolExecutor:
        """创建线程池
        
        Args:
            task_batch_id: 任务批次ID
            parallel_num: 并行数量
            executor_timeout: 执行器超时时间（秒）
        """
        current_time = time.time()
        expire_time = current_time + executor_timeout  # 计算过期时间
        with ThreadPoolCache._lock:
            if task_batch_id in ThreadPoolCache._cache_thread_pool:
                cache_thread_pool = ThreadPoolCache._cache_thread_pool[task_batch_id]
                # 更新过期时间
                ThreadPoolCache._cache_expire_time[task_batch_id] = expire_time
                if cache_thread_pool._max_workers > 1:
                    return cache_thread_pool

                # HACK: _max_workers 为私有变量, 另外这样是否起到作用
                cache_thread_pool._max_workers = min(
                    parallel_num,
                    cache_thread_pool._max_workers,
                )
                return cache_thread_pool

            thread_pool_executor = ThreadPoolExecutor(
                max_workers=parallel_num,
                thread_name_prefix=f"snail-job-job-{task_batch_id}",
            )

            ThreadPoolCache._cache_thread_pool[task_batch_id] = thread_pool_executor
            ThreadPoolCache._cache_events[task_batch_id] = threading.Event()
            ThreadPoolCache._cache_expire_time[task_batch_id] = expire_time

            # 启动监控线程（如果还没启动）
            ThreadPoolCache._start_monitoring()

            return thread_pool_executor

    @staticmethod
    def get_thread_pool(task_batch_id: int) -> ThreadPoolExecutor:
        """获取线程池"""
        with ThreadPoolCache._lock:
            return ThreadPoolCache._cache_thread_pool.get(task_batch_id)

    @staticmethod
    def get_thread_pool_size() -> int:
        """获取线程池缓存大小"""
        with ThreadPoolCache._lock:
            return len(ThreadPoolCache._cache_thread_pool)

    @staticmethod
    def event_is_set(task_batch_id: int) -> threading.Event:
        with ThreadPoolCache._lock:
            event = ThreadPoolCache._cache_events.get(task_batch_id)
            return event is not None and event.is_set()

    @staticmethod
    def stop_thread_pool(task_batch_id: int):
        with ThreadPoolCache._lock:
            # 1. 发送
            thread_event = ThreadPoolCache._cache_events.get(task_batch_id)
            if thread_event is not None:
                thread_event.set()

            # 2. 关闭线程池，不再接受新任务
            thread_pool_executor = ThreadPoolCache._cache_thread_pool.pop(
                task_batch_id,
                None,
            )
            if thread_pool_executor is not None:
                thread_pool_executor.shutdown(wait=False)
            
            # 3. 清理相关记录
            ThreadPoolCache._cache_events.pop(task_batch_id, None)
            ThreadPoolCache._cache_expire_time.pop(task_batch_id, None)

    @staticmethod
    def _update_cache_metrics():
        """更新线程池缓存指标到 metrics"""
        try:
            from snailjob.metrics import get_metrics
            metrics = get_metrics()
            cache_size = ThreadPoolCache.get_thread_pool_size()
            # 上报线程池缓存大小
            metrics.set_thread_pool_cache(cache_size)
        except Exception as e:
            SnailLog.LOCAL.debug(f"更新线程池缓存指标失败: {e}")

    @staticmethod
    def _check_timeout_and_cleanup():
        """检查超时的线程池并自动清理"""
        current_time = time.time()
        timeout_task_batch_ids = []
        
        with ThreadPoolCache._lock:
            for task_batch_id, expire_time in list(ThreadPoolCache._cache_expire_time.items()):
                # 直接判断当前时间是否超过过期时间
                if current_time >= expire_time:
                    timeout_task_batch_ids.append(task_batch_id)
        
        # 清理超时的线程池
        for task_batch_id in timeout_task_batch_ids:
            expire_time = ThreadPoolCache._cache_expire_time.get(task_batch_id, current_time)
            SnailLog.LOCAL.info(
                f"线程池超时，自动清理: task_batch_id={task_batch_id}, "
                f"过期时间={expire_time:.1f}, 当前时间={current_time:.1f}"
            )
            ThreadPoolCache.stop_thread_pool(task_batch_id)

    @staticmethod
    def _start_monitoring():
        """启动线程池缓存监控线程"""
        if ThreadPoolCache._monitor_thread is None or not ThreadPoolCache._monitor_thread.is_alive():
            def monitor_loop():
                """监控循环"""
                while True:
                    try:
                        # 更新指标
                        ThreadPoolCache._update_cache_metrics()
                        # 检查超时并清理
                        ThreadPoolCache._check_timeout_and_cleanup()
                        time.sleep(ThreadPoolCache._monitor_interval)
                    except Exception as e:
                        SnailLog.LOCAL.debug(f"线程池缓存监控线程异常: {e}")
                        time.sleep(ThreadPoolCache._monitor_interval)
            
            ThreadPoolCache._monitor_thread = threading.Thread(
                target=monitor_loop,
                name="snail-job-thread-pool-cache-monitor",
                daemon=True
            )
            ThreadPoolCache._monitor_thread.start()
            SnailLog.LOCAL.debug("线程池缓存监控线程已启动")


class ExecutorManager:
    """执行管理器"""

    _executors: Dict[str, JobExecutorInfo] = {}
    _lock = threading.RLock()
    _running_lock = threading.RLock()
    _running_tasks: int = 0

    # 单机串行：全局串行队列（客户端同一时刻只允许执行 1 个 taskBatch）
    _serial_queue: "queue.Queue[tuple]" = queue.Queue()
    _serial_worker_started: bool = False
    # 单机串行：排队任务取消集合（用于 stop，将任务从队列语义上“移除”）
    _serial_cancelled: set = set()
    _serial_cancelled_lock = threading.RLock()

    @staticmethod
    def _cancel_serial(task_batch_id: int) -> None:
        if task_batch_id is None:
            return
        with ExecutorManager._serial_cancelled_lock:
            ExecutorManager._serial_cancelled.add(int(task_batch_id))

    @staticmethod
    def _is_serial_cancelled(task_batch_id: int) -> bool:
        if task_batch_id is None:
            return False
        with ExecutorManager._serial_cancelled_lock:
            return int(task_batch_id) in ExecutorManager._serial_cancelled

    @staticmethod
    def _clear_serial_cancelled(task_batch_id: int) -> None:
        if task_batch_id is None:
            return
        with ExecutorManager._serial_cancelled_lock:
            ExecutorManager._serial_cancelled.discard(int(task_batch_id))

    @staticmethod
    def _select_executor(
        executor_info: JobExecutorInfo,
        taks_type: JobTaskTypeEnum,
        mr_stage: MapReduceStageEnum = None,
        task_name: str = None,
    ) -> Optional[Callable]:
        """根据调度参数选择执行器函数"""
        if (
            taks_type == JobTaskTypeEnum.MAP
            or taks_type == JobTaskTypeEnum.MAP_REDUCE
            and mr_stage == MapReduceStageEnum.MAP
        ):
            if task_name is None:
                raise SnailJobError("Map任务名称不能为空")
            if task_name in executor_info.mapMethods:
                return executor_info.mapMethods[task_name]
            else:
                raise SnailJobError(f"Map任务 [{task_name}] 不存在")
        elif taks_type == JobTaskTypeEnum.MAP_REDUCE:
            if mr_stage == MapReduceStageEnum.REDUCE:
                if executor_info.reduceMethod is None:
                    raise SnailJobError("Reduce任务不存在")
                return executor_info.reduceMethod
            elif mr_stage == MapReduceStageEnum.MERGE_REDUCE:
                if executor_info.mergeMethod is None:
                    raise SnailJobError("Merge任务不存在")
                return executor_info.mergeMethod
        else:
            if executor_info.jobMethod is None:
                raise SnailJobError("执行器不存在")
            return executor_info.jobMethod

    @staticmethod
    def register(executor: Union[Callable, MapExecutor, MapReduceExecutor]):
        """注册执行器

        Args:
            executor (callable): 执行器函数, 必须为 `@job` 装饰的函数，
            或者是`MapExecutor`, `MapReduceExecutor`类型

        Raises:
            SnailJobError: 执行器配置错误
        """
        if callable(executor):
            if not hasattr(executor, "executor_name"):
                raise SnailJobError(f"[{executor.__name__}] 没有使用 @job 装饰器")

            with ExecutorManager._lock:
                if executor.executor_name in ExecutorManager._executors:
                    raise SnailJobError(f"执行器 [{executor.executor_name}] 已经存在")

                ExecutorManager._executors[executor.executor_name] = JobExecutorInfo(
                    executorName=executor.executor_name,
                    jobMethod=executor,
                )
                SnailLog.LOCAL.info(f"成功注册执行器: {executor.executor_name}")
        elif isinstance(executor, (MapExecutor, MapReduceExecutor)):
            executor_info = executor.executor_info
            with ExecutorManager._lock:
                if executor_info.executorName in ExecutorManager._executors:
                    raise SnailJobError(f"执行器 [{executor_info.executorName}] 已经存在")
                ExecutorManager._executors[executor_info.executorName] = executor_info
                SnailLog.LOCAL.info(f"成功注册执行器: {executor_info.executorName}")
        else:
            raise SnailJobError("错误的执行器类型")

    @staticmethod
    def register_or_update(executor: Union[Callable, MapExecutor, MapReduceExecutor]):
        """
        注册或更新执行器（用于运行时动态追加/刷新）。

        规则：
        - 不存在：新增
        - 已存在：覆盖更新（仅影响后续任务；已提交执行的任务不受影响）
        """
        if callable(executor):
            if not hasattr(executor, "executor_name"):
                raise SnailJobError(f"[{executor.__name__}] 没有使用 @job 装饰器")

            with ExecutorManager._lock:
                ExecutorManager._executors[executor.executor_name] = JobExecutorInfo(
                    executorName=executor.executor_name,
                    jobMethod=executor,
                )
                SnailLog.LOCAL.info(f"注册/更新执行器: {executor.executor_name}")
        elif isinstance(executor, (MapExecutor, MapReduceExecutor)):
            executor_info = executor.executor_info
            with ExecutorManager._lock:
                ExecutorManager._executors[executor_info.executorName] = executor_info
                SnailLog.LOCAL.info(f"注册/更新执行器: {executor_info.executorName}")
        else:
            raise SnailJobError("错误的执行器类型")

    @staticmethod
    def _execute_wrapper(
        job_method: Callable,
        request: DispatchJobRequest,
    ):
        # running++：用于“单机串行/空闲探测”更实时地判断客户端是否空闲
        with ExecutorManager._running_lock:
            ExecutorManager._running_tasks += 1

        # 设置 context
        SnailContextManager.set_context(request)
        
        # 获取指标收集器
        metrics = get_metrics()
        start_time = time.time()

        try:
            job_args = build_args(request)
            execute_result: ExecuteResult = job_method(job_args)
            
            # 记录任务执行时长
            duration = time.time() - start_time
            job_id = str(request.jobId)
            metrics.record_job_execution_duration(job_id, duration)

            dispatch_result = build_dispatch_result(
                request=request,
                execute_result=execute_result,
                change_wf_context=job_args.change_wf_context,
            )
            # 优化：优先走“官方原版”直连上报；失败才进入 outbox 持久化补偿
            status = send_dispatch_result(dispatch_result)
            if status == StatusEnum.YES:
                SnailLog.REMOTE.info(
                    f"Task executed and reported successfully taskBatchId:{request.taskBatchId} {execute_result}"
                )
                return

            # 直连失败：写入本地 outbox（持久化），由后台线程可靠重试直到 ACK
            outbox = get_outbox()
            outbox.enqueue(dispatch_result)

            # must_ack：等待该 taskBatchId 上报成功；若 stop，则提前结束等待（但 outbox 仍继续重试）
            waiter = outbox.waiter(request.taskBatchId)
            poll = float(getattr(settings, "outbox_wait_ack_poll_seconds", 0.5))
            while not waiter.event.is_set():
                if ThreadPoolCache.event_is_set(request.taskBatchId):
                    SnailLog.LOCAL.warning(
                        f"OUTBOX_WAIT_ABORTED_BY_STOP taskBatchId={request.taskBatchId} "
                        f"note=任务已执行完成但等待结果上报ACK阶段收到stop，提前结束等待，后台仍会继续补偿上报"
                    )
                    return
                time.sleep(poll)

            if waiter.status == "acked":
                SnailLog.REMOTE.info(
                    f"Task executed and reported successfully taskBatchId:{request.taskBatchId} {execute_result}"
                )
            else:
                # 超过最大上报窗口放弃（按需求：返回失败，但 outbox 不再上报）
                SnailLog.REMOTE.error(
                    f"Task executed but result report dropped taskBatchId:{request.taskBatchId} "
                    f"reason={waiter.message} {execute_result}"
                )
        except Exception as ex:
            SnailLog.REMOTE.error(
                f"Execution wrapper exception taskBatchId:[{request.getTaskBatchId}] {str(ex)}",
            )
            # 记录任务调度结果错误
            job_id = str(request.jobId)
            metrics.record_dispatch_result_error(job_id)
            
            dispatch_result = build_dispatch_result(
                request=request,
                execute_result=ExecuteResult.failure(str(ex)),
                change_wf_context=job_args.change_wf_context,
            )
            # 异常结果：同样优先直连；失败再进入 outbox，且同样 must_ack
            status = send_dispatch_result(dispatch_result)
            if status == StatusEnum.YES:
                SnailLog.REMOTE.error(
                    f"Execution failed but reported successfully taskBatchId:{request.taskBatchId} err={str(ex)}"
                )
                return

            outbox = get_outbox()
            outbox.enqueue(dispatch_result)

            waiter = outbox.waiter(request.taskBatchId)
            poll = float(getattr(settings, "outbox_wait_ack_poll_seconds", 0.5))
            while not waiter.event.is_set():
                if ThreadPoolCache.event_is_set(request.taskBatchId):
                    SnailLog.LOCAL.warning(
                        f"OUTBOX_WAIT_ABORTED_BY_STOP taskBatchId={request.taskBatchId} "
                        f"note=任务执行失败但等待结果上报ACK阶段收到stop，提前结束等待，后台仍会继续补偿上报"
                    )
                    return
                time.sleep(poll)

            if waiter.status == "acked":
                SnailLog.REMOTE.error(
                    f"Execution failed and reported successfully taskBatchId:{request.taskBatchId} err={str(ex)}"
                )
            else:
                SnailLog.REMOTE.error(
                    f"Execution failed but result report dropped taskBatchId:{request.taskBatchId} "
                    f"reason={waiter.message} err={str(ex)}"
                )
        finally:
            # 集群类型任务, 客户端可以主动关闭线程池, batchId 不会有后续的调度
            if request.taskType == JobTaskTypeEnum.CLUSTER:
                ThreadPoolCache.stop_thread_pool(request.taskBatchId)

            # running--
            with ExecutorManager._running_lock:
                ExecutorManager._running_tasks = max(0, ExecutorManager._running_tasks - 1)

    @staticmethod
    def is_idle(is_print: bool = False) -> bool:
        """更实时的空闲判断：当前是否没有运行中的任务。"""
        with ExecutorManager._running_lock:
            if is_print:
                SnailLog.LOCAL.info(f"【客户端空闲检测】当前运行中任务数: {ExecutorManager._running_tasks}, 是否空闲: {ExecutorManager._running_tasks == 0}")
            return ExecutorManager._running_tasks == 0

    @staticmethod
    def _start_serial_worker():
        """启动单机串行 worker（只启动一次）"""
        if ExecutorManager._serial_worker_started:
            return
        ExecutorManager._serial_worker_started = True

        def _worker():
            while True:
                item = ExecutorManager._serial_queue.get()
                try:
                    req, enqueue_at = item
                    # stop 取消：直接跳过，不再执行
                    if ExecutorManager._is_serial_cancelled(req.taskBatchId):
                        ExecutorManager._clear_serial_cancelled(req.taskBatchId)
                        continue
                    # 等待客户端空闲再执行，保证“单机串行”
                    queue_timeout = int(getattr(req, "queueTimeout", 0) or 0)
                    while not ExecutorManager.is_idle():
                        # stop 取消：等待期间也允许中断
                        if ExecutorManager._is_serial_cancelled(req.taskBatchId):
                            ExecutorManager._clear_serial_cancelled(req.taskBatchId)
                            break
                        if queue_timeout > 0 and (time.time() - enqueue_at) >= queue_timeout:
                            # 排队超时：直接上报失败，避免无限等待
                            try:
                                # 若已 stop，则不再上报超时失败，避免覆盖“停止”语义
                                if ExecutorManager._is_serial_cancelled(req.taskBatchId):
                                    ExecutorManager._clear_serial_cancelled(req.taskBatchId)
                                    break
                                execute_result = ExecuteResult(status=StatusEnum.NO, result=None, message="排队超时")
                                dispatch_result = build_dispatch_result(
                                    request=req,
                                    execute_result=execute_result,
                                    change_wf_context=WfContext.from_dict({}),
                                )
                                send_dispatch_result(dispatch_result)
                            except Exception:
                                pass
                            break
                        time.sleep(0.2)
                    else:
                        # 真正开始执行前，上报服务端切换为 RUNNING
                        try:
                            send_dispatch_start({
                                "jobId": req.jobId,
                                "taskBatchId": req.taskBatchId,
                                "taskId": req.taskId,
                                "groupName": req.groupName
                            })
                        except Exception:
                            pass
                        ExecutorManager._dispatch_impl(req)
                except Exception as e:
                    SnailLog.LOCAL.error(f"单机串行 worker 执行异常: {type(e).__name__}:{e}")
                finally:
                    ExecutorManager._serial_queue.task_done()

        t = threading.Thread(target=_worker, name="snailjob-single-machine-serial", daemon=True)
        t.start()

    @staticmethod
    def _dispatch_impl(request: DispatchJobRequest) -> Result:
        """执行任务批次

        Args:
            dispatch_job_request (DispatchJobRequest): 任务调度信息
        """
        try:
            SnailContextManager.set_context(request)
            if request.executorType != ExecutorTypeEnum.PYTHON:
                SnailLog.REMOTE.error("执行器类型必须为 Python")
                return Result.failure("执行器类型必须为 Python")

            with ExecutorManager._lock:
                executor_info = ExecutorManager._executors.get(request.executorInfo)
            if executor_info is None:
                return Result.failure(f"找不到执行器: {request.executorInfo}")

            if isinstance(request.retryCount, int) and request.retryCount > 0:
                SnailLog.REMOTE.info(f"任务执行/调度失败执行重试. 重试次数:[{request.retryCount}]")

            # 选择执行器函数
            job_method: Callable = None
            job_method = ExecutorManager._select_executor(
                executor_info=executor_info,
                taks_type=request.taskType,
                mr_stage=request.mrStage,
                task_name=request.taskName,
            )
            if job_method is None:
                SnailLog.REMOTE.error("执行器函数不存在")
                return Result.failure("执行器函数不存在")

            # 创建线程池, 执行任务
            thread_pool = ThreadPoolCache.create_thread_pool(
                request.taskBatchId,
                max(1, request.parallelNum),
                request.executorTimeout,
            )
            thread_pool.submit(partial(ExecutorManager._execute_wrapper, job_method, request))

        except Exception:
            message = f"客户端发生非预期异常. taskBatchId:[{request.taskBatchId}]"
            SnailLog.REMOTE.error(message)
            return Result.failure(message, status=StatusEnum.NO)

        SnailLog.REMOTE.info(f"批次:[{request.taskBatchId}] 任务调度成功.")
        return Result.success()

    @staticmethod
    def dispatch(request: DispatchJobRequest) -> Result:
        """
        执行任务批次（入口）。

        当 blockStrategy=5（单机串行）时：入队等待，立即返回成功；由 worker 串行执行。
        """
        if isinstance(getattr(request, "blockStrategy", None), int) and request.blockStrategy == 5:
            ExecutorManager._start_serial_worker()
            ExecutorManager._serial_queue.put((request, time.time()))
            SnailLog.REMOTE.info(f"单机串行入队成功. taskBatchId:[{request.taskBatchId}]")
            return Result.success()

        return ExecutorManager._dispatch_impl(request)

    @staticmethod
    def stop(request: StopJobRequest):
        """停止任务批次

        Args:
            stop_request (StopJobRequest): 任务停止请求
        """
        # 优先取消排队任务（若在队列中，避免后续被 worker 执行）
        ExecutorManager._cancel_serial(request.taskBatchId)
        # 再停止正在运行/已创建的线程池
        ThreadPoolCache.stop_thread_pool(request.taskBatchId)

    @staticmethod
    def register_executors_to_server():
        with ExecutorManager._lock:
            executor_names = list(ExecutorManager._executors.keys())
        executors = [JobExecutor(executorInfo=name) for name in executor_names]
        register_executors(executors)

    @staticmethod
    def registry_node_metadata_to_server():
        request = NodeMetadataRequest(labels=settings.label_dict)
        registry_node_metadata(request)
