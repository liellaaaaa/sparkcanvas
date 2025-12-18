"""
CORS 中间件配置
"""
from fastapi.middleware.cors import CORSMiddleware
from typing import List


def setup_cors_middleware(app, allowed_origins: List[str] = None):
    """
    配置CORS中间件
    
    Args:
        app: FastAPI应用实例
        allowed_origins: 允许的源列表，如果为None则允许所有源（仅开发环境）
    """
    if allowed_origins is None:
        # 开发环境：允许所有源
        allowed_origins = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

