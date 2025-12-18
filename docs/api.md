# SparkCanvas API 接口文档

## 文档说明

本文档包含SparkCanvas项目的所有API接口定义，按照模块组织，每个接口包含接口描述、请求数据和响应数据三部分。

**Base URL:** `/api/v1`

**认证方式:** Bearer Token (JWT)

**响应格式:** 统一JSON格式

---

## 1. 工作台API模块 (Workspace API)

### 1.1 创建会话

**接口描述:** 创建新的工作会话，用于内容生成流程。会话用于管理对话上下文和记忆。

**请求数据:**

- **Method:** `POST`
- **Path:** `/api/v1/workspace/create-session`
- **Headers:**
  ```
  Authorization: Bearer {token}
  Content-Type: application/json
  ```
- **Body:** 无

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "session_id": "uuid-string",
    "created_at": "2026-01-01T10:00:00",
    "expires_at": "2026-01-01T10:30:00"
  }
}
```

---

### 1.2 发送消息

**接口描述:** 发送消息到工作台，触发完整的内容生成流程（联网检索→标题优化→文风模仿→情绪强化→配图生成→输出解析）。

**请求数据:**

- **Method:** `POST`
- **Path:** `/api/v1/workspace/send-message`
- **Headers:**
  ```
  Authorization: Bearer {token}
  Content-Type: application/json
  ```
- **Body:**
  ```json
  {
    "session_id": "string (required)",
    "message": "string (required)",
    "material_source": "string (optional)",
    "platform": "string (required)"
  }
  ```
  - `session_id`: 会话ID
  - `message`: 用户输入的消息内容
  - `material_source`: 素材源，可选值: `"online"`(联网检索), `"rag"`(RAG知识库), `"upload"`(本地上传)，默认`"online"`
  - `platform`: 目标平台，必填值: `"xiaohongshu"`(小红书) 或 `"douyin"`(抖音)

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "session_id": "string",
    "content": {
      "title": "string",
      "body": "string",
      "image_url": "string"
    },
    "status": "completed",
    "timestamp": "2026-01-01T10:00:00"
  }
}
```

**状态码:**
- `200`: 成功
- `400`: 请求参数错误
- `401`: 未授权
- `429`: 请求频率超限
- `500`: 服务器内部错误
- `503`: 服务暂时不可用（大模型API异常）

---

### 1.3 获取会话信息

**接口描述:** 获取指定会话的详细信息，包括创建时间、过期时间、消息数量等。

**请求数据:**

- **Method:** `GET`
- **Path:** `/api/v1/workspace/session/{session_id}`
- **Headers:**
  ```
  Authorization: Bearer {token}
  ```
- **Path Parameters:**
  - `session_id`: 会话ID (string, required)

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "session_id": "string",
    "created_at": "2026-01-01T10:00:00",
    "expires_at": "2026-01-01T10:30:00",
    "message_count": 10,
    "last_message_time": "2026-01-01T10:15:00"
  }
}
```

---

### 1.4 上传素材/文档

**接口描述:** 上传素材或文档到工作台，支持PDF、Word、Txt格式。上传的文档将用于内容生成。

**请求数据:**

- **Method:** `POST`
- **Path:** `/api/v1/workspace/upload-material`
- **Headers:**
  ```
  Authorization: Bearer {token}
  Content-Type: multipart/form-data
  ```
- **Body (Form Data):**
  - `session_id`: 会话ID (string, required)
  - `file`: 上传的文件 (file, required, 支持PDF/Word/Txt格式)

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "file_id": "string",
    "file_name": "string",
    "file_size": 1024,
    "uploaded_at": "2026-01-01T10:00:00"
  }
}
```

---

### 1.5 重新生成

**接口描述:** 基于已有会话重新生成内容，支持调整情绪强度、风格偏好等参数。

**请求数据:**

- **Method:** `POST`
- **Path:** `/api/v1/workspace/regenerate`
- **Headers:**
  ```
  Authorization: Bearer {token}
  Content-Type: application/json
  ```
- **Body:**
  ```json
  {
    "session_id": "string (required)",
    "adjustments": {
      "emotion_intensity": "string (optional)",
      "style_preference": "string (optional)"
    }
  }
  ```
  - `session_id`: 会话ID
  - `adjustments`: 调整参数（可选）
    - `emotion_intensity`: 情绪强度
    - `style_preference`: 风格偏好

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "session_id": "string",
    "content": {
      "title": "string",
      "body": "string",
      "image_url": "string"
    },
    "status": "completed",
    "timestamp": "2026-01-01T10:00:00"
  }
}
```

---

## 2. 登录注册API模块 (Authentication API)

### 2.1 发送邮箱验证码

**接口描述:** 发送4位数字验证码到用户邮箱，用于注册验证。同一邮箱5分钟内只能发送一次。

**请求数据:**

- **Method:** `POST`
- **Path:** `/api/v1/auth/send-code`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body:**
  ```json
  {
    "email": "string (required)"
  }
  ```
  - `email`: 用户邮箱地址

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "message": "验证码已发送到您的邮箱"
  }
}
```

**状态码:**
- `200`: 成功
- `400`: 邮箱格式错误
- `429`: 请求频率超限（同一邮箱5分钟内只能发送一次）
- `500`: 服务器内部错误

---

### 2.2 注册

**接口描述:** 用户注册，创建新账户。需要提供用户名、邮箱、密码和邮箱验证码。

**请求数据:**

- **Method:** `POST`
- **Path:** `/api/v1/auth/register`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body:**
  ```json
  {
    "username": "string (required)",
    "email": "string (required)",
    "password": "string (required)",
    "verify_code": "string (required)"
  }
  ```
  - `username`: 用户名，长度1-100
  - `email`: 邮箱地址
  - `password`: 密码，长度8-32
  - `verify_code`: 邮箱验证码，4位数字

**响应数据:**

**成功响应:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "user_id": 1,
    "username": "string",
    "email": "string",
    "access_token": "string"
  }
}
```

**错误响应:**
```json
{
  "code": 400,
  "message": "请求参数错误",
  "error": {
    "verify_code": "验证码错误或已过期",
    "email": "邮箱已被注册"
  }
}
```

---

### 2.3 登录

**接口描述:** 用户登录，通过邮箱和密码验证，返回访问令牌(Access Token)。

**请求数据:**

- **Method:** `POST`
- **Path:** `/api/v1/auth/login`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body:**
  ```json
  {
    "email": "string (required)",
    "password": "string (required)"
  }
  ```
  - `email`: 邮箱地址
  - `password`: 密码

**响应数据:**

**成功响应:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "user_id": 1,
    "username": "string",
    "email": "string",
    "access_token": "string"
  }
}
```

**错误响应:**
```json
{
  "code": 401,
  "message": "认证失败",
  "error": "邮箱或密码错误"
}
```

---

### 2.4 登出

**接口描述:** 用户登出，使当前Token失效。

**请求数据:**

- **Method:** `POST`
- **Path:** `/api/v1/auth/logout`
- **Headers:**
  ```
  Authorization: Bearer {token}
  ```
- **Body:** 无

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

---

## 3. Prompt管理API模块 (Prompt Management API)

### 3.1 创建Prompt

**接口描述:** 创建新的Prompt模板，用于内容生成时的提示词管理。

**请求数据:**

- **Method:** `POST`
- **Path:** `/api/v1/prompt/create`
- **Headers:**
  ```
  Authorization: Bearer {token}
  Content-Type: application/json
  ```
- **Body:**
  ```json
  {
    "name": "string (required)",
    "content": "string (required)"
  }
  ```
  - `name`: 模板名称，长度1-255
  - `content`: Prompt内容

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "string",
    "content": "string",
    "user_id": 1,
    "created_at": "2026-01-01T10:00:00"
  }
}
```

---

### 3.2 查询Prompt列表

**接口描述:** 查询当前用户的所有Prompt模板列表，支持分页。

**请求数据:**

- **Method:** `GET`
- **Path:** `/api/v1/prompt/list`
- **Headers:**
  ```
  Authorization: Bearer {token}
  ```
- **Query Parameters:**
  - `page`: 页码，默认1 (integer, optional)
  - `page_size`: 每页数量，默认20，最大100 (integer, optional)

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": 1,
        "name": "string",
        "content": "string",
        "user_id": 1,
        "created_at": "2026-01-01T10:00:00",
        "updated_at": "2026-01-01T10:00:00"
      }
    ]
  }
}
```

---

### 3.3 更新Prompt

**接口描述:** 更新指定的Prompt模板，支持更新名称和内容。

**请求数据:**

- **Method:** `PUT`
- **Path:** `/api/v1/prompt/update`
- **Headers:**
  ```
  Authorization: Bearer {token}
  Content-Type: application/json
  ```
- **Body:**
  ```json
  {
    "id": "integer (required)",
    "name": "string (optional)",
    "content": "string (optional)"
  }
  ```
  - `id`: Prompt模板ID
  - `name`: 模板名称（可选）
  - `content`: Prompt内容（可选）

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "string",
    "content": "string",
    "updated_at": "2026-01-01T10:00:00"
  }
}
```

---

### 3.4 删除Prompt

**接口描述:** 删除指定的Prompt模板。

**请求数据:**

- **Method:** `DELETE`
- **Path:** `/api/v1/prompt/delete`
- **Headers:**
  ```
  Authorization: Bearer {token}
  Content-Type: application/json
  ```
- **Body:**
  ```json
  {
    "id": "integer (required)"
  }
  ```
  - `id`: Prompt模板ID

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

---

## 4. 历史记录API模块 (History API)

### 4.1 查询对话历史记录

**接口描述:** 查询用户的对话历史记录，支持按会话ID筛选和分页。

**请求数据:**

- **Method:** `GET`
- **Path:** `/api/v1/history/conversations`
- **Headers:**
  ```
  Authorization: Bearer {token}
  ```
- **Query Parameters:**
  - `session_id`: 会话ID，不传则返回所有会话 (string, optional)
  - `page`: 页码，默认1 (integer, optional)
  - `page_size`: 每页数量，默认20，最大100 (integer, optional)

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "session_id": "string",
        "message": "string",
        "response": "string",
        "timestamp": "2026-01-01T10:00:00"
      }
    ]
  }
}
```

---

### 4.2 按关键词搜索历史记录

**接口描述:** 按关键词搜索对话历史记录，支持全文检索。

**请求数据:**

- **Method:** `GET`
- **Path:** `/api/v1/history/search`
- **Headers:**
  ```
  Authorization: Bearer {token}
  ```
- **Query Parameters:**
  - `keyword`: 搜索关键词 (string, required)
  - `page`: 页码，默认1 (integer, optional)
  - `page_size`: 每页数量，默认20，最大100 (integer, optional)

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "session_id": "string",
        "message": "string",
        "response": "string",
        "timestamp": "2026-01-01T10:00:00"
      }
    ]
  }
}
```

---

## 5. 内容管理API模块 (Contents API)

### 5.1 查询内容历史

**接口描述:** 查询用户生成的内容历史记录（草稿/已发布），支持按平台和状态筛选。

**请求数据:**

- **Method:** `GET`
- **Path:** `/api/v1/contents/list`
- **Headers:**
  ```
  Authorization: Bearer {token}
  ```
- **Query Parameters:**
  - `platform`: 平台筛选，可选值: `"xiaohongshu"`(小红书) 或 `"douyin"`(抖音) (string, optional)
  - `status`: 状态筛选，可选值: `"draft"`(草稿) 或 `"published"`(已发布) (string, optional)
  - `page`: 页码，默认1 (integer, optional)
  - `page_size`: 每页数量，默认20，最大100 (integer, optional)

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": 1,
        "platform": "xiaohongshu",
        "title": "string",
        "body": "string",
        "image_url": "string",
        "status": "draft",
        "generated_at": "2026-01-01T10:00:00"
      }
    ]
  }
}
```

---

### 5.2 搜索内容

**接口描述:** 按关键词搜索内容记录，支持全文检索。

**请求数据:**

- **Method:** `GET`
- **Path:** `/api/v1/contents/search`
- **Headers:**
  ```
  Authorization: Bearer {token}
  ```
- **Query Parameters:**
  - `keyword`: 搜索关键词 (string, required)
  - `page`: 页码，默认1 (integer, optional)
  - `page_size`: 每页数量，默认20，最大100 (integer, optional)

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": 1,
        "platform": "xiaohongshu",
        "title": "string",
        "body": "string",
        "image_url": "string",
        "status": "draft",
        "generated_at": "2026-01-01T10:00:00"
      }
    ]
  }
}
```

---

## 6. 配图生成API模块 (Image Generation API)

### 6.1 生成配图

**接口描述:** 根据内容文本生成配图，使用DALL·E 3 API，确保分辨率≥1080P。

**请求数据:**

- **Method:** `POST`
- **Path:** `/api/v1/image/generate`
- **Headers:**
  ```
  Authorization: Bearer {token}
  Content-Type: application/json
  ```
- **Body:**
  ```json
  {
    "content": "string (required)",
    "platform": "string (required)"
  }
  ```
  - `content`: 内容文本，用于生成配图
  - `platform`: 目标平台，必填值: `"xiaohongshu"`(小红书) 或 `"douyin"`(抖音)

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "image_url": "string",
    "resolution": "1080x1080",
    "generated_at": "2026-01-01T10:00:00"
  }
}
```

---

### 6.2 批量生成配图

**接口描述:** 批量生成配图，返回多张备选图片（默认3张，最多5张），每张图片包含图文匹配度评分。

**请求数据:**

- **Method:** `POST`
- **Path:** `/api/v1/image/batch-generate`
- **Headers:**
  ```
  Authorization: Bearer {token}
  Content-Type: application/json
  ```
- **Body:**
  ```json
  {
    "content": "string (required)",
    "platform": "string (required)",
    "count": "integer (optional)"
  }
  ```
  - `content`: 内容文本
  - `platform`: 目标平台，必填值: `"xiaohongshu"`(小红书) 或 `"douyin"`(抖音)
  - `count`: 生成数量，默认3，最大5 (integer, optional)

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "images": [
      {
        "image_url": "string",
        "resolution": "1080x1080",
        "match_score": 0.85
      }
    ],
    "generated_at": "2026-01-01T10:00:00"
  }
}
```

---

### 6.3 下载图片

**接口描述:** 下载指定URL的图片文件。

**请求数据:**

- **Method:** `GET`
- **Path:** `/api/v1/image/download`
- **Headers:**
  ```
  Authorization: Bearer {token}
  ```
- **Query Parameters:**
  - `image_url`: 图片URL (string, required)

**响应数据:**

返回图片文件流 (binary)

---

## 7. RAG知识库API模块 (RAG Knowledge Base API)

### 7.1 文档上传

**接口描述:** 上传文档到RAG知识库，自动进行格式解析、智能分块、向量化并存储到Chroma向量数据库。

**请求数据:**

- **Method:** `POST`
- **Path:** `/api/v1/rag/upload`
- **Headers:**
  ```
  Authorization: Bearer {token}
  Content-Type: multipart/form-data
  ```
- **Body (Form Data):**
  - `file`: 上传的文件 (file, required, 支持PDF/Word/Txt格式)

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "document_id": "string",
    "file_name": "string",
    "file_size": 1024,
    "chunks_count": 10,
    "uploaded_at": "2026-01-01T10:00:00"
  }
}
```

---

### 7.2 删除文档

**接口描述:** 删除RAG知识库中的指定文档及其所有向量数据。

**请求数据:**

- **Method:** `DELETE`
- **Path:** `/api/v1/rag/delete`
- **Headers:**
  ```
  Authorization: Bearer {token}
  Content-Type: application/json
  ```
- **Body:**
  ```json
  {
    "document_id": "string (required)"
  }
  ```
  - `document_id`: 文档ID

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

---

### 7.3 文档列表

**接口描述:** 查询当前用户上传的所有文档列表，支持分页。

**请求数据:**

- **Method:** `GET`
- **Path:** `/api/v1/rag/list`
- **Headers:**
  ```
  Authorization: Bearer {token}
  ```
- **Query Parameters:**
  - `page`: 页码，默认1 (integer, optional)
  - `page_size`: 每页数量，默认20，最大100 (integer, optional)

**响应数据:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "document_id": "string",
        "file_name": "string",
        "file_size": 1024,
        "chunks_count": 10,
        "uploaded_at": "2026-01-01T10:00:00"
      }
    ]
  }
}
```

---

## 附录

### 统一响应格式

所有API接口统一使用以下响应格式：

```json
{
  "code": integer,
  "message": "string",
  "data": object | array | null,
  "error": object | string | null
}
```

**字段说明:**
- `code`: 响应状态码，HTTP状态码或业务状态码
- `message`: 响应消息，成功时为"success"，失败时为错误描述
- `data`: 响应数据，成功时返回数据，失败时为null
- `error`: 错误信息，成功时为null，失败时返回错误详情

### 状态码说明

| 状态码 | 说明 |
|-------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（Token无效或过期） |
| 404 | 资源不存在 |
| 429 | 请求频率超限 |
| 500 | 服务器内部错误 |
| 503 | 服务暂时不可用（大模型API异常） |

### 认证说明

大部分接口需要认证，需要在请求头中携带JWT Token：

```
Authorization: Bearer {access_token}
```

Token通过登录接口获取，有效期为2小时。

### 错误响应示例

**参数验证错误:**
```json
{
  "code": 400,
  "message": "请求参数错误",
  "error": {
    "field_name": "错误描述"
  }
}
```

**业务逻辑错误:**
```json
{
  "code": 400,
  "message": "业务逻辑错误",
  "error": "具体错误描述"
}
```

**服务器错误:**
```json
{
  "code": 500,
  "message": "服务器内部错误",
  "error": "错误详情（开发环境）"
}
```

