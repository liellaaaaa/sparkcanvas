# 工具函数目录

## 文件说明

- `http.js` - HTTP请求封装，统一处理API请求
- `storage.js` - 本地存储工具，封装uni存储API

## 使用示例

### HTTP请求
```javascript
import http from '@/utils/http'

// 登录
const result = await http.login({ email: 'xxx', password: 'xxx' })

// 创建工作会话
const session = await http.createSession()
```

### 本地存储
```javascript
import storage from '@/utils/storage'

// 存储Token
storage.setToken('xxx')

// 获取Token
const token = storage.getToken()

// 存储用户信息
storage.setUserInfo({ id: 1, username: 'xxx' })
```

