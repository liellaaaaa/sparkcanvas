"""
FastAPI 依赖注入
"""
from pathlib import Path
from core.mail import create_mail_instance
from core.config import load_config
from core.auth import AuthHandler
from fastapi_mail import FastMail
from models import AsyncSession, create_async_engine_from_config, create_session_factory

# 加载全局配置
config = load_config()

# 验证 MySQL URL 配置
if not config.mysql_url:
    raise ValueError(
        "MySQL URL 未配置！请检查配置文件中的 mysql.url 设置。\n"
        f"配置文件路径应为: {Path(__file__).resolve().parents[0] / 'config' / 'config.yaml'}"
    )

# 创建数据库引擎和会话工厂
engine = create_async_engine_from_config(config.mysql_url)
AsyncSessionFactory = create_session_factory(engine)

# 创建全局 AuthHandler 实例
auth_handler = AuthHandler(config)


async def get_session() -> AsyncSession:
    """
    获取数据库会话
    
    Yields:
        AsyncSession: 异步数据库会话
    """
    session = AsyncSessionFactory()
    try:
        yield session
    finally:
        await session.close()


async def get_mail() -> FastMail:
    """
    获取邮件客户端
    
    Returns:
        FastMail: FastMail 实例
    """
    return create_mail_instance(config)


def get_auth_handler() -> AuthHandler:
    """
    获取认证处理器
    
    Returns:
        AuthHandler: JWT认证处理器
    """
    return auth_handler

