"use strict";
const common_vendor = require("../../common/vendor.js");
const utils_http = require("../../utils/http.js");
const utils_storage = require("../../utils/storage.js");
const _sfc_main = {
  __name: "login",
  setup(__props) {
    const formData = common_vendor.reactive({
      email: "",
      password: ""
    });
    const loading = common_vendor.ref(false);
    const validateEmail = (email) => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email);
    };
    const handleLogin = async () => {
      if (!formData.email.trim()) {
        common_vendor.index.showToast({ title: "请输入邮箱", icon: "none" });
        return;
      }
      if (!validateEmail(formData.email)) {
        common_vendor.index.showToast({ title: "请输入正确的邮箱格式", icon: "none" });
        return;
      }
      if (!formData.password.trim()) {
        common_vendor.index.showToast({ title: "请输入密码", icon: "none" });
        return;
      }
      if (formData.password.length < 6) {
        common_vendor.index.showToast({ title: "密码长度至少6位", icon: "none" });
        return;
      }
      loading.value = true;
      common_vendor.index.showLoading({ title: "登录中..." });
      try {
        const result = await utils_http.http.login({
          email: formData.email.trim(),
          password: formData.password
        });
        utils_storage.storage.setToken(result.token);
        utils_storage.storage.setUserInfo(result.user);
        common_vendor.index.showToast({ title: "登录成功", icon: "success" });
        setTimeout(() => {
          common_vendor.index.switchTab({
            url: "/pages/workspace/workspace"
          });
        }, 1500);
      } catch (e) {
        common_vendor.index.__f__("error", "at pages/login/login.vue:113", "登录失败:", e);
        let errorMessage = e.message || "登录失败，请检查邮箱和密码";
        if (errorMessage.includes("超时") || errorMessage.includes("连接")) {
          common_vendor.index.showModal({
            title: "连接失败",
            content: errorMessage + "\n\n请检查：\n1. 后端服务是否已启动（运行 python spark-backend/main.py）\n2. 访问 http://localhost:8000/health 测试后端是否正常\n3. 检查后端日志是否有错误信息",
            showCancel: false,
            confirmText: "我知道了"
          });
        } else {
          common_vendor.index.showToast({
            title: errorMessage,
            icon: "none",
            duration: 3e3
          });
        }
      } finally {
        loading.value = false;
        common_vendor.index.hideLoading();
      }
    };
    const goToRegister = () => {
      common_vendor.index.navigateTo({
        url: "/pages/register/register"
      });
    };
    return (_ctx, _cache) => {
      return {
        a: formData.email,
        b: common_vendor.o(($event) => formData.email = $event.detail.value),
        c: formData.password,
        d: common_vendor.o(($event) => formData.password = $event.detail.value),
        e: common_vendor.t(loading.value ? "登录中..." : "登录"),
        f: common_vendor.o(handleLogin),
        g: loading.value,
        h: common_vendor.o(goToRegister)
      };
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-e4e4508d"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/login/login.js.map
