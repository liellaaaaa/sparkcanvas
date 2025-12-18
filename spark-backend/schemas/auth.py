"""
认证相关 Schema 定义
"""
from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Annotated

# 自定义类型别名
UsernameStr = Annotated[str, Field(min_length=3, max_length=20, description="用户名")]
PasswordStr = Annotated[str, Field(min_length=6, max_length=20, description="密码")]


class RegisterIn(BaseModel):
    """注册请求"""
    email: EmailStr
    username: UsernameStr
    password: PasswordStr
    confirm_password: PasswordStr
    code: Annotated[str, Field(min_length=4, max_length=4, description="邮箱验证码")]

    @model_validator(mode="after")
    def password_is_match(self):
        """验证两次密码是否一致"""
        if self.password != self.confirm_password:
            raise ValueError("两个密码不一致！")
        return self


class UserCreateSchema(BaseModel):
    """用户创建 Schema"""
    email: EmailStr
    username: UsernameStr
    password: PasswordStr


class LoginIn(BaseModel):
    """登录请求"""
    email: EmailStr
    password: PasswordStr


class UserSchema(BaseModel):
    """用户信息"""
    id: Annotated[int, Field(...)]
    email: EmailStr
    username: UsernameStr


class LoginOut(BaseModel):
    """登录响应"""
    user: UserSchema
    token: str

