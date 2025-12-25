# RAG知识库模块快速开始指南

## 一、环境准备

### 1.1 安装依赖

```bash
cd spark-backend
pip install -r requirements.txt
```

**新增依赖:**
- `langchain-community>=0.3.0`: LangChain社区组件
- `pypdf>=3.0.0`: PDF文档解析
- `docx2txt>=0.8`: Word文档解析
- `dashscope>=1.14.0`: 阿里云DashScope SDK（已存在）

### 1.2 配置DashScope API Key

在`config/config.yaml`中配置：

```yaml
dashscope:
  api_key: "your-dashscope-api-key"
  embedding_model: "text-embedding-v4"
```

或通过环境变量：

```bash
export DASHSCOPE_API_KEY="your-dashscope-api-key"
export DASHSCOPE_EMBEDDING_MODEL="text-embedding-v4"
```

### 1.3 启动服务

```bash
cd spark-backend
python main.py
```

## 二、快速测试

### 2.1 使用测试脚本

```bash
cd spark-backend/test
python test_rag_api.py
```

测试脚本会自动：
1. 检查服务健康状态
2. 登录/注册用户
3. 创建测试文档
4. 上传文档
5. 查询文档列表
6. 语义检索
7. 删除文档

### 2.2 使用HTTP客户端测试

#### 2.2.1 登录获取Token

```http
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "email": "your-email@example.com",
  "password": "your-password"
}
```

#### 2.2.2 上传文档

```http
POST http://localhost:8000/api/v1/rag/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: <选择文件>
```

#### 2.2.3 查询文档列表

```http
GET http://localhost:8000/api/v1/rag/list?page=1&page_size=20
Authorization: Bearer {token}
```

#### 2.2.4 语义检索

```http
POST http://localhost:8000/api/v1/rag/search
Authorization: Bearer {token}
Content-Type: application/json

{
  "query": "查询关键词",
  "top_k": 5
}
```

#### 2.2.5 删除文档

```http
DELETE http://localhost:8000/api/v1/rag/delete
Authorization: Bearer {token}
Content-Type: application/json

{
  "document_id": "uuid-string"
}
```

## 三、常见问题

### 3.1 DashScope API Key未配置

**错误信息:** `Chroma客户端未初始化，请检查DashScope配置`

**解决方法:**
1. 检查`config/config.yaml`中的`dashscope.api_key`配置
2. 或设置环境变量`DASHSCOPE_API_KEY`

### 3.2 文档上传失败

**可能原因:**
1. 文件格式不支持（仅支持PDF、Word、Txt）
2. 文件过大（建议不超过10MB）
3. DashScope API调用失败

**解决方法:**
1. 检查文件格式
2. 检查文件大小
3. 查看日志文件了解详细错误信息

### 3.3 检索结果为空

**可能原因:**
1. 文档未上传成功
2. 查询文本与文档内容不相关
3. 用户ID不匹配

**解决方法:**
1. 检查文档列表，确认文档已上传
2. 尝试使用文档中的关键词进行检索
3. 确认使用正确的用户Token

## 四、测试数据准备

### 4.1 创建测试文档

创建一个`test_document.txt`文件：

```
这是一个测试文档。

用于测试RAG知识库的文档上传和检索功能。

包含一些测试内容，用于验证语义检索是否正常工作。

关键词：测试、RAG、知识库、检索
```

### 4.2 上传测试文档

使用测试脚本或HTTP客户端上传文档。

### 4.3 测试检索

尝试以下查询：
- "测试"
- "RAG"
- "知识库"
- "检索功能"

## 五、性能优化建议

1. **文档大小:** 建议单文件不超过10MB
2. **分块大小:** 默认1000字符，可根据实际需求调整
3. **批量上传:** 如需上传大量文档，建议分批上传
4. **检索优化:** 使用合适的top_k值，避免返回过多结果

## 六、下一步

1. 查看完整开发文档：`RAG_MODULE_SUMMARY.md`
2. 查看文件清单：`FILES_CREATED.md`
3. 集成到工作台模块，实现RAG检索功能

