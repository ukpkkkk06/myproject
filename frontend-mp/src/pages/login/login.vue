<template>
  <view class="wrap">
    <input class="ipt" v-model="account" placeholder="账号" />
    <input class="ipt" v-model="password" password placeholder="密码" />
    <button :disabled="loading" @tap="onLogin">{{ loading ? '登录中…' : '登录' }}</button>
    <button class="link" @tap="goRegister">没有账号？去注册</button>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/utils/api'

const account = ref('')
const password = ref('')
const loading = ref(false)

function toast(t: string) { uni.showToast({ icon: 'none', title: t }) }

async function onLogin() {
  const acc = account.value.trim()
  const pwd = password.value.trim()
  if (!acc || !pwd) return toast('请输入账号和密码')
  loading.value = true
  try {
    uni.removeStorageSync('token') // 避免使用到旧 token
    const token = await api.login(acc, pwd)
    uni.setStorageSync('token', token.access_token)
    const me = await api.me()
    uni.showToast({ icon: 'none', title: me.is_admin ? '欢迎管理员' : '欢迎' })
    uni.reLaunch({ url: me.is_admin ? '/pages/index/index' : '/pages/lobby/lobby' })
  } catch (e: any) {
    toast(e?.data?.message || '登录失败')
  } finally {
    loading.value = false
  }
}

function goRegister() {
  uni.redirectTo({ url: '/pages/register/register' })
}

onMounted(async () => {
  const token = uni.getStorageSync('token')
  if (!token) return
  try {
    const me = await api.me()
    uni.reLaunch({ url: me.is_admin ? '/pages/index/index' : '/pages/lobby/lobby' })
  } catch {
    // token 失效则停留在登录页
    uni.removeStorageSync('token')
  }
})
</script>

<style scoped>
.wrap{padding:32rpx}.ipt{border:1px solid #ddd;padding:16rpx;border-radius:8rpx;margin-bottom:16rpx}
</style>