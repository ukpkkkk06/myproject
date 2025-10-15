<template>
  <view class="eb-page">
    <!-- 顶部导航 -->
    <view class="top-nav">
      <view class="nav-content">
        <text class="nav-icon">📖</text>
        <text class="nav-title">错题本</text>
        <view class="nav-badge">{{ total }}</view>
      </view>
    </view>

    <view class="content-wrapper">
      <!-- 筛选卡片 -->
      <view class="card toolbar-card">
        <view class="filter-header">
          <text class="filter-icon">🎯</text>
          <text class="filter-title">筛选条件</text>
        </view>
        <view class="toggle-group">
          <view class="toggle-item">
            <view class="toggle-label-wrap">
              <text class="toggle-icon">⏰</text>
              <text class="toggle-label">只看到期复习</text>
            </view>
            <switch :checked="onlyDue" @change="toggleDue" color="#66b4ff" />
          </view>
        </view>
      </view>

      <!-- 统计卡片 -->
      <view class="stats-bar">
        <view class="stat-card">
          <text class="stat-icon">📝</text>
          <view class="stat-content">
            <text class="stat-label">错题总数</text>
            <text class="stat-value">{{ total }}</text>
          </view>
        </view>
        <view class="stat-card">
          <text class="stat-icon">⏳</text>
          <view class="stat-content">
            <text class="stat-label">待复习</text>
            <text class="stat-value highlight">{{ onlyDue ? items.length : '—' }}</text>
          </view>
        </view>
      </view>

      <!-- 题目列表 -->
      <view class="list-section">
        <view v-if="!loading && items.length===0" class="empty-state">
          <text class="empty-icon">🎉</text>
          <text class="empty-title">暂无错题</text>
          <text class="empty-hint">{{ onlyDue ? '当前无待复习题目' : '继续加油，保持好状态！' }}</text>
        </view>

        <view class="question-list">
          <view
            v-for="it in items"
            :key="it.id"
            class="question-card"
            @tap="viewQuestion(it)"
          >
            <!-- 左侧彩条 -->
            <view class="card-stripe" :class="'stripe-' + countLevel(it.wrong_count)"></view>

            <!-- 卡片头部 -->
            <view class="card-header">
              <view class="qid-badge">
                <text class="badge-icon">#</text>
                <text class="badge-text">{{ it.question_id }}</text>
              </view>
              <view class="error-badge" :class="'level-' + countLevel(it.wrong_count)">
                <text class="error-icon">❌</text>
                <text class="error-text">{{ it.wrong_count }}次</text>
              </view>
            </view>

            <!-- 题干 -->
            <view class="card-body">
              <text class="stem-text">{{ stemOf(it) }}</text>
            </view>

            <!-- 时间信息 -->
            <view class="card-footer">
              <view class="time-item">
                <text class="time-icon">📅</text>
                <text class="time-label">最近错误</text>
                <text class="time-value">{{ fmtDate(it.last_wrong_time) || '—' }}</text>
              </view>
              <view class="time-divider"></view>
              <view class="time-item">
                <text class="time-icon">⏰</text>
                <text class="time-label">下次复习</text>
                <text class="time-value review">{{ fmtDate(it.next_review_time) || '—' }}</text>
              </view>
            </view>

            <!-- 操作提示 -->
            <view class="card-action">
              <text class="action-hint">点击查看详情 ›</text>
            </view>
          </view>
        </view>

        <button
          v-if="hasMore"
          class="load-more-btn"
          :disabled="loading"
          @tap="loadMore"
        >
          <text class="load-icon">{{ loading ? '⏳' : '⬇️' }}</text>
          <text>{{ loading ? '加载中…' : '加载更多' }}</text>
        </button>
      </view>
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

function fmtDate(s?: string) {
  if (!s) return ''
  try {
    const dt = s.replace('T', ' ').split('.')[0]
    return dt.split(' ')[0]
  } catch {
    return ''
  }
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
  } finally { 
    loading.value = false 
  }
}

const hasMore = computed(()=> items.value.length < total.value)

function loadMore(){ 
  if(!loading.value && hasMore.value) fetchPage(page.value+1) 
}

function toggleDue(e:any){ 
  onlyDue.value = !!e.detail.value
  fetchPage(1) 
}

function stemOf(it: Item): string {
  // 🔥 直接使用后端返回的 stem 字段
  if (it.stem && it.stem.trim()) {
    return it.stem.trim()
  }
  return `题目 #${it.question_id}`
}

function viewQuestion(it:Item){
  uni.navigateTo({ 
    url:`/pages/question-detail/question-detail?id=${it.question_id}&wrong=${it.wrong_count}` 
  })
}

function countLevel(n:number){
  if(n>=5) return 'high'
  if(n>=3) return 'mid'
  return 'low'
}

onMounted(()=>{
  if(!uni.getStorageSync('token')) {
    return uni.reLaunch({ url:'/pages/login/login' })
  }
  fetchPage(1)
})
</script>

<style scoped>
:root, page, .eb-page {
  --c-bg-start:#e8f2ff;
  --c-bg-end:#f5f9ff;
  --c-card:#fff;
  --c-border:#d8e6f5;
  --c-border-hover:#c6d9ec;
  --c-primary:#66b4ff;
  --c-primary-dark:#4b9ef0;
  --c-primary-light:#e6f3ff;
  --c-text:#1f2d3d;
  --c-text-sec:#5f7085;
  --c-text-muted:#8da1b5;
  --c-success:#38b26f;
  --c-success-bg:#e8f9f0;
  --c-warn:#ffb020;
  --c-warn-bg:#fff7e3;
  --c-danger:#ff4d4f;
  --c-danger-bg:#fff1f0;
  --shadow-sm:0 4rpx 12rpx rgba(35,72,130,.06);
  --shadow-md:0 8rpx 24rpx rgba(35,72,130,.08);
  --shadow-lg:0 16rpx 48rpx rgba(35,72,130,.12);
  --radius-lg:24rpx;
  --radius-md:16rpx;
  --radius-sm:12rpx;
}

.eb-page{
  min-height:100vh;
  background:linear-gradient(180deg,var(--c-bg-start),var(--c-bg-end));
}

/* ========== 顶部导航 ========== */
.top-nav{
  position:fixed;
  left:0;
  right:0;
  top:0;
  padding-top:env(safe-area-inset-top);
  height:calc(env(safe-area-inset-top) + 96rpx);
  background:linear-gradient(135deg, #66b4ff 0%, #4a9fff 100%);
  display:flex;
  align-items:flex-end;
  justify-content:center;
  padding-bottom:20rpx;
  box-shadow:var(--shadow-md);
  z-index:100;
}

.nav-content{
  display:flex;
  align-items:center;
  gap:12rpx;
  position:relative;
}

.nav-icon{
  font-size:40rpx;
  line-height:1;
}

.nav-title{
  font-size:36rpx;
  font-weight:700;
  color:#fff;
}

.nav-badge{
  padding:4rpx 12rpx;
  background:rgba(255,255,255,0.25);
  color:#fff;
  font-size:22rpx;
  font-weight:600;
  border-radius:999rpx;
  margin-left:4rpx;
}

/* ========== 内容区域 ========== */
.content-wrapper{
  padding:calc(env(safe-area-inset-top) + 116rpx) 28rpx 120rpx;
  display:flex;
  flex-direction:column;
  gap:24rpx;
}

/* ========== 筛选卡片 ========== */
.card{
  background:var(--c-card);
  border-radius:var(--radius-lg);
  box-shadow:var(--shadow-lg);
  overflow:hidden;
}

.toolbar-card{
  padding:28rpx 32rpx;
}

.filter-header{
  display:flex;
  align-items:center;
  gap:10rpx;
  padding-bottom:20rpx;
  border-bottom:1rpx solid #f0f2f5;
  margin-bottom:20rpx;
}

.filter-icon{
  font-size:28rpx;
  line-height:1;
}

.filter-title{
  font-size:28rpx;
  font-weight:600;
  color:var(--c-text);
}

.toggle-group{
  display:flex;
  flex-direction:column;
  gap:16rpx;
}

.toggle-item{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:20rpx 24rpx;
  background:#f7f9fc;
  border-radius:var(--radius-sm);
}

.toggle-label-wrap{
  display:flex;
  align-items:center;
  gap:10rpx;
}

.toggle-icon{
  font-size:28rpx;
  line-height:1;
}

.toggle-label{
  font-size:26rpx;
  font-weight:500;
  color:var(--c-text);
}

/* ========== 统计卡片 ========== */
.stats-bar{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:16rpx;
}

.stat-card{
  background:var(--c-card);
  border-radius:var(--radius-md);
  padding:24rpx;
  box-shadow:var(--shadow-sm);
  display:flex;
  align-items:center;
  gap:16rpx;
}

.stat-icon{
  font-size:48rpx;
  line-height:1;
}

.stat-content{
  flex:1;
  display:flex;
  flex-direction:column;
  gap:6rpx;
}

.stat-label{
  font-size:22rpx;
  color:var(--c-text-sec);
}

.stat-value{
  font-size:36rpx;
  font-weight:700;
  color:var(--c-text);
}

.stat-value.highlight{
  color:var(--c-primary-dark);
}

/* ========== 题目列表 ========== */
.list-section{
  display:flex;
  flex-direction:column;
  gap:20rpx;
}

.empty-state{
  text-align:center;
  padding:120rpx 40rpx;
  display:flex;
  flex-direction:column;
  align-items:center;
  gap:16rpx;
}

.empty-icon{
  font-size:96rpx;
  opacity:0.6;
}

.empty-title{
  font-size:32rpx;
  font-weight:600;
  color:var(--c-text-sec);
}

.empty-hint{
  font-size:24rpx;
  color:var(--c-text-muted);
}

.question-list{
  display:flex;
  flex-direction:column;
  gap:20rpx;
}

.question-card{
  background:var(--c-card);
  border-radius:var(--radius-md);
  padding:28rpx;
  box-shadow:var(--shadow-sm);
  position:relative;
  overflow:hidden;
  transition:all 0.3s;
}

.question-card:active{
  box-shadow:var(--shadow-md);
  transform:translateY(-4rpx);
}

.card-stripe{
  position:absolute;
  left:0;
  top:0;
  bottom:0;
  width:6rpx;
}

.stripe-low{
  background:linear-gradient(to bottom, var(--c-success) 0%, #2ea160 100%);
}

.stripe-mid{
  background:linear-gradient(to bottom, var(--c-warn) 0%, #e69800 100%);
}

.stripe-high{
  background:linear-gradient(to bottom, var(--c-danger) 0%, #d73a3c 100%);
}

.card-header{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:16rpx;
}

.qid-badge{
  display:inline-flex;
  align-items:center;
  gap:4rpx;
  padding:8rpx 16rpx;
  background:var(--c-primary-light);
  border-radius:999rpx;
  font-weight:700;
}

.badge-icon{
  font-size:20rpx;
  color:var(--c-primary-dark);
}

.badge-text{
  font-size:24rpx;
  color:var(--c-primary-dark);
}

.error-badge{
  display:inline-flex;
  align-items:center;
  gap:6rpx;
  padding:8rpx 16rpx;
  border-radius:999rpx;
  font-size:22rpx;
  font-weight:600;
}

.error-icon{
  font-size:20rpx;
  line-height:1;
}

.level-low{
  background:var(--c-success-bg);
  color:var(--c-success);
}

.level-mid{
  background:var(--c-warn-bg);
  color:var(--c-warn);
}

.level-high{
  background:var(--c-danger-bg);
  color:var(--c-danger);
}

.card-body{
  margin-bottom:16rpx;
}

.stem-text{
  font-size:28rpx;
  line-height:1.7;
  color:var(--c-text);
  display:-webkit-box;
  -webkit-box-orient:vertical;
  -webkit-line-clamp:2;
  line-clamp:2;  /* 🔥 添加标准属性 */
  overflow:hidden;
  word-break:break-word;
}

.card-footer{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding-top:16rpx;
  border-top:1rpx solid #f0f2f5;
  gap:16rpx;
}

.time-item{
  flex:1;
  display:flex;
  flex-direction:column;
  gap:6rpx;
}

.time-icon{
  font-size:24rpx;
  line-height:1;
  margin-bottom:2rpx;
}

.time-label{
  font-size:20rpx;
  color:var(--c-text-sec);
}

.time-value{
  font-size:22rpx;
  color:var(--c-text-muted);
  font-weight:500;
}

.time-value.review{
  color:var(--c-primary-dark);
  font-weight:600;
}

.time-divider{
  width:1rpx;
  height:60rpx;
  background:#e8eef5;
}

.card-action{
  margin-top:12rpx;
  padding-top:12rpx;
  border-top:1rpx solid #f0f2f5;
  text-align:right;
}

.action-hint{
  font-size:24rpx;
  color:var(--c-primary);
  font-weight:600;
}

/* ========== 加载更多 ========== */
.load-more-btn{
  width:100%;
  padding:28rpx;
  border-radius:var(--radius-md);
  background:linear-gradient(135deg, #66b4ff 0%, #4a9fff 100%);
  color:#fff;
  font-size:28rpx;
  font-weight:600;
  border:none;
  box-shadow:var(--shadow-sm);
  display:flex;
  align-items:center;
  justify-content:center;
  gap:10rpx;
  transition:all 0.3s;
}

.load-more-btn:active:not([disabled]){
  box-shadow:var(--shadow-md);
  transform:translateY(-2rpx);
}

.load-more-btn[disabled]{
  opacity:0.6;
}

.load-icon{
  font-size:32rpx;
  line-height:1;
}

button::after{
  border:none;
}

@media (min-width:700rpx){
  .toolbar-card, .stats-bar, .question-card, .load-more-btn{
    max-width:900rpx;
    margin-left:auto;
    margin-right:auto;
  }
}
</style>