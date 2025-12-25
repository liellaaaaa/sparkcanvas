"""
DashScope Embedding 服务封装
"""
from __future__ import annotations

from typing import List, Optional
import dashscope
from http import HTTPStatus
from langchain_core.embeddings import Embeddings

from core.config import AppConfig
from core.logger import logger


class DashScopeEmbeddings(Embeddings):
    """
    DashScope Embedding 封装类，兼容 LangChain Embeddings 接口
    """
    
    def __init__(self, api_key: str, model: str = "text-embedding-v4"):
        """
        初始化 DashScope Embeddings
        
        Args:
            api_key: DashScope API Key
            model: Embedding 模型名称，默认 text-embedding-v4
        """
        self.api_key = api_key
        self.model = model
        dashscope.api_key = api_key
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量生成文档向量
        
        Args:
            texts: 文本列表
        
        Returns:
            向量列表
        """
        if not texts:
            return []
        
        try:
            # DashScope 支持批量处理
            resp = dashscope.TextEmbedding.call(
                model=self.model,
                input=texts,
            )
            
            if resp.status_code == HTTPStatus.OK:
                embeddings = []
                for item in resp.output.get('embeddings', []):
                    embeddings.append(item.get('embedding', []))
                return embeddings
            else:
                logger.error(f"DashScope Embedding 调用失败: {resp.message}")
                raise Exception(f"DashScope Embedding 调用失败: {resp.message}")
        except Exception as e:
            logger.error(f"DashScope Embedding 异常: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        生成查询向量
        
        Args:
            text: 查询文本
        
        Returns:
            向量
        """
        try:
            resp = dashscope.TextEmbedding.call(
                model=self.model,
                input=text,
            )
            
            if resp.status_code == HTTPStatus.OK:
                embeddings = resp.output.get('embeddings', [])
                if embeddings:
                    return embeddings[0].get('embedding', [])
                return []
            else:
                logger.error(f"DashScope Embedding 调用失败: {resp.message}")
                raise Exception(f"DashScope Embedding 调用失败: {resp.message}")
        except Exception as e:
            logger.error(f"DashScope Embedding 异常: {e}")
            raise


def get_embeddings(config: AppConfig) -> Optional[DashScopeEmbeddings]:
    """
    获取 DashScope Embeddings 实例（单例模式）
    
    Args:
        config: 应用配置对象
    
    Returns:
        DashScopeEmbeddings实例，如果配置不完整则返回None
    """
    if not config.dashscope_api_key or not config.dashscope_embedding_model:
        return None
    
    return DashScopeEmbeddings(
        api_key=config.dashscope_api_key,
        model=config.dashscope_embedding_model
    )

