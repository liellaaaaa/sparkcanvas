/**
 * 应用配置
 */
const config = {
  // API 基础地址
  // 开发环境：http://localhost:8000
  // 生产环境：需要配置实际的后端地址
  BASE_URL: 'http://localhost:8000',
  
  // 请求超时时间（毫秒）
  TIMEOUT: 10000,
  
  // Token 存储 key
  TOKEN_KEY: 'access_token',
  
  // 用户信息存储 key
  USER_INFO_KEY: 'user_info'
}

export default config

