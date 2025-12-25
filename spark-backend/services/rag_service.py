"""
RAG 知识库服务（文档上传、向量检索）
"""
from __future__ import annotations

import uuid
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import json

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
)
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from core.config import AppConfig, load_config
from core.logger import logger
from storage.chroma_client import get_chroma_client
from schemas.rag import (
    RAGDocumentUploadOut,
    RAGDocumentItem,
    RAGDocumentListOut,
    RAGSearchResult,
    RAGSearchOut,
)


# 文档元数据存储（使用JSON文件，后续可迁移到MySQL）
METADATA_FILE = Path(__file__).parent.parent / "storage" / "rag_metadata.json"


def _load_metadata() -> Dict[str, Any]:
    """加载文档元数据"""
    if not METADATA_FILE.exists():
        return {}
    try:
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载元数据失败: {e}")
        return {}


def _save_metadata(metadata: Dict[str, Any]):
    """保存文档元数据"""
    METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存元数据失败: {e}")


class RAGService:
    """RAG知识库服务"""
    
    def __init__(self, config: Optional[AppConfig] = None):
        """
        初始化RAG服务
        
        Args:
            config: 应用配置对象，如果不提供则自动加载
        """
        self.config = config or load_config()
        self.chroma_client = get_chroma_client(self.config)
        if self.chroma_client is None:
            logger.warning("[RAG] Chroma客户端未初始化，部分功能可能不可用")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def _get_document_loader(self, file_path: Path, file_extension: str):
        """
        根据文件类型获取文档加载器
        
        Args:
            file_path: 文件路径
            file_extension: 文件扩展名
        
        Returns:
            文档加载器实例
        """
        file_extension = file_extension.lower()
        
        if file_extension == '.pdf':
            return PyPDFLoader(str(file_path))
        elif file_extension == '.txt':
            return TextLoader(str(file_path), encoding='utf-8')
        elif file_extension in ['.docx', '.doc']:
            return Docx2txtLoader(str(file_path))
        else:
            raise ValueError(f"不支持的文件类型: {file_extension}")
    
    async def upload_document(
        self,
        user_id: int,
        file_content: bytes,
        file_name: str,
    ) -> RAGDocumentUploadOut:
        """
        上传文档到RAG知识库
        
        Args:
            user_id: 用户ID
            file_content: 文件内容（字节）
            file_name: 文件名
        
        Returns:
            上传结果
        """
        if self.chroma_client is None:
            raise Exception("Chroma客户端未初始化，请检查DashScope配置")
        
        # 生成文档ID
        document_id = str(uuid.uuid4())
        
        # 保存临时文件
        file_extension = Path(file_name).suffix
        temp_dir = Path(self.config.chroma_persist_directory) / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_file = temp_dir / f"{document_id}{file_extension}"
        
        try:
            # 写入临时文件
            with open(temp_file, 'wb') as f:
                f.write(file_content)
            
            # 加载文档
            loader = self._get_document_loader(temp_file, file_extension)
            documents = loader.load()
            
            # 文本分块
            chunks = self.text_splitter.split_documents(documents)
            
            # 为每个chunk添加元数据
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    'document_id': document_id,
                    'user_id': user_id,
                    'file_name': file_name,
                    'chunk_index': i,
                })
            
            # 向量化并存储到Chroma
            self.chroma_client.add_documents(chunks)
            self.chroma_client.persist()
            
            # 保存文档元数据
            metadata = _load_metadata()
            if str(user_id) not in metadata:
                metadata[str(user_id)] = {}
            
            uploaded_at = datetime.utcnow().isoformat() + 'Z'
            metadata[str(user_id)][document_id] = {
                'document_id': document_id,
                'file_name': file_name,
                'file_size': len(file_content),
                'chunks_count': len(chunks),
                'uploaded_at': uploaded_at,
            }
            _save_metadata(metadata)
            
            logger.info(f"[RAG] 文档上传成功: {document_id}, 用户: {user_id}, 分块数: {len(chunks)}")
            
            return RAGDocumentUploadOut(
                document_id=document_id,
                file_name=file_name,
                file_size=len(file_content),
                chunks_count=len(chunks),
                uploaded_at=uploaded_at,
            )
        
        except Exception as e:
            logger.error(f"[RAG] 文档上传失败: {e}")
            raise
        finally:
            # 清理临时文件
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except:
                    pass
    
    async def delete_document(self, user_id: int, document_id: str) -> bool:
        """
        删除文档
        
        Args:
            user_id: 用户ID
            document_id: 文档ID
        
        Returns:
            是否删除成功
        """
        if self.chroma_client is None:
            raise Exception("Chroma客户端未初始化，请检查DashScope配置")
        
        try:
            # 从Chroma删除文档（通过metadata过滤）
            # 注意：Chroma的delete方法需要传入ids或filter
            # 这里我们需要先查询出所有相关的chunk IDs，然后删除
            
            # 获取所有文档
            all_docs = self.chroma_client.get()
            
            # 找到属于该文档的所有chunk IDs
            chunk_ids_to_delete = []
            if all_docs and 'ids' in all_docs and 'metadatas' in all_docs:
                for i, metadata in enumerate(all_docs.get('metadatas', [])):
                    if metadata.get('document_id') == document_id and metadata.get('user_id') == user_id:
                        chunk_ids_to_delete.append(all_docs['ids'][i])
            
            # 删除chunks
            if chunk_ids_to_delete:
                self.chroma_client.delete(ids=chunk_ids_to_delete)
                self.chroma_client.persist()
            
            # 从元数据中删除
            metadata = _load_metadata()
            if str(user_id) in metadata and document_id in metadata[str(user_id)]:
                del metadata[str(user_id)][document_id]
                _save_metadata(metadata)
            
            logger.info(f"文档删除成功: {document_id}, 用户: {user_id}")
            return True
        
        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            raise
    
    async def list_documents(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> RAGDocumentListOut:
        """
        查询文档列表
        
        Args:
            user_id: 用户ID
            page: 页码，默认1
            page_size: 每页数量，默认20，最大100
        
        Returns:
            文档列表
        """
        page_size = min(page_size, 100)
        
        try:
            # 从元数据中获取文档列表
            metadata = _load_metadata()
            user_docs = metadata.get(str(user_id), {})
            
            # 转换为列表并排序
            items = []
            for doc_id, doc_info in user_docs.items():
                items.append(RAGDocumentItem(
                    document_id=doc_id,
                    file_name=doc_info['file_name'],
                    file_size=doc_info['file_size'],
                    chunks_count=doc_info['chunks_count'],
                    uploaded_at=doc_info['uploaded_at'],
                ))
            
            # 按上传时间倒序排序
            items.sort(key=lambda x: x.uploaded_at, reverse=True)
            
            # 分页
            total = len(items)
            start = (page - 1) * page_size
            end = start + page_size
            paginated_items = items[start:end]
            
            logger.info(f"[RAG] 查询文档列表: user_id={user_id}, page={page}, page_size={page_size}, total={total}")
            
            return RAGDocumentListOut(
                total=total,
                page=page,
                page_size=page_size,
                items=paginated_items,
            )
        except Exception as e:
            logger.error(f"[RAG] 查询文档列表失败: {e}")
            raise
    
    async def search(
        self,
        user_id: int,
        query: str,
        top_k: int = 5,
    ) -> RAGSearchOut:
        """
        语义检索
        
        Args:
            user_id: 用户ID
            query: 查询文本
            top_k: 返回Top-K结果，默认5
        
        Returns:
            检索结果
        """
        if self.chroma_client is None:
            raise Exception("Chroma客户端未初始化，请检查DashScope配置")
        
        try:
            # 使用Chroma进行相似度检索
            # 注意：Chroma的filter参数在不同版本中可能有差异
            # 这里先尝试使用where参数（新版本），如果失败则使用filter参数（旧版本）
            # 如果都失败，则先检索再过滤
            results = []
            try:
                # 尝试使用新版本的where参数
                results = self.chroma_client.similarity_search_with_score(
                    query,
                    k=top_k * 2,  # 多检索一些，以便过滤后仍有足够结果
                    where={"user_id": user_id},
                )
            except:
                try:
                    # 尝试使用filter参数
                    results = self.chroma_client.similarity_search_with_score(
                        query,
                        k=top_k * 2,
                        filter={"user_id": user_id},
                    )
                except:
                    # 如果都失败，先检索再过滤
                    results = self.chroma_client.similarity_search_with_score(
                        query,
                        k=top_k * 2,
                    )
            
            # 转换为响应格式并过滤用户
            search_results = []
            for doc, score in results:
                # 只返回属于该用户的文档
                if doc.metadata.get('user_id') == user_id:
                    search_results.append(RAGSearchResult(
                        content=doc.page_content,
                        score=float(score),
                        metadata=doc.metadata,
                    ))
                    # 达到top_k数量后停止
                    if len(search_results) >= top_k:
                        break
            
            return RAGSearchOut(
                query=query,
                results=search_results,
            )
        
        except Exception as e:
            logger.error(f"[RAG] 检索失败: {e}")
            import traceback
            logger.error(f"[RAG] 检索异常详情: {traceback.format_exc()}")
            raise
