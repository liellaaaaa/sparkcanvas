<template>
  <view class="workspace-page">
    <view class="bg-decoration"></view>

    <view class="header">
      <view class="title-wrapper">
        <text class="title">知识库</text>
        <view class="badge">RAG</view>
      </view>
      <text class="subtitle">上传文档，构建你的专属知识库</text>
    </view>
    
    <!-- 上传文档卡片 -->
    <view class="upload-card card">
      <view class="card-title">
        <uni-icons type="cloud-upload" size="20" color="#3c9cff"></uni-icons>
        <text>上传文档</text>
      </view>
      <view class="upload-section">
        <button class="btn btn-primary btn-upload" @click="handleChooseFile">
          <uni-icons type="plusempty" size="18" color="#fff"></uni-icons>
          <text>上传文档</text>
        </button>
        <text class="upload-tip">支持 PDF、Word、Txt 格式</text>
      </view>
      <view v-if="uploading" class="upload-status">
        <text>上传中...</text>
      </view>
    </view>

    <!-- 语义检索卡片 -->
    <view class="search-card card">
      <view class="card-title">
        <uni-icons type="search" size="20" color="#3c9cff"></uni-icons>
        <text>语义检索</text>
      </view>
      <view class="search-container">
        <uni-icons type="search" size="18" color="#999"></uni-icons>
        <input
          class="search-input"
          v-model="searchQuery"
          placeholder="输入关键词进行语义检索..."
          placeholder-style="color:#bbb"
          @confirm="handleSearch"
        />
        <view v-if="isSearchMode" class="clear-btn" @click="cancelSearch">
          <uni-icons type="clear" size="18" color="#ff4d4f"></uni-icons>
        </view>
      </view>
    </view>

    <!-- 搜索结果 -->
    <view v-if="isSearchMode && searchResults.length > 0" class="search-results">
      <view class="section-title">
        <uni-icons type="list" size="18" color="#3c9cff"></uni-icons>
        <text>搜索结果 ({{ searchResults.length }} 条)</text>
      </view>
      <view
        v-for="(result, index) in searchResults"
        :key="index"
        class="search-result-item card"
      >
        <view class="result-header">
          <text class="result-score">距离值: {{ formatDistance(result.distance) }}</text>
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
        <uni-icons type="folder" size="18" color="#3c9cff"></uni-icons>
        <text>我的文档 (共 {{ total }} 个)</text>
      </view>
      
      <view v-if="loading" class="state-placeholder">
        <text class="loading-text">正在加载文档...</text>
      </view>
      
      <view v-else-if="documentList.length === 0" class="state-placeholder">
        <uni-icons type="info" size="40" color="#ddd"></uni-icons>
        <text class="empty-text">暂无文档，请上传文档</text>
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
            <view 
              class="footer-btn delete" 
              @click="handleDelete(doc.document_id, doc.file_name)"
            >
              <uni-icons type="trash" size="14" color="#ff4d4f"></uni-icons>
              <text>删除</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 分页 -->
    <view v-if="!isSearchMode && total > 0" class="pagination-floating card">
      <view class="p-btn" :class="{ disabled: page === 1 }" @click="loadPage(page - 1)">
        <uni-icons type="left" size="16" :color="page === 1 ? '#ccc' : '#3c9cff'"></uni-icons>
      </view>
      <text class="p-info">{{ page }} / {{ totalPages }}</text>
      <view class="p-btn" :class="{ disabled: page >= totalPages }" @click="loadPage(page + 1)">
        <uni-icons type="right" size="16" :color="page >= totalPages ? '#ccc' : '#3c9cff'"></uni-icons>
      </view>
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

// 格式化距离值，保留3位小数，数值越小表示越相似
const formatDistance = (distance) => {
  const value = Number(distance)
  if (Number.isNaN(value)) return '-'
  return value.toFixed(3)
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
.workspace-page {
  min-height: 100vh;
  padding: 40rpx 30rpx 140rpx;
  background-color: #fcfdfe;
  position: relative;
}

.bg-decoration {
  position: absolute;
  top: -150rpx; right: -100rpx; width: 500rpx; height: 500rpx;
  background: radial-gradient(circle, rgba(60, 156, 255, 0.08) 0%, transparent 70%);
}

.header { margin-bottom: 40rpx; }
.title-wrapper { display: flex; align-items: center; gap: 12rpx; }
.title { font-size: 52rpx; font-weight: 800; color: #1a1a1a; }
.badge { background: #3c9cff; color: #fff; font-size: 18rpx; padding: 4rpx 10rpx; border-radius: 6rpx; }
.subtitle { font-size: 26rpx; color: #999; margin-top: 12rpx; display: block; }

.card {
  background: #ffffff;
  border-radius: 32rpx;
  padding: 30rpx;
  box-shadow: 0 15rpx 40rpx rgba(160, 180, 210, 0.1);
  border: 1rpx solid rgba(240, 244, 250, 0.8);
  margin-bottom: 30rpx;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 12rpx;
  font-size: 30rpx;
  font-weight: 700;
  color: #333;
  margin-bottom: 30rpx;
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
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
}

.btn-primary {
  background: linear-gradient(135deg, #3c9cff 0%, #007aff 100%);
  color: #ffffff;
}

.btn:disabled {
  opacity: 0.5;
}

.btn-upload {
  width: 100%;
  padding: 24rpx;
  font-size: 30rpx;
  font-weight: 600;
}

.upload-tip {
  font-size: 24rpx;
  color: #999;
}

.upload-status {
  margin-top: 20rpx;
  text-align: center;
  color: #3c9cff;
  font-size: 26rpx;
}

.search-container {
  display: flex;
  align-items: center;
  background: #f8f9fb;
  border-radius: 20rpx;
  padding: 16rpx 24rpx;
  gap: 16rpx;
}

.search-input {
  flex: 1;
  font-size: 26rpx;
  color: #333;
}

.clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12rpx;
  font-size: 30rpx;
  font-weight: 700;
  color: #333;
  margin-bottom: 24rpx;
  padding: 0 10rpx;
}

.search-results {
  margin-bottom: 30rpx;
}

.search-result-item {
  margin-bottom: 20rpx;
  transition: transform 0.2s;
}

.search-result-item:active {
  transform: scale(0.98);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid #f0f3f8;
}

.result-score {
  font-size: 24rpx;
  color: #3c9cff;
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
  font-size: 26rpx;
  color: #444;
  line-height: 1.6;
  word-break: break-all;
}

.documents-section {
  margin-bottom: 30rpx;
}

.state-placeholder {
  padding: 100rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20rpx;
}

.empty-text, .loading-text {
  color: #ccc;
  font-size: 26rpx;
}

.document-item {
  margin-bottom: 20rpx;
  transition: transform 0.2s;
}

.document-item:active {
  transform: scale(0.98);
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
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

.doc-meta {
  font-size: 24rpx;
  color: #999;
}

.footer-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 10rpx 20rpx;
  border-radius: 12rpx;
  font-size: 24rpx;
  font-weight: 600;
  transition: all 0.2s;
}

.footer-btn.delete {
  background: #fff1f0;
  color: #ff4d4f;
}

.pagination-floating {
  position: fixed;
  bottom: 40rpx;
  left: 50%;
  transform: translateX(-50%);
  width: 400rpx;
  height: 90rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40rpx;
  margin-bottom: 0;
  border-radius: 100rpx;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  z-index: 99;
  box-shadow: 0 10rpx 40rpx rgba(0,0,0,0.1);
}

.p-info {
  font-size: 24rpx;
  font-weight: 700;
  color: #444;
}

.p-btn {
  padding: 10rpx;
}

.p-btn.disabled {
  opacity: 0.3;
}
</style>
