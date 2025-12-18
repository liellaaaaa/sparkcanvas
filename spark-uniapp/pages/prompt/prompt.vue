<template>
  <view class="prompt-page">
    <view class="header">
      <text class="title">🎨 Prompt管理</text>
    </view>
    
    <view class="content-card card">
      <view class="placeholder">
        <text>Prompt管理功能开发中...</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

// TODO: 实现Prompt管理逻辑
</script>

<style scoped>
.prompt-page {
  min-height: 100vh;
  padding: 20rpx;
  background: #f8f8f8;
}

.header {
  text-align: center;
  margin-bottom: 40rpx;
  padding: 40rpx 0;
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
  padding: 40rpx 32rpx;
}

.placeholder {
  text-align: center;
  padding: 60rpx 0;
  color: #999;
}
</style>

