"""
Chroma 向量数据库客户端封装
"""
from typing import Optional
from pathlib import Path

try:
    from langchain_community.vectorstores import Chroma
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    Chroma = None  # type: ignore

from core.config import AppConfig
from core.logger import logger
from services.embedding_service import get_embeddings as get_dashscope_embeddings


_chroma_client: Optional[Chroma] = None
_embeddings = None


def get_chroma_client(config: AppConfig) -> Optional[Chroma]:
    """
    获取 Chroma 客户端（单例模式）
    
    Args:
        config: 应用配置对象
    
    Returns:
        Chroma客户端实例，如果Chroma未安装或配置不完整则返回None
    """
    global _chroma_client, _embeddings
    
    if not CHROMA_AVAILABLE:
        logger.warning("[Chroma] langchain_community未安装，Chroma功能不可用")
        return None
    
    if not config.dashscope_api_key or not config.dashscope_embedding_model:
        logger.warning(f"[Chroma] DashScope配置不完整: api_key={'已配置' if config.dashscope_api_key else '未配置'}, embedding_model={config.dashscope_embedding_model or '未配置'}")
        return None
    
    if _chroma_client is None:
        try:
            # 确保目录存在
            persist_dir = Path(config.chroma_persist_directory)
            persist_dir.mkdir(parents=True, exist_ok=True)
            
            # 初始化 DashScope Embeddings
            _embeddings = get_dashscope_embeddings(config)
            if _embeddings is None:
                logger.error("[Chroma] DashScope Embeddings初始化失败")
                return None
            
            # 初始化 Chroma
            _chroma_client = Chroma(
                persist_directory=str(persist_dir),
                embedding_function=_embeddings,
            )
            logger.info(f"[Chroma] 客户端初始化成功，持久化目录: {persist_dir}")
        except Exception as e:
            logger.error(f"[Chroma] 客户端初始化失败: {e}")
            import traceback
            logger.error(f"[Chroma] 初始化异常详情: {traceback.format_exc()}")
            return None
    
    return _chroma_client


def get_embeddings(config: AppConfig):
    """
    获取 Embeddings 实例
    
    Args:
        config: 应用配置对象
    
    Returns:
        DashScopeEmbeddings实例
    """
    return get_dashscope_embeddings(config)

