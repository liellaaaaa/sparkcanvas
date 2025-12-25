<template>
  <view class="rag-page">
    <view class="header">
      <text class="title">📖 知识库</text>
    </view>
    
    <!-- 上传文档卡片 -->
    <view class="upload-card card">
      <view class="upload-section">
        <button class="btn btn-primary btn-upload" @click="handleChooseFile">
          📤 上传文档
        </button>
        <text class="upload-tip">支持 PDF、Word、Txt 格式</text>
      </view>
      <view v-if="uploading" class="upload-status">
        <text>上传中...</text>
      </view>
    </view>

    <!-- 语义检索卡片 -->
    <view class="search-card card">
      <view class="search-box">
        <input
          class="search-input"
          v-model="searchQuery"
          placeholder="输入关键词进行语义检索..."
          @confirm="handleSearch"
        />
        <button class="btn btn-primary btn-small" @click="handleSearch">🔍 搜索</button>
      </view>
      <view v-if="isSearchMode" class="search-tip">
        <text>搜索关键词: {{ searchQuery }}</text>
        <text class="cancel-search" @click="cancelSearch">取消搜索</text>
      </view>
    </view>

    <!-- 搜索结果 -->
    <view v-if="isSearchMode && searchResults.length > 0" class="search-results">
      <view class="section-title">🔍 搜索结果 ({{ searchResults.length }} 条)</view>
      <view
        v-for="(result, index) in searchResults"
        :key="index"
        class="search-result-item card"
      >
        <view class="result-header">
          <text class="result-score">相似度: {{ (result.score * 100).toFixed(1) }}%</text>
          <text class="result-file">{{ result.metadata.file_name }}</text>
        </view>
        <view class="result-content">
          <text class="result-text">{{ result.content }}</text>
        </view>
      </view>
    </view>

    <!-- 文档列表 -->
    <view v-if="!isSearchMode" class="documents-section">
      <view class="section-title">
        📚 我的文档 (共 {{ total }} 个)
      </view>
      
      <view v-if="loading" class="loading">
        <text>加载中...</text>
      </view>
      
      <view v-else-if="documentList.length === 0" class="empty">
        <text>暂无文档，请上传文档</text>
      </view>
      
      <view v-else>
        <view
          v-for="(doc, index) in documentList"
          :key="doc.document_id"
          class="document-item card"
        >
          <view class="doc-header">
            <view class="doc-info">
              <text class="doc-name">{{ doc.file_name }}</text>
              <text class="doc-meta">
                {{ formatFileSize(doc.file_size) }} · {{ doc.chunks_count }} 块 · {{ formatTime(doc.uploaded_at) }}
              </text>
            </view>
            <button 
              class="btn-delete" 
              @click="handleDelete(doc.document_id, doc.file_name)"
            >
              🗑️
            </button>
          </view>
        </view>
      </view>
    </view>

    <!-- 分页 -->
    <view v-if="!isSearchMode && total > 0" class="pagination">
      <button
        class="btn btn-outline btn-small"
        :disabled="page === 1"
        @click="loadPage(page - 1)"
      >上一页</button>
      <text class="page-info">第 {{ page }} / {{ totalPages }} 页 (共 {{ total }} 个)</text>
      <button
        class="btn btn-outline btn-small"
        :disabled="page >= totalPages"
        @click="loadPage(page + 1)"
      >下一页</button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import http from '@/utils/http.js'

// 数据
const documentList = ref([])
const searchResults = ref([])
const loading = ref(false)
const uploading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchQuery = ref('')
const isSearchMode = ref(false)

// 计算总页数
const totalPages = computed(() => {
  return Math.ceil(total.value / pageSize.value)
})

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  
  // 小于1分钟
  if (diff < 60000) {
    return '刚刚'
  }
  // 小于1小时
  if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  }
  // 小于1天
  if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  }
  // 小于7天
  if (diff < 604800000) {
    return `${Math.floor(diff / 86400000)}天前`
  }
  // 显示具体日期
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 选择文件
const handleChooseFile = () => {
  // uni.chooseFile 支持 H5、小程序、App 多平台
  uni.chooseFile({
    count: 1,
    extension: ['.pdf', '.doc', '.docx', '.txt'],
    success: (res) => {
      if (res.tempFiles && res.tempFiles.length > 0) {
        const file = res.tempFiles[0]
        // 检查文件大小（限制50MB）
        if (file.size > 50 * 1024 * 1024) {
          uni.showToast({
            title: '文件大小不能超过50MB',
            icon: 'none'
          })
          return
        }
        uploadDocument(file.path)
      }
    },
    fail: (err) => {
      console.error('选择文件失败:', err)
      uni.showToast({
        title: err.errMsg || '选择文件失败',
        icon: 'none'
      })
    }
  })
}

// 上传文档
const uploadDocument = async (filePath) => {
  uploading.value = true
  try {
    const response = await http.uploadDocument(filePath)
    if (response.code === 200) {
      uni.showToast({
        title: '上传成功',
        icon: 'success'
      })
      // 刷新文档列表
      loadDocuments(true)
    } else {
      uni.showToast({
        title: response.message || '上传失败',
        icon: 'none'
      })
    }
  } catch (error) {
    console.error('上传文档失败:', error)
    uni.showToast({
      title: error.message || '上传失败',
      icon: 'none'
    })
  } finally {
    uploading.value = false
  }
}

// 加载文档列表
const loadDocuments = async (resetPage = false) => {
  if (resetPage) {
    page.value = 1
  }
  
  loading.value = true
  try {
    const response = await http.getDocuments({
      page: page.value,
      page_size: pageSize.value
    })
    
    if (response.code === 200) {
      documentList.value = response.data.items || []
      total.value = response.data.total || 0
    } else {
      uni.showToast({
        title: response.message || '加载失败',
        icon: 'none'
      })
    }
  } catch (error) {
    console.error('加载文档列表失败:', error)
    uni.showToast({
      title: error.message || '加载失败',
      icon: 'none'
    })
  } finally {
    loading.value = false
  }
}

// 语义检索
const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    uni.showToast({
      title: '请输入搜索关键词',
      icon: 'none'
    })
    return
  }
  
  isSearchMode.value = true
  loading.value = true
  
  try {
    const response = await http.searchRAG({
      query: searchQuery.value.trim(),
      top_k: 5
    })
    
    if (response.code === 200) {
      searchResults.value = response.data.results || []
      if (searchResults.value.length === 0) {
        uni.showToast({
          title: '未找到相关文档',
          icon: 'none'
        })
      }
    } else {
      uni.showToast({
        title: response.message || '搜索失败',
        icon: 'none'
      })
    }
  } catch (error) {
    console.error('搜索失败:', error)
    uni.showToast({
      title: error.message || '搜索失败',
      icon: 'none'
    })
  } finally {
    loading.value = false
  }
}

// 取消搜索
const cancelSearch = () => {
  isSearchMode.value = false
  searchQuery.value = ''
  searchResults.value = []
  loadDocuments(true)
}

// 删除文档
const handleDelete = (documentId, fileName) => {
  uni.showModal({
    title: '确认删除',
    content: `确定要删除文档 "${fileName}" 吗？`,
    success: async (res) => {
      if (res.confirm) {
        await deleteDocument(documentId)
      }
    }
  })
}

// 执行删除
const deleteDocument = async (documentId) => {
  try {
    const response = await http.deleteDocument(documentId)
    if (response.code === 200) {
      uni.showToast({
        title: '删除成功',
        icon: 'success'
      })
      // 刷新文档列表
      loadDocuments(true)
    } else {
      uni.showToast({
        title: response.message || '删除失败',
        icon: 'none'
      })
    }
  } catch (error) {
    console.error('删除文档失败:', error)
    uni.showToast({
      title: error.message || '删除失败',
      icon: 'none'
    })
  }
}

// 加载指定页
const loadPage = (newPage) => {
  if (newPage < 1 || newPage > totalPages.value) {
    return
  }
  page.value = newPage
  loadDocuments()
}

// 页面加载时获取数据
onMounted(() => {
  loadDocuments()
})
</script>

<style scoped>
.rag-page {
  min-height: 100vh;
  padding: 20rpx;
  background: #f8f8f8;
  padding-bottom: 120rpx;
}

.header {
  text-align: center;
  margin-bottom: 30rpx;
  padding: 40rpx 0 20rpx;
}

.title {
  font-size: 48rpx;
  font-weight: 700;
  color: #333;
}

.card {
  background: #ffffff;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.upload-card {
  margin-bottom: 30rpx;
}

.upload-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20rpx;
}

.btn {
  padding: 16rpx 32rpx;
  border-radius: 12rpx;
  font-size: 28rpx;
  border: none;
  cursor: pointer;
}

.btn-primary {
  background: #007aff;
  color: #ffffff;
}

.btn-outline {
  background: transparent;
  border: 2rpx solid #007aff;
  color: #007aff;
}

.btn-small {
  padding: 12rpx 24rpx;
  font-size: 24rpx;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-upload {
  width: 100%;
  padding: 24rpx;
  font-size: 32rpx;
}

.upload-tip {
  font-size: 24rpx;
  color: #999;
}

.upload-status {
  margin-top: 20rpx;
  text-align: center;
  color: #007aff;
  font-size: 28rpx;
}

.search-card {
  margin-bottom: 30rpx;
}

.search-box {
  display: flex;
  gap: 20rpx;
  align-items: center;
}

.search-input {
  flex: 1;
  height: 70rpx;
  padding: 0 20rpx;
  background: #f5f5f5;
  border-radius: 12rpx;
  font-size: 28rpx;
}

.search-tip {
  margin-top: 20rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 24rpx;
  color: #666;
}

.cancel-search {
  color: #007aff;
  text-decoration: underline;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 20rpx;
  padding: 0 10rpx;
}

.search-results {
  margin-bottom: 30rpx;
}

.search-result-item {
  margin-bottom: 20rpx;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15rpx;
  padding-bottom: 15rpx;
  border-bottom: 1rpx solid #eee;
}

.result-score {
  font-size: 24rpx;
  color: #007aff;
  font-weight: 600;
}

.result-file {
  font-size: 24rpx;
  color: #666;
}

.result-content {
  margin-top: 15rpx;
}

.result-text {
  font-size: 28rpx;
  color: #333;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 5;
  overflow: hidden;
}

.documents-section {
  margin-bottom: 30rpx;
}

.loading, .empty {
  text-align: center;
  padding: 60rpx 0;
  color: #999;
  font-size: 28rpx;
}

.document-item {
  margin-bottom: 20rpx;
}

.doc-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.doc-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.doc-name {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.doc-meta {
  font-size: 24rpx;
  color: #999;
}

.btn-delete {
  padding: 10rpx 20rpx;
  background: transparent;
  border: none;
  font-size: 32rpx;
  cursor: pointer;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx 20rpx;
  background: #ffffff;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.page-info {
  font-size: 24rpx;
  color: #666;
}
</style>
