# RAG知识库模块文件清单

## 一、后端代码文件

### 1. Schema定义
- **文件路径:** `spark-backend/schemas/rag.py`
- **说明:** 定义RAG知识库相关的数据模型
- **主要内容:**
  - `RAGDocumentUploadOut`: 文档上传响应
  - `RAGDocumentItem`: 文档列表项
  - `RAGDocumentListOut`: 文档列表响应
  - `RAGDeleteIn`: 删除文档请求
  - `RAGSearchIn`: 检索请求
  - `RAGSearchOut`: 检索响应
  - `RAGSearchResult`: 检索结果项

### 2. Embedding服务
- **文件路径:** `spark-backend/services/embedding_service.py`
- **说明:** DashScope Embedding封装，兼容LangChain接口
- **主要类:**
  - `DashScopeEmbeddings`: DashScope Embedding封装类
    - `embed_documents()`: 批量生成文档向量
    - `embed_query()`: 生成查询向量
  - `get_embeddings()`: 获取Embeddings实例（单例模式）

### 3. RAG服务层
- **文件路径:** `spark-backend/services/rag_service.py`
- **说明:** RAG知识库业务逻辑层
- **主要类:**
  - `RAGService`: RAG知识库服务类
    - `upload_document()`: 上传文档
    - `delete_document()`: 删除文档
    - `list_documents()`: 查询文档列表
    - `search()`: 语义检索

### 4. Chroma客户端（已更新）
- **文件路径:** `spark-backend/storage/chroma_client.py`
- **修改内容:** 
  - 移除OpenAI Embeddings依赖
  - 使用DashScope Embeddings
  - 更新配置检查逻辑

### 5. 路由层
- **文件路径:** `spark-backend/routers/rag.py`
- **说明:** RAG知识库API路由
- **主要接口:**
  - `POST /api/v1/rag/upload`: 上传文档
  - `DELETE /api/v1/rag/delete`: 删除文档
  - `GET /api/v1/rag/list`: 查询文档列表
  - `POST /api/v1/rag/search`: 语义检索

### 6. 修改的文件

#### 6.1 应用入口
- **文件路径:** `spark-backend/main.py`
- **修改内容:** 
  - 导入RAG路由
  - 注册RAG路由

#### 6.2 配置文件
- **文件路径:** `spark-backend/core/config.py`
- **修改内容:**
  - 添加`dashscope_embedding_model`配置项
  - 更新配置加载逻辑

#### 6.3 配置文件
- **文件路径:** `config/config.yaml`
- **修改内容:**
  - 添加DashScope配置项

#### 6.4 依赖文件
- **文件路径:** `spark-backend/requirements.txt`
- **修改内容:**
  - 添加`langchain-community>=0.3.0`
  - 添加`pypdf>=3.0.0`
  - 添加`docx2txt>=0.8`

## 二、文档文件

### 1. 模块开发总结
- **文件路径:** `docs/RAG知识库模块开发文档/RAG_MODULE_SUMMARY.md`
- **说明:** 完整的模块开发文档，包括架构设计、API接口、开发流程等

### 2. 文件清单（本文件）
- **文件路径:** `docs/RAG知识库模块开发文档/FILES_CREATED.md`
- **说明:** 记录所有创建和修改的文件

## 三、文件依赖关系

```
main.py
  └── routers/rag.py
      └── services/rag_service.py
          ├── storage/chroma_client.py
          │   └── services/embedding_service.py
          │       └── dashscope API
          └── langchain (文档加载、分块)

services/embedding_service.py
  └── dashscope API
```

## 四、数据存储

### Chroma向量存储
- **存储位置:** `./chroma_db`（可配置）
- **存储内容:** 文档分块的向量数据
- **元数据:** document_id、user_id、file_name、chunk_index

### 文档元数据存储
- **存储位置:** `spark-backend/storage/rag_metadata.json`
- **存储内容:** 文档基本信息（文件名、大小、分块数等）
- **格式:** JSON文件
- **后续:** 可迁移到MySQL表

## 五、API端点

### 上传文档
- **方法:** POST
- **路径:** `/api/v1/rag/upload`
- **认证:** Bearer Token
- **参数:** 
  - `file` (multipart/form-data): 上传的文件

### 删除文档
- **方法:** DELETE
- **路径:** `/api/v1/rag/delete`
- **认证:** Bearer Token
- **参数:**
  - `document_id` (JSON body): 文档ID

### 查询文档列表
- **方法:** GET
- **路径:** `/api/v1/rag/list`
- **认证:** Bearer Token
- **参数:**
  - `page` (query): 页码，默认1
  - `page_size` (query): 每页数量，默认20，最大100

### 语义检索
- **方法:** POST
- **路径:** `/api/v1/rag/search`
- **认证:** Bearer Token
- **参数:**
  - `query` (JSON body): 查询文本
  - `top_k` (JSON body): 返回Top-K结果，默认5

## 六、后续开发建议

1. **元数据迁移:** 规划从JSON文件迁移到MySQL的方案
2. **文档格式扩展:** 支持更多文档格式（Markdown、Excel等）
3. **检索优化:** 实现混合检索（向量检索+关键词检索）
4. **缓存机制:** 对热点查询结果进行缓存
5. **批量操作:** 支持批量上传、批量删除等操作
6. **统计分析:** 添加文档使用统计、检索统计等功能

