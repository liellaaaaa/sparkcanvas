from loguru import logger
import sys


def setup_logger():
    """
    配置日志系统（使用 loguru）
    
    Returns:
        logger: 配置好的 logger 实例
    """
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        backtrace=False,
        diagnose=False,
        enqueue=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    return logger

