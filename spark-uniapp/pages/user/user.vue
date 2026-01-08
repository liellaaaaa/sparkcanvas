<template>
  <view class="workspace-page">
    <view class="bg-decoration"></view>

    <view class="header">
      <view class="title-wrapper">
        <text class="title">用户中心</text>
        <view class="badge">USER</view>
      </view>
      <text class="subtitle">查看账户信息与会话状态</text>
    </view>

    <view class="card">
      <view class="card-title">
        <uni-icons type="person" size="20" color="#3c9cff"></uni-icons>
        <text>账户信息</text>
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

      <button class="main-generate-btn logout-btn" @click="handleLogout">
        <uni-icons type="closeempty" size="18" color="#fff"></uni-icons>
        <text>退出登录</text>
      </button>
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

.header { margin-bottom: 40rpx; }
.title-wrapper { display: flex; align-items: center; gap: 12rpx; }
.title { font-size: 52rpx; font-weight: 800; color: #1a1a1a; }
.badge { background: #3c9cff; color: #fff; font-size: 18rpx; padding: 4rpx 10rpx; border-radius: 6rpx; }
.subtitle { font-size: 26rpx; color: #999; margin-top: 12rpx; display: block; }

.card {
  background: #ffffff;
  border-radius: 32rpx;
  padding: 40rpx;
  box-shadow: 0 15rpx 40rpx rgba(160, 180, 210, 0.1);
  border: 1rpx solid rgba(240, 244, 250, 0.8);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 12rpx;
  font-size: 30rpx;
  font-weight: 700;
  color: #333;
  margin-bottom: 40rpx;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f0f3f8;
}

.info-row:last-of-type {
  border-bottom: none;
}

.label {
  font-size: 28rpx;
  font-weight: 600;
  color: #444;
}

.value {
  font-size: 28rpx;
  color: #666;
}

.main-generate-btn {
  margin-top: 50rpx;
  height: 100rpx;
  line-height: 100rpx;
  color: #fff !important;
  font-size: 30rpx;
  font-weight: 700;
  border-radius: 28rpx;
  border: none;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  transition: all 0.3s;
}

.logout-btn {
  background: linear-gradient(135deg, #ff4d4f 0%, #e53935 100%);
}
</style>

