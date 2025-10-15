<template>
  <view class="qb-page">
    <!-- 顶部卡片 -->
    <view class="card head-card">
      <view class="header">
        <view class="header-title">
          <text class="title-icon">📚</text>
          <view class="title-content">
            <text class="title-text">我的题库</text>
            <text class="title-sub">共 {{ total }} 道题目</text>
          </view>
        </view>
      </view>

      <view class="search-section">
        <view class="search-box">
          <text class="search-icon">🔍</text>
          <input
            class="search-input"
            v-model="keyword"
            placeholder="搜索题干关键词"
            placeholder-class="ph"
            @confirm="refresh"
          />
          <button v-if="keyword" class="clear-btn" @tap="clearSearch">×</button>
        </view>
        <button class="search-btn" @tap="refresh">搜索</button>
      </view>

      <view class="filter-section">
        <view class="filter-title">
          <text class="filter-icon">🎯</text>
          <text>筛选条件</text>
        </view>
        <view class="filter-grid">
          <picker mode="selector" :range="subjectNames" @change="onSubject">
            <view class="filter-pill">
              <text class="pill-label">学科</text>
              <text class="pill-value">{{ subjectLabel }}</text>
              <text class="pill-arrow">›</text>
            </view>
          </picker>
          <picker mode="selector" :range="levelNames" @change="onLevel">
            <view class="filter-pill">
              <text class="pill-label">学段</text>
              <text class="pill-value">{{ levelLabel }}</text>
              <text class="pill-arrow">›</text>
            </view>
          </picker>
        </view>
        <view class="active-toggle">
          <text class="toggle-label">仅显示启用题目</text>
          <switch :checked="activeOnly" @change="toggleActive" color="#66b4ff" />
        </view>
      </view>
    </view>

    <!-- 工具栏 -->
    <view class="action-bar">
      <button class="action-btn import-btn" @tap="openImport">
        <text class="btn-icon">📥</text>
        <text>导入Excel</text>
      </button>
      <button class="action-btn refresh-btn" @tap="refresh">
        <text class="btn-icon">🔄</text>
        <text>刷新</text>
      </button>
    </view>

    <!-- 题目列表 -->
    <view class="list-container">
      <view v-if="!loading && items.length===0" class="empty-state">
        <text class="empty-icon">📝</text>
        <text class="empty-text">暂无题目</text>
        <text class="empty-hint">点击"导入Excel"批量添加题目</text>
      </view>

      <view class="question-list">
        <view
          v-for="q in items"
          :key="q.question_id"
          class="question-card"
          @tap="viewDetail(q)"
        >
          <view class="card-header">
            <view class="qid-badge">
              <text class="badge-icon">#</text>
              <text class="badge-id">{{ q.question_id }}</text>
            </view>
            <view class="card-meta">
              <text class="meta-type">{{ q.type || '未分类' }}</text>
              <text class="meta-divider">|</text>
              <text class="meta-diff">{{ q.difficulty ?? '未定级' }}</text>
            </view>
          </view>

          <view class="card-body">
            <view class="question-stem">{{ q.stem || '无题干' }}</view>
          </view>

          <view class="card-footer">
            <view class="status-badge" :class="'status-' + (q.audit_status || 'draft').toLowerCase()">
              <text class="status-dot">●</text>
              <text class="status-text">{{ formatStatus(q.audit_status) }}</text>
            </view>
            <view class="card-time">
              <text class="time-icon">🕒</text>
              <text class="time-text">{{ fmtTime(q.updated_at || (q as any).created_at) }}</text>
            </view>
          </view>

          <view class="card-actions">
            <text class="action-hint">点击编辑 ›</text>
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
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api, type MyQuestionItem, type TagItem } from '@/utils/api'

const items = ref<MyQuestionItem[]>([])
const page = ref(1)
const size = ref(10)
const total = ref(0)
const loading = ref(false)

const keyword = ref('')
const subjectId = ref<number|null>(null)
const levelId = ref<number|null>(null)
const activeOnly = ref(false)

const subjects = ref<Array<{id:number|null; name:string}>>([{ id: null as number|null, name: '全部' }])
const levels   = ref<Array<{id:number|null; name:string}>>([{ id: null as number|null, name: '全部' }])
const subjectNames = computed(()=> subjects.value.map(s=>s.name))
const levelNames   = computed(()=> levels.value.map(s=>s.name))
const subjectLabel = computed(()=> subjects.value.find(s=>s.id===subjectId.value)?.name || '全部')
const levelLabel   = computed(()=> levels.value.find(s=>s.id===levelId.value)?.name || '全部')

const hasMore = computed(()=> items.value.length < total.value)

function clearSearch(){
  keyword.value = ''
  refresh()
}

function formatStatus(s?: string){
  const map: Record<string, string> = {
    'approved': '已通过',
    'pending': '待审核',
    'rejected': '已拒绝',
    'draft': '草稿'
  }
  return map[(s||'draft').toLowerCase()] || s || '草稿'
}

function fmtTime(s?: string){
  if(!s) return '未知'
  try { 
    const dt = s.replace('T',' ').split('.')[0]
    // 简化显示：只保留日期
    return dt.split(' ')[0]
  } catch { return '未知' }
}

async function fetch(p=1, append=false){
  loading.value = true
  try {
    const resp = await api.getMyQuestions({
      page: p,
      size: size.value,
      keyword: keyword.value || undefined,
      subject_id: subjectId.value==null ? undefined : subjectId.value,
      level_id: levelId.value==null ? undefined : levelId.value,
      active_only: activeOnly.value
    })
    total.value = resp?.total ?? 0
    const list = resp?.items ?? []
    if(!append) items.value = list
    else items.value = items.value.concat(list)
    page.value = resp?.page ?? p
  } catch(e:any){
    uni.showToast({ icon:'none', title: e?.data?.message || '加载失败' })
  } finally { loading.value = false }
}

function refresh(){ fetch(1,false) }
function loadMore(){ if(!loading.value && hasMore.value) fetch(page.value+1,true) }
function onSubject(e:any){
  const idx = Number(e.detail.value)
  subjectId.value = subjects.value[idx].id
  refresh()
}
function onLevel(e:any){
  const idx = Number(e.detail.value)
  levelId.value = levels.value[idx].id
  refresh()
}
function toggleActive(e:any){ activeOnly.value = !!e.detail.value; refresh() }
function viewDetail(q:MyQuestionItem){
  uni.navigateTo({ url: '/pages/question-edit/question-edit?id=' + q.question_id })
}

async function openImport(){
  uni.showActionSheet({
    itemList: ['下载模板', '上传并导入'],
    success: async (r:any)=>{
      const idx = r.tapIndex
      if(idx === 0){
        try{
          uni.showLoading({ title:'下载中' })
          const tempPath = await api.downloadImportTemplate()
          uni.hideLoading()
          if (typeof uni.openDocument === 'function') {
            uni.openDocument({
              filePath: tempPath,
              showMenu: true,
              success(){ uni.showToast({ icon:'none', title:'已打开模板' }) },
              fail(){ uni.showToast({ icon:'none', title:'已下载到临时目录' }) }
            })
          } else {
            uni.showToast({ icon:'none', title:'已下载' })
          }
        }catch(e:any){
          uni.hideLoading()
          uni.showToast({ icon:'none', title: e?.data?.message || '下载失败' })
        }
      } else if(idx === 1){
        const pickAndImport = (files:any[]) => {
          const file = files?.[0]
          if(!file) return
          const filePath = (file.path || file.tempFilePath)
          if(!filePath) return uni.showToast({ icon:'none', title:'无法读取文件路径' })
          uni.showLoading({ title:'导入中' })
          api.importQuestionsExcel(filePath)
            .then(res=>{
              uni.showModal({
                title:'导入完成',
                content:`总行:${res.total_rows}\n成功:${res.success}\n失败:${res.failed}${
                  res.failed? '\n错误:\n'+ res.errors.slice(0,5).map(e=>`行${e.row}:${e.reason}`).join('\n') + (res.errors.length>5?'\n...':'') : ''
                }`,
                showCancel:false
              })
              if(res.success>0) refresh()
            })
            .catch((e:any)=> uni.showToast({ icon:'none', title: e?.data?.message || '导入失败' }))
            .finally(()=> uni.hideLoading())
        }
        if (typeof uni.chooseFile === 'function') {
          uni.chooseFile({
            extension:['.xlsx'],
            count:1,
            success: (r2:any)=> pickAndImport(r2.tempFiles || []),
          })
        } else if (typeof uni.chooseMessageFile === 'function') {
          uni.chooseMessageFile({
            type:'file',
            extension:['.xlsx'],
            count:1,
            success: (r2:any)=> pickAndImport(r2.tempFiles || []),
          })
        } else {
          uni.showToast({ icon:'none', title:'当前端不支持选择文件' })
        }
      }
    }
  })
}

onMounted(async ()=>{
  if(!uni.getStorageSync('token')) return uni.reLaunch({ url:'/pages/login/login' })
  try {
    const [subs, levelList] = await Promise.all([
      api.listTags({ type: 'SUBJECT' }),
      api.listTags({ type: 'LEVEL' }),
    ])
    subjects.value = [{ id: null as number|null, name: '全部' }, ...(subs||[]).map((t:TagItem)=>({ id: t.id, name: t.name }))]
    levels.value   = [{ id: null as number|null, name: '全部' }, ...(levelList||[]).map((t:TagItem)=>({ id: t.id, name: t.name }))]
  } catch {}
  fetch(1)
})
</script>

<style scoped>
:root, page, .qb-page {
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
  --c-green:#38b26f;
  --c-green-bg:#e8f9f0;
  --c-warn:#ffb020;
  --c-warn-bg:#fff7e3;
  --c-red:#ff4d4f;
  --c-red-bg:#fff1f0;
  --c-blue:#4b9ef0;
  --c-blue-bg:#e6f3ff;
  --shadow-sm:0 4rpx 12rpx rgba(35,72,130,.06);
  --shadow-md:0 8rpx 24rpx rgba(35,72,130,.08);
  --shadow-lg:0 16rpx 48rpx rgba(35,72,130,.12);
  --radius-lg:24rpx;
  --radius-md:16rpx;
  --radius-sm:12rpx;
}

.qb-page{
  min-height:100vh;
  background:linear-gradient(180deg,var(--c-bg-start),var(--c-bg-end));
  padding:32rpx 28rpx 140rpx;
}

/* ========== 顶部卡片 ========== */
.card{
  background:var(--c-card);
  border-radius:var(--radius-lg);
  box-shadow:var(--shadow-lg);
  overflow:hidden;
}

.head-card{
  margin-bottom:28rpx;
}

.header{
  background:linear-gradient(135deg, #66b4ff 0%, #4a9fff 100%);
  padding:40rpx 32rpx;
  position:relative;
}
.header::after{
  content:'';
  position:absolute;
  bottom:0;
  left:0;
  right:0;
  height:40rpx;
  background:var(--c-card);
  border-radius:var(--radius-lg) var(--radius-lg) 0 0;
}

.header-title{
  display:flex;
  align-items:center;
  gap:16rpx;
}
.title-icon{
  font-size:56rpx;
  line-height:1;
}
.title-content{
  display:flex;
  flex-direction:column;
  gap:8rpx;
}
.title-text{
  font-size:40rpx;
  font-weight:700;
  color:#fff;
  line-height:1.2;
}
.title-sub{
  font-size:24rpx;
  color:rgba(255,255,255,0.85);
}

/* ========== 搜索区 ========== */
.search-section{
  display:flex;
  gap:16rpx;
  padding:0 32rpx 32rpx;
}

.search-box{
  flex:1;
  display:flex;
  align-items:center;
  gap:12rpx;
  padding:0 24rpx;
  background:#f7f9fc;
  border:2rpx solid var(--c-border);
  border-radius:var(--radius-md);
  transition:all 0.3s;
}
.search-box:focus-within{
  background:#fff;
  border-color:var(--c-primary);
  box-shadow:0 0 0 6rpx var(--c-primary-light);
}

.search-icon{
  font-size:32rpx;
  color:var(--c-text-muted);
}

.search-input{
  flex:1;
  height:86rpx;
  line-height:86rpx;
  font-size:28rpx;
  color:var(--c-text);
  background:transparent;
  border:none;
}
.ph{ 
  color:var(--c-text-muted); 
  font-size:28rpx; 
}

.clear-btn{
  width:48rpx;
  height:48rpx;
  border-radius:50%;
  background:#dce5f0;
  color:var(--c-text-sec);
  font-size:32rpx;
  font-weight:700;
  display:flex;
  align-items:center;
  justify-content:center;
  border:none;
  padding:0;
  line-height:1;
}
.clear-btn:active{
  opacity:0.7;
}

.search-btn{
  padding:0 36rpx;
  height:86rpx;
  border-radius:var(--radius-md);
  background:linear-gradient(135deg, var(--c-primary) 0%, #4a9fff 100%);
  color:#fff;
  font-size:28rpx;
  font-weight:600;
  border:none;
  box-shadow:var(--shadow-sm);
  transition:all 0.3s;
}
.search-btn:active{
  box-shadow:var(--shadow-md);
  transform:translateY(-2rpx);
}

/* ========== 筛选区 ========== */
.filter-section{
  padding:0 32rpx 32rpx;
  display:flex;
  flex-direction:column;
  gap:20rpx;
}

.filter-title{
  display:flex;
  align-items:center;
  gap:10rpx;
  font-size:26rpx;
  font-weight:600;
  color:var(--c-text-sec);
}
.filter-icon{
  font-size:28rpx;
}

.filter-grid{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:16rpx;
}

.filter-pill{
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:20rpx 24rpx;
  background:#f7f9fc;
  border:2rpx solid var(--c-border);
  border-radius:var(--radius-sm);
  transition:all 0.3s;
}
.filter-pill:active{
  background:#fff;
  border-color:var(--c-primary);
}

.pill-label{
  font-size:24rpx;
  color:var(--c-text-sec);
}
.pill-value{
  flex:1;
  text-align:center;
  font-size:26rpx;
  font-weight:600;
  color:var(--c-primary-dark);
}
.pill-arrow{
  font-size:32rpx;
  color:var(--c-text-muted);
  font-weight:300;
}

.active-toggle{
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:20rpx 24rpx;
  background:#f7f9fc;
  border-radius:var(--radius-sm);
}
.toggle-label{
  font-size:26rpx;
  color:var(--c-text);
  font-weight:500;
}

/* ========== 工具栏 ========== */
.action-bar{
  display:flex;
  gap:16rpx;
  margin-bottom:28rpx;
}

.action-btn{
  flex:1;
  padding:24rpx;
  border-radius:var(--radius-md);
  display:flex;
  align-items:center;
  justify-content:center;
  gap:10rpx;
  font-size:28rpx;
  font-weight:600;
  border:none;
  box-shadow:var(--shadow-sm);
  transition:all 0.3s;
}
.action-btn:active{
  transform:translateY(-2rpx);
}

.import-btn{
  background:linear-gradient(135deg, #52c41a 0%, #38b26f 100%);
  color:#fff;
}
.refresh-btn{
  background:#fff;
  color:var(--c-text-sec);
  border:2rpx solid var(--c-border);
}

.btn-icon{
  font-size:32rpx;
}

/* ========== 题目列表 ========== */
.list-container{
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
  opacity:0.5;
}
.empty-text{
  font-size:32rpx;
  color:var(--c-text-sec);
  font-weight:600;
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
  transition:all 0.3s;
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
.question-card:active{
  box-shadow:var(--shadow-md);
  transform:translateY(-4rpx);
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
  font-size:24rpx;
  color:var(--c-primary-dark);
}
.badge-id{
  font-size:26rpx;
  color:var(--c-primary-dark);
}

.card-meta{
  display:flex;
  align-items:center;
  gap:10rpx;
  font-size:24rpx;
  color:var(--c-text-sec);
}
.meta-divider{
  color:var(--c-border-hover);
}
.meta-diff{
  font-weight:600;
}

.card-body{
  margin-bottom:16rpx;
}

.question-stem{
  font-size:28rpx;
  line-height:1.6;
  color:var(--c-text);
  display:-webkit-box;
  -webkit-box-orient:vertical;
  -webkit-line-clamp:3;
  overflow:hidden;
}

.card-footer{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding-top:16rpx;
  border-top:1rpx solid #f0f2f5;
}

.status-badge{
  display:inline-flex;
  align-items:center;
  gap:8rpx;
  padding:8rpx 16rpx;
  border-radius:999rpx;
  font-size:22rpx;
  font-weight:600;
}
.status-dot{
  font-size:16rpx;
  line-height:1;
}

.status-approved{
  background:var(--c-green-bg);
  color:var(--c-green);
}
.status-pending{
  background:var(--c-warn-bg);
  color:var(--c-warn);
}
.status-rejected{
  background:var(--c-red-bg);
  color:var(--c-red);
}
.status-draft{
  background:#f0f2f5;
  color:var(--c-text-muted);
}

.card-time{
  display:flex;
  align-items:center;
  gap:6rpx;
  font-size:22rpx;
  color:var(--c-text-muted);
}
.time-icon{
  font-size:24rpx;
}

.card-actions{
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
  background:linear-gradient(135deg, var(--c-primary) 0%, #4a9fff 100%);
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
}

button::after{
  border:none;
}
</style>
