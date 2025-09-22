<template>
  <view class="container">
    <view class="title">后端健康状态</view>
    <text>{{ JSON.stringify(health) }}</text>

    <view class="title">筛选</view>
    <view class="row">
      <input class="ipt" placeholder="账号关键词" v-model="account" />
      <input class="ipt" placeholder="邮箱关键词" v-model="email" />
      <button size="mini" @tap="onSearch">搜索</button>
    </view>

    <view style="padding:16rpx">
      <view style="font-weight:600;margin-bottom:12rpx">用户列表（共 {{ total }} 条）</view>
      <view v-for="u in items" :key="u.id" style="padding:12rpx 0;border-bottom:1px dashed #eee">
        <text>{{ u.account }}：{{ u.role || '—' }}  状态：{{ (u.status || '').toLowerCase() }}</text>
      </view>
    </view>

    <view class="footer">
      <button :disabled="loading || finished" @tap="onLoadMore">
        {{ finished ? '没有更多了' : (loading ? '加载中…' : '加载更多') }}
      </button>
    </view>

    <button size="mini" @tap="logout">退出登录</button>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api, type UserSimple } from '@/utils/api'

const health = ref<any>(null)   // 新增：定义 health

const items = ref<UserSimple[]>([])
const total = ref(0)

const account = ref('')
const email = ref('')
const skip = ref(0)
const limit = ref(10)
const loading = ref(false)
const finished = ref(false)

async function load(reset = false) {
  if (loading.value) return
  loading.value = true
  try {
    if (reset) {
      skip.value = 0
      finished.value = false
      items.value = []
    }
    const page = await api.usersSimple(skip.value, limit.value, account.value, email.value)
    total.value = page.total ?? 0
    items.value = items.value.concat(page.items ?? [])
    skip.value += page.items?.length ?? 0
    if ((items.value.length >= total.value) || (page.items?.length ?? 0) < limit.value) {
      finished.value = true
    }
  } finally {
    loading.value = false
  }
}

function onSearch() { load(true) }
function onLoadMore() { if (!finished.value) load(false) }

async function guard() {
  try {
    const me = await api.me()
    if (!me.is_admin) {
      uni.showToast({ icon: 'none', title: '无权访问后台' })
      setTimeout(() => uni.reLaunch({ url: '/pages/lobby/lobby' }), 500)
      return false
    }
    return true
  } catch {
    uni.reLaunch({ url: '/pages/login/login' })
    return false
  }
}

const ensureLogin = () => {
  const token = uni.getStorageSync('token')
  if (!token) { uni.reLaunch({ url: '/pages/login/login' }); return false }
  return true
}
function logout() { uni.removeStorageSync('token'); uni.reLaunch({ url: '/pages/login/login' }) }

onMounted(async () => {
  if (!ensureLogin()) return            // 新增：先检查是否已登录（有 token）
  const ok = await guard()
  if (!ok) return
  health.value = await api.health()     // 新增：真正拉取健康状态
  await load(true)
})
</script>

<style scoped>
.container { padding: 24rpx; }
.title { margin: 24rpx 0 12rpx; font-weight: bold; }
.row { display: flex; gap: 12rpx; align-items: center; }
.ipt { flex: 1; border: 1px solid #ddd; padding: 8rpx 12rpx; border-radius: 6rpx; }
.footer { margin-top: 24rpx; }
</style>
