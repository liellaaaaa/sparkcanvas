"""
RAG 知识库相关 Schema 定义
"""
from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel, Field


class RAGDocumentUploadOut(BaseModel):
    """文档上传响应"""
    
    document_id: str = Field(..., description="文档ID")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    chunks_count: int = Field(..., description="分块数量")
    uploaded_at: str = Field(..., description="上传时间（ISO8601）")


class RAGDocumentItem(BaseModel):
    """文档列表项"""
    
    document_id: str = Field(..., description="文档ID")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    chunks_count: int = Field(..., description="分块数量")
    uploaded_at: str = Field(..., description="上传时间（ISO8601）")


class RAGDocumentListOut(BaseModel):
    """文档列表响应"""
    
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    items: List[RAGDocumentItem] = Field(..., description="文档列表")


class RAGDeleteIn(BaseModel):
    """删除文档请求"""
    
    document_id: str = Field(..., description="文档ID")


class RAGSearchIn(BaseModel):
    """RAG检索请求"""
    
    query: str = Field(..., description="查询文本")
    top_k: int = Field(default=5, description="返回Top-K结果，默认5")


class RAGSearchResult(BaseModel):
    """RAG检索结果项"""
    
    content: str = Field(..., description="文档内容")
    distance: float = Field(..., description="距离值（Chroma返回的原始距离，数值越小表示越相似）")
    metadata: dict = Field(default_factory=dict, description="元数据")


class RAGSearchOut(BaseModel):
    """RAG检索响应"""
    
    results: List[RAGSearchResult] = Field(..., description="检索结果")
    query: str = Field(..., description="查询文本")

