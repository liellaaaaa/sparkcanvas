"""
Prompt 管理服务
"""
from typing import Optional
from fastapi import HTTPException
from core.logger import logger
from repository.prompt_repo import PromptRepository
from schemas.prompt import (
    PromptCreateIn,
    PromptUpdateIn,
    PromptDeleteIn,
    PromptOut,
    PromptListOut,
)
from utils.response import APIResponse, success_response


class PromptService:
    """Prompt管理服务类"""

    def __init__(self, repo: PromptRepository):
        """
        初始化Prompt服务

        Args:
            repo: Prompt数据访问层
        """
        self.repo = repo

    async def create_prompt(
        self,
        user_id: int,
        data: PromptCreateIn,
    ) -> APIResponse:
        """
        创建Prompt业务逻辑

        Args:
            user_id: 用户ID
            data: Prompt创建数据

        Returns:
            APIResponse: 包含创建的Prompt信息

        Raises:
            HTTPException: 当数据验证失败或创建失败时抛出
        """
        # 验证数据
        if not data.name or not data.content:
            raise HTTPException(
                status_code=400,
                detail="name和content不能为空"
            )

        # 验证platform值合法性
        valid_platforms = ["xiaohongshu", "douyin", "通用"]
        if data.platform not in valid_platforms:
            raise HTTPException(
                status_code=400,
                detail=f"platform值必须为: {', '.join(valid_platforms)}"
            )

        try:
            # 创建Prompt
            prompt = await self.repo.create(user_id, data)
            logger.info(f"用户{user_id}创建Prompt: {prompt.id} - {prompt.name}")

            # 返回响应
            return success_response(PromptOut.model_validate(prompt))
        except Exception as e:
            logger.error(f"创建Prompt失败: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"创建Prompt失败: {str(e)}"
            )

    async def list_prompts(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        platform: Optional[str] = None,
        category: Optional[str] = None,
    ) -> APIResponse:
        """
        分页查询Prompt列表

        Args:
            user_id: 用户ID
            page: 页码（默认1）
            page_size: 每页数量（默认20，最大100）
            platform: 平台筛选（可选）
            category: 分类筛选（可选）

        Returns:
            APIResponse: 包含Prompt列表和分页信息
        """
        # 验证分页参数
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20
        if page_size > 100:
            page_size = 100

        try:
            # 查询列表
            items, total = await self.repo.get_by_user_id(
                user_id=user_id,
                page=page,
                page_size=page_size,
                platform=platform,
                category=category,
            )

            # 转换为输出格式
            prompt_list = [PromptOut.model_validate(item) for item in items]

            # 返回响应
            return success_response(
                PromptListOut(
                    total=total,
                    page=page,
                    page_size=page_size,
                    items=prompt_list,
                )
            )
        except Exception as e:
            logger.error(f"查询Prompt列表失败: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"查询Prompt列表失败: {str(e)}"
            )

    async def update_prompt(
        self,
        user_id: int,
        data: PromptUpdateIn,
    ) -> APIResponse:
        """
        更新Prompt业务逻辑

        Args:
            user_id: 用户ID
            data: Prompt更新数据

        Returns:
            APIResponse: 包含更新后的Prompt信息

        Raises:
            HTTPException: 当Prompt不存在、无权限或更新失败时抛出
        """
        # 校验Prompt存在性和所有权
        prompt = await self.repo.get_by_id(data.id, user_id)
        if not prompt:
            raise HTTPException(
                status_code=404,
                detail="Prompt不存在或无权限"
            )

        # 验证platform值合法性（如果提供）
        if data.platform is not None:
            valid_platforms = ["xiaohongshu", "douyin", "通用"]
            if data.platform not in valid_platforms:
                raise HTTPException(
                    status_code=400,
                    detail=f"platform值必须为: {', '.join(valid_platforms)}"
                )

        try:
            # 更新Prompt
            updated_prompt = await self.repo.update(data.id, user_id, data)

            if not updated_prompt:
                raise HTTPException(
                    status_code=404,
                    detail="Prompt不存在或无权限"
                )

            logger.info(f"用户{user_id}更新Prompt: {updated_prompt.id}")

            # 返回响应
            return success_response(PromptOut.model_validate(updated_prompt))
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"更新Prompt失败: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"更新Prompt失败: {str(e)}"
            )

    async def delete_prompt(
        self,
        user_id: int,
        data: PromptDeleteIn,
    ) -> APIResponse:
        """
        删除Prompt业务逻辑

        Args:
            user_id: 用户ID
            data: Prompt删除数据

        Returns:
            APIResponse: 删除成功响应

        Raises:
            HTTPException: 当Prompt不存在、无权限或删除失败时抛出
        """
        # 校验Prompt存在性和所有权
        prompt = await self.repo.get_by_id(data.id, user_id)
        if not prompt:
            raise HTTPException(
                status_code=404,
                detail="Prompt不存在或无权限"
            )

        try:
            # 删除Prompt
            success = await self.repo.delete(data.id, user_id)

            if not success:
                raise HTTPException(
                    status_code=404,
                    detail="Prompt不存在或无权限"
                )

            logger.info(f"用户{user_id}删除Prompt: {data.id}")

            # 返回响应
            return success_response(None)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"删除Prompt失败: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"删除Prompt失败: {str(e)}"
            )

    async def get_prompt_by_id(
        self,
        prompt_id: int,
        user_id: int,
    ) -> APIResponse:
        """
        根据ID获取Prompt（含权限校验）

        Args:
            prompt_id: Prompt ID
            user_id: 用户ID

        Returns:
            APIResponse: 包含Prompt详情

        Raises:
            HTTPException: 当Prompt不存在或无权限时抛出
        """
        # 校验Prompt存在性和所有权
        prompt = await self.repo.get_by_id(prompt_id, user_id)
        if not prompt:
            raise HTTPException(
                status_code=404,
                detail="Prompt不存在或无权限"
            )

        # 返回响应
        return success_response(PromptOut.model_validate(prompt))

