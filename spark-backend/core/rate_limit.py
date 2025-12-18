from __future__ import annotations

import time
from typing import Optional, Tuple

from .config import AppConfig

# 延迟导入，避免循环依赖
def _get_redis(url: str):
    """延迟导入Redis客户端"""
    from ..storage.redis_client import get_redis
    return get_redis(url)

# 固定窗口限流配置
# 开发环境建议值：IP和会话限制提高到1000/小时，便于测试
IP_LIMIT_PER_HOUR = 1000
SESSION_LIMIT_PER_HOUR = 1000
GLOBAL_LIMIT_PER_MIN = 10000


def _incr_with_ttl(key: str, ttl_seconds: int, cfg: AppConfig) -> int:
    """
    递增计数器并设置过期时间
    
    Args:
        key: Redis key
        ttl_seconds: 过期时间（秒）
        cfg: 应用配置
    
    Returns:
        递增后的值
    """
    r = _get_redis(cfg.redis_url)
    if not r:
        return 0
    val = r.incr(key)
    if val == 1:
        r.expire(key, ttl_seconds)
    return int(val)


def check_rate_limit(cfg: AppConfig, ip: str, session_id: Optional[str] = None) -> Tuple[bool, Optional[int]]:
    """
    检查限流
    
    Args:
        cfg: 应用配置
        ip: 客户端IP地址
        session_id: 会话ID（可选）
    
    Returns:
        (是否允许, 重试秒数): 当不允许时，给出建议的 retry-after 秒数
    """
    now = int(time.time())
    
    # 全局每分钟限流
    minute_bucket = now // 60
    g_key = f"rl:global:{minute_bucket}"
    g_val = _incr_with_ttl(g_key, 60, cfg)
    if g_val and g_val > GLOBAL_LIMIT_PER_MIN:
        return False, 60 - (now % 60)

    # IP每小时限流
    hour_bucket = now // 3600
    ip_key = f"rl:ip:{ip}:{hour_bucket}"
    ip_val = _incr_with_ttl(ip_key, 3600, cfg)
    if ip_val and ip_val > IP_LIMIT_PER_HOUR:
        return False, 3600 - (now % 3600)

    # 会话每小时限流
    if session_id:
        s_key = f"rl:sess:{session_id}:{hour_bucket}"
        s_val = _incr_with_ttl(s_key, 3600, cfg)
        if s_val and s_val > SESSION_LIMIT_PER_HOUR:
            return False, 3600 - (now % 3600)

    return True, None

