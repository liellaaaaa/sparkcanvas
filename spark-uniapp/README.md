# SparkCanvas UniApp 前端项目

## 项目简介

SparkCanvas UniApp 前端项目，基于 uni-app 框架开发，支持多端部署（H5、小程序、App）。

## 项目结构

```
spark-uniapp/
├── pages/              # 页面目录
│   ├── workspace/     # 工作台页面
│   ├── login/         # 登录页面
│   ├── register/       # 注册页面
│   ├── history/        # 历史记录页面
│   ├── prompt/         # Prompt管理页面
│   └── rag/            # RAG知识库页面
├── static/             # 静态资源目录
│   ├── tabbar/        # TabBar图标
│   └── images/        # 图片资源
├── utils/              # 工具函数
│   ├── http.js         # HTTP请求封装
│   └── storage.js      # 本地存储工具
├── manifest.json       # 应用配置文件
├── pages.json          # 页面路由配置
├── main.js             # 应用入口文件
├── App.vue             # 应用根组件
├── index.html          # H5入口文件
└── uni.scss            # 全局样式变量
```

## 功能模块

### 1. 工作台（Workspace）
- 内容创作工作台
- 对话上下文管理
- 素材源选择（联网/RAG/上传）
- 内容生成与预览

### 2. 登录注册（Auth）
- 邮箱注册登录
- 验证码校验
- Token管理

### 3. 历史记录（History）
- 对话历史查看
- 内容历史管理
- 搜索功能

### 4. Prompt管理
- Prompt模板创建
- Prompt列表查看
- Prompt编辑删除

### 5. RAG知识库
- 文档上传
- 知识库管理
- 语义检索

## 开发指南

### 环境要求
- HBuilderX 3.0+
- Node.js 14+
- Vue 3

### 安装依赖
```bash
npm install
```

### 运行项目
- H5: 在HBuilderX中运行到浏览器
- 小程序: 在HBuilderX中运行到微信开发者工具
- App: 在HBuilderX中运行到手机或模拟器

### 配置说明

#### API地址配置
在 `utils/http.js` 中修改 `BASE_URL`：
```javascript
const BASE_URL = 'http://your-api-domain.com/api/v1'
```

#### 应用配置
在 `manifest.json` 中配置应用信息、权限等。

## 注意事项

1. **Token管理**: 所有需要认证的API请求会自动携带Token
2. **错误处理**: HTTP请求会自动处理401错误并跳转登录页
3. **存储管理**: 使用 `utils/storage.js` 统一管理本地存储
4. **页面路由**: 在 `pages.json` 中配置页面路由和TabBar

## 待开发功能

- [ ] 工作台完整功能实现
- [ ] 内容生成界面
- [ ] 配图预览
- [ ] 历史记录详情
- [ ] Prompt编辑器
- [ ] 文档上传功能
- [ ] 用户中心


