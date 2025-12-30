"""
工作台相关 Schema 定义
"""
from __future__ import annotations

from typing import Literal, Optional, Dict, Any

from pydantic import BaseModel, Field


class WorkspaceSessionCreateOut(BaseModel):
    """创建会话响应"""

    session_id: str = Field(..., description="会话ID")
    created_at: str = Field(..., description="创建时间（ISO8601）")
    expires_at: str = Field(..., description="过期时间（ISO8601）")


class WorkspaceSendMessageIn(BaseModel):
    """发送消息请求"""

    session_id: str = Field(..., description="会话ID")
    message: str = Field(..., description="用户输入的消息内容")
    material_source: Literal["online", "rag"] = Field(
        "online", description='素材源："online"(联网)、"rag"(知识库)'
    )
    platform: Literal["xiaohongshu", "douyin"] = Field(
        ..., description='目标平台："xiaohongshu" 或 "douyin"'
    )


class WorkspaceContent(BaseModel):
    """生成的内容结果"""

    title: str = Field(..., description="内容标题")
    body: str = Field(..., description="正文内容（Markdown）")
    image_url: Optional[str] = Field(None, description="配图URL")


class WorkspaceSendMessageOut(BaseModel):
    """发送消息响应"""

    session_id: str
    content: WorkspaceContent
    status: Literal["generating", "completed"]
    timestamp: str


class WorkspaceSessionInfoOut(BaseModel):
    """会话信息"""

    session_id: str
    created_at: str
    expires_at: str
    message_count: int
    last_message_time: Optional[str] = None


class WorkspaceRegenerateIn(BaseModel):
    """重新生成请求"""

    session_id: str = Field(..., description="会话ID")
    adjustments: Dict[str, Any] = Field(
        default_factory=dict, description="调整参数，如情绪强度、风格偏好等"
    )


class WorkspaceRegenerateOut(WorkspaceSendMessageOut):
    """重新生成响应，与发送消息响应结构一致"""

    pass



