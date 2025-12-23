# 历史记录模块快速开始

## 一、前置条件

1. Redis服务已启动并配置
2. 后端服务已启动
3. 已获取有效的JWT Token（通过登录接口）

## 二、测试流程

### 2.1 准备工作

1. **启动Redis服务**
   ```bash
   # Windows
   redis-server
   
   # Linux/Mac
   redis-server
   ```

2. **配置Redis连接**
   在`config/config.dev.yaml`或环境变量中配置：
   ```yaml
   redis:
     url: "redis://localhost:6379/0"
   ```

3. **启动后端服务**
   ```bash
   cd spark-backend
   python main.py
   ```

### 2.2 测试步骤

#### 步骤1: 登录获取Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "your_password"
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "user_id": 1,
    "username": "test",
    "email": "test@example.com",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

#### 步骤2: 创建工作会话并发送消息

```http
POST /api/v1/workspace/create-session
Authorization: Bearer {access_token}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2026-01-01T10:00:00Z",
    "expires_at": "2026-01-01T10:30:00Z"
  }
}
```

```http
POST /api/v1/workspace/send-message
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "帮我写一篇关于旅行的文章",
  "material_source": "online",
  "platform": "xiaohongshu"
}
```

**说明:** 发送消息后，系统会自动保存历史记录到Redis。

#### 步骤3: 查询历史记录

```http
GET /api/v1/history/conversations?page=1&page_size=20
Authorization: Bearer {access_token}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 1,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "message": "帮我写一篇关于旅行的文章",
        "response": "标题\n\n正文内容...",
        "timestamp": "2026-01-01T10:00:00Z"
      }
    ]
  }
}
```

#### 步骤4: 按会话ID查询

```http
GET /api/v1/history/conversations?session_id=550e8400-e29b-41d4-a716-446655440000&page=1&page_size=20
Authorization: Bearer {access_token}
```

#### 步骤5: 关键词搜索

```http
GET /api/v1/history/search?keyword=旅行&page=1&page_size=20
Authorization: Bearer {access_token}
```

## 三、使用HTTP测试文件

创建`test_history.http`文件进行测试：

```http
### 变量定义
@baseUrl = http://localhost:8000
@token = your_access_token_here

### 1. 查询所有历史记录
GET {{baseUrl}}/api/v1/history/conversations?page=1&page_size=20
Authorization: Bearer {{token}}

### 2. 按会话ID查询
GET {{baseUrl}}/api/v1/history/conversations?session_id=550e8400-e29b-41d4-a716-446655440000&page=1&page_size=20
Authorization: Bearer {{token}}

### 3. 关键词搜索
GET {{baseUrl}}/api/v1/history/search?keyword=旅行&page=1&page_size=20
Authorization: Bearer {{token}}
```

## 四、验证Redis存储

### 4.1 使用Redis CLI验证

```bash
# 连接Redis
redis-cli

# 查看用户会话索引
SMEMBERS history:user:1:index

# 查看会话历史记录
LRANGE history:user:1:session:{session_id} 0 -1

# 查看搜索索引
LRANGE history:search:user:1 0 10
```

### 4.2 验证数据格式

Redis中存储的数据为JSON字符串，例如：
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "帮我写一篇关于旅行的文章",
  "response": "标题\n\n正文内容...",
  "timestamp": "2026-01-01T10:00:00Z"
}
```

## 五、常见问题

### 5.1 历史记录查询为空

**可能原因:**
1. Redis未启动或连接失败
2. 用户ID不匹配
3. 历史记录已过期（TTL 7天）

**解决方法:**
1. 检查Redis服务状态
2. 确认使用的Token对应的用户ID
3. 检查Redis中的Key是否存在

### 5.2 搜索功能不工作

**可能原因:**
1. 搜索索引未创建
2. 关键词匹配失败

**解决方法:**
1. 确认已发送过消息（会自动创建搜索索引）
2. 尝试使用消息或回复中的关键词

### 5.3 分页参数无效

**可能原因:**
- 页码或每页数量超出限制

**解决方法:**
- 页码必须 >= 1
- 每页数量必须在 1-100 之间

## 六、性能测试建议

### 6.1 批量生成测试数据

可以通过多次调用`send-message`接口生成大量历史记录，然后测试：
- 分页查询性能
- 搜索性能
- Redis内存占用

### 6.2 监控指标

- Redis内存使用量
- 查询响应时间
- 搜索响应时间
- 数据过期情况

## 七、下一步

1. **前端联调:** 与前端开发人员联调历史记录功能
2. **功能优化:** 根据实际使用情况优化搜索算法
3. **数据迁移:** 规划从Redis迁移到MySQL的方案

