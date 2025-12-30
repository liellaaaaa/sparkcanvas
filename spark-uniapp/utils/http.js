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
      timeout: options.timeout || config.TIMEOUT // 支持每个请求单独设置超时时间
    })
    
    // 对于 POST/PUT/DELETE 请求，确保数据正确序列化
    // uni.request 在 Content-Type 为 application/json 时会自动序列化，但我们需要确保数据格式正确
    if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(requestConfig.method.toUpperCase()) && requestConfig.data) {
      // 确保 data 是对象格式，uni.request 会自动序列化为 JSON
      if (typeof requestConfig.data === 'string') {
        try {
          requestConfig.data = JSON.parse(requestConfig.data)
        } catch (e) {
          // 如果已经是字符串且无法解析，保持原样
        }
      }
    }
    
    // 添加调试日志
    console.log('发送请求:', {
      url: requestConfig.url,
      method: requestConfig.method,
      data: requestConfig.data,
      header: requestConfig.header,
      timeout: requestConfig.timeout
    })
    
    uni.request({
      url: requestConfig.url,
      method: requestConfig.method,
      data: requestConfig.data,
      header: requestConfig.header,
      timeout: requestConfig.timeout,
      dataType: 'json',
      success: (res) => {
        console.log('请求成功:', {
          statusCode: res.statusCode,
          data: res.data
        })
        responseInterceptor(res)
          .then(resolve)
          .catch(reject)
      },
      fail: (err) => {
        console.error('请求失败:', err)
        console.error('请求配置:', {
          url: requestConfig.url,
          method: requestConfig.method,
          timeout: requestConfig.timeout
        })
        let errorMsg = err.errMsg || '网络请求失败'
        
        // 提供更友好的错误提示
        if (errorMsg.includes('timeout')) {
          errorMsg = `请求超时（${requestConfig.timeout}ms），请检查：\n1. 后端服务是否已启动（访问 http://localhost:8000/health 测试）\n2. 后端服务是否正常运行\n3. 数据库连接是否正常\n4. 检查浏览器控制台是否有CORS错误`
        } else if (errorMsg.includes('fail') || errorMsg.includes('connect')) {
          errorMsg = `无法连接到服务器（${requestConfig.url}），请检查：\n1. 后端服务是否已启动\n2. 后端服务是否监听在正确的地址和端口\n3. 防火墙是否阻止了连接\n4. 检查浏览器控制台是否有CORS错误`
        }
        
        reject(new Error(errorMsg))
      }
    })
  })
}

// API方法封装
const http = {
  // 测试连接
  testConnection: () => request({ 
    url: '/health', 
    method: 'GET',
    timeout: 5000 // 健康检查5秒超时即可
  }),
  
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
    data,
    timeout: 15000 // 登录接口15秒超时，给数据库查询等操作留出时间
  }),
  
  logout: () => {
    // 清除本地存储
    uni.removeStorageSync(config.TOKEN_KEY)
    uni.removeStorageSync(config.USER_INFO_KEY)
    return Promise.resolve()
  },
  
  // 工作台相关
  createSession: () => request({ url: '/api/v1/workspace/create-session', method: 'POST', timeout: 10000 }),
  sendMessage: (data) => request({ url: '/api/v1/workspace/send-message', method: 'POST', data, timeout: 60000 }), // LLM 生成需要更长时间
  getSession: (sessionId) => request({ url: `/api/v1/workspace/session/${sessionId}`, method: 'GET', timeout: 10000 }),
  regenerate: (data) => request({ url: '/api/v1/workspace/regenerate', method: 'POST', data, timeout: 60000 }), // LLM 生成需要更长时间
  
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
  deleteHistory: (data) => request({ 
    url: '/api/v1/history/delete', 
    method: 'DELETE', 
    data 
  }),
  
  // 内容管理相关
  getContents: (params) => request({ url: '/contents/list', method: 'GET', data: params }),
  searchContents: (params) => request({ url: '/contents/search', method: 'GET', data: params }),
  
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

