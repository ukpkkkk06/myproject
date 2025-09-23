<template>
  <view class="container">
    <view class="title">欢迎来到大厅</view>
    <view class="btn-col">
      <button class="action-btn" @tap="goPractice">开始刷题</button>
      <button class="action-btn" @tap="goHistory">历史考试</button>
      <button class="action-btn" @tap="goWrongbook">错题本</button>
      <button class="action-btn" @tap="goProfile">个人中心</button>
    </view>
  </view>
</template>

<script setup lang="ts">
function goPractice() { uni.navigateTo({ url: '/pages/practice/practice' }) }
function goHistory() { uni.showToast({ icon: 'none', title: '待实现' }) }
function goWrongbook() { uni.showToast({ icon: 'none', title: '待实现' }) }
function goProfile() { uni.navigateTo({ url: '/pages/profile/profile' }) }
</script>

<style scoped>
.container { padding: 24rpx; }
.title { font-size: 36rpx; font-weight: 600; margin-bottom: 24rpx; }
.btn-col { display: flex; flex-direction: column; gap: 16rpx; }
.action-btn { width: 100%; height: 88rpx; line-height: 88rpx; background: #1677ff; color: #fff; border: none; border-radius: 12rpx; font-size: 30rpx; }
</style>