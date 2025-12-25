# RAG知识库模块开发总结

## 一、模块概述

RAG知识库模块实现了文档上传、向量化存储、语义检索等功能。使用Chroma作为向量数据库，DashScope（阿里通义）作为Embedding服务，支持PDF、Word、Txt等格式的文档。

## 二、技术架构

### 2.1 分层架构

```
路由层 (routers/rag.py)
    ↓
服务层 (services/rag_service.py)
    ↓
存储层 (storage/chroma_client.py + services/embedding_service.py)
    ↓
Chroma + DashScope API
```

### 2.2 核心技术栈

1. **向量数据库：** Chroma（本地持久化存储）
2. **Embedding服务：** DashScope text-embedding-v4
3. **文档解析：** LangChain DocumentLoaders（PDF、Word、Txt）
4. **文本分块：** RecursiveCharacterTextSplitter

### 2.3 数据存储设计

#### Chroma存储
- **持久化目录：** `./chroma_db`（可配置）
- **向量维度：** 1536（DashScope text-embedding-v4）
- **元数据：** 每个chunk包含document_id、user_id、file_name、chunk_index

#### 文档元数据存储
- **存储方式：** JSON文件（`storage/rag_metadata.json`）
- **数据结构：**
  ```json
  {
    "user_id": {
      "document_id": {
        "document_id": "uuid",
        "file_name": "example.pdf",
        "file_size": 1024,
        "chunks_count": 10,
        "uploaded_at": "2026-01-01T10:00:00Z"
      }
    }
  }
  ```
- **后续优化：** 可迁移到MySQL表存储

## 三、API接口

### 3.1 上传文档

**接口:** `POST /api/v1/rag/upload`

**功能:** 上传文档到RAG知识库，自动进行格式解析、智能分块、向量化并存储到Chroma。

**请求参数:**
- `file` (必填): 上传的文件（支持PDF/Word/Txt格式）

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "document_id": "uuid-string",
    "file_name": "example.pdf",
    "file_size": 1024,
    "chunks_count": 10,
    "uploaded_at": "2026-01-01T10:00:00Z"
  }
}
```

### 3.2 删除文档

**接口:** `DELETE /api/v1/rag/delete`

**功能:** 删除RAG知识库中的指定文档及其所有向量数据。

**请求参数:**
```json
{
  "document_id": "uuid-string"
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

### 3.3 文档列表

**接口:** `GET /api/v1/rag/list`

**功能:** 查询当前用户上传的所有文档列表，支持分页。

**请求参数:**
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
        "document_id": "uuid-string",
        "file_name": "example.pdf",
        "file_size": 1024,
        "chunks_count": 10,
        "uploaded_at": "2026-01-01T10:00:00Z"
      }
    ]
  }
}
```

### 3.4 语义检索

**接口:** `POST /api/v1/rag/search`

**功能:** 按关键词进行语义检索，返回相似度最高的文档片段。

**请求参数:**
```json
{
  "query": "查询文本",
  "top_k": 5
}
```

**响应示例:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "query": "查询文本",
    "results": [
      {
        "content": "文档内容片段",
        "score": 0.85,
        "metadata": {
          "document_id": "uuid-string",
          "user_id": 1,
          "file_name": "example.pdf",
          "chunk_index": 0
        }
      }
    ]
  }
}
```

## 四、开发流程

### 4.1 从文档上传到向量存储的完整流程

#### 步骤1: 创建Schema定义
- **文件:** `schemas/rag.py`
- **内容:** 定义请求/响应数据模型
  - `RAGDocumentUploadOut`: 文档上传响应
  - `RAGDocumentItem`: 文档列表项
  - `RAGDocumentListOut`: 文档列表响应
  - `RAGDeleteIn`: 删除文档请求
  - `RAGSearchIn`: 检索请求
  - `RAGSearchOut`: 检索响应

#### 步骤2: 实现DashScope Embedding封装
- **文件:** `services/embedding_service.py`
- **功能:** 
  - `DashScopeEmbeddings`: 封装DashScope API，兼容LangChain Embeddings接口
  - `get_embeddings()`: 获取Embeddings实例（单例模式）

#### 步骤3: 更新Chroma客户端
- **文件:** `storage/chroma_client.py`
- **修改:** 替换OpenAI Embeddings为DashScope Embeddings
- **功能:**
  - `get_chroma_client()`: 获取Chroma客户端（单例模式）
  - `get_embeddings()`: 获取Embeddings实例

#### 步骤4: 创建RAG服务层
- **文件:** `services/rag_service.py`
- **功能:**
  - `upload_document()`: 上传文档，解析、分块、向量化、存储
  - `delete_document()`: 删除文档及其向量数据
  - `list_documents()`: 查询文档列表
  - `search()`: 语义检索

#### 步骤5: 创建路由层
- **文件:** `routers/rag.py`
- **功能:**
  - 定义API端点
  - 处理HTTP请求/响应
  - 用户认证（Bearer Token）
  - 文件上传处理

#### 步骤6: 注册路由
- **文件:** `main.py`
- **操作:** 导入并注册RAG路由

### 4.2 数据流转过程

```
用户上传文档
    ↓
rag_service.upload_document()
    ↓
文档解析（PDF/Word/Txt）
    ↓
文本分块（RecursiveCharacterTextSplitter）
    ↓
DashScope Embedding向量化
    ↓
Chroma向量存储
    ↓
保存文档元数据（JSON文件）
    ↓
返回上传结果

用户检索
    ↓
POST /api/v1/rag/search
    ↓
rag_service.search()
    ↓
DashScope Embedding向量化查询文本
    ↓
Chroma相似度检索
    ↓
过滤用户数据
    ↓
返回检索结果
```

## 五、DashScope Embedding优势

### 5.1 为什么使用DashScope？

1. **国产化：** 阿里云服务，符合国产化要求
2. **性能优异：** text-embedding-v4模型性能优秀
3. **成本可控：** 相比OpenAI API，成本更低
4. **稳定可靠：** 阿里云基础设施保障

### 5.2 技术实现

1. **兼容LangChain：** 实现LangChain Embeddings接口，无缝集成
2. **批量处理：** 支持批量向量化，提升效率
3. **错误处理：** 完善的异常处理和日志记录

## 六、配置说明

### 6.1 配置文件

在`config/config.yaml`中添加DashScope配置：

```yaml
dashscope:
  api_key: "your-api-key"
  model: "qwen-max"
  temperature: 0.7
  embedding_model: "text-embedding-v4"

chroma:
  persist_directory: "./chroma_db"
```

### 6.2 环境变量

也可以通过环境变量配置：

```bash
export DASHSCOPE_API_KEY="your-api-key"
export DASHSCOPE_EMBEDDING_MODEL="text-embedding-v4"
export CHROMA_PERSIST_DIRECTORY="./chroma_db"
```

## 七、注意事项

1. **文件大小限制：** 建议单文件不超过10MB，避免处理时间过长
2. **分块策略：** 默认chunk_size=1000，chunk_overlap=200，可根据实际需求调整
3. **用户隔离：** 所有操作都基于user_id进行隔离，确保数据安全
4. **元数据存储：** 当前使用JSON文件存储元数据，后续可迁移到MySQL
5. **向量维度：** DashScope text-embedding-v4向量维度为1536
6. **错误处理：** 文档上传失败不影响其他功能，仅记录错误日志

## 八、文件清单

```
spark-backend/
├── schemas/
│   └── rag.py                      # RAG相关Schema定义
├── services/
│   ├── embedding_service.py        # DashScope Embedding封装
│   └── rag_service.py              # RAG服务层
├── storage/
│   ├── chroma_client.py            # Chroma客户端（已更新为DashScope）
│   └── rag_metadata.json           # 文档元数据存储（自动生成）
├── routers/
│   └── rag.py                      # RAG路由
├── test/
│   └── test_rag_api.py             # RAG API测试脚本
└── main.py                          # 应用入口（已注册路由）
```

## 九、后续优化方向

1. **元数据迁移：** 将JSON文件存储迁移到MySQL表
2. **文档格式扩展：** 支持更多文档格式（Markdown、Excel等）
3. **分块策略优化：** 根据文档类型选择不同的分块策略
4. **检索优化：** 支持混合检索（向量检索+关键词检索）
5. **缓存机制：** 对热点查询结果进行缓存
6. **批量操作：** 支持批量上传、批量删除等操作
7. **统计分析：** 添加文档使用统计、检索统计等功能

