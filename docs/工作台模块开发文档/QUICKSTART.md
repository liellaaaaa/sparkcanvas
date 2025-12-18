# SparkCanvas 工作台模块快速启动指南

本指南说明如何在本地启动后端、完成登录获取 Token，并调用工作台相关接口完成基础联调。

> 当前工作台模块已实现会话管理与占位内容生成逻辑，后续可无缝接入真实内容生成引擎。

## 1. 环境准备

### 1.1 安装后端依赖

```bash
cd spark-backend
pip install -r requirements.txt
```

### 1.2 数据库与配置

确保你已经按照登录认证模块的 QUICKSTART 完成以下步骤：

- 已创建数据库 `sparkcanvas`
- 已执行 `python init_db.py` 创建基础表（`users` 等）
- 已配置好 `config/.env` 或 `config/config.yaml`（MySQL / JWT / 邮件 / Redis 等）

### 1.3 启动后端

```bash
cd spark-backend
python main.py
```

默认监听：`http://localhost:8000`

可访问：

- 健康检查：`GET /health`
- 文档：
  - Swagger UI: `http://localhost:8000/docs`
  - ReDoc: `http://localhost:8000/redoc`

## 2. 登录获取 Token

所有工作台接口默认需要 JWT 认证，请先完成登录流程。

### 2.1 发送验证码

```bash
curl "http://localhost:8000/auth/code?email=test@example.com"
```

### 2.2 注册用户（如尚未注册）

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

### 2.3 用户登录

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456"
  }'
```

响应示例（简化）：

```json
{
  "user": {
    "id": 1,
    "email": "test@example.com",
    "username": "testuser"
  },
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

> 后续调用工作台接口时，需要在请求头中携带：  
> `Authorization: Bearer {token}`

## 3. 工作台接口快速体验

### 3.1 创建会话

**接口**：`POST /api/v1/workspace/create-session`  
**认证**：需要

```bash
curl -X POST "http://localhost:8000/api/v1/workspace/create-session" \
  -H "Authorization: Bearer {token}"
```

响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "session_id": "uuid-string",
    "created_at": "2026-01-01T10:00:00Z",
    "expires_at": "2026-01-01T10:30:00Z"
  },
  "error": null
}
```

### 3.2 发送消息

**接口**：`POST /api/v1/workspace/send-message`  
**认证**：需要

```bash
curl -X POST "http://localhost:8000/api/v1/workspace/send-message" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "上一步返回的session_id",
    "message": "帮我写一篇关于提升自媒体爆款率的小红书笔记",
    "material_source": "online",
    "platform": "xiaohongshu"
  }'
```

返回示例（占位生成结构）：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "session_id": "string",
    "content": {
      "title": "[xiaohongshu] 首次生成内容占位标题",
      "body": "这是一个工作台占位内容，后续会接入真实的大模型内容生成逻辑。\n- 平台：xiaohongshu\n- 素材源：online\n- 原始输入：帮我写一篇关于提升自媒体爆款率的小红书笔记",
      "image_url": null
    },
    "status": "completed",
    "timestamp": "2026-01-01T10:00:00Z"
  },
  "error": null
}
```

### 3.3 获取会话信息

**接口**：`GET /api/v1/workspace/session/{session_id}`  
**认证**：需要

```bash
curl "http://localhost:8000/api/v1/workspace/session/{session_id}" \
  -H "Authorization: Bearer {token}"
```

响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "session_id": "string",
    "created_at": "2026-01-01T10:00:00Z",
    "expires_at": "2026-01-01T10:30:00Z",
    "message_count": 2,
    "last_message_time": "2026-01-01T10:01:00Z"
  },
  "error": null
}
```

### 3.4 上传素材（占位实现）

**接口**：`POST /api/v1/workspace/upload-material`  
**认证**：需要  
**说明**：当前实现仅返回文件元信息，不做真实存储与解析。

```bash
curl -X POST "http://localhost:8000/api/v1/workspace/upload-material" \
  -H "Authorization: Bearer {token}" \
  -F "session_id={session_id}" \
  -F "file=@/path/to/your/file.txt"
```

响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "file_id": "session_id:file.txt",
    "file_name": "file.txt",
    "file_size": 1024,
    "uploaded_at": "2026-01-01T10:05:00Z"
  },
  "error": null
}
```

### 3.5 重新生成

**接口**：`POST /api/v1/workspace/regenerate`  
**认证**：需要

```bash
curl -X POST "http://localhost:8000/api/v1/workspace/regenerate" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "{session_id}",
    "adjustments": {
      "emotion_intensity": "high",
      "style_preference": "大V同款"
    }
  }'
```

响应结构与 `send-message` 一致，只是生成逻辑目前仍为占位。

## 4. 前端联调注意事项（简要）

详细的前后端联调说明见：`docs/工作台模块开发文档/前后端联调测试指南.md`，这里只列关键点：

- 基础 URL 建议配置为：`http://localhost:8000`
- 工作台相关接口统一前缀：`/api/v1/workspace`
- 所有接口需要在请求头携带：
  - `Authorization: Bearer {token}`
- 响应统一为：
  - `code` / `message` / `data` / `error` 四个字段

## 5. 常见问题

1. **提示会话不存在或已过期**
   - 检查 `session_id` 是否正确
   - 检查 Redis 是否正常工作
2. **401/403 未授权**
   - 确认登录获取的 `token` 是否正确、未过期
   - 请求头中是否正确设置了 `Authorization: Bearer {token}`
3. **上传素材报错**
   - 确认使用了 `multipart/form-data` 方式提交
   - 参数名需为 `session_id` 与 `file`

如果后续需要接入真实内容生成链路，可在不改变接口的前提下，直接扩展 `WorkspaceService` 中的占位实现。 


