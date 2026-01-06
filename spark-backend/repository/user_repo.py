# """
# 用户相关数据访问层
# """
# from models import AsyncSession
# from models.user import EmailCode, User
# from sqlalchemy import select, exists
# from datetime import datetime, timedelta
# from schemas.auth import UserCreateSchema


# class UserRepository:
#     """用户数据访问层"""
    
#     def __init__(self, session: AsyncSession):
#         self.session = session

#     async def get_by_email(self, email: str) -> User | None:
#         """
#         根据邮箱获取用户
        
#         Args:
#             email: 邮箱地址
        
#         Returns:
#             用户对象或None
#         """
#         # 只读查询不需要 begin()，直接查询即可
#         user = await self.session.scalar(select(User).where(User.email == email))
#         return user

#     async def email_is_exist(self, email: str) -> bool:
#         """
#         检查邮箱是否已存在
        
#         Args:
#             email: 邮箱地址
        
#         Returns:
#             是否存在
#         """
#         # 只读查询不需要 begin()，直接查询即可
#         stmt = select(exists().where(User.email == email))
#         return await self.session.scalar(stmt)

#     async def create(self, user_schema: UserCreateSchema) -> User:
#         """
#         创建用户
        
#         Args:
#             user_schema: 用户创建Schema
        
#         Returns:
#             创建的用户对象
#         """
#         async with self.session.begin():
#             user = User(**user_schema.model_dump())
#             self.session.add(user)
#             return user


# class EmailCodeRepository:
#     """邮箱验证码数据访问层"""
    
#     def __init__(self, session: AsyncSession):
#         self.session = session

#     async def create(self, email: str, code: str) -> EmailCode:
#         """
#         创建邮箱验证码
        
#         Args:
#             email: 邮箱地址
#             code: 验证码
        
#         Returns:
#             创建的验证码对象
#         """
#         async with self.session.begin():
#             email_code = EmailCode(email=email, code=code)
#             self.session.add(email_code)
#             return email_code

#     async def check_email_code(self, email: str, code: str) -> bool:
#         """
#         验证邮箱验证码是否正确
        
#         Args:
#             email: 邮箱地址
#             code: 验证码
        
#         Returns:
#             是否正确
#         """
#         # 只读查询不需要 begin()，直接查询即可
#         stmt = select(EmailCode).where(EmailCode.email == email, EmailCode.code == code)
#         email_code: EmailCode | None = await self.session.scalar(stmt)
#         if email_code is None:
#             return False
#         # 验证码有效期为10分钟
#         if (datetime.now() - email_code.created_time) > timedelta(minutes=10):
#             return False
#         return True
"""
用户相关数据访问层
"""
from models import AsyncSession
from models.user import EmailCode, User
from sqlalchemy import select, exists
from datetime import datetime, timedelta
from schemas.auth import UserCreateSchema


class UserRepository:
    """用户数据访问层"""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱地址
        
        Returns:
            用户对象或None
        """
        # 只读查询不需要 begin()，直接查询即可
        user = await self.session.scalar(select(User).where(User.email == email))
        return user

    async def email_is_exist(self, email: str) -> bool:
        """
        检查邮箱是否已存在
        
        Args:
            email: 邮箱地址
        
        Returns:
            是否存在
        """
        # 只读查询不需要 begin()，直接查询即可
        stmt = select(exists().where(User.email == email))
        return await self.session.scalar(stmt)

    async def create(self, user_schema: UserCreateSchema) -> User:
        """
        创建用户
        
        Args:
            user_schema: 用户创建Schema
        
        Returns:
            创建的用户对象
        """
        # 直接添加对象，事务由路由层统一管理
        user = User(**user_schema.model_dump())
        self.session.add(user)
        # 刷新以获取生成的ID
        await self.session.flush()
        return user


class EmailCodeRepository:
    """邮箱验证码数据访问层"""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, email: str, code: str) -> EmailCode:
        """
        创建邮箱验证码
        
        Args:
            email: 邮箱地址
            code: 验证码
        
        Returns:
            创建的验证码对象
        """
        # 直接添加对象，事务由路由层统一管理
        email_code = EmailCode(email=email, code=code)
        self.session.add(email_code)
        # 刷新以获取生成的ID
        await self.session.flush()
        return email_code

    async def check_email_code(self, email: str, code: str) -> bool:
        """
        验证邮箱验证码是否正确
        
        Args:
            email: 邮箱地址
            code: 验证码
        
        Returns:
            是否正确
        """
        # 只读查询不需要 begin()，直接查询即可
        stmt = select(EmailCode).where(EmailCode.email == email, EmailCode.code == code)
        email_code: EmailCode | None = await self.session.scalar(stmt)
        if email_code is None:
            return False
        # 验证码有效期为10分钟
        if (datetime.now() - email_code.created_time) > timedelta(minutes=10):
            return False
        return True



