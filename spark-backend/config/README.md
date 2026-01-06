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

# 阿里云 DashScope (通义千问) 配置
DASHSCOPE_API_KEY=
DASHSCOPE_MODEL=qwen-max
DASHSCOPE_TEMPERATURE=0.7
DASHSCOPE_EMBEDDING_MODEL=text-embedding-v4
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
- `DASHSCOPE_API_KEY`: 阿里云通义千问 API 密钥（用于内容生成）

## 常见问题

### 1. 通义千问连接错误 (ConnectionResetError 10054)

**错误信息**:
```
通义千问异常: ('Connection aborted.', ConnectionResetError(10054, '远程主机强迫关闭了一个现有的连接。'))
```

**可能原因**:
1. **网络不稳定**: 与阿里云 DashScope API 服务器的连接被中断
2. **API 密钥未配置或无效**: 检查 `DASHSCOPE_API_KEY` 是否正确配置
3. **请求超时**: 网络延迟过高导致连接超时
4. **防火墙/代理问题**: 本地防火墙或代理阻止了与阿里云服务器的连接
5. **SSL/TLS 证书问题**: SSL 握手失败

**解决方案**:

1. **检查 API 密钥配置**:
   - 确保在 `.env` 文件中配置了 `DASHSCOPE_API_KEY`
   - 访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/) 获取 API Key
   - 检查 API Key 是否有效,是否有足够的调用额度

2. **检查网络连接**:
   ```bash
   # 测试是否能访问阿里云 API
   ping dashscope.aliyuncs.com
   
   # 或使用 curl 测试
   curl -I https://dashscope.aliyuncs.com
   ```

3. **添加重试机制**: 代码中已有降级处理,但可以考虑添加自动重试

4. **更换网络环境**: 
   - 尝试切换到其他网络环境(例如手机热点)
   - 检查是否有代理设置影响连接

5. **查看详细日志**:
   - 检查后端日志中是否有更详细的错误信息
   - 确认是否是特定时间段的网络波动

**临时解决方案**:
- 系统已实现降级机制,当通义千问调用失败时会返回提示信息
- 可以稍后重试,或者暂时使用其他网络环境

### 2. 如何获取通义千问 API Key

1. 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/)
2. 登录阿里云账号(没有账号需要先注册)
3. 开通 DashScope 服务
4. 在控制台创建 API Key
5. 将 API Key 配置到 `.env` 文件的 `DASHSCOPE_API_KEY` 中
6. 重启后端服务使配置生效

