<template>
  <view class="eb-page">
    <!-- 筛选卡片 -->
    <view class="card toolbar-card">
      <view class="toggle">
        <switch :checked="onlyDue" @change="toggleDue" color="#66b4ff" />
        <text class="toggle-label">只看到期复习</text>
      </view>
    </view>

    <!-- 列表 -->
    <view class="list">
      <view v-if="!loading && items.length===0" class="empty">暂无错题</view>

      <view
        v-for="it in items"
        :key="it.id"
        class="q-item"
        @tap="viewQuestion(it)"
      >
        <view class="top">
          <text class="qid">Q{{ it.question_id }}</text>
          <text class="cnt" :class="countLevel(it.wrong_count)">错 {{ it.wrong_count }} 次</text>
        </view>
        <view class="meta-row">
          <text class="meta-label">最近：</text>
          <text class="meta-val">{{ fmt(it.last_wrong_time) || '—' }}</text>
          <text class="sep"></text>
          <text class="meta-label">复习：</text>
          <text class="meta-val">{{ fmt(it.next_review_time) || '—' }}</text>
        </view>
      </view>

      <button
        v-if="hasMore"
        class="load-btn"
        :disabled="loading"
        @tap="loadMore"
      >{{ loading ? '加载中…' : '加载更多' }}</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { api, type ErrorBookItem } from '@/utils/api'

type Item = ErrorBookItem

const items = ref<Item[]>([])
const page = ref(1)
const size = ref(10)
const total = ref(0)
const loading = ref(false)
const onlyDue = ref(false)

function fmt(s?: string) {
  return s ? s.replace('T',' ').split('.')[0] : ''
}

async function fetchPage(p=1) {
  loading.value = true
  try {
    const data = await api.getMyErrorBook(p, size.value, onlyDue.value, false)
    if(p===1) items.value = data.items || []
    else items.value = items.value.concat(data.items || [])
    total.value = data.total || 0
    page.value = data.page || p
  } catch(e:any){
    uni.showToast({ icon:'none', title: e?.data?.message || '加载失败' })
  } finally { loading.value=false }
}

const hasMore = computed(()=> items.value.length < total.value)
function loadMore(){ if(!loading.value && hasMore.value) fetchPage(page.value+1) }
function toggleDue(e:any){ onlyDue.value = !!e.detail.value; fetchPage(1) }
function viewQuestion(it:Item){
  uni.showToast({ icon:'none', title:`题目 ${it.question_id}` })
  // 可跳转详情页
  // uni.navigateTo({ url:'/pages/question-detail/question-detail?id='+it.question_id })
}

function countLevel(n:number){
  if(n>=5) return 'high'
  if(n>=3) return 'mid'
  return 'low'
}

onMounted(()=>{
  if(!uni.getStorageSync('token')) return uni.reLaunch({ url:'/pages/login/login' })
  fetchPage(1)
})
</script>

<style scoped>
:root, page, .eb-page {
  --c-bg-grad-top:#e8f2ff;
  --c-bg-grad-bottom:#f5f9ff;
  --c-panel:#ffffff;
  --c-border:#d8e6f5;
  --c-border-strong:#c6d9ec;
  --c-primary:#66b4ff;
  --c-primary-dark:#4b9ef0;
  --c-primary-light:#d4ecff;
  --c-text:#1f2d3d;
  --c-text-sec:#5f7085;
  --c-danger:#ff4d4f;
  --c-warn:#ffb020;
  --c-green:#38b26f;
  --radius:20rpx;
  --radius-s:14rpx;
}

.eb-page{
  min-height:100vh;
  padding:24rpx 28rpx 140rpx;
  box-sizing:border-box;
  background:linear-gradient(180deg,var(--c-bg-grad-top),var(--c-bg-grad-bottom));
  display:flex;
  flex-direction:column;
}

.card{
  background:var(--c-panel);
  border:1rpx solid var(--c-border);
  border-radius:var(--radius);
  box-shadow:0 8rpx 24rpx rgba(35,72,130,0.08),0 2rpx 6rpx rgba(35,72,130,0.06);
}

.toolbar-card{
  padding:30rpx 34rpx;
  margin-bottom:34rpx;
}

.toggle{
  display:flex;
  align-items:center;
  gap:18rpx;
}
.toggle-label{
  font-size:26rpx;
  color:var(--c-text-sec);
}

.list{
  display:flex;
  flex-direction:column;
  gap:26rpx;
}

.q-item{
  background:#fff;
  border:1rpx solid var(--c-border);
  border-radius:var(--radius-s);
  padding:26rpx 30rpx 30rpx;
  box-shadow:0 4rpx 12rpx rgba(35,72,130,0.06);
  display:flex;
  flex-direction:column;
  gap:12rpx;
  transition:background .15s,border-color .15s;
}
.q-item:active{ opacity:.88; }
.top{
  display:flex;
  justify-content:space-between;
  align-items:center;
  font-size:28rpx;
  font-weight:600;
}
.qid{ color:var(--c-primary-dark); }
.cnt{ font-size:26rpx; font-weight:600; }
.cnt.low{ color:var(--c-primary-dark); }
.cnt.mid{ color:var(--c-warn); }
.cnt.high{ color:var(--c-danger); }

.meta-row{
  display:flex;
  flex-wrap:wrap;
  gap:6rpx;
  font-size:24rpx;
  line-height:1.5;
}
.meta-label{ color:var(--c-text-sec); }
.meta-val{ color:var(--c-text); }
.sep{ width:24rpx; }

.empty{
  text-align:center;
  color:var(--c-text-sec);
  padding:160rpx 0 40rpx;
  font-size:30rpx;
}

.load-btn{
  margin-top:8rpx;
  background:linear-gradient(90deg,#a9d6ff,#66b4ff);
  color:#fff;
  font-size:30rpx;
  font-weight:600;
  border:none;
  border-radius:var(--radius-s);
  padding:28rpx 0;
  box-shadow:0 6rpx 14rpx rgba(102,180,255,.35);
}
.load-btn:active{ opacity:.85; }
.load-btn[disabled]{ opacity:.55; }

@media (min-width:700rpx){
  .toolbar-card,.q-item,.load-btn{ max-width:900rpx; margin-left:auto; margin-right:auto; }
}
</style>