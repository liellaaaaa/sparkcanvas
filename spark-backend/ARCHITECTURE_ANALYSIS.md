# SparkCanvas 架构分析


## 一、完整架构

### 1.1 目录结构

```
spark-backend/
├── main.py                    # FastAPI 应用入口
├── dependencies.py            # 依赖注入（数据库、认证等）
├── requirements.txt           # 项目依赖
│
├── core/                      # 🔧 基础设施层（核心工具）
│   ├── __init__.py
│   ├── config.py             # 配置管理（从 .env 和 YAML 加载）
│   ├── logger.py             # 日志配置（loguru）
│   ├── rate_limit.py         # 限流功能（Redis 固定窗口）
│   └── exceptions.py         # 自定义异常类
│
├── storage/                   # 💾 存储层
│   ├── __init__.py
│   ├── redis_client.py       # Redis 客户端封装
│   ├── chroma_client.py      # Chroma 向量数据库客户端
│   └── session_store.py      # 会话存储管理
│
├── models/                    # 📊 数据模型层
│   ├── __init__.py
│   ├── user.py               # 用户模型
│   ├── content.py            # 内容模型
│   ├── prompt.py             # Prompt 模型
│   └── base.py               # 基础模型（SQLAlchemy Base）
│
├── repository/                # 🗄️ 数据访问层
│   ├── __init__.py
│   ├── user_repo.py          # 用户数据访问
│   ├── content_repo.py       # 内容数据访问
│   ├── prompt_repo.py        # Prompt 数据访问
│   └── base_repo.py          # 基础 Repository 类
│
├── services/                  # 🎯 业务服务层
│   ├── __init__.py
│   ├── auth_service.py       # 认证服务（注册、登录、Token管理）
│   ├── workspace_service.py  # 工作台服务（Memory管理、对话上下文）
│   ├── content_service.py    # 内容生成服务（标题优化、文风、情绪强化）
│   ├── image_service.py      # 配图生成服务（DALL·E 3）
│   ├── rag_service.py        # RAG 知识库服务（文档上传、向量检索）
│   ├── prompt_service.py     # Prompt 管理服务
│   ├── history_service.py    # 历史记录服务
│   └── llm_client.py         # LLM 客户端封装（OpenAI API）
│
├── routers/                   # 🛣️ 路由层
│   ├── __init__.py
│   ├── workspace.py         # 工作台 API
│   ├── auth.py              # 认证 API
│   ├── prompt.py            # Prompt 管理 API
│   ├── history.py           # 历史记录 API
│   ├── contents.py          # 内容管理 API
│   ├── image.py             # 配图生成 API
│   └── rag.py               # RAG 知识库 API
│
├── schemas/                   # 📋 数据验证层（Pydantic 模型）
│   ├── __init__.py
│   ├── workspace.py         # 工作台相关 Schema
│   ├── auth.py              # 认证相关 Schema
│   ├── prompt.py            # Prompt 相关 Schema
│   ├── history.py           # 历史记录相关 Schema
│   ├── contents.py          # 内容相关 Schema
│   ├── image.py             # 配图相关 Schema
│   └── common.py            # 通用 Schema（响应格式等）
│
├── utils/                     # 🛠️ 工具层
│   ├── __init__.py
│   ├── response.py          # 响应格式化工具
│   ├── exceptions.py         # 异常处理工具
│   ├── validators.py        # 数据验证工具
│   └── helpers.py           # 通用辅助函数
│
├── middleware/                # 🔄 中间件层
│   ├── __init__.py
│   ├── logging.py           # 请求日志中间件
│   ├── rate_limit.py        # 限流中间件
│   ├── error_handler.py     # 错误处理中间件
│   └── cors.py              # CORS 中间件
│
└── settings/                  # ⚙️ 配置层
    ├── __init__.py
    ├── dev.py               # 开发环境配置
    ├── prod.py              # 生产环境配置
    └── base.py              # 基础配置
```

### 1.2 架构分层说明

```
┌─────────────────────────────────────────┐
│         routers/ (API 路由层)            │  ← 处理 HTTP 请求/响应
├─────────────────────────────────────────┤
│         services/ (业务服务层)           │  ← 核心业务逻辑
├─────────────────────────────────────────┤
│    repository/ (数据访问层)              │  ← 数据库操作
│    storage/ (存储层)                     │  ← Redis/Chroma 操作
├─────────────────────────────────────────┤
│         models/ (数据模型层)             │  ← ORM 模型定义
├─────────────────────────────────────────┤
│    core/ (基础设施层)                     │  ← 配置、日志、限流
│    utils/ (工具层)                        │  ← 通用工具函数
│    middleware/ (中间件层)                 │  ← 跨切面关注点
└─────────────────────────────────────────┘
```

## 二、各模块职责说明

### 2.1 core/ - 基础设施层
**职责**：提供项目运行所需的基础设施和工具

| 文件 | 职责 |
|------|------|
| `config.py` | 配置管理（从 .env 和 YAML 加载，参考 ai-volunteer 设计） |
| `logger.py` | 日志配置（loguru 设置） |
| `rate_limit.py` | 限流功能（Redis 固定窗口限流） |
| `exceptions.py` | 自定义异常类定义 |

**示例**：
```python
# core/config.py - 参考 ai-volunteer/backend/core/config.py
from dataclasses import dataclass
from pathlib import Path
import os
import yaml
from dotenv import load_dotenv

@dataclass
class AppConfig:
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    mysql_url: str = ""
    redis_url: str = ""
    openai_api_key: str = ""
    # ... 其他配置

def load_config(env: str | None = None) -> AppConfig:
    # 从 .env 和 YAML 加载配置
    pass
```

### 2.2 storage/ - 存储层
**职责**：统一管理所有存储客户端（Redis、Chroma 等）

| 文件 | 职责 |
|------|------|
| `redis_client.py` | Redis 客户端封装（连接池、基本操作） |
| `chroma_client.py` | Chroma 向量数据库客户端封装 |
| `session_store.py` | 会话存储管理（基于 Redis） |

**示例**：
```python
# storage/redis_client.py
from redis import asyncio as aioredis
from core.config import AppConfig

async def get_redis(redis_url: str) -> aioredis.Redis:
    """获取 Redis 客户端"""
    return await aioredis.from_url(redis_url)

# storage/chroma_client.py
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

def get_chroma_client(persist_directory: str):
    """获取 Chroma 客户端"""
    embeddings = OpenAIEmbeddings()
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings)
```

### 2.3 services/ - 业务服务层
**职责**：封装所有业务逻辑，routers 只负责调用 services

| 文件 | 职责 |
|------|------|
| `auth_service.py` | 认证服务（注册、登录、Token 生成/验证） |
| `workspace_service.py` | 工作台服务（Memory 管理、对话上下文、会话管理） |
| `content_service.py` | 内容生成服务（标题优化、文风模仿、情绪强化、结构化生成） |
| `image_service.py` | 配图生成服务（DALL·E 3 API 调用、图文匹配度评估） |
| `rag_service.py` | RAG 知识库服务（文档上传、分块、向量化、语义检索） |
| `prompt_service.py` | Prompt 管理服务（CRUD 操作） |
| `history_service.py` | 历史记录服务（对话历史、内容历史） |
| `llm_client.py` | LLM 客户端封装（OpenAI API 调用） |

**示例**：
```python
# services/auth_service.py
from core.auth import AuthHandler
from repository.user_repo import UserRepository
from schemas.auth import RegisterRequest, LoginRequest

class AuthService:
    def __init__(self, user_repo: UserRepository, auth_handler: AuthHandler):
        self.user_repo = user_repo
        self.auth_handler = auth_handler
    
    async def register(self, request: RegisterRequest):
        # 1. 验证验证码
        # 2. 检查邮箱是否已注册
        # 3. 密码加密
        # 4. 创建用户
        # 5. 生成 Token
        pass
    
    async def login(self, request: LoginRequest):
        # 1. 验证邮箱密码
        # 2. 生成 Token
        pass
```

### 2.4 utils/ - 工具层
**职责**：提供通用工具函数和辅助类

| 文件 | 职责 |
|------|------|
| `response.py` | 统一响应格式（成功/失败响应） |
| `exceptions.py` | 异常处理工具（异常捕获、格式化） |
| `validators.py` | 数据验证工具（邮箱验证、密码强度等） |
| `helpers.py` | 通用辅助函数（时间格式化、字符串处理等） |

**示例**：
```python
# utils/response.py
from typing import Any, Optional
from pydantic import BaseModel

class APIResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None
    error: Optional[Any] = None

def success_response(data: Any = None, message: str = "success") -> APIResponse:
    return APIResponse(code=200, message=message, data=data)

def error_response(code: int, message: str, error: Any = None) -> APIResponse:
    return APIResponse(code=code, message=message, error=error)
```

### 2.5 middleware/ - 中间件层
**职责**：处理跨切面关注点（日志、限流、错误处理等）

| 文件 | 职责 |
|------|------|
| `logging.py` | 请求日志中间件（记录请求/响应） |
| `rate_limit.py` | 限流中间件（调用 core/rate_limit.py） |
| `error_handler.py` | 错误处理中间件（统一异常处理） |
| `cors.py` | CORS 中间件（跨域处理） |

**示例**：
```python
# middleware/logging.py
from fastapi import Request
from loguru import logger
import time

async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.2f}s")
    return response
```

