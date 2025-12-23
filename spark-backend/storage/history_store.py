"""
历史记录存储层（Redis实现）

说明：
- 当前使用Redis存储历史记录，后续可迁移到MySQL
- 历史记录按用户ID组织，支持按会话ID筛选和关键词搜索
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from .redis_client import get_redis
from core.config import AppConfig

# 历史记录TTL：7天（与架构文档一致）
HISTORY_TTL_SECONDS = 7 * 24 * 60 * 60  # 7天


def _user_history_key(user_id: int) -> str:
    """生成用户历史记录索引key"""
    return f"history:user:{user_id}:index"


def _conversation_history_key(user_id: int, session_id: str) -> str:
    """生成会话历史记录key"""
    return f"history:user:{user_id}:session:{session_id}"


def _now_iso() -> str:
    """返回UTC时间ISO格式字符串"""
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def save_conversation_history(
    cfg: AppConfig,
    user_id: int,
    session_id: str,
    message: str,
    response: str,
) -> None:
    """
    保存对话历史记录
    
    Args:
        cfg: 应用配置对象
        user_id: 用户ID
        session_id: 会话ID
        message: 用户消息
        response: 助手回复
    """
    r = get_redis(cfg.redis_url)
    if not r:
        return
    
    timestamp = _now_iso()
    history_item = {
        "session_id": session_id,
        "message": message,
        "response": response,
        "timestamp": timestamp,
    }
    
    # 1. 保存到会话历史记录列表（使用List存储，便于按时间顺序查询）
    history_key = _conversation_history_key(user_id, session_id)
    r.lpush(history_key, json.dumps(history_item, ensure_ascii=False))
    r.expire(history_key, HISTORY_TTL_SECONDS)
    
    # 2. 维护用户会话索引（用于快速查询用户的所有会话）
    index_key = _user_history_key(user_id)
    r.sadd(index_key, session_id)
    r.expire(index_key, HISTORY_TTL_SECONDS)
    
    # 3. 维护全局搜索索引（用于关键词搜索）
    # 将消息和回复内容存储到搜索索引中
    search_key = f"history:search:user:{user_id}"
    search_data = {
        "session_id": session_id,
        "message": message,
        "response": response,
        "timestamp": timestamp,
    }
    r.lpush(search_key, json.dumps(search_data, ensure_ascii=False))
    r.expire(search_key, HISTORY_TTL_SECONDS)
    # 限制搜索索引长度，避免内存占用过大
    r.ltrim(search_key, 0, 9999)  # 最多保留10000条记录


def get_conversation_history(
    cfg: AppConfig,
    user_id: int,
    session_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    """
    获取对话历史记录
    
    Args:
        cfg: 应用配置对象
        user_id: 用户ID
        session_id: 会话ID，如果为None则返回所有会话的历史记录
        page: 页码
        page_size: 每页数量
    
    Returns:
        包含total、page、page_size、items的字典
    """
    r = get_redis(cfg.redis_url)
    if not r:
        return {"total": 0, "page": page, "page_size": page_size, "items": []}
    
    items: List[Dict[str, Any]] = []
    
    if session_id:
        # 查询指定会话的历史记录
        history_key = _conversation_history_key(user_id, session_id)
        raw_items = r.lrange(history_key, 0, -1)
        for raw_item in raw_items:
            try:
                item = json.loads(raw_item)
                items.append(item)
            except Exception:
                continue
    else:
        # 查询所有会话的历史记录
        index_key = _user_history_key(user_id)
        session_ids = list(r.smembers(index_key))
        
        for sid in session_ids:
            history_key = _conversation_history_key(user_id, sid)
            raw_items = r.lrange(history_key, 0, -1)
            for raw_item in raw_items:
                try:
                    item = json.loads(raw_item)
                    items.append(item)
                except Exception:
                    continue
    
    # 按时间戳倒序排序（最新的在前）
    items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # 分页
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_items = items[start:end]
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": paginated_items,
    }


def search_conversation_history(
    cfg: AppConfig,
    user_id: int,
    keyword: str,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    """
    按关键词搜索对话历史记录
    
    Args:
        cfg: 应用配置对象
        user_id: 用户ID
        keyword: 搜索关键词
        page: 页码
        page_size: 每页数量
    
    Returns:
        包含total、page、page_size、items的字典
    """
    r = get_redis(cfg.redis_url)
    if not r:
        return {"total": 0, "page": page, "page_size": page_size, "items": []}
    
    search_key = f"history:search:user:{user_id}"
    raw_items = r.lrange(search_key, 0, -1)
    
    # 简单的关键词匹配（后续可优化为更复杂的全文检索）
    keyword_lower = keyword.lower()
    matched_items: List[Dict[str, Any]] = []
    
    for raw_item in raw_items:
        try:
            item = json.loads(raw_item)
            message = item.get("message", "").lower()
            response = item.get("response", "").lower()
            
            # 在消息或回复中搜索关键词
            if keyword_lower in message or keyword_lower in response:
                matched_items.append(item)
        except Exception:
            continue
    
    # 按时间戳倒序排序
    matched_items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # 分页
    total = len(matched_items)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_items = matched_items[start:end]
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": paginated_items,
    }

