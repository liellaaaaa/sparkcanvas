"""
统一响应格式工具
"""
from typing import Any, Optional
from pydantic import BaseModel


class APIResponse(BaseModel):
    """标准API响应格式"""
    code: int
    message: str
    data: Optional[Any] = None
    error: Optional[Any] = None


def success_response(data: Any = None, message: str = "success") -> APIResponse:
    """
    成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
    
    Returns:
        APIResponse对象
    """
    return APIResponse(code=200, message=message, data=data)


def error_response(code: int, message: str, error: Any = None) -> APIResponse:
    """
    错误响应
    
    Args:
        code: 错误码
        message: 错误消息
        error: 错误详情
    
    Returns:
        APIResponse对象
    """
    return APIResponse(code=code, message=message, error=error)

