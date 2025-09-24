<template>
  <view class="wrap">
    <view class="search-bar">
      <input class="ipt" v-model="keyword" placeholder="搜索题干关键词" @confirm="refresh" />
      <button size="mini" @tap="refresh">搜索</button>
    </view>

    <view class="filters">
      <picker mode="selector" :range="types" @change="onType">
        <view class="picker">类型: {{ selType || '全部' }}</view>
      </picker>
      <picker mode="selector" :range="difficulties" @change="onDiff">
        <view class="picker">难度: {{ selDiffLabel }}</view>
      </picker>
      <switch :checked="activeOnly" @change="toggleActive" /> <text>仅启用</text>
    </view>

    <view v-if="items.length===0 && !loading" class="empty">暂无题目</view>

    <view v-for="q in items" :key="q.question_id" class="qitem" @tap="viewDetail(q)">
      <view class="line">
        <text class="qid">{{ q.question_id }}</text>
        <text class="meta">{{ q.type }} | {{ q.difficulty ?? '-' }}</text>
      </view>
      <view class="stem">{{ q.stem }}</view>
      <view class="status">
        <text :class="['tag', q.audit_status.toLowerCase()]">{{ q.audit_status }}</text>
        <text class="time">{{ q.updated_at.replace('T',' ').split('.')[0] }}</text>
      </view>
    </view>

    <button v-if="hasMore" class="more" :disabled="loading" @tap="loadMore">
      {{ loading ? '加载中...' : '加载更多' }}
    </button>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api, type MyQuestionItem } from '@/utils/api'

const items = ref<MyQuestionItem[]>([])
const page = ref(1)
const size = ref(10)
const total = ref(0)
const loading = ref(false)

const keyword = ref('')
const selType = ref<string | ''>('')
const selDiff = ref<number | null>(null)
const activeOnly = ref(false)

const types = ['SC','MC','TF','FILL','ESSAY']
const difficulties = ['全部','1','2','3','4','5']
const selDiffLabel = computed(() => selDiff.value == null ? '全部' : selDiff.value)

const hasMore = computed(() => items.value.length < total.value)

async function fetch(p=1, append=false) {
  loading.value = true
  try {
    const resp = await api.getMyQuestions({
      page: p,
      size: size.value,
      keyword: keyword.value || undefined,
      qtype: selType.value || undefined,
      difficulty: selDiff.value == null ? undefined : selDiff.value,
      active_only: activeOnly.value
    })
    total.value = resp.total
    if (!append) items.value = resp.items
    else items.value = items.value.concat(resp.items)
    page.value = resp.page
  } catch (e:any) {
    uni.showToast({ icon:'none', title: e?.data?.message || '加载失败' })
  } finally {
    loading.value = false
  }
}

function refresh(){ fetch(1,false) }
function loadMore(){ if(!loading.value && hasMore.value) fetch(page.value+1,true) }
function onType(e:any){ const idx = e.detail.value; selType.value = types[idx]; refresh() }
function onDiff(e:any){
  const idx = e.detail.value
  selDiff.value = idx===0 ? null : Number(difficulties[idx])
  refresh()
}
function toggleActive(e:any){ activeOnly.value = !!e.detail.value; refresh() }
function viewDetail(q: MyQuestionItem){
  uni.showToast({ icon:'none', title:`题目ID ${q.question_id}` })
  // TODO: 跳转详情 /pages/question-detail/question-detail?qid=...
}

onMounted(()=>{
  if(!uni.getStorageSync('token')) return uni.reLaunch({ url:'/pages/login/login' })
  fetch(1)
})
</script>

<style scoped>
.wrap { padding:24rpx; }
.search-bar { display:flex; gap:12rpx; margin-bottom:20rpx; }
.ipt { flex:1; background:#fff; padding:12rpx 16rpx; border-radius:8rpx; }
.filters { display:flex; flex-wrap:wrap; gap:20rpx; font-size:24rpx; margin-bottom:16rpx; align-items:center; }
.picker { padding:6rpx 16rpx; background:#fff; border-radius:20rpx; box-shadow:0 2rpx 6rpx rgba(0,0,0,0.06); }
.empty { text-align:center; color:#888; padding:60rpx 0; }
.qitem { background:#fff; padding:20rpx; border-radius:16rpx; margin-bottom:16rpx; box-shadow:0 4rpx 10rpx rgba(0,0,0,0.04); }
.line { display:flex; justify-content:space-between; font-weight:600; margin-bottom:8rpx; }
.qid { color:#1677ff; }
.meta { color:#555; font-size:24rpx; }
.stem { color:#222; font-size:28rpx; line-height:1.5; max-height:3.2em; overflow:hidden; }
.status { display:flex; justify-content:space-between; margin-top:12rpx; font-size:22rpx; align-items:center;}
.tag { padding:4rpx 12rpx; border-radius:12rpx; background:#f5f5f5; }
.tag.pending { background:#fffbe6; color:#ad8b00; }
.tag.approved { background:#e6fffb; color:#08979c; }
.tag.rejected { background:#fff1f0; color:#cf1322; }
.time { color:#999; }
.more { width:100%; background:#1677ff; color:#fff; margin-top:12rpx; }
</style>
