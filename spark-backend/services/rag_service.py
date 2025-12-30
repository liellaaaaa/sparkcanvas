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
    
    def _convert_distance_to_similarity(self, distances: List[float]) -> List[float]:
        """
        将Chroma返回的距离分数转换为相似度分数
        
        Chroma返回的是distances（距离），距离越小越相似。
        根据实际测试，Chroma返回的距离值通常在0.5-2.0之间。
        
        转换策略（结合绝对阈值和相对关系）：
        1. 使用反距离归一化：similarity = 1 / (1 + distance)
        2. 根据距离的绝对值设置相似度上限：
           - distance < 0.5: 相似度可达1.0（100%）
           - distance < 1.0: 相似度上限0.9（90%）
           - distance < 1.5: 相似度上限0.7（70%）
           - distance >= 1.5: 相似度上限0.5（50%）
        3. 在绝对阈值范围内，使用相对关系调整
        
        Args:
            distances: 距离分数列表（距离越小越相似）
        
        Returns:
            相似度分数列表（0.0-1.0，表示0%-100%，数值越大越相似）
        """
        if not distances:
            return []
        
        min_distance = min(distances)
        max_distance = max(distances)
        
        # 如果所有距离相同，根据距离绝对值返回相似度
        if max_distance == min_distance:
            distance = min_distance
            if distance < 0.5:
                return [1.0] * len(distances)
            elif distance < 1.0:
                return [0.9] * len(distances)
            elif distance < 1.5:
                return [0.7] * len(distances)
            else:
                return [0.5] * len(distances)
        
        # 根据距离绝对值计算相似度
        def get_similarity_from_distance(d: float) -> float:
            """
            根据距离绝对值计算相似度
            
            使用分段线性函数，让相似度更合理：
            - distance < 0.5: 相似度 0.9-1.0（非常相关）
            - distance < 1.0: 相似度 0.7-0.9（相关）
            - distance < 1.5: 相似度 0.5-0.7（一般相关）
            - distance >= 1.5: 相似度 0.0-0.5（不太相关）
            """
            if d < 0.5:
                # 距离很小，相似度很高
                return 0.9 + (0.5 - d) / 0.5 * 0.1  # 0.9-1.0
            elif d < 1.0:
                # 距离较小，相似度较高
                return 0.7 + (1.0 - d) / 0.5 * 0.2  # 0.7-0.9
            elif d < 1.5:
                # 距离中等，相似度中等
                return 0.5 + (1.5 - d) / 0.5 * 0.2  # 0.5-0.7
            else:
                # 距离较大，相似度较低
                # 使用反距离：similarity = 1 / (1 + distance)，然后缩放到0-0.5
                inv_sim = 1.0 / (1.0 + d)
                return inv_sim * 0.5  # 0.0-0.5
        
        # 计算每个距离的相似度
        similarity_scores = [get_similarity_from_distance(d) for d in distances]
        
        # 如果有多个结果，使用相对关系微调（但不超过绝对阈值）
        # 注意：相似度已经根据绝对阈值计算，这里不需要再次归一化
        # 直接返回即可，保持绝对阈值的限制
        
        # 确保相似度在[0, 1]范围内
        similarity_scores = [max(0.0, min(1.0, s)) for s in similarity_scores]
        
        return similarity_scores
    
    def _normalize_scores_relative(self, similarity_scores: List[float]) -> List[float]:
        """
        使用相对归一化方法，保留相似度的相对关系，同时适当拉开差距
        
        注意：相似度分数已经在_convert_distance_to_similarity中考虑了绝对阈值，
        这里只需要轻微调整相对关系，让相关结果的相似度更合理。
        
        策略：
        1. 如果最高分数 >= 0.6，说明有相关结果，使用min-max归一化拉开差距
        2. 如果最高分数 < 0.6，保持原始分数，但确保最低分数不会太低
        
        Args:
            similarity_scores: 相似度分数列表（已经是0-1范围，考虑了绝对阈值）
        
        Returns:
            归一化后的分数列表（0.0-1.0，表示0%-100%），保持相对关系
        """
        if not similarity_scores:
            return []
        
        max_score = max(similarity_scores)
        min_score = min(similarity_scores)
        
        # 如果所有分数相同，返回原始分数
        if max_score == min_score:
            return similarity_scores
        
        # 如果最高分数 >= 0.6，说明有相关结果，使用min-max归一化拉开差距
        if max_score >= 0.6:
            # 使用min-max归一化，将范围映射到[0.3, 1.0]
            # 这样最相似的结果接近1.0，最不相似的结果至少0.3
            normalized = [
                0.3 + ((s - min_score) / (max_score - min_score)) * 0.7
                for s in similarity_scores
            ]
            return normalized
        elif max_score >= 0.4:
            # 如果最高分数在0.4-0.6之间，轻微拉开差距
            # 将范围映射到[0.2, max_score * 1.2]，但不超过0.8
            normalized = [
                0.2 + ((s - min_score) / (max_score - min_score)) * min(max_score * 0.6, 0.6)
                for s in similarity_scores
            ]
            normalized = [min(s, 0.8) for s in normalized]
            return normalized
        else:
            # 如果最高分数 < 0.4，保持原始分数，但确保最低分数不会太低
            # 将范围映射到[0.15, max_score * 1.1]，但不超过0.6
            if max_score > min_score:
                normalized = [
                    0.15 + ((s - min_score) / (max_score - min_score)) * min(max_score * 0.45, 0.45)
                    for s in similarity_scores
                ]
                normalized = [min(s, 0.6) for s in normalized]
                return normalized
            else:
                return similarity_scores
    
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
            检索结果，score 字段为 Chroma 返回的原始距离值（距离越小越相似）
        """
        if self.chroma_client is None:
            raise Exception("Chroma客户端未初始化，请检查DashScope配置")

        try:
            # 使用Chroma进行相似度检索
            # 注意：Chroma返回的是distances（距离），距离越小越相似
            # Chroma的filter/where参数在不同版本中可能有差异，这里尝试多种方式
            results: List[Any] = []
            try:
                # 尝试使用新版本的 where 参数
                results = self.chroma_client.similarity_search_with_score(
                    query,
                    k=top_k * 2,  # 多检索一些，以便过滤后仍有足够结果
                    where={"user_id": user_id},
                )
            except Exception:
                try:
                    # 尝试使用旧版本的 filter 参数
                    results = self.chroma_client.similarity_search_with_score(
                        query,
                        k=top_k * 2,
                        filter={"user_id": user_id},
                    )
                except Exception:
                    # 如果都失败，先不带过滤检索，再在应用层按 user_id 过滤
                    results = self.chroma_client.similarity_search_with_score(
                        query,
                        k=top_k * 2,
                    )

            # 收集属于该用户的结果及其原始距离值
            candidate_results: List[tuple[Document, float]] = []
            raw_distances: List[float] = []
            for doc, raw_score in results:
                if doc.metadata.get("user_id") == user_id:
                    distance = float(raw_score)
                    candidate_results.append((doc, distance))
                    raw_distances.append(distance)

            if not candidate_results:
                logger.info(f"[RAG] 检索无结果: user_id={user_id}, query={query}")
                return RAGSearchOut(query=query, results=[])

            # 记录原始距离值，便于排查
            logger.info(
                f"[RAG] 检索原始距离分数 (前{min(top_k, len(raw_distances))}个): "
                f"{[round(d, 4) for d in raw_distances[:top_k]]}"
            )

            # 直接使用距离值，越小越相似，不做归一化
            search_results: List[RAGSearchResult] = []
            for doc, distance in candidate_results:
                search_results.append(
                    RAGSearchResult(
                        content=doc.page_content,
                        distance=float(distance),  # 距离值
                        metadata=doc.metadata,
                    )
                )

                if len(search_results) >= top_k:
                    break

            logger.info(
                f"[RAG] 检索完成: user_id={user_id}, query={query}, 返回{len(search_results)}条结果"
            )

            return RAGSearchOut(query=query, results=search_results)

        except Exception as e:
            logger.error(f"[RAG] 检索失败: {e}")
            import traceback
            logger.error(f"[RAG] 检索异常详情: {traceback.format_exc()}")
            raise
