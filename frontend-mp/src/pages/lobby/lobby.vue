<template>
  <view class="page">
    <view class="custom-bar">
      <text class="title">大厅</text>
      <button class="logout" size="mini" @tap="logout">退出</button>
    </view>

    <view class="body">
      <view class="btn-col">
        <button class="action" @tap="goPractice">开始刷题</button>
        <button class="action" @tap="goQuestionBank">我的题库</button>
        <button class="action" @tap="goErrorBook">错题本</button>
        <button class="action" @tap="goProfile">个人中心</button>
        <button class="danger" @tap="logout">退出登录</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
function goPractice(){ uni.navigateTo({ url:'/pages/practice/practice' }) }
function goQuestionBank(){ uni.navigateTo({ url:'/pages/question-bank/question-bank' }) }
function goErrorBook(){ uni.navigateTo({ url:'/pages/error-book/error-book' }) }
function goProfile(){ uni.navigateTo({ url:'/pages/profile/profile' }) }

function logout() {
  uni.showModal({
    title: '确认退出',
    content: '确定要退出当前账号？',
    success(res) {
      if (res.confirm) {
        try {
          uni.removeStorageSync('token')
          // 如果后端有 /logout 可在此调用
        } catch(e){}
        uni.reLaunch({ url:'/pages/login/login' })
      }
    }
  })
}
</script>

<style scoped>
.page { min-height:100vh; background:#f5f6fa; }
.custom-bar {
  height: 100rpx;
  padding: 0 28rpx;
  display:flex;
  align-items:flex-end;
  justify-content:space-between;
  padding-bottom:16rpx;
  background:#1677ff;
}
.title { color:#fff; font-size:36rpx; font-weight:600; }
.logout { line-height:1; background:#fff; color:#1677ff; }
.body { padding:32rpx; }
.btn-col { display:flex; flex-direction:column; gap:28rpx; }
.action {
  background:#1677ff;
  color:#fff;
  border-radius:12rpx;
}
.danger {
  background:#ff4d4f;
  color:#fff;
  border-radius:12rpx;
}
</style>