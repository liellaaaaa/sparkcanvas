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
    // 后端返回格式可能是: { code: 200, message: "success", data: {...}, error: null }
    // 也可能是直接返回数据: { user: {...}, token: "..." }
    if (data && typeof data === 'object') {
      // 检查是否存在 code 字段
      if ('code' in data) {
        // 有 code 字段，按统一格式处理
        if (data.code === 200) {
          // 业务成功，返回完整响应对象（保持 code、message、data 结构）
          // 这样前端可以统一检查 response.code === 200 和访问 response.data
          return Promise.resolve(data)
        } else {
          // 业务错误，返回错误信息
          const errorMsg = data.message || data.error || '请求失败'
          return Promise.reject(new Error(errorMsg))
        }
      } else {
        // 没有 code 字段，直接返回数据（兼容登录等直接返回数据的接口）
        return Promise.resolve(data)
      }
    }
    // 兼容直接返回数据的情况
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
  createSession: () => request({ url: '/api/v1/workspace/create-session', method: 'POST' }),
  sendMessage: (data) => request({ url: '/api/v1/workspace/send-message', method: 'POST', data }),
  getSession: (sessionId) => request({ url: `/api/v1/workspace/session/${sessionId}`, method: 'GET' }),
  uploadMaterial: (data) => request({ url: '/api/v1/workspace/upload-material', method: 'POST', data }),
  regenerate: (data) => request({ url: '/api/v1/workspace/regenerate', method: 'POST', data }),
  
  // 历史记录相关
  getConversations: (params) => {
    // 将params对象转换为URL查询参数
    const queryString = Object.keys(params || {})
      .filter(key => params[key] !== undefined && params[key] !== null)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
      .join('&')
    return request({ 
      url: `/api/v1/history/conversations${queryString ? '?' + queryString : ''}`, 
      method: 'GET' 
    })
  },
  searchHistory: (params) => {
    // 将params对象转换为URL查询参数
    const queryString = Object.keys(params || {})
      .filter(key => params[key] !== undefined && params[key] !== null)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
      .join('&')
    return request({ 
      url: `/api/v1/history/search${queryString ? '?' + queryString : ''}`, 
      method: 'GET' 
    })
  },
  
  // 内容管理相关
  getContents: (params) => request({ url: '/contents/list', method: 'GET', data: params }),
  searchContents: (params) => request({ url: '/contents/search', method: 'GET', data: params }),
  
  // Prompt管理相关
  createPrompt: (data) => request({ url: '/api/v1/prompt/create', method: 'POST', data }),
  getPrompts: (params) => {
    const queryString = Object.keys(params || {})
      .filter(key => params[key] !== undefined && params[key] !== null)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
      .join('&')
    return request({ url: `/api/v1/prompt/list${queryString ? '?' + queryString : ''}`, method: 'GET' })
  },
  updatePrompt: (data) => request({ url: '/api/v1/prompt/update', method: 'PUT', data }),
  deletePrompt: (data) => request({ url: '/api/v1/prompt/delete', method: 'DELETE', data }),
  
  // 配图生成相关
  generateImage: (data) => request({ url: '/image/generate', method: 'POST', data }),
  batchGenerateImage: (data) => request({ url: '/image/batch-generate', method: 'POST', data }),
  
  // RAG知识库相关
  // 上传文档：POST /api/v1/rag/upload (multipart/form-data)
  uploadDocument: (filePath) => {
    return new Promise((resolve, reject) => {
      const token = uni.getStorageSync(config.TOKEN_KEY)
      uni.uploadFile({
        url: BASE_URL + '/api/v1/rag/upload',
        filePath: filePath,
        name: 'file',
        header: {
          'Authorization': token ? `Bearer ${token}` : ''
        },
        success: (res) => {
          // 检查HTTP状态码
          if (res.statusCode === 200) {
            try {
              const data = JSON.parse(res.data)
              if (data.code === 200) {
                resolve(data)
              } else {
                reject(new Error(data.message || data.detail || '上传失败'))
              }
            } catch (e) {
              reject(new Error('响应解析失败'))
            }
          } else if (res.statusCode === 401) {
            // 未授权，清除Token并跳转登录
            uni.removeStorageSync(config.TOKEN_KEY)
            uni.removeStorageSync(config.USER_INFO_KEY)
            uni.reLaunch({
              url: '/pages/login/login'
            })
            reject(new Error('登录已过期，请重新登录'))
          } else {
            // 其他HTTP错误
            try {
              const data = JSON.parse(res.data)
              reject(new Error(data.detail || data.message || `上传失败: ${res.statusCode}`))
            } catch (e) {
              reject(new Error(`上传失败: ${res.statusCode}`))
            }
          }
        },
        fail: (err) => {
          reject(new Error(err.errMsg || '上传失败'))
        }
      })
    })
  },
  
  // 删除文档：DELETE /api/v1/rag/delete (请求体包含 document_id)
  deleteDocument: (documentId) => {
    return request({ 
      url: '/api/v1/rag/delete', 
      method: 'DELETE',
      data: {
        document_id: documentId
      }
    })
  },
  
  // 文档列表：GET /api/v1/rag/list?page=1&page_size=20
  getDocuments: (params) => {
    const queryString = Object.keys(params || {})
      .filter(key => params[key] !== undefined && params[key] !== null)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
      .join('&')
    return request({ 
      url: `/api/v1/rag/list${queryString ? '?' + queryString : ''}`, 
      method: 'GET' 
    })
  },
  
  // 语义检索：POST /api/v1/rag/search
  searchRAG: (data) => request({ 
    url: '/api/v1/rag/search', 
    method: 'POST', 
    data 
  })
}

export default http

