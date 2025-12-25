"""
Prompt管理路由

接口前缀：/api/v1/prompt

说明：
- 所有接口默认需要登录（Bearer Token），与架构与 API 文档保持一致
"""
from __future__ import annotations

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query

from core.auth import AuthHandler
from dependencies import get_auth_handler, get_session
from models import AsyncSession
from schemas.prompt import (
    PromptCreateIn,
    PromptUpdateIn,
    PromptDeleteIn,
)
from repository.prompt_repo import PromptRepository
from services.prompt_service import PromptService
from utils.response import APIResponse


router = APIRouter(prefix="/api/v1/prompt", tags=["Prompt管理"])

# 认证依赖（统一使用 Access Token）
auth_handler: AuthHandler = get_auth_handler()
CurrentUserId = Annotated[int, Depends(auth_handler.auth_access_dependency)]


@router.post("/create", response_model=APIResponse, summary="创建Prompt")
async def create_prompt(
    payload: PromptCreateIn,
    current_user_id: CurrentUserId,
    session: AsyncSession = Depends(get_session),
):
    """
    创建新的Prompt模板，用于内容生成时的提示词管理。
    
    需要JWT认证，只能创建当前用户自己的Prompt。
    """
    repo = PromptRepository(session)
    service = PromptService(repo)
    return await service.create_prompt(current_user_id, payload)


@router.get("/list", response_model=APIResponse, summary="查询Prompt列表")
async def list_prompts(
    current_user_id: CurrentUserId,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    platform: Optional[str] = Query(None, description="平台筛选：xiaohongshu/douyin/通用"),
    category: Optional[str] = Query(None, description="分类筛选"),
    session: AsyncSession = Depends(get_session),
):
    """
    查询当前用户的所有Prompt模板列表，支持分页和筛选。
    
    支持按platform和category筛选，仅返回当前用户的Prompt。
    """
    repo = PromptRepository(session)
    service = PromptService(repo)
    return await service.list_prompts(
        current_user_id,
        page=page,
        page_size=page_size,
        platform=platform,
        category=category,
    )


@router.put("/update", response_model=APIResponse, summary="更新Prompt")
async def update_prompt(
    payload: PromptUpdateIn,
    current_user_id: CurrentUserId,
    session: AsyncSession = Depends(get_session),
):
    """
    更新指定的Prompt模板，支持更新名称和内容。
    
    需要JWT认证，只能更新当前用户自己的Prompt。
    """
    repo = PromptRepository(session)
    service = PromptService(repo)
    return await service.update_prompt(current_user_id, payload)


@router.delete("/delete", response_model=APIResponse, summary="删除Prompt")
async def delete_prompt(
    payload: PromptDeleteIn,
    current_user_id: CurrentUserId,
    session: AsyncSession = Depends(get_session),
):
    """
    删除指定的Prompt模板。
    
    需要JWT认证，只能删除当前用户自己的Prompt。
    """
    repo = PromptRepository(session)
    service = PromptService(repo)
    return await service.delete_prompt(current_user_id, payload)


@router.get("/{prompt_id}", response_model=APIResponse, summary="获取Prompt详情")
async def get_prompt_detail(
    prompt_id: int,
    current_user_id: CurrentUserId,
    session: AsyncSession = Depends(get_session),
):
    """
    获取指定Prompt的详情（仅限所属用户）
    """
    repo = PromptRepository(session)
    service = PromptService(repo)
    return await service.get_prompt_by_id(prompt_id, current_user_id)

