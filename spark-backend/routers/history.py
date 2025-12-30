"""
历史记录路由

接口前缀：/api/v1/history

说明：
- 所有接口默认需要登录（Bearer Token）
- 历史记录存储在Redis，TTL为7天
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Annotated, Optional

from core.auth import AuthHandler
from dependencies import get_auth_handler
from schemas.history import ConversationHistoryListOut, ConversationHistoryDeleteIn
from services.history_service import HistoryService
from utils.response import APIResponse


router = APIRouter(prefix="/api/v1/history", tags=["历史记录"])

# 认证依赖（统一使用 Access Token）
auth_handler: AuthHandler = get_auth_handler()
CurrentUserId = Annotated[int, Depends(auth_handler.auth_access_dependency)]


@router.get(
    "/conversations",
    response_model=APIResponse,
    summary="查询对话历史记录",
)
async def get_conversation_history(
    current_user_id: CurrentUserId,
    session_id: Optional[str] = Query(None, description="会话ID，不传则返回所有会话"),
    page: int = Query(1, ge=1, description="页码，默认1"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，默认20，最大100"),
):
    """
    查询用户的对话历史记录，支持按会话ID筛选和分页。
    
    Args:
        current_user_id: 当前用户ID（从Token中解析）
        session_id: 会话ID，可选
        page: 页码
        page_size: 每页数量
    
    Returns:
        对话历史记录列表
    """
    service = HistoryService()
    return await service.get_conversation_history(
        current_user_id, session_id, page, page_size
    )


@router.get(
    "/search",
    response_model=APIResponse,
    summary="按关键词搜索历史记录",
)
async def search_conversation_history(
    current_user_id: CurrentUserId,
    keyword: str = Query(..., description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码，默认1"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，默认20，最大100"),
):
    """
    按关键词搜索对话历史记录，支持全文检索。
    
    Args:
        current_user_id: 当前用户ID（从Token中解析）
        keyword: 搜索关键词
        page: 页码
        page_size: 每页数量
    
    Returns:
        匹配的对话历史记录列表
    """
    service = HistoryService()
    return await service.search_conversation_history(
        current_user_id, keyword, page, page_size
    )


@router.delete(
    "/delete",
    response_model=APIResponse,
    summary="删除历史记录",
)
async def delete_conversation_history(
    payload: ConversationHistoryDeleteIn,
    current_user_id: CurrentUserId,
):
    """
    删除指定的对话历史记录。
    
    Args:
        payload: 删除请求数据（包含session_id和timestamp）
        current_user_id: 当前用户ID（从Token中解析）
    
    Returns:
        删除成功响应
    """
    service = HistoryService()
    return await service.delete_conversation_history(current_user_id, payload)

