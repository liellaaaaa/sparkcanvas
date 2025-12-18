<template>
  <view class="login-page">
    <view class="header">
      <text class="title">欢迎使用 SparkCanvas</text>
      <text class="subtitle">AI内容创作平台</text>
    </view>
    
    <view class="login-card card">
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
        <text class="label">密码</text>
        <input
          v-model="formData.password"
          class="input"
          placeholder="请输入密码"
          placeholder-class="placeholder"
          type="password"
        />
      </view>
      
      <button class="btn login-btn" @click="handleLogin" :loading="loading">
        {{ loading ? '登录中...' : '登录' }}
      </button>
      
      <view class="footer-links">
        <text class="link" @click="goToRegister">还没有账号？立即注册</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import http from '@/utils/http.js'
import storage from '@/utils/storage.js'

const formData = reactive({
  email: '',
  password: ''
})

const loading = ref(false)

// 邮箱格式验证
const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const handleLogin = async () => {
  // 表单验证
  if (!formData.email.trim()) {
    uni.showToast({ title: '请输入邮箱', icon: 'none' })
    return
  }
  
  if (!validateEmail(formData.email)) {
    uni.showToast({ title: '请输入正确的邮箱格式', icon: 'none' })
    return
  }
  
  if (!formData.password.trim()) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return
  }
  
  if (formData.password.length < 6) {
    uni.showToast({ title: '密码长度至少6位', icon: 'none' })
    return
  }
  
  loading.value = true
  uni.showLoading({ title: '登录中...' })
  
  try {
    // 调用登录API
    const result = await http.login({
      email: formData.email.trim(),
      password: formData.password
    })
    
    // 存储Token和用户信息
    storage.setToken(result.token)
    storage.setUserInfo(result.user)
    
    uni.showToast({ title: '登录成功', icon: 'success' })
    
    // 延迟跳转，让用户看到成功提示
    setTimeout(() => {
      uni.switchTab({
        url: '/pages/workspace/workspace'
      })
    }, 1500)
  } catch (e) {
    console.error('登录失败:', e)
    uni.showToast({
      title: e.message || '登录失败，请检查邮箱和密码',
      icon: 'none',
      duration: 2000
    })
  } finally {
    loading.value = false
    uni.hideLoading()
  }
}

const goToRegister = () => {
  uni.navigateTo({
    url: '/pages/register/register'
  })
}
</script>

<style scoped>
.login-page {
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

.login-btn {
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

.login-btn:active {
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

