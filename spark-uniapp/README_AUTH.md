# SparkCanvas 前端登录注册模块使用说明

## 📋 功能说明

已完成前端登录注册界面的开发，并与后端API完成联调。

### ✅ 已实现功能

1. **登录页面** (`pages/login/login.vue`)
   - 邮箱和密码输入
   - 表单验证（邮箱格式、密码长度）
   - 调用后端登录API
   - Token和用户信息存储
   - 登录成功后跳转到工作台

2. **注册页面** (`pages/register/register.vue`)
   - 用户名、邮箱、验证码、密码、确认密码输入
   - 表单验证（用户名长度、邮箱格式、密码一致性等）
   - 发送邮箱验证码（60秒倒计时）
   - 调用后端注册API
   - 注册成功后自动登录

3. **HTTP工具** (`utils/http.js`)
   - 统一的API请求封装
   - 自动添加Token到请求头
   - 响应拦截和错误处理
   - Token过期自动跳转登录

4. **存储工具** (`utils/storage.js`)
   - Token存储管理
   - 用户信息存储管理

5. **配置文件** (`utils/config.js`)
   - API基础地址配置
   - 统一配置管理

## 🔧 配置说明

### API 地址配置

编辑 `utils/config.js` 文件，修改 `BASE_URL`：

```javascript
const config = {
  // 开发环境
  BASE_URL: 'http://localhost:8000',
  
  // 生产环境（需要修改为实际的后端地址）
  // BASE_URL: 'https://api.yourdomain.com',
}
```

### 跨域配置

后端已配置 CORS，允许所有来源访问（开发环境）。生产环境需要修改后端 `main.py` 中的 CORS 配置。

## 📡 API 接口

### 1. 发送验证码

**请求**:
```
GET /auth/code?email={email}
```

**响应**:
```json
{
  "result": "success"
}
```

### 2. 用户注册

**请求**:
```
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "confirm_password": "password123",
  "code": "1234"
}
```

**响应**:
```json
{
  "result": "success"
}
```

### 3. 用户登录

**请求**:
```
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应**:
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## 🚀 使用流程

### 注册流程

1. 打开注册页面
2. 输入用户名（3-20字符）
3. 输入邮箱
4. 点击"发送验证码"按钮
5. 查收邮箱验证码（4位数字）
6. 输入验证码
7. 输入密码（6-20字符）
8. 确认密码
9. 点击"注册"按钮
10. 注册成功后自动登录，跳转到工作台

### 登录流程

1. 打开登录页面
2. 输入邮箱
3. 输入密码
4. 点击"登录"按钮
5. 登录成功后跳转到工作台

## 📝 表单验证规则

### 登录页面

- **邮箱**: 必填，需符合邮箱格式
- **密码**: 必填，长度至少6位

### 注册页面

- **用户名**: 必填，3-20个字符
- **邮箱**: 必填，需符合邮箱格式
- **验证码**: 必填，4位数字
- **密码**: 必填，6-20个字符
- **确认密码**: 必填，需与密码一致

## 🔐 Token 管理

### 存储位置

- Token: `access_token`
- 用户信息: `user_info`

### 自动处理

- 请求时自动添加 `Authorization: Bearer {token}` 头
- Token过期时自动清除并跳转登录页

### 手动操作

```javascript
import storage from '@/utils/storage.js'

// 设置Token
storage.setToken('your-token')

// 获取Token
const token = storage.getToken()

// 删除Token
storage.removeToken()

// 设置用户信息
storage.setUserInfo({ id: 1, email: '...', username: '...' })

// 获取用户信息
const userInfo = storage.getUserInfo()
```

## 🐛 常见问题

### 1. 网络请求失败

**问题**: 提示"网络请求失败"

**解决**:
- 检查后端服务是否启动
- 检查 `utils/config.js` 中的 `BASE_URL` 是否正确
- 检查网络连接

### 2. 验证码发送失败

**问题**: 点击发送验证码后提示失败

**解决**:
- 检查邮箱格式是否正确
- 检查后端邮件服务配置
- 查看后端日志

### 3. 登录/注册失败

**问题**: 提示"登录失败"或"注册失败"

**解决**:
- 检查输入信息是否正确
- 检查后端API是否正常
- 查看错误提示信息

### 4. Token 过期

**问题**: 提示"登录已过期"

**解决**:
- 重新登录获取新Token
- 检查Token存储是否正常

## 📱 页面跳转

### 从登录页跳转到注册页

```javascript
uni.navigateTo({
  url: '/pages/register/register'
})
```

### 从注册页跳转到登录页

```javascript
uni.navigateTo({
  url: '/pages/login/login'
})
```

### 登录成功后跳转到工作台

```javascript
uni.switchTab({
  url: '/pages/workspace/workspace'
})
```

## 🎨 UI 说明

### 登录页面

- 渐变紫色背景
- 白色卡片式表单
- 圆角输入框
- 渐变蓝色按钮

### 注册页面

- 渐变紫色背景
- 白色卡片式表单
- 验证码发送按钮（带倒计时）
- 确认密码输入框

## 🔄 前后端联调

### 测试步骤

1. **启动后端服务**
   ```bash
   cd spark-backend
   python main.py
   ```

2. **配置前端API地址**
   - 编辑 `utils/config.js`
   - 设置 `BASE_URL: 'http://localhost:8000'`

3. **测试注册流程**
   - 打开注册页面
   - 输入信息并发送验证码
   - 查收邮箱验证码
   - 完成注册

4. **测试登录流程**
   - 打开登录页面
   - 输入邮箱和密码
   - 点击登录

### 联调检查清单

- [ ] 后端服务正常运行
- [ ] 前端API地址配置正确
- [ ] 发送验证码功能正常
- [ ] 注册功能正常
- [ ] 登录功能正常
- [ ] Token存储正常
- [ ] 页面跳转正常

## 📞 技术支持

如有问题，请检查：
1. 后端服务日志
2. 浏览器/开发者工具控制台
3. 网络请求详情
4. 后端API文档：http://localhost:8000/docs

