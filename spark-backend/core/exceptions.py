"""
自定义异常类
"""


class SparkCanvasException(Exception):
    """基础异常类"""
    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationError(SparkCanvasException):
    """验证错误"""
    def __init__(self, message: str):
        super().__init__(message, code=400)


class AuthenticationError(SparkCanvasException):
    """认证错误"""
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, code=401)


class AuthorizationError(SparkCanvasException):
    """授权错误"""
    def __init__(self, message: str = "无权限访问"):
        super().__init__(message, code=403)


class NotFoundError(SparkCanvasException):
    """资源未找到"""
    def __init__(self, message: str = "资源未找到"):
        super().__init__(message, code=404)


class RateLimitError(SparkCanvasException):
    """限流错误"""
    def __init__(self, message: str = "请求频率超限", retry_after: int = None):
        super().__init__(message, code=429)
        self.retry_after = retry_after


class ServiceUnavailableError(SparkCanvasException):
    """服务不可用"""
    def __init__(self, message: str = "服务暂时不可用"):
        super().__init__(message, code=503)

