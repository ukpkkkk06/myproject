<template>
  <view class="lobby-page">
    <view class="nav">
      <text class="nav-title">大厅</text>
    </view>

    <view class="content">
      <view class="panel">
        <view class="panel-head">
          <text class="panel-title">功能中心</text>
          <text class="panel-sub">选择你要进行的操作</text>
        </view>

        <view class="vertical">
          <button class="btn primary fullW" @tap="goPractice">开始刷题</button>
          <button class="btn primary fullW" @tap="goQuestionBank">我的题库</button>
          <button class="btn primary fullW" @tap="goErrorBook">错题本</button>
          <button class="btn primary fullW" @tap="goProfile">个人中心</button>
        </view>

        <button class="btn danger fullW logout" @tap="logout">退出登录</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
function goPractice(){ uni.navigateTo({ url:'/pages/practice/practice' }) }
function goQuestionBank(){ uni.navigateTo({ url:'/pages/question-bank/question-bank' }) }
function goErrorBook(){ uni.navigateTo({ url:'/pages/error-book/error-book' }) }
function goProfile(){ uni.navigateTo({ url:'/pages/profile/profile' }) }
function logout(){
  uni.showModal({
    title:'确认退出',
    content:'确定要退出当前账号？',
    success(res){
      if(res.confirm){
        uni.removeStorageSync('token')
        uni.reLaunch({ url:'/pages/login/login' })
      }
    }
  })
}
</script>

<style scoped>
:root, page, .lobby-page {
  --c-bg-grad-top:#e8f2ff;
  --c-bg-grad-bottom:#f5f9ff;
  --c-panel:#ffffff;
  --c-border:#d8e6f5;
  --c-primary:#66b4ff;
  --c-primary-dark:#4b9ef0;
  --c-primary-light:#d4ecff;
  --c-text:#1f2d3d;
  --c-text-sec:#5f7085;
  --c-danger:#ff4d4f;
  --c-danger-dark:#d73a3c;
  --radius:20rpx;
  --radius-s:12rpx;
}

.lobby-page {
  min-height:100vh;
  background:linear-gradient(180deg,var(--c-bg-grad-top),var(--c-bg-grad-bottom));
  display:flex;
  flex-direction:column;
  box-sizing:border-box;
  padding-top:120rpx;
}

.nav {
  position:fixed;
  top:0; left:0; right:0;
  height:120rpx;
  padding:40rpx 36rpx 0;
  box-sizing:border-box;
  display:flex;
  justify-content:center;
  align-items:center;
  backdrop-filter:blur(10px);
  background:rgba(255,255,255,0.55);
  border-bottom:1rpx solid rgba(214,230,245,0.8);
  z-index:10;
}

.nav-title {
  font-size:40rpx;
  font-weight:700;
  letter-spacing:1rpx;
  color:var(--c-text);
}

.content {
  padding:40rpx 44rpx 120rpx;
  flex:1;
  display:flex;
  flex-direction:column;
  box-sizing:border-box;
}

.panel {
  background:var(--c-panel);
  border:1rpx solid var(--c-border);
  border-radius:var(--radius);
  padding:48rpx 42rpx 56rpx;
  box-shadow:0 8rpx 24rpx rgba(35,72,130,0.08),0 2rpx 6rpx rgba(35,72,130,0.06);
  display:flex;
  flex-direction:column;
  gap:46rpx;
}

.panel-head { display:flex; flex-direction:column; gap:10rpx; }
.panel-title { font-size:42rpx; font-weight:600; color:var(--c-text); }
.panel-sub { font-size:26rpx; color:var(--c-text-sec); }

.vertical {
  display:flex;
  flex-direction:column;
  gap:28rpx;
}

.btn {
  border:none;
  border-radius:var(--radius-s);
  font-size:30rpx;
  font-weight:600;
  letter-spacing:1rpx;
  padding:28rpx 0;
  color:#fff;
  background:#ccc;
  box-shadow:0 4rpx 10rpx rgba(0,0,0,0.08);
  transition:opacity .18s;
}

.btn.primary {
  background:linear-gradient(90deg,#a9d6ff,#66b4ff);
  box-shadow:0 6rpx 14rpx rgba(102,180,255,0.35);
}
.btn.primary:active,
.btn.danger:active { opacity:.85; }

.btn.danger {
  background:linear-gradient(90deg,var(--c-danger),var(--c-danger-dark));
  box-shadow:0 6rpx 14rpx rgba(255,77,79,0.28);
}

.fullW { width:100%; }
.logout { margin-top:4rpx; }

.btn[disabled]{ opacity:.55; }

@media (min-width:700rpx){
  .panel { max-width:680rpx; margin:0 auto; }
}
</style>