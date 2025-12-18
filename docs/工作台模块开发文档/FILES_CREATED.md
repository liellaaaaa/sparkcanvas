# 工作台模块开发 - 新增文件清单

## 📁 新增/修改的文件列表

### 1. Schema 层（`spark-backend/schemas/`）

- ✅ `schemas/workspace.py`
  - 定义工作台相关请求/响应数据模型：
    - `WorkspaceSessionCreateOut`
    - `WorkspaceSendMessageIn` / `WorkspaceSendMessageOut`
    - `WorkspaceContent`
    - `WorkspaceSessionInfoOut`
    - `WorkspaceUploadMaterialOut`
    - `WorkspaceRegenerateIn` / `WorkspaceRegenerateOut`

### 2. 服务层（`spark-backend/services/`）

- ✅ `services/workspace_service.py`
  - `WorkspaceService`：
    - `create_session()`
    - `get_session_info()`
    - `send_message()`
    - `regenerate()`
  - 内容生成方法：
    - `_generate_content_with_llm()`:调用通义千问生成内容
    - `_generate_fallback_content()`：LLM调用失败时的降级处理
  


### 3. 路由层（`spark-backend/routers/`）

- ✅ `routers/workspace.py`
  - 新增工作台路由模块：
    - `POST /api/v1/workspace/create-session`
    - `POST /api/v1/workspace/send-message`
    - `GET  /api/v1/workspace/session/{session_id}`
    - `POST /api/v1/workspace/upload-material`
    - `POST /api/v1/workspace/regenerate`
  - 统一接入 JWT 认证依赖

- ✅ `routers/__init__.py`
  - 导出 `workspace_router`

### 4. 应用入口（`spark-backend/main.py`）

- ✅ `main.py`
  - 引入并注册 `workspace_router`

### 5. 文档目录（`docs/工作台模块开发文档/`）

- ✅ `WORKSPACE_MODULE_SUMMARY.md`：本模块开发总结
- ✅ `FILES_CREATED.md`：文件变更与说明（本文件）
- ✅ `QUICKSTART.md`：工作台模块快速上手与测试指南
- ✅ `前后端联调测试指南.md`：前后端联调步骤与注意事项
- ✅ `test_workspace.http`：工作台模块 HTTP 接口测试文件

## 📊 文件统计概览

- 代码文件：
  - Schema：1 个（`schemas/workspace.py`）
  - Service：1 个（`services/workspace_service.py`）
  - Router：2 个（`routers/workspace.py`, `routers/__init__.py`）
  - 应用入口修改：1 个（`main.py`）

- 文档与测试：
  - 工作台文档：4 个
  - HTTP 测试：1 个

## 🔍 关键文件简要说明

- `schemas/workspace.py`
  - 对应系统架构与 `docs/api.md` 中的工作台 API 数据结构，方便前后端对齐字段。

- `services/workspace_service.py`
  - 封装工作台业务逻辑，将 Redis 会话存储与 API 解耦，便于后续扩展真正的内容生成链路。

- `routers/workspace.py`
  - 将工作台 API 统一挂载在 `/api/v1/workspace` 前缀下，风格与整体 API 设计保持一致。

- `docs/工作台模块开发文档/前后端联调测试指南.md`
  - 约定前端如何携带 Token、如何调用工作台接口，以及常见问题排查。

### 6. 配置文件

- ✅ `config/config.dev.yaml`
  - 新增 `dashscope` 配置（api_key / model / temperature）
  - 新增 `tavily` 配置（api_key）

- ✅ `spark-backend/core/config.py`
  - `AppConfig` 新增字段：`dashscope_api_key` / `dashscope_model` / `dashscope_temperature`
  - `load_config()` 新增 dashscope 配置读取

## ✅ 完成状态

所有与工作台模块相关的新增文件已创建并通过基础语法与 linter 检查，可直接用于本地运行与前端联调。  
**已接入阿里云通义千问（qwen-max）实现真实内容生成**，后续可继续扩展 RAG、配图生成等能力。


