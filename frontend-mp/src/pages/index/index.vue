<template>
  <view class="admin-page">
    <!-- 自定义安全区导航 -->
    <view class="safe-nav">
      <text class="nav-title">管理员后台</text>
      <view class="nav-badge">Admin</view>
    </view>

    <!-- 主体 -->
    <view class="body" v-if="ready">
      <!-- 健康状态卡片 - 添加图标和动画 -->
      <view class="card health-card">
        <view class="card-header">
          <view class="card-title-wrap">
            <text class="card-icon">🏥</text>
            <text class="card-title">系统健康状态</text>
          </view>
          <view class="status-badge" :class="{ 
            online: health.status === 'healthy', 
            warning: health.status === 'warning',
            error: health.status === 'unhealthy' 
          }">
            {{ getStatusText(health.status) }}
          </view>
        </view>
        
        <!-- 健康检查详情 -->
        <view class="health-checks" v-if="health.checks">
          <!-- 数据库状态 -->
          <view class="check-item" v-if="health.checks.database">
            <view class="check-header">
              <text class="check-icon">{{ getCheckIcon(health.checks.database.status) }}</text>
              <text class="check-name">数据库</text>
              <view class="check-status" :class="getCheckStatusClass(health.checks.database.status)">
                {{ getCheckStatusText(health.checks.database.status) }}
              </view>
            </view>
            <text class="check-message">{{ health.checks.database.message }}</text>
          </view>
          
          <!-- 系统状态 -->
          <view class="check-item" v-if="health.checks.system">
            <view class="check-header">
              <text class="check-icon">{{ getCheckIcon(health.checks.system.status) }}</text>
              <text class="check-name">系统资源</text>
              <view class="check-status" :class="getCheckStatusClass(health.checks.system.status)">
                {{ getCheckStatusText(health.checks.system.status) }}
              </view>
            </view>
            <text class="check-message">{{ health.checks.system.message }}</text>
            
            <!-- 系统详情（CPU、内存） -->
            <view class="system-details" v-if="health.checks.system.details">
              <view class="detail-item">
                <text class="detail-label">CPU使用率</text>
                <view class="progress-bar">
                  <view class="progress-fill cpu" :style="{ width: health.checks.system.details.cpu_percent + '%' }"></view>
                </view>
                <text class="detail-value">{{ health.checks.system.details.cpu_percent }}%</text>
              </view>
              <view class="detail-item">
                <text class="detail-label">内存使用率</text>
                <view class="progress-bar">
                  <view class="progress-fill memory" :style="{ width: health.checks.system.details.memory_percent + '%' }"></view>
                </view>
                <text class="detail-value">{{ health.checks.system.details.memory_percent }}%</text>
              </view>
            </view>
          </view>
        </view>
        
        <!-- 更新时间 -->
        <view class="health-footer" v-if="health.timestamp">
          <text class="update-time">🕐 更新时间: {{ formatTimestamp(health.timestamp) }}</text>
        </view>
      </view>

      <!-- 用户管理卡片 -->
      <view class="card user-card">
        <view class="card-header">
          <view class="card-title-wrap">
            <text class="card-icon">👥</text>
            <text class="card-title small">用户管理</text>
          </view>
          <text class="total-badge">共 {{ total }} 人</text>
        </view>

        <!-- 筛选区 - 优化布局 -->
        <view class="filters">
          <view class="filter-group">
            <text class="filter-label">账号</text>
            <input
              class="ipt"
              v-model="account"
              placeholder="输入账号关键词"
              placeholder-class="ph"
              @confirm="onSearch"
            />
          </view>
          <view class="filter-group">
            <text class="filter-label">邮箱</text>
            <input
              class="ipt"
              v-model="email"
              placeholder="输入邮箱关键词"
              placeholder-class="ph"
              @confirm="onSearch"
            />
          </view>
          <button class="btn primary search" :disabled="loading" @tap="onSearch">
            <text v-if="!loading">🔍 搜索</text>
            <text v-else>搜索中…</text>
          </button>
        </view>

        <!-- 用户列表 - 优化卡片式布局 -->
        <view class="list">
          <view v-for="u in items" :key="u.id" class="user-item">
            <view class="user-avatar">{{ u.account.charAt(0).toUpperCase() }}</view>
            <view class="user-info">
              <text class="user-name">{{ u.account }}</text>
              <text class="user-role">{{ u.role || '普通用户' }}</text>
            </view>
            <button class="view-btn" @tap="openDetail(u)">
              <text>查看详情</text>
              <text class="arrow">→</text>
            </button>
          </view>
          <view v-if="!loading && items.length===0" class="empty">
            <text class="empty-icon">📭</text>
            <text class="empty-text">暂无用户数据</text>
          </view>
        </view>

        <!-- 分页控件 - 优化样式 -->
        <view class="pager" v-if="total > 0">
          <button class="pg-btn" :disabled="page<=1 || loading" @tap="goPrev">
            <text class="pg-arrow">←</text>
            <text>上一页</text>
          </button>
          <view class="pg-info-wrap">
            <text class="pg-current">{{ page }}</text>
            <text class="pg-sep">/</text>
            <text class="pg-total">{{ totalPages }}</text>
          </view>
          <button class="pg-btn" :disabled="page>=totalPages || loading" @tap="goNext">
            <text>下一页</text>
            <text class="pg-arrow">→</text>
          </button>
        </view>
      </view>

      <!-- 操作区 - 添加更多功能入口 -->
      <view class="card actions-card">
        <view class="action-grid">
          <button class="action-item" @tap="showStats">
            <text class="action-icon">📊</text>
            <text class="action-text">数据统计</text>
          </button>
          <button class="action-item" @tap="showSettings">
            <text class="action-icon">⚙️</text>
            <text class="action-text">系统设置</text>
          </button>
          <button class="action-item" @tap="showLogs">
            <text class="action-icon">📝</text>
            <text class="action-text">操作日志</text>
          </button>
        </view>
        <button class="btn danger wide logout-btn" @tap="logout">
          <text>🚪 退出登录</text>
        </button>
      </view>
    </view>

    <!-- 加载占位 -->
    <view v-else class="boot">
      <view class="loader"></view>
      <text class="boot-text">加载中…</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { api, type UserSimple, adminGetStats } from '@/utils/api'

const health = ref<any>({})
const items = ref<UserSimple[]>([])
const total = ref(0)
let healthCheckTimer: number | null = null

const account = ref('')
const email = ref('')

const page = ref(1)
const limit = ref(5)
const loading = ref(false)
const ready = ref(false)

const totalPages = computed(()=> Math.max(1, Math.ceil((total.value || 0) / limit.value)))

async function load(p = page.value){
  if(loading.value) return
  loading.value = true
  try{
    const offset = (p - 1) * limit.value
    const rsp = await api.usersSimple(offset, limit.value, account.value, email.value)
    items.value = rsp.items ?? []
    total.value = rsp.total ?? items.value.length
    page.value = p
  } catch(e:any){
    uni.showToast({ icon:'none', title: e?.data?.message || '加载失败' })
  } finally { loading.value=false }
}

function onSearch(){ load(1) }
function goPrev(){ if(page.value>1) load(page.value-1) }
function goNext(){ if(page.value<totalPages.value) load(page.value+1) }

function logout(){
  uni.removeStorageSync('token')
  uni.reLaunch({ url:'/pages/login/login' })
}

// 📊 数据统计
async function showStats() {
  uni.showLoading({ title: '加载中...' })
  
  try {
    const stats = await adminGetStats()
    
    const statsInfo = `
📊 系统数据统计

👥 用户总数: ${stats.users.total} 人
📝 题目总数: ${stats.questions.total} 题
🌳 知识点数: ${stats.knowledge.total} 个

📄 当前页码: ${page.value}/${totalPages.value}
✅ 系统状态: ${getStatusText(health.value.status)}
${health.value.checks?.system?.details ? 
`
💻 CPU使用: ${health.value.checks.system.details.cpu_percent}%
🧠 内存使用: ${health.value.checks.system.details.memory_percent}%` : ''}
    `.trim()
    
    uni.hideLoading()
    uni.showModal({
      title: '数据统计',
      content: statsInfo,
      showCancel: false,
      confirmText: '知道了'
    })
  } catch (e: any) {
    uni.hideLoading()
    uni.showToast({ 
      icon: 'none', 
      title: e?.data?.message || '获取统计数据失败' 
    })
  }
}

// ⚙️ 系统设置
function showSettings() {
  uni.showActionSheet({
    itemList: ['刷新健康状态', '清空筛选条件', '重新加载用户列表'],
    success: (res) => {
      if (res.tapIndex === 0) {
        // 刷新健康状态
        fetchHealth()
        uni.showToast({ icon: 'success', title: '已刷新' })
      } else if (res.tapIndex === 1) {
        // 清空筛选
        account.value = ''
        email.value = ''
        load(1)
        uni.showToast({ icon: 'success', title: '已清空' })
      } else if (res.tapIndex === 2) {
        // 重新加载
        load(page.value)
        uni.showToast({ icon: 'success', title: '已重载' })
      }
    }
  })
}

// 📝 操作日志
function showLogs() {
  const now = new Date()
  const timestamp = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
  
  const logInfo = `
📝 最近操作记录

🕐 ${timestamp}
👤 当前用户: 管理员
📄 当前页面: 管理员后台
🔍 筛选条件:
   账号: ${account.value || '无'}
   邮箱: ${email.value || '无'}
📊 数据状态:
   用户总数: ${total.value}
   当前页: ${page.value}/${totalPages.value}
   加载状态: ${loading.value ? '加载中' : '已完成'}

💡 提示: 完整的操作日志功能开发中...
  `.trim()
  
  uni.showModal({
    title: '操作日志',
    content: logInfo,
    showCancel: false,
    confirmText: '知道了'
  })
}

async function guardAdmin(){
  const token = uni.getStorageSync('token')
  if(!token){ uni.reLaunch({ url:'/pages/login/login' }); return false }
  try{
    const me = await api.me()
    if(!me.is_admin){
      uni.showToast({ icon:'none', title:'无权访问' })
      setTimeout(()=> uni.reLaunch({ url:'/pages/lobby/lobby' }), 600)
      return false
    }
    return true
  }catch{
    uni.removeStorageSync('token')
    uni.reLaunch({ url:'/pages/login/login' })
    return false
  }
}

// 🎨 健康状态显示辅助函数
function getStatusText(status: string) {
  const map: Record<string, string> = {
    'healthy': '✅ 正常运行',
    'warning': '⚠️ 有警告',
    'unhealthy': '❌ 异常',
    'ok': '✅ 正常'
  }
  return map[status] || '未知'
}

function getCheckIcon(status: string) {
  const map: Record<string, string> = {
    'healthy': '✅',
    'warning': '⚠️',
    'unhealthy': '❌'
  }
  return map[status] || '❓'
}

function getCheckStatusText(status: string) {
  const map: Record<string, string> = {
    'healthy': '健康',
    'warning': '警告',
    'unhealthy': '异常'
  }
  return map[status] || '未知'
}

function getCheckStatusClass(status: string) {
  return status === 'healthy' ? 'status-healthy' : 
         status === 'warning' ? 'status-warning' : 
         'status-error'
}

function formatTimestamp(timestamp: string) {
  try {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000)
    
    if (diff < 60) return `${diff}秒前`
    if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
    if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
    
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return timestamp
  }
}

function openDetail(u: UserSimple){
  uni.navigateTo({ url: `/pages/user-detail/user-detail?uid=${u.id}` })
}

// 获取健康状态
async function fetchHealth() {
  try { 
    health.value = await api.health() 
  } catch (e) {
    console.error('获取健康状态失败:', e)
  }
}

// 启动定时健康检查（每30秒）
function startHealthCheck() {
  // 立即执行一次
  fetchHealth()
  
  // 每30秒自动刷新
  healthCheckTimer = setInterval(() => {
    fetchHealth()
  }, 30000) as unknown as number
}

// 停止定时检查
function stopHealthCheck() {
  if (healthCheckTimer) {
    clearInterval(healthCheckTimer)
    healthCheckTimer = null
  }
}

onMounted(async ()=>{
  if(!(await guardAdmin())) return
  startHealthCheck() // 启动健康检查定时器
  ready.value = true
  load(1)
})

onUnmounted(() => {
  stopHealthCheck() // 清理定时器
})
</script>

<style scoped>
:root, page, .admin-page {
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
  --c-danger-dark:#d73a3c;
  --c-success:#38b26f;
  --radius:24rpx;
  --radius-s:16rpx;
  --shadow-sm:0 4rpx 12rpx rgba(35,72,130,.06);
  --shadow-md:0 8rpx 24rpx rgba(35,72,130,.08),0 2rpx 6rpx rgba(35,72,130,.06);
  --shadow-lg:0 12rpx 36rpx rgba(35,72,130,.12),0 4rpx 12rpx rgba(35,72,130,.08);
}

.admin-page{
  min-height:100vh;
  background:linear-gradient(180deg,var(--c-bg-grad-top),var(--c-bg-grad-bottom));
  display:flex;
  flex-direction:column;
}

/* 🎨 优化导航栏 */
.safe-nav{
  position:fixed;
  top:0; left:0; right:0;
  padding-top:env(safe-area-inset-top);
  padding-top:constant(safe-area-inset-top);
  height:calc(env(safe-area-inset-top) + 100rpx);
  height:calc(constant(safe-area-inset-top) + 100rpx);
  box-sizing:border-box;
  display:flex;
  align-items:flex-end;
  justify-content:space-between;
  padding:0 40rpx 20rpx;
  background:rgba(255,255,255,.65);
  backdrop-filter:blur(20px) saturate(180%);
  border-bottom:1rpx solid rgba(214,230,245,.6);
  box-shadow:var(--shadow-sm);
  z-index:10;
}
.nav-title{
  font-size:42rpx;
  font-weight:700;
  color:var(--c-text);
  letter-spacing:1rpx;
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

.body{
  padding:calc(env(safe-area-inset-top) + 120rpx) 40rpx 140rpx;
  display:flex;
  flex-direction:column;
  gap:40rpx;
  box-sizing:border-box;
}

/* 🎨 优化卡片样式 */
.card{
  background:var(--c-panel);
  border:1rpx solid var(--c-border);
  border-radius:var(--radius);
  padding:40rpx;
  box-shadow:var(--shadow-md);
  display:flex;
  flex-direction:column;
  gap:32rpx;
  transition:box-shadow .3s ease, transform .3s ease;
}
.card:active{
  transform:translateY(2rpx);
}

/* 🎨 卡片头部 */
.card-header{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:20rpx;
}
.card-title-wrap{
  display:flex;
  align-items:center;
  gap:16rpx;
}
.card-icon{
  font-size:44rpx;
  line-height:1;
}
.card-title{
  font-size:38rpx;
  font-weight:700;
  color:var(--c-text);
  letter-spacing:.5rpx;
}
.card-title.small{ font-size:36rpx; }

/* 🎨 状态徽章 */
.status-badge{
  padding:10rpx 24rpx;
  background:#f0f2f5;
  color:var(--c-text-sec);
  font-size:24rpx;
  font-weight:600;
  border-radius:30rpx;
  transition:all .3s ease;
}
.status-badge.online{
  background:linear-gradient(135deg, #d4f5e7, #b8eed5);
  color:var(--c-success);
  box-shadow:0 4rpx 12rpx rgba(56,178,111,.15);
}
.status-badge.warning{
  background:linear-gradient(135deg, #fef3c7, #fde68a);
  color:#b45309;
  box-shadow:0 4rpx 12rpx rgba(180,83,9,.15);
}
.status-badge.error{
  background:linear-gradient(135deg, #fee2e2, #fecaca);
  color:#dc2626;
  box-shadow:0 4rpx 12rpx rgba(220,38,38,.15);
}

.total-badge{
  padding:10rpx 24rpx;
  background:var(--c-primary-light);
  color:var(--c-primary-dark);
  font-size:24rpx;
  font-weight:600;
  border-radius:30rpx;
}

/* 🎨 健康状态 */
.health-checks {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  margin-top: 20rpx;
}

.check-item {
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
  padding: 28rpx;
  border-radius: 20rpx;
  border: 1rpx solid rgba(216,230,245,.8);
  transition: all .3s ease;
}

.check-item:active {
  transform: scale(0.98);
}

.check-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 16rpx;
}

.check-icon {
  font-size: 36rpx;
}

.check-name {
  flex: 1;
  font-size: 30rpx;
  font-weight: 600;
  color: #1e293b;
}

.check-status {
  padding: 8rpx 20rpx;
  border-radius: 30rpx;
  font-size: 24rpx;
  font-weight: 500;
}

.status-healthy {
  background: #dcfce7;
  color: #15803d;
}

.status-warning {
  background: #fef3c7;
  color: #b45309;
}

.status-error {
  background: #fee2e2;
  color: #dc2626;
}

.check-message {
  font-size: 26rpx;
  color: #64748b;
  line-height: 1.5;
  display: block;
}

/* 系统详情 */
.system-details {
  margin-top: 24rpx;
  padding-top: 24rpx;
  border-top: 1rpx solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.detail-label {
  font-size: 26rpx;
  color: #475569;
  min-width: 140rpx;
}

.progress-bar {
  flex: 1;
  height: 16rpx;
  background: #e2e8f0;
  border-radius: 8rpx;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  border-radius: 8rpx;
  transition: width .5s ease;
  position: relative;
}

.progress-fill.cpu {
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
}

.progress-fill.memory {
  background: linear-gradient(90deg, #8b5cf6, #a78bfa);
}

.detail-value {
  font-size: 26rpx;
  font-weight: 600;
  color: #1e293b;
  min-width: 80rpx;
  text-align: right;
}

/* 健康状态页脚 */
.health-footer {
  margin-top: 24rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid #e2e8f0;
}

.update-time {
  font-size: 24rpx;
  color: #94a3b8;
  display: block;
  text-align: center;
}
.kv:active{
  transform:scale(.98);
  box-shadow:var(--shadow-sm);
}
.k{
  color:var(--c-text-sec);
  font-weight:500;
}
.v{
  color:var(--c-text);
  font-weight:700;
}
.v.ok{
  color:var(--c-success);
  text-shadow:0 2rpx 8rpx rgba(56,178,111,.2);
}

/* 🎨 筛选区域 */
.filters{
  display:flex;
  flex-direction:column;
  gap:24rpx;
}
.filter-group{
  display:flex;
  flex-direction:column;
  gap:12rpx;
}
.filter-label{
  font-size:26rpx;
  color:var(--c-text-sec);
  font-weight:600;
  padding-left:4rpx;
}

.ipt{
  width:100%;
  height:88rpx;
  line-height:88rpx;
  padding:0 28rpx;
  font-size:30rpx;
  background:#fff;
  border:2rpx solid var(--c-border);
  border-radius:var(--radius-s);
  box-sizing:border-box;
  color:var(--c-text);
  transition:all .25s ease;
}
.ipt:focus{
  border-color:var(--c-primary);
  box-shadow:0 0 0 6rpx var(--c-primary-light);
  background:#fafcff;
}
.ph{
  color:#9ab2c7;
  font-size:28rpx;
}

/* 🎨 用户列表 - 卡片式 */
.list{
  display:flex;
  flex-direction:column;
  gap:20rpx;
}
.user-item{
  display:flex;
  align-items:center;
  gap:24rpx;
  padding:28rpx 32rpx;
  background:#fff;
  border:1rpx solid var(--c-border);
  border-radius:var(--radius-s);
  box-shadow:var(--shadow-sm);
  transition:all .25s ease;
}
.user-item:active{
  transform:translateY(2rpx);
  box-shadow:var(--shadow-md);
  border-color:var(--c-primary-light);
}

/* 🎨 用户头像 */
.user-avatar{
  width:80rpx;
  height:80rpx;
  border-radius:50%;
  background:linear-gradient(135deg, var(--c-primary-light), #e8f5ff);
  color:var(--c-primary-dark);
  font-size:32rpx;
  font-weight:700;
  display:flex;
  align-items:center;
  justify-content:center;
  flex-shrink:0;
  border:2rpx solid var(--c-primary);
  box-shadow:0 4rpx 12rpx rgba(102,180,255,.15);
}

.user-info{
  flex:1;
  display:flex;
  flex-direction:column;
  gap:6rpx;
  min-width:0;
}
.user-name{
  font-size:32rpx;
  font-weight:600;
  color:var(--c-text);
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
}
.user-role{
  font-size:24rpx;
  color:var(--c-text-sec);
  padding:4rpx 16rpx;
  background:var(--c-primary-light);
  border-radius:20rpx;
  width:fit-content;
}

/* 🎨 查看按钮 */
.view-btn{
  display:flex;
  align-items:center;
  gap:8rpx;
  padding:16rpx 28rpx;
  font-size:26rpx;
  color:var(--c-primary-dark);
  background:var(--c-primary-light);
  border:1rpx solid var(--c-primary);
  border-radius:30rpx;
  box-shadow:none;
  font-weight:600;
  transition:all .2s ease;
}
.view-btn:active{
  background:var(--c-primary);
  color:#fff;
  transform:scale(.96);
}
.arrow{
  font-size:30rpx;
  transition:transform .2s ease;
}
.view-btn:active .arrow{
  transform:translateX(4rpx);
}

.empty{
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  gap:20rpx;
  padding:120rpx 0;
}
.empty-icon{
  font-size:80rpx;
  opacity:.5;
}
.empty-text{
  font-size:28rpx;
  color:var(--c-text-sec);
}

/* 🎨 统一按钮样式 */
.btn{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:10rpx;
  width:auto;
  border:2rpx solid transparent;
  border-radius:var(--radius-s);
  font-size:30rpx;
  font-weight:600;
  padding:26rpx 0;
  color:#fff;
  background:#ccc;
  box-shadow:var(--shadow-sm);
  transition:all .25s ease;
}
.btn.wide{ width:100%; }
.btn.primary{
  background:linear-gradient(135deg, var(--c-primary), var(--c-primary-dark));
  border-color:var(--c-primary);
}
.btn.danger{
  background:linear-gradient(135deg, var(--c-danger), var(--c-danger-dark));
  border-color:var(--c-danger);
}
button::after{ border:none; }

.btn:active{
  opacity:.9;
  transform:translateY(2rpx);
  box-shadow:var(--shadow-md);
}
.btn[disabled]{
  opacity:.5;
  transform:none;
}
.search{ width:100%; }

/* 🎨 分页控件 */
.pager{
  margin-top:12rpx;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:32rpx;
}
.pg-btn{
  display:flex;
  align-items:center;
  gap:8rpx;
  padding:20rpx 32rpx;
  font-size:28rpx;
  font-weight:600;
  color:var(--c-text);
  background:#fff;
  border:2rpx solid var(--c-border);
  border-radius:30rpx;
  box-shadow:var(--shadow-sm);
  transition:all .2s ease;
}
.pg-btn:active{
  background:var(--c-primary-light);
  border-color:var(--c-primary);
  color:var(--c-primary-dark);
  transform:scale(.96);
}
.pg-btn[disabled]{
  color:#9aa6b2;
  background:#f7f9fc;
  border-color:#e6eef6;
  opacity:.6;
}
.pg-arrow{
  font-size:32rpx;
  line-height:1;
}

.pg-info-wrap{
  display:flex;
  align-items:baseline;
  gap:8rpx;
  padding:12rpx 28rpx;
  background:var(--c-primary-light);
  border-radius:30rpx;
}
.pg-current{
  font-size:36rpx;
  font-weight:700;
  color:var(--c-primary-dark);
}
.pg-sep{
  font-size:28rpx;
  color:var(--c-text-sec);
}
.pg-total{
  font-size:28rpx;
  color:var(--c-text-sec);
  font-weight:600;
}

/* 🎨 操作区域 */
.actions-card{
  gap:32rpx;
}
.action-grid{
  display:grid;
  grid-template-columns:repeat(3, 1fr);
  gap:20rpx;
}
.action-item{
  display:flex;
  flex-direction:column;
  align-items:center;
  gap:12rpx;
  padding:32rpx 20rpx;
  background:linear-gradient(135deg, #f8fafc, #fff);
  border:1rpx solid var(--c-border);
  border-radius:var(--radius-s);
  box-shadow:var(--shadow-sm);
  transition:all .25s ease;
}
.action-item:active{
  transform:translateY(2rpx);
  box-shadow:var(--shadow-md);
  border-color:var(--c-primary-light);
  background:var(--c-primary-light);
}
.action-icon{
  font-size:48rpx;
  line-height:1;
}
.action-text{
  font-size:24rpx;
  color:var(--c-text-sec);
  font-weight:600;
}

.logout-btn{
  margin-top:12rpx;
}

/* 🎨 加载动画 */
.boot{
  min-height:100vh;
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  gap:32rpx;
  background:linear-gradient(180deg,var(--c-bg-grad-top),var(--c-bg-grad-bottom));
}
.loader{
  width:60rpx;
  height:60rpx;
  border:6rpx solid var(--c-primary-light);
  border-top-color:var(--c-primary);
  border-radius:50%;
  animation:spin 1s linear infinite;
}
@keyframes spin{
  to{ transform:rotate(360deg); }
}
.boot-text{
  font-size:30rpx;
  color:var(--c-text-sec);
  font-weight:600;
}

@media (min-width:880rpx){
  .body{ max-width:960rpx; margin:0 auto; }
}
</style>
