from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .redis_client import get_redis
from ..core.config import AppConfig

SESSION_TTL_SECONDS = 30 * 60  # 30分钟


def _session_key(session_id: str) -> str:
    """生成会话Redis key"""
    return f"session:{session_id}"


def _now_iso() -> str:
    """返回UTC时间ISO格式字符串"""
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def create_session(cfg: AppConfig) -> Dict[str, str]:
    """
    创建新会话
    
    Args:
        cfg: 应用配置对象
    
    Returns:
        包含session_id、created_at、expires_at的字典
    """
    session_id = str(uuid.uuid4())
    r = get_redis(cfg.redis_url)
    created_at = _now_iso()
    expires_at = (datetime.utcnow() + timedelta(seconds=SESSION_TTL_SECONDS)).isoformat(timespec="seconds") + "Z"
    payload = {
        "session_id": session_id,
        "created_at": created_at,
        "expires_at": expires_at,
        "messages": [],
    }
    if r:
        r.setex(_session_key(session_id), SESSION_TTL_SECONDS, json.dumps(payload, ensure_ascii=False))
        try:
            # 维护全局会话索引，便于历史查询
            r.sadd("session:index", session_id)
        except Exception:
            pass
    return {"session_id": session_id, "created_at": created_at, "expires_at": expires_at}


def get_session(cfg: AppConfig, session_id: str) -> Optional[Dict[str, Any]]:
    """
    获取会话信息
    
    Args:
        cfg: 应用配置对象
        session_id: 会话ID
    
    Returns:
        会话信息字典，如果不存在则返回None
    """
    r = get_redis(cfg.redis_url)
    if not r:
        return None
    raw = r.get(_session_key(session_id))
    if not raw:
        return None
    return json.loads(raw)


def touch_session(cfg: AppConfig, session_id: str) -> None:
    """
    更新会话过期时间（续期）
    
    Args:
        cfg: 应用配置对象
        session_id: 会话ID
    """
    r = get_redis(cfg.redis_url)
    if not r:
        return
    raw = r.get(_session_key(session_id))
    if not raw:
        return
    data = json.loads(raw)
    r.setex(_session_key(session_id), SESSION_TTL_SECONDS, json.dumps(data, ensure_ascii=False))


def list_sessions(cfg: AppConfig, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    列出会话列表（分页）
    
    Args:
        cfg: 应用配置对象
        page: 页码
        page_size: 每页数量
    
    Returns:
        包含total、page、page_size、items的字典
    """
    r = get_redis(cfg.redis_url)
    if not r:
        return {"total": 0, "page": page, "page_size": page_size, "items": []}
    try:
        all_ids = list(r.smembers("session:index"))
    except Exception:
        all_ids = []
    total = len(all_ids)
    start = (page - 1) * page_size
    end = start + page_size
    ids = all_ids[start:end]
    items = []
    for sid in ids:
        raw = r.get(_session_key(sid))
        if not raw:
            continue
        data = json.loads(raw)
        messages = data.get("messages", [])
        # 如果有消息，使用最后一条消息的时间；否则使用创建时间
        last_message_time = messages[-1].get("timestamp") if messages else None
        items.append(
            {
                "session_id": sid,
                "created_at": data.get("created_at"),
                "updated_at": last_message_time or data.get("created_at"),
                "expires_at": data.get("expires_at"),
                "message_count": len(messages),
            }
        )
    return {"total": total, "page": page, "page_size": page_size, "items": items}


def append_message(cfg: AppConfig, session_id: str, role: str, content: str) -> None:
    """
    向会话添加消息
    
    Args:
        cfg: 应用配置对象
        session_id: 会话ID
        role: 消息角色（user/assistant）
        content: 消息内容
    """
    r = get_redis(cfg.redis_url)
    if not r:
        return
    raw = r.get(_session_key(session_id))
    if not raw:
        return
    data = json.loads(raw)
    data.setdefault("messages", []).append(
        {"role": role, "content": content, "timestamp": _now_iso()}
    )
    r.setex(_session_key(session_id), SESSION_TTL_SECONDS, json.dumps(data, ensure_ascii=False))

