# 历史记录模块开发总结

## 一、模块概述

历史记录模块实现了对话历史记录的存储、查询和搜索功能。当前使用Redis作为存储后端，后续可平滑迁移到MySQL。

## 二、技术架构

### 2.1 分层架构

```
路由层 (routers/history.py)
    ↓
服务层 (services/history_service.py)
    ↓
存储层 (storage/history_store.py)
    ↓
Redis
```

### 2.2 数据存储设计

#### Redis Key设计

1. **用户会话索引**
   - Key: `history:user:{user_id}:index`
   - 类型: Set
   - 用途: 存储用户的所有会话ID
   - TTL: 7天

2. **会话历史记录**
   - Key: `history:user:{user_id}:session:{session_id}`
   - 类型: List
   - 用途: 存储指定会话的所有历史记录
   - TTL: 7天

3. **搜索索引**
   - Key: `history:search:user:{user_id}`
   - 类型: List
   - 用途: 存储所有历史记录，用于关键词搜索
   - TTL: 7天
   - 限制: 最多保留10000条记录

#### 数据格式

每条历史记录存储为JSON格式：
```json
{
  "session_id": "uuid-string",
  "message": "用户消息",
  "response": "助手回复",
  "timestamp": "2026-01-01T10:00:00Z"
}
```

## 三、API接口

### 3.1 查询对话历史记录

**接口:** `GET /api/v1/history/conversations`

**功能:** 查询用户的对话历史记录，支持按会话ID筛选和分页。

**请求参数:**
- `session_id` (可选): 会话ID，不传则返回所有会话
- `page` (可选): 页码，默认1
- `page_size` (可选): 每页数量，默认20，最大100

**响应示例:**
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
        "session_id": "uuid-string",
        "message": "用户消息",
        "response": "助手回复",
        "timestamp": "2026-01-01T10:00:00Z"
      }
    ]
  }
}
```

### 3.2 按关键词搜索历史记录

**接口:** `GET /api/v1/history/search`

**功能:** 按关键词搜索对话历史记录，支持全文检索。

**请求参数:**
- `keyword` (必填): 搜索关键词
- `page` (可选): 页码，默认1
- `page_size` (可选): 每页数量，默认20，最大100

**响应格式:** 与查询接口相同

## 四、开发流程

### 4.1 从历史记录开发到存入Redis的完整流程

#### 步骤1: 创建Schema定义
- **文件:** `schemas/history.py`
- **内容:** 定义请求/响应数据模型
  - `ConversationHistoryItem`: 单条历史记录
  - `ConversationHistoryListOut`: 历史记录列表响应

#### 步骤2: 创建存储层
- **文件:** `storage/history_store.py`
- **功能:** 
  - `save_conversation_history()`: 保存历史记录到Redis
  - `get_conversation_history()`: 从Redis查询历史记录
  - `search_conversation_history()`: 从Redis搜索历史记录
- **Redis操作:**
  1. 使用`LPUSH`将记录添加到List（保持时间顺序）
  2. 使用`SADD`维护用户会话索引
  3. 使用`EXPIRE`设置TTL为7天
  4. 使用`LTRIM`限制搜索索引长度

#### 步骤3: 创建服务层
- **文件:** `services/history_service.py`
- **功能:**
  - `get_conversation_history()`: 业务逻辑封装，参数校验
  - `search_conversation_history()`: 搜索业务逻辑封装
- **职责:**
  - 参数校验（页码、每页数量限制）
  - 调用存储层获取数据
  - 数据格式转换（Dict → Schema）
  - 日志记录

#### 步骤4: 创建路由层
- **文件:** `routers/history.py`
- **功能:**
  - 定义API端点
  - 处理HTTP请求/响应
  - 用户认证（Bearer Token）
  - 参数解析（Query参数）

#### 步骤5: 注册路由
- **文件:** `main.py`
- **操作:** 导入并注册历史记录路由

#### 步骤6: 集成到工作台
- **文件:** `services/workspace_service.py`
- **功能:** 在`send_message()`和`regenerate()`方法中自动保存历史记录
- **实现:** 调用`history_store.save_conversation_history()`

### 4.2 数据流转过程

```
用户发送消息
    ↓
workspace_service.send_message()
    ↓
生成内容后调用 history_store.save_conversation_history()
    ↓
Redis存储:
  1. 保存到会话历史记录List
  2. 添加到用户会话索引Set
  3. 添加到搜索索引List
    ↓
用户查询历史记录
    ↓
GET /api/v1/history/conversations
    ↓
history_service.get_conversation_history()
    ↓
history_store.get_conversation_history()
    ↓
从Redis读取数据并返回
```

## 五、Redis存储优势

### 5.1 为什么先使用Redis？

1. **快速开发:** Redis操作简单，无需设计表结构
2. **高性能:** Redis读写速度快，适合高频查询
3. **灵活扩展:** 支持多种数据结构（List、Set、Hash）
4. **自动过期:** 支持TTL，自动清理过期数据

### 5.2 后续迁移到MySQL的考虑

当前设计已考虑后续迁移：

1. **抽象存储层:** 存储逻辑集中在`history_store.py`，便于替换
2. **统一接口:** 服务层只依赖存储层的函数接口，不关心底层实现
3. **数据格式:** 使用JSON格式存储，便于迁移到MySQL的JSON字段

**迁移步骤（后续）:**
1. 创建MySQL表结构
2. 实现MySQL版本的存储函数
3. 修改`history_store.py`，添加配置开关选择存储后端
4. 数据迁移脚本（从Redis导出到MySQL）

## 六、注意事项

1. **TTL设置:** 历史记录TTL为7天，过期后自动删除
2. **搜索索引限制:** 搜索索引最多保留10000条记录，避免内存占用过大
3. **错误处理:** 历史记录保存失败不影响主流程，仅记录警告日志
4. **数据一致性:** 当前实现为最终一致性，不保证强一致性

## 七、文件清单

```
spark-backend/
├── schemas/
│   └── history.py              # 历史记录Schema定义
├── storage/
│   └── history_store.py         # 历史记录存储层（Redis）
├── services/
│   ├── history_service.py       # 历史记录服务层
│   └── workspace_service.py     # 工作台服务（已集成历史记录保存）
├── routers/
│   └── history.py               # 历史记录路由
└── main.py                      # 应用入口（已注册路由）
```

## 八、后续优化方向

1. **全文检索优化:** 使用Elasticsearch或MySQL的FULLTEXT索引
2. **数据持久化:** 迁移到MySQL，支持更复杂的查询
3. **缓存优化:** 热点数据缓存，提升查询性能
4. **统计分析:** 添加历史记录统计分析功能

