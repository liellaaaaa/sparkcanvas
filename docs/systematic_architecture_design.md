# SparkCanvas系统 - 系统架构设计报告

## 文档信息

| 项目名称 | SparkCanvas系统 |
|---------|------------------|
| 文档版本 | v1.0 |
| 编写日期 | 2026年 |
| 编写人员 | zyq |
| 文档类型 | 系统架构设计报告 |

## 1. 架构设计

### 1.1 架构总览

系统采用**分层架构（Layered Architecture）**设计模式，结合**模块化设计**和**微服务思想**，确保关注点分离、模块解耦和高内聚低耦合。整体架构分为五层：表现层、应用层、业务层、数据层和外部服务层。

#### 1.1.1 架构分层说明

**架构层次关系：**
```
表现层 → 应用层 → 业务层 → 数据层
                    ↓
                外部服务层
```

**各层组件明细：**

| 层次 | 组件 | 说明 |
|-----|------|------|
| **表现层** | uni-app多端应用 | Vue3组合式API |
| | PC端 | Web应用 |
| **应用层** | API网关 | 路由转发 |
| | 用户认证 | 权限控制、JWT验证 |
| **业务层** | 工作台模块 | Memory管理、对话上下文 |
| | 内容生成引擎 | LangChain编排、智能生成 |
| | 素材狩猎模块 | 联网检索+RAG知识库 |
| | 标题优化模块 | 自我反思、点击率预测 |
| | 配图生成模块 | DALL·E 3图片生成 |
| | Prompt管理模块 | 模板管理 |
| | 历史记录模块 | 草稿箱、统计分析 |
| **数据层** | MySQL | 用户/内容/Prompt数据存储 |
| | Redis | 验证码/缓存/会话存储 |
| | Chroma | 向量知识库、语义检索 |
| **外部服务层** | LLM API | OpenAI/国产大模型 |
| | DALL·E 3 | AI图片生成服务 |
| | Tavily Search | 实时联网检索 |
| | Web Scraping | 网页内容爬取 |

#### 1.1.2 架构层次说明

| 层次 | 名称 | 职责 | 技术选型 |
|-----|------|------|---------|
| **表现层** | Presentation Layer | 用户交互、界面展示 | uni-app + Vue3 + 组合式API |
| **应用层** | Application Layer | 请求路由、认证鉴权 | FastAPI + JWT + Redis |
| **业务层** | Business Layer | 核心业务逻辑、内容生成编排、智能体调度 | LangChain + Pydantic + 业务模块 |
| **数据层** | Data Layer | 数据持久化、缓存管理、向量检索 | MySQL + Redis + Chroma |
| **外部服务层** | External Services | 大模型调用、图片生成、联网搜索 | OpenAI API + Tavily + Scraping |

### 1.2 架构设计原则

#### 1.2.1 分层原则

1. **关注点分离（Separation of Concerns）**
   - 每一层只处理特定类型的任务
   - 表现层负责用户交互
   - 应用层负责请求路由、认证和流控
   - 业务层负责核心内容生成逻辑
   - 数据层负责数据持久化和向量检索

2. **依赖方向**
   - 上层依赖下层，下层不依赖上层
   - 通过接口和抽象实现层间解耦
   - 业务层不直接依赖具体的数据访问实现

3. **单一职责原则（Single Responsibility Principle）**
   - 每个模块只负责一个业务功能
   - 模块间通过明确的接口通信
   - 避免模块职责重叠和混淆

#### 1.2.2 模块化设计原则

1. **高内聚低耦合（High Cohesion, Low Coupling）**
   - 模块内部功能紧密相关
   - 模块间依赖最小化
   - 通过依赖注入（Dependency Injection）管理模块依赖

2. **接口隔离原则（Interface Segregation Principle）**
   - 定义清晰的模块接口
   - 避免接口臃肿，按需暴露功能
   - 每个模块提供独立的API端点

3. **开闭原则（Open-Closed Principle）**
   - 对扩展开放，对修改关闭
   - 通过插件机制支持功能扩展
   - 支持新增文风模板、Prompt模板、素材源

#### 1.2.3 KPI导向设计原则

1. **情绪价值优先**
   - 内容生成链路集成情绪强化模块
   - Prompt模板内置情绪点（治愈/共鸣/趣味/新鲜感）
   - 多版本生成+情绪打分筛选机制

2. **视觉质量保障**
   - 配图生成独立模块，确保≥1080P
   - 多图备选机制（≥3张）
   - 图文匹配度评估与优化

3. **标题优化机制**
   - 标题生成≥5版本
   - 自我反思打分模块
   - 点击率预测模型集成

### 1.3 核心模块详细设计

#### 1.3.1 工作台模块（Workspace Module with Memory）

**模块职责：**
- 一键式内容生产工作台
- 多轮对话与上下文记忆（Memory Management）
- 素材源选择与上传（联网/RAG/本地）
- 全流程编排与监控（联网→标题→文风→配图→输出）
- 版本迭代与重生成

**模块架构：**

**工作台模块组成：**
- **Memory管理器**
  - 短期记忆：当前对话上下文
  - 上下文压缩：优化Token使用
- **素材源路由器**
  - 联网检索：Tavily Search热点抓取
  - RAG知识库：向量检索、语义匹配
  - 本地上传：文档解析、格式转换
- **生成编排引擎**
  - 链路编排：LangChain SequentialChain
- **版本管理器**
  - 草稿保存：自动保存、手动保存
  - 版本对比：历史版本查看
  - 快速重生成：参数调整后重新生成

**技术实现要点：**
- 使用LangChain的ConversationBufferMemory管理短期记忆
- 素材源路由采用策略模式（Strategy Pattern）
- 生成链路使用LangChain的SequentialChain编排
- 支持流式输出（Server-Sent Events）实时反馈进度

**接口设计：**
```python
POST /api/v1/workspace/create-session    # 创建工作会话
POST /api/v1/workspace/send-message      # 发送消息
POST /api/v1/workspace/upload-material   # 上传素材/文档
POST /api/v1/workspace/regenerate        # 重新生成
GET  /api/v1/workspace/history           # 获取对话历史
```

#### 1.3.2 内容生成引擎（Content Generation Engine）

**模块职责：**
- 标题智能优化（3版本+自我反思）
- 文风模仿与情绪强化
- 结构化内容生成（爆款三段式）
- 输出解析与格式适配

**模块架构：**

**内容生成引擎组成：**
- **标题优化器**
  - 多版本生成：3个标题候选
  - 自我反思打分：点击率预测模型
  - 最优筛选：自动选择最佳标题
- **文风模仿器**
  - 大V文风库：RAG检索相似风格
  - Few-Shot学习：示例驱动风格迁移
  - 风格迁移：保持一致性
- **情绪强化器**
  - 情绪点注入：治愈/共鸣/趣味/新鲜感
  - 情绪强度控制：可调节情绪浓度
  - 情绪打分：量化评估情绪价值
- **结构生成器**
  - 吸睛开头：第一段吸引注意力
  - 价值传递：核心内容输出
  - 互动引导：结尾引导用户互动
- **输出解析器**
  - JSON结构化：标准化数据格式
  - Markdown格式：富文本展示
  - 平台适配：小红书/抖音格式转换

**技术实现要点：**
- 标题优化采用LLM自我反思（Self-Reflection）机制
- 文风模仿使用RAG技术，检索大V文风库
- 情绪强化通过Prompt Engineering实现
- 结构生成使用CoT（Chain of Thought）技术
- 输出解析使用Pydantic进行结构化数据验证

**核心Chain设计：**
```python
# 标题优化链
TitleGenerationChain -> TitleScoringChain -> TitleSelectionChain

# 内容生成链
StyleRetrievalChain -> EmotionEnhancementChain -> StructureGenerationChain -> OutputParsingChain
```


#### 1.3.3 配图生成模块（Image Generation Module）

**模块职责：**
- AI图片生成（DALL·E 3）
- 图文匹配度优化
- 多图备选机制（≥3张）
- 平台格式适配（小红书/抖音封面）

**模块架构：**

**配图生成模块组成：**
- **Prompt构建器**
  - 内容分析：提取视觉元素、关键词
  - 风格定义：小红书/抖音视觉风格
  - Prompt优化：生成高质量图片描述
- **图片生成器**
  - DALL·E 3 API：调用OpenAI图片生成
  - 批量生成：≥3张备选图片
  - 异步处理：提升生成效率
- **质量评估器**
  - 分辨率检测：确保≥1080P
  - 图文匹配度：CLIP模型评估≥85%
  - 风格统一度：视觉风格一致性≥90%
- **格式适配器**
  - 尺寸裁剪：适配平台封面尺寸
  - 格式转换：JPG/PNG格式转换
  - 压缩优化：文件大小优化

**技术实现要点：**
- 使用OpenAI DALL·E 3 API生成图片
- Prompt构建采用模板+内容分析混合方案
- 图文匹配度使用CLIP模型评估
- 支持异步批量生成，提升效率
- 图片存储使用OSS（阿里云）

**接口设计：**
```python
POST /api/v1/image/generate           # 生成配图
POST /api/v1/image/batch-generate     # 批量生成（≥3张）
GET  /api/v1/image/download           # 下载图片
```

#### 1.3.5 RAG知识库模块（RAG Knowledge Base Module）

**模块职责：**
- 多格式文档上传与解析
- 智能分块与向量化
- 语义检索与相似度排序
- 容量与成本监控

**模块架构：**

**RAG知识库模块组成：**
- **文档处理器**
  - 格式解析：支持PDF/Word/Txt等格式
  - 智能分块：RecursiveCharacterTextSplitter分块
  - 元数据提取：文档标题、作者等信息
- **向量化引擎**
  - Embedding生成：OpenAI API或本地模型
  - 向量存储：Chroma持久化存储
  - 索引优化：提升检索性能
- **检索服务**
  - 语义检索：向量相似度检索
  - 相似度排序：Top-K结果排序
  - 上下文拼接：检索结果上下文组装
- **监控中心**
  - 存储容量：向量库容量监控
  - API调用统计：Embedding调用次数统计
  - 成本监控：API调用成本追踪

**技术实现要点：**
- 使用LangChain的DocumentLoaders解析多格式文档
- 文本分块使用RecursiveCharacterTextSplitter
- Embedding使用OpenAI API
- 向量存储使用Chroma，支持持久化
- 检索使用相似度

**接口设计：**
```python
POST /api/v1/rag/upload               # 上传文档
POST /api/v1/rag/delete               # 删除文档
POST /api/v1/rag/search               # 语义检索
GET  /api/v1/rag/list                 # 文档列表
GET  /api/v1/rag/stats                # 容量统计
```

#### 1.3.6 Prompt管理模块（Prompt Management Module）

**模块职责：**
- 预设/自定义Prompt管理
- 快速测试与评分反馈
- 版本管理与回滚
- 模板分类（文风/情绪/结构）

**模块架构：**

**Prompt管理模块组成：**
- **模板管理器**
  - CRUD操作：创建/读取/更新/删除

**技术实现要点：**
- Prompt模板存储在MySQL（prompt表）

**接口设计：**
```python
POST /api/v1/prompt/create            # 创建Prompt
PUT  /api/v1/prompt/update            # 更新Prompt
DELETE /api/v1/prompt/delete          # 删除Prompt
GET  /api/v1/prompt/list              # 查询Prompt列表
```

#### 1.3.7 历史记录模块（History Module）

**模块职责：**
- 草稿/已发布内容管理
- 对话历史集中管理

**模块架构：**

**历史记录模块组成：**
- **内容管理器**
  - 草稿箱：未发布内容管理
  - 已发布：已发布内容归档
- **对话历史**
  - 会话记录：会话列表管理
  - 消息历史：对话消息记录
- **搜索引擎**
  - 关键词搜索：全文检索
  - 时间范围：按时间筛选

**技术实现要点：**
- 内容记录存储在MySQL（contents表）
- 对话历史短期存储在Redis（TTL 7天）
- 搜索引擎支持全文检索（MySQL FULLTEXT）

**接口设计：**
```python
GET  /api/v1/history/contents         # 查询内容历史
GET  /api/v1/history/conversations    # 查询对话历史
GET  /api/v1/history/search           # 关键词搜索
```

#### 1.3.8 登录注册模块（Authentication Module）

**模块职责：**
- 邮箱注册登录
- 验证码校验（邮箱）
- JWT令牌管理

**模块架构：**

**登录注册模块组成：**
- **注册服务**
  - 信息校验：邮箱验证
  - 密码加密：bcrypt哈希加密
  - 用户创建：写入MySQL users表
- **登录服务**
  - 凭证验证：邮箱+密码验证
  - JWT生成：生成Access Token
- **验证码服务**
  - 验证码生成：4位数字验证码
  - Redis存储：TTL 5分钟自动过期
  - 邮件发送：发送验证码到用户
- **Token管理**
  - Token签发：生成JWT令牌
  - Token验证：验证令牌有效性

**技术实现要点：**
- 密码使用bcrypt加密存储
- 验证码存储在Redis（TTL 5分钟）
- JWT使用FastAPI的依赖注入实现鉴权

**接口设计：**
```python
POST /api/v1/auth/send-code           # 发送验证码
POST /api/v1/auth/register            # 注册
POST /api/v1/auth/login               # 登录
POST /api/v1/auth/logout              # 登出
```

#### 1.3.9 路由模块（Router Module）

**模块职责：**
- 统一前后端路由与API分发
- 动态配置与权限拦截

**模块架构：**

**路由模块组成：**
- **API网关**
  - 路由分发：请求路由到对应模块
  - 协议转换：HTTP/WebSocket协议转换
  - 负载均衡：多实例负载均衡（未来扩展）
- **权限拦截器**
  - Token验证：JWT令牌验证

**技术实现要点：**
- 使用FastAPI的APIRouter进行模块化路由

### 1.4 数据流设计

#### 1.4.1 内容生产全流程数据流

**流程步骤：**

1. **用户发起创作请求** → 工作台模块（Memory管理）

2. **素材源选择**：
   - 联网检索 → Tavily Search热点抓取
   - RAG检索 → Chroma向量库语义检索

3. **素材汇总与拼接** → 合并所有素材源内容

4. **内容生成引擎处理**：
   - 标题优化器：3版本生成 → 自我反思打分（点击率预测≥90分）
   - 文风模仿器：RAG大V文风检索
   - 情绪强化器：情绪点注入（治愈/共鸣/趣味）

5. **结构化生成**：爆款三段式（吸睛开头-价值传递-互动引导）

6. **输出解析**：JSON/Markdown格式转换

7. **配图生成**：
   - DALL·E 3 API批量生成3张
   - 质量评估（分辨率≥1080P、图文匹配度≥85%）

8. **平台适配**：小红书/抖音格式转换

9. **内容存储**：MySQL contents表持久化

10. **前端展示**：预览与编辑

11. **用户操作分支**：
    - 满意 → 发布/下载
    - 修改 → 调整参数，重新生成（回到步骤1）
    - 保存 → 草稿箱（存储到MySQL）

#### 1.4.2 RAG知识库检索数据流

**文档上传流程：**
1. 用户上传文档 → 文档处理器（格式解析：PDF/Word/Txt）
2. 智能分块 → RecursiveCharacterTextSplitter分块处理
3. Embedding生成 → OpenAI API向量化
4. 向量存储 → Chroma持久化存储

**RAG检索流程：**
1. 用户发起RAG检索 → 查询向量化（Embedding生成）
2. Chroma语义检索 → 相似度排序（Top-K结果）
3. 上下文拼接 → 组装检索结果上下文
4. 返回工作台 → 供内容生成引擎使用

#### 1.4.3 用户认证数据流

**用户注册流程：**
1. 用户注册请求 → 发送验证码
2. Redis存储验证码（TTL 5分钟）
3. 邮件发送验证码
4. 用户输入验证码 → 验证码校验
   - 失败 → 返回错误提示
   - 成功 → 密码bcrypt加密 → MySQL users表存储用户信息

**用户登录流程：**
1. 用户登录请求 → 凭证验证（邮箱+密码）
2. 验证结果判断：
   - 失败 → 返回错误信息
   - 成功 → 生成JWT Token（Access Token）
3. 返回Token给前端 → 前端存储Token，后续请求携带Token


### 1.5 技术架构图

#### 1.5.1 系统技术栈全景图

**技术栈层次关系：**
```
前端技术栈 → 后端技术栈 → 数据存储
                    ↓
                外部服务
```

**技术栈明细：**

| 层次 | 技术组件 | 说明 |
|-----|---------|------|
| **前端技术栈** | uni-app | PC端 |
| | Vue3 | 组合式API、响应式系统 |
| | Pinia | 状态管理 |
| | uni-ui | 组件库 |
| **后端技术栈** | FastAPI | 异步Web框架 |
| | LangChain | 智能体框架、LLM编排 |
| | Pydantic | 数据校验、类型验证 |
| | SQLAlchemy | 异步ORM、数据库操作 |
| **数据存储** | MySQL | 关系数据库（用户/内容/Prompt） |
| | Redis | 缓存/验证码/会话存储 |
| | Chroma | 向量数据库（RAG知识库） |
| **外部服务** | OpenAI API | LLM+DALL·E 3图片生成 |
| | Tavily Search | 实时联网检索 |
| | Web Scraping | 网页内容爬取 |

## 2. 技术选型

### 2.1 技术选型原则

1. **成熟稳定**：选择经过生产环境验证的技术
2. **社区活跃**：选择有活跃社区支持的技术
3. **性能优先**：优先考虑高性能的技术方案
4. **开发效率**：平衡开发效率和运行性能
5. **学习成本**：考虑团队技术栈和学习成本
6. **生态完整**：选择生态完善、工具链丰富的技术
7. **KPI导向**：技术选型需支撑三大核心KPI（情绪价值、配图质量、标题点击率）

### 2.2 前端技术栈

#### 2.2.1 前端框架

| 技术 | 版本 | 选型理由 | 应用场景 |
|-----|------|---------|---------|
| **uni-app** | 最新版 | 1. 一次开发多端部署（PC/H5/小程序）<br>2. Vue生态，学习成本低<br>3. 丰富的插件市场<br>4. 官方文档完善，中文友好 | PC端应用开发 |
| **Vue3** | 3.x | 1. 组合式API，逻辑复用性强<br>2. 响应式系统性能优异<br>3. TypeScript支持好<br>4. 生态丰富（Vue Router、Pinia等） | 前端应用开发 |

**关键特性：**
- 组合式API：更好的逻辑复用和类型推导
- 响应式系统：基于Proxy的响应式系统
- 组件化：单文件组件（SFC）支持
- 性能优化：编译时优化，运行时性能好

#### 2.2.2 状态管理

| 技术 | 版本 | 选型理由 | 应用场景 |
|-----|------|---------|---------|
| **Pinia** | 最新版 | 1. Vue 3官方推荐的状态管理<br>2. TypeScript支持好<br>3. 轻量级，API简洁<br>4. 支持DevTools | 全局状态管理（用户信息、会话状态等） |

#### 2.2.3 UI组件库

| 技术 | 版本 | 选型理由 | 应用场景 |
|-----|------|---------|---------|
| **uni-ui** | 最新版 | 1. uni-app官方组件库<br>2. 组件丰富，文档完善<br>3. 多端适配<br>4. 开箱即用 | UI组件（表单、列表、对话框等） |

### 2.3 后端技术栈

#### 2.3.1 Web框架

| 技术 | 版本 | 选型理由 | 应用场景 |
|-----|------|---------|---------|
| **FastAPI** | 0.100+ | 1. 基于Starlette和Pydantic，性能优异<br>2. 原生支持异步编程（async/await）<br>3. 自动生成OpenAPI/Swagger文档<br>4. 类型提示支持，开发体验好<br>5. 依赖注入系统完善 | 所有HTTP API接口 |

**关键特性：**
- 异步支持：基于ASGI，支持高并发
- 自动文档：自动生成交互式API文档
- 数据验证：基于Pydantic的自动数据验证
- 类型安全：完整的类型提示支持

#### 2.3.2 数据库ORM

| 技术 | 版本 | 选型理由 | 应用场景 |
|-----|------|---------|---------|
| **SQLAlchemy** | 2.0+ | 1. Python最成熟的ORM框架<br>2. 支持异步操作（AsyncIO）<br>3. 灵活的查询构建器<br>4. 完善的迁移工具（Alembic）<br>5. 支持多种数据库 | 数据库访问层 |

**关键特性：**
- 异步支持：SQLAlchemy 2.0原生支持async/await
- 查询构建：强大的查询API
- 关系映射：完善的关系映射支持
- 迁移管理：Alembic数据库迁移工具

#### 2.3.3 数据库

| 技术 | 版本 | 选型理由 | 应用场景 |
|-----|------|---------|---------|
| **MySQL** | 8.0+ | 1. 成熟稳定，生产环境广泛使用<br>2. 完善的ACID事务支持<br>3. 丰富的索引类型<br>4. 良好的性能表现<br>5. 社区活跃，文档完善 | 主数据库（用户/内容/Prompt） |
| **Redis** | 6.0+ | 1. 高性能内存数据库<br>2. 丰富的数据结构（String、Hash、List、Set、Sorted Set）<br>3. 支持持久化（RDB、AOF）<br>4. 支持集群模式<br>5. 完善的过期策略 | 验证码存储、会话缓存 |
| **Chroma** | 最新版 | 1. 轻量级向量数据库<br>2. 本地部署，无需付费<br>3. 与LangChain集成好<br>4. 支持持久化存储<br>5. 简单易用 | RAG知识库向量存储 |

**MySQL应用场景：**
- 用户信息存储（users表）
- 内容记录存储（contents表）
- Prompt模板存储（prompt表）

**Redis应用场景：**
- 邮箱验证码存储（TTL 5分钟）
- 用户会话缓存（TTL 30分钟）
- 热点数据缓存

**Chroma应用场景：**
- RAG知识库向量化存储
- 大V文风库向量检索
- 语义相似度搜索

#### 2.3.4 AI/ML框架

| 技术 | 版本 | 选型理由 | 应用场景 |
|-----|------|---------|---------|
| **LangChain** | 1.0+ | 1. 简化LLM应用开发<br>2. 丰富的工具链和集成<br>3. 支持多种LLM提供商<br>4. 链式调用（Chain）支持<br>5. 记忆（Memory）管理完善<br>6. 支持RAG、Agents等高级功能 | 对话管理、内容生成编排、RAG检索 |

**关键特性：**
- 链式调用：支持复杂的生成流程编排
- 记忆管理：短期记忆和长期记忆支持
- 工具集成：支持外部工具调用（Tavily Search等）
- 提示工程：灵活的提示模板管理
- RAG支持：向量检索与上下文增强

#### 2.3.5 数据校验框架

| 技术 | 版本 | 选型理由 | 应用场景 |
|-----|------|---------|---------|
| **Pydantic** | 2.0+ | 1. 基于Python类型提示的数据验证<br>2. 自动生成JSON Schema<br>3. 性能优异<br>4. 与FastAPI深度集成<br>5. 支持复杂数据模型 | 请求/响应数据验证、数据模型定义 |

**关键特性：**
- 类型验证：基于Python类型提示
- 自动转换：自动类型转换和验证
- JSON Schema：自动生成OpenAPI Schema
- 性能优化：使用Rust实现核心验证逻辑

#### 2.3.6 HTTP客户端

| 技术 | 版本 | 选型理由 | 应用场景 |
|-----|------|---------|---------|
| **httpx** | 最新版 | 1. 异步HTTP客户端<br>2. 支持HTTP/1.1和HTTP/2<br>3. 自动连接池管理<br>4. 超时和重试支持<br>5. 与FastAPI生态兼容 | 调用外部API（OpenAI、Tavily Search等） |

**关键特性：**
- 异步支持：原生async/await支持
- 连接复用：自动连接池管理
- 超时控制：灵活的超时配置
- 重试机制：支持自动重试

#### 2.3.7 数据库迁移工具

| 技术 | 版本 | 选型理由 | 应用场景 |
|-----|------|---------|---------|
| **Alembic** | 最新版 | 1. SQLAlchemy官方迁移工具<br>2. 版本控制支持<br>3. 支持回滚<br>4. 团队协作友好 | 数据库版本管理和迁移 |

### 2.4 外部服务依赖

#### 2.4.1 大模型平台

| 服务 | 说明 | 应用场景 |
|-----|------|---------|
| **OpenAI API** | 提供大语言模型和图片生成服务 | 内容生成、标题优化、图片生成（DALL·E 3） |

**关键特性：**
- GPT-4/GPT-3.5：高质量文本生成
- DALL·E 3：高质量图片生成
- Embedding API：文本向量化
- API稳定，文档完善

#### 2.4.2 联网检索服务

| 服务 | 说明 | 应用场景 |
|-----|------|---------|
| **Tavily Search** | 实时热点搜索API | 素材狩猎模块的联网检索 |

**关键特性：**
- 实时热点抓取
- 搜索结果质量高
- API简单易用
- 支持LangChain集成

#### 2.4.3 网页爬取

| 技术 | 说明 | 应用场景 |
|-----|------|---------|
| **BeautifulSoup** | HTML解析库 | 网页内容提取 |
| **Playwright** | 浏览器自动化 | 动态网页爬取（可选） |

### 2.5 开发工具链

#### 2.5.1 代码质量

| 技术 | 版本 | 选型理由 | 应用场景 |
|-----|------|---------|---------|
| **black** | 最新版 | 1. Python代码格式化<br>2. 零配置，开箱即用<br>3. 风格统一 | 代码格式化 |
| **flake8** | 最新版 | 1. Python代码检查<br>2. 风格检查<br>3. 错误检测 | 代码检查 |
| **mypy** | 最新版 | 1. 静态类型检查<br>2. 类型安全<br>3. 与FastAPI配合好 | 类型检查 |

#### 2.5.2 测试框架

| 技术 | 版本 | 选型理由 | 应用场景 |
|-----|------|---------|---------|
| **pytest** | 最新版 | 1. Python主流测试框架<br>2. 丰富的插件生态<br>3. 异步测试支持<br>4. 参数化测试 | 后端单元测试、集成测试 |
| **pytest-asyncio** | 最新版 | 1. pytest异步测试支持<br>2. 与FastAPI配合好 | 异步代码测试 |
| **httpx** | 最新版 | 1. 异步HTTP客户端<br>2. 测试客户端支持 | API测试 |

### 2.6 部署与运维

#### 2.6.1 容器化

| 技术 | 版本 | 选型理由 | 应用场景 |
|-----|------|---------|---------|
| **Docker** | 最新版 | 1. 容器化标准<br>2. 环境一致性<br>3. 易于部署 | 应用容器化 |
| **Docker Compose** | 最新版 | 1. 多容器编排<br>2. 开发环境友好<br>3. 配置简单 | 本地开发环境、单机部署 |

#### 2.6.2 Web服务器

| 技术 | 版本 | 选型理由 | 应用场景 |
|-----|------|---------|---------|
| **Uvicorn** | 最新版 | 1. ASGI服务器<br>2. 高性能<br>3. 与FastAPI配合好<br>4. 支持HTTP/2 | FastAPI应用服务器 |

#### 2.6.3 反向代理（可选）

| 技术 | 版本 | 选型理由 | 应用场景 |
|-----|------|---------|---------|
| **Nginx** | 最新版 | 1. 高性能反向代理<br>2. 负载均衡<br>3. SSL终止<br>4. 静态文件服务 | 生产环境反向代理、负载均衡（未来扩展） |

### 2.7 日志与监控

#### 2.7.1 日志

| 技术 | 版本 | 选型理由 | 应用场景 |
|-----|------|---------|---------|
| **loguru** | 最新版 | 1. Python日志库<br>2. 简单易用<br>3. 结构化日志支持<br>4. 自动日志轮转 | 应用日志记录 |

### 2.8 技术选型总结

#### 2.8.1 技术栈全景图

**技术栈层次关系：**
```
前端技术栈（uni-app + Vue3 + Pinia）
    ↓
后端技术栈（FastAPI + LangChain + SQLAlchemy）
    ↓
数据存储（MySQL + Redis + Chroma）
    ↓
外部服务（OpenAI API + Tavily Search）
```

#### 2.8.2 技术选型优势

1. **性能优势**
   - FastAPI异步框架，支持高并发
   - Redis缓存提升响应速度
   - LangChain异步支持，提升生成效率

2. **开发效率**
   - FastAPI自动文档生成
   - Vue3 Composition API提升代码复用
   - LangChain简化LLM应用开发
   - Alembic简化数据库迁移

3. **可维护性**
   - 类型提示支持，减少错误
   - 模块化设计，易于维护
   - 完善的测试工具链

4. **可扩展性**
   - 模块化设计，支持功能扩展
   - 插件机制支持新增功能
   - 支持水平扩展

5. **KPI支撑**
   - LangChain支持复杂的情绪强化和标题优化流程
   - DALL·E 3保障配图质量
   - RAG技术支撑大V文风模仿

#### 2.8.3 技术风险与应对

| 风险 | 应对策略 |
|-----|---------|
| 新技术学习成本 | 提供技术培训和文档，代码评审 |
| 第三方服务依赖 | 实现降级策略，监控服务状态 |
| 性能瓶颈 | 性能测试，优化热点代码，缓存策略 |
| 安全漏洞 | 定期更新依赖，安全扫描，代码审计 |
| API调用成本 | 实现缓存机制，优化调用频率，成本监控 |

## 3. 数据库设计

### 3.1 数据库选型

#### 3.1.1 主数据库

| 数据库 | 版本 | 选型理由 | 应用场景 |
|-------|------|---------|---------|
| **MySQL** | 8.0+ | 1. 成熟稳定，生产环境广泛使用<br>2. 完善的ACID事务支持<br>3. 丰富的索引类型<br>4. 良好的性能表现<br>5. 社区活跃，文档完善 | 用户信息、内容记录、Prompt模板持久化存储 |

#### 3.1.2 缓存数据库

| 数据库 | 版本 | 选型理由 | 应用场景 |
|-------|------|---------|---------|
| **Redis** | 6.0+ | 1. 高性能内存数据库<br>2. 支持过期策略（TTL）<br>3. 丰富的数据结构<br>4. 支持持久化（RDB、AOF） | 验证码存储、会话缓存 |

#### 3.1.3 向量数据库

| 数据库 | 版本 | 选型理由 | 应用场景 |
|-------|------|---------|---------|
| **Chroma** | 最新版 | 1. 轻量级向量数据库<br>2. 本地部署，无需付费<br>3. 与LangChain集成好<br>4. 支持持久化存储<br>5. 简单易用 | RAG知识库向量存储、语义检索 |

### 3.2 数据库命名规范

#### 3.2.1 数据库命名

- **数据库名称：** `sparkcanvas`
- **命名规范：** 小写字母，单词完整，语义清晰

#### 3.2.2 表命名规范

- **表名：** 小写字母，单数形式，语义清晰
- **示例：** `users`（用户表）、`contents`（内容表）、`prompt`（Prompt表）

#### 3.2.3 字段命名规范

- **字段名：** 小写字母，单词间使用下划线分隔
- **主键：** 统一使用 `id`，类型为 `INT`，自增
- **外键：** 使用 `表名_id` 格式，如 `user_id`
- **命名示例：** `password_hash`、`generated_at`、`user_id`

### 3.3 核心数据表设计

#### 3.3.1 用户表 (users)

**表说明：**
存储用户注册和登录信息。

**表结构：**

| 字段名 | 数据类型 | 约束 | 说明 |
|-------|---------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT, NOT NULL | 主键ID |
| username | VARCHAR(100) | NOT NULL | 用户名 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 邮箱（唯一） |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希（bcrypt加密） |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

**表创建SQL：**

```sql
CREATE DATABASE IF NOT EXISTS sparkcanvas;

USE sparkcanvas;

CREATE TABLE IF NOT EXISTS users
(
    id            INT          PRIMARY KEY AUTO_INCREMENT NOT NULL COMMENT '主键ID',
    username      VARCHAR(100) NOT NULL COMMENT '用户名',
    email         VARCHAR(255) UNIQUE NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    created_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

**字段说明：**

1. **id（主键）**
   - 类型：`INT`
   - 约束：主键、自增、非空
   - 说明：唯一标识每个用户

2. **username（用户名）**
   - 类型：`VARCHAR(100)`
   - 约束：非空
   - 说明：用户显示名称

3. **email（邮箱）**
   - 类型：`VARCHAR(255)`
   - 约束：唯一、非空
   - 说明：用户登录邮箱，用于注册和登录

4. **password_hash（密码哈希）**
   - 类型：`VARCHAR(255)`
   - 约束：非空
   - 说明：使用bcrypt加密后的密码哈希值

5. **created_at（创建时间）**
   - 类型：`TIMESTAMP`
   - 约束：默认当前时间
   - 说明：用户注册时间

6. **updated_at（更新时间）**
   - 类型：`TIMESTAMP`
   - 约束：自动更新
   - 说明：用户信息最后更新时间

#### 3.3.2 Prompt表 (prompt)

**表说明：**
存储用户创建和管理的Prompt模板。

**表结构：**

| 字段名 | 数据类型 | 约束 | 说明 |
|-------|---------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT, NOT NULL | 主键ID |
| name | VARCHAR(255) | NOT NULL | 模板名称 |
| content | TEXT | NOT NULL | Prompt内容 |
| user_id | INT | NOT NULL, FOREIGN KEY | 创建者用户ID |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

**表创建SQL：**

```sql
CREATE TABLE IF NOT EXISTS prompt
(
    id         INT          PRIMARY KEY AUTO_INCREMENT NOT NULL COMMENT '主键ID',
    name       VARCHAR(255) NOT NULL COMMENT '模板名称',
    content    TEXT         NOT NULL COMMENT 'Prompt内容',
    user_id    INT          NOT NULL COMMENT '创建者用户ID',
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Prompt模板表';
```

**字段说明：**

1. **id（主键）**
   - 类型：`INT`
   - 约束：主键、自增、非空
   - 说明：唯一标识每个Prompt模板

2. **name（模板名称）**
   - 类型：`VARCHAR(255)`
   - 约束：非空
   - 说明：Prompt模板的名称，便于用户识别

3. **content（Prompt内容）**
   - 类型：`TEXT`
   - 约束：非空
   - 说明：Prompt模板的完整内容

4. **user_id（创建者）**
   - 类型：`INT`
   - 约束：非空、外键
   - 说明：创建该Prompt模板的用户ID，关联users表

5. **created_at（创建时间）**
   - 类型：`TIMESTAMP`
   - 约束：默认当前时间
   - 说明：Prompt模板创建时间

6. **updated_at（更新时间）**
   - 类型：`TIMESTAMP`
   - 约束：自动更新
   - 说明：Prompt模板最后更新时间

#### 3.3.3 内容记录表 (contents)

**表说明：**
存储用户生成的内容记录（草稿和已发布内容）。

**表结构：**

| 字段名 | 数据类型 | 约束 | 说明 |
|-------|---------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT, NOT NULL | 主键ID |
| user_id | INT | NOT NULL, FOREIGN KEY | 用户ID |
| platform | ENUM('xiaohongshu','douyin') | NOT NULL | 目标平台 |
| title | VARCHAR(500) | NOT NULL | 标题 |
| body | TEXT | NOT NULL | 正文内容 |
| image_url | VARCHAR(500) | NULL | 配图URL（OSS存储） |
| status | ENUM('draft','published') | DEFAULT 'draft' | 状态（草稿/已发布） |
| generated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 生成时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

**表创建SQL：**

```sql
CREATE TABLE IF NOT EXISTS contents
(
    id           INT                              PRIMARY KEY AUTO_INCREMENT NOT NULL COMMENT '主键ID',
    user_id      INT                              NOT NULL COMMENT '用户ID',
    platform     ENUM('xiaohongshu','douyin')    NOT NULL COMMENT '目标平台',
    title        VARCHAR(500)                      NOT NULL COMMENT '标题',
    body         TEXT                              NOT NULL COMMENT '正文内容',
    image_url    VARCHAR(500)                     NULL COMMENT '配图URL',
    status       ENUM('draft','published')        DEFAULT 'draft' COMMENT '状态',
    generated_at TIMESTAMP                         DEFAULT CURRENT_TIMESTAMP COMMENT '生成时间',
    updated_at   TIMESTAMP                         DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='内容记录表';
```

**字段说明：**

1. **id（主键）**
   - 类型：`INT`
   - 约束：主键、自增、非空
   - 说明：唯一标识每条内容记录

2. **user_id（用户ID）**
   - 类型：`INT`
   - 约束：非空、外键
   - 说明：创建该内容的用户ID，关联users表

3. **platform（目标平台）**
   - 类型：`ENUM('xiaohongshu','douyin')`
   - 约束：非空
   - 说明：内容目标发布平台（小红书/抖音）

4. **title（标题）**
   - 类型：`VARCHAR(500)`
   - 约束：非空
   - 说明：生成的内容标题

5. **body（正文内容）**
   - 类型：`TEXT`
   - 约束：非空
   - 说明：生成的内容正文

6. **image_url（配图URL）**
   - 类型：`VARCHAR(500)`
   - 约束：可为空
   - 说明：配图在OSS中的URL地址

7. **status（状态）**
   - 类型：`ENUM('draft','published')`
   - 约束：默认'draft'
   - 说明：内容状态（草稿/已发布）

8. **generated_at（生成时间）**
   - 类型：`TIMESTAMP`
   - 约束：默认当前时间
   - 说明：内容生成时间

9. **updated_at（更新时间）**
   - 类型：`TIMESTAMP`
   - 约束：自动更新
   - 说明：内容最后更新时间

### 3.4 索引设计

#### 3.4.1 索引设计原则

1. **主键索引**
   - 所有表自动创建主键索引：`PRIMARY KEY (id)`

2. **查询优化索引**
   - 根据业务查询需求创建合适的索引
   - 避免过度索引，影响写入性能
   - 优先为外键和常用查询字段创建索引

#### 3.4.2 索引设计

**主要索引：**

| 索引名称 | 表名 | 索引字段 | 索引类型 | 说明 |
|---------|------|---------|---------|------|
| PRIMARY | users | id | PRIMARY KEY | 主键索引，自动创建 |
| uk_email | users | email | UNIQUE | 邮箱唯一索引，自动创建 |
| PRIMARY | prompt | id | PRIMARY KEY | 主键索引，自动创建 |
| idx_user_id | prompt | user_id | INDEX | 用户ID索引，用于查询用户的Prompt |
| PRIMARY | contents | id | PRIMARY KEY | 主键索引，自动创建 |
| idx_user_id | contents | user_id | INDEX | 用户ID索引，用于查询用户的内容 |
| idx_platform | contents | platform | INDEX | 平台索引，用于按平台筛选 |
| idx_status | contents | status | INDEX | 状态索引，用于查询草稿/已发布 |
| idx_generated_at | contents | generated_at | INDEX | 生成时间索引，用于时间范围查询 |

**索引创建SQL：**

```sql
-- prompt表索引
CREATE INDEX idx_user_id ON prompt(user_id);

-- contents表索引
CREATE INDEX idx_user_id ON contents(user_id);
CREATE INDEX idx_platform ON contents(platform);
CREATE INDEX idx_status ON contents(status);
CREATE INDEX idx_generated_at ON contents(generated_at);
```

**索引使用场景：**

1. **主键索引（id）**
   - 场景：根据ID查询单条记录
   - 性能：O(log n) 查询复杂度

2. **邮箱唯一索引（email）**
   - 场景：用户登录时根据邮箱查询
   - 性能：O(log n) 查询复杂度，保证唯一性

3. **用户ID索引（user_id）**
   - 场景：查询用户的所有Prompt或内容
   - 性能：提升查询速度，避免全表扫描

4. **平台索引（platform）**
   - 场景：按平台筛选内容
   - 性能：提升筛选速度

5. **状态索引（status）**
   - 场景：查询草稿箱或已发布内容
   - 性能：提升状态筛选速度

6. **生成时间索引（generated_at）**
   - 场景：按时间范围查询内容
   - 性能：提升时间范围查询速度

### 3.5 数据存储设计

#### 3.5.1 MySQL数据存储

**存储内容：**
- 用户信息（users表）
- Prompt模板（prompt表）
- 内容记录（contents表）

**存储策略：**
- 所有业务数据持久化存储
- 支持事务操作，保证数据一致性
- 定期备份，确保数据安全
- 使用InnoDB引擎，支持外键约束

#### 3.5.2 Redis数据存储

**存储内容：**
- 邮箱验证码
- 用户会话缓存

**存储策略：**

| 存储Key | 数据类型 | TTL | 说明 |
|---------|---------|-----|------|
| `verify_code:{email}` | String | 5分钟 | 邮箱验证码 |
| `session:{session_id}` | Hash | 30分钟 | 用户会话信息 |

**验证码存储结构：**
```
Key: verify_code:user@example.com
Value: 1234
TTL: 300秒（5分钟）
```

**会话存储结构（示例）：**
```json
{
  "session_id": "uuid-string",
  "user_id": 1,
  "created_at": "2026-01-01T10:00:00",
  "expires_at": "2026-01-01T10:30:00"
}
```

**会话记录管理：**
- 会话创建时设置TTL为30分钟
- 每次交互更新TTL，保持会话活跃
- 会话过期后自动删除

#### 3.5.3 Chroma向量数据库存储

**存储内容：**
- RAG知识库文档向量化结果
- 大V文风库向量数据

**存储策略：**
- 使用Chroma持久化存储
- 每个文档分块后生成Embedding向量
- 支持语义检索和相似度排序
- 向量维度：1536（OpenAI text-embedding-ada-002）

**向量存储结构：**
```
Collection: knowledge_base
Documents: 文档分块文本
Embeddings: 1536维向量
Metadata: 文档ID、用户ID、创建时间等
```

### 3.6 数据关系设计

#### 3.6.1 表关系说明

**表关系图：**
```
users (1) ──< (N) prompt
users (1) ──< (N) contents
```

**关系说明：**
- **users 与 prompt：** 一对多关系，一个用户可以创建多个Prompt模板
- **users 与 contents：** 一对多关系，一个用户可以生成多条内容记录

#### 3.6.2 数据流向

**用户注册/登录流程：**
```
用户注册/登录 → 验证码服务（Redis） → 用户信息存储（MySQL users表）
```

**内容生成流程：**
```
内容生成 → 内容存储（MySQL contents表） → 配图存储（OSS） → 内容记录更新
```

**RAG知识库流程：**
```
文档上传 → 文档解析 → Embedding生成 → Chroma向量存储 → 语义检索
```

### 3.7 数据安全设计

#### 3.7.1 数据加密

1. **传输加密**
   - 数据库连接使用SSL/TLS加密
   - 应用与数据库通信加密传输

2. **敏感信息保护**
   - 密码使用bcrypt加密存储（password_hash字段）
   - 邮箱等敏感信息在日志中脱敏处理
   - 数据库访问权限控制

#### 3.7.2 数据备份

1. **备份策略**
   - MySQL：定期全量备份（每日）+ 增量备份（每小时）
   - Redis：RDB快照备份（每日）+ AOF持久化
   - Chroma：向量库文件定期备份
   - 备份文件加密存储

2. **恢复策略**
   - 支持时间点恢复
   - 定期恢复演练
   - 备份文件异地存储

#### 3.7.3 数据访问控制

1. **数据库用户权限**
   - 应用使用专用数据库用户
   - 最小权限原则（只授予必要的SELECT、INSERT、UPDATE、DELETE权限）
   - 禁止直接操作生产数据库

2. **SQL注入防护**
   - 使用ORM框架（SQLAlchemy）防止SQL注入
   - 参数化查询
   - 输入验证和过滤

3. **数据脱敏**
   - 日志中隐藏敏感信息（密码、邮箱等）
   - 查询结果脱敏处理

### 3.8 数据迁移设计

#### 3.8.1 数据库初始化

**初始化步骤：**

1. 创建数据库
   ```sql
   CREATE DATABASE IF NOT EXISTS sparkcanvas;
   ```

2. 创建数据表
   ```sql
   USE sparkcanvas;
   CREATE TABLE IF NOT EXISTS users (...);
   CREATE TABLE IF NOT EXISTS prompt (...);
   CREATE TABLE IF NOT EXISTS contents (...);
   ```

3. 创建索引
   ```sql
   CREATE INDEX idx_user_id ON prompt(user_id);
   CREATE INDEX idx_user_id ON contents(user_id);
   CREATE INDEX idx_platform ON contents(platform);
   CREATE INDEX idx_status ON contents(status);
   CREATE INDEX idx_generated_at ON contents(generated_at);
   ```

#### 3.8.2 数据库迁移工具

- **工具：** Alembic（SQLAlchemy迁移工具）
- **用途：** 数据库版本管理和迁移
- **优势：** 版本控制、回滚支持、团队协作

**迁移流程：**
1. 使用SQLAlchemy定义数据模型
2. 使用Alembic生成迁移脚本
3. 执行迁移脚本创建/更新表结构
4. 支持版本回滚

### 3.9 性能优化设计

#### 3.9.1 查询优化

1. **索引优化**
   - 为常用查询字段建立索引（user_id、platform、status等）
   - 避免在WHERE子句中使用函数
   - 使用覆盖索引减少回表查询

2. **查询优化**
   - 使用EXPLAIN分析查询计划
   - 避免SELECT *，只查询需要的字段
   - 合理使用LIMIT限制返回结果数量
   - 使用分页查询处理大量数据

#### 3.9.2 连接池管理

1. **连接池配置**
   - 使用SQLAlchemy连接池
   - 合理设置连接池大小
   - 连接超时和回收机制

2. **连接池参数**
   - `pool_size`: 连接池大小（建议：10-20）
   - `max_overflow`: 最大溢出连接数（建议：10）
   - `pool_timeout`: 获取连接超时时间（建议：30秒）
   - `pool_recycle`: 连接回收时间（建议：3600秒）

#### 3.9.3 缓存策略

1. **Redis缓存**
   - Prompt模板缓存（TTL 1小时）
   - 用户会话缓存（TTL 30分钟）

2. **查询结果缓存**
   - 相同查询条件的结果缓存
   - 缓存失效策略（时间过期或主动失效）

### 3.10 数据设计总结

#### 3.10.1 数据库设计特点

1. **简洁性**
   - 核心业务表结构清晰，字段语义明确
   - 表数量适中，便于维护

2. **可扩展性**
   - 预留扩展空间（如contents表可添加更多字段）
   - 支持通过Alembic进行数据库版本管理
   - 表结构设计支持未来功能扩展

3. **性能优化**
   - 合理的索引设计
   - 连接池管理
   - 查询优化
   - 缓存策略

4. **数据安全**
   - 数据加密传输
   - 密码加密存储
   - 访问权限控制
   - 定期备份

5. **关系清晰**
   - 表间关系明确（用户-Prompt、用户-内容）
   - 外键约束保证数据完整性
   - 级联删除保证数据一致性

#### 3.10.2 数据存储架构

**数据存储层次：**
```
MySQL（关系数据）
  ├── users（用户信息）
  ├── prompt（Prompt模板）
  └── contents（内容记录）

Redis（缓存数据）
  ├── 验证码存储
  └── 会话缓存

Chroma（向量数据）
  └── RAG知识库向量存储
```

**数据流向：**
```
用户操作 → 应用层 → 数据访问层 → MySQL/Redis/Chroma
```

## 4. API模块设计

### 4.1 API设计原则

#### 4.1.1 RESTful设计原则

1. **资源导向**
   - 使用名词表示资源，动词表示操作
   - URL路径清晰表达资源层级关系

2. **HTTP方法语义**
   - GET：查询资源
   - POST：创建资源
   - PUT：更新资源（完整更新）
   - PATCH：更新资源（部分更新）
   - DELETE：删除资源

3. **状态码规范**
   - 2xx：成功响应
   - 4xx：客户端错误
   - 5xx：服务器错误

#### 4.1.2 API设计规范

1. **URL命名**
   - 使用小写字母
   - 单词间使用连字符（-）分隔
   - 使用复数形式表示资源集合

2. **版本管理**
   - API版本通过URL路径管理：`/api/v1/...`
   - 支持向后兼容

3. **响应格式**
   - 统一使用JSON格式
   - 响应结构标准化

### 4.2 API模块架构

#### 4.2.1 API模块组成

**API模块结构：**
```
API模块
├── 工作台API模块（对话模块）
│   ├── 发送消息接口
│   ├── 创建会话接口
│   └── 获取会话信息接口
├── 登录注册API模块
│   ├── 发送邮箱验证码接口
│   ├── 注册接口
│   └── 登录接口
├── Prompt管理API模块
│   ├── 创建Prompt接口
│   ├── 查询Prompt接口
│   ├── 更新Prompt接口
│   └── 删除Prompt接口
├── 历史记录API模块
│   ├── 查询对话历史记录接口
│   └── 按关键词搜索历史记录接口
├── 内容管理API模块
│   ├── 查询内容历史接口
│   └── 搜索内容接口
├── 配图生成API模块
│   ├── 生成配图接口
│   └── 批量生成配图接口
└── RAG知识库API模块
    └── 文档上传接口
```

#### 4.2.2 API路由设计

**路由前缀：** `/api/v1`

**路由分组：**
- `/api/v1/workspace` - 工作台相关接口
- `/api/v1/auth` - 登录注册相关接口
- `/api/v1/prompt` - Prompt管理相关接口
- `/api/v1/history` - 历史记录相关接口
- `/api/v1/contents` - 内容管理相关接口
- `/api/v1/image` - 配图生成相关接口
- `/api/v1/rag` - RAG知识库相关接口

### 4.3 核心API接口设计

#### 4.3.1 工作台API模块（Workspace API）

##### 4.3.1.1 创建会话接口

**接口描述：** 创建新的工作会话

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `POST /api/v1/workspace/create-session` |
| 请求方法 | POST |
| 功能说明 | 创建新的工作会话，用于内容生成 |

**请求头：**
```
Authorization: Bearer {token}
```

**请求参数：** 无

**响应参数：**

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

**响应参数说明：**

| 参数名 | 类型 | 说明 |
|-------|------|------|
| code | integer | 响应状态码 |
| message | string | 响应消息 |
| data | object | 响应数据 |
| data.session_id | string | 会话ID |
| data.created_at | string | 创建时间 |
| data.expires_at | string | 过期时间 |

##### 4.3.1.2 发送消息接口

**接口描述：** 发送消息到工作台，触发内容生成流程

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `POST /api/v1/workspace/send-message` |
| 请求方法 | POST |
| 功能说明 | 发送消息，触发内容生成（联网检索→标题优化→文风→配图→输出） |

**请求头：**
```
Authorization: Bearer {token}
```

**请求参数：**

```json
{
  "session_id": "string (必填)",
  "message": "string (必填)",
  "material_source": "string (可选)",
  "platform": "string (必填)"
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| session_id | string | 是 | 会话ID |
| message | string | 是 | 用户输入的消息内容 |
| material_source | string | 否 | 素材源（"online"/"rag"/"upload"），默认"online" |
| platform | string | 是 | 目标平台（"xiaohongshu"/"douyin"） |

**响应参数：**

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
    "status": "generating",
    "timestamp": "2026-01-01T10:00:00"
  }
}
```

**响应参数说明：**

| 参数名 | 类型 | 说明 |
|-------|------|------|
| code | integer | 响应状态码 |
| message | string | 响应消息 |
| data | object | 响应数据 |
| data.session_id | string | 会话ID |
| data.content | object | 生成的内容 |
| data.content.title | string | 标题 |
| data.content.body | string | 正文内容 |
| data.content.image_url | string | 配图URL |
| data.status | string | 状态（generating/completed） |
| data.timestamp | string | 响应时间戳 |

**状态码说明：**

| 状态码 | 说明 |
|-------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 429 | 请求频率超限 |
| 500 | 服务器内部错误 |
| 503 | 服务暂时不可用（大模型API异常） |

##### 4.3.1.3 获取会话信息接口

**接口描述：** 获取会话信息

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `GET /api/v1/workspace/session/{session_id}` |
| 请求方法 | GET |
| 功能说明 | 获取指定会话的信息 |

**请求头：**
```
Authorization: Bearer {token}
```

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| session_id | string | 是 | 会话ID |

**响应参数：**

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

##### 4.3.1.4 上传素材/文档接口

**接口描述：** 上传素材或文档到工作台

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `POST /api/v1/workspace/upload-material` |
| 请求方法 | POST |
| 功能说明 | 上传素材或文档，用于内容生成 |

**请求头：**
```
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| session_id | string | 是 | 会话ID |
| file | file | 是 | 上传的文件（支持PDF/Word/Txt） |

**响应参数：**

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

##### 4.3.1.5 重新生成接口

**接口描述：** 基于已有会话重新生成内容

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `POST /api/v1/workspace/regenerate` |
| 请求方法 | POST |
| 功能说明 | 重新生成内容，支持参数调整 |

**请求头：**
```
Authorization: Bearer {token}
```

**请求参数：**

```json
{
  "session_id": "string (必填)",
  "adjustments": {
    "emotion_intensity": "string (可选)",
    "style_preference": "string (可选)"
  }
}
```

**响应参数：** 同发送消息接口

#### 4.3.2 登录注册API模块（Authentication API）

##### 4.3.2.1 发送邮箱验证码接口

**接口描述：** 发送邮箱验证码

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `POST /api/v1/auth/send-code` |
| 请求方法 | POST |
| 功能说明 | 发送4位数字验证码到用户邮箱 |

**请求参数：**

```json
{
  "email": "string (必填)"
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| email | string | 是 | 用户邮箱地址 |

**响应参数：**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "message": "验证码已发送到您的邮箱"
  }
}
```

**状态码说明：**

| 状态码 | 说明 |
|-------|------|
| 200 | 成功 |
| 400 | 邮箱格式错误 |
| 429 | 请求频率超限（同一邮箱5分钟内只能发送一次） |
| 500 | 服务器内部错误 |

##### 4.3.2.2 注册接口

**接口描述：** 用户注册

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `POST /api/v1/auth/register` |
| 请求方法 | POST |
| 功能说明 | 用户注册，创建新账户 |

**请求参数：**

```json
{
  "username": "string (必填)",
  "email": "string (必填)",
  "password": "string (必填)",
  "verify_code": "string (必填)"
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| username | string | 是 | 用户名，长度1-100 |
| email | string | 是 | 邮箱地址 |
| password | string | 是 | 密码，长度8-32 |
| verify_code | string | 是 | 邮箱验证码，4位数字 |

**响应参数：**

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

**错误响应：**

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

##### 4.3.2.3 登录接口

**接口描述：** 用户登录

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `POST /api/v1/auth/login` |
| 请求方法 | POST |
| 功能说明 | 用户登录，获取访问令牌 |

**请求参数：**

```json
{
  "email": "string (必填)",
  "password": "string (必填)"
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| email | string | 是 | 邮箱地址 |
| password | string | 是 | 密码 |

**响应参数：**

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

**错误响应：**

```json
{
  "code": 401,
  "message": "认证失败",
  "error": "邮箱或密码错误"
}
```

##### 4.3.2.4 登出接口

**接口描述：** 用户登出

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `POST /api/v1/auth/logout` |
| 请求方法 | POST |
| 功能说明 | 用户登出，使Token失效 |

**请求头：**
```
Authorization: Bearer {token}
```

**请求参数：** 无

**响应参数：**

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

#### 4.3.3 Prompt管理API模块（Prompt Management API）

##### 4.3.3.1 创建Prompt接口

**接口描述：** 创建新的Prompt模板

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `POST /api/v1/prompt/create` |
| 请求方法 | POST |
| 功能说明 | 创建新的Prompt模板 |

**请求头：**
```
Authorization: Bearer {token}
```

**请求参数：**

```json
{
  "name": "string (必填)",
  "content": "string (必填)"
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| name | string | 是 | 模板名称，长度1-255 |
| content | string | 是 | Prompt内容 |

**响应参数：**

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

##### 4.3.3.2 查询Prompt接口

**接口描述：** 查询Prompt模板列表

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `GET /api/v1/prompt/list` |
| 请求方法 | GET |
| 功能说明 | 查询当前用户的Prompt模板列表 |

**请求头：**
```
Authorization: Bearer {token}
```

**查询参数：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认20，最大100 |

**响应参数：**

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

##### 4.3.3.3 更新Prompt接口

**接口描述：** 更新Prompt模板

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `PUT /api/v1/prompt/update` |
| 请求方法 | PUT |
| 功能说明 | 更新指定的Prompt模板 |

**请求头：**
```
Authorization: Bearer {token}
```

**请求参数：**

```json
{
  "id": "integer (必填)",
  "name": "string (可选)",
  "content": "string (可选)"
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| id | integer | 是 | Prompt模板ID |
| name | string | 否 | 模板名称 |
| content | string | 否 | Prompt内容 |

**响应参数：**

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

##### 4.3.3.4 删除Prompt接口

**接口描述：** 删除Prompt模板

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `DELETE /api/v1/prompt/delete` |
| 请求方法 | DELETE |
| 功能说明 | 删除指定的Prompt模板 |

**请求头：**
```
Authorization: Bearer {token}
```

**请求参数：**

```json
{
  "id": "integer (必填)"
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| id | integer | 是 | Prompt模板ID |

**响应参数：**

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

#### 4.3.4 历史记录API模块（History API）

##### 4.3.4.1 查询对话历史记录接口

**接口描述：** 查询对话历史记录

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `GET /api/v1/history/conversations` |
| 请求方法 | GET |
| 功能说明 | 查询用户的对话历史记录 |

**请求头：**
```
Authorization: Bearer {token}
```

**查询参数：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| session_id | string | 否 | 会话ID，不传则返回所有会话 |
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认20，最大100 |

**响应参数：**

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

##### 4.3.4.2 按关键词搜索历史记录接口

**接口描述：** 按关键词搜索历史记录

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `GET /api/v1/history/search` |
| 请求方法 | GET |
| 功能说明 | 按关键词搜索对话历史记录 |

**请求头：**
```
Authorization: Bearer {token}
```

**查询参数：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| keyword | string | 是 | 搜索关键词 |
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认20，最大100 |

**响应参数：** 同查询对话历史记录接口

#### 4.3.5 内容管理API模块（Contents API）

##### 4.3.5.1 查询内容历史接口

**接口描述：** 查询用户生成的内容历史

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `GET /api/v1/contents/list` |
| 请求方法 | GET |
| 功能说明 | 查询用户的内容记录（草稿/已发布） |

**请求头：**
```
Authorization: Bearer {token}
```

**查询参数：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| platform | string | 否 | 平台筛选（"xiaohongshu"/"douyin"） |
| status | string | 否 | 状态筛选（"draft"/"published"） |
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认20，最大100 |

**响应参数：**

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

##### 4.3.5.2 搜索内容接口

**接口描述：** 按关键词搜索内容

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `GET /api/v1/contents/search` |
| 请求方法 | GET |
| 功能说明 | 按关键词搜索内容记录 |

**请求头：**
```
Authorization: Bearer {token}
```

**查询参数：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| keyword | string | 是 | 搜索关键词 |
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认20，最大100 |

**响应参数：** 同查询内容历史接口

#### 4.3.6 配图生成API模块（Image Generation API）

##### 4.3.6.1 生成配图接口

**接口描述：** 生成配图

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `POST /api/v1/image/generate` |
| 请求方法 | POST |
| 功能说明 | 根据内容生成配图（DALL·E 3） |

**请求头：**
```
Authorization: Bearer {token}
```

**请求参数：**

```json
{
  "content": "string (必填)",
  "platform": "string (必填)"
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| content | string | 是 | 内容文本，用于生成配图 |
| platform | string | 是 | 目标平台（"xiaohongshu"/"douyin"） |

**响应参数：**

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

##### 4.3.6.2 批量生成配图接口

**接口描述：** 批量生成配图（≥3张）

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `POST /api/v1/image/batch-generate` |
| 请求方法 | POST |
| 功能说明 | 批量生成配图，返回多张备选图片 |

**请求头：**
```
Authorization: Bearer {token}
```

**请求参数：**

```json
{
  "content": "string (必填)",
  "platform": "string (必填)",
  "count": "integer (可选)"
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| content | string | 是 | 内容文本 |
| platform | string | 是 | 目标平台 |
| count | integer | 否 | 生成数量，默认3，最大5 |

**响应参数：**

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

##### 4.3.6.3 下载图片接口

**接口描述：** 下载生成的图片

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `GET /api/v1/image/download` |
| 请求方法 | GET |
| 功能说明 | 下载指定URL的图片 |

**请求头：**
```
Authorization: Bearer {token}
```

**查询参数：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| image_url | string | 是 | 图片URL |

**响应：** 返回图片文件流

#### 4.3.7 RAG知识库API模块（RAG Knowledge Base API）

##### 4.3.7.1 文档上传接口

**接口描述：** 上传文档到RAG知识库

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `POST /api/v1/rag/upload` |
| 请求方法 | POST |
| 功能说明 | 上传文档，自动解析、分块、向量化并存储到Chroma |

**请求头：**
```
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| file | file | 是 | 上传的文件（支持PDF/Word/Txt） |

**响应参数：**

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

##### 4.3.7.2 删除文档接口

**接口描述：** 删除RAG知识库中的文档

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `DELETE /api/v1/rag/delete` |
| 请求方法 | DELETE |
| 功能说明 | 删除指定的文档及其向量数据 |

**请求头：**
```
Authorization: Bearer {token}
```

**请求参数：**

```json
{
  "document_id": "string (必填)"
}
```

**响应参数：**

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

##### 4.3.7.3 文档列表接口

**接口描述：** 查询RAG知识库文档列表

**接口信息：**

| 项目 | 内容 |
|-----|------|
| 接口路径 | `GET /api/v1/rag/list` |
| 请求方法 | GET |
| 功能说明 | 查询当前用户上传的文档列表 |

**请求头：**
```
Authorization: Bearer {token}
```

**查询参数：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认20，最大100 |

**响应参数：**

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

### 4.4 API响应格式规范

#### 4.4.1 标准响应格式

所有API接口统一使用以下响应格式：

```json
{
  "code": integer,
  "message": "string",
  "data": object | array | null,
  "error": object | string | null
}
```

**字段说明：**

| 字段名 | 类型 | 说明 |
|-------|------|------|
| code | integer | 响应状态码，HTTP状态码或业务状态码 |
| message | string | 响应消息，成功时为"success"，失败时为错误描述 |
| data | object/array/null | 响应数据，成功时返回数据，失败时为null |
| error | object/string/null | 错误信息，成功时为null，失败时返回错误详情 |

#### 4.4.2 状态码规范

**HTTP状态码：**

| 状态码 | 说明 | 使用场景 |
|-------|------|---------|
| 200 | 成功 | 请求成功处理 |
| 400 | 请求错误 | 请求参数错误、格式错误 |
| 401 | 未授权 | Token无效或过期 |
| 404 | 未找到 | 资源不存在 |
| 429 | 请求过多 | 超过限流阈值 |
| 500 | 服务器错误 | 服务器内部错误 |
| 503 | 服务不可用 | 外部服务不可用（如大模型API异常） |

**业务状态码（code字段）：**

| 状态码 | 说明 |
|-------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 404 | 资源不存在 |
| 429 | 请求频率超限 |
| 500 | 服务器内部错误 |
| 503 | 服务暂时不可用 |

### 4.5 API错误处理

#### 4.5.1 错误响应格式

**参数验证错误：**

```json
{
  "code": 400,
  "message": "请求参数错误",
  "error": {
    "field_name": "错误描述"
  }
}
```

**业务逻辑错误：**

```json
{
  "code": 400,
  "message": "业务逻辑错误",
  "error": "具体错误描述"
}
```

**服务器错误：**

```json
{
  "code": 500,
  "message": "服务器内部错误",
  "error": "错误详情（开发环境）"
}
```

#### 4.5.2 错误处理策略

1. **参数验证**
   - 使用Pydantic进行请求参数验证
   - 返回详细的字段级错误信息

2. **业务逻辑错误**
   - 返回友好的错误提示
   - 不暴露系统内部细节

3. **异常处理**
   - 捕获所有未处理异常
   - 记录错误日志
   - 返回通用错误响应

### 4.6 API认证与授权

#### 4.6.1 JWT认证

**Token格式：**
```
Authorization: Bearer {access_token}
```

**Token生成：**
- 用户登录成功后生成JWT Token
- Token包含用户ID、邮箱等信息
- Token有效期：2小时

**Token验证：**
- 所有需要认证的接口都需要在请求头中携带Token
- 服务器验证Token有效性和过期时间
- Token无效或过期返回401错误

#### 4.6.2 权限控制

- 用户只能访问自己的资源（Prompt、内容记录等）
- 通过Token中的user_id进行权限校验
- 跨用户访问返回403错误

### 4.7 API模块实现要点

#### 4.7.1 技术实现

1. **路由组织**
   - 使用FastAPI的APIRouter进行路由分组
   - 每个模块独立的路由文件

2. **请求验证**
   - 使用Pydantic模型定义请求/响应格式
   - 自动参数验证和类型转换

3. **异步处理**
   - 所有API接口使用async/await
   - 异步数据库操作
   - 异步外部API调用

4. **中间件**
   - 请求日志记录
   - 错误处理
   - CORS处理

#### 4.7.2 代码结构

```
api/
├── __init__.py
├── main.py                 # FastAPI应用入口
├── dependencies.py         # 依赖注入（认证等）
├── middleware.py           # 中间件
├── routers/
│   ├── __init__.py
│   ├── workspace.py       # 工作台API路由
│   ├── auth.py            # 登录注册API路由
│   ├── prompt.py          # Prompt管理API路由
│   ├── history.py         # 历史记录API路由
│   ├── contents.py        # 内容管理API路由
│   ├── image.py           # 配图生成API路由
│   └── rag.py             # RAG知识库API路由
├── schemas/
│   ├── __init__.py
│   ├── workspace.py       # 工作台相关Schema
│   ├── auth.py            # 认证相关Schema
│   ├── prompt.py          # Prompt相关Schema
│   ├── history.py         # 历史记录相关Schema
│   ├── contents.py        # 内容相关Schema
│   ├── image.py           # 配图相关Schema
│   └── common.py          # 通用Schema
└── utils/
    ├── __init__.py
    ├── response.py        # 响应格式化
    └── exceptions.py      # 异常处理
```

### 4.8 API模块总结

#### 4.8.1 API模块特点

1. **RESTful设计**
   - 符合REST设计原则
   - 资源导向的URL设计
   - 标准HTTP方法使用

2. **统一规范**
   - 统一的响应格式
   - 统一的错误处理
   - 统一的认证机制

3. **易于使用**
   - 自动生成API文档（FastAPI Swagger）
   - 清晰的参数说明
   - 友好的错误提示

4. **高性能**
   - 异步处理
   - 错误降级

#### 4.8.2 API端点汇总

| 模块 | 端点 | 方法 | 功能 |
|-----|------|------|------|
| 工作台 | `/api/v1/workspace/create-session` | POST | 创建会话 |
| 工作台 | `/api/v1/workspace/send-message` | POST | 发送消息 |
| 工作台 | `/api/v1/workspace/session/{session_id}` | GET | 获取会话信息 |
| 工作台 | `/api/v1/workspace/upload-material` | POST | 上传素材 |
| 工作台 | `/api/v1/workspace/regenerate` | POST | 重新生成 |
| 认证 | `/api/v1/auth/send-code` | POST | 发送验证码 |
| 认证 | `/api/v1/auth/register` | POST | 注册 |
| 认证 | `/api/v1/auth/login` | POST | 登录 |
| 认证 | `/api/v1/auth/logout` | POST | 登出 |
| Prompt | `/api/v1/prompt/create` | POST | 创建Prompt |
| Prompt | `/api/v1/prompt/list` | GET | 查询Prompt列表 |
| Prompt | `/api/v1/prompt/update` | PUT | 更新Prompt |
| Prompt | `/api/v1/prompt/delete` | DELETE | 删除Prompt |
| 历史 | `/api/v1/history/conversations` | GET | 查询对话历史 |
| 历史 | `/api/v1/history/search` | GET | 搜索历史记录 |
| 内容 | `/api/v1/contents/list` | GET | 查询内容历史 |
| 内容 | `/api/v1/contents/search` | GET | 搜索内容 |
| 配图 | `/api/v1/image/generate` | POST | 生成配图 |
| 配图 | `/api/v1/image/batch-generate` | POST | 批量生成配图 |
| 配图 | `/api/v1/image/download` | GET | 下载图片 |
| RAG | `/api/v1/rag/upload` | POST | 上传文档 |
| RAG | `/api/v1/rag/delete` | DELETE | 删除文档 |
| RAG | `/api/v1/rag/list` | GET | 文档列表 |