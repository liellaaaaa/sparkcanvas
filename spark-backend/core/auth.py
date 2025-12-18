"""
JWT 认证处理模块
"""
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime, timedelta
from enum import Enum
from threading import Lock
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from .config import AppConfig


class SingletonMeta(type):
    """
    线程安全的单例模式实现
    """
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class TokenTypeEnum(Enum):
    """Token类型枚举"""
    ACCESS_TOKEN = 1
    REFRESH_TOKEN = 2


class AuthHandler(metaclass=SingletonMeta):
    """JWT认证处理器"""
    security = HTTPBearer()
    # Authorization: Bearer {token}

    def __init__(self, config: AppConfig):
        self.secret = config.jwt_secret_key
        self.access_token_expires = timedelta(hours=config.jwt_access_token_expires_hours)
        self.refresh_token_expires = timedelta(days=config.jwt_refresh_token_expires_days)

    def _encode_token(self, user_id: int, token_type: TokenTypeEnum):
        """
        编码Token
        
        Args:
            user_id: 用户ID
            token_type: Token类型
        
        Returns:
            JWT token字符串
        """
        payload = dict(
            iss=user_id,
            sub=str(token_type.value)
        )
        to_encode = payload.copy()
        if token_type == TokenTypeEnum.ACCESS_TOKEN:
            exp = datetime.utcnow() + self.access_token_expires
        else:
            exp = datetime.utcnow() + self.refresh_token_expires
        to_encode.update({"exp": int(exp.timestamp())})
        return jwt.encode(to_encode, self.secret, algorithm='HS256')

    def encode_login_token(self, user_id: int):
        """
        生成登录Token（包含access_token和refresh_token）
        
        Args:
            user_id: 用户ID
        
        Returns:
            包含access_token和refresh_token的字典
        """
        access_token = self._encode_token(user_id, TokenTypeEnum.ACCESS_TOKEN)
        refresh_token = self._encode_token(user_id, TokenTypeEnum.REFRESH_TOKEN)
        login_token = dict(
            access_token=f"{access_token}",
            refresh_token=f"{refresh_token}"
        )
        return login_token

    def encode_update_token(self, user_id: int):
        """
        生成更新Token（仅access_token）
        
        Args:
            user_id: 用户ID
        
        Returns:
            包含access_token的字典
        """
        access_token = self._encode_token(user_id, TokenTypeEnum.ACCESS_TOKEN)
        update_token = dict(
            access_token=f"{access_token}"
        )
        return update_token

    def decode_access_token(self, token: str):
        """
        解码Access Token
        ACCESS TOKEN：不可用（过期，或有问题），都用403错误
        
        Args:
            token: JWT token字符串
        
        Returns:
            用户ID
        
        Raises:
            HTTPException: Token无效或过期
        """
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            if payload['sub'] != str(TokenTypeEnum.ACCESS_TOKEN.value):
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Token类型错误！')
            return payload['iss']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Access Token已过期！')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Access Token不可用！')

    def decode_refresh_token(self, token: str):
        """
        解码Refresh Token
        REFRESH TOKEN：不可用（过期，或有问题），都用401错误
        
        Args:
            token: JWT token字符串
        
        Returns:
            用户ID
        
        Raises:
            HTTPException: Token无效或过期
        """
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            if payload['sub'] != str(TokenTypeEnum.REFRESH_TOKEN.value):
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Token类型错误！')
            return payload['iss']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Refresh Token已过期！')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Refresh Token不可用！')

    def auth_access_dependency(self, auth: HTTPAuthorizationCredentials = Security(security)):
        """
        FastAPI依赖注入：验证Access Token
        
        Args:
            auth: HTTP授权凭证
        
        Returns:
            用户ID
        """
        return self.decode_access_token(auth.credentials)

    def auth_refresh_dependency(self, auth: HTTPAuthorizationCredentials = Security(security)):
        """
        FastAPI依赖注入：验证Refresh Token
        
        Args:
            auth: HTTP授权凭证
        
        Returns:
            用户ID
        """
        return self.decode_refresh_token(auth.credentials)

