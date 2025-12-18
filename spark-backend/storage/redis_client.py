from __future__ import annotations

from typing import Optional

try:
    import redis  # sync client
except Exception:  # pragma: no cover
    redis = None  # type: ignore


_client = None


def get_redis(url: str) -> Optional["redis.Redis"]:
    """
    获取 Redis 客户端（单例模式）
    
    Args:
        url: Redis连接URL
    
    Returns:
        Redis客户端实例，如果redis未安装或url为空则返回None
    """
    global _client
    if redis is None or not url:
        return None
    if _client is None:
        _client = redis.from_url(url, decode_responses=True)
    return _client

