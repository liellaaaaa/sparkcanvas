"""
用户相关数据模型
"""
from . import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, DateTime
from pwdlib import PasswordHash
from datetime import datetime

# pwdlib
# pip install "pwdlib[argon2]"

password_hash = PasswordHash.recommended()


class User(Base):
    """用户模型"""
    __tablename__ = 'user'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    _password: Mapped[str] = mapped_column(String(200), nullable=False)

    def __init__(self, *args, **kwargs):
        password = kwargs.pop('password', None)
        super().__init__(*args, **kwargs)
        if password:
            self.password = password

    @property
    def password(self):
        """获取密码（返回加密后的密码）"""
        return self._password

    @password.setter
    def password(self, raw_password: str):
        """设置密码（自动加密）"""
        self._password = password_hash.hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """
        验证密码
        
        Args:
            raw_password: 原始密码
        
        Returns:
            密码是否正确
        """
        return password_hash.verify(raw_password, self.password)


class EmailCode(Base):
    """邮箱验证码模型"""
    __tablename__ = 'email_code'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    created_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

