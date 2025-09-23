<template>
  <view class="wrap">
    <view class="toolbar">
      <switch :checked="onlyDue" @change="toggleDue" /> <text>只看到期复习</text>
    </view>

    <view v-if="items.length === 0" class="empty">暂无错题</view>

    <view v-for="it in items" :key="it.id" class="item" @tap="viewQuestion(it)">
      <view class="line">
        <text class="qid">Q{{ it.question_id }}</text>
        <text class="cnt">错 {{ it.wrong_count }} 次</text>
      </view>
      <view class="sub">
        <text>最近：{{ fmt(it.last_wrong_time) || '—' }}</text>
        <text>复习：{{ fmt(it.next_review_time) || '—' }}</text>
      </view>
    </view>

    <button v-if="hasMore" class="btn" @tap="loadMore" :disabled="loading">
      {{ loading ? '加载中…' : '加载更多' }}
    </button>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { api, type ErrorBookItem, type ErrorBookListResp } from '@/utils/api'

type Item = ErrorBookItem
type Resp = ErrorBookListResp

const items = ref<Item[]>([])
const page = ref(1)
const size = ref(10)
const total = ref(0)
const loading = ref(false)
const onlyDue = ref(false)

function fmt(s?: string) {
  if (!s) return ''
  return s.replace('T', ' ').split('.')[0]
}

async function fetchPage(p = 1) {
  loading.value = true
  try {
    const data = await api.getMyErrorBook(p, size.value, onlyDue.value, false)
    if (p === 1) items.value = data.items || []
    else items.value = items.value.concat(data.items || [])
    total.value = data.total || 0
    page.value = data.page || p
  } catch (e: any) {
    uni.showToast({ icon: 'none', title: e?.data?.message || '加载失败' })
  } finally {
    loading.value = false
  }
}

const hasMore = computed(() => items.value.length < total.value)
function loadMore() { if (!loading.value && hasMore.value) fetchPage(page.value + 1) }
function toggleDue(e: any) { onlyDue.value = !!e.detail.value; fetchPage(1) }
function viewQuestion(it: Item) { uni.showToast({ icon: 'none', title: `题目 ${it.question_id}` }) }

onMounted(() => {
  const token = uni.getStorageSync('token')
  if (!token) return uni.reLaunch({ url: '/pages/login/login' })
  fetchPage(1)
})
</script>

<style scoped>
.wrap { padding: 24rpx; }
.toolbar { display: flex; align-items: center; gap: 12rpx; margin-bottom: 16rpx; }
.empty { color: #888; padding: 40rpx 0; text-align: center; }
.item { padding: 16rpx; border-radius: 12rpx; background: #fff; margin-bottom: 12rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); }
.line { display: flex; justify-content: space-between; font-weight: 600; }
.qid { color: #1677ff; }
.cnt { color: #fa541c; }
.sub { display: flex; justify-content: space-between; color: #666; margin-top: 6rpx; font-size: 24rpx; }
.btn { width: 100%; margin-top: 12rpx; background: #1677ff; color: #fff; }
</style>