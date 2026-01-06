"use strict";
const common_vendor = require("../../common/vendor.js");
const utils_http = require("../../utils/http.js");
const _sfc_main = {
  __name: "history",
  setup(__props) {
    const historyList = common_vendor.ref([]);
    const loading = common_vendor.ref(false);
    const page = common_vendor.ref(1);
    const pageSize = common_vendor.ref(20);
    const total = common_vendor.ref(0);
    const searchKeyword = common_vendor.ref("");
    const isSearchMode = common_vendor.ref(false);
    const expandedItems = common_vendor.ref({});
    const totalPages = common_vendor.ref(0);
    const formatTime = (timeStr) => {
      if (!timeStr)
        return "";
      const date = new Date(timeStr);
      const now = /* @__PURE__ */ new Date();
      const diff = now - date;
      if (diff < 6e4) {
        return "刚刚";
      }
      if (diff < 36e5) {
        return `${Math.floor(diff / 6e4)}分钟前`;
      }
      if (diff < 864e5) {
        return `${Math.floor(diff / 36e5)}小时前`;
      }
      if (diff < 6048e5) {
        return `${Math.floor(diff / 864e5)}天前`;
      }
      return date.toLocaleDateString("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit"
      });
    };
    const loadHistory = async (resetPage = false) => {
      if (resetPage) {
        page.value = 1;
      }
      loading.value = true;
      try {
        let response;
        if (isSearchMode.value && searchKeyword.value.trim()) {
          response = await utils_http.http.searchHistory({
            keyword: searchKeyword.value.trim(),
            page: page.value,
            page_size: pageSize.value
          });
        } else {
          response = await utils_http.http.getConversations({
            page: page.value,
            page_size: pageSize.value
          });
        }
        if (response.code === 200) {
          historyList.value = response.data.items || [];
          total.value = response.data.total || 0;
          totalPages.value = Math.ceil(total.value / pageSize.value);
          expandedItems.value = {};
        } else {
          common_vendor.index.showToast({
            title: response.message || "加载失败",
            icon: "none"
          });
        }
      } catch (error) {
        common_vendor.index.__f__("error", "at pages/history/history.vue:186", "加载历史记录失败:", error);
        common_vendor.index.showToast({
          title: error.message || "加载失败",
          icon: "none"
        });
      } finally {
        loading.value = false;
      }
    };
    const handleSearch = () => {
      if (!searchKeyword.value.trim()) {
        common_vendor.index.showToast({
          title: "请输入搜索关键词",
          icon: "none"
        });
        return;
      }
      isSearchMode.value = true;
      loadHistory(true);
    };
    const cancelSearch = () => {
      isSearchMode.value = false;
      searchKeyword.value = "";
      loadHistory(true);
    };
    const loadPage = (newPage) => {
      if (newPage < 1 || newPage > totalPages.value) {
        return;
      }
      page.value = newPage;
      loadHistory();
    };
    const getPreviewText = (text) => {
      if (!text)
        return "";
      const lines = text.split("\n");
      if (lines.length <= 5) {
        return text;
      }
      return lines.slice(0, 5).join("\n");
    };
    const needsExpand = (text) => {
      if (!text)
        return false;
      const lines = text.split("\n");
      return lines.length > 5;
    };
    const getItemKey = (item) => {
      return `${item.session_id}-${item.timestamp}`;
    };
    const isExpanded = (item) => {
      return expandedItems.value[getItemKey(item)] || false;
    };
    const toggleExpand = (item) => {
      const key = getItemKey(item);
      expandedItems.value[key] = !expandedItems.value[key];
    };
    const handleCopy = (item) => {
      const content = item.response || "";
      if (!content) {
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
          common_vendor.index.__f__("error", "at pages/history/history.vue:279", "复制失败:", err);
          common_vendor.index.showToast({
            title: "复制失败，请稍后重试",
            icon: "none"
          });
        }
      });
    };
    const handleDelete = (item) => {
      common_vendor.index.showModal({
        title: "确认删除",
        content: "确定要删除这条历史记录吗？此操作不可恢复。",
        success: async (res) => {
          if (res.confirm) {
            try {
              await utils_http.http.deleteHistory({
                session_id: item.session_id,
                timestamp: item.timestamp
              });
              common_vendor.index.showToast({
                title: "删除成功",
                icon: "success"
              });
              await loadHistory();
            } catch (error) {
              common_vendor.index.__f__("error", "at pages/history/history.vue:307", "删除失败:", error);
              common_vendor.index.showToast({
                title: error.message || "删除失败，请稍后重试",
                icon: "none",
                duration: 2e3
              });
            }
          }
        }
      });
    };
    common_vendor.onMounted(() => {
      loadHistory();
    });
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.o(handleSearch),
        b: searchKeyword.value,
        c: common_vendor.o(($event) => searchKeyword.value = $event.detail.value),
        d: common_vendor.o(handleSearch),
        e: isSearchMode.value
      }, isSearchMode.value ? {
        f: common_vendor.t(searchKeyword.value),
        g: common_vendor.o(cancelSearch)
      } : {}, {
        h: loading.value
      }, loading.value ? {} : historyList.value.length === 0 ? {} : {
        j: common_vendor.f(historyList.value, (item, index, i0) => {
          return common_vendor.e({
            a: common_vendor.t(item.session_id.slice(0, 8)),
            b: common_vendor.t(formatTime(item.timestamp)),
            c: common_vendor.o(($event) => handleDelete(item), `${item.session_id}-${item.timestamp}`),
            d: common_vendor.t(item.message),
            e: common_vendor.t(isExpanded(item) ? item.response : getPreviewText(item.response)),
            f: isExpanded(item) ? 1 : "",
            g: common_vendor.o(($event) => handleCopy(item), `${item.session_id}-${item.timestamp}`),
            h: needsExpand(item.response)
          }, needsExpand(item.response) ? {
            i: common_vendor.t(isExpanded(item) ? "收起" : "展开"),
            j: common_vendor.o(($event) => toggleExpand(item), `${item.session_id}-${item.timestamp}`)
          } : {}, {
            k: `${item.session_id}-${item.timestamp}`
          });
        })
      }, {
        i: historyList.value.length === 0,
        k: total.value > 0
      }, total.value > 0 ? {
        l: page.value === 1,
        m: common_vendor.o(($event) => loadPage(page.value - 1)),
        n: common_vendor.t(page.value),
        o: common_vendor.t(totalPages.value),
        p: common_vendor.t(total.value),
        q: page.value >= totalPages.value,
        r: common_vendor.o(($event) => loadPage(page.value + 1))
      } : {});
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-b2d018fa"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/history/history.js.map
