"use strict";
const common_vendor = require("../../common/vendor.js");
const utils_http = require("../../utils/http.js");
const _sfc_main = {
  __name: "rag",
  setup(__props) {
    const documentList = common_vendor.ref([]);
    const searchResults = common_vendor.ref([]);
    const loading = common_vendor.ref(false);
    const uploading = common_vendor.ref(false);
    const page = common_vendor.ref(1);
    const pageSize = common_vendor.ref(20);
    const total = common_vendor.ref(0);
    const searchQuery = common_vendor.ref("");
    const isSearchMode = common_vendor.ref(false);
    const totalPages = common_vendor.computed(() => {
      return Math.ceil(total.value / pageSize.value);
    });
    const formatFileSize = (bytes) => {
      if (!bytes)
        return "0 B";
      if (bytes < 1024)
        return bytes + " B";
      if (bytes < 1024 * 1024)
        return (bytes / 1024).toFixed(1) + " KB";
      return (bytes / (1024 * 1024)).toFixed(1) + " MB";
    };
    const formatDistance = (distance) => {
      const value = Number(distance);
      if (Number.isNaN(value))
        return "-";
      return value.toFixed(3);
    };
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
    const handleChooseFile = () => {
      common_vendor.index.chooseFile({
        count: 1,
        extension: [".pdf", ".doc", ".docx", ".txt"],
        success: (res) => {
          if (res.tempFiles && res.tempFiles.length > 0) {
            const file = res.tempFiles[0];
            if (file.size > 50 * 1024 * 1024) {
              common_vendor.index.showToast({
                title: "文件大小不能超过50MB",
                icon: "none"
              });
              return;
            }
            uploadDocument(file.path);
          }
        },
        fail: (err) => {
          common_vendor.index.__f__("error", "at pages/rag/rag.vue:199", "选择文件失败:", err);
          common_vendor.index.showToast({
            title: err.errMsg || "选择文件失败",
            icon: "none"
          });
        }
      });
    };
    const uploadDocument = async (filePath) => {
      uploading.value = true;
      try {
        const response = await utils_http.http.uploadDocument(filePath);
        if (response.code === 200) {
          common_vendor.index.showToast({
            title: "上传成功",
            icon: "success"
          });
          loadDocuments(true);
        } else {
          common_vendor.index.showToast({
            title: response.message || "上传失败",
            icon: "none"
          });
        }
      } catch (error) {
        common_vendor.index.__f__("error", "at pages/rag/rag.vue:227", "上传文档失败:", error);
        common_vendor.index.showToast({
          title: error.message || "上传失败",
          icon: "none"
        });
      } finally {
        uploading.value = false;
      }
    };
    const loadDocuments = async (resetPage = false) => {
      if (resetPage) {
        page.value = 1;
      }
      loading.value = true;
      try {
        const response = await utils_http.http.getDocuments({
          page: page.value,
          page_size: pageSize.value
        });
        if (response.code === 200) {
          documentList.value = response.data.items || [];
          total.value = response.data.total || 0;
        } else {
          common_vendor.index.showToast({
            title: response.message || "加载失败",
            icon: "none"
          });
        }
      } catch (error) {
        common_vendor.index.__f__("error", "at pages/rag/rag.vue:260", "加载文档列表失败:", error);
        common_vendor.index.showToast({
          title: error.message || "加载失败",
          icon: "none"
        });
      } finally {
        loading.value = false;
      }
    };
    const handleSearch = async () => {
      if (!searchQuery.value.trim()) {
        common_vendor.index.showToast({
          title: "请输入搜索关键词",
          icon: "none"
        });
        return;
      }
      isSearchMode.value = true;
      loading.value = true;
      try {
        const response = await utils_http.http.searchRAG({
          query: searchQuery.value.trim(),
          top_k: 5
        });
        if (response.code === 200) {
          searchResults.value = response.data.results || [];
          if (searchResults.value.length === 0) {
            common_vendor.index.showToast({
              title: "未找到相关文档",
              icon: "none"
            });
          }
        } else {
          common_vendor.index.showToast({
            title: response.message || "搜索失败",
            icon: "none"
          });
        }
      } catch (error) {
        common_vendor.index.__f__("error", "at pages/rag/rag.vue:304", "搜索失败:", error);
        common_vendor.index.showToast({
          title: error.message || "搜索失败",
          icon: "none"
        });
      } finally {
        loading.value = false;
      }
    };
    const cancelSearch = () => {
      isSearchMode.value = false;
      searchQuery.value = "";
      searchResults.value = [];
      loadDocuments(true);
    };
    const handleDelete = (documentId, fileName) => {
      common_vendor.index.showModal({
        title: "确认删除",
        content: `确定要删除文档 "${fileName}" 吗？`,
        success: async (res) => {
          if (res.confirm) {
            await deleteDocument(documentId);
          }
        }
      });
    };
    const deleteDocument = async (documentId) => {
      try {
        const response = await utils_http.http.deleteDocument(documentId);
        if (response.code === 200) {
          common_vendor.index.showToast({
            title: "删除成功",
            icon: "success"
          });
          loadDocuments(true);
        } else {
          common_vendor.index.showToast({
            title: response.message || "删除失败",
            icon: "none"
          });
        }
      } catch (error) {
        common_vendor.index.__f__("error", "at pages/rag/rag.vue:353", "删除文档失败:", error);
        common_vendor.index.showToast({
          title: error.message || "删除失败",
          icon: "none"
        });
      }
    };
    const loadPage = (newPage) => {
      if (newPage < 1 || newPage > totalPages.value) {
        return;
      }
      page.value = newPage;
      loadDocuments();
    };
    common_vendor.onMounted(() => {
      loadDocuments();
    });
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.o(handleChooseFile),
        b: uploading.value
      }, uploading.value ? {} : {}, {
        c: common_vendor.o(handleSearch),
        d: searchQuery.value,
        e: common_vendor.o(($event) => searchQuery.value = $event.detail.value),
        f: common_vendor.o(handleSearch),
        g: isSearchMode.value
      }, isSearchMode.value ? {
        h: common_vendor.t(searchQuery.value),
        i: common_vendor.o(cancelSearch)
      } : {}, {
        j: isSearchMode.value && searchResults.value.length > 0
      }, isSearchMode.value && searchResults.value.length > 0 ? {
        k: common_vendor.t(searchResults.value.length),
        l: common_vendor.f(searchResults.value, (result, index, i0) => {
          return {
            a: common_vendor.t(formatDistance(result.distance)),
            b: common_vendor.t(result.metadata.file_name),
            c: common_vendor.t(result.content),
            d: index
          };
        })
      } : {}, {
        m: !isSearchMode.value
      }, !isSearchMode.value ? common_vendor.e({
        n: common_vendor.t(total.value),
        o: loading.value
      }, loading.value ? {} : documentList.value.length === 0 ? {} : {
        q: common_vendor.f(documentList.value, (doc, index, i0) => {
          return {
            a: common_vendor.t(doc.file_name),
            b: common_vendor.t(formatFileSize(doc.file_size)),
            c: common_vendor.t(doc.chunks_count),
            d: common_vendor.t(formatTime(doc.uploaded_at)),
            e: common_vendor.o(($event) => handleDelete(doc.document_id, doc.file_name), doc.document_id),
            f: doc.document_id
          };
        })
      }, {
        p: documentList.value.length === 0
      }) : {}, {
        r: !isSearchMode.value && total.value > 0
      }, !isSearchMode.value && total.value > 0 ? {
        s: page.value === 1,
        t: common_vendor.o(($event) => loadPage(page.value - 1)),
        v: common_vendor.t(page.value),
        w: common_vendor.t(totalPages.value),
        x: common_vendor.t(total.value),
        y: page.value >= totalPages.value,
        z: common_vendor.o(($event) => loadPage(page.value + 1))
      } : {});
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-b694027e"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/rag/rag.js.map
