"""
路由模块
"""
from .auth import router as auth_router
from .workspace import router as workspace_router
from .prompt import router as prompt_router

__all__ = ["auth_router", "workspace_router", "prompt_router"]

