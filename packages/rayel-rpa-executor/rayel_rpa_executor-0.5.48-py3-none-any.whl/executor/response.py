"""执行器响应模型"""

from typing import Any, Optional

from pydantic import BaseModel


class ExecutorResponse(BaseModel):
    """
    执行器响应类
    
    用于统一返回执行结果，包含：
    - message: 返回信息，记录成功以及异常的文字提醒
    - data: 实际脚本结果，任意类型，视脚本实际返回结果而定
    
    使用方式：
    1. 在业务脚本（main.py）中：
       - 成功：ExecutorResponse.success(browser_manager, **kwargs) - 自动获取录屏和trace
       - 异常：ExecutorResponse.error(browser_manager, message, **kwargs) - 自动获取录屏、trace和traceback并抛出异常
    
    2. 在执行器代码中：
       - 直接构造：ExecutorResponse(message="...", data=...)
    """
    
    message: str
    data: Any = None
    
    @staticmethod
    def success(
        browser_manager=None,
        message: str = "执行完成",
        **kwargs
    ) -> "ExecutorResponse":
        """
        创建成功响应（平层传递参数，自动转换到 data）
        
        Args:
            browser_manager: BrowserManager 实例，传入后自动获取 video 和 trace（推荐）
            message: 成功信息
            video: 录屏文件路径（手动指定，不传则从 browser_manager 获取）
            trace: trace文件路径（手动指定，不传则从 browser_manager 获取）
            **kwargs: 其他任意业务参数（自动添加到 data）
            
        Returns:
            ExecutorResponse: 成功响应对象，所有参数自动放入 data 字典
            
        Examples:
            # 方式1：传入 browser_manager 自动获取（推荐）
            ExecutorResponse.success(
                self.browser,
                title="test",
                count=100
            )
            
            # 方式2：手动传递 video 和 trace
            ExecutorResponse.success(
                video=browser_manager.get_video_path(),
                trace=browser_manager.get_trace_path(),
                title="test"
            )
            
            # 结果：{"message": "执行完成", "data": {"video": "...", "trace": "...", "title": "test", "count": 100}}
        """
        # 自动构造 data 字典
        result_data = {}
        
        # 从 browser_manager 自动获取 video 和 trace
        if browser_manager:
            try:
                auto_video = browser_manager.get_video_path()
                auto_trace = browser_manager.get_trace_path()
                if auto_video:
                    result_data["video"] = auto_video
                if auto_trace:
                    result_data["trace"] = auto_trace
            except:
                pass
        
        # 添加其他参数
        result_data.update(kwargs)
        
        return ExecutorResponse(message=message, data=result_data if result_data else None)
    
    @staticmethod
    def error(
        browser_manager,
        message: str = "执行失败",
        **kwargs
    ):
        """
        直接处理异常并抛出 ScriptExecutionError（平层传递参数）
        
        自动提取 traceback，并获取录屏和trace文件，然后抛出 ScriptExecutionError。
        
        Args:
            browser_manager: BrowserManager 实例，用于获取 video 和 trace
            message: 错误消息
            **kwargs: 其他业务数据
            
        Raises:
            ScriptExecutionError: 带有完整数据的脚本执行异常
            
        Examples:
            # 方式1：自定义消息（推荐）
            except Exception as e:
                logger.REMOTE.error(f"执行异常: {str(e)}")
                ExecutorResponse.error(self.browser, f"执行异常: {str(e)}")
            
            # 方式2：简单消息
            except asyncio.CancelledError as e:
                ExecutorResponse.error(self.browser, "流程被中断")
            
            # 方式3：添加额外业务数据
            except Exception as e:
                ExecutorResponse.error(self.browser, f"数据处理失败: {str(e)}", step="数据处理", retry_count=3)
        """
        import traceback
        from executor.exceptions import ScriptExecutionError
        
        # 构造 data 字典，自动添加 traceback
        result_data = {
            "traceback": traceback.format_exc()
        }
        
        # 获取 video 和 trace
        if browser_manager:
            try:
                video = browser_manager.get_video_path()
                trace = browser_manager.get_trace_path()
                if video:
                    result_data["video"] = video
                if trace:
                    result_data["trace"] = trace
            except:
                pass
        
        # 添加其他参数
        result_data.update(kwargs)
        
        # 抛出异常
        raise ScriptExecutionError(message, data=result_data)
