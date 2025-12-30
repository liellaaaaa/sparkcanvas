<template>
  <view class="history-page">
    <view class="header">
      <text class="title">📚 历史记录</text>
    </view>
    
    <!-- 搜索栏 -->
    <view class="search-card card">
      <view class="search-box">
        <input
          class="search-input"
          v-model="searchKeyword"
          placeholder="搜索历史记录..."
          @confirm="handleSearch"
        />
        <button class="btn btn-primary btn-small" @click="handleSearch">🔍 搜索</button>
      </view>
      <view v-if="isSearchMode" class="search-tip">
        <text>搜索关键词: {{ searchKeyword }}</text>
        <text class="cancel-search" @click="cancelSearch">取消搜索</text>
      </view>
    </view>

    <!-- 历史记录列表 -->
    <view class="history-list">
      <view v-if="loading" class="loading">
        <text>加载中...</text>
      </view>
      
      <view v-else-if="historyList.length === 0" class="empty">
        <text>暂无历史记录</text>
      </view>
      
      <view v-else>
        <view
          v-for="(item, index) in historyList"
          :key="`${item.session_id}-${item.timestamp}`"
          class="history-item card"
        >
          <view class="item-header">
            <text class="session-tag">会话: {{ item.session_id.slice(0, 8) }}...</text>
            <view class="header-right">
              <text class="time-text">{{ formatTime(item.timestamp) }}</text>
              <button class="btn-delete" @click="handleDelete(item)">🗑️ 删除</button>
            </view>
          </view>
          
          <view class="item-content">
            <view class="message-section">
              <text class="label">用户消息：</text>
              <text class="message-text">{{ item.message }}</text>
            </view>
            
            <view class="response-section">
              <text class="label">助手回复：</text>
              <view class="response-container">
                <text class="response-text" :class="{ 'expanded': isExpanded(item) }">
                  {{ isExpanded(item) ? item.response : getPreviewText(item.response) }}
                </text>
                <view class="action-buttons">
                  <text 
                    class="action-btn copy-btn" 
                    @click="handleCopy(item)"
                  >
                    复制
                  </text>
                  <text 
                    v-if="needsExpand(item.response)" 
                    class="action-btn expand-btn" 
                    @click="toggleExpand(item)"
                  >
                    {{ isExpanded(item) ? '收起' : '展开' }}
                  </text>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 分页 -->
    <view v-if="total > 0" class="pagination">
      <button
        class="btn btn-outline btn-small"
        :disabled="page === 1"
        @click="loadPage(page - 1)"
      >上一页</button>
      <text class="page-info">第 {{ page }} / {{ totalPages }} 页 (共 {{ total }} 条)</text>
      <button
        class="btn btn-outline btn-small"
        :disabled="page >= totalPages"
        @click="loadPage(page + 1)"
      >下一页</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '@/utils/http.js'

// 数据
const historyList = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchKeyword = ref('')
const isSearchMode = ref(false)
const expandedItems = ref({}) // 记录每个item是否展开

// 计算总页数
const totalPages = ref(0)

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

// 加载历史记录
const loadHistory = async (resetPage = false) => {
  if (resetPage) {
    page.value = 1
  }
  
  loading.value = true
  try {
    let response
    if (isSearchMode.value && searchKeyword.value.trim()) {
      // 搜索模式
      response = await http.searchHistory({
        keyword: searchKeyword.value.trim(),
        page: page.value,
        page_size: pageSize.value
      })
    } else {
      // 查询模式
      response = await http.getConversations({
        page: page.value,
        page_size: pageSize.value
      })
    }
    
    if (response.code === 200) {
      historyList.value = response.data.items || []
      total.value = response.data.total || 0
      totalPages.value = Math.ceil(total.value / pageSize.value)
      // 重置展开状态
      expandedItems.value = {}
    } else {
      uni.showToast({
        title: response.message || '加载失败',
        icon: 'none'
      })
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
    uni.showToast({
      title: error.message || '加载失败',
      icon: 'none'
    })
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  if (!searchKeyword.value.trim()) {
    uni.showToast({
      title: '请输入搜索关键词',
      icon: 'none'
    })
    return
  }
  isSearchMode.value = true
  loadHistory(true)
}

// 取消搜索
const cancelSearch = () => {
  isSearchMode.value = false
  searchKeyword.value = ''
  loadHistory(true)
}

// 加载指定页
const loadPage = (newPage) => {
  if (newPage < 1 || newPage > totalPages.value) {
    return
  }
  page.value = newPage
  loadHistory()
}

// 获取预览文本（前5行）
const getPreviewText = (text) => {
  if (!text) return ''
  const lines = text.split('\n')
  if (lines.length <= 5) {
    return text
  }
  return lines.slice(0, 5).join('\n')
}

// 判断是否需要展开按钮
const needsExpand = (text) => {
  if (!text) return false
  const lines = text.split('\n')
  return lines.length > 5
}

// 获取唯一标识
const getItemKey = (item) => {
  return `${item.session_id}-${item.timestamp}`
}

// 判断是否展开
const isExpanded = (item) => {
  return expandedItems.value[getItemKey(item)] || false
}

// 切换展开/收起
const toggleExpand = (item) => {
  const key = getItemKey(item)
  expandedItems.value[key] = !expandedItems.value[key]
}

// 一键复制
const handleCopy = (item) => {
  const content = item.response || ''
  if (!content) {
    uni.showToast({
      title: '内容为空，无法复制',
      icon: 'none'
    })
    return
  }
  
  uni.setClipboardData({
    data: content,
    success: () => {
      uni.showToast({
        title: '复制成功',
        icon: 'success',
        duration: 1500
      })
    },
    fail: (err) => {
      console.error('复制失败:', err)
      uni.showToast({
        title: '复制失败，请稍后重试',
        icon: 'none'
      })
    }
  })
}

// 删除历史记录
const handleDelete = (item) => {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这条历史记录吗？此操作不可恢复。',
    success: async (res) => {
      if (res.confirm) {
        try {
          await http.deleteHistory({
            session_id: item.session_id,
            timestamp: item.timestamp
          })
          uni.showToast({
            title: '删除成功',
            icon: 'success'
          })
          // 重新加载列表
          await loadHistory()
        } catch (error) {
          console.error('删除失败:', error)
          uni.showToast({
            title: error.message || '删除失败，请稍后重试',
            icon: 'none',
            duration: 2000
          })
        }
      }
    }
  })
}

// 页面加载时获取数据
onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.history-page {
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

.history-list {
  margin-bottom: 30rpx;
}

.history-item {
  margin-bottom: 20rpx;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
  padding-bottom: 15rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.session-tag {
  font-size: 24rpx;
  color: #007aff;
  background: #e6f3ff;
  padding: 6rpx 12rpx;
  border-radius: 6rpx;
}

.time-text {
  font-size: 24rpx;
  color: #999;
}

.item-content {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.message-section,
.response-section {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.label {
  font-size: 26rpx;
  font-weight: 600;
  color: #333;
}

.message-text,
.response-text {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
}

.response-container {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.response-text {
  background: #f8f8f8;
  padding: 20rpx;
  border-radius: 12rpx;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 20rpx;
  padding: 10rpx 0;
}

.action-btn {
  color: #007aff;
  font-size: 26rpx;
  cursor: pointer;
}

.expand-btn {
  color: #007aff;
  font-size: 26rpx;
  cursor: pointer;
}

.copy-btn {
  color: #007aff;
  font-size: 26rpx;
  cursor: pointer;
}

.btn-delete {
  padding: 8rpx 16rpx;
  background: #ff3b30;
  color: #ffffff;
  border-radius: 8rpx;
  font-size: 24rpx;
  border: none;
  cursor: pointer;
}

.loading,
.empty {
  text-align: center;
  padding: 100rpx 0;
  color: #999;
  font-size: 28rpx;
}

.pagination {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #ffffff;
  padding: 20rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.08);
  z-index: 100;
}

.page-info {
  font-size: 24rpx;
  color: #666;
}
</style>
