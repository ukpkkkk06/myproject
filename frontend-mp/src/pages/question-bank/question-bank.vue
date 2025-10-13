<template>
  <view class="qb-page">
    <view class="card head-card">
      <view class="search-row">
        <input
          class="search-input"
          v-model="keyword"
          placeholder="搜索题干关键词"
          placeholder-class="ph"
          @confirm="refresh"
        />
        <button class="mini-btn primary" @tap="refresh">搜索</button>
      </view>

      <view class="filter-row">
        <picker mode="selector" :range="subjectNames" @change="onSubject">
          <view class="pill">
            学科：<text class="pill-val">{{ subjectLabel }}</text>
          </view>
        </picker>
        <picker mode="selector" :range="levelNames" @change="onLevel">
          <view class="pill">
            学段：<text class="pill-val">{{ levelLabel }}</text>
          </view>
        </picker>
        <view class="switch-wrap">
          <switch :checked="activeOnly" @change="toggleActive" color="#66b4ff" />
          <text class="sw-label">仅启用</text>
        </view>
      </view>
    </view>

    <view class="toolbar">
      <button class="mini-btn" @tap="openImport">导入Excel</button>
    </view>

    <view class="list">
      <view v-if="!loading && items.length===0" class="empty">暂无题目</view>
      <view
        v-for="q in items"
        :key="q.question_id"
        class="q-card"
        @tap="viewDetail(q)"
      >
        <view class="q-top">
          <text class="qid">#{{ q.question_id }}</text>
          <text class="q-meta">{{ q.type || '-' }} | {{ q.difficulty ?? '-' }}</text>
        </view>
        <view class="stem">{{ q.stem || '-' }}</view>
        <view class="q-bottom">
          <text class="tag" :class="statusCls(q.audit_status)">{{ q.audit_status }}</text>
          <text class="time">{{ fmtTime(q.updated_at || (q as any).created_at) }}</text>
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

function fmtTime(s?: string){
  if(!s) return '-'
  try { return s.replace('T',' ').split('.')[0] } catch { return '-' }
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
function statusCls(s?: string){
  s = (s||'').toLowerCase()
  if(s==='approved') return 'approved'
  if(s==='pending') return 'pending'
  if(s==='rejected') return 'rejected'
  return ''
}

async function openImport(){
  uni.showActionSheet({
    itemList: ['下载模板', '上传并导入'],
    success: async (r:any)=>{
      const idx = r.tapIndex
      if(idx === 0){
        // 下载模板
        try{
          uni.showLoading({ title:'下载中' })
          const tempPath = await api.downloadImportTemplate()
          uni.hideLoading()
          // 尝试直接打开（微信小程序支持）
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
        // 上传并导入
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
  --c-green:#38b26f;
  --c-green-bg:#e6fff5;
  --c-warn:#ffb020;
  --c-warn-bg:#fff7e3;
  --c-red:#ff4d4f;
  --c-red-bg:#fff1f0;
  --radius:20rpx;
  --radius-s:14rpx;
}

.qb-page{
  min-height:100vh;
  background:linear-gradient(180deg,var(--c-bg-grad-top),var(--c-bg-grad-bottom));
  padding:24rpx 26rpx 120rpx;
  box-sizing:border-box;
  display:flex;
  flex-direction:column;
}

.card{
  background:var(--c-panel);
  border:1rpx solid var(--c-border);
  border-radius:var(--radius);
  box-shadow:0 8rpx 24rpx rgba(35,72,130,0.08),0 2rpx 6rpx rgba(35,72,130,0.06);
}

.head-card{
  padding:40rpx 34rpx 38rpx;
  margin-bottom:34rpx;
  display:flex;
  flex-direction:column;
  gap:34rpx;
}

.search-row{
  display:flex;
  gap:20rpx;
  align-items:center;
}

.search-input{
  flex:1;
  height:86rpx;
  line-height:86rpx;
  padding:0 30rpx;
  font-size:30rpx;
  background:#fff;
  border:1rpx solid var(--c-border);
  border-radius:var(--radius-s);
  box-sizing:border-box;
  transition:border-color .18s, box-shadow .18s;
  color:var(--c-text);
}
.search-input:focus{
  border-color:var(--c-primary);
  box-shadow:0 0 0 4rpx var(--c-primary-light);
}
.ph{ color:#9ab2c7; font-size:30rpx; line-height:86rpx; }

.mini-btn{
  padding:0 34rpx;
  height:86rpx;
  line-height:86rpx;
  font-size:28rpx;
  border:none;
  border-radius:var(--radius-s);
  color:#fff;
  background:#ccc;
  font-weight:600;
}
.mini-btn.primary{
  background:linear-gradient(90deg,#a9d6ff,#66b4ff);
  box-shadow:0 6rpx 14rpx rgba(102,180,255,.35);
}
.mini-btn:active{ opacity:.85; }
.mini-btn[disabled]{ opacity:.5; }

.filter-row{
  display:flex;
  flex-wrap:wrap;
  gap:20rpx 22rpx;
  align-items:center;
}

.pill{
  background:#fff;
  border:1rpx solid var(--c-border);
  border-radius:999rpx;
  padding:14rpx 28rpx;
  font-size:24rpx;
  line-height:1;
  color:var(--c-text-sec);
  display:flex;
  align-items:center;
  gap:4rpx;
  box-shadow:0 2rpx 6rpx rgba(35,72,130,0.08);
}
.pill-val{ color:var(--c-primary-dark); font-weight:600; }

.switch-wrap{ display:flex; align-items:center; gap:10rpx; }
.sw-label{ font-size:24rpx; color:var(--c-text-sec); }

.list{ display:flex; flex-direction:column; gap:24rpx; }

.q-card{
  background:#fff;
  border:1rpx solid var(--c-border);
  border-radius:var(--radius-s);
  padding:26rpx 30rpx 30rpx;
  box-shadow:0 4rpx 12rpx rgba(35,72,130,0.06);
  display:flex;
  flex-direction:column;
  gap:10rpx;
  transition:border-color .15s, box-shadow .15s, background .15s;
}
.q-card:active{ opacity:.88; }
.q-top{
  display:flex;
  justify-content:space-between;
  font-size:26rpx;
  font-weight:600;
}
.qid{ color:var(--c-primary-dark); }
.q-meta{ color:var(--c-text-sec); font-weight:500; }
.stem{
  font-size:30rpx;
  line-height:1.55;
  color:var(--c-text);
  display:-webkit-box;
  -webkit-box-orient:vertical;
  -webkit-line-clamp:3;
  line-clamp:3; /* 标准属性，兼容性提示 */
  overflow:hidden;
}
.q-bottom{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-top:6rpx;
}
.tag{
  font-size:22rpx;
  padding:10rpx 20rpx;
  border-radius:999rpx;
  font-weight:600;
  letter-spacing:.5rpx;
  background:#eef3f7;
  color:var(--c-text-sec);
  line-height:1;
}
.tag.approved{ background:var(--c-green-bg); color:var(--c-green); }
.tag.pending{ background:var(--c-warn-bg); color:var(--c-warn); }
.tag.rejected{ background:var(--c-red-bg); color:var(--c-red); }
.time{ font-size:22rpx; color:#9aa6b2; }

.empty{
  text-align:center;
  color:var(--c-text-sec);
  padding:120rpx 0 40rpx;
  font-size:28rpx;
}

.load-btn{
  margin-top:12rpx;
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

.toolbar{ padding:16rpx 24rpx; display:flex; gap:20rpx; }

@media (min-width:700rpx){
  .head-card, .q-card { max-width:900rpx; margin:0 auto; }
  .load-btn { max-width:900rpx; margin:12rpx auto 0; }
}
</style>
