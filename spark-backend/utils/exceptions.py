"""
异常处理工具
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..core.exceptions import SparkCanvasException
from .response import error_response


async def exception_handler(request: Request, exc: SparkCanvasException) -> JSONResponse:
    """
    处理自定义异常
    
    Args:
        request: FastAPI请求对象
        exc: 自定义异常
    
    Returns:
        JSON响应
    """
    return JSONResponse(
        status_code=exc.code,
        content=error_response(exc.code, exc.message, exc.message).dict()
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    处理HTTP异常
    
    Args:
        request: FastAPI请求对象
        exc: HTTP异常
    
    Returns:
        JSON响应
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.status_code, exc.detail).dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    处理请求验证异常
    
    Args:
        request: FastAPI请求对象
        exc: 验证异常
    
    Returns:
        JSON响应
    """
    errors = exc.errors()
    error_details = {error["loc"][-1]: error["msg"] for error in errors}
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(400, "请求参数错误", error_details).dict()
    )

