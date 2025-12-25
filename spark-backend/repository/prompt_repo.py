"""
Prompt相关数据访问层
"""
from typing import Optional, Tuple
from models import AsyncSession
from models.prompt import Prompt
from sqlalchemy import select, func
from schemas.prompt import PromptCreateIn, PromptUpdateIn


class PromptRepository:
    """Prompt数据访问层"""
    
    def __init__(self, session: AsyncSession):
        """
        初始化Prompt数据访问层
        
        Args:
            session: 数据库会话
        """
        self.session = session
    
    async def create(self, user_id: int, data: PromptCreateIn) -> Prompt:
        """
        创建Prompt
        
        Args:
            user_id: 用户ID
            data: Prompt创建数据
            
        Returns:
            创建的Prompt对象
        """
        async with self.session.begin():
            prompt = Prompt(
                user_id=user_id,
                **data.model_dump()
            )
            self.session.add(prompt)
            await self.session.flush()
            return prompt
    
    async def get_by_id(self, prompt_id: int, user_id: int) -> Optional[Prompt]:
        """
        根据ID获取Prompt（包含用户ID校验）
        
        Args:
            prompt_id: Prompt ID
            user_id: 用户ID
            
        Returns:
            Prompt对象或None
        """
        async with self.session.begin():
            stmt = select(Prompt).where(
                Prompt.id == prompt_id,
                Prompt.user_id == user_id
            )
            return await self.session.scalar(stmt)
    
    async def get_by_user_id(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        platform: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Tuple[list[Prompt], int]:
        """
        根据用户ID分页查询Prompt列表（支持筛选）
        
        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
            platform: 平台筛选（可选）
            category: 分类筛选（可选）
            
        Returns:
            (Prompt列表, 总数量)
        """
        async with self.session.begin():
            # 构建基础查询
            stmt = select(Prompt).where(Prompt.user_id == user_id)
            
            # 添加筛选条件
            if platform:
                stmt = stmt.where(Prompt.platform == platform)
            if category:
                stmt = stmt.where(Prompt.category == category)
            
            # 查询总数
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total = await self.session.scalar(count_stmt) or 0
            
            # 分页查询
            offset = (page - 1) * page_size
            stmt = stmt.order_by(Prompt.created_at.desc()).offset(offset).limit(page_size)
            items = (await self.session.scalars(stmt)).all()
            
            return list(items), total
    
    async def update(
        self,
        prompt_id: int,
        user_id: int,
        data: PromptUpdateIn,
    ) -> Optional[Prompt]:
        """
        更新Prompt
        
        Args:
            prompt_id: Prompt ID
            user_id: 用户ID
            data: Prompt更新数据
            
        Returns:
            更新后的Prompt对象或None
        """
        async with self.session.begin():
            stmt = select(Prompt).where(
                Prompt.id == prompt_id,
                Prompt.user_id == user_id
            )
            prompt = await self.session.scalar(stmt)
            
            if not prompt:
                return None
            
            # 更新字段（只更新提供的字段）
            update_data = data.model_dump(exclude_unset=True, exclude={'id'})
            for key, value in update_data.items():
                setattr(prompt, key, value)
            
            await self.session.flush()
            return prompt
    
    async def delete(self, prompt_id: int, user_id: int) -> bool:
        """
        删除Prompt
        
        Args:
            prompt_id: Prompt ID
            user_id: 用户ID
            
        Returns:
            是否删除成功
        """
        async with self.session.begin():
            stmt = select(Prompt).where(
                Prompt.id == prompt_id,
                Prompt.user_id == user_id
            )
            prompt = await self.session.scalar(stmt)
            
            if not prompt:
                return False
            
            await self.session.delete(prompt)
            return True
    
    async def check_ownership(self, prompt_id: int, user_id: int) -> bool:
        """
        检查Prompt是否属于指定用户
        
        Args:
            prompt_id: Prompt ID
            user_id: 用户ID
            
        Returns:
            是否属于该用户
        """
        async with self.session.begin():
            stmt = select(Prompt).where(
                Prompt.id == prompt_id,
                Prompt.user_id == user_id
            )
            result = await self.session.scalar(stmt)
            return result is not None

