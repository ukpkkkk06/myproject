<template>
  <view class="wrap">
    <input class="ipt" v-model="account" placeholder="账号" />
    <input class="ipt" v-model="password" password placeholder="密码" />
    <button :disabled="loading" @tap="onLogin">{{ loading ? '登录中…' : '登录' }}</button>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { api } from '@/utils/api'
const account = ref('alice')
const password = ref('123456')
const loading = ref(false)
async function onLogin() {
  if (loading.value) return
  loading.value = true
  try {
    const t = await api.login(account.value, password.value)
    uni.setStorageSync('token', t.access_token)
    uni.reLaunch({ url: '/pages/index/index' })
  } catch {
    uni.showToast({ title: '账号或密码错误', icon: 'none' })
  } finally { loading.value = false }
}
</script>

<style scoped>
.wrap{padding:32rpx}.ipt{border:1px solid #ddd;padding:16rpx;border-radius:8rpx;margin-bottom:16rpx}
</style>