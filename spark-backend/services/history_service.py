"""
历史记录服务层

职责：
- 对话历史记录的查询与搜索
- 与存储层交互，提供业务逻辑封装
"""
from __future__ import annotations

from typing import Optional

from core.config import load_config, AppConfig
from core.logger import logger
from schemas.history import (
    ConversationHistoryItem,
    ConversationHistoryListOut,
    ConversationHistoryDeleteIn,
)
from storage import history_store
from utils.response import APIResponse, success_response


_cfg: AppConfig = load_config()


class HistoryService:
    """历史记录服务"""

    def __init__(self, cfg: AppConfig | None = None) -> None:
        self.cfg = cfg or _cfg

    async def get_conversation_history(
        self,
        user_id: int,
        session_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> APIResponse:
        """
        获取对话历史记录
        
        Args:
            user_id: 用户ID
            session_id: 会话ID，如果为None则返回所有会话的历史记录
            page: 页码
            page_size: 每页数量
        
        Returns:
            APIResponse对象
        """
        # 参数校验
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20
        if page_size > 100:
            page_size = 100  # 限制最大每页数量
        
        # 从存储层获取数据
        data = history_store.get_conversation_history(
            self.cfg, user_id, session_id, page, page_size
        )
        
        # 转换为Schema对象
        items = [
            ConversationHistoryItem(**item) for item in data.get("items", [])
        ]
        
        out = ConversationHistoryListOut(
            total=data.get("total", 0),
            page=data.get("page", page),
            page_size=data.get("page_size", page_size),
            items=items,
        )
        
        logger.info(
            f"[History] user_id={user_id} session_id={session_id} "
            f"查询历史记录 page={page} page_size={page_size} total={out.total}"
        )
        
        return success_response(out)

    async def search_conversation_history(
        self,
        user_id: int,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
    ) -> APIResponse:
        """
        按关键词搜索对话历史记录
        
        Args:
            user_id: 用户ID
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
        
        Returns:
            APIResponse对象
        """
        # 参数校验
        if not keyword or not keyword.strip():
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="搜索关键词不能为空")
        
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20
        if page_size > 100:
            page_size = 100  # 限制最大每页数量
        
        # 从存储层获取数据
        data = history_store.search_conversation_history(
            self.cfg, user_id, keyword.strip(), page, page_size
        )
        
        # 转换为Schema对象
        items = [
            ConversationHistoryItem(**item) for item in data.get("items", [])
        ]
        
        out = ConversationHistoryListOut(
            total=data.get("total", 0),
            page=data.get("page", page),
            page_size=data.get("page_size", page_size),
            items=items,
        )
        
        logger.info(
            f"[History] user_id={user_id} keyword={keyword} "
            f"搜索历史记录 page={page} page_size={page_size} total={out.total}"
        )
        
        return success_response(out)

    async def delete_conversation_history(
        self,
        user_id: int,
        data: ConversationHistoryDeleteIn,
    ) -> APIResponse:
        """
        删除指定的对话历史记录
        
        Args:
            user_id: 用户ID
            data: 删除请求数据（包含session_id和timestamp）
        
        Returns:
            APIResponse对象
        """
        # 参数校验
        if not data.session_id or not data.timestamp:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="session_id和timestamp不能为空")
        
        # 从存储层删除
        deleted = history_store.delete_conversation_history(
            self.cfg, user_id, data.session_id, data.timestamp
        )
        
        if not deleted:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="历史记录不存在或已被删除")
        
        logger.info(
            f"[History] user_id={user_id} session_id={data.session_id} "
            f"timestamp={data.timestamp} 删除历史记录成功"
        )
        
        return success_response(None)
