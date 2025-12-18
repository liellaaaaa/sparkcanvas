"""
数据模型模块
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import MetaData


# 定义命名约定的Base类
class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        # ix: index，索引
        "ix": 'ix_%(column_0_label)s',
        # un：unique，唯一约束
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        # ck：Check，检查约束
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        # fk：Foreign Key，外键约束
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        # pk：Primary Key，主键约束
        "pk": "pk_%(table_name)s"
    })


def create_async_engine_from_config(mysql_url: str):
    """
    创建异步数据库引擎
    
    Args:
        mysql_url: MySQL 连接字符串
    
    Returns:
        AsyncEngine 对象
    """
    engine = create_async_engine(
        mysql_url,
        # 将输出所有执行SQL的日志（默认是关闭的）
        echo=True,
        # 连接池大小（默认是5个）
        pool_size=10,
        # 允许连接池最大的连接数（默认是10个）
        max_overflow=20,
        # 获得连接超时时间（默认是30s）
        pool_timeout=10,
        # 连接回收时间（默认是-1，代表永不回收）
        pool_recycle=3600,
        # 连接前是否预检查（默认为False）
        pool_pre_ping=True,
    )
    return engine


def create_session_factory(engine):
    """
    创建异步会话工厂
    
    Args:
        engine: AsyncEngine 对象
    
    Returns:
        sessionmaker 对象
    """
    return sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autoflush=True,
        expire_on_commit=False
    )


# 导入所有模型（确保在使用 Base.metadata.create_all 前导入）
from . import user

__all__ = ['Base', 'create_async_engine_from_config', 'create_session_factory', 'AsyncSession']

