<template>
  <view class="user-page">
    <view class="card">
      <view class="header">
        <text class="title">用户中心</text>
        <text class="subtitle">查看账户信息与会话状态</text>
      </view>

      <view class="info-row">
        <text class="label">用户名</text>
        <text class="value">{{ userInfo.username || '未填写' }}</text>
      </view>

      <view class="info-row">
        <text class="label">邮箱</text>
        <text class="value">{{ userInfo.email || '未填写' }}</text>
      </view>

      <view class="info-row">
        <text class="label">Token 状态</text>
        <text class="value">{{ token ? '已登录' : '未登录' }}</text>
      </view>

      <button class="btn logout-btn" @click="handleLogout">退出登录</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '@/utils/http.js'
import storage from '@/utils/storage.js'

const userInfo = ref({})
const token = ref('')

const loadUser = () => {
  userInfo.value = storage.getUserInfo() || {}
  token.value = storage.getToken() || ''
}

const handleLogout = async () => {
  try {
    await http.logout()
    uni.showToast({ title: '已退出登录', icon: 'none' })
    setTimeout(() => {
      uni.reLaunch({
        url: '/pages/login/login'
      })
    }, 500)
  } catch (e) {
    uni.showToast({ title: e?.message || '退出失败', icon: 'none' })
  }
}

onMounted(() => {
  loadUser()
})
</script>

<style scoped>
.user-page {
  min-height: 100vh;
  padding: 32rpx;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9effd 100%);
  box-sizing: border-box;
}

.card {
  background: #fff;
  border-radius: 24rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.06);
  padding: 32rpx;
}

.header {
  margin-bottom: 24rpx;
}

.title {
  font-size: 36rpx;
  font-weight: 700;
  color: #333;
  display: block;
  margin-bottom: 8rpx;
}

.subtitle {
  font-size: 26rpx;
  color: #888;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 2rpx solid #f5f5f5;
}

.info-row:last-child {
  border-bottom: none;
}

.label {
  font-size: 28rpx;
  color: #666;
}

.value {
  font-size: 28rpx;
  color: #333;
}

.btn {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  border-radius: 16rpx;
  border: none;
  font-size: 30rpx;
  margin-top: 32rpx;
}

.logout-btn {
  background: #ffecec;
  color: #e53935;
}
</style>

