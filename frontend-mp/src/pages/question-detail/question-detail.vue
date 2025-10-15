// filepath: c:\Users\yjq\Desktop\myproject\frontend-mp\src\pages\question-detail\question-detail.vue
<template>
  <view class="qd-page">
    <!-- 顶部导航 -->
    <view class="top-nav">
      <view class="nav-content">
        <text class="nav-icon">📝</text>
        <text class="nav-title">题目详情</text>
      </view>
    </view>

    <view class="content-wrapper">
      <!-- 题目卡片 -->
      <view class="card question-card">
        <view class="card-badge">
          <text class="badge-icon">#</text>
          <text class="badge-text">{{ qid }}</text>
        </view>

        <!-- 题干 -->
        <view class="section stem-section">
          <view class="section-header">
            <text class="section-icon">📋</text>
            <text class="section-title">题干</text>
          </view>
          <view class="stem-content">{{ q?.stem || '加载中…' }}</view>
        </view>

        <!-- 选项 -->
        <view class="section options-section">
          <view class="section-header">
            <text class="section-icon">✅</text>
            <text class="section-title">选项</text>
          </view>
          <view v-if="q?.options?.length" class="options-list">
            <view v-for="(op, idx) in q?.options" :key="idx" class="option-item">
              <view class="option-badge">{{ op.key || String.fromCharCode(65+idx) }}</view>
              <text class="option-text">{{ op.text || op.content }}</text>
            </view>
          </view>
          <view v-else class="empty-hint">
            <text class="empty-icon">📭</text>
            <text class="empty-text">暂无选项</text>
          </view>
        </view>

        <!-- 解析 -->
        <view class="section analysis-section">
          <view class="section-header">
            <text class="section-icon">💡</text>
            <text class="section-title">解析</text>
          </view>
          <view class="analysis-content">
            <text class="analysis-text">{{ q?.analysis || '暂无解析' }}</text>
          </view>
        </view>
      </view>

      <!-- 知识点卡片 -->
      <view class="card knowledge-card">
        <view class="section-header">
          <text class="section-icon">🎯</text>
          <text class="section-title">知识点</text>
          <view class="kp-count">{{ selectedIds.length }}</view>
        </view>
        <view class="kp-container">
          <view v-if="selectedIds.length===0" class="empty-hint">
            <text class="empty-icon">📚</text>
            <text class="empty-text">暂未绑定知识点</text>
          </view>
          <view v-else class="kp-chips">
            <view v-for="id in selectedIds" :key="id" class="kp-chip">
              <text class="chip-text">{{ idToPath.get(id) || ('#'+id) }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 统计卡片 -->
      <view class="card stats-card">
        <view class="stats-row">
          <view class="stat-item">
            <text class="stat-icon">❌</text>
            <view class="stat-content">
              <text class="stat-label">历史错误次数</text>
              <text class="stat-value" :class="'level-' + getErrorLevel(wrongCount)">{{ wrongCount }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 操作按钮 -->
      <button class="action-btn back-btn" @tap="goBack">
        <text class="btn-icon">↩️</text>
        <text>返回</text>
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import {
  api,
  listKnowledgeTree,
  getQuestionKnowledge,
  type KnowledgeNode,
  type QuestionBrief
} from '@/utils/api'

const qid = ref<number>(0)
const wrongCount = ref<number>(0)
const q = ref<QuestionBrief | null>(null)

function getErrorLevel(count: number): string {
  if (count === 0) return 'zero'
  if (count <= 2) return 'low'
  if (count <= 5) return 'mid'
  return 'high'
}

function goBack(){
  try{
    const pages = getCurrentPages?.()
    if(pages && pages.length > 1) return uni.navigateBack()
  }catch(e){}
  uni.reLaunch({ url:'/pages/error-book/error-book' })
}

async function loadDetail(){
  try{
    const d = await api.getQuestionDetail(qid.value)
    const raw: any = d || {}
    q.value = {
      id: (raw.id ?? qid.value) as number,
      stem: (raw.stem ?? raw.title ?? '') as string,
      options: (raw.options ?? raw.choices ?? []) as any[],
      analysis: (raw.analysis ?? raw.explanation ?? '') as string,
    }
  }catch{
    q.value = { id: qid.value, stem: `#${qid.value}`, options: [], analysis: '' } as any
  }
}

/* ------- 知识点展示状态（仅读取） ------- */
type KpOpt = { id:number; label:string }

const kpTree = ref<KnowledgeNode[]>([])
const idToPath = ref<Map<number, string>>(new Map())
const selectedIds = ref<number[]>([])

function flattenTree(nodes: KnowledgeNode[], prefix = ''): KpOpt[] {
  const ret: KpOpt[] = []
  for(const n of nodes || []){
    const label = prefix ? `${prefix}/${n.name}` : n.name
    ret.push({ id: n.id, label })
    if(n.children && n.children.length){
      ret.push(...flattenTree(n.children, label))
    }
    idToPath.value.set(n.id, label)
  }
  return ret
}

async function loadKnowledge(){
  try{
    const tree = await listKnowledgeTree()
    kpTree.value = tree || []
    flattenTree(kpTree.value)
  }catch{
    kpTree.value = []
  }
  try{
    const list = await getQuestionKnowledge(qid.value) as Array<{ knowledge_id: number }>
    selectedIds.value = (list || []).map((x: { knowledge_id: number }) => Number(x.knowledge_id))
  }catch{
    selectedIds.value = []
  }
}

onLoad(async (opt:any)=>{
  qid.value = Number(opt?.id || 0)
  wrongCount.value = Number(opt?.wrong || 0)
  if(!qid.value){
    uni.showToast({ icon:'none', title:'参数错误' })
    setTimeout(()=>goBack(), 600)
    return
  }
  await Promise.all([loadDetail(), loadKnowledge()])
})
</script>

<style scoped>
:root, page, .qd-page{
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
  --c-warn:#ffb020;
  --c-danger:#ff4d4f;
  --shadow-sm:0 4rpx 12rpx rgba(35,72,130,.06);
  --shadow-md:0 8rpx 24rpx rgba(35,72,130,.08);
  --shadow-lg:0 16rpx 48rpx rgba(35,72,130,.12);
  --radius-lg:24rpx;
  --radius-md:16rpx;
  --radius-sm:12rpx;
}

.qd-page{
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

/* ========== 内容区域 ========== */
.content-wrapper{
  padding:calc(env(safe-area-inset-top) + 116rpx) 28rpx 120rpx;
  display:flex;
  flex-direction:column;
  gap:24rpx;
}

/* ========== 卡片样式 ========== */
.card{
  background:var(--c-card);
  border-radius:var(--radius-lg);
  box-shadow:var(--shadow-lg);
  padding:32rpx;
  position:relative;
  overflow:hidden;
}

.question-card::before{
  content:'';
  position:absolute;
  left:0;
  top:0;
  bottom:0;
  width:6rpx;
  background:linear-gradient(to bottom, var(--c-primary) 0%, #4a9fff 100%);
}

.card-badge{
  position:absolute;
  top:32rpx;
  right:32rpx;
  display:flex;
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

/* ========== 区块样式 ========== */
.section{
  display:flex;
  flex-direction:column;
  gap:16rpx;
}

.section + .section{
  margin-top:28rpx;
  padding-top:28rpx;
  border-top:1rpx solid #f0f2f5;
}

.section-header{
  display:flex;
  align-items:center;
  gap:10rpx;
}

.section-icon{
  font-size:28rpx;
  line-height:1;
}

.section-title{
  font-size:28rpx;
  font-weight:600;
  color:var(--c-text);
}

/* ========== 题干 ========== */
.stem-content{
  font-size:30rpx;
  line-height:1.8;
  color:var(--c-text);
  padding:20rpx 24rpx;
  background:#f7f9fc;
  border-radius:var(--radius-sm);
  word-break:break-word;
}

/* ========== 选项 ========== */
.options-list{
  display:flex;
  flex-direction:column;
  gap:16rpx;
}

.option-item{
  display:flex;
  align-items:flex-start;
  gap:16rpx;
  padding:20rpx 24rpx;
  background:#f7f9fc;
  border-radius:var(--radius-sm);
  transition:all 0.3s;
}

.option-item:active{
  background:#eef3f7;
}

.option-badge{
  width:48rpx;
  height:48rpx;
  border-radius:50%;
  background:linear-gradient(135deg, var(--c-primary) 0%, #4a9fff 100%);
  color:#fff;
  font-size:24rpx;
  font-weight:700;
  display:flex;
  align-items:center;
  justify-content:center;
  flex-shrink:0;
}

.option-text{
  flex:1;
  font-size:28rpx;
  line-height:1.6;
  color:var(--c-text);
  padding-top:4rpx;
}

/* ========== 解析 ========== */
.analysis-content{
  padding:20rpx 24rpx;
  background:#fffbf0;
  border-left:4rpx solid var(--c-warn);
  border-radius:var(--radius-sm);
}

.analysis-text{
  font-size:28rpx;
  line-height:1.8;
  color:var(--c-text);
  word-break:break-word;
}

/* ========== 知识点 ========== */
.kp-count{
  margin-left:auto;
  padding:6rpx 16rpx;
  background:var(--c-primary-light);
  color:var(--c-primary-dark);
  font-size:22rpx;
  font-weight:600;
  border-radius:999rpx;
}

.kp-container{
  margin-top:8rpx;
}

.kp-chips{
  display:flex;
  flex-wrap:wrap;
  gap:12rpx;
}

.kp-chip{
  display:inline-flex;
  align-items:center;
  padding:12rpx 20rpx;
  background:linear-gradient(135deg, var(--c-primary-light) 0%, #d6ebff 100%);
  border:2rpx solid var(--c-primary);
  border-radius:999rpx;
  transition:all 0.3s;
}

.kp-chip:active{
  transform:scale(0.96);
}

.chip-text{
  font-size:24rpx;
  color:var(--c-primary-dark);
  font-weight:600;
  max-width:400rpx;
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
}

/* ========== 空状态 ========== */
.empty-hint{
  display:flex;
  flex-direction:column;
  align-items:center;
  gap:12rpx;
  padding:48rpx 0;
}

.empty-icon{
  font-size:64rpx;
  opacity:0.5;
}

.empty-text{
  font-size:26rpx;
  color:var(--c-text-muted);
}

/* ========== 统计卡片 ========== */
.stats-card{
  background:linear-gradient(135deg, #f7f9fc 0%, #fff 100%);
}

.stats-row{
  display:flex;
  gap:16rpx;
}

.stat-item{
  flex:1;
  display:flex;
  align-items:center;
  gap:16rpx;
  padding:24rpx;
  background:#fff;
  border-radius:var(--radius-md);
  border:2rpx solid var(--c-border);
}

.stat-icon{
  font-size:48rpx;
  line-height:1;
}

.stat-content{
  flex:1;
  display:flex;
  flex-direction:column;
  gap:8rpx;
}

.stat-label{
  font-size:24rpx;
  color:var(--c-text-sec);
}

.stat-value{
  font-size:40rpx;
  font-weight:700;
}

.stat-value.level-zero{
  color:var(--c-success);
}

.stat-value.level-low{
  color:var(--c-primary);
}

.stat-value.level-mid{
  color:var(--c-warn);
}

.stat-value.level-high{
  color:var(--c-danger);
}

/* ========== 操作按钮 ========== */
.action-btn{
  width:100%;
  padding:28rpx 0;
  border-radius:var(--radius-md);
  font-size:30rpx;
  font-weight:600;
  border:none;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:10rpx;
  transition:all 0.3s;
  box-shadow:var(--shadow-sm);
}

.back-btn{
  background:#f7f9fc;
  color:var(--c-text-sec);
  border:2rpx solid var(--c-border);
}

.back-btn:active{
  background:#eef3f7;
  box-shadow:var(--shadow-md);
  transform:translateY(-2rpx);
}

.btn-icon{
  font-size:32rpx;
  line-height:1;
}

button::after{
  border:none;
}
</style>