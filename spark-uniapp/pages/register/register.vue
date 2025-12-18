<template>
  <view class="register-page">
    <view class="header">
      <text class="title">注册 SparkCanvas</text>
      <text class="subtitle">开启AI创作之旅</text>
    </view>
    
    <view class="register-card card">
      <view class="input-group">
        <text class="label">用户名</text>
        <input
          v-model="formData.username"
          class="input"
          placeholder="请输入用户名"
          placeholder-class="placeholder"
          type="text"
        />
      </view>
      
      <view class="input-group">
        <text class="label">邮箱</text>
        <input
          v-model="formData.email"
          class="input"
          placeholder="请输入邮箱"
          placeholder-class="placeholder"
          type="text"
        />
      </view>
      
      <view class="input-group">
        <text class="label">验证码</text>
        <view class="code-row">
          <input
            v-model="formData.verifyCode"
            class="input code-input"
            placeholder="请输入验证码"
            placeholder-class="placeholder"
            type="text"
          />
          <button class="code-btn" @click="sendCode" :disabled="codeCountdown > 0">
            {{ codeCountdown > 0 ? `${codeCountdown}s` : '发送验证码' }}
          </button>
        </view>
      </view>
      
      <view class="input-group">
        <text class="label">密码</text>
        <input
          v-model="formData.password"
          class="input"
          placeholder="请输入密码（8-32位）"
          placeholder-class="placeholder"
          type="password"
        />
      </view>
      
      <button class="btn register-btn" @click="handleRegister" :loading="loading">
        {{ loading ? '注册中...' : '注册' }}
      </button>
      
      <view class="footer-links">
        <text class="link" @click="goToLogin">已有账号？立即登录</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive } from 'vue'

const formData = reactive({
  username: '',
  email: '',
  verifyCode: '',
  password: ''
})

const loading = ref(false)
const codeCountdown = ref(0)

const sendCode = async () => {
  if (!formData.email.trim()) {
    uni.showToast({ title: '请先输入邮箱', icon: 'none' })
    return
  }
  
  // TODO: 调用发送验证码API
  // await http.sendCode({ email: formData.email })
  
  uni.showToast({ title: '验证码已发送', icon: 'success' })
  codeCountdown.value = 60
  const timer = setInterval(() => {
    codeCountdown.value--
    if (codeCountdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

const handleRegister = async () => {
  if (!formData.username.trim()) {
    uni.showToast({ title: '请输入用户名', icon: 'none' })
    return
  }
  if (!formData.email.trim()) {
    uni.showToast({ title: '请输入邮箱', icon: 'none' })
    return
  }
  if (!formData.verifyCode.trim()) {
    uni.showToast({ title: '请输入验证码', icon: 'none' })
    return
  }
  if (!formData.password.trim() || formData.password.length < 8) {
    uni.showToast({ title: '密码长度至少8位', icon: 'none' })
    return
  }
  
  loading.value = true
  uni.showLoading({ title: '注册中...' })
  
  try {
    // TODO: 调用注册API
    // const result = await http.register(formData)
    // uni.setStorageSync('access_token', result.access_token)
    // uni.setStorageSync('user_info', result.user)
    
    uni.showToast({ title: '注册成功', icon: 'success' })
    setTimeout(() => {
      uni.switchTab({
        url: '/pages/workspace/workspace'
      })
    }, 1500)
  } catch (e) {
    uni.showToast({
      title: e.message || '注册失败',
      icon: 'none'
    })
  } finally {
    loading.value = false
    uni.hideLoading()
  }
}

const goToLogin = () => {
  uni.navigateTo({
    url: '/pages/login/login'
  })
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  padding: 40rpx 30rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  text-align: center;
  margin-bottom: 60rpx;
  padding-top: 80rpx;
}

.title {
  font-size: 48rpx;
  font-weight: 700;
  color: #ffffff;
  display: block;
  margin-bottom: 12rpx;
}

.subtitle {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.8);
}

.card {
  background: #ffffff;
  border-radius: 24rpx;
  box-shadow: 0 8rpx 30rpx rgba(0, 0, 0, 0.2);
  padding: 50rpx 40rpx;
}

.input-group {
  margin-bottom: 40rpx;
}

.label {
  display: block;
  font-size: 30rpx;
  color: #333;
  margin-bottom: 16rpx;
  font-weight: 500;
}

.input {
  width: 100%;
  height: 88rpx;
  padding: 0 28rpx;
  border-radius: 16rpx;
  background: #f8f8f8;
  border: 2rpx solid #e0e0e0;
  font-size: 30rpx;
  color: #333;
  box-sizing: border-box;
}

.input:focus {
  border-color: #3c9cff;
  background: #f0f7ff;
}

.placeholder {
  color: #aaa;
}

.code-row {
  display: flex;
  gap: 20rpx;
}

.code-input {
  flex: 1;
}

.code-btn {
  width: 200rpx;
  height: 88rpx;
  line-height: 88rpx;
  font-size: 26rpx;
  color: #3c9cff;
  background: #f0f7ff;
  border: 2rpx solid #3c9cff;
  border-radius: 16rpx;
  padding: 0;
}

.code-btn[disabled] {
  opacity: 0.6;
  color: #999;
  border-color: #ccc;
}

.register-btn {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  font-size: 32rpx;
  font-weight: 600;
  border-radius: 50rpx;
  color: #fff;
  background: linear-gradient(135deg, #3c9cff, #2b7ce9);
  border: none;
  box-shadow: 0 6rpx 20rpx rgba(60, 156, 255, 0.3);
  margin-top: 20rpx;
}

.register-btn:active {
  transform: scale(0.98);
}

.footer-links {
  text-align: center;
  margin-top: 40rpx;
}

.link {
  font-size: 28rpx;
  color: #3c9cff;
}
</style>

