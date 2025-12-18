/**
 * HTTP请求封装
 * 统一处理API请求、错误处理、Token管理等
 */

const BASE_URL = 'http://localhost:8000/api/v1' // TODO: 从配置文件读取

// 请求拦截器
const requestInterceptor = (config) => {
  // 添加Token
  const token = uni.getStorageSync('access_token')
  if (token) {
    config.header = {
      ...config.header,
      'Authorization': `Bearer ${token}`
    }
  }
  
  // 设置默认请求头
  config.header = {
    'Content-Type': 'application/json',
    ...config.header
  }
  
  return config
}

// 响应拦截器
const responseInterceptor = (response) => {
  const { statusCode, data } = response
  
  // HTTP状态码处理
  if (statusCode === 200) {
    // 业务状态码处理
    if (data.code === 200) {
      return Promise.resolve(data.data)
    } else if (data.code === 401) {
      // Token过期，跳转登录
      uni.removeStorageSync('access_token')
      uni.removeStorageSync('user_info')
      uni.reLaunch({
        url: '/pages/login/login'
      })
      return Promise.reject(new Error(data.message || '登录已过期'))
    } else {
      return Promise.reject(new Error(data.message || '请求失败'))
    }
  } else if (statusCode === 401) {
    uni.removeStorageSync('access_token')
    uni.reLaunch({
      url: '/pages/login/login'
    })
    return Promise.reject(new Error('未授权'))
  } else {
    return Promise.reject(new Error(`请求失败: ${statusCode}`))
  }
}

// 通用请求方法
const request = (options) => {
  return new Promise((resolve, reject) => {
    // 请求拦截
    const config = requestInterceptor({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: options.header || {}
    })
    
    uni.request({
      ...config,
      success: (res) => {
        responseInterceptor(res)
          .then(resolve)
          .catch(reject)
      },
      fail: (err) => {
        reject(new Error(err.errMsg || '网络请求失败'))
      }
    })
  })
}

// API方法封装
const http = {
  // 认证相关
  sendCode: (data) => request({ url: '/auth/send-code', method: 'POST', data }),
  register: (data) => request({ url: '/auth/register', method: 'POST', data }),
  login: (data) => request({ url: '/auth/login', method: 'POST', data }),
  logout: () => request({ url: '/auth/logout', method: 'POST' }),
  
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

