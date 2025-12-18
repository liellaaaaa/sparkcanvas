/**
 * HTTP请求封装
 * 统一处理API请求、错误处理、Token管理等
 */
import config from './config.js'

const BASE_URL = config.BASE_URL

// 请求拦截器
const requestInterceptor = (options) => {
  // 添加Token
  const token = uni.getStorageSync(config.TOKEN_KEY)
  if (token) {
    options.header = {
      ...options.header,
      'Authorization': `Bearer ${token}`
    }
  }
  
  // 设置默认请求头
  options.header = {
    'Content-Type': 'application/json',
    ...options.header
  }
  
  return options
}

// 响应拦截器
const responseInterceptor = (response) => {
  const { statusCode, data } = response
  
  // HTTP状态码处理
  if (statusCode === 200) {
    // 后端直接返回数据，没有包装在 code/data 中
    // 成功响应直接返回数据
    return Promise.resolve(data)
  } else if (statusCode === 400) {
    // 400 错误，通常是业务错误
    const errorMsg = data?.detail || data?.message || '请求参数错误'
    return Promise.reject(new Error(errorMsg))
  } else if (statusCode === 401) {
    // 未授权，清除Token并跳转登录
    uni.removeStorageSync(config.TOKEN_KEY)
    uni.removeStorageSync(config.USER_INFO_KEY)
    uni.reLaunch({
      url: '/pages/login/login'
    })
    return Promise.reject(new Error('登录已过期，请重新登录'))
  } else if (statusCode === 403) {
    // 禁止访问
    return Promise.reject(new Error(data?.detail || '无权限访问'))
  } else if (statusCode === 500) {
    // 服务器错误
    return Promise.reject(new Error(data?.detail || '服务器错误'))
  } else {
    return Promise.reject(new Error(data?.detail || `请求失败: ${statusCode}`))
  }
}

// 通用请求方法
const request = (options) => {
  return new Promise((resolve, reject) => {
    // 请求拦截
    const requestConfig = requestInterceptor({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: options.header || {},
      timeout: config.TIMEOUT
    })
    
    uni.request({
      ...requestConfig,
      success: (res) => {
        responseInterceptor(res)
          .then(resolve)
          .catch(reject)
      },
      fail: (err) => {
        console.error('请求失败:', err)
        reject(new Error(err.errMsg || '网络请求失败，请检查网络连接'))
      }
    })
  })
}

// API方法封装
const http = {
  // 认证相关
  // 发送验证码：GET /auth/code?email=xxx
  sendCode: (email) => request({ 
    url: `/auth/code?email=${encodeURIComponent(email)}`, 
    method: 'GET' 
  }),
  
  // 用户注册：POST /auth/register
  register: (data) => request({ 
    url: '/auth/register', 
    method: 'POST', 
    data 
  }),
  
  // 用户登录：POST /auth/login
  login: (data) => request({ 
    url: '/auth/login', 
    method: 'POST', 
    data 
  }),
  
  logout: () => {
    // 清除本地存储
    uni.removeStorageSync(config.TOKEN_KEY)
    uni.removeStorageSync(config.USER_INFO_KEY)
    return Promise.resolve()
  },
  
  // 工作台相关
  createSession: () => request({ url: '/workspace/create-session', method: 'POST' }),
  sendMessage: (data) => request({ url: '/workspace/send-message', method: 'POST', data }),
  getSession: (sessionId) => request({ url: `/workspace/session/${sessionId}`, method: 'GET' }),
  uploadMaterial: (data) => request({ url: '/workspace/upload-material', method: 'POST', data }),
  regenerate: (data) => request({ url: '/workspace/regenerate', method: 'POST', data }),
  
  // 历史记录相关
  getConversations: (params) => request({ url: '/history/conversations', method: 'GET', data: params }),
  searchHistory: (params) => request({ url: '/history/search', method: 'GET', data: params }),
  
  // 内容管理相关
  getContents: (params) => request({ url: '/contents/list', method: 'GET', data: params }),
  searchContents: (params) => request({ url: '/contents/search', method: 'GET', data: params }),
  
  // Prompt管理相关
  createPrompt: (data) => request({ url: '/prompt/create', method: 'POST', data }),
  getPrompts: (params) => request({ url: '/prompt/list', method: 'GET', data: params }),
  updatePrompt: (data) => request({ url: '/prompt/update', method: 'PUT', data }),
  deletePrompt: (data) => request({ url: '/prompt/delete', method: 'DELETE', data }),
  
  // 配图生成相关
  generateImage: (data) => request({ url: '/image/generate', method: 'POST', data }),
  batchGenerateImage: (data) => request({ url: '/image/batch-generate', method: 'POST', data }),
  
  // RAG知识库相关
  uploadDocument: (data) => request({ url: '/rag/upload', method: 'POST', data }),
  deleteDocument: (data) => request({ url: '/rag/delete', method: 'DELETE', data }),
  getDocuments: (params) => request({ url: '/rag/list', method: 'GET', data: params }),
  searchRAG: (data) => request({ url: '/rag/search', method: 'POST', data })
}

export default http

