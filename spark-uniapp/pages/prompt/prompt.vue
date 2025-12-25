<template>
  <view class="prompt-page">
    <view class="header">
      <text class="title">🎨 Prompt管理</text>
      <text class="subtitle">管理你的Prompt模板，提升内容生成效率</text>
    </view>

    <!-- 筛选栏 -->
    <view class="filter-card card">
      <view class="filter-row">
        <view class="filter-label">平台筛选</view>
        <view class="tags-row">
          <text
            v-for="p in platformOptions"
            :key="p.value"
            :class="['tag', selectedPlatform === p.value ? 'tag-primary' : 'tag-default']"
            @click="handlePlatformChange(p.value)"
          >{{ p.label }}</text>
        </view>
      </view>
      <view class="filter-row" v-if="selectedPlatform">
        <view class="filter-label">分类筛选</view>
        <input
          class="filter-input"
          v-model="selectedCategory"
          placeholder="输入分类名称"
          @input="handleCategoryChange"
        />
      </view>
    </view>

    <!-- 操作栏 -->
    <view class="action-bar">
      <button class="btn btn-primary" @click="showCreateModal = true">
        ➕ 创建Prompt
      </button>
    </view>

    <!-- Prompt列表 -->
    <view class="list-card card">
      <view v-if="loading && promptList.length === 0" class="loading-state">
        <text>加载中...</text>
      </view>
      
      <view v-else-if="promptList.length === 0" class="empty-state">
        <text>暂无Prompt模板，点击上方按钮创建</text>
      </view>

      <view v-else>
        <view
          v-for="item in promptList"
          :key="item.id"
          class="prompt-item"
        >
          <view class="item-header">
            <view class="item-title-row">
              <text class="item-title">{{ item.name }}</text>
              <text class="item-platform">{{ getPlatformLabel(item.platform) }}</text>
            </view>
            <view class="item-meta">
              <text class="item-category" v-if="item.category">{{ item.category }}</text>
              <text class="item-time">{{ formatTime(item.created_at) }}</text>
            </view>
          </view>
          
          <view class="item-description" v-if="item.description">
            <text>{{ item.description }}</text>
          </view>
          
          <view class="item-content-preview">
            <text>{{ truncateContent(item.content) }}</text>
          </view>
          
          <view class="item-actions">
            <button class="btn btn-small btn-outline" @click="handleView(item)">
              查看
            </button>
            <button class="btn btn-small btn-outline" @click="handleEdit(item)">
              编辑
            </button>
            <button class="btn btn-small btn-secondary" @click="handleDelete(item)">
              删除
            </button>
          </view>
        </view>

        <!-- 加载更多 -->
        <view v-if="promptList.length < total" class="load-more">
          <button 
            class="btn btn-outline" 
            :loading="loadingMore"
            @click="handleLoadMore"
          >
            {{ loadingMore ? '加载中...' : '加载更多' }}
          </button>
        </view>
        
        <view v-else-if="promptList.length > 0" class="no-more">
          <text>没有更多数据了</text>
        </view>
      </view>
    </view>

    <!-- 创建/编辑Modal -->
    <view v-if="showCreateModal || showEditModal" class="modal-overlay" @click="closeModal">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">{{ showCreateModal ? '创建Prompt' : '编辑Prompt' }}</text>
          <text class="modal-close" @click="closeModal">✕</text>
        </view>
        
        <view class="modal-body">
          <view class="form-group">
            <text class="form-label">模板名称 *</text>
            <input
              class="form-input"
              v-model="formData.name"
              placeholder="请输入模板名称（1-255字符）"
              maxlength="255"
            />
          </view>

          <view class="form-group">
            <text class="form-label">平台类型</text>
            <view class="tags-row">
              <text
                v-for="p in platformOptions"
                :key="p.value"
                :class="['tag', formData.platform === p.value ? 'tag-primary' : 'tag-default']"
                @click="formData.platform = p.value"
              >{{ p.label }}</text>
            </view>
          </view>

          <view class="form-group">
            <text class="form-label">分类/垂类</text>
            <input
              class="form-input"
              v-model="formData.category"
              placeholder="例如：家居收纳、职场成长"
              maxlength="100"
            />
          </view>

          <view class="form-group">
            <text class="form-label">模板描述</text>
            <textarea
              class="form-textarea"
              v-model="formData.description"
              placeholder="简要描述模板的用途和使用场景"
              maxlength="500"
            />
          </view>

          <view class="form-group">
            <text class="form-label">Prompt内容 *</text>
            <textarea
              class="form-textarea form-textarea-large"
              v-model="formData.content"
              placeholder="输入Prompt模板内容，可使用{{变量名}}占位符"
              :auto-height="true"
            />
          </view>
        </view>
        
        <view class="modal-footer">
          <button class="btn btn-outline" @click="closeModal">取消</button>
          <button 
            class="btn btn-primary" 
            :loading="submitting"
            :disabled="submitting"
            @click="handleSubmit"
          >
            {{ submitting ? (showCreateModal ? '创建中...' : '保存中...') : '确定' }}
          </button>
        </view>
      </view>
    </view>

    <!-- 查看详情Modal -->
    <view v-if="showViewModal && viewingPrompt" class="modal-overlay" @click="showViewModal = false">
      <view class="modal-content modal-content-large" @click.stop>
        <view class="modal-header">
          <text class="modal-title">{{ viewingPrompt.name }}</text>
          <text class="modal-close" @click="showViewModal = false">✕</text>
        </view>
        
        <view class="modal-body">
          <view class="detail-group">
            <text class="detail-label">平台类型</text>
            <text class="detail-value">{{ getPlatformLabel(viewingPrompt.platform) }}</text>
          </view>
          
          <view class="detail-group" v-if="viewingPrompt.category">
            <text class="detail-label">分类</text>
            <text class="detail-value">{{ viewingPrompt.category }}</text>
          </view>
          
          <view class="detail-group" v-if="viewingPrompt.description">
            <text class="detail-label">描述</text>
            <text class="detail-value">{{ viewingPrompt.description }}</text>
          </view>
          
          <view class="detail-group">
            <text class="detail-label">Prompt内容</text>
            <view class="detail-content">
              <text>{{ viewingPrompt.content }}</text>
            </view>
          </view>
          
          <view class="detail-group">
            <text class="detail-label">创建时间</text>
            <text class="detail-value">{{ formatTime(viewingPrompt.created_at) }}</text>
          </view>
          
          <view class="detail-group">
            <text class="detail-label">更新时间</text>
            <text class="detail-value">{{ formatTime(viewingPrompt.updated_at) }}</text>
          </view>
        </view>
        
        <view class="modal-footer">
          <button class="btn btn-primary" @click="handleEditFromView">编辑</button>
          <button class="btn btn-outline" @click="showViewModal = false">关闭</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { onLoad, onPullDownRefresh } from '@dcloudio/uni-app'
import http from '@/utils/http.js'

// ========== 响应式数据 ==========
const loading = ref(false)
const loadingMore = ref(false)
const submitting = ref(false)
const promptList = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

// 筛选条件
const selectedPlatform = ref('')
const selectedCategory = ref('')

// Modal状态
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showViewModal = ref(false)
const viewingPrompt = ref(null)

// 表单数据
const formData = reactive({
  id: null,
  name: '',
  content: '',
  platform: '通用',
  category: '',
  description: ''
})

// 平台选项
const platformOptions = [
  { label: '全部', value: '' },
  { label: '小红书', value: 'xiaohongshu' },
  { label: '抖音', value: 'douyin' },
  { label: '通用', value: '通用' }
]

// ========== 工具函数 ==========
const formatTime = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const date = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${date} ${hours}:${minutes}`
}

const getPlatformLabel = (platform) => {
  const option = platformOptions.find(p => p.value === platform)
  return option ? option.label : platform
}

const truncateContent = (content) => {
  if (!content) return ''
  return content.length > 100 ? content.substring(0, 100) + '...' : content
}

// ========== 数据加载 ==========
const loadPromptList = async (resetPage = false) => {
  try {
    if (resetPage) {
      page.value = 1
      promptList.value = []
    }
    
    loading.value = true
    
    const params = {
      page: page.value,
      page_size: pageSize.value
    }
    
    if (selectedPlatform.value) {
      params.platform = selectedPlatform.value
    }
    
    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }
    
    const res = await http.getPrompts(params)
    const payload = res?.data || res

    if (resetPage) {
      promptList.value = payload.items || []
    } else {
      promptList.value = [...promptList.value, ...(payload.items || [])]
    }

    total.value = payload.total || 0
  } catch (e) {
    console.error('加载Prompt列表失败:', e)
    uni.showToast({
      title: e.message || '加载失败，请稍后重试',
      icon: 'none',
      duration: 2000
    })
  } finally {
    loading.value = false
  }
}

const handleLoadMore = async () => {
  if (promptList.value.length >= total.value) {
    uni.showToast({ title: '没有更多数据了', icon: 'none' })
    return
  }
  
  try {
    loadingMore.value = true
    page.value++
    await loadPromptList(false)
  } catch (e) {
    page.value-- // 恢复页码
  } finally {
    loadingMore.value = false
  }
}

// ========== 筛选处理 ==========
const handlePlatformChange = (platform) => {
  selectedPlatform.value = platform
  selectedCategory.value = '' // 清空分类筛选
  loadPromptList(true)
}

const handleCategoryChange = () => {
  // 防抖处理，延迟搜索
  clearTimeout(handleCategoryChange.timer)
  handleCategoryChange.timer = setTimeout(() => {
    loadPromptList(true)
  }, 500)
}

// ========== 表单验证 ==========
const validateForm = () => {
  if (!formData.name.trim()) {
    uni.showToast({ title: '请输入模板名称', icon: 'none' })
    return false
  }
  
  if (formData.name.length > 255) {
    uni.showToast({ title: '模板名称不能超过255个字符', icon: 'none' })
    return false
  }
  
  if (!formData.content.trim()) {
    uni.showToast({ title: '请输入Prompt内容', icon: 'none' })
    return false
  }
  
  const validPlatforms = ['xiaohongshu', 'douyin', '通用']
  if (!validPlatforms.includes(formData.platform)) {
    uni.showToast({ title: '请选择有效的平台类型', icon: 'none' })
    return false
  }
  
  if (formData.category && formData.category.length > 100) {
    uni.showToast({ title: '分类名称不能超过100个字符', icon: 'none' })
    return false
  }
  
  if (formData.description && formData.description.length > 500) {
    uni.showToast({ title: '描述不能超过500个字符', icon: 'none' })
    return false
  }
  
  return true
}

// ========== 表单处理 ==========
const resetForm = () => {
  formData.id = null
  formData.name = ''
  formData.content = ''
  formData.platform = '通用'
  formData.category = ''
  formData.description = ''
}

const fillForm = (prompt) => {
  formData.id = prompt.id
  formData.name = prompt.name
  formData.content = prompt.content
  formData.platform = prompt.platform
  formData.category = prompt.category || ''
  formData.description = prompt.description || ''
}

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }
  
  try {
    submitting.value = true
    
    const data = {
      name: formData.name.trim(),
      content: formData.content.trim(),
      platform: formData.platform,
      category: formData.category.trim() || undefined,
      description: formData.description.trim() || undefined
    }
    
    if (showEditModal.value && formData.id) {
      // 更新
      data.id = formData.id
      await http.updatePrompt(data)
      uni.showToast({ title: '更新成功', icon: 'success' })
    } else {
      // 创建
      await http.createPrompt(data)
      uni.showToast({ title: '创建成功', icon: 'success' })
    }
    
    closeModal()
    await loadPromptList(true)
  } catch (e) {
    console.error('提交失败:', e)
    uni.showToast({
      title: e.message || '操作失败，请稍后重试',
      icon: 'none',
      duration: 2000
    })
  } finally {
    submitting.value = false
  }
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  showViewModal.value = false
  resetForm()
}

// ========== 操作处理 ==========
const handleView = (prompt) => {
  viewingPrompt.value = prompt
  showViewModal.value = true
}

const handleEdit = (prompt) => {
  fillForm(prompt)
  showEditModal.value = true
}

const handleEditFromView = () => {
  if (viewingPrompt.value) {
    fillForm(viewingPrompt.value)
    showViewModal.value = false
    showEditModal.value = true
  }
}

const handleDelete = (prompt) => {
  uni.showModal({
    title: '确认删除',
    content: `确定要删除模板"${prompt.name}"吗？此操作不可恢复。`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await http.deletePrompt({ id: prompt.id })
          uni.showToast({ title: '删除成功', icon: 'success' })
          await loadPromptList(true)
        } catch (e) {
          console.error('删除失败:', e)
          uni.showToast({
            title: e.message || '删除失败，请稍后重试',
            icon: 'none',
            duration: 2000
          })
        }
      }
    }
  })
}

// ========== 生命周期 ==========
onLoad(() => {
  loadPromptList(true)
})

onPullDownRefresh(async () => {
  await loadPromptList(true)
  uni.stopPullDownRefresh()
})
</script>

<style scoped>
.prompt-page {
  min-height: 100vh;
  padding: 20rpx;
  background: #f8f8f8;
  padding-bottom: 40rpx;
}

.header {
  text-align: center;
  margin-bottom: 32rpx;
  padding: 32rpx 0;
}

.title {
  font-size: 44rpx;
  font-weight: 700;
  color: #333;
  display: block;
  margin-bottom: 8rpx;
}

.subtitle {
  font-size: 26rpx;
  color: #888;
}

.card {
  background: #ffffff;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
  padding: 32rpx 28rpx;
  margin-bottom: 24rpx;
}

/* 筛选栏 */
.filter-card {
  padding: 24rpx;
}

.filter-row {
  margin-bottom: 20rpx;
}

.filter-row:last-child {
  margin-bottom: 0;
}

.filter-label {
  font-size: 26rpx;
  color: #666;
  margin-bottom: 12rpx;
  display: block;
}

.filter-input {
  width: 100%;
  height: 64rpx;
  padding: 0 20rpx;
  border-radius: 12rpx;
  background: #f8f8f8;
  border: 2rpx solid #e0e0e0;
  font-size: 26rpx;
  box-sizing: border-box;
}

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.tag {
  padding: 8rpx 20rpx;
  border-radius: 999rpx;
  font-size: 24rpx;
  transition: all 0.2s;
}

.tag-primary {
  background: linear-gradient(135deg, #3c9cff 0%, #4facfe 100%);
  color: #fff;
}

.tag-default {
  background-color: #f5f5f5;
  color: #666;
}

/* 操作栏 */
.action-bar {
  margin-bottom: 24rpx;
  display: flex;
  justify-content: flex-end;
}

/* 列表卡片 */
.list-card {
  min-height: 400rpx;
}

.loading-state,
.empty-state,
.no-more {
  text-align: center;
  padding: 80rpx 20rpx;
  color: #999;
  font-size: 26rpx;
}

/* Prompt项 */
.prompt-item {
  padding: 24rpx;
  border-bottom: 2rpx solid #f0f0f0;
  margin-bottom: 20rpx;
}

.prompt-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.item-header {
  margin-bottom: 12rpx;
}

.item-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8rpx;
}

.item-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  flex: 1;
}

.item-platform {
  font-size: 22rpx;
  color: #fff;
  background: linear-gradient(135deg, #3c9cff 0%, #4facfe 100%);
  padding: 4rpx 12rpx;
  border-radius: 999rpx;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 16rpx;
  font-size: 24rpx;
  color: #999;
}

.item-category {
  color: #3c9cff;
}

.item-description {
  margin-bottom: 12rpx;
  font-size: 26rpx;
  color: #666;
}

.item-content-preview {
  margin-bottom: 16rpx;
  padding: 16rpx;
  background: #f8f8f8;
  border-radius: 12rpx;
  font-size: 24rpx;
  color: #555;
  line-height: 1.6;
}

.item-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12rpx;
}

.load-more {
  text-align: center;
  padding: 32rpx 0;
}

/* 按钮 */
.btn {
  padding: 0 32rpx;
  height: 72rpx;
  line-height: 72rpx;
  border-radius: 999rpx;
  font-size: 28rpx;
  border: none;
}

.btn-small {
  height: 56rpx;
  line-height: 56rpx;
  padding: 0 24rpx;
  font-size: 24rpx;
}

.btn-primary {
  background: linear-gradient(135deg, #3c9cff 0%, #4facfe 100%);
  color: #fff;
}

.btn-secondary {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: #fff;
}

.btn-outline {
  background: transparent;
  border: 2rpx solid #3c9cff;
  color: #3c9cff;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 40rpx;
}

.modal-content {
  width: 100%;
  max-width: 600rpx;
  max-height: 80vh;
  background: #fff;
  border-radius: 24rpx;
  display: flex;
  flex-direction: column;
}

.modal-content-large {
  max-width: 700rpx;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx;
  border-bottom: 2rpx solid #f0f0f0;
}

.modal-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.modal-close {
  font-size: 40rpx;
  color: #999;
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 32rpx;
}

.modal-footer {
  display: flex;
  gap: 16rpx;
  padding: 32rpx;
  border-top: 2rpx solid #f0f0f0;
}

.modal-footer .btn {
  flex: 1;
}

/* 表单 */
.form-group {
  margin-bottom: 32rpx;
}

.form-label {
  display: block;
  font-size: 28rpx;
  color: #333;
  margin-bottom: 12rpx;
  font-weight: 500;
}

.form-input {
  width: 100%;
  height: 88rpx;
  padding: 0 28rpx;
  border-radius: 16rpx;
  background: #f8f8f8;
  border: 2rpx solid #e0e0e0;
  font-size: 28rpx;
  color: #333;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: #3c9cff;
  background: #f0f7ff;
}

.form-textarea {
  width: 100%;
  min-height: 120rpx;
  padding: 20rpx;
  border-radius: 16rpx;
  border: 2rpx solid #e5e5e5;
  background: #fafafa;
  font-size: 28rpx;
  box-sizing: border-box;
}

.form-textarea-large {
  min-height: 300rpx;
}

/* 详情 */
.detail-group {
  margin-bottom: 24rpx;
}

.detail-label {
  display: block;
  font-size: 26rpx;
  color: #666;
  margin-bottom: 8rpx;
}

.detail-value {
  font-size: 28rpx;
  color: #333;
  line-height: 1.6;
}

.detail-content {
  padding: 16rpx;
  background: #f8f8f8;
  border-radius: 12rpx;
  font-size: 26rpx;
  color: #555;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
