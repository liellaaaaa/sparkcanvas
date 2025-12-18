"""
限流中间件
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

from ..core.config import AppConfig
from ..core.rate_limit import check_rate_limit
from ..core.exceptions import RateLimitError
from ..utils.response import error_response


async def rate_limit_middleware(request: Request, call_next, config: AppConfig):
    """
    限流中间件
    
    Args:
        request: FastAPI请求对象
        call_next: 下一个中间件或路由处理函数
        config: 应用配置对象
    
    Returns:
        响应对象
    """
    # 获取客户端IP
    client_ip = request.client.host if request.client else "unknown"
    
    # 获取会话ID（如果存在）
    session_id = request.headers.get("X-Session-ID")
    
    # 检查限流
    allowed, retry_after = check_rate_limit(config, client_ip, session_id)
    
    if not allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=error_response(
                429,
                "请求频率超限",
                {"retry_after": retry_after} if retry_after else None
            ).dict(),
            headers={"Retry-After": str(retry_after)} if retry_after else None
        )
    
    # 继续处理请求
    response = await call_next(request)
    return response

