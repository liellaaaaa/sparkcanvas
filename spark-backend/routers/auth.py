# """
# 认证路由
# """
# from fastapi import APIRouter, Query, Depends, HTTPException
# from pydantic import EmailStr
# from typing import Annotated
# from dependencies import get_mail, get_session, get_auth_handler
# from fastapi_mail import FastMail, MessageSchema, MessageType
# from models import AsyncSession
# import string
# import random
# from aiosmtplib import SMTPResponseException
# from repository.user_repo import EmailCodeRepository, UserRepository
# from schemas import ResponseOut
# from schemas.auth import RegisterIn, LoginIn, LoginOut
# from services.auth_service import AuthService

# router = APIRouter(prefix="/auth", tags=["认证"])


# @router.get("/code", response_model=ResponseOut)
# async def get_email_code(
#     email: Annotated[EmailStr, Query(...)],
#     mail: FastMail = Depends(get_mail),
#     session: AsyncSession = Depends(get_session),
# ):
#     """
#     发送邮箱验证码
    
#     Args:
#         email: 邮箱地址
#         mail: FastMail 实例
#         session: 数据库会话
    
#     Returns:
#         操作结果
#     """
#     # 1. 生成4位数字的验证码
#     source = string.digits * 4
#     code = "".join(random.sample(source, 4))
    
#     # 2. 创建消息对象
#     message = MessageSchema(
#         subject="【SparkCanvas】注册验证码",
#         recipients=[email],
#         body=f"您的验证码为：{code}，十分钟内有效！",
#         subtype=MessageType.plain
#     )
    
#     # 3. 发送邮件
#     try:
#         await mail.send_message(message)
#     except SMTPResponseException as e:
#         if e.code == -1 and b"\\x00\\x00\\x00" in str(e).encode():
#             print("⚠️ 忽略 QQ 邮箱 SMTP 关闭阶段的非标准响应（邮件已成功发送）")
#             # 将邮箱和验证码存储到数据库中
#             email_code_repo = EmailCodeRepository(session=session)
#             await email_code_repo.create(str(email), code)
#         else:
#             raise HTTPException(500, detail="邮件发送失败！")
    
#     # 4. 存储验证码到数据库
#     email_code_repo = EmailCodeRepository(session=session)
#     await email_code_repo.create(str(email), code)
    
#     return ResponseOut()


# @router.post("/register", response_model=ResponseOut)
# async def register(
#     data: RegisterIn,
#     session: AsyncSession = Depends(get_session),
#     auth_handler = Depends(get_auth_handler),
# ):
#     """
#     用户注册
    
#     Args:
#         data: 注册数据
#         session: 数据库会话
#         auth_handler: JWT认证处理器
    
#     Returns:
#         操作结果
#     """
#     user_repo = UserRepository(session=session)
#     email_code_repo = EmailCodeRepository(session=session)
#     auth_service = AuthService(user_repo, email_code_repo, auth_handler)
    
#     await auth_service.register(data)
#     return ResponseOut()


# @router.post('/login', response_model=LoginOut)
# async def login(
#     data: LoginIn,
#     session: AsyncSession = Depends(get_session),
#     auth_handler = Depends(get_auth_handler),
# ):
#     """
#     用户登录
    
#     Args:
#         data: 登录数据
#         session: 数据库会话
#         auth_handler: JWT认证处理器
    
#     Returns:
#         登录响应（包含用户信息和Token）
#     """
#     user_repo = UserRepository(session=session)
#     email_code_repo = EmailCodeRepository(session=session)
#     auth_service = AuthService(user_repo, email_code_repo, auth_handler)
    
#     return await auth_service.login(data)


"""
认证路由
"""
from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import EmailStr
from typing import Annotated
from dependencies import get_mail, get_session, get_auth_handler
from fastapi_mail import FastMail, MessageSchema, MessageType
from models import AsyncSession
from models.user import EmailCode
from sqlalchemy import select, desc
from datetime import datetime, timedelta
import string
import random
from aiosmtplib import SMTPResponseException
from repository.user_repo import EmailCodeRepository, UserRepository
from schemas import ResponseOut
from schemas.auth import RegisterIn, LoginIn, LoginOut
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["认证"])


@router.get("/debug/codes")
async def debug_email_codes(
    email: Annotated[str, Query(...)],
    session: AsyncSession = Depends(get_session),
):
    """
    调试接口：查看指定邮箱的所有验证码记录
    
    注意：此接口仅用于调试，生产环境应删除或添加权限控制
    
    使用方法：
    GET /auth/debug/codes?email=1337706441@qq.com
    """
    # 查询该邮箱的所有验证码记录
    stmt = (
        select(EmailCode)
        .where(EmailCode.email == email)
        .order_by(desc(EmailCode.created_time))
        .limit(10)
    )
    codes = await session.scalars(stmt)
    
    result = {
        "email": email,
        "count": 0,
        "codes": [],
        "current_time": datetime.now().isoformat()
    }
    
    for code_obj in codes:
        now = datetime.now()
        time_diff = now - code_obj.created_time
        is_valid = time_diff <= timedelta(minutes=10)
        
        result["codes"].append({
            "id": code_obj.id,
            "code": code_obj.code,
            "code_repr": repr(code_obj.code),  # 显示原始字符串，包括特殊字符
            "code_length": len(code_obj.code),
            "created_time": code_obj.created_time.isoformat(),
            "time_diff_seconds": time_diff.total_seconds(),
            "time_diff_minutes": round(time_diff.total_seconds() / 60, 2),
            "is_valid": is_valid,
            "is_expired": not is_valid
        })
        result["count"] += 1
    
    return result


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
    code = code.strip()  # 确保验证码格式正确
    
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
            # 忽略 QQ 邮箱 SMTP 关闭阶段的非标准响应
            pass
        else:
            await session.rollback()
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


