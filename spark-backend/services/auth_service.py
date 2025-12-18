"""
认证服务
"""
from fastapi import HTTPException
from core.auth import AuthHandler
from repository.user_repo import UserRepository, EmailCodeRepository
from schemas.auth import RegisterIn, LoginIn, UserCreateSchema, LoginOut, UserSchema
from models.user import User


class AuthService:
    """认证服务类"""
    
    def __init__(self, user_repo: UserRepository, email_code_repo: EmailCodeRepository, auth_handler: AuthHandler):
        """
        初始化认证服务
        
        Args:
            user_repo: 用户数据访问层
            email_code_repo: 邮箱验证码数据访问层
            auth_handler: JWT认证处理器
        """
        self.user_repo = user_repo
        self.email_code_repo = email_code_repo
        self.auth_handler = auth_handler
    
    async def register(self, request: RegisterIn) -> None:
        """
        用户注册
        
        Args:
            request: 注册请求数据
        
        Raises:
            HTTPException: 邮箱已存在或验证码错误
        """
        # 1. 判断邮箱是否存在
        email_exist = await self.user_repo.email_is_exist(email=str(request.email))
        if email_exist:
            raise HTTPException(400, detail="该邮箱已经存在！")
        
        # 2. 校验验证码是否正确
        email_code_match = await self.email_code_repo.check_email_code(
            email=str(request.email), 
            code=str(request.code)
        )
        if not email_code_match:
            raise HTTPException(400, detail='邮箱或验证码错误！')
        
        # 3. 创建用户
        try:
            await self.user_repo.create(
                UserCreateSchema(
                    email=str(request.email),
                    password=request.password,
                    username=request.username
                )
            )
        except Exception as e:
            raise HTTPException(500, detail=f"注册失败：{str(e)}")
    
    async def login(self, request: LoginIn) -> LoginOut:
        """
        用户登录
        
        Args:
            request: 登录请求数据
        
        Returns:
            登录响应数据（包含用户信息和Token）
        
        Raises:
            HTTPException: 用户不存在或密码错误
        """
        # 1. 根据邮箱查找用户
        user: User | None = await self.user_repo.get_by_email(str(request.email))
        if not user:
            raise HTTPException(400, detail="该用户不存在！")
        
        # 2. 验证密码
        if not user.check_password(request.password):
            raise HTTPException(400, detail="邮箱或密码错误！")
        
        # 3. 生成JWT Token
        tokens = self.auth_handler.encode_login_token(user.id)
        
        # 4. 返回登录响应
        return LoginOut(
            user=UserSchema(
                id=user.id,
                email=user.email,
                username=user.username
            ),
            token=tokens['access_token']
        )
