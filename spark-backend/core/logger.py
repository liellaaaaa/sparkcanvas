"""
日志配置模块
"""
from loguru import logger
import sys

# 配置日志格式
logger.remove()  # 移除默认的处理器
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# 添加文件日志
logger.add(
    "logs/sparkcanvas_{time:YYYY-MM-DD}.log",
    rotation="00:00",  # 每天午夜轮转
    retention="30 days",  # 保留30天
    level="DEBUG",
    encoding="utf-8"
)

__all__ = ['logger']
