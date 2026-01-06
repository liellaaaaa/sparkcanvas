"use strict";
const config = {
  // API 基础地址
  // 开发环境（浏览器）：http://localhost:8000
  // 开发环境（真机）：http://你的本机IP:8000，例如：http://192.168.1.100:8000
  // 生产环境：需要配置实际的后端地址
  // 微信小程序环境不支持 process 对象，直接使用默认值
  BASE_URL: "http://47.83.142.3:8000",
  // 请求超时时间（毫秒）
  // 普通请求：15秒
  // LLM 生成需要较长时间，会在具体接口中单独设置
  TIMEOUT: 15e3,
  // Token 存储 key
  TOKEN_KEY: "access_token",
  // 用户信息存储 key
  USER_INFO_KEY: "user_info"
};
exports.config = config;
//# sourceMappingURL=../../.sourcemap/mp-weixin/utils/config.js.map
