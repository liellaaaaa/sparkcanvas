<template>
  <view class="workspace-page">
    <view class="bg-decoration"></view>

    <view class="header">
      <view class="title-wrapper">
        <text class="title">SparkCanvas</text>
        <view class="badge">PRO</view>
      </view>
      <text class="subtitle">让灵感瞬间点燃，一键生成爆款内容</text>
    </view>

    <view class="content-card card">
      <view class="card-title">
        <uni-icons type="compose" size="20" color="#3c9cff"></uni-icons>
        <text>创作设置</text>
      </view>

      <view class="field-row">
        <text class="field-label-main">发布平台</text>
        <view class="field-right-content">
          <view v-for="p in platforms" :key="p.value" class="tag-container">
            <view 
              :class="['platform-tag', (platform === p.value || activeDropdown === p.value) ? 'tag-active' : 'tag-default']"
              @click="toggleDropdown(p.value)"
            >
              <text>{{ getDisplayName(p) }}</text>
              <uni-icons 
                :type="activeDropdown === p.value ? 'arrowup' : 'arrowdown'" 
                size="12" 
                :color="(platform === p.value || activeDropdown === p.value) ? '#fff' : '#999'"
              ></uni-icons>
            </view>

            <view v-if="activeDropdown === p.value" class="dropdown-box animate-in">
              <view class="dropdown-grid">
                <view 
                  v-for="(opt, index) in directionOptions" 
                  :key="index"
                  :class="[
                    'grid-item', 
                    (isDeleteMode && pendingDelete === opt) ? 'item-pending-delete' : '',
                    (!isDeleteMode && selectedDirections[p.value] === opt) ? 'item-selected' : ''
                  ]"
                  @click.stop="handleItemClick(p.value, opt)"
                >
                  {{ opt }}
                  <view v-if="!isDeleteMode && selectedDirections[p.value] === opt" class="selected-badge">
                    <uni-icons type="checkmarkempty" size="10" color="#fff"></uni-icons>
                  </view>
                  <view v-if="isDeleteMode" class="delete-badge">
                    <uni-icons type="closeempty" size="10" color="#fff"></uni-icons>
                  </view>
                </view>
                
                <view v-if="!isDeleteMode" class="grid-item custom-input-wrapper">
                  <template v-if="isAddingCustom">
                    <input 
                      class="inline-input" 
                      v-model="customInputName" 
                      placeholder="方向名" 
                      :focus="true"
                      @click.stop=""
                      @confirm="confirmInlineCustom(p.value)"
                    />
                    <view class="inline-actions">
                      <uni-icons type="checkbox-filled" size="18" color="#52c41a" @click.stop="confirmInlineCustom(p.value)"></uni-icons>
                      <uni-icons type="clear" size="18" color="#ff4d4f" @click.stop="isAddingCustom = false"></uni-icons>
                    </view>
                  </template>
                  <view v-else class="add-btn-inner" @click.stop="isAddingCustom = true">
                    <uni-icons type="plusempty" size="14" color="#3c9cff"></uni-icons>
                    <text class="add-text">定制</text>
                  </view>
                </view>
              </view>
              
              <view 
                :class="['manage-btn', isDeleteMode ? 'manage-btn-active' : '']" 
                @click.stop="toggleDeleteMode"
              >
                <uni-icons :type="isDeleteMode ? 'undo' : 'trash'" size="14" :color="isDeleteMode ? '#666' : '#ff4d4f'"></uni-icons>
                <text :style="{ color: isDeleteMode ? '#666' : '#ff4d4f', marginLeft: '6rpx' }">
                  {{ isDeleteMode ? '取消删除' : '删除方向' }}
                </text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <view v-if="activeDropdown" class="overlay" @click="closeDropdown"></view>

      <view class="field-row">
        <text class="field-label-main">增强模式</text>
        <view class="field-right-content">
          <text
            v-for="s in materialSources"
            :key="s.value"
            :class="['mini-tag', materialSource === s.value ? 'mini-tag-active' : 'mini-tag-default']"
            @click="materialSource = s.value"
          >{{ s.label }}</text>
        </view>
      </view>

      <view class="field-row-column">
        <view class="textarea-header">
          <text class="field-label-main">创作需求</text>
          <text class="word-count">{{ inputText.length }}/1000</text>
        </view>
        <view class="textarea-container">
          <textarea
            class="input-area"
            v-model="inputText"
            placeholder="描述你想写的主题，例如：帮我写一篇提升笔记爆款率的干货..."
            placeholder-style="color:#bbb;font-size:26rpx"
            maxlength="1000"
          />
        </view>
      </view>

      <button
        class="main-generate-btn"
        :loading="loading"
        :disabled="loading || !inputText.trim() || !platform"
        @click="handleGenerate"
      >
        <text v-if="!loading">🚀 开启 AI 创作灵感</text>
        <text v-else>正在生成中...</text>
      </button>
    </view>

    <!-- 生成结果展示区域 -->
    <view v-if="generatedContent" class="result-card card">
      <view class="card-title">
        <uni-icons type="checkmarkempty" size="20" color="#52c41a"></uni-icons>
        <text>生成结果</text>
      </view>
      <view class="result-content">
        <text class="result-text">{{ generatedContent }}</text>
      </view>
      <view class="result-actions">
        <button class="action-btn copy-btn" @click="copyContent">
          <uni-icons type="copy" size="16" color="#3c9cff"></uni-icons>
          <text>复制</text>
        </button>
        <button class="action-btn clear-btn" @click="clearContent">
          <uni-icons type="trash" size="16" color="#ff4d4f"></uni-icons>
          <text>清除</text>
        </button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import http from '@/utils/http.js'

const platforms = [{ label: '小红书', value: 'xiaohongshu' }, { label: '抖音', value: 'douyin' }]
const materialSources = [{ label: '联网搜索', value: 'online' }, { label: 'RAG知识库', value: 'rag' }]

const platform = ref('')
const selectedDirections = ref({ xiaohongshu: '', douyin: '' })
const activeDropdown = ref(null)

// 定制与删除逻辑状态
const isDeleteMode = ref(false)
const pendingDelete = ref('')
const isAddingCustom = ref(false)
const customInputName = ref('')

const directionOptions = ref(['美食', '宠物', '影视剧', '科普', '旅行', '美妆', '穿搭'])
const materialSource = ref('online')
const inputText = ref('')
const loading = ref(false)
const sessionId = ref('')
const generatedContent = ref('')

const getDisplayName = (p) => {
  const dir = selectedDirections.value[p.value]
  return dir ? `${p.label} - ${dir}` : p.label
}

const toggleDropdown = (v) => {
  // 点击平台标签时，立即选中该平台
  platform.value = v
  
  // 如果下拉框已打开，则关闭；否则打开
  if (activeDropdown.value === v) {
    closeDropdown()
  } else {
    activeDropdown.value = v
  }
}

const closeDropdown = () => {
  activeDropdown.value = null
  isDeleteMode.value = false
  isAddingCustom.value = false
  customInputName.value = ''
  pendingDelete.value = ''
}

const toggleDeleteMode = () => {
  isDeleteMode.value = !isDeleteMode.value
  isAddingCustom.value = false
  pendingDelete.value = ''
}

const handleItemClick = (pVal, opt) => {
  if (!isDeleteMode.value) {
    // 如果点击的是已选中的方向，则取消选择方向（但保持平台选中）
    if (selectedDirections.value[pVal] === opt) {
      selectedDirections.value[pVal] = ''
      // 不清除 platform，保持平台选中状态
    } else {
      // 选择新方向
      platform.value = pVal
      selectedDirections.value[pVal] = opt
    }
    closeDropdown()
  } else {
    if (pendingDelete.value === opt) executeDelete(opt)
    else pendingDelete.value = opt
  }
}

const executeDelete = (opt) => {
  directionOptions.value = directionOptions.value.filter(item => item !== opt)
  platforms.forEach(p => {
    if (selectedDirections.value[p.value] === opt) {
      selectedDirections.value[p.value] = ''
      // 删除方向时不清除平台，保持平台选中状态
    }
  })
  pendingDelete.value = ''
  uni.showToast({ title: '已移除', icon: 'none' })
}

// 行内定制确认逻辑
const confirmInlineCustom = (pId) => {
  const val = customInputName.value.trim()
  if (!val) {
    isAddingCustom.value = false
    return
  }
  if (!directionOptions.value.includes(val)) {
    directionOptions.value.push(val)
  }
  platform.value = pId
  selectedDirections.value[pId] = val
  closeDropdown()
  uni.showToast({ title: '定制成功并选中', icon: 'none' })
}

const handleGenerate = async () => {
  // 验证必填项
  if (!inputText.value.trim()) {
    uni.showToast({ title: '请输入创作需求', icon: 'none' })
    return
  }
  
  if (!platform.value) {
    uni.showToast({ title: '请选择发布平台', icon: 'none' })
    return
  }

  loading.value = true
  
  try {
    // 如果没有会话ID，先创建会话
    if (!sessionId.value) {
      const sessionRes = await http.createSession()
      if (sessionRes.code === 200 && sessionRes.data) {
        sessionId.value = sessionRes.data.session_id
      } else {
        throw new Error(sessionRes.message || '创建会话失败')
      }
    }

    // 发送消息，触发内容生成
    // 获取当前平台选中的方向
    const direction = selectedDirections.value[platform.value] || ''
    
    const messageRes = await http.sendMessage({
      session_id: sessionId.value,
      message: inputText.value.trim(),
      material_source: materialSource.value,
      platform: platform.value,
      direction: direction  // 传递方向信息
    })

    if (messageRes.code === 200 && messageRes.data) {
      const content = messageRes.data.content
      // 将生成的内容对象转换为纯文本字符串（只提取 title 和 body）
      let textContent = ''
      if (typeof content === 'object' && content !== null) {
        // 如果 content 是对象，提取 title 和 body
        const title = content.title || ''
        const body = content.body || ''
        // 组合标题和正文，去除 Markdown 格式标记
        textContent = title ? `${title}\n\n${body}` : body
        // 清理 Markdown 标记（如 #、**、* 等）
        textContent = textContent
          .replace(/^#+\s*/gm, '') // 移除标题标记
          .replace(/\*\*(.*?)\*\*/g, '$1') // 移除粗体标记
          .replace(/\*(.*?)\*/g, '$1') // 移除斜体标记
          .replace(/`(.*?)`/g, '$1') // 移除行内代码标记
          .trim()
      } else if (typeof content === 'string') {
        // 如果 content 已经是字符串，直接使用
        textContent = content
      }
      // 将纯文本内容保存到响应式变量中
      generatedContent.value = textContent
      uni.showToast({ 
        title: '生成成功', 
        icon: 'success',
        duration: 2000
      })
    } else {
      throw new Error(messageRes.message || '生成失败')
    }
  } catch (error) {
    console.error('生成失败:', error)
    uni.showToast({ 
      title: error.message || '生成失败，请重试', 
      icon: 'none',
      duration: 3000
    })
  } finally {
    loading.value = false
  }
}

// 复制内容到剪贴板
const copyContent = () => {
  // 确保复制的是字符串
  const textToCopy = typeof generatedContent.value === 'string' 
    ? generatedContent.value 
    : String(generatedContent.value || '')
  
  uni.setClipboardData({
    data: textToCopy,
    success: () => {
      uni.showToast({ 
        title: '已复制到剪贴板', 
        icon: 'success',
        duration: 2000
      })
    }
  })
}

// 清除生成的内容
const clearContent = () => {
  generatedContent.value = ''
  uni.showToast({ 
    title: '已清除', 
    icon: 'none',
    duration: 1500
  })
}
</script>

<style scoped>
.workspace-page {
  min-height: 100vh;
  padding: 40rpx 30rpx;
  background-color: #fcfdfe;
  position: relative;
}

.bg-decoration {
  position: absolute;
  top: -150rpx; right: -100rpx; width: 500rpx; height: 500rpx;
  background: radial-gradient(circle, rgba(60, 156, 255, 0.08) 0%, transparent 70%);
}

.header { margin-bottom: 50rpx; }
.title-wrapper { display: flex; align-items: center; gap: 12rpx; }
.title { font-size: 52rpx; font-weight: 800; color: #1a1a1a; }
.badge { background: #3c9cff; color: #fff; font-size: 18rpx; padding: 4rpx 10rpx; border-radius: 6rpx; }
.subtitle { font-size: 26rpx; color: #999; margin-top: 12rpx; display: block; }

.card {
  background: #ffffff; border-radius: 40rpx; padding: 40rpx;
  box-shadow: 0 30rpx 80rpx rgba(160, 180, 210, 0.12);
  border: 1rpx solid rgba(240, 244, 250, 0.8);
}

.card-title { display: flex; align-items: center; gap: 12rpx; font-size: 30rpx; font-weight: 700; color: #333; margin-bottom: 40rpx; }

.field-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 44rpx; }
.field-row-column { display: flex; flex-direction: column; margin-bottom: 44rpx; }
.field-label-main { font-size: 28rpx; font-weight: 600; color: #444; }
.field-right-content { display: flex; justify-content: flex-end; gap: 16rpx; flex-grow: 1; }
.textarea-header { display: flex; justify-content: space-between; align-items: center; }

.platform-tag { display: flex; align-items: center; gap: 8rpx; padding: 12rpx 24rpx; border-radius: 16rpx; font-size: 24rpx; transition: all 0.2s; }
.tag-active { background: #3c9cff; color: #fff !important; }
.tag-default { background: #f5f7fa; color: #777; }

.mini-tag { padding: 10rpx 20rpx; border-radius: 12rpx; font-size: 22rpx; transition: all 0.2s; }
.mini-tag-active { background: #3c9cff; color: #fff !important; }
.mini-tag-default { background: #f5f7fa; color: #777; }

.dropdown-box {
  position: absolute; top: 80rpx; right: 0; width: 360rpx;
  background: rgba(255, 255, 255, 0.98); backdrop-filter: blur(10px);
  border-radius: 24rpx; padding: 20rpx; z-index: 1001;
  box-shadow: 0 20rpx 50rpx rgba(0,0,0,0.1); border: 1rpx solid #eee;
}

.dropdown-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12rpx; margin-bottom: 20rpx;}
.grid-item { position: relative; padding: 16rpx; background: #f8faff; border-radius: 12rpx; font-size: 22rpx; text-align: center; color: #444; transition: all 0.3s; display: flex; align-items: center; justify-content: center;}

/* 定制输入框样式 */
.custom-input-wrapper {
  grid-column: span 1;
  border: 1rpx dashed #3c9cff;
  background: #fff !important;
  padding: 8rpx !important;
}

.inline-input {
  width: 65%;
  font-size: 20rpx;
  text-align: left;
  padding-left: 8rpx;
}

.inline-actions {
  display: flex;
  gap: 4rpx;
}

.add-btn-inner {
  display: flex;
  align-items: center;
  gap: 4rpx;
}

/* 状态样式 */
.item-selected { background-color: #3c9cff !important; color: #ffffff !important; }
.selected-badge { position: absolute; top: -6rpx; right: -6rpx; width: 22rpx; height: 22rpx; background: #52c41a; border-radius: 50%; display: flex; justify-content: center; align-items: center; border: 2rpx solid #fff; }
.item-pending-delete { background-color: #ff4d4f !important; color: #ffffff !important; transform: scale(1.05); }
.delete-badge { position: absolute; top: -6rpx; right: -6rpx; width: 22rpx; height: 22rpx; background: #ff4d4f; border-radius: 50%; display: flex; justify-content: center; align-items: center; border: 2rpx solid #fff; }

.manage-btn { display: flex; justify-content: center; align-items: center; padding: 14rpx; background-color: #fff1f0; border-radius: 12rpx; font-size: 22rpx; }
.manage-btn-active { background-color: #f5f5f5; }

.add-text { font-size: 20rpx; color: #3c9cff; }

.textarea-container { background: #f8f9fb; border-radius: 24rpx; padding: 24rpx; border: 2rpx solid #f0f2f5; margin-top: 16rpx; }
.input-area { width: 100%; height: 260rpx; font-size: 28rpx; color: #333; line-height: 1.6;}
.word-count { font-size: 20rpx; color: #ccc; }

.main-generate-btn { 
  margin-top: 50rpx; 
  height: 100rpx; 
  line-height: 100rpx; 
  background: linear-gradient(135deg, #3c9cff 0%, #007aff 100%); 
  color: #fff !important; 
  font-size: 30rpx; 
  font-weight: 700; 
  border-radius: 28rpx; 
  border: none; 
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.main-generate-btn:disabled {
  opacity: 0.6;
  background: linear-gradient(135deg, #ccc 0%, #aaa 100%);
}

.overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 1000; }
.animate-in { animation: fadeIn 0.2s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-10rpx); } to { opacity: 1; transform: translateY(0); } }

/* 生成结果卡片样式 */
.result-card {
  margin-top: 40rpx;
  animation: fadeIn 0.3s ease-out;
}

.result-content {
  background: #f8f9fb;
  border-radius: 24rpx;
  padding: 30rpx;
  border: 2rpx solid #f0f2f5;
  margin-bottom: 30rpx;
  min-height: 200rpx;
  max-height: 800rpx;
  overflow-y: auto;
}

.result-text {
  font-size: 28rpx;
  color: #333;
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.result-actions {
  display: flex;
  gap: 20rpx;
  justify-content: flex-end;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 16rpx 32rpx;
  border-radius: 16rpx;
  font-size: 26rpx;
  border: none;
  background: #f5f7fa;
  color: #666;
  transition: all 0.2s;
}

.copy-btn:active {
  background: #e6f4ff;
  color: #3c9cff;
}

.clear-btn:active {
  background: #fff1f0;
  color: #ff4d4f;
}
</style>