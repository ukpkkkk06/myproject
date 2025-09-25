<template>
  <view class="login-page">
    <view class="brand-area">
      <text class="logo">题练平台</text>
      <text class="slogan">轻松高效 · 专注练题</text>
    </view>

    <view class="card">
      <view class="card-title">登录账户</view>

      <view class="field">
        <input
          v-model="account"
          class="ipt"
          placeholder="账号"
          placeholder-class="ipt-ph"
          @focus="focus='account'"
          @blur="focus=''"
        />
      </view>

      <view class="field">
        <input
          v-model="password"
          password
          class="ipt"
          placeholder="密码"
          placeholder-class="ipt-ph"
          @focus="focus='password'"
          @blur="focus=''"
        />
      </view>

      <button class="btn primary" :disabled="loading" @tap="onLogin">
        登录
      </button>

      <view class="links">
        <text class="link" @tap="goRegister">没有账号？立即注册</text>
      </view>
    </view>

    <view class="footer">
      <text class="ft-text">© 2025 Quiz App</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'

const account = ref('')
const password = ref('')
const loading = ref(false)
const focus = ref('')
const placeholderStyle = 'color:#9fb5cc;font-size:28rpx;'

function toast(t:string){ uni.showToast({ icon:'none', title:t }) }

async function onLogin(){
  const acc = account.value.trim()
  const pwd = password.value.trim()
  if(!acc || !pwd) return toast('请输入账号和密码')
  loading.value = true
  try{
    uni.removeStorageSync('token')
    const token = await api.login(acc, pwd)
    uni.setStorageSync('token', token.access_token)
    const me = await api.me()
    uni.reLaunch({ url: me.is_admin ? '/pages/index/index' : '/pages/lobby/lobby' })
  }catch(e:any){
    toast(e?.data?.message || '登录失败')
  }finally{
    loading.value = false
  }
}

function goRegister(){
  uni.redirectTo({ url:'/pages/register/register' })
}

onMounted(async ()=>{
  const t = uni.getStorageSync('token')
  if(!t) return
  try{
    const me = await api.me()
    uni.reLaunch({ url: me.is_admin ? '/pages/index/index' : '/pages/lobby/lobby' })
  }catch{ uni.removeStorageSync('token') }
})
</script>

<style scoped>
/* 颜色变量保持，仅调整按钮浅蓝 */
:root, page {
  --c-bg: #f5f9ff;
  --c-bg-grad-top: #e8f2ff;
  --c-bg-grad-bottom: #f5f9ff;
  --c-panel: #ffffff;
  --c-border: #d8e6f5;
  --c-primary: #66b4ff;          /* 浅蓝主色 */
  --c-primary-dark: #4b9ef0;     /* 略深 */
  --c-primary-light: #d4ecff;
  --c-text: #1f2d3d;
  --c-text-sec: #5f7085;
  --radius: 20rpx;
  --radius-s: 12rpx;
}

.login-page {
  min-height: 100vh;
  padding: 80rpx 56rpx 60rpx;
  box-sizing: border-box;
  background: linear-gradient(180deg,var(--c-bg-grad-top),var(--c-bg-grad-bottom));
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

.brand-area {
  text-align: center;
  margin-bottom: 60rpx;
  user-select: none;
}

.logo {
  font-size: 56rpx;
  font-weight: 700;
  letter-spacing: 2rpx;
  color: var(--c-primary-dark);
  text-shadow: 0 4rpx 8rpx rgba(58,131,247,0.18);
}

.slogan {
  display: block;
  margin-top: 16rpx;
  font-size: 26rpx;
  color: var(--c-text-sec);
  letter-spacing: 1rpx;
}

.card {
  background: var(--c-panel);
  border: 1rpx solid var(--c-border);
  border-radius: var(--radius);
  padding: 48rpx 44rpx 54rpx;
  box-shadow: 0 8rpx 24rpx rgba(35,72,130,0.08), 0 2rpx 6rpx rgba(35,72,130,0.06);
  display: flex;
  flex-direction: column;
  gap: 34rpx;
}

.card-title {
  font-size: 40rpx;
  font-weight: 600;
  color: var(--c-text);
  text-align: center;
  margin-bottom: 8rpx;
}

.field { display: flex; flex-direction: column; }

.ipt {
  width: 100%;
  font-size: 30rpx;
  padding: 0 28rpx;
  height: 92rpx;                 /* 固定高度，避免裁切 */
  line-height: 92rpx;            /* 占位与文本垂直居中 */
  background: #fff;
  border: 1rpx solid var(--c-border);
  border-radius: var(--radius-s);
  box-sizing: border-box;
  color: var(--c-text);
  transition: border-color .18s, box-shadow .18s;
}

.ipt-ph {                       /* 占位符样式（微信小程序专用） */
  color: #99acc2;
  font-size: 30rpx;
  line-height: 92rpx;
  letter-spacing: 0;
}

.ipt:focus {
  border-color: var(--c-primary);
  box-shadow: 0 0 0 4rpx var(--c-primary-light);
}

/* 按钮改浅蓝 */
.btn.primary {
  background: linear-gradient(90deg,#a9d6ff,#66b4ff);
  box-shadow: 0 6rpx 14rpx rgba(102,180,255,0.35);
  border: none;
  font-size: 32rpx;
  font-weight: 600;
}
.btn.primary:active { opacity:.88; }

.btn[disabled] { opacity:.55; }

.links {
  margin-top: 6rpx;
  text-align: center;
  font-size: 26rpx;
}

.link {
  color: var(--c-primary-dark);
  text-decoration: underline;
}

.link:active { opacity: .75; }

.footer {
  margin-top: auto;
  padding-top: 60rpx;
  text-align: center;
}

.ft-text {
  font-size: 22rpx;
  color: #99a8ba;
}
</style>