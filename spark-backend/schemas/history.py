"""
历史记录相关 Schema 定义
"""
from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel, Field


class ConversationHistoryItem(BaseModel):
    """对话历史记录项"""
    
    session_id: str = Field(..., description="会话ID")
    message: str = Field(..., description="用户消息")
    response: str = Field(..., description="助手回复")
    timestamp: str = Field(..., description="时间戳（ISO8601）")


class ConversationHistoryListOut(BaseModel):
    """对话历史记录列表响应"""
    
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    items: List[ConversationHistoryItem] = Field(..., description="历史记录列表")

