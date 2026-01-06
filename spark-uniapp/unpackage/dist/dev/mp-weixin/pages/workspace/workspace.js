"use strict";
const common_vendor = require("../../common/vendor.js");
const utils_http = require("../../utils/http.js");
const _sfc_main = {
  __name: "workspace",
  setup(__props) {
    const platforms = [
      { label: "小红书", value: "xiaohongshu" },
      { label: "抖音", value: "douyin" }
    ];
    const materialSources = [
      { label: "联网检索", value: "online" },
      { label: "RAG知识库", value: "rag" }
    ];
    const sessionId = common_vendor.ref("");
    const sessionInfo = common_vendor.ref({});
    const platform = common_vendor.ref("xiaohongshu");
    const materialSource = common_vendor.ref("online");
    const inputText = common_vendor.ref("");
    const loading = common_vendor.ref(false);
    const regenerating = common_vendor.ref(false);
    const hasResult = common_vendor.ref(false);
    const resultTitle = common_vendor.ref("");
    const resultBody = common_vendor.ref("");
    const resultImageUrl = common_vendor.ref("");
    const resultStatus = common_vendor.ref("");
    const resultTimestamp = common_vendor.ref("");
    const resultBodyLines = common_vendor.computed(() => {
      return resultBody.value ? resultBody.value.split("\n") : [];
    });
    const formatTime = (isoStr) => {
      if (!isoStr)
        return "";
      const d = new Date(isoStr);
      return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, "0")}`;
    };
    const initSession = async () => {
      var _a, _b, _c;
      try {
        loading.value = true;
        const res = await utils_http.http.createSession();
        sessionId.value = ((_a = res == null ? void 0 : res.data) == null ? void 0 : _a.session_id) || "";
        if (sessionId.value) {
          sessionInfo.value = {
            created_at: (_b = res == null ? void 0 : res.data) == null ? void 0 : _b.created_at,
            expires_at: (_c = res == null ? void 0 : res.data) == null ? void 0 : _c.expires_at,
            message_count: 0
          };
        }
      } catch (e) {
        common_vendor.index.__f__("error", "at pages/workspace/workspace.vue:179", "创建工作台会话失败:", e);
        common_vendor.index.showToast({ title: (e == null ? void 0 : e.message) || "创建会话失败", icon: "none" });
      } finally {
        loading.value = false;
      }
    };
    const createNewSession = async () => {
      hasResult.value = false;
      resultTitle.value = "";
      resultBody.value = "";
      resultImageUrl.value = "";
      inputText.value = "";
      await initSession();
      common_vendor.index.showToast({ title: "已创建新会话", icon: "success" });
    };
    const refreshSessionInfo = async () => {
      if (!sessionId.value)
        return;
      try {
        const res = await utils_http.http.getSession(sessionId.value);
        if (res == null ? void 0 : res.data) {
          sessionInfo.value = res.data;
        }
      } catch (e) {
        common_vendor.index.__f__("error", "at pages/workspace/workspace.vue:205", "获取会话信息失败:", e);
        common_vendor.index.showToast({ title: (e == null ? void 0 : e.message) || "获取会话信息失败", icon: "none" });
      }
    };
    const handleGenerate = async () => {
      var _a, _b, _c;
      if (!inputText.value.trim())
        return;
      if (!sessionId.value) {
        await initSession();
        if (!sessionId.value)
          return;
      }
      try {
        loading.value = true;
        const payload = {
          session_id: sessionId.value,
          message: inputText.value,
          material_source: materialSource.value,
          platform: platform.value
        };
        const res = await utils_http.http.sendMessage(payload);
        const content = (_a = res == null ? void 0 : res.data) == null ? void 0 : _a.content;
        if (content) {
          resultTitle.value = content.title || "";
          resultBody.value = content.body || "";
          resultImageUrl.value = content.image_url || "";
          resultStatus.value = ((_b = res == null ? void 0 : res.data) == null ? void 0 : _b.status) || "completed";
          resultTimestamp.value = formatTime((_c = res == null ? void 0 : res.data) == null ? void 0 : _c.timestamp);
          hasResult.value = true;
          await refreshSessionInfo();
        } else {
          common_vendor.index.showToast({ title: "后端未返回内容", icon: "none" });
        }
      } catch (e) {
        common_vendor.index.__f__("error", "at pages/workspace/workspace.vue:241", "发送消息失败:", e);
        common_vendor.index.showToast({ title: (e == null ? void 0 : e.message) || "生成失败，请稍后重试", icon: "none" });
      } finally {
        loading.value = false;
      }
    };
    const handleRegenerate = async () => {
      var _a, _b, _c;
      if (!sessionId.value)
        return;
      try {
        regenerating.value = true;
        const payload = {
          session_id: sessionId.value,
          adjustments: {
            emotion_intensity: "high",
            style_preference: platform.value === "xiaohongshu" ? "小红书爆款" : "抖音热门"
          }
        };
        const res = await utils_http.http.regenerate(payload);
        const content = (_a = res == null ? void 0 : res.data) == null ? void 0 : _a.content;
        if (content) {
          resultTitle.value = content.title || "";
          resultBody.value = content.body || "";
          resultImageUrl.value = content.image_url || "";
          resultStatus.value = ((_b = res == null ? void 0 : res.data) == null ? void 0 : _b.status) || "completed";
          resultTimestamp.value = formatTime((_c = res == null ? void 0 : res.data) == null ? void 0 : _c.timestamp);
          await refreshSessionInfo();
          common_vendor.index.showToast({ title: "重新生成完成", icon: "success" });
        }
      } catch (e) {
        common_vendor.index.__f__("error", "at pages/workspace/workspace.vue:273", "重新生成失败:", e);
        common_vendor.index.showToast({ title: (e == null ? void 0 : e.message) || "重新生成失败", icon: "none" });
      } finally {
        regenerating.value = false;
      }
    };
    const handleCopyResult = () => {
      let content = "";
      if (resultTitle.value) {
        content += resultTitle.value + "\n\n";
      }
      if (resultBody.value) {
        content += resultBody.value;
      }
      if (!content.trim()) {
        common_vendor.index.showToast({
          title: "内容为空，无法复制",
          icon: "none"
        });
        return;
      }
      common_vendor.index.setClipboardData({
        data: content,
        success: () => {
          common_vendor.index.showToast({
            title: "复制成功",
            icon: "success",
            duration: 1500
          });
        },
        fail: (err) => {
          common_vendor.index.__f__("error", "at pages/workspace/workspace.vue:308", "复制失败:", err);
          common_vendor.index.showToast({
            title: "复制失败，请稍后重试",
            icon: "none"
          });
        }
      });
    };
    common_vendor.onLoad(async () => {
      await initSession();
    });
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: sessionId.value
      }, sessionId.value ? common_vendor.e({
        b: common_vendor.t(sessionId.value.slice(0, 8)),
        c: common_vendor.t(sessionInfo.value.message_count || 0),
        d: sessionInfo.value.last_message_time
      }, sessionInfo.value.last_message_time ? {
        e: common_vendor.t(formatTime(sessionInfo.value.last_message_time))
      } : {}, {
        f: common_vendor.o(refreshSessionInfo),
        g: common_vendor.o(createNewSession)
      }) : {}, {
        h: common_vendor.f(platforms, (p, k0, i0) => {
          return {
            a: common_vendor.t(p.label),
            b: p.value,
            c: common_vendor.n(platform.value === p.value ? "tag-primary" : "tag-default"),
            d: common_vendor.o(($event) => platform.value = p.value, p.value)
          };
        }),
        i: common_vendor.f(materialSources, (s, k0, i0) => {
          return {
            a: common_vendor.t(s.label),
            b: s.value,
            c: common_vendor.n(materialSource.value === s.value ? "tag-primary" : "tag-default"),
            d: common_vendor.o(($event) => materialSource.value = s.value, s.value)
          };
        }),
        j: inputText.value,
        k: common_vendor.o(($event) => inputText.value = $event.detail.value),
        l: hasResult.value
      }, hasResult.value ? {
        m: common_vendor.t(regenerating.value ? "重新生成中..." : "🔄 重新生成"),
        n: regenerating.value,
        o: regenerating.value,
        p: common_vendor.o(handleRegenerate)
      } : {}, {
        q: loading.value || !inputText.value.trim(),
        r: common_vendor.o(handleGenerate),
        s: hasResult.value
      }, hasResult.value ? common_vendor.e({
        t: resultStatus.value === "completed"
      }, resultStatus.value === "completed" ? {} : {}, {
        v: resultStatus.value === "completed"
      }, resultStatus.value === "completed" ? {
        w: common_vendor.o(handleCopyResult)
      } : {}, {
        x: common_vendor.t(resultTitle.value),
        y: common_vendor.f(resultBodyLines.value, (line, idx, i0) => {
          return {
            a: common_vendor.t(line),
            b: common_vendor.t(idx < resultBodyLines.value.length - 1 ? "\n" : ""),
            c: idx
          };
        }),
        z: resultImageUrl.value
      }, resultImageUrl.value ? {
        A: resultImageUrl.value
      } : {}, {
        B: common_vendor.t(resultTimestamp.value)
      }) : {});
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-245b3c15"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/workspace/workspace.js.map
