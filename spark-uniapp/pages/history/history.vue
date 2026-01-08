<template>
  <view class="workspace-page">
    <view class="bg-decoration"></view>

    <view class="header">
      <view class="title-wrapper">
        <text class="title">历史记录</text>
        <view class="badge">HISTORY</view>
      </view>
      <text class="subtitle">回顾你的创作历程与灵感足迹</text>
    </view>

    <view class="search-card card">
      <view class="search-container">
        <uni-icons type="search" size="18" color="#999"></uni-icons>
        <input
          class="search-input"
          v-model="searchKeyword"
          placeholder="搜索创作内容或标题..."
          placeholder-style="color:#bbb"
          @confirm="handleSearch"
        />
        <view v-if="isSearchMode" class="clear-btn" @click="cancelSearch">
          <uni-icons type="clear" size="18" color="#ff4d4f"></uni-icons>
        </view>
      </view>
    </view>

    <view class="history-list">
      <view v-if="loading" class="state-placeholder">
        <text class="loading-text">正在加载创作记忆...</text>
      </view>
      
      <view v-else-if="historyList.length === 0" class="state-placeholder">
        <uni-icons type="info" size="40" color="#ddd"></uni-icons>
        <text class="empty-text">暂无历史，去工作台开始创作吧</text>
      </view>
      
      <view v-else>
        <view
          v-for="(item, index) in historyList"
          :key="`${item.session_id}-${item.timestamp}`"
          class="history-item card animate-in"
          :style="{ animationDelay: index * 0.05 + 's' }"
        >
          <view class="item-header">
            <view class="platform-indicator">
              <view class="dot"></view>
              <text class="session-tag">会话: {{ item.session_id.slice(0, 8) }}</text>
            </view>
            <text class="time-text">{{ formatTime(item.timestamp) }}</text>
          </view>
          
          <view class="item-body">
            <view class="content-box user-message">
              <view class="box-label">
                <uni-icons type="person" size="12" color="#3c9cff"></uni-icons>
                <text>需求</text>
              </view>
              <text class="message-text">{{ item.message }}</text>
            </view>
            
            <view class="content-box assistant-response">
              <view class="box-label">
                <uni-icons type="paperplane" size="12" color="#52c41a"></uni-icons>
                <text>生成结果</text>
              </view>
              <text class="response-text" :class="{ 'expanded': isExpanded(item) }">
                {{ isExpanded(item) ? item.response : getPreviewText(item.response) }}
              </text>
            </view>
          </view>

          <view class="item-footer">
            <view class="footer-left">
              <text v-if="needsExpand(item.response)" class="footer-btn" @click="toggleExpand(item)">
                {{ isExpanded(item) ? '收起' : '查看全文' }}
              </text>
            </view>
            <view class="footer-right">
              <view class="footer-btn copy" @click="handleCopy(item)">
                <uni-icons type="copy" size="14" color="#3c9cff"></uni-icons>
                <text>复制</text>
              </view>
              <view class="footer-btn delete" @click="handleDelete(item)">
                <uni-icons type="trash" size="14" color="#ff4d4f"></uni-icons>
                <text>删除</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view v-if="total > 0" class="pagination-floating card">
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
/* 逻辑部分保持原样，仅做少量适配 */
import { ref, onMounted, computed } from 'vue'
import http from '@/utils/http.js'

const historyList = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')
const isSearchMode = ref(false)
const expandedItems = ref({})
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return `${date.getMonth() + 1}月${date.getDate()}日 ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const loadHistory = async (resetPage = false) => {
  if (resetPage) page.value = 1
  loading.value = true
  try {
    let response = isSearchMode.value ? 
      await http.searchHistory({ keyword: searchKeyword.value, page: page.value, page_size: pageSize.value }) :
      await http.getConversations({ page: page.value, page_size: pageSize.value })
    if (response.code === 200) {
      historyList.value = response.data.items || []
      total.value = response.data.total || 0
    }
  } finally {
    loading.value = false
  }
}

const handleSearch = () => { if (searchKeyword.value.trim()) { isSearchMode.value = true; loadHistory(true); } }
const cancelSearch = () => { isSearchMode.value = false; searchKeyword.value = ''; loadHistory(true); }
const loadPage = (p) => { if (p >= 1 && p <= totalPages.value) { page.value = p; loadHistory(); uni.pageScrollTo({ scrollTop: 0 }); } }
const getPreviewText = (t) => t ? (t.split('\n').slice(0, 3).join('\n') + (t.split('\n').length > 3 ? '...' : '')) : ''
const needsExpand = (t) => t && t.split('\n').length > 3
const getItemKey = (item) => `${item.session_id}-${item.timestamp}`
const isExpanded = (item) => expandedItems.value[getItemKey(item)] || false
const toggleExpand = (item) => { const k = getItemKey(item); expandedItems.value[k] = !expandedItems.value[k]; }

const handleCopy = (item) => {
  uni.setClipboardData({ data: item.response, success: () => uni.showToast({ title: '已复制结果' }) })
}

const handleDelete = (item) => {
  uni.showModal({
    title: '确认删除',
    content: '删除后无法找回，确认吗？',
    confirmColor: '#ff4d4f',
    success: async (res) => {
      if (res.confirm) {
        await http.deleteHistory({ session_id: item.session_id, timestamp: item.timestamp })
        loadHistory()
      }
    }
  })
}

onMounted(() => loadHistory())
</script>

<style scoped>
/* 引用工作台核心设计规范 */
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

/* 搜索框美化 */
.search-container {
  display: flex;
  align-items: center;
  background: #f8f9fb;
  border-radius: 20rpx;
  padding: 16rpx 24rpx;
  gap: 16rpx;
}
.search-input { flex: 1; font-size: 26rpx; color: #333; }

/* 列表项美化 */
.history-item { transition: transform 0.2s; }
.history-item:active { transform: scale(0.98); }

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid #f0f3f8;
}

.platform-indicator { display: flex; align-items: center; gap: 10rpx; }
.dot { width: 12rpx; height: 12rpx; background: #3c9cff; border-radius: 50%; }
.session-tag { font-size: 24rpx; font-weight: 600; color: #666; }
.time-text { font-size: 22rpx; color: #bbb; }

.item-body { display: flex; flex-direction: column; gap: 20rpx; }

.content-box {
  padding: 20rpx;
  border-radius: 20rpx;
  position: relative;
}
.user-message { background: #f0f7ff; }
.assistant-response { background: #f8f9fb; }

.box-label {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-bottom: 12rpx;
  opacity: 0.7;
}
.box-label text { font-size: 22rpx; font-weight: 700; color: #444; }

.message-text, .response-text {
  font-size: 26rpx;
  line-height: 1.6;
  color: #444;
  word-break: break-all;
}

/* 底部操作 */
.item-footer {
  margin-top: 24rpx;
  padding-top: 20rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.footer-btn.copy { background: #eef6ff; color: #3c9cff; }
.footer-btn.delete { background: #fff1f0; color: #ff4d4f; }
.footer-left .footer-btn { color: #888; background: transparent; padding: 0; }

/* 悬浮分页器 */
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
.p-info { font-size: 24rpx; font-weight: 700; color: #444; }
.p-btn { padding: 10rpx; }
.p-btn.disabled { opacity: 0.3; }

/* 状态占位 */
.state-placeholder {
  padding: 100rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20rpx;
}
.empty-text, .loading-text { color: #ccc; font-size: 26rpx; }

/* 动画 */
.animate-in {
  animation: slideUp 0.4s ease-out both;
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(30rpx); }
  to { opacity: 1; transform: translateY(0); }
}
</style>