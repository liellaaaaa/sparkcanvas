<template>
  <view class="workspace-page">
    <view class="header">
      <text class="title">✨ SparkCanvas 工作台</text>
      <text class="subtitle">一键生成爆款内容</text>
    </view>

    <!-- 会话信息卡片 -->
    <view v-if="sessionId" class="session-card card">
      <view class="session-header">
        <text class="session-label">当前会话</text>
        <text class="session-id">{{ sessionId.slice(0, 8) }}...</text>
      </view>
      <view class="session-meta">
        <text>消息数: {{ sessionInfo.message_count || 0 }}</text>
        <text v-if="sessionInfo.last_message_time">最后消息: {{ formatTime(sessionInfo.last_message_time) }}</text>
      </view>
      <view class="session-actions">
        <button class="btn btn-small btn-outline" @click="refreshSessionInfo">刷新状态</button>
        <button class="btn btn-small btn-outline" @click="createNewSession">新建会话</button>
      </view>
    </view>

    <!-- 内容生成区域 -->
    <view class="content-card card">
      <view class="card-title">📝 内容创作</view>

      <!-- 平台选择 -->
      <view class="field-row">
        <view class="field-label">目标平台</view>
        <view class="field-value tags-row">
          <text
            v-for="p in platforms"
            :key="p.value"
            :class="['tag', platform === p.value ? 'tag-primary' : 'tag-default']"
            @click="platform = p.value"
          >{{ p.label }}</text>
        </view>
      </view>

      <!-- 素材源选择 -->
      <view class="field-row">
        <view class="field-label">素材来源</view>
        <view class="field-value tags-row">
          <text
            v-for="s in materialSources"
            :key="s.value"
            :class="['tag', materialSource === s.value ? 'tag-primary' : 'tag-default']"
            @click="materialSource = s.value"
          >{{ s.label }}</text>
        </view>
      </view>

      <!-- 文件上传（素材源为 upload 时显示） -->
      <view v-if="materialSource === 'upload'" class="field-row column">
        <view class="field-label">上传素材文件</view>
        <view class="upload-area" @click="handleChooseFile">
          <text v-if="!uploadedFile">点击选择文件（支持 PDF/Word/Txt）</text>
          <text v-else class="uploaded-file-name">{{ uploadedFile.name }} ({{ formatFileSize(uploadedFile.size) }})</text>
        </view>
        <button
          v-if="uploadedFile"
          class="btn btn-small btn-outline"
          :loading="uploading"
          @click="handleUploadMaterial"
        >上传到工作台</button>
      </view>

      <!-- 用户输入 -->
      <view class="field-row column">
        <view class="field-label">创作需求</view>
        <textarea
          class="input-area"
          v-model="inputText"
          placeholder="例如：帮我写一篇关于提升小红书笔记爆款率的心得分享"
          :auto-height="true"
          maxlength="-1"
        />
      </view>

      <!-- 操作按钮 -->
      <view class="actions-row">
        <button
          v-if="hasResult"
          class="btn btn-secondary"
          :loading="regenerating"
          :disabled="regenerating"
          @click="handleRegenerate"
        >
          {{ regenerating ? '重新生成中...' : '🔄 重新生成' }}
        </button>
        <button
          class="btn btn-primary"
          :loading="loading"
          :disabled="loading || !inputText.trim()"
          @click="handleGenerate"
        >
          {{ loading ? '生成中...' : '✨ 生成内容' }}
        </button>
      </view>

      <!-- 生成结果展示 -->
      <view v-if="hasResult" class="result-card">
        <view class="result-header">
          <text class="result-label">生成结果</text>
          <view class="result-actions">
            <text v-if="resultStatus === 'completed'" class="result-status">生成完毕</text>
            <button
              v-if="resultStatus === 'completed'"
              class="btn-copy"
              @click="handleCopyResult"
            >
              复制
            </button>
          </view>
        </view>
        <view class="result-title">{{ resultTitle }}</view>
        <view class="result-body">
          <text v-for="(line, idx) in resultBodyLines" :key="idx">{{ line }}{{ idx < resultBodyLines.length - 1 ? '\n' : '' }}</text>
        </view>
        <view v-if="resultImageUrl" class="result-image">
          <image :src="resultImageUrl" mode="widthFix" />
        </view>
        <view class="result-meta">
          <text>生成时间: {{ resultTimestamp }}</text>
        </view>
      </view>

      <!-- 占位提示 -->
      <view v-else class="placeholder">
        <text>选择平台和素材来源，输入创作需求，点击生成按钮开始创作。</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import http from '../../utils/http.js'

// ========== 平台与素材源选项 ==========
const platforms = [
  { label: '小红书', value: 'xiaohongshu' },
  { label: '抖音', value: 'douyin' }
]
const materialSources = [
  { label: '联网检索', value: 'online' },
  { label: 'RAG知识库', value: 'rag' },
  { label: '上传素材', value: 'upload' }
]

// ========== 响应式状态 ==========
const sessionId = ref('')
const sessionInfo = ref({})
const platform = ref('xiaohongshu')
const materialSource = ref('online')
const inputText = ref('')

// 上传相关
const uploadedFile = ref(null)
const uploading = ref(false)

// 生成相关
const loading = ref(false)
const regenerating = ref(false)
const hasResult = ref(false)
const resultTitle = ref('')
const resultBody = ref('')
const resultImageUrl = ref('')
const resultStatus = ref('')
const resultTimestamp = ref('')

// ========== 计算属性 ==========
const resultBodyLines = computed(() => {
  return resultBody.value ? resultBody.value.split('\n') : []
})

// ========== 工具函数 ==========
const formatTime = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0B'
  if (bytes < 1024) return bytes + 'B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + 'KB'
  return (bytes / 1024 / 1024).toFixed(1) + 'MB'
}

// ========== 会话管理 ==========
const initSession = async () => {
  try {
    loading.value = true
    const res = await http.createSession()
    sessionId.value = res?.data?.session_id || ''
    if (sessionId.value) {
      sessionInfo.value = {
        created_at: res?.data?.created_at,
        expires_at: res?.data?.expires_at,
        message_count: 0
      }
    }
  } catch (e) {
    console.error('创建工作台会话失败:', e)
    uni.showToast({ title: e?.message || '创建会话失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

const createNewSession = async () => {
  // 清空当前结果
  hasResult.value = false
  resultTitle.value = ''
  resultBody.value = ''
  resultImageUrl.value = ''
  inputText.value = ''
  await initSession()
  uni.showToast({ title: '已创建新会话', icon: 'success' })
}

const refreshSessionInfo = async () => {
  if (!sessionId.value) return
  try {
    const res = await http.getSession(sessionId.value)
    if (res?.data) {
      sessionInfo.value = res.data
    }
  } catch (e) {
    console.error('获取会话信息失败:', e)
    uni.showToast({ title: e?.message || '获取会话信息失败', icon: 'none' })
  }
}

// ========== 文件上传 ==========
const handleChooseFile = () => {
  uni.chooseMessageFile({
    count: 1,
    type: 'file',
    extension: ['pdf', 'doc', 'docx', 'txt'],
    success: (res) => {
      if (res.tempFiles && res.tempFiles.length > 0) {
        uploadedFile.value = res.tempFiles[0]
      }
    },
    fail: () => {
      // 小程序环境可能不支持，尝试 chooseFile
      uni.chooseFile && uni.chooseFile({
        count: 1,
        extension: ['pdf', 'doc', 'docx', 'txt'],
        success: (res) => {
          if (res.tempFiles && res.tempFiles.length > 0) {
            uploadedFile.value = res.tempFiles[0]
          }
        }
      })
    }
  })
}

const handleUploadMaterial = async () => {
  if (!uploadedFile.value || !sessionId.value) return
  try {
    uploading.value = true
    // 使用 uni.uploadFile 上传
    const token = uni.getStorageSync('access_token')
    const uploadRes = await new Promise((resolve, reject) => {
      uni.uploadFile({
        url: 'http://localhost:8000/api/v1/workspace/upload-material',
        filePath: uploadedFile.value.path,
        name: 'file',
        formData: { session_id: sessionId.value },
        header: { 'Authorization': `Bearer ${token}` },
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(JSON.parse(res.data))
          } else {
            reject(new Error('上传失败'))
          }
        },
        fail: reject
      })
    })
    if (uploadRes?.code === 200) {
      uni.showToast({ title: '素材上传成功', icon: 'success' })
    }
  } catch (e) {
    console.error('上传素材失败:', e)
    uni.showToast({ title: e?.message || '上传失败', icon: 'none' })
  } finally {
    uploading.value = false
  }
}

// ========== 内容生成 ==========
const handleGenerate = async () => {
  if (!inputText.value.trim()) return
  if (!sessionId.value) {
    await initSession()
    if (!sessionId.value) return
  }

  try {
    loading.value = true
    const payload = {
      session_id: sessionId.value,
      message: inputText.value,
      material_source: materialSource.value,
      platform: platform.value
    }
    const res = await http.sendMessage(payload)
    const content = res?.data?.content
    if (content) {
      resultTitle.value = content.title || ''
      resultBody.value = content.body || ''
      resultImageUrl.value = content.image_url || ''
      resultStatus.value = res?.data?.status || 'completed'
      resultTimestamp.value = formatTime(res?.data?.timestamp)
      hasResult.value = true
      // 刷新会话信息
      await refreshSessionInfo()
    } else {
      uni.showToast({ title: '后端未返回内容', icon: 'none' })
    }
  } catch (e) {
    console.error('发送消息失败:', e)
    uni.showToast({ title: e?.message || '生成失败，请稍后重试', icon: 'none' })
  } finally {
    loading.value = false
  }
}

// ========== 重新生成 ==========
const handleRegenerate = async () => {
  if (!sessionId.value) return
  try {
    regenerating.value = true
    const payload = {
      session_id: sessionId.value,
      adjustments: {
        emotion_intensity: 'high',
        style_preference: platform.value === 'xiaohongshu' ? '小红书爆款' : '抖音热门'
      }
    }
    const res = await http.regenerate(payload)
    const content = res?.data?.content
    if (content) {
      resultTitle.value = content.title || ''
      resultBody.value = content.body || ''
      resultImageUrl.value = content.image_url || ''
      resultStatus.value = res?.data?.status || 'completed'
      resultTimestamp.value = formatTime(res?.data?.timestamp)
      // 刷新会话信息
      await refreshSessionInfo()
      uni.showToast({ title: '重新生成完成', icon: 'success' })
    }
  } catch (e) {
    console.error('重新生成失败:', e)
    uni.showToast({ title: e?.message || '重新生成失败', icon: 'none' })
  } finally {
    regenerating.value = false
  }
}

// ========== 复制结果 ==========
const handleCopyResult = () => {
  let content = ''
  if (resultTitle.value) {
    content += resultTitle.value + '\n\n'
  }
  if (resultBody.value) {
    content += resultBody.value
  }
  
  if (!content.trim()) {
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

// ========== 生命周期 ==========
onLoad(async () => {
  await initSession()
})
</script>

<style scoped>
.workspace-page {
  min-height: 100vh;
  padding: 20rpx;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.header {
  text-align: center;
  margin-bottom: 32rpx;
  padding: 32rpx 0;
}

.title {
  font-size: 44rpx;
  font-weight: 700;
  color: #3c9cff;
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
  box-shadow: 0 8rpx 30rpx rgba(60, 156, 255, 0.1);
  padding: 32rpx 28rpx;
  margin-bottom: 24rpx;
}

.card-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 28rpx;
  padding-bottom: 16rpx;
  border-bottom: 2rpx dashed #f0f0f0;
}

/* 会话信息卡片 */
.session-card {
  padding: 24rpx;
}

.session-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.session-label {
  font-size: 26rpx;
  color: #666;
}

.session-id {
  font-size: 24rpx;
  color: #3c9cff;
  font-family: monospace;
}

.session-meta {
  display: flex;
  gap: 24rpx;
  font-size: 24rpx;
  color: #999;
  margin-bottom: 16rpx;
}

.session-actions {
  display: flex;
  gap: 16rpx;
}

/* 字段行 */
.field-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
}

.field-row.column {
  flex-direction: column;
  align-items: flex-start;
}

.field-label {
  font-size: 28rpx;
  color: #555;
  margin-bottom: 12rpx;
}

.field-value {
  font-size: 28rpx;
  color: #333;
}

.tags-row {
  display: flex;
  gap: 16rpx;
}

.tag {
  padding: 10rpx 24rpx;
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

/* 上传区域 */
.upload-area {
  width: 100%;
  min-height: 120rpx;
  border: 2rpx dashed #d0d0d0;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fafafa;
  margin-bottom: 16rpx;
  padding: 20rpx;
  box-sizing: border-box;
}

.upload-area text {
  font-size: 26rpx;
  color: #999;
}

.uploaded-file-name {
  color: #3c9cff !important;
}

/* 输入区域 */
.input-area {
  width: 100%;
  min-height: 160rpx;
  border-radius: 16rpx;
  border: 2rpx solid #e5e5e5;
  padding: 20rpx;
  font-size: 28rpx;
  background-color: #fafafa;
  box-sizing: border-box;
}

/* 按钮 */
.actions-row {
  margin-top: 24rpx;
  display: flex;
  justify-content: flex-end;
  gap: 16rpx;
}

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

/* 结果卡片 */
.result-card {
  margin-top: 32rpx;
  padding: 24rpx;
  border-radius: 16rpx;
  background: linear-gradient(135deg, #f9fbff 0%, #f0f7ff 100%);
  border: 2rpx solid rgba(60, 156, 255, 0.15);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.result-label {
  font-size: 26rpx;
  color: #666;
}

.result-actions {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.result-status {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  color: #52c41a;
  background-color: rgba(82, 196, 26, 0.1);
  padding: 6rpx 16rpx;
  border-radius: 999rpx;
  height: 40rpx;
  box-sizing: border-box;
}

.btn-copy {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  color: #52c41a;
  background-color: rgba(82, 196, 26, 0.1);
  padding: 6rpx 16rpx;
  border-radius: 999rpx;
  border: none;
  cursor: pointer;
  height: 40rpx;
  box-sizing: border-box;
  font-weight: normal;
}

.result-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 16rpx;
  line-height: 1.4;
}

.result-body {
  font-size: 28rpx;
  color: #555;
  line-height: 1.7;
  white-space: pre-wrap;
  margin-bottom: 16rpx;
}

.result-image {
  margin: 16rpx 0;
}

.result-image image {
  width: 100%;
  border-radius: 12rpx;
}

.result-meta {
  font-size: 22rpx;
  color: #999;
  text-align: right;
}

/* 占位提示 */
.placeholder {
  text-align: center;
  padding: 60rpx 20rpx;
  color: #999;
  font-size: 26rpx;
}
</style>
