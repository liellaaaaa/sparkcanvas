"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const common_vendor = require("./common/vendor.js");
const utils_storage = require("./utils/storage.js");
if (!Math) {
  "./pages/workspace/workspace.js";
  "./pages/login/login.js";
  "./pages/register/register.js";
  "./pages/history/history.js";
  "./pages/rag/rag.js";
}
const _sfc_main = {
  onLaunch: function() {
    common_vendor.index.__f__("log", "at App.vue:6", "SparkCanvas App Launch");
    this.checkLoginStatus();
  },
  onShow: function() {
    common_vendor.index.__f__("log", "at App.vue:11", "SparkCanvas App Show");
  },
  onHide: function() {
    common_vendor.index.__f__("log", "at App.vue:14", "SparkCanvas App Hide");
  },
  methods: {
    checkLoginStatus() {
      const token = utils_storage.storage.getToken();
      const userInfo = utils_storage.storage.getUserInfo();
      if (token && userInfo) {
        common_vendor.index.__f__("log", "at App.vue:23", "用户已登录:", userInfo);
      } else {
        common_vendor.index.__f__("log", "at App.vue:25", "用户未登录");
      }
    }
  }
};
function createApp() {
  const app = common_vendor.createSSRApp(_sfc_main);
  return {
    app
  };
}
createApp().app.mount("#app");
exports.createApp = createApp;
//# sourceMappingURL=../.sourcemap/mp-weixin/app.js.map
