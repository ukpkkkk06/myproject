<template>
  <view class="container">
    <view class="title">欢迎来到大厅</view>
    <view class="hint">您已登录为普通用户。</view>
    <button class="btn" @tap="toProfile">个人中心（占位）</button>
    <button class="link" @tap="logout">退出登录</button>
  </view>
</template>

<script setup lang="ts">
function toProfile() {
  uni.showToast({ icon: 'none', title: 'TODO: 个人中心' })
}
function logout() {
  uni.removeStorageSync('token')
  uni.reLaunch({ url: '/pages/login/login' })
}
</script>

<style scoped>
.container { padding: 24rpx; }
.title { font-size: 36rpx; font-weight: 600; margin-bottom: 12rpx; }
.hint { color: #666; margin-bottom: 24rpx; }
.btn { background: #1677ff; color: #fff; padding: 20rpx; border-radius: 8rpx; margin-bottom: 12rpx; }
.link { background: transparent; color: #ff4d4f; }
</style>