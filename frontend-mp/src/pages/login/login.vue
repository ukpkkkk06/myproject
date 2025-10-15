<template>
  <view class="login-page">
    <!-- 装饰性背景元素 -->
    <view class="bg-deco">
      <view class="circle circle-1"></view>
      <view class="circle circle-2"></view>
      <view class="circle circle-3"></view>
    </view>

    <!-- 品牌区域优化 -->
    <view class="brand-area">
      <view class="logo-wrap">
        <text class="logo-icon">📚</text>
        <text class="logo">题练平台</text>
      </view>
      <text class="slogan">轻松高效 · 专注练题</text>
      <view class="slogan-badge">智能学习助手</view>
    </view>

    <!-- 登录卡片 -->
    <view class="card">
      <view class="card-header">
        <text class="card-icon">🔐</text>
        <text class="card-title">登录账户</text>
      </view>

      <!-- 账号输入 -->
      <view class="field" :class="{ focused: focus === 'account' }">
        <view class="field-header">
          <text class="field-icon">👤</text>
          <text class="field-label">账号</text>
        </view>
        <input
          v-model="account"
          class="ipt"
          placeholder="请输入账号"
          placeholder-class="ipt-ph"
          @focus="focus='account'"
          @blur="focus=''"
        />
      </view>

      <!-- 密码输入 -->
      <view class="field" :class="{ focused: focus === 'password' }">
        <view class="field-header">
          <text class="field-icon">🔒</text>
          <text class="field-label">密码</text>
        </view>
        <input
          v-model="password"
          password
          class="ipt"
          placeholder="请输入密码"
          placeholder-class="ipt-ph"
          @focus="focus='password'"
          @blur="focus=''"
        />
      </view>

      <!-- 登录按钮 -->
      <button class="btn primary" :disabled="loading" @tap="onLogin">
        <text class="btn-icon" v-if="!loading">✓</text>
        <text>{{ loading ? '登录中…' : '立即登录' }}</text>
      </button>

      <!-- 链接区域 -->
      <view class="links">
        <view class="link-item" @tap="goRegister">
          <text class="link-icon">✨</text>
          <text class="link-text">没有账号？立即注册</text>
        </view>
      </view>
    </view>

    <!-- 底部信息 -->
    <view class="footer">
      <view class="footer-divider">
        <view class="divider-line"></view>
        <text class="divider-text">安全登录</text>
        <view class="divider-line"></view>
      </view>
      <text class="ft-text">© 2025 Quiz App · 智能题库系统</text>
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
:root, page {
  --c-bg: #f5f9ff;
  --c-bg-grad-top: #e8f2ff;
  --c-bg-grad-bottom: #f5f9ff;
  --c-panel: #ffffff;
  --c-border: #d8e6f5;
  --c-primary: #66b4ff;
  --c-primary-dark: #4b9ef0;
  --c-primary-light: #d4ecff;
  --c-text: #1f2d3d;
  --c-text-sec: #5f7085;
  --radius: 24rpx;
  --radius-s: 16rpx;
  --shadow-sm: 0 4rpx 12rpx rgba(35,72,130,.06);
  --shadow-md: 0 8rpx 24rpx rgba(35,72,130,.08), 0 2rpx 6rpx rgba(35,72,130,.06);
  --shadow-lg: 0 12rpx 36rpx rgba(35,72,130,.12);
}

.login-page {
  min-height: 100vh;
  padding: 120rpx 48rpx 80rpx;
  box-sizing: border-box;
  background: linear-gradient(180deg, var(--c-bg-grad-top), var(--c-bg-grad-bottom));
  display: flex;
  flex-direction: column;
  align-items: stretch;
  position: relative;
  overflow: hidden;
}

/* 🎨 装饰性背景圆圈 */
.bg-deco {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(102,180,255,.15), rgba(102,180,255,0));
  animation: float 20s ease-in-out infinite;
}

.circle-1 {
  width: 400rpx; height: 400rpx;
  top: -100rpx; right: -100rpx;
  animation-delay: 0s;
}

.circle-2 {
  width: 300rpx; height: 300rpx;
  bottom: 100rpx; left: -80rpx;
  animation-delay: 5s;
}

.circle-3 {
  width: 200rpx; height: 200rpx;
  top: 40%; left: 60%;
  animation-delay: 10s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); opacity: .3; }
  50% { transform: translate(30rpx, -30rpx) scale(1.1); opacity: .5; }
}

/* 🎨 品牌区域优化 */
.brand-area {
  text-align: center;
  margin-bottom: 80rpx;
  user-select: none;
  position: relative;
  z-index: 1;
  animation: fadeInDown 0.8s ease;
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-30rpx); }
  to { opacity: 1; transform: translateY(0); }
}

.logo-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  margin-bottom: 20rpx;
}

.logo-icon {
  font-size: 64rpx;
  line-height: 1;
  filter: drop-shadow(0 4rpx 12rpx rgba(102,180,255,.3));
}

.logo {
  font-size: 56rpx;
  font-weight: 700;
  letter-spacing: 2rpx;
  color: var(--c-primary-dark);
  text-shadow: 0 4rpx 8rpx rgba(58,131,247,0.18);
  background: linear-gradient(135deg, #66b4ff, #4b9ef0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.slogan {
  display: block;
  margin-top: 12rpx;
  font-size: 26rpx;
  color: var(--c-text-sec);
  letter-spacing: 1rpx;
  font-weight: 500;
}

.slogan-badge {
  display: inline-block;
  margin-top: 20rpx;
  padding: 8rpx 24rpx;
  background: linear-gradient(135deg, var(--c-primary-light), #e8f5ff);
  color: var(--c-primary-dark);
  font-size: 22rpx;
  font-weight: 600;
  border-radius: 30rpx;
  border: 1rpx solid var(--c-primary);
  box-shadow: var(--shadow-sm);
}

/* 🎨 登录卡片优化 */
.card {
  background: var(--c-panel);
  border: 1rpx solid var(--c-border);
  border-radius: var(--radius);
  padding: 48rpx 44rpx 54rpx;
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
  gap: 32rpx;
  position: relative;
  z-index: 1;
  animation: fadeInUp 0.8s ease 0.2s backwards;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30rpx); }
  to { opacity: 1; transform: translateY(0); }
}

/* 🎨 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  padding-bottom: 24rpx;
  border-bottom: 2rpx dashed var(--c-border);
}

.card-icon {
  font-size: 44rpx;
  line-height: 1;
}

.card-title {
  font-size: 36rpx;
  font-weight: 700;
  color: var(--c-text);
  letter-spacing: 1rpx;
}

/* 🎨 输入字段优化 */
.field {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  transition: all 0.3s ease;
}

.field.focused {
  transform: translateY(-2rpx);
}

.field-header {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding-left: 4rpx;
}

.field-icon {
  font-size: 28rpx;
  line-height: 1;
}

.field-label {
  font-size: 26rpx;
  color: var(--c-text-sec);
  font-weight: 600;
}

.ipt {
  width: 100%;
  font-size: 30rpx;
  padding: 0 28rpx;
  height: 92rpx;
  line-height: 92rpx;
  background: #fff;
  border: 2rpx solid var(--c-border);
  border-radius: var(--radius-s);
  box-sizing: border-box;
  color: var(--c-text);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.ipt-ph {
  color: #99acc2;
  font-size: 28rpx;
}

.ipt:focus {
  border-color: var(--c-primary);
  box-shadow: 0 0 0 6rpx var(--c-primary-light);
  background: #fafcff;
  transform: translateY(-2rpx);
}

/* 🎨 按钮优化 */
.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  width: 100%;
  height: 96rpx;
  border: none;
  border-radius: var(--radius-s);
  font-size: 32rpx;
  font-weight: 700;
  letter-spacing: 2rpx;
  color: #fff;
  background: #ccc;
  box-shadow: var(--shadow-md);
  margin-top: 12rpx;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(135deg, rgba(255,255,255,.2), transparent);
  opacity: 0;
  transition: opacity 0.25s ease;
}

.btn:active::before {
  opacity: 1;
}

.btn-icon {
  font-size: 36rpx;
  line-height: 1;
}

.btn.primary {
  background: linear-gradient(135deg, #a9d6ff, #66b4ff, #4b9ef0);
  box-shadow: 0 8rpx 20rpx rgba(102,180,255,.4), var(--shadow-md);
}

.btn:active {
  opacity: 0.9;
  transform: translateY(2rpx) scale(0.98);
}

.btn[disabled] {
  opacity: 0.5;
  transform: none;
}

button::after { border: none; }

/* 🎨 链接区域优化 */
.links {
  margin-top: 8rpx;
  display: flex;
  justify-content: center;
}

.link-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 16rpx 32rpx;
  background: linear-gradient(135deg, var(--c-primary-light), #e8f5ff);
  border-radius: 30rpx;
  border: 1rpx solid var(--c-primary);
  box-shadow: var(--shadow-sm);
  transition: all 0.25s ease;
}

.link-item:active {
  transform: scale(0.96);
  box-shadow: var(--shadow-md);
}

.link-icon {
  font-size: 28rpx;
  line-height: 1;
}

.link-text {
  font-size: 26rpx;
  color: var(--c-primary-dark);
  font-weight: 600;
}

/* 🎨 底部优化 */
.footer {
  margin-top: auto;
  padding-top: 80rpx;
  text-align: center;
  position: relative;
  z-index: 1;
  animation: fadeIn 0.8s ease 0.4s backwards;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.footer-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20rpx;
  margin-bottom: 24rpx;
}

.divider-line {
  flex: 1;
  max-width: 120rpx;
  height: 2rpx;
  background: linear-gradient(90deg, transparent, var(--c-border), transparent);
}

.divider-text {
  font-size: 22rpx;
  color: var(--c-text-sec);
  opacity: 0.6;
  font-weight: 500;
}

.ft-text {
  font-size: 22rpx;
  color: #99a8ba;
  font-weight: 500;
}

/* 响应式 */
@media (min-width: 750rpx) {
  .card {
    max-width: 640rpx;
    margin: 0 auto;
  }
}
</style>