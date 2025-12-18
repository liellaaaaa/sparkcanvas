"""
请求日志中间件
"""
from fastapi import Request
from loguru import logger
import time


async def logging_middleware(request: Request, call_next):
    """
    请求日志中间件
    
    Args:
        request: FastAPI请求对象
        call_next: 下一个中间件或路由处理函数
    
    Returns:
        响应对象
    """
    start_time = time.time()
    
    # 记录请求信息
    logger.info(
        f"Request: {request.method} {request.url.path} | "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    # 处理请求
    response = await call_next(request)
    
    # 计算处理时间
    process_time = time.time() - start_time
    
    # 记录响应信息
    logger.info(
        f"Response: {response.status_code} | "
        f"Time: {process_time:.2f}s | "
        f"Path: {request.url.path}"
    )
    
    return response

