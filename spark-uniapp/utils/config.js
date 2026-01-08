/**
 * 应用配置
 * 
 * 注意：
 * - 在移动设备（真机）上测试时，不能使用 localhost
 * - 需要使用开发机器的实际IP地址，例如：http://192.168.1.100:8000
 * - 在 HBuilderX 中运行到浏览器时可以使用 localhost
 * - 获取本机IP：Windows 运行 ipconfig，Mac/Linux 运行 ifconfig
 */
const config = {
  // API 基础地址
  // 开发环境（浏览器）：http://localhost:8000
  // 开发环境（真机）：http://你的本机IP:8000，例如：http://192.168.1.100:8000
  // 生产环境：需要配置实际的后端地址
  // 微信小程序环境不支持 process 对象，直接使用默认值
  BASE_URL: 'https://sparkcanvas.icu:8000',
  
  // 请求超时时间（毫秒）
  // 普通请求：15秒
  // LLM 生成需要较长时间，会在具体接口中单独设置
  TIMEOUT: 15000,
  
  // Token 存储 key
  TOKEN_KEY: 'access_token',
  
  // 用户信息存储 key
  USER_INFO_KEY: 'user_info'
}

// 开发环境自动检测（仅在 H5 浏览器环境）
// #ifdef H5
if (typeof window !== 'undefined' && window.location) {
  const hostname = window.location.hostname
  // 如果是 localhost 或 127.0.0.1，尝试使用当前页面的 hostname
  // 这样可以支持通过 IP 访问前端时自动使用相同 IP 访问后端
  if (config.BASE_URL.includes('localhost') && hostname !== 'localhost' && hostname !== '127.0.0.1') {
    // 如果前端是通过 IP 访问的，自动使用相同 IP 访问后端
    const protocol = window.location.protocol
    const port = '8000' // 后端端口
    config.BASE_URL = `${protocol}//${hostname}:${port}`
    console.log('自动检测到后端地址:', config.BASE_URL)
  }
}
// #endif

export default config

