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
5. **微信小程序环境**: 
   - 微信小程序不支持 Node.js 的 `process` 对象
   - 已移除 `process.env` 的使用,改为直接配置
   - 在微信开发者工具中测试时,需要在"设置-项目设置"中勾选"不校验合法域名"
   - 正式发布前需要在微信公众平台配置服务器域名白名单

## 常见问题

### 1. 微信小程序报错: process is not defined
**原因**: 微信小程序环境不支持 Node.js 的 `process` 对象

**解决方案**: 
- 已在 `utils/config.js` 中移除 `process.env` 的使用
- 改为直接配置 `BASE_URL: 'http://127.0.0.1:8000'`
- 如需修改后端地址,直接编辑此配置项即可

### 2. 微信小程序报错: WXSS 文件编译错误 unexpected token `$`
**原因**: `App.vue` 中使用 `<style>` 标签导入 `uni.scss`,但未指定 `lang="scss"`,导致 SCSS 变量未被编译

**解决方案**:
- 已将 `App.vue` 中的 `<style>` 改为 `<style lang="scss">`
- 重新编译项目即可

### 3. 微信小程序无法连接后端
**解决方案**:
1. 在微信开发者工具中,点击右上角"详情"
2. 在"本地设置"中勾选"不校验合法域名、web-view(业务域名)、TLS版本以及HTTPS证书"
3. 确保后端服务已启动并运行在 `http://127.0.0.1:8000`

### 4. 在真机上测试时无法连接
**原因**: 真机无法访问 localhost 或 127.0.0.1

**解决方案**:
1. 获取你的电脑IP地址 (Windows: `ipconfig`, Mac/Linux: `ifconfig`)
2. 修改 `utils/config.js` 中的 `BASE_URL`,例如: `http://192.168.1.100:8000`
3. 确保手机和电脑在同一网络
4. 确保电脑防火墙允许 8000 端口访问

### 5. 注册失败 - 事务错误
**前端表现**: 注册时提示"注册失败: A transaction is already begun on this Session."

**这是后端问题,不是前端问题!**

**原因**:
- 后端数据库事务管理冲突
- SQLAlchemy 异步会话中，会话已经在一个事务中，再次调用 `begin()` 导致错误

**解决方案**:
1. **已修复**: 后端代码已优化事务管理方式
2. **重启后端服务**: 确保使用最新代码
3. **检查后端日志**: 查看是否有其他错误信息
4. **重试注册**: 如果问题已修复，可以重新尝试注册

详见后端文档: `spark-backend/config/README.md`

### 6. 内容生成失败 - 通义千问连接错误
**前端表现**: 点击生成后返回错误提示,内容显示"生成失败 - 降级内容"

**后端日志显示**:
```
通义千问异常: ('Connection aborted.', ConnectionResetError(10054))
```

**这是后端问题,不是前端问题!**

**原因**:
- 后端与阿里云通义千问 API 的连接被中断
- 可能是网络不稳定、API 密钥未配置或防火墙问题

**解决方案**:
1. **检查后端配置**: 确保后端 `.env` 文件中配置了 `DASHSCOPE_API_KEY`
2. **获取 API Key**: 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/) 获取
3. **重启后端服务**: 修改配置后需要重启
4. **检查网络**: 确保后端服务器能访问阿里云 API
5. **重试**: 后端已实现自动重试机制,可以直接点击"重新生成"

详见后端文档: `spark-backend/config/README.md`

## 待开发功能

- [ ] 工作台完整功能实现
- [ ] 内容生成界面
- [ ] 配图预览
- [ ] 历史记录详情
- [ ] Prompt编辑器
- [ ] 文档上传功能
- [ ] 用户中心

## 项目改进建议

### 已完成的改进
1. ✅ 修复微信小程序 `process is not defined` 错误
2. ✅ 修复微信小程序 WXSS 编译错误(SCSS 变量问题)
3. ✅ 优化配置文件,兼容多端部署
4. ✅ 完善错误处理和用户提示
5. ✅ 修复后端注册事务管理问题（A transaction is already begun on this Session）

### 待改进项
1. 考虑使用条件编译为不同平台配置不同的 API 地址
2. 添加环境配置文件(开发/测试/生产环境)
3. 完善错误提示和用户引导
4. 添加网络状态检测和重连机制


