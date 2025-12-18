"""
Chroma 向量数据库客户端封装
"""
from typing import Optional
from pathlib import Path

try:
    from langchain_community.vectorstores import Chroma
    from langchain_openai import OpenAIEmbeddings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    Chroma = None  # type: ignore
    OpenAIEmbeddings = None  # type: ignore

from ..core.config import AppConfig


_chroma_client: Optional[Chroma] = None
_embeddings: Optional[OpenAIEmbeddings] = None


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
        return None
    
    if not config.openai_api_key or not config.openai_embedding_model:
        return None
    
    if _chroma_client is None:
        # 确保目录存在
        persist_dir = Path(config.chroma_persist_directory)
        persist_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化 Embeddings
        _embeddings = OpenAIEmbeddings(
            model=config.openai_embedding_model,
            openai_api_key=config.openai_api_key,
            openai_api_base=config.openai_base_url if config.openai_base_url else None,
        )
        
        # 初始化 Chroma
        _chroma_client = Chroma(
            persist_directory=str(persist_dir),
            embedding_function=_embeddings,
        )
    
    return _chroma_client


def get_embeddings(config: AppConfig) -> Optional[OpenAIEmbeddings]:
    """
    获取 Embeddings 实例
    
    Args:
        config: 应用配置对象
    
    Returns:
        OpenAIEmbeddings实例
    """
    global _embeddings
    
    if not CHROMA_AVAILABLE:
        return None
    
    if not config.openai_api_key or not config.openai_embedding_model:
        return None
    
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(
            model=config.openai_embedding_model,
            openai_api_key=config.openai_api_key,
            openai_api_base=config.openai_base_url if config.openai_base_url else None,
        )
    
    return _embeddings

