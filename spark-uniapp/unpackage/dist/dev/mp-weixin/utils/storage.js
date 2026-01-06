"use strict";
const common_vendor = require("../common/vendor.js");
const storage = {
  // 设置存储
  set(key, value) {
    try {
      common_vendor.index.setStorageSync(key, value);
      return true;
    } catch (e) {
      common_vendor.index.__f__("error", "at utils/storage.js:13", "存储失败:", e);
      return false;
    }
  },
  // 获取存储
  get(key, defaultValue = null) {
    try {
      const value = common_vendor.index.getStorageSync(key);
      return value !== "" ? value : defaultValue;
    } catch (e) {
      common_vendor.index.__f__("error", "at utils/storage.js:24", "读取存储失败:", e);
      return defaultValue;
    }
  },
  // 删除存储
  remove(key) {
    try {
      common_vendor.index.removeStorageSync(key);
      return true;
    } catch (e) {
      common_vendor.index.__f__("error", "at utils/storage.js:35", "删除存储失败:", e);
      return false;
    }
  },
  // 清空所有存储
  clear() {
    try {
      common_vendor.index.clearStorageSync();
      return true;
    } catch (e) {
      common_vendor.index.__f__("error", "at utils/storage.js:46", "清空存储失败:", e);
      return false;
    }
  },
  // Token相关
  setToken(token) {
    return this.set("access_token", token);
  },
  getToken() {
    return this.get("access_token");
  },
  removeToken() {
    return this.remove("access_token");
  },
  // 用户信息相关
  setUserInfo(userInfo) {
    return this.set("user_info", userInfo);
  },
  getUserInfo() {
    return this.get("user_info");
  },
  removeUserInfo() {
    return this.remove("user_info");
  }
};
exports.storage = storage;
//# sourceMappingURL=../../.sourcemap/mp-weixin/utils/storage.js.map
