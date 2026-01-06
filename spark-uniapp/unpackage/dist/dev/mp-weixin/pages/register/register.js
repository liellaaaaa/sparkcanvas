"use strict";
const common_vendor = require("../../common/vendor.js");
const utils_http = require("../../utils/http.js");
const utils_storage = require("../../utils/storage.js");
const _sfc_main = {
  __name: "register",
  setup(__props) {
    const formData = common_vendor.reactive({
      username: "",
      email: "",
      verifyCode: "",
      password: "",
      confirmPassword: ""
    });
    const loading = common_vendor.ref(false);
    const codeCountdown = common_vendor.ref(0);
    let countdownTimer = null;
    const validateEmail = (email) => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email);
    };
    const sendCode = async () => {
      if (!formData.email.trim()) {
        common_vendor.index.showToast({ title: "请先输入邮箱", icon: "none" });
        return;
      }
      if (!validateEmail(formData.email)) {
        common_vendor.index.showToast({ title: "请输入正确的邮箱格式", icon: "none" });
        return;
      }
      if (codeCountdown.value > 0) {
        return;
      }
      try {
        common_vendor.index.showLoading({ title: "发送中..." });
        await utils_http.http.sendCode(formData.email.trim());
        common_vendor.index.showToast({ title: "验证码已发送，请查收邮箱", icon: "success", duration: 2e3 });
        codeCountdown.value = 60;
        if (countdownTimer) {
          clearInterval(countdownTimer);
        }
        countdownTimer = setInterval(() => {
          codeCountdown.value--;
          if (codeCountdown.value <= 0) {
            clearInterval(countdownTimer);
            countdownTimer = null;
          }
        }, 1e3);
      } catch (e) {
        common_vendor.index.__f__("error", "at pages/register/register.vue:141", "发送验证码失败:", e);
        common_vendor.index.showToast({
          title: e.message || "验证码发送失败，请稍后重试",
          icon: "none",
          duration: 2e3
        });
      } finally {
        common_vendor.index.hideLoading();
      }
    };
    const handleRegister = async () => {
      if (!formData.username.trim()) {
        common_vendor.index.showToast({ title: "请输入用户名", icon: "none" });
        return;
      }
      if (formData.username.trim().length < 3 || formData.username.trim().length > 20) {
        common_vendor.index.showToast({ title: "用户名长度为3-20个字符", icon: "none" });
        return;
      }
      if (!formData.email.trim()) {
        common_vendor.index.showToast({ title: "请输入邮箱", icon: "none" });
        return;
      }
      if (!validateEmail(formData.email)) {
        common_vendor.index.showToast({ title: "请输入正确的邮箱格式", icon: "none" });
        return;
      }
      if (!formData.verifyCode.trim()) {
        common_vendor.index.showToast({ title: "请输入验证码", icon: "none" });
        return;
      }
      if (formData.verifyCode.trim().length !== 4) {
        common_vendor.index.showToast({ title: "验证码为4位数字", icon: "none" });
        return;
      }
      if (!formData.password.trim()) {
        common_vendor.index.showToast({ title: "请输入密码", icon: "none" });
        return;
      }
      if (formData.password.length < 6 || formData.password.length > 20) {
        common_vendor.index.showToast({ title: "密码长度为6-20个字符", icon: "none" });
        return;
      }
      if (!formData.confirmPassword.trim()) {
        common_vendor.index.showToast({ title: "请确认密码", icon: "none" });
        return;
      }
      if (formData.password !== formData.confirmPassword) {
        common_vendor.index.showToast({ title: "两次输入的密码不一致", icon: "none" });
        return;
      }
      loading.value = true;
      common_vendor.index.showLoading({ title: "注册中..." });
      try {
        await utils_http.http.register({
          username: formData.username.trim(),
          email: formData.email.trim(),
          password: formData.password,
          confirm_password: formData.confirmPassword,
          code: formData.verifyCode.trim()
        });
        common_vendor.index.showToast({ title: "注册成功", icon: "success" });
        setTimeout(async () => {
          try {
            const loginResult = await utils_http.http.login({
              email: formData.email.trim(),
              password: formData.password
            });
            utils_storage.storage.setToken(loginResult.token);
            utils_storage.storage.setUserInfo(loginResult.user);
            common_vendor.index.switchTab({
              url: "/pages/workspace/workspace"
            });
          } catch (e) {
            common_vendor.index.__f__("error", "at pages/register/register.vue:238", "自动登录失败:", e);
            common_vendor.index.showToast({
              title: "注册成功，请登录",
              icon: "success"
            });
            setTimeout(() => {
              common_vendor.index.navigateTo({
                url: "/pages/login/login"
              });
            }, 1500);
          }
        }, 1500);
      } catch (e) {
        common_vendor.index.__f__("error", "at pages/register/register.vue:251", "注册失败:", e);
        common_vendor.index.showToast({
          title: e.message || "注册失败，请检查信息后重试",
          icon: "none",
          duration: 2e3
        });
      } finally {
        loading.value = false;
        common_vendor.index.hideLoading();
      }
    };
    const goToLogin = () => {
      common_vendor.index.navigateTo({
        url: "/pages/login/login"
      });
    };
    common_vendor.onUnmounted(() => {
      if (countdownTimer) {
        clearInterval(countdownTimer);
        countdownTimer = null;
      }
    });
    return (_ctx, _cache) => {
      return {
        a: formData.username,
        b: common_vendor.o(($event) => formData.username = $event.detail.value),
        c: formData.email,
        d: common_vendor.o(($event) => formData.email = $event.detail.value),
        e: formData.verifyCode,
        f: common_vendor.o(($event) => formData.verifyCode = $event.detail.value),
        g: common_vendor.t(codeCountdown.value > 0 ? `${codeCountdown.value}s` : "发送验证码"),
        h: common_vendor.o(sendCode),
        i: codeCountdown.value > 0,
        j: formData.password,
        k: common_vendor.o(($event) => formData.password = $event.detail.value),
        l: formData.confirmPassword,
        m: common_vendor.o(($event) => formData.confirmPassword = $event.detail.value),
        n: common_vendor.t(loading.value ? "注册中..." : "注册"),
        o: common_vendor.o(handleRegister),
        p: loading.value,
        q: common_vendor.o(goToLogin)
      };
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-bac4a35d"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/register/register.js.map
