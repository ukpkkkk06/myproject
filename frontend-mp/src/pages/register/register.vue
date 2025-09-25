<template>
  <view class="reg-page">
    <view class="brand-area">
      <text class="logo">题练平台</text>
      <text class="slogan">轻松高效 · 专注练题</text>
    </view>

    <view class="card">
      <view class="card-title">创建账号</view>

      <view class="field">
        <input
          v-model="account"
          class="ipt"
          placeholder="账号（≥3 位）"
          placeholder-class="ipt-ph"
        />
      </view>

      <view class="field">
        <input
          v-model="password"
          password
          class="ipt"
          placeholder="密码（≥6 位）"
          placeholder-class="ipt-ph"
        />
      </view>

      <view class="field">
        <input
          v-model="email"
          class="ipt"
          placeholder="邮箱（可选）"
          placeholder-class="ipt-ph"
        />
      </view>

      <view class="field">
        <input
          v-model="nickname"
          class="ipt"
          placeholder="昵称（可选）"
          placeholder-class="ipt-ph"
        />
      </view>

      <button class="btn primary" :disabled="submitting" @tap="onSubmit">
        {{ submitting ? '提交中…' : '注册' }}
      </button>

      <view class="links">
        <text class="link" @tap="goLogin">已有账号？去登录</text>
      </view>
    </view>

    <view class="footer">
      <text class="ft-text">© 2025 Quiz App</text>
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
  --radius: 20rpx;
  --radius-s: 12rpx;
}

.reg-page {
  min-height:100vh;
  padding:80rpx 56rpx 60rpx;
  background:linear-gradient(180deg,var(--c-bg-grad-top),var(--c-bg-grad-bottom));
  display:flex;
  flex-direction:column;
}

.brand-area {
  text-align:center;
  margin-bottom:60rpx;
  user-select:none;
  display:flex;
  flex-direction:column;
  align-items:center;
}

.logo {
  font-size:56rpx;
  font-weight:700;
  letter-spacing:2rpx;
  color:var(--c-primary-dark);
  text-shadow:0 4rpx 8rpx rgba(75,158,240,0.18);
  display:block;
  line-height:1.15;
}

.slogan {
  display:block;
  margin-top:16rpx;
  font-size:26rpx;
  color:var(--c-text-sec);
  letter-spacing:1rpx;
  line-height:1.3;
}

.card {
  background:var(--c-panel);
  border:1rpx solid var(--c-border);
  border-radius:var(--radius);
  padding:48rpx 44rpx 54rpx;
  box-shadow:0 8rpx 24rpx rgba(35,72,130,0.08),0 2rpx 6rpx rgba(35,72,130,0.06);
  display:flex;
  flex-direction:column;
  gap:34rpx;
}

.card-title {
  font-size:40rpx;
  font-weight:600;
  color:var(--c-text);
  text-align:center;
  margin-bottom:4rpx;
}

.field { display:flex; flex-direction:column; }

.ipt {
  width:100%;
  font-size:30rpx;
  padding:0 28rpx;
  height:92rpx;
  line-height:92rpx;
  background:#fff;
  border:1rpx solid var(--c-border);
  border-radius:var(--radius-s);
  box-sizing:border-box;
  color:var(--c-text);
  transition:border-color .18s, box-shadow .18s;
}

.ipt-ph {
  color:#99acc2;
  font-size:30rpx;
  line-height:92rpx;
}

.ipt:focus {
  border-color:var(--c-primary);
  box-shadow:0 0 0 4rpx var(--c-primary-light);
}

.btn {
  width:100%;
  padding:26rpx 0;
  border-radius:var(--radius-s);
  font-size:32rpx;
  font-weight:600;
  text-align:center;
  border:none;
  background:#ccc;
  color:#fff;
  letter-spacing:1rpx;
}
.btn.primary {
  background:linear-gradient(90deg,#a9d6ff,#66b4ff);
  box-shadow:0 6rpx 14rpx rgba(102,180,255,0.35);
}
.btn.primary:active { opacity:.88; }
.btn[disabled] { opacity:.55; }

.links {
  text-align:center;
  font-size:26rpx;
  margin-top:2rpx;
}
.link { color:var(--c-primary-dark); text-decoration:underline; }
.link:active { opacity:.75; }

.footer {
  margin-top:auto;
  padding-top:60rpx;
  text-align:center;
}
.ft-text { font-size:22rpx; color:#99a8ba; }
</style>
