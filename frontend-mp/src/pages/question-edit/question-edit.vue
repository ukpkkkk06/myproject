<template>
  <view class="qe-page">
    <view class="card">
      <view class="header">
        <view class="title">
          <text class="icon">✏️</text>
          <text>编辑题目</text>
        </view>
        <view class="subtitle">完善题目信息，让学习更高效</view>
      </view>

      <view class="form">
        <!-- 题干 -->
        <view class="field-group">
          <view class="label">
            <text class="label-icon">📝</text>
            <text>题干</text>
            <text class="required">*</text>
          </view>
          <textarea class="ipt area" v-model="form.stem" placeholder="请输入题干内容" />
        </view>

        <!-- 选项 -->
        <view class="field-group">
          <view class="label">
            <text class="label-icon">📋</text>
            <text>选项</text>
            <text class="required">*</text>
          </view>
          <view class="opts">
            <view class="opt-card" v-for="(op, i) in form.options" :key="i">
              <view class="opt-header">
                <view class="opt-key-badge">{{ keyOf(i) }}</view>
                <input class="opt-input" v-model="op.text" :placeholder="'请输入选项 ' + keyOf(i)" />
              </view>
              <view class="opt-actions">
                <label class="correct-label" :class="{ active: form.correct_answer===keyOf(i) }" @tap="setCorrect(i)">
                  <radio :checked="form.correct_answer===keyOf(i)" color="#66b4ff" />
                  <text>正确答案</text>
                </label>
                <button class="mini-btn danger" @tap="removeOpt(i)">
                  <text class="btn-icon">🗑️</text>
                  <text>删除</text>
                </button>
              </view>
            </view>
            <button class="add-opt-btn" @tap="addOpt">
              <text class="plus-icon">+</text>
              <text>新增选项</text>
            </button>
          </view>
        </view>

        <!-- 解析 -->
        <view class="field-group">
          <view class="label">
            <text class="label-icon">💡</text>
            <text>解析</text>
          </view>
          <textarea class="ipt area" v-model="form.analysis" placeholder="请输入题目解析（可选）" />
        </view>

        <!-- 状态 -->
        <view class="field-group">
          <view class="status-bar">
            <view class="label-with-icon">
              <text class="label-icon">⚙️</text>
              <text class="label">题目状态</text>
            </view>
            <view class="status-switch">
              <switch :checked="form.is_active" @change="onActiveChange" color="#66b4ff" />
              <text class="status-text" :class="{ active: form.is_active }">
                {{ form.is_active ? '✓ 已启用' : '✕ 已停用' }}
              </text>
            </view>
          </view>
        </view>

        <!-- 学科/学段 -->
        <view class="field-group">
          <view class="label">
            <text class="label-icon">🏫</text>
            <text>分类标签</text>
          </view>
          <view class="tag-row">
            <view class="tag-item">
              <text class="tag-label">学科</text>
              <picker class="tag-picker" mode="selector" :range="subjects" range-key="name" @change="onSubjectPick">
                <view class="tag-value">{{ curSubjectName || '请选择' }}</view>
              </picker>
            </view>
            <view class="tag-item">
              <text class="tag-label">学段</text>
              <picker class="tag-picker" mode="selector" :range="levels" range-key="name" @change="onLevelPick">
                <view class="tag-value">{{ curLevelName || '请选择' }}</view>
              </picker>
            </view>
          </view>
        </view>

        <!-- 知识点 -->
        <view class="field-group kp-group">
          <view class="label-row">
            <view class="label">
              <text class="label-icon">🎯</text>
              <text>知识点</text>
            </view>
            <view class="kp-count">{{ selectedKpIds.length }} 个</view>
          </view>

          <!-- 已选知识点 -->
          <view class="selected-kp">
            <view v-if="selectedKpIds.length===0" class="empty-state">
              <text class="empty-icon">📚</text>
              <text class="empty-text">暂未绑定知识点</text>
            </view>
            <view v-else class="kp-chips">
              <view v-for="id in selectedKpIds" :key="id" class="kp-chip">
                <text class="chip-text">{{ idToPath.get(id) || ('#'+id) }}</text>
                <text class="chip-close" @tap="removeKp(id)">×</text>
              </view>
            </view>
          </view>

          <!-- 搜索框 -->
          <view class="search-box">
            <text class="search-icon">🔍</text>
            <input class="search-input" v-model="kpKeyword" placeholder="搜索知识点，如：数学/代数" @confirm="noop" />
          </view>

          <!-- 知识点列表 -->
          <view class="kp-selector">
            <scroll-view scroll-y class="kp-scroll">
              <checkbox-group @change="onKpCheckboxChange">
                <label v-for="opt in filteredKp" :key="opt.id" class="kp-option" :class="{ checked: kpIdsSet.has(opt.id) }">
                  <checkbox :value="String(opt.id)" :checked="kpIdsSet.has(opt.id)" color="#66b4ff" />
                  <text class="kp-name">{{ opt.label }}</text>
                </label>
              </checkbox-group>
              <view v-if="filteredKp.length===0" class="no-result">
                <text>😅 没有找到匹配的知识点</text>
              </view>
            </scroll-view>
          </view>
        </view>

        <!-- 操作按钮 -->
        <view class="btn-group">
          <button class="action-btn primary" :disabled="saving" @tap="save">
            <text class="btn-icon">{{ saving ? '⏳' : '💾' }}</text>
            <text>{{ saving ? '保存中…' : '保存修改' }}</text>
          </button>
          <button class="action-btn ghost" @tap="goBack">
            <text class="btn-icon">↩️</text>
            <text>返回</text>
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import {
  api,
  listKnowledgeTree,
  bindQuestionKnowledge,
  getQuestionKnowledge,
  type TagItem,
  type KnowledgeNode,
  type QuestionKnowledgeItem
} from '@/utils/api'

const qid = ref<number>(0)
const saving = ref(false)
const form = ref<{
  stem: string
  options: { key?: string; text: string }[]
  correct_answer: string
  analysis: string
  is_active: boolean
}>({
  stem: '',
  options: [],
  correct_answer: 'A',
  analysis: '',
  is_active: true,
})

const subjects = ref<TagItem[]>([])
const levels = ref<TagItem[]>([])
const curSubjectId = ref<number|null>(null)
const curLevelId = ref<number|null>(null)
const curSubjectName = computed(()=> subjects.value.find(t=>t.id===curSubjectId.value)?.name || '')
const curLevelName = computed(()=> levels.value.find(t=>t.id===curLevelId.value)?.name || '')

type KpOpt = { id:number; label:string }
const kpTree = ref<KnowledgeNode[]>([])
const kpOptions = ref<KpOpt[]>([])
const idToPath = ref<Map<number, string>>(new Map())
const selectedKpIds = ref<number[]>([])
const kpKeyword = ref('')

const kpIdsSet = computed(()=> new Set(selectedKpIds.value))
const filteredKp = computed(()=> {
  const kw = kpKeyword.value.trim().toLowerCase()
  if(!kw) return kpOptions.value
  return kpOptions.value.filter(o => o.label.toLowerCase().includes(kw))
})

function noop(){}
function keyOf(i:number){ return String.fromCharCode(65 + i) }
function setCorrect(i:number){ form.value.correct_answer = keyOf(i) }
function addOpt(){ form.value.options.push({ text: '' }) }
function removeOpt(i:number){
  form.value.options.splice(i,1)
  if(form.value.correct_answer === keyOf(i)) form.value.correct_answer = keyOf(0)
}
function removeKp(id: number){
  selectedKpIds.value = selectedKpIds.value.filter(x => x !== id)
}
function onKpCheckboxChange(e: any){
  const vals = (e?.detail?.value || []) as string[]
  selectedKpIds.value = vals.map(v => Number(v))
}

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

function normalizeOptions(raw:any): {key?:string; text:string}[] {
  if(!raw) return []
  if(Array.isArray(raw)){
    return raw.map((it:any, i:number)=> {
      if(typeof it === 'string') return { key: keyOf(i), text: it }
      return { key: it.key ?? keyOf(i), text: it.text ?? it.content ?? '' }
    })
  }
  if(typeof raw === 'object'){
    return Object.entries(raw).map(([k,v]:any)=> ({ key: k, text: String(v) }))
  }
  return []
}

async function load(){
  try {
    const d:any = await api.getQuestionDetail(qid.value)
    form.value.stem = d?.stem ?? d?.title ?? ''
    form.value.options = normalizeOptions(d?.options ?? d?.choices)
    if(form.value.options.length===0) form.value.options = [{text:''},{text:''}]
    form.value.analysis = d?.analysis ?? d?.explanation ?? ''
    form.value.correct_answer = (d?.correct_answer ?? 'A')
    form.value.is_active = !!(d?.is_active ?? true)
  } catch(e:any){
    uni.showToast({ icon:'none', title: e?.data?.message || '加载题目失败' })
  }
}

async function loadTags(){
  subjects.value = await api.listTags({ type:'SUBJECT' }).catch(()=>[])
  levels.value = await api.listTags({ type:'LEVEL' }).catch(()=>[])
  const qt = await api.getQuestionTags(qid.value).catch(()=>null)
  if(qt){
    curSubjectId.value = qt.subject_id ?? null
    curLevelId.value = qt.level_id ?? null
  }
}

async function loadKnowledge(){
  try{
    const tree = await listKnowledgeTree()
    kpTree.value = tree || []
    kpOptions.value = flattenTree(kpTree.value)
  }catch{
    kpTree.value = []; kpOptions.value = []
  }
  try{
    const list = await getQuestionKnowledge(qid.value)
    selectedKpIds.value = (list || []).map((x: any) => Number(x.knowledge_id))
  }catch{
    selectedKpIds.value = []
  }
}

function onSubjectPick(e:any){
  const idx = Number(e?.detail?.value ?? -1)
  if(idx>=0) curSubjectId.value = subjects.value[idx].id
}
function onLevelPick(e:any){
  const idx = Number(e?.detail?.value ?? -1)
  if(idx>=0) curLevelId.value = levels.value[idx].id
}

async function save(){
  if(!form.value.stem.trim()){ return uni.showToast({ icon:'none', title:'请填写题干' }) }
  if(form.value.options.length<2){ return uni.showToast({ icon:'none', title:'至少两个选项' }) }
  saving.value = true
  try{
    const payload = {
      stem: form.value.stem,
      options: form.value.options.map((o: {key?:string; text:string}, i:number)=> ({ key: o.key ?? keyOf(i), text: o.text })),
      correct_answer: form.value.correct_answer,
      analysis: form.value.analysis,
      is_active: form.value.is_active,
    }
    await api.updateQuestion(qid.value, payload)
    await api.setQuestionTags(qid.value, {
      subject_id: curSubjectId.value ?? undefined,
      level_id: curLevelId.value ?? undefined,
    })
    const kpItems: QuestionKnowledgeItem[] = selectedKpIds.value.map(id => ({ knowledge_id: id }))
    await bindQuestionKnowledge(qid.value, kpItems)
    
    // 🔥 修复：先发送事件，再提示和返回
    uni.$emit('question-updated', { 
      questionId: qid.value,
      timestamp: Date.now() 
    })
    
    uni.showToast({ icon:'success', title:'已保存' })
    setTimeout(()=>goBack(), 400)
  }catch(e:any){
    uni.showToast({ icon:'none', title: e?.data?.message || '保存失败' })
  }finally{ 
    saving.value=false 
  }
}

function goBack(){
  try{
    const pages = getCurrentPages?.()
    if(pages && pages.length>1) return uni.navigateBack()
  }catch(e){}
  uni.reLaunch({ url:'/pages/question-bank/question-bank' })
}

function onActiveChange(e: any) {
  form.value.is_active = !!e?.detail?.value
}

onLoad((opt:any)=>{
  qid.value = Number(opt?.id || 0)
  if(!qid.value){ uni.showToast({ icon:'none', title:'参数错误' }); return setTimeout(()=>goBack(),500) }
  load()
  loadTags()
  loadKnowledge()
})
</script>

<style scoped>
:root, page, .qe-page{
  --c-bg-start:#e8f2ff;
  --c-bg-end:#f5f9ff;
  --c-card:#fff;
  --c-border:#d8e6f5;
  --c-text:#1f2d3d;
  --c-text-light:#5f7085;
  --c-text-muted:#8da1b5;
  --c-primary:#66b4ff;
  --c-primary-light:#e6f3ff;
  --c-success:#52c41a;
  --c-danger:#ff4d4f;
  --c-danger-light:#fff5f5;
  --shadow-sm: 0 4rpx 12rpx rgba(35,72,130,.06);
  --shadow-md: 0 8rpx 24rpx rgba(35,72,130,.08);
  --shadow-lg: 0 16rpx 48rpx rgba(35,72,130,.12);
  --radius-lg:24rpx;
  --radius-md:16rpx;
  --radius-sm:12rpx;
}

.qe-page{
  min-height:100vh;
  background:linear-gradient(180deg,var(--c-bg-start),var(--c-bg-end));
  padding:32rpx 28rpx 140rpx;
}

.card{
  background:var(--c-card);
  border-radius:var(--radius-lg);
  box-shadow:var(--shadow-lg);
  overflow:hidden;
}

/* ========== 头部 ========== */
.header{
  background:linear-gradient(135deg, #66b4ff 0%, #4a9fff 100%);
  padding:40rpx 32rpx 36rpx;
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
.title{
  display:flex;
  align-items:center;
  gap:12rpx;
  font-size:40rpx;
  font-weight:700;
  color:#fff;
  margin-bottom:12rpx;
}
.icon{
  font-size:44rpx;
}
.subtitle{
  font-size:26rpx;
  color:rgba(255,255,255,0.85);
  margin-left:56rpx;
}

/* ========== 表单 ========== */
.form{
  padding:32rpx;
  display:flex;
  flex-direction:column;
  gap:28rpx;
}

.field-group{
  display:flex;
  flex-direction:column;
  gap:16rpx;
}

.label{
  display:flex;
  align-items:center;
  gap:8rpx;
  font-size:28rpx;
  font-weight:600;
  color:var(--c-text);
}
.label-icon{
  font-size:32rpx;
}
.required{
  color:var(--c-danger);
  font-size:28rpx;
  margin-left:4rpx;
}

.ipt{
  width:100%;
  padding:24rpx 20rpx;
  font-size:30rpx;
  color:var(--c-text);
  background:#f7f9fc;
  border:2rpx solid var(--c-border);
  border-radius:var(--radius-sm);
  transition:all 0.3s;
}
.ipt:focus{
  background:#fff;
  border-color:var(--c-primary);
  box-shadow:0 0 0 6rpx var(--c-primary-light);
}
.area{
  min-height:180rpx;
  line-height:1.6;
}

/* ========== 选项卡片 ========== */
.opts{
  display:flex;
  flex-direction:column;
  gap:16rpx;
}
.opt-card{
  background:#f7f9fc;
  border:2rpx solid var(--c-border);
  border-radius:var(--radius-md);
  padding:20rpx;
  transition:all 0.3s;
}
.opt-card:active{
  transform:scale(0.99);
}
.opt-header{
  display:flex;
  align-items:center;
  gap:16rpx;
  margin-bottom:16rpx;
}
.opt-key-badge{
  width:56rpx;
  height:56rpx;
  border-radius:50%;
  background:linear-gradient(135deg, var(--c-primary) 0%, #4a9fff 100%);
  color:#fff;
  font-size:28rpx;
  font-weight:700;
  display:flex;
  align-items:center;
  justify-content:center;
  flex-shrink:0;
}
.opt-input{
  flex:1;
  padding:16rpx 18rpx;
  font-size:28rpx;
  background:#fff;
  border:2rpx solid #e8eef5;
  border-radius:var(--radius-sm);
}
.opt-actions{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:16rpx;
}
.correct-label{
  display:flex;
  align-items:center;
  gap:10rpx;
  padding:10rpx 18rpx;
  background:#fff;
  border:2rpx solid var(--c-border);
  border-radius:var(--radius-sm);
  font-size:26rpx;
  color:var(--c-text-light);
  transition:all 0.3s;
}
.correct-label.active{
  background:var(--c-primary-light);
  border-color:var(--c-primary);
  color:var(--c-primary);
  font-weight:600;
}
.mini-btn{
  padding:10rpx 18rpx;
  border-radius:var(--radius-sm);
  font-size:24rpx;
  border:2rpx solid var(--c-border);
  background:#fff;
  display:flex;
  align-items:center;
  gap:6rpx;
}
.mini-btn.danger{
  border-color:#ffccc7;
  color:var(--c-danger);
}
.mini-btn.danger:active{
  background:var(--c-danger-light);
}
.btn-icon{
  font-size:26rpx;
}

.add-opt-btn{
  width:100%;
  padding:24rpx;
  background:#fff;
  border:2rpx dashed var(--c-primary);
  border-radius:var(--radius-md);
  color:var(--c-primary);
  font-size:28rpx;
  font-weight:600;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:10rpx;
  transition:all 0.3s;
}
.add-opt-btn:active{
  background:var(--c-primary-light);
}
.plus-icon{
  font-size:36rpx;
  font-weight:700;
}

/* ========== 状态栏 ========== */
.status-bar{
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:24rpx;
  background:#f7f9fc;
  border-radius:var(--radius-md);
}
.label-with-icon{
  display:flex;
  align-items:center;
  gap:10rpx;
}
.status-switch{
  display:flex;
  align-items:center;
  gap:14rpx;
}
.status-text{
  font-size:28rpx;
  color:var(--c-text-muted);
  font-weight:600;
  transition:color 0.3s;
}
.status-text.active{
  color:var(--c-success);
}

/* ========== 标签行 ========== */
.tag-row{
  display:flex;
  gap:16rpx;
}
.tag-item{
  flex:1;
  display:flex;
  flex-direction:column;
  gap:12rpx;
}
.tag-label{
  font-size:24rpx;
  color:var(--c-text-light);
  padding-left:4rpx;
}
.tag-picker{
  width:100%;
}
.tag-value{
  padding:20rpx 18rpx;
  background:#f7f9fc;
  border:2rpx solid var(--c-border);
  border-radius:var(--radius-sm);
  color:var(--c-text);
  font-size:28rpx;
  transition:all 0.3s;
}
.tag-picker:active .tag-value{
  background:#fff;
  border-color:var(--c-primary);
}

/* ========== 知识点 ========== */
.kp-group{
  background:linear-gradient(to bottom, #f7f9fc 0%, #fff 100%);
  border-radius:var(--radius-md);
  padding:24rpx;
  border:2rpx solid var(--c-border);
}
.label-row{
  display:flex;
  align-items:center;
  justify-content:space-between;
  margin-bottom:16rpx;
}
.kp-count{
  padding:6rpx 16rpx;
  background:var(--c-primary-light);
  color:var(--c-primary);
  font-size:24rpx;
  font-weight:600;
  border-radius:999rpx;
}

.selected-kp{
  margin-bottom:16rpx;
}
.empty-state{
  text-align:center;
  padding:40rpx 0;
  color:var(--c-text-muted);
}
.empty-icon{
  font-size:64rpx;
  display:block;
  margin-bottom:12rpx;
}
.empty-text{
  font-size:26rpx;
}

.kp-chips{
  display:flex;
  flex-wrap:wrap;
  gap:12rpx;
}
.kp-chip{
  display:inline-flex;
  align-items:center;
  gap:8rpx;
  padding:12rpx 18rpx;
  background:linear-gradient(135deg, var(--c-primary-light) 0%, #d6ebff 100%);
  border:2rpx solid var(--c-primary);
  border-radius:999rpx;
  font-size:24rpx;
  color:var(--c-primary);
  font-weight:600;
  transition:all 0.3s;
}
.chip-text{
  max-width:400rpx;
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
}
.chip-close{
  width:32rpx;
  height:32rpx;
  border-radius:50%;
  background:var(--c-primary);
  color:#fff;
  font-size:28rpx;
  font-weight:700;
  display:flex;
  align-items:center;
  justify-content:center;
  margin-left:4rpx;
}
.chip-close:active{
  opacity:0.7;
}

.search-box{
  display:flex;
  align-items:center;
  gap:12rpx;
  padding:18rpx 20rpx;
  background:#fff;
  border:2rpx solid var(--c-border);
  border-radius:var(--radius-sm);
  margin-bottom:16rpx;
}
.search-icon{
  font-size:32rpx;
  color:var(--c-text-muted);
}
.search-input{
  flex:1;
  font-size:28rpx;
  color:var(--c-text);
}

.kp-selector{
  background:#fff;
  border:2rpx solid var(--c-border);
  border-radius:var(--radius-sm);
  overflow:hidden;
}
.kp-scroll{
  max-height:480rpx;
}
.kp-option{
  display:flex;
  align-items:center;
  gap:16rpx;
  padding:20rpx 18rpx;
  border-bottom:1rpx solid #f0f2f5;
  transition:background 0.2s;
}
.kp-option:last-child{
  border-bottom:none;
}
.kp-option:active{
  background:#f7f9fc;
}
.kp-option.checked{
  background:var(--c-primary-light);
}
.kp-name{
  flex:1;
  font-size:26rpx;
  color:var(--c-text);
  line-height:1.5;
}
.no-result{
  text-align:center;
  padding:60rpx 0;
  color:var(--c-text-muted);
  font-size:26rpx;
}

/* ========== 操作按钮 ========== */
.btn-group{
  display:flex;
  flex-direction:column;
  gap:16rpx;
  margin-top:12rpx;
}
.action-btn{
  width:100%;
  padding:28rpx 0;
  border-radius:var(--radius-md);
  font-size:32rpx;
  font-weight:600;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:10rpx;
  border:none;
  box-shadow:var(--shadow-sm);
  transition:all 0.3s;
}
.action-btn.primary{
  background:linear-gradient(135deg, var(--c-primary) 0%, #4a9fff 100%);
  color:#fff;
}
.action-btn.primary:active:not([disabled]){
  box-shadow:var(--shadow-md);
  transform:translateY(-2rpx);
}
.action-btn.primary[disabled]{
  opacity:0.6;
}
.action-btn.ghost{
  background:#f7f9fc;
  color:var(--c-text-light);
  border:2rpx solid var(--c-border);
}
.action-btn.ghost:active{
  background:#eef3f7;
}

button::after{
  border:none;
}
</style>