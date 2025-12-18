"""
通用辅助函数
"""
from datetime import datetime
from typing import Any, Dict


def format_datetime(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间
    
    Args:
        dt: 日期时间对象
        format: 格式字符串
    
    Returns:
        格式化后的字符串
    """
    return dt.strftime(format)


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """
    脱敏处理敏感数据
    
    Args:
        data: 原始数据
        mask_char: 掩码字符
        visible_chars: 可见字符数（前后各显示几个字符）
    
    Returns:
        脱敏后的数据
    """
    if not data or len(data) <= visible_chars * 2:
        return mask_char * len(data) if data else ""
    return data[:visible_chars] + mask_char * (len(data) - visible_chars * 2) + data[-visible_chars:]


def paginate(items: list, page: int, page_size: int) -> Dict[str, Any]:
    """
    分页处理
    
    Args:
        items: 数据列表
        page: 页码（从1开始）
        page_size: 每页数量
    
    Returns:
        包含total、page、page_size、items的字典
    """
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_items = items[start:end]
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": paginated_items
    }

