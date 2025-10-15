<template>
  <view class="reg-page">
    <!-- 顶部装饰 -->
    <view class="deco-top">
      <view class="deco-circle circle-1"></view>
      <view class="deco-circle circle-2"></view>
      <view class="deco-circle circle-3"></view>
    </view>

    <!-- 品牌区 -->
    <view class="brand-area">
      <view class="logo-wrapper">
        <text class="logo-icon">📝</text>
        <text class="logo">题练平台</text>
      </view>
      <text class="slogan">轻松高效 · 专注练题</text>
      <view class="slogan-sub">
        <text class="sub-item">✓ 智能组卷</text>
        <text class="sub-divider">·</text>
        <text class="sub-item">✓ 错题本</text>
        <text class="sub-divider">·</text>
        <text class="sub-item">✓ 知识图谱</text>
      </view>
    </view>

    <!-- 注册卡片 -->
    <view class="card">
      <view class="card-header">
        <text class="card-title">创建账号</text>
        <text class="card-subtitle">开启你的高效学习之旅</text>
      </view>

      <view class="form">
        <view class="field">
          <view class="field-label">
            <text class="label-icon">👤</text>
            <text class="label-text">账号</text>
            <text class="label-required">*</text>
          </view>
          <view class="input-wrapper">
            <input
              v-model="account"
              class="ipt"
              placeholder="请输入账号（≥3位字符）"
              placeholder-class="ipt-ph"
            />
          </view>
        </view>

        <view class="field">
          <view class="field-label">
            <text class="label-icon">🔐</text>
            <text class="label-text">密码</text>
            <text class="label-required">*</text>
          </view>
          <view class="input-wrapper">
            <input
              v-model="password"
              password
              class="ipt"
              placeholder="请输入密码（≥6位字符）"
              placeholder-class="ipt-ph"
            />
          </view>
        </view>

        <view class="field">
          <view class="field-label">
            <text class="label-icon">📧</text>
            <text class="label-text">邮箱</text>
            <text class="label-optional">选填</text>
          </view>
          <view class="input-wrapper">
            <input
              v-model="email"
              class="ipt"
              placeholder="请输入邮箱地址"
              placeholder-class="ipt-ph"
            />
          </view>
        </view>

        <view class="field">
          <view class="field-label">
            <text class="label-icon">✨</text>
            <text class="label-text">昵称</text>
            <text class="label-optional">选填</text>
          </view>
          <view class="input-wrapper">
            <input
              v-model="nickname"
              class="ipt"
              placeholder="请输入昵称"
              placeholder-class="ipt-ph"
            />
          </view>
        </view>

        <button class="btn primary" :disabled="submitting" @tap="onSubmit">
          <text class="btn-icon">{{ submitting ? '⏳' : '🚀' }}</text>
          <text>{{ submitting ? '注册中…' : '立即注册' }}</text>
        </button>

        <view class="links">
          <text class="link-text">已有账号？</text>
          <text class="link" @tap="goLogin">立即登录 →</text>
        </view>
      </view>
    </view>

    <!-- 底部 -->
    <view class="footer">
      <view class="footer-divider"></view>
      <text class="ft-text">© 2025 Quiz App · 专注在线练题</text>
      <view class="footer-links">
        <text class="footer-link">用户协议</text>
        <text class="footer-divider-dot">·</text>
        <text class="footer-link">隐私政策</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { api } from '@/utils/api'

const account = ref('')
const password = ref('')
const email = ref('')
const nickname = ref('')
const submitting = ref(false)

function toast(t:string){ uni.showToast({ icon:'none', title:t }) }

async function onSubmit() {
  const acc = account.value.trim()
  const pwd = password.value.trim()
  if(acc.length < 3) return toast('账号至少3位')
  if(pwd.length < 6) return toast('密码至少6位')
  submitting.value = true
  try {
    await api.register(acc, pwd, email.value.trim() || undefined, nickname.value.trim() || undefined)
    toast('注册成功，请登录')
    setTimeout(()=> uni.redirectTo({ url:'/pages/login/login' }), 700)
  } catch(e:any){
    toast(e?.data?.message || '注册失败')
  } finally { submitting.value = false }
}

function goLogin(){ uni.redirectTo({ url:'/pages/login/login' }) }
</script>

<style scoped>
:root, page {
  --c-bg-start: #e8f2ff;
  --c-bg-end: #f5f9ff;
  --c-panel: #ffffff;
  --c-border: #d8e6f5;
  --c-border-hover: #c6d9ec;
  --c-primary: #66b4ff;
  --c-primary-dark: #4b9ef0;
  --c-primary-light: #e6f3ff;
  --c-text: #1f2d3d;
  --c-text-sec: #5f7085;
  --c-text-muted: #8da1b5;
  --c-danger: #ff4d4f;
  --shadow-sm: 0 4rpx 12rpx rgba(35,72,130,.06);
  --shadow-md: 0 8rpx 24rpx rgba(35,72,130,.08);
  --shadow-lg: 0 16rpx 48rpx rgba(35,72,130,.12);
  --radius-lg: 24rpx;
  --radius-md: 16rpx;
  --radius-sm: 12rpx;
}

.reg-page {
  min-height: 100vh;
  padding: 60rpx 48rpx 80rpx;
  background: linear-gradient(180deg, var(--c-bg-start), var(--c-bg-end));
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* ========== 顶部装饰 ========== */
.deco-top {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 400rpx;
  pointer-events: none;
  overflow: hidden;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(102,180,255,0.15) 0%, rgba(102,180,255,0.05) 100%);
  animation: float 20s infinite ease-in-out;
}

.circle-1 {
  width: 300rpx;
  height: 300rpx;
  top: -150rpx;
  right: -100rpx;
  animation-delay: 0s;
}

.circle-2 {
  width: 200rpx;
  height: 200rpx;
  top: 80rpx;
  left: -80rpx;
  animation-delay: 3s;
}

.circle-3 {
  width: 150rpx;
  height: 150rpx;
  top: 200rpx;
  right: 60rpx;
  animation-delay: 6s;
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-30rpx) rotate(10deg); }
}

/* ========== 品牌区 ========== */
.brand-area {
  text-align: center;
  margin-bottom: 56rpx;
  position: relative;
  z-index: 1;
}

.logo-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  margin-bottom: 20rpx;
}

.logo-icon {
  font-size: 64rpx;
  line-height: 1;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12rpx); }
}

.logo {
  font-size: 56rpx;
  font-weight: 700;
  letter-spacing: 3rpx;
  background: linear-gradient(135deg, #66b4ff 0%, #4b9ef0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.2;
}

.slogan {
  display: block;
  font-size: 28rpx;
  color: var(--c-text-sec);
  letter-spacing: 2rpx;
  margin-bottom: 16rpx;
  font-weight: 500;
}

.slogan-sub {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  font-size: 22rpx;
  color: var(--c-text-muted);
}

.sub-divider {
  color: var(--c-border-hover);
}

/* ========== 注册卡片 ========== */
.card {
  background: var(--c-panel);
  border-radius: var(--radius-lg);
  padding: 0;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 8rpx;
  background: linear-gradient(90deg, #66b4ff 0%, #4b9ef0 100%);
}

.card-header {
  padding: 48rpx 40rpx 36rpx;
  text-align: center;
  background: linear-gradient(180deg, var(--c-primary-light) 0%, transparent 100%);
}

.card-title {
  font-size: 40rpx;
  font-weight: 700;
  color: var(--c-text);
  display: block;
  margin-bottom: 12rpx;
}

.card-subtitle {
  font-size: 24rpx;
  color: var(--c-text-sec);
  display: block;
}

.form {
  padding: 0 40rpx 48rpx;
  display: flex;
  flex-direction: column;
  gap: 28rpx;
}

/* ========== 表单字段 ========== */
.field {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.field-label {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding-left: 4rpx;
}

.label-icon {
  font-size: 28rpx;
  line-height: 1;
}

.label-text {
  font-size: 26rpx;
  font-weight: 600;
  color: var(--c-text);
}

.label-required {
  color: var(--c-danger);
  font-size: 24rpx;
  margin-left: 2rpx;
}

.label-optional {
  padding: 2rpx 12rpx;
  background: #f0f2f5;
  color: var(--c-text-muted);
  font-size: 20rpx;
  border-radius: 999rpx;
  margin-left: 8rpx;
}

.input-wrapper {
  position: relative;
}

.ipt {
  width: 100%;
  padding: 0 24rpx;
  height: 92rpx;
  line-height: 92rpx;
  font-size: 28rpx;
  color: var(--c-text);
  background: #f7f9fc;
  border: 2rpx solid var(--c-border);
  border-radius: var(--radius-sm);
  box-sizing: border-box;
  transition: all 0.3s;
}

.ipt-ph {
  color: var(--c-text-muted);
  font-size: 26rpx;
}

.ipt:focus {
  background: #fff;
  border-color: var(--c-primary);
  box-shadow: 0 0 0 6rpx var(--c-primary-light);
}

/* ========== 按钮 ========== */
.btn {
  width: 100%;
  padding: 28rpx 0;
  margin-top: 12rpx;
  border-radius: var(--radius-md);
  font-size: 32rpx;
  font-weight: 600;
  text-align: center;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  transition: all 0.3s;
}

.btn.primary {
  background: linear-gradient(135deg, #66b4ff 0%, #4b9ef0 100%);
  color: #fff;
  box-shadow: var(--shadow-md);
}

.btn.primary:active:not([disabled]) {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2rpx);
}

.btn[disabled] {
  opacity: 0.6;
}

.btn-icon {
  font-size: 32rpx;
  line-height: 1;
}

/* ========== 链接区 ========== */
.links {
  text-align: center;
  font-size: 26rpx;
  margin-top: 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
}

.link-text {
  color: var(--c-text-sec);
}

.link {
  color: var(--c-primary-dark);
  font-weight: 600;
  position: relative;
}

.link::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: -2rpx;
  height: 2rpx;
  background: var(--c-primary-dark);
  transform: scaleX(0);
  transition: transform 0.3s;
}

.link:active::after {
  transform: scaleX(1);
}

/* ========== 底部 ========== */
.footer {
  margin-top: auto;
  padding-top: 48rpx;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
}

.footer-divider {
  width: 120rpx;
  height: 2rpx;
  background: linear-gradient(90deg, transparent 0%, var(--c-border) 50%, transparent 100%);
  margin-bottom: 8rpx;
}

.ft-text {
  font-size: 22rpx;
  color: var(--c-text-muted);
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 12rpx;
  font-size: 20rpx;
}

.footer-link {
  color: var(--c-text-muted);
}

.footer-link:active {
  color: var(--c-primary);
}

.footer-divider-dot {
  color: var(--c-border-hover);
}

button::after {
  border: none;
}
</style>
