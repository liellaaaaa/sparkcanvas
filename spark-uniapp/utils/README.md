# 工具函数目录

## 文件说明

- `config.js` - 应用配置，包括API地址、超时时间等
- `http.js` - HTTP请求封装，统一处理API请求
- `storage.js` - 本地存储工具，封装uni存储API

## 配置说明

### API 地址配置

**重要：真机测试时必须使用本机IP地址，不能使用 localhost！**

1. **浏览器测试**：可以使用 `http://localhost:8000`
2. **真机测试**：必须使用本机IP地址，例如 `http://192.168.1.100:8000`

#### 如何获取本机IP地址

- **Windows**：打开命令提示符，运行 `ipconfig`，查找 "IPv4 地址"
- **Mac/Linux**：打开终端，运行 `ifconfig`，查找 "inet" 地址

#### 修改配置

编辑 `config.js` 文件，修改 `BASE_URL`：

```javascript
const config = {
  // 将 localhost 替换为你的本机IP地址
  BASE_URL: 'http://192.168.1.100:8000', // 替换为你的实际IP
  // ...
}
```

#### 常见问题

**Q: 为什么真机测试时提示请求超时？**  
A: 因为真机上 `localhost` 指向设备本身，无法访问开发机器。请使用本机IP地址。

**Q: 如何确认后端服务已启动？**  
A: 在浏览器访问 `http://你的IP:8000/health`，如果返回 `{"status":"ok"}` 说明服务正常。

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

