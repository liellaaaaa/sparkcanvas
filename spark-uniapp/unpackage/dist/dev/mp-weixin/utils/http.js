"use strict";
const common_vendor = require("../common/vendor.js");
const utils_config = require("./config.js");
const BASE_URL = utils_config.config.BASE_URL;
const requestInterceptor = (options) => {
  const token = common_vendor.index.getStorageSync(utils_config.config.TOKEN_KEY);
  if (token) {
    options.header = {
      ...options.header,
      "Authorization": `Bearer ${token}`
    };
  }
  options.header = {
    "Content-Type": "application/json",
    ...options.header
  };
  return options;
};
const responseInterceptor = (response) => {
  const { statusCode, data } = response;
  if (statusCode === 200) {
    if (data && typeof data === "object") {
      if ("code" in data) {
        if (data.code === 200) {
          return Promise.resolve(data);
        } else {
          const errorMsg = data.message || data.error || "请求失败";
          return Promise.reject(new Error(errorMsg));
        }
      } else {
        return Promise.resolve(data);
      }
    }
    return Promise.resolve(data);
  } else if (statusCode === 400) {
    const errorMsg = (data == null ? void 0 : data.detail) || (data == null ? void 0 : data.message) || "请求参数错误";
    return Promise.reject(new Error(errorMsg));
  } else if (statusCode === 401) {
    common_vendor.index.removeStorageSync(utils_config.config.TOKEN_KEY);
    common_vendor.index.removeStorageSync(utils_config.config.USER_INFO_KEY);
    common_vendor.index.reLaunch({
      url: "/pages/login/login"
    });
    return Promise.reject(new Error("登录已过期，请重新登录"));
  } else if (statusCode === 403) {
    return Promise.reject(new Error((data == null ? void 0 : data.detail) || "无权限访问"));
  } else if (statusCode === 500) {
    return Promise.reject(new Error((data == null ? void 0 : data.detail) || "服务器错误"));
  } else {
    return Promise.reject(new Error((data == null ? void 0 : data.detail) || `请求失败: ${statusCode}`));
  }
};
const request = (options) => {
  return new Promise((resolve, reject) => {
    const requestConfig = requestInterceptor({
      url: BASE_URL + options.url,
      method: options.method || "GET",
      data: options.data,
      header: options.header || {},
      timeout: options.timeout || utils_config.config.TIMEOUT
      // 支持每个请求单独设置超时时间
    });
    if (["POST", "PUT", "DELETE", "PATCH"].includes(requestConfig.method.toUpperCase()) && requestConfig.data) {
      if (typeof requestConfig.data === "string") {
        try {
          requestConfig.data = JSON.parse(requestConfig.data);
        } catch (e) {
        }
      }
    }
    common_vendor.index.__f__("log", "at utils/http.js:106", "发送请求:", {
      url: requestConfig.url,
      method: requestConfig.method,
      data: requestConfig.data,
      header: requestConfig.header,
      timeout: requestConfig.timeout
    });
    common_vendor.index.request({
      url: requestConfig.url,
      method: requestConfig.method,
      data: requestConfig.data,
      header: requestConfig.header,
      timeout: requestConfig.timeout,
      dataType: "json",
      success: (res) => {
        common_vendor.index.__f__("log", "at utils/http.js:122", "请求成功:", {
          statusCode: res.statusCode,
          data: res.data
        });
        responseInterceptor(res).then(resolve).catch(reject);
      },
      fail: (err) => {
        common_vendor.index.__f__("error", "at utils/http.js:131", "请求失败:", err);
        common_vendor.index.__f__("error", "at utils/http.js:132", "请求配置:", {
          url: requestConfig.url,
          method: requestConfig.method,
          timeout: requestConfig.timeout
        });
        let errorMsg = err.errMsg || "网络请求失败";
        if (errorMsg.includes("timeout")) {
          errorMsg = `请求超时（${requestConfig.timeout}ms），请检查：
1. 后端服务是否已启动（访问 http://localhost:8000/health 测试）
2. 后端服务是否正常运行
3. 数据库连接是否正常
4. 检查浏览器控制台是否有CORS错误`;
        } else if (errorMsg.includes("fail") || errorMsg.includes("connect")) {
          errorMsg = `无法连接到服务器（${requestConfig.url}），请检查：
1. 后端服务是否已启动
2. 后端服务是否监听在正确的地址和端口
3. 防火墙是否阻止了连接
4. 检查浏览器控制台是否有CORS错误`;
        }
        reject(new Error(errorMsg));
      }
    });
  });
};
const http = {
  // 测试连接
  testConnection: () => request({
    url: "/health",
    method: "GET",
    timeout: 5e3
    // 健康检查5秒超时即可
  }),
  // 认证相关
  // 发送验证码：GET /auth/code?email=xxx
  sendCode: (email) => request({
    url: `/auth/code?email=${encodeURIComponent(email)}`,
    method: "GET"
  }),
  // 用户注册：POST /auth/register
  register: (data) => request({
    url: "/auth/register",
    method: "POST",
    data
  }),
  // 用户登录：POST /auth/login
  login: (data) => request({
    url: "/auth/login",
    method: "POST",
    data,
    timeout: 15e3
    // 登录接口15秒超时，给数据库查询等操作留出时间
  }),
  logout: () => {
    common_vendor.index.removeStorageSync(utils_config.config.TOKEN_KEY);
    common_vendor.index.removeStorageSync(utils_config.config.USER_INFO_KEY);
    return Promise.resolve();
  },
  // 工作台相关
  createSession: () => request({ url: "/api/v1/workspace/create-session", method: "POST", timeout: 1e4 }),
  sendMessage: (data) => request({ url: "/api/v1/workspace/send-message", method: "POST", data, timeout: 12e4 }),
  // LLM 生成需要更长时间
  getSession: (sessionId) => request({ url: `/api/v1/workspace/session/${sessionId}`, method: "GET", timeout: 1e4 }),
  regenerate: (data) => request({ url: "/api/v1/workspace/regenerate", method: "POST", data, timeout: 12e4 }),
  // LLM 生成需要更长时间
  // 历史记录相关
  getConversations: (params) => {
    const queryString = Object.keys(params || {}).filter((key) => params[key] !== void 0 && params[key] !== null).map((key) => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`).join("&");
    return request({
      url: `/api/v1/history/conversations${queryString ? "?" + queryString : ""}`,
      method: "GET"
    });
  },
  searchHistory: (params) => {
    const queryString = Object.keys(params || {}).filter((key) => params[key] !== void 0 && params[key] !== null).map((key) => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`).join("&");
    return request({
      url: `/api/v1/history/search${queryString ? "?" + queryString : ""}`,
      method: "GET"
    });
  },
  deleteHistory: (data) => request({
    url: "/api/v1/history/delete",
    method: "DELETE",
    data
  }),
  // 内容管理相关
  getContents: (params) => request({ url: "/contents/list", method: "GET", data: params }),
  searchContents: (params) => request({ url: "/contents/search", method: "GET", data: params }),
  // 配图生成相关
  generateImage: (data) => request({ url: "/image/generate", method: "POST", data }),
  batchGenerateImage: (data) => request({ url: "/image/batch-generate", method: "POST", data }),
  // RAG知识库相关
  // 上传文档：POST /api/v1/rag/upload (multipart/form-data)
  uploadDocument: (filePath) => {
    return new Promise((resolve, reject) => {
      const token = common_vendor.index.getStorageSync(utils_config.config.TOKEN_KEY);
      common_vendor.index.uploadFile({
        url: BASE_URL + "/api/v1/rag/upload",
        filePath,
        name: "file",
        header: {
          "Authorization": token ? `Bearer ${token}` : ""
        },
        success: (res) => {
          if (res.statusCode === 200) {
            try {
              const data = JSON.parse(res.data);
              if (data.code === 200) {
                resolve(data);
              } else {
                reject(new Error(data.message || data.detail || "上传失败"));
              }
            } catch (e) {
              reject(new Error("响应解析失败"));
            }
          } else if (res.statusCode === 401) {
            common_vendor.index.removeStorageSync(utils_config.config.TOKEN_KEY);
            common_vendor.index.removeStorageSync(utils_config.config.USER_INFO_KEY);
            common_vendor.index.reLaunch({
              url: "/pages/login/login"
            });
            reject(new Error("登录已过期，请重新登录"));
          } else {
            try {
              const data = JSON.parse(res.data);
              reject(new Error(data.detail || data.message || `上传失败: ${res.statusCode}`));
            } catch (e) {
              reject(new Error(`上传失败: ${res.statusCode}`));
            }
          }
        },
        fail: (err) => {
          reject(new Error(err.errMsg || "上传失败"));
        }
      });
    });
  },
  // 删除文档：DELETE /api/v1/rag/delete (请求体包含 document_id)
  deleteDocument: (documentId) => {
    return request({
      url: "/api/v1/rag/delete",
      method: "DELETE",
      data: {
        document_id: documentId
      }
    });
  },
  // 文档列表：GET /api/v1/rag/list?page=1&page_size=20
  getDocuments: (params) => {
    const queryString = Object.keys(params || {}).filter((key) => params[key] !== void 0 && params[key] !== null).map((key) => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`).join("&");
    return request({
      url: `/api/v1/rag/list${queryString ? "?" + queryString : ""}`,
      method: "GET"
    });
  },
  // 语义检索：POST /api/v1/rag/search
  searchRAG: (data) => request({
    url: "/api/v1/rag/search",
    method: "POST",
    data
  })
};
exports.http = http;
//# sourceMappingURL=../../.sourcemap/mp-weixin/utils/http.js.map
