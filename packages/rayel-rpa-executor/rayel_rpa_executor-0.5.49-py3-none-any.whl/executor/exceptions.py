"""自定义异常类"""


class ExecutorError(Exception):
    """Playwright 执行器基础异常"""

    pass


class GitOperationError(ExecutorError):
    """Git 操作异常"""

    pass


class RequirementNotFoundError(ExecutorError):
    """需求文件夹或文件不存在异常"""

    pass


class DependencyInstallError(ExecutorError):
    """依赖安装异常"""

    pass


class ScriptExecutionError(ExecutorError):
    """脚本执行异常
    
    支持携带额外数据，用于在异常时也能传递录屏、报告等文件信息
    """
    
    def __init__(self, message: str, data=None):
        """
        初始化异常
        
        Args:
            message: 异常消息
            data: 额外数据（如录屏路径、报告路径等）
        """
        super().__init__(message)
        self.data = data


class ConfigurationError(ExecutorError):
    """配置错误异常"""

    pass

