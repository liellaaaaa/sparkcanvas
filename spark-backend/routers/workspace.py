"""
工作台路由

接口前缀：/api/v1/workspace

说明：
- 所有接口默认需要登录（Bearer Token），与架构与 API 文档保持一致
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from core.auth import AuthHandler
from dependencies import get_auth_handler
from schemas.workspace import (
    WorkspaceSessionCreateOut,
    WorkspaceSendMessageIn,
    WorkspaceSendMessageOut,
    WorkspaceSessionInfoOut,
    WorkspaceRegenerateIn,
    WorkspaceRegenerateOut,
)
from services.workspace_service import WorkspaceService
from utils.response import APIResponse


router = APIRouter(prefix="/api/v1/workspace", tags=["工作台"])

# 认证依赖（统一使用 Access Token）
auth_handler: AuthHandler = get_auth_handler()
CurrentUserId = Annotated[int, Depends(auth_handler.auth_access_dependency)]


@router.post("/create-session", response_model=APIResponse, summary="创建会话")
async def create_session(current_user_id: CurrentUserId):
    """
    创建新的工作会话，用于内容生成流程。
    """
    service = WorkspaceService()
    return await service.create_session(current_user_id)


@router.post("/send-message", response_model=APIResponse, summary="发送消息")
async def send_message(
    payload: WorkspaceSendMessageIn,
    current_user_id: CurrentUserId,
):
    """
    发送消息到工作台，触发内容生成流程。

    当前实现使用占位生成逻辑，方便前端尽早联调。
    """
    service = WorkspaceService()
    return await service.send_message(current_user_id, payload)


@router.get(
    "/session/{session_id}",
    response_model=APIResponse,
    summary="获取会话信息",
)
async def get_session_info(
    session_id: str,
    current_user_id: CurrentUserId,  # 保留认证依赖，后续可根据 user_id 做权限校验
):
    """
    获取指定会话的详细信息。
    """
    service = WorkspaceService()
    info = await service.get_session_info(session_id)
    if not info:
        raise HTTPException(status_code=404, detail="会话不存在或已过期")
    return APIResponse(code=200, message="success", data=info)


@router.post("/regenerate", response_model=APIResponse, summary="重新生成")
async def regenerate(
    payload: WorkspaceRegenerateIn,
    current_user_id: CurrentUserId,
):
    """
    基于已有会话重新生成内容。
    """
    service = WorkspaceService()
    return await service.regenerate(current_user_id, payload)



