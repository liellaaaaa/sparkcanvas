"""
Prompt相关 Schema 定义
"""
from __future__ import annotations

from typing import Literal, Optional, List
from datetime import datetime

from pydantic import BaseModel, Field


class PromptCreateIn(BaseModel):
    """创建Prompt请求"""
    
    name: str = Field(..., min_length=1, max_length=255, description="模板名称")
    content: str = Field(..., min_length=1, description="Prompt内容")
    platform: Literal["xiaohongshu", "douyin", "通用"] = Field(
        default="通用",
        description="平台类型：xiaohongshu(小红书)、douyin(抖音)、通用"
    )
    category: Optional[str] = Field(None, max_length=100, description="分类/垂类")
    description: Optional[str] = Field(None, max_length=500, description="模板描述")


class PromptUpdateIn(BaseModel):
    """更新Prompt请求"""
    
    id: int = Field(..., description="Prompt ID")
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="模板名称")
    content: Optional[str] = Field(None, min_length=1, description="Prompt内容")
    platform: Optional[Literal["xiaohongshu", "douyin", "通用"]] = Field(
        None,
        description="平台类型"
    )
    category: Optional[str] = Field(None, max_length=100, description="分类/垂类")
    description: Optional[str] = Field(None, max_length=500, description="模板描述")


class PromptDeleteIn(BaseModel):
    """删除Prompt请求"""
    
    id: int = Field(..., description="Prompt ID")


class PromptOut(BaseModel):
    """Prompt输出"""
    
    id: int = Field(..., description="Prompt ID")
    name: str = Field(..., description="模板名称")
    content: str = Field(..., description="Prompt内容")
    platform: str = Field(..., description="平台类型")
    category: Optional[str] = Field(None, description="分类/垂类")
    description: Optional[str] = Field(None, description="模板描述")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class PromptListOut(BaseModel):
    """Prompt分页列表输出"""
    
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    items: List[PromptOut] = Field(..., description="Prompt列表")

