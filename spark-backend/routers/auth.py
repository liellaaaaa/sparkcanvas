"""
认证路由
"""
from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import EmailStr
from typing import Annotated
from dependencies import get_mail, get_session, get_auth_handler
from fastapi_mail import FastMail, MessageSchema, MessageType
from models import AsyncSession
import string
import random
from aiosmtplib import SMTPResponseException
from repository.user_repo import EmailCodeRepository, UserRepository
from schemas import ResponseOut
from schemas.auth import RegisterIn, LoginIn, LoginOut
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["认证"])


@router.get("/code", response_model=ResponseOut)
async def get_email_code(
    email: Annotated[EmailStr, Query(...)],
    mail: FastMail = Depends(get_mail),
    session: AsyncSession = Depends(get_session),
):
    """
    发送邮箱验证码
    
    Args:
        email: 邮箱地址
        mail: FastMail 实例
        session: 数据库会话
    
    Returns:
        操作结果
    """
    # 1. 生成4位数字的验证码
    source = string.digits * 4
    code = "".join(random.sample(source, 4))
    
    # 2. 创建消息对象
    message = MessageSchema(
        subject="【SparkCanvas】注册验证码",
        recipients=[email],
        body=f"您的验证码为：{code}，十分钟内有效！",
        subtype=MessageType.plain
    )
    
    # 3. 发送邮件并存储验证码到数据库
    email_code_repo = EmailCodeRepository(session=session)
    try:
        await mail.send_message(message)
    except SMTPResponseException as e:
        if e.code == -1 and b"\\x00\\x00\\x00" in str(e).encode():
            print("⚠️ 忽略 QQ 邮箱 SMTP 关闭阶段的非标准响应（邮件已成功发送）")
        else:
            await session.rollback()  # 发生错误时回滚
            raise HTTPException(500, detail="邮件发送失败！")
    
    # 4. 存储验证码到数据库
    await email_code_repo.create(str(email), code)
    await session.commit()  # 提交事务
    
    return ResponseOut()


@router.post("/register", response_model=ResponseOut)
async def register(
    data: RegisterIn,
    session: AsyncSession = Depends(get_session),
    auth_handler = Depends(get_auth_handler),
):
    """
    用户注册
    
    Args:
        data: 注册数据
        session: 数据库会话
        auth_handler: JWT认证处理器
    
    Returns:
        操作结果
    """
    try:
        user_repo = UserRepository(session=session)
        email_code_repo = EmailCodeRepository(session=session)
        auth_service = AuthService(user_repo, email_code_repo, auth_handler)
        
        await auth_service.register(data)
        await session.commit()  # 统一提交事务
        return ResponseOut()
    except Exception as e:
        await session.rollback()  # 发生错误时回滚
        raise


@router.post('/login', response_model=LoginOut)
async def login(
    data: LoginIn,
    session: AsyncSession = Depends(get_session),
    auth_handler = Depends(get_auth_handler),
):
    """
    用户登录
    
    Args:
        data: 登录数据
        session: 数据库会话
        auth_handler: JWT认证处理器
    
    Returns:
        登录响应（包含用户信息和Token）
    """
    user_repo = UserRepository(session=session)
    email_code_repo = EmailCodeRepository(session=session)
    auth_service = AuthService(user_repo, email_code_repo, auth_handler)
    
    return await auth_service.login(data)

