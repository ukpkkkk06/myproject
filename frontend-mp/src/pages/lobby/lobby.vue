<template>
  <view class="lobby-page">
    <!-- 优化导航栏 -->
    <view class="nav">
      <text class="nav-title">🏠 学习大厅</text>
      <view class="nav-badge">Ready</view>
    </view>

    <view class="content">
      <!-- 欢迎卡片 -->
      <view class="welcome-card">
        <text class="welcome-icon">👋</text>
        <text class="welcome-text">欢迎回来，开始今天的学习吧！</text>
      </view>

      <view class="panel">
        <view class="panel-head">
          <text class="panel-title">📚 功能中心</text>
          <text class="panel-sub">选择你要进行的操作</text>
        </view>

        <!-- 学科选择卡片 -->
        <view class="select-card">
          <view class="select-header">
            <text class="select-icon">🎯</text>
            <text class="select-label">选择学科</text>
          </view>
          <picker mode="selector" :range="names" @change="onPickSubject">
            <view class="picker">
              <text class="picker-text">{{ names[subjectIdx+1] || '全部学科' }}</text>
              <text class="picker-arrow">▼</text>
            </view>
          </picker>
        </view>

        <!-- 知识点选择卡片 -->
        <view class="select-card">
          <view class="select-header">
            <text class="select-icon">🌲</text>
            <text class="select-label">选择知识点</text>
          </view>
          <picker mode="selector" :range="kpNames" @change="onPickKp">
            <view class="picker">
              <text class="picker-text">{{ kpNames[kpIdx+1] || '全部知识点' }}</text>
              <text class="picker-arrow">▼</text>
            </view>
          </picker>
          
          <!-- 子知识点开关 -->
          <view class="kp-switch">
            <text class="switch-label">包含子知识点</text>
            <switch 
              :checked="includeChildren" 
              @change="onToggleChildren"
              color="#66b4ff"
            />
          </view>
        </view>

        <!-- 🆕 题型选择卡片 -->
        <view class="select-card">
          <view class="select-header">
            <text class="select-icon">📋</text>
            <text class="select-label">题型筛选</text>
          </view>
          <view class="type-options">
            <view 
              class="type-option" 
              :class="{ active: questionTypes.includes('SC') }"
              @tap="toggleType('SC')"
            >
              <text class="type-icon">○</text>
              <text>单选题</text>
            </view>
            <view 
              class="type-option" 
              :class="{ active: questionTypes.includes('MC') }"
              @tap="toggleType('MC')"
            >
              <text class="type-icon">☑</text>
              <text>多选题</text>
            </view>
            <view 
              class="type-option" 
              :class="{ active: questionTypes.includes('FILL') }"
              @tap="toggleType('FILL')"
            >
              <text class="type-icon">___</text>
              <text>填空题</text>
            </view>
          </view>
        </view>

        <!-- 功能按钮网格 -->
        <view class="action-grid">
          <button class="action-btn primary" @tap="startPractice">
            <text class="action-icon">✏️</text>
            <text class="action-text">开始刷题</text>
            <text class="action-desc">智能练习</text>
          </button>
          
          <button class="action-btn secondary" @tap="goQuestionBank">
            <text class="action-icon">📖</text>
            <text class="action-text">我的题库</text>
            <text class="action-desc">题目管理</text>
          </button>
          
          <button class="action-btn accent" @tap="goErrorBook">
            <text class="action-icon">📝</text>
            <text class="action-text">错题本</text>
            <text class="action-desc">巩固薄弱</text>
          </button>
          
          <button class="action-btn info" @tap="goProfile">
            <text class="action-icon">👤</text>
            <text class="action-text">个人中心</text>
            <text class="action-desc">账号设置</text>
          </button>
        </view>

        <!-- 退出按钮 -->
        <button class="btn danger fullW logout" @tap="logout">
          <text class="logout-icon">🚪</text>
          <text>退出登录</text>
        </button>
      </view>

      <!-- 底部装饰 -->
      <view class="footer-deco">
        <text class="deco-text">© 2025 学习助手</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api, type KnowledgeNode } from '@/utils/api'

/* 学科 */
const subjects = ref<{id:number;name:string}[]>([])
const subjectIdx = ref(-1)
const names = computed(()=> ['全部学科', ...subjects.value.map(s=>s.name)])
function onPickSubject(e:any){ subjectIdx.value = Number(e.detail.value) - 1 }

/* 知识点 */
const kpTree = ref<KnowledgeNode[]>([])
type KpOpt = { id:number; label:string }
const kpOptions = ref<KpOpt[]>([])
const kpIdx = ref(-1)
const kpNames = computed(()=> ['全部知识点', ...kpOptions.value.map(o=>o.label)])
function onPickKp(e:any){ kpIdx.value = Number(e.detail.value) - 1 }
const includeChildren = ref(true)
function onToggleChildren(e:any){ includeChildren.value = !!e.detail.value }

/* 🆕 题型筛选 */
const questionTypes = ref<string[]>(['SC', 'MC', 'FILL'])  // 🆕 默认全选,包含填空题
function toggleType(type: string) {
  const idx = questionTypes.value.indexOf(type)
  if (idx >= 0) {
    // 取消选择(但至少保留一个)
    if (questionTypes.value.length > 1) {
      questionTypes.value.splice(idx, 1)
    }
  } else {
    // 添加选择
    questionTypes.value.push(type)
  }
}

/* 扁平化知识点树为"路径"便于选择 */
function flattenKp(nodes: KnowledgeNode[], prefix = ''): KpOpt[] {
  const out: KpOpt[] = []
  for (const n of nodes || []) {
    const label = prefix ? `${prefix}/${n.name}` : n.name
    out.push({ id: n.id, label })
    if (n.children && n.children.length) {
      out.push(...flattenKp(n.children, label))
    }
  }
  return out
}

onMounted(async ()=>{
  try { subjects.value = await api.listSubjects() } catch { subjects.value = [] }
  try {
    kpTree.value = await api.listKnowledgeTree()
    kpOptions.value = flattenKp(kpTree.value)
  } catch { kpTree.value = []; kpOptions.value = [] }
})

async function startPractice(){
  const selSubject = subjectIdx.value>=0 ? subjects.value[subjectIdx.value] : null
  const subjectId = selSubject?.id

  const selKp = kpIdx.value>=0 ? kpOptions.value[kpIdx.value] : null
  const knowledgeId = selKp?.id

  try{
    const r = await api.createPractice(5, subjectId, knowledgeId, includeChildren.value, questionTypes.value)
    uni.navigateTo({ url: `/pages/practice/practice?attemptId=${r.attempt_id}&total=${r.total}&seq=${r.start_seq ?? r.first_seq ?? 1}` })
  }catch(e:any){
    const msg = e?.data?.message || e?.data?.detail || '创建练习失败'
    uni.showToast({ icon:'none', title: msg })
  }
}

function goQuestionBank(){ uni.navigateTo({ url:'/pages/question-bank/question-bank' }) }
function goErrorBook(){ uni.navigateTo({ url:'/pages/error-book/error-book' }) }
function goProfile(){ uni.navigateTo({ url:'/pages/profile/profile' }) }
function logout(){
  uni.showModal({
    title:'确认退出',
    content:'确定要退出当前账号？',
    success(res){
      if(res.confirm){
        uni.removeStorageSync('token')
        uni.reLaunch({ url:'/pages/login/login' })
      }
    }
  })
}
</script>

<style scoped>
:root, page, .lobby-page {
  --c-bg-grad-top:#e8f2ff;
  --c-bg-grad-bottom:#f5f9ff;
  --c-panel:#ffffff;
  --c-border:#d8e6f5;
  --c-border-strong:#c6d9ec;
  --c-primary:#66b4ff;
  --c-primary-dark:#4b9ef0;
  --c-primary-light:#d4ecff;
  --c-secondary:#8dd3c7;
  --c-accent:#ffa366;
  --c-info:#9b9bff;
  --c-text:#1f2d3d;
  --c-text-sec:#5f7085;
  --c-danger:#ff4d4f;
  --c-danger-dark:#d73a3c;
  --radius:24rpx;
  --radius-s:16rpx;
  --shadow-sm:0 4rpx 12rpx rgba(35,72,130,.06);
  --shadow-md:0 8rpx 24rpx rgba(35,72,130,.08),0 2rpx 6rpx rgba(35,72,130,.06);
  --shadow-lg:0 12rpx 36rpx rgba(35,72,130,.12),0 4rpx 12rpx rgba(35,72,130,.08);
}

.lobby-page {
  min-height:100vh;
  background:linear-gradient(180deg,var(--c-bg-grad-top),var(--c-bg-grad-bottom));
  display:flex;
  flex-direction:column;
  box-sizing:border-box;
  padding-top:120rpx;
}

/* 🎨 优化导航栏 */
.nav {
  position:fixed;
  top:0; left:0; right:0;
  height:120rpx;
  padding:40rpx 40rpx 0;
  box-sizing:border-box;
  display:flex;
  justify-content:space-between;
  align-items:center;
  backdrop-filter:blur(20px) saturate(180%);
  background:rgba(255,255,255,0.65);
  border-bottom:1rpx solid rgba(214,230,245,0.6);
  box-shadow:var(--shadow-sm);
  z-index:10;
}

.nav-title {
  font-size:42rpx;
  font-weight:700;
  letter-spacing:1rpx;
  color:var(--c-text);
}

.nav-badge{
  padding:8rpx 20rpx;
  background:linear-gradient(135deg, var(--c-primary), var(--c-primary-dark));
  color:#fff;
  font-size:22rpx;
  font-weight:600;
  border-radius:20rpx;
  box-shadow:0 4rpx 12rpx rgba(102,180,255,.25);
}

.content {
  padding:40rpx 40rpx 120rpx;
  flex:1;
  display:flex;
  flex-direction:column;
  gap:32rpx;
  box-sizing:border-box;
}

/* 🎨 欢迎卡片 */
.welcome-card{
  background:linear-gradient(135deg, var(--c-primary-light), #e8f5ff);
  border:1rpx solid var(--c-primary);
  border-radius:var(--radius);
  padding:32rpx 40rpx;
  display:flex;
  align-items:center;
  gap:20rpx;
  box-shadow:var(--shadow-md);
  animation:slideInDown .5s ease;
}

@keyframes slideInDown{
  from{ opacity:0; transform:translateY(-20rpx); }
  to{ opacity:1; transform:translateY(0); }
}

.welcome-icon{
  font-size:48rpx;
  line-height:1;
}

.welcome-text{
  flex:1;
  font-size:28rpx;
  color:var(--c-primary-dark);
  font-weight:600;
}

/* 🎨 主面板 */
.panel {
  background:var(--c-panel);
  border:1rpx solid var(--c-border);
  border-radius:var(--radius);
  padding:48rpx 40rpx 56rpx;
  box-shadow:var(--shadow-md);
  display:flex;
  flex-direction:column;
  gap:40rpx;
  animation:fadeIn .5s ease .1s backwards;
}

@keyframes fadeIn{
  from{ opacity:0; transform:translateY(20rpx); }
  to{ opacity:1; transform:translateY(0); }
}

.panel-head { 
  display:flex; 
  flex-direction:column; 
  gap:12rpx; 
}

.panel-title { 
  font-size:40rpx; 
  font-weight:700; 
  color:var(--c-text);
  letter-spacing:.5rpx;
}

.panel-sub { 
  font-size:26rpx; 
  color:var(--c-text-sec); 
  font-weight:500;
}

/* 🎨 选择卡片 */
.select-card{
  background:linear-gradient(135deg, #f8fafc, #fff);
  border:1rpx solid var(--c-border);
  border-radius:var(--radius-s);
  padding:28rpx 32rpx;
  display:flex;
  flex-direction:column;
  gap:20rpx;
  box-shadow:var(--shadow-sm);
  transition:all .25s ease;
}

.select-card:active{
  transform:translateY(2rpx);
  box-shadow:var(--shadow-md);
}

.select-header{
  display:flex;
  align-items:center;
  gap:12rpx;
}

.select-icon{
  font-size:36rpx;
  line-height:1;
}

.select-label{
  font-size:28rpx;
  font-weight:600;
  color:var(--c-text);
}

/* 🎨 选择器 */
.picker{ 
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:16rpx;
  padding:20rpx 24rpx; 
  background:#fff;
  border:2rpx solid var(--c-border);
  border-radius:var(--radius-s);
  box-shadow:var(--shadow-sm);
  transition:all .25s ease;
}

.picker:active{
  border-color:var(--c-primary);
  box-shadow:0 0 0 6rpx var(--c-primary-light);
  background:#fafcff;
}

.picker-text{
  flex:1;
  font-size:28rpx;
  color:var(--c-text);
  font-weight:500;
}

.picker-arrow{
  font-size:20rpx;
  color:var(--c-text-sec);
  transition:transform .25s ease;
}

.picker:active .picker-arrow{
  transform:translateY(2rpx);
}

/* 🎨 开关 */
.kp-switch { 
  display:flex; 
  align-items:center; 
  justify-content:space-between;
  gap:16rpx; 
  padding:16rpx 24rpx;
  background:var(--c-primary-light);
  border-radius:var(--radius-s);
  margin-top:4rpx;
}

.switch-label{
  font-size:26rpx;
  color:var(--c-primary-dark);
  font-weight:600;
}

/* � 题型选择样式 */
.type-options{
  display:flex;
  gap:16rpx;
  margin-top:8rpx;
}

.type-option{
  flex:1;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:8rpx;
  padding:20rpx 16rpx;
  background:#fff;
  border:2rpx solid var(--c-border);
  border-radius:var(--radius-s);
  font-size:26rpx;
  color:var(--c-text-sec);
  font-weight:500;
  transition:all .25s ease;
  cursor:pointer;
}

.type-option.active{
  background:linear-gradient(135deg, var(--c-primary-light), #e8f5ff);
  border-color:var(--c-primary);
  color:var(--c-primary-dark);
  font-weight:700;
  box-shadow:0 4rpx 12rpx rgba(102,180,255,.2);
}

.type-option:active{
  transform:scale(.95);
}

.type-icon{
  font-size:28rpx;
  line-height:1;
}

/* �🎨 功能按钮网格 - 优化版 */
.action-grid{
  display:grid;
  grid-template-columns:repeat(2, 1fr);  /* 始终 2 列 */
  grid-template-rows:repeat(2, 1fr);     /* 🔥 新增：始终 2 行 */
  gap:24rpx;
}

.action-btn{
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  gap:12rpx;
  padding:40rpx 20rpx;
  min-height:240rpx;
  aspect-ratio:1;  /* 🔥 新增：保持正方形比例 */
  border:2rpx solid transparent;
  border-radius:var(--radius);
  box-shadow:var(--shadow-md);
  transition:all .25s ease;
  position:relative;
  overflow:hidden;
}

.action-btn::before{
  content:'';
  position:absolute;
  top:0; left:0; right:0; bottom:0;
  background:linear-gradient(135deg, rgba(255,255,255,.2), transparent);
  opacity:0;
  transition:opacity .25s ease;
}

.action-btn:active::before{
  opacity:1;
}

.action-btn:active{
  transform:translateY(2rpx) scale(.98);
  box-shadow:var(--shadow-lg);
}

.action-btn.primary{
  background:linear-gradient(135deg, var(--c-primary), var(--c-primary-dark));
  border-color:var(--c-primary);
}

.action-btn.secondary{
  background:linear-gradient(135deg, var(--c-secondary), #6fc4b9);
  border-color:var(--c-secondary);
}

.action-btn.accent{
  background:linear-gradient(135deg, var(--c-accent), #ff8a4d);
  border-color:var(--c-accent);
}

.action-btn.info{
  background:linear-gradient(135deg, var(--c-info), #7a7aff);
  border-color:var(--c-info);
}

.action-icon{
  font-size:52rpx;
  line-height:1;
  filter:drop-shadow(0 4rpx 8rpx rgba(0,0,0,.15));
}

.action-text{
  font-size:30rpx;
  font-weight:700;
  color:#fff;
  letter-spacing:.5rpx;
}

.action-desc{
  font-size:22rpx;
  color:rgba(255,255,255,.85);
  font-weight:500;
}

/* 🎨 退出按钮 */
.btn {
  display:flex;
  align-items:center;
  justify-content:center;
  gap:12rpx;
  border:2rpx solid transparent;
  border-radius:var(--radius-s);
  font-size:30rpx;
  font-weight:600;
  letter-spacing:1rpx;
  padding:28rpx 0;
  color:#fff;
  background:#ccc;
  box-shadow:var(--shadow-md);
  transition:all .25s ease;
}

.btn:active { 
  opacity:.9; 
  transform:translateY(2rpx);
  box-shadow:var(--shadow-lg);
}

.btn.danger {
  background:linear-gradient(135deg,var(--c-danger),var(--c-danger-dark));
  border-color:var(--c-danger);
}

.fullW { width:100%; }

.logout { 
  margin-top:8rpx; 
  position:relative;
  overflow:hidden;
}

.logout::before{
  content:'';
  position:absolute;
  top:0; left:0; right:0; bottom:0;
  background:linear-gradient(135deg, rgba(255,255,255,.15), transparent);
  opacity:0;
  transition:opacity .25s ease;
}

.logout:active::before{
  opacity:1;
}

.logout-icon{
  font-size:32rpx;
}

.btn[disabled]{ opacity:.55; }

button::after{ border:none; }

/* 🎨 底部装饰 */
.footer-deco{
  text-align:center;
  padding:40rpx 0 20rpx;
}

.deco-text{
  font-size:24rpx;
  color:var(--c-text-sec);
  opacity:.6;
}

/* 响应式 */
@media (min-width:700rpx){
  .panel { max-width:680rpx; margin:0 auto; }
  .welcome-card { max-width:680rpx; margin:0 auto; width:100%; }
  /* 🔥 宽屏下也保持 2x2 */
  .action-grid{
    grid-template-columns:repeat(2, 1fr);
  }
}

@media (min-width:900rpx){
  .action-grid{
    grid-template-columns:repeat(4, 1fr);
  }
}
</style>