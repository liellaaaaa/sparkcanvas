# 配置说明

## 配置文件说明

本项目使用两种方式管理配置：
1. `.env` 环境变量文件（优先级最高）
2. `config.yaml` 配置文件

### 配置步骤

1. **创建 .env 文件**

在 `config` 目录下创建 `.env` 文件，内容如下：

```env
# 应用配置
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8000

# 数据库配置
MYSQL_URL=mysql+aiomysql://root:1234@127.0.0.1:3306/sparkcanvas?charset=utf8mb4

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# JWT 配置
JWT_SECRET_KEY=sparkcanvas-secret-key-2024
JWT_ACCESS_TOKEN_EXPIRES_HOURS=24
JWT_REFRESH_TOKEN_EXPIRES_DAYS=30

# 邮件配置 (已配置 zhiliao-ainame 的授权码)
MAIL_USERNAME=487935272@qq.com
MAIL_PASSWORD=uixvdbysupnmbjha
MAIL_FROM=487935272@qq.com
MAIL_PORT=587
MAIL_SERVER=smtp.qq.com
MAIL_FROM_NAME=SparkCanvas
MAIL_STARTTLS=true
MAIL_SSL_TLS=false

# OpenAI 配置
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL_NAME=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# DALL·E 3 配置
DALLE_API_KEY=
DALLE_BASE_URL=https://api.openai.com/v1

# Tavily Search 配置
TAVILY_API_KEY=

# Chroma 配置
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

2. **邮箱配置说明**

已配置 zhiliao-ainame 项目的邮箱授权码：
- 邮箱：487935272@qq.com
- 授权码：uixvdbysupnmbjha
- 服务器：smtp.qq.com
- 端口：587

该配置可以直接用于发送验证码邮件。

3. **数据库配置说明**

确保 MySQL 数据库已创建：
```sql
CREATE DATABASE sparkcanvas DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

4. **初始化数据库**

```bash
cd spark-backend
python init_db.py
```

## 配置项说明

### 必需配置
- `MYSQL_URL`: 数据库连接字符串
- `JWT_SECRET_KEY`: JWT 加密密钥（生产环境务必修改）
- `MAIL_USERNAME`: 邮箱用户名
- `MAIL_PASSWORD`: 邮箱授权码

### 可选配置
- `REDIS_URL`: Redis 连接字符串（用于限流和会话管理）
- `OPENAI_API_KEY`: OpenAI API 密钥（用于 LLM 对话）
- `DALLE_API_KEY`: DALL·E API 密钥（用于配图生成）
- `TAVILY_API_KEY`: Tavily API 密钥（用于联网检索）

