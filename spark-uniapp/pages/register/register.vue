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
          placeholder="请输入密码（6-20位）"
          placeholder-class="placeholder"
          type="password"
        />
      </view>
      
      <view class="input-group">
        <text class="label">确认密码</text>
        <input
          v-model="formData.confirmPassword"
          class="input"
          placeholder="请再次输入密码"
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
import { ref, reactive, onUnmounted } from 'vue'
import http from '@/utils/http.js'
import storage from '@/utils/storage.js'

const formData = reactive({
  username: '',
  email: '',
  verifyCode: '',
  password: '',
  confirmPassword: ''
})

const loading = ref(false)
const codeCountdown = ref(0)
let countdownTimer = null

// 邮箱格式验证
const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// 发送验证码
const sendCode = async () => {
  if (!formData.email.trim()) {
    uni.showToast({ title: '请先输入邮箱', icon: 'none' })
    return
  }
  
  if (!validateEmail(formData.email)) {
    uni.showToast({ title: '请输入正确的邮箱格式', icon: 'none' })
    return
  }
  
  // 如果正在倒计时，不允许重复发送
  if (codeCountdown.value > 0) {
    return
  }
  
  try {
    uni.showLoading({ title: '发送中...' })
    
    // 调用发送验证码API
    await http.sendCode(formData.email.trim())
    
    uni.showToast({ title: '验证码已发送，请查收邮箱', icon: 'success', duration: 2000 })
    
    // 开始倒计时
    codeCountdown.value = 60
    if (countdownTimer) {
      clearInterval(countdownTimer)
    }
    countdownTimer = setInterval(() => {
      codeCountdown.value--
      if (codeCountdown.value <= 0) {
        clearInterval(countdownTimer)
        countdownTimer = null
      }
    }, 1000)
  } catch (e) {
    console.error('发送验证码失败:', e)
    uni.showToast({
      title: e.message || '验证码发送失败，请稍后重试',
      icon: 'none',
      duration: 2000
    })
  } finally {
    uni.hideLoading()
  }
}

// 用户注册
const handleRegister = async () => {
  // 表单验证
  if (!formData.username.trim()) {
    uni.showToast({ title: '请输入用户名', icon: 'none' })
    return
  }
  
  if (formData.username.trim().length < 3 || formData.username.trim().length > 20) {
    uni.showToast({ title: '用户名长度为3-20个字符', icon: 'none' })
    return
  }
  
  if (!formData.email.trim()) {
    uni.showToast({ title: '请输入邮箱', icon: 'none' })
    return
  }
  
  if (!validateEmail(formData.email)) {
    uni.showToast({ title: '请输入正确的邮箱格式', icon: 'none' })
    return
  }
  
  if (!formData.verifyCode.trim()) {
    uni.showToast({ title: '请输入验证码', icon: 'none' })
    return
  }
  
  if (formData.verifyCode.trim().length !== 4) {
    uni.showToast({ title: '验证码为4位数字', icon: 'none' })
    return
  }
  
  if (!formData.password.trim()) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return
  }
  
  if (formData.password.length < 6 || formData.password.length > 20) {
    uni.showToast({ title: '密码长度为6-20个字符', icon: 'none' })
    return
  }
  
  if (!formData.confirmPassword.trim()) {
    uni.showToast({ title: '请确认密码', icon: 'none' })
    return
  }
  
  if (formData.password !== formData.confirmPassword) {
    uni.showToast({ title: '两次输入的密码不一致', icon: 'none' })
    return
  }
  
  loading.value = true
  uni.showLoading({ title: '注册中...' })
  
  try {
    // 调用注册API
    await http.register({
      username: formData.username.trim(),
      email: formData.email.trim(),
      password: formData.password,
      confirm_password: formData.confirmPassword,
      code: formData.verifyCode.trim()
    })
    
    uni.showToast({ title: '注册成功', icon: 'success' })
    
    // 注册成功后，自动登录
    setTimeout(async () => {
      try {
        const loginResult = await http.login({
          email: formData.email.trim(),
          password: formData.password
        })
        
        // 存储Token和用户信息
        storage.setToken(loginResult.token)
        storage.setUserInfo(loginResult.user)
        
        // 跳转到工作台
        uni.switchTab({
          url: '/pages/workspace/workspace'
        })
      } catch (e) {
        // 自动登录失败，跳转到登录页
        console.error('自动登录失败:', e)
        uni.showToast({
          title: '注册成功，请登录',
          icon: 'success'
        })
        setTimeout(() => {
          uni.navigateTo({
            url: '/pages/login/login'
          })
        }, 1500)
      }
    }, 1500)
  } catch (e) {
    console.error('注册失败:', e)
    uni.showToast({
      title: e.message || '注册失败，请检查信息后重试',
      icon: 'none',
      duration: 2000
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

// 组件卸载时清除定时器
onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
})
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

