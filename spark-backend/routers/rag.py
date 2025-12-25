"""
RAG 知识库路由

接口前缀：/api/v1/rag

说明：
- 所有接口默认需要登录（Bearer Token）
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import Annotated

from core.auth import AuthHandler
from dependencies import get_auth_handler
from schemas.rag import (
    RAGDocumentUploadOut,
    RAGDocumentListOut,
    RAGDeleteIn,
    RAGSearchIn,
    RAGSearchOut,
)
from services.rag_service import RAGService
from utils.response import APIResponse


router = APIRouter(prefix="/api/v1/rag", tags=["RAG知识库"])

# 认证依赖（统一使用 Access Token）
auth_handler: AuthHandler = get_auth_handler()
CurrentUserId = Annotated[int, Depends(auth_handler.auth_access_dependency)]


@router.post("/upload", response_model=APIResponse, summary="上传文档")
async def upload_document(
    current_user_id: CurrentUserId,
    file: UploadFile = File(...),
):
    """
    上传文档到RAG知识库，自动进行格式解析、智能分块、向量化并存储到Chroma。
    
    支持格式：PDF、Word、Txt
    """
    # 验证文件类型
    allowed_extensions = {'.pdf', '.txt', '.docx', '.doc'}
    file_extension = None
    if file.filename:
        file_extension = '.' + file.filename.split('.')[-1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型，仅支持: {', '.join(allowed_extensions)}"
        )
    
    # 读取文件内容
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"读取文件失败: {str(e)}")
    
    # 调用服务层上传文档
    service = RAGService()
    try:
        result = await service.upload_document(
            user_id=current_user_id,
            file_content=file_content,
            file_name=file.filename or "unknown",
        )
        return APIResponse(code=200, message="success", data=result)
    except Exception as e:
        from core.logger import logger
        import traceback
        error_detail = str(e)
        logger.error(f"[RAG API] 上传文档失败: {error_detail}")
        logger.error(f"[RAG API] 异常详情: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"上传文档失败: {error_detail}")


@router.delete("/delete", response_model=APIResponse, summary="删除文档")
async def delete_document(
    payload: RAGDeleteIn,
    current_user_id: CurrentUserId,
):
    """
    删除RAG知识库中的指定文档及其所有向量数据。
    """
    service = RAGService()
    try:
        await service.delete_document(
            user_id=current_user_id,
            document_id=payload.document_id,
        )
        return APIResponse(code=200, message="success", data=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文档失败: {str(e)}")


@router.get("/list", response_model=APIResponse, summary="文档列表")
async def list_documents(
    current_user_id: CurrentUserId,
    page: int = 1,
    page_size: int = 20,
):
    """
    查询当前用户上传的所有文档列表，支持分页。
    """
    page_size = min(page_size, 100)  # 限制最大100
    
    service = RAGService()
    try:
        result = await service.list_documents(
            user_id=current_user_id,
            page=page,
            page_size=page_size,
        )
        return APIResponse(code=200, message="success", data=result)
    except Exception as e:
        from core.logger import logger
        import traceback
        error_detail = str(e)
        logger.error(f"[RAG API] 查询文档列表失败: {error_detail}")
        logger.error(f"[RAG API] 异常详情: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"查询文档列表失败: {error_detail}")


@router.post("/search", response_model=APIResponse, summary="语义检索")
async def search_documents(
    payload: RAGSearchIn,
    current_user_id: CurrentUserId,
):
    """
    按关键词进行语义检索，返回相似度最高的文档片段。
    """
    service = RAGService()
    try:
        result = await service.search(
            user_id=current_user_id,
            query=payload.query,
            top_k=payload.top_k,
        )
        return APIResponse(code=200, message="success", data=result)
    except Exception as e:
        from core.logger import logger
        import traceback
        error_detail = str(e)
        logger.error(f"[RAG API] 检索失败: {error_detail}")
        logger.error(f"[RAG API] 异常详情: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"检索失败: {error_detail}")

