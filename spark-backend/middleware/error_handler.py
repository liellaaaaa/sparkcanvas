"""
错误处理中间件
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..core.exceptions import SparkCanvasException
from ..utils.response import error_response
from ..utils.exceptions import (
    exception_handler,
    http_exception_handler,
    validation_exception_handler
)


# 这些函数已经在 utils/exceptions.py 中定义
# 这里只是重新导出，方便在 main.py 中使用
__all__ = [
    "exception_handler",
    "http_exception_handler",
    "validation_exception_handler"
]

