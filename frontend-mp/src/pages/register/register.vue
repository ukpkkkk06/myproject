<template>
  <view class="container">
    <view class="title">注册</view>
    <view class="form">
      <input class="input" placeholder="账号" v-model="account" />
      <input class="input" placeholder="密码" password v-model="password" />
      <input class="input" placeholder="邮箱（可选）" v-model="email" />
      <input class="input" placeholder="昵称（可选）" v-model="nickname" />
      <button class="btn" :disabled="submitting" @tap="onSubmit">注册</button>
      <button class="link" @tap="goLogin">已有账号？去登录</button>
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

function toast(title: string) {
  uni.showToast({ title, icon: 'none', duration: 2000 })
}

async function onSubmit() {
  const acc = account.value.trim()
  const pwd = password.value.trim()
  if (!acc) return toast('账号不能为空')
  if (!pwd) return toast('密码不能为空')

  submitting.value = true
  try {
    await api.register(acc, pwd, email.value || undefined, nickname.value || undefined)
    toast('注册成功，请登录')
    setTimeout(() => {
      uni.redirectTo({ url: '/pages/login/login' })
    }, 800)
  } catch (e: any) {
    // 统一展示后端全局异常处理器返回的 message
    const msg = e?.data?.message || '注册失败'
    toast(msg)
  } finally {
    submitting.value = false
  }
}

function goLogin() {
  uni.redirectTo({ url: '/pages/login/login' })
}
</script>

<style scoped>
.container { padding: 24rpx; }
.title { font-size: 36rpx; font-weight: 600; margin-bottom: 24rpx; }
.form { display: flex; flex-direction: column; gap: 16rpx; }
.input { padding: 20rpx; border: 1px solid #ddd; border-radius: 8rpx; }
.btn { background: #07c160; color: #fff; padding: 20rpx; border-radius: 8rpx; }
.link { background: transparent; color: #1677ff; }
</style>
