# SparkCanvas 快速启动指南

## 🎉 开发完成情况

✅ **已完成：邮箱验证码发送、注册、登录模块**

已完成以下功能：
- 邮箱验证码发送
- 用户注册（带验证码验证）
- 用户登录（JWT Token）
- 密码加密存储（Argon2）

## 📋 环境准备

### 1. 安装 Python 依赖

```bash
cd spark-backend
pip install -r requirements.txt
```

### 2. 配置环境

#### 方式一：使用 .env 文件（推荐）

在 `config` 目录创建 `.env` 文件：

```env
# 数据库配置（必需）
MYSQL_URL=mysql+aiomysql://root:1234@127.0.0.1:3306/sparkcanvas?charset=utf8mb4

# JWT 配置（必需）
JWT_SECRET_KEY=sparkcanvas-secret-key-2024

# 邮件配置（已配置授权码，可直接使用）
MAIL_USERNAME=487935272@qq.com
MAIL_PASSWORD=uixvdbysupnmbjha
MAIL_FROM=487935272@qq.com
MAIL_PORT=587
MAIL_SERVER=smtp.qq.com
MAIL_FROM_NAME=SparkCanvas
```

#### 方式二：修改 config.yaml

编辑 `config/config.yaml` 文件，修改相应配置项。

### 3. 创建数据库

```sql
CREATE DATABASE sparkcanvas DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 初始化数据库表

```bash
cd spark-backend
python init_db.py
```

成功后会输出：✅ 数据库表创建成功！

## 🚀 启动应用

```bash
cd spark-backend
python main.py
```

或使用 uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API 测试

### 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 使用 HTTP 文件测试

打开 `spark-backend/test_auth.http` 文件，使用 VS Code 的 REST Client 插件测试 API。

### 测试流程

#### 1. 发送验证码

```bash
curl "http://localhost:8000/auth/code?email=test@example.com"
```

响应：
```json
{
  "result": "success"
}
```

验证码会发送到指定邮箱（由于使用的是 zhiliao-ainame 的配置，实际会从 487935272@qq.com 发送）。

#### 2. 注册用户

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "test123456",
    "confirm_password": "test123456",
    "code": "1234"
  }'
```

响应：
```json
{
  "result": "success"
}
```

#### 3. 用户登录

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456"
  }'
```

响应：
```json
{
  "user": {
    "id": 1,
    "email": "test@example.com",
    "username": "testuser"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## 🔧 技术栈

### 后端框架
- **FastAPI**: 现代高性能 Web 框架
- **SQLAlchemy 2.0**: 异步 ORM
- **aiomysql**: 异步 MySQL 驱动
- **Pydantic**: 数据验证

### 认证与安全
- **PyJWT**: JWT Token 生成和验证
- **pwdlib[argon2]**: 密码加密（Argon2 算法）

### 邮件服务
- **fastapi-mail**: 邮件发送
- **aiosmtplib**: 异步 SMTP 客户端

## 📁 项目结构

```
spark-backend/
├── core/                    # 核心模块
│   ├── auth.py             # JWT 认证（AuthHandler）
│   ├── mail.py             # 邮件发送（create_mail_instance）
│   ├── config.py           # 配置管理（load_config）
│   └── logger.py           # 日志配置
├── models/                  # 数据模型（SQLAlchemy）
│   ├── __init__.py         # Base, 数据库引擎
│   └── user.py             # User, EmailCode 模型
├── schemas/                 # Pydantic 模式
│   ├── __init__.py
│   ├── common.py           # ResponseOut
│   └── auth.py             # RegisterIn, LoginIn, LoginOut, UserSchema
├── repository/             # 数据访问层
│   └── user_repo.py        # UserRepository, EmailCodeRepository
├── services/               # 业务服务层
│   └── auth_service.py     # AuthService
├── routers/                # 路由层
│   └── auth.py             # 认证路由（/auth/code, /auth/register, /auth/login）
├── main.py                 # 应用入口
├── dependencies.py         # 依赖注入（get_session, get_mail, get_auth_handler）
└── init_db.py             # 数据库初始化脚本
```

## 🎯 核心功能说明

### 1. 邮箱验证码

- **端点**: `GET /auth/code?email=xxx`
- **功能**: 生成4位数字验证码，发送到指定邮箱
- **有效期**: 10分钟
- **存储**: 存储到 `email_code` 表

### 2. 用户注册

- **端点**: `POST /auth/register`
- **验证**:
  - 邮箱是否已存在
  - 验证码是否正确（10分钟有效期）
  - 两次密码是否一致
- **密码**: 使用 Argon2 算法加密存储

### 3. 用户登录

- **端点**: `POST /auth/login`
- **验证**: 邮箱和密码
- **返回**: JWT Token（access_token）
- **Token 有效期**: 24小时（可配置）

## 📖 配置说明

### 邮箱配置

项目已配置 zhiliao-ainame 的邮箱授权码，可直接使用：

| 配置项 | 值 |
|-------|-----|
| MAIL_USERNAME | 487935272@qq.com |
| MAIL_PASSWORD | uixvdbysupnmbjha |
| MAIL_SERVER | smtp.qq.com |
| MAIL_PORT | 587 |
| MAIL_FROM_NAME | SparkCanvas |

### JWT 配置

| 配置项 | 默认值 | 说明 |
|-------|--------|------|
| JWT_SECRET_KEY | sparkcanvas-secret-key-2024 | 生产环境务必修改 |
| JWT_ACCESS_TOKEN_EXPIRES_HOURS | 24 | Access Token 有效期（小时） |
| JWT_REFRESH_TOKEN_EXPIRES_DAYS | 30 | Refresh Token 有效期（天） |

## ⚠️ 注意事项

### 1. QQ 邮箱特殊处理

代码已处理 QQ 邮箱 SMTP 关闭阶段的非标准响应：

```python
except SMTPResponseException as e:
    if e.code == -1 and b"\\x00\\x00\\x00" in str(e).encode():
        print("⚠️ 忽略 QQ 邮箱 SMTP 关闭阶段的非标准响应（邮件已成功发送）")
```

### 2. 密码安全

- 使用 Argon2 算法加密（推荐的密码加密算法）
- 密码长度：6-20 字符
- 用户名长度：3-20 字符

### 3. 验证码有效期

验证码有效期为 10 分钟，在 `EmailCodeRepository.check_email_code` 中验证。

### 4. 数据库字符集

数据库使用 utf8mb4 字符集，支持 emoji 等特殊字符。

## 🔍 故障排查

### 邮件发送失败

1. 检查网络连接
2. 确认 SMTP 配置正确
3. 查看日志中的详细错误信息

### 数据库连接失败

1. 确认 MySQL 服务已启动
2. 检查数据库连接字符串
3. 确认数据库已创建

### JWT Token 验证失败

1. 检查 Token 是否过期
2. 确认 JWT_SECRET_KEY 配置正确
3. Token 格式：`Bearer {token}`

## 📝 下一步开发

基于已完成的认证模块，可以继续开发：

- [ ] 工作台模块
- [ ] 内容生成模块
- [ ] 配图生成模块
- [ ] RAG 知识库模块
- [ ] Prompt 管理模块
- [ ] 历史记录模块

## 📞 技术支持

详细文档请参考：
- `spark-backend/SETUP.md` - 详细配置指南
- `config/README.md` - 配置说明
- `spark-backend/ARCHITECTURE_ANALYSIS.md` - 架构分析

