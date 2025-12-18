"""
数据验证工具
"""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
    
    Returns:
        是否有效
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    验证密码强度
    
    要求：
    - 长度8-32位
    - 至少包含一个字母和一个数字
    
    Args:
        password: 密码
    
    Returns:
        (是否有效, 错误消息)
    """
    if len(password) < 8 or len(password) > 32:
        return False, "密码长度必须在8-32位之间"
    
    if not re.search(r'[a-zA-Z]', password):
        return False, "密码必须包含至少一个字母"
    
    if not re.search(r'\d', password):
        return False, "密码必须包含至少一个数字"
    
    return True, None

