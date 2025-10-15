<template>
  <view class="ud-page">
    <!-- 顶部导航 -->
    <view class="safe-nav">
      <view class="nav-content">
        <text class="nav-icon">👤</text>
        <text class="nav-title">用户详情</text>
      </view>
    </view>

    <view class="body">
      <!-- 基本信息卡片 -->
      <view class="card info-card">
        <view class="card-header">
          <text class="card-icon">📋</text>
          <text class="card-title">基本信息</text>
        </view>
        <view class="info-grid">
          <view class="info-row">
            <text class="info-label">用户ID</text>
            <text class="info-value">{{ u?.id }}</text>
          </view>
          <view class="info-row">
            <text class="info-label">账号</text>
            <text class="info-value primary">{{ u?.account }}</text>
          </view>
          <view class="info-row">
            <text class="info-label">昵称</text>
            <text class="info-value">{{ u?.nickname || '—' }}</text>
          </view>
          <view class="info-row">
            <text class="info-label">邮箱</text>
            <text class="info-value">{{ u?.email || '—' }}</text>
          </view>
          <view class="info-row">
            <text class="info-label">状态</text>
            <view class="status-badge" :class="'status-' + ((u?.status || '').toLowerCase() || 'active')">
              <text class="status-dot">●</text>
              <text>{{ (u?.status || 'active').toLowerCase() }}</text>
            </view>
          </view>
          <view class="info-row">
            <text class="info-label">角色</text>
            <view class="roles-wrapper">
              <text v-for="r in (u?.roles || [])" :key="r.code" class="role-pill">{{ r.name || r.code }}</text>
              <text v-if="!u?.roles?.length" class="empty-text">—</text>
            </view>
          </view>
          <view class="info-row">
            <text class="info-label">注册时间</text>
            <text class="info-value time">{{ dt(u?.created_at) || '—' }}</text>
          </view>
          <view class="info-row">
            <text class="info-label">最近登录</text>
            <text class="info-value time">{{ dt(u?.last_login_at) || '—' }}</text>
          </view>
        </view>
      </view>

      <!-- 编辑资料卡片 -->
      <view class="card edit-card">
        <view class="card-header">
          <text class="card-icon">✏️</text>
          <text class="card-title">修改资料</text>
        </view>
        <view class="form-fields">
          <view class="field-group">
            <view class="field-label">
              <text class="label-icon">✨</text>
              <text>昵称</text>
            </view>
            <input class="ipt" v-model="form.nickname" placeholder="请输入昵称" placeholder-class="ph" />
          </view>
          <view class="field-group">
            <view class="field-label">
              <text class="label-icon">📧</text>
              <text>邮箱</text>
            </view>
            <input class="ipt" v-model="form.email" placeholder="请输入邮箱（可选）" placeholder-class="ph" />
          </view>
          <view class="field-group">
            <view class="field-label">
              <text class="label-icon">⚙️</text>
              <text>状态</text>
            </view>
            <picker class="picker" mode="selector" :range="statusOptions" @change="onPickStatus">
              <view class="select">{{ form.status || '请选择状态' }}</view>
            </picker>
          </view>
        </view>
        <button class="action-btn primary" :disabled="savingInfo" @tap="saveInfo">
          <text class="btn-icon">{{ savingInfo ? '⏳' : '💾' }}</text>
          <text>{{ savingInfo ? '保存中…' : '保存资料' }}</text>
        </button>
      </view>

      <!-- 重置密码卡片 -->
      <view class="card pwd-card">
        <view class="card-header">
          <text class="card-icon">🔐</text>
          <text class="card-title">重置密码</text>
        </view>
        <view class="form-fields">
          <view class="field-group">
            <view class="field-label">
              <text class="label-icon">🔑</text>
              <text>新密码</text>
            </view>
            <input class="ipt" v-model="pwd1" password placeholder="至少6位字符" placeholder-class="ph" />
          </view>
          <view class="field-group">
            <view class="field-label">
              <text class="label-icon">🔒</text>
              <text>确认密码</text>
            </view>
            <input class="ipt" v-model="pwd2" password placeholder="再次输入新密码" placeholder-class="ph" />
          </view>
        </view>
        <button class="action-btn danger" :disabled="savingPwd" @tap="resetPwd">
          <text class="btn-icon">{{ savingPwd ? '⏳' : '🔄' }}</text>
          <text>{{ savingPwd ? '提交中…' : '更新密码' }}</text>
        </button>
      </view>

      <!-- 返回按钮 -->
      <button class="action-btn ghost back-btn" @tap="goBack">
        <text class="btn-icon">↩️</text>
        <text>返回后台</text>
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { adminGetUserDetail, adminUpdateUser, adminResetUserPassword, type AdminUserDetail } from '@/utils/api'

function goBack(){
  try{
    const pages = (getCurrentPages && getCurrentPages()) as any[]
    if (pages && pages.length > 1) return uni.navigateBack()
  }catch(e){}
  uni.reLaunch({ url: '/pages/index/index' })
}

const uid = ref<number>(0)
const u = ref<AdminUserDetail | null>(null)

const form = ref<{ nickname: string; email?: string; status?: string }>({ nickname: '', email: '', status: undefined })
const statusOptions = ['active', 'disabled']
function onPickStatus(e:any){ form.value.status = statusOptions[e.detail.value] }

const savingInfo = ref(false)
const savingPwd = ref(false)
const pwd1 = ref(''); const pwd2 = ref('')

function toast(t:string){ uni.showToast({ icon:'none', title:t }) }
function dt(s?:string){ return s ? s.replace('T',' ').split('.')[0] : '' }

async function loadDetail(){
  u.value = await adminGetUserDetail(uid.value)
  form.value.nickname = u.value?.nickname || ''
  form.value.email = u.value?.email || ''
  form.value.status = (u.value?.status || '').toLowerCase() || undefined
}

async function saveInfo(){
  if(!form.value.nickname.trim()) return toast('昵称不能为空')
  savingInfo.value = true
  try{
    const payload:any = {
      nickname: form.value.nickname.trim(),
      email: form.value.email?.trim() || null,
    }
    if(form.value.status) payload.status = form.value.status.toUpperCase()
    await adminUpdateUser(uid.value, payload)
    toast('已保存')
    await loadDetail()
  }catch(e:any){
    toast(e?.data?.message || '保存失败')
  }finally{ savingInfo.value = false }
}

async function resetPwd(){
  if(!pwd1.value || pwd1.value.length < 6) return toast('新密码至少6位')
  if(pwd1.value !== pwd2.value) return toast('两次密码不一致')
  savingPwd.value = true
  try{
    await adminResetUserPassword(uid.value, pwd1.value)
    toast('密码已更新')
    pwd1.value = ''; pwd2.value = ''
  }catch(e:any){
    toast(e?.data?.message || '更新失败')
  }finally{ savingPwd.value = false }
}

onLoad(async (q:any) => {
  uid.value = Number(q?.uid || 0)
  if(!uid.value){ toast('参数错误'); setTimeout(()=>uni.navigateBack(), 600); return }
  try{ await loadDetail() }catch{ toast('加载失败') }
})
</script>

<style scoped>
:root, page, .ud-page {
  --c-bg-start:#e8f2ff;
  --c-bg-end:#f5f9ff;
  --c-card:#fff;
  --c-border:#d8e6f5;
  --c-primary:#66b4ff;
  --c-primary-dark:#4b9ef0;
  --c-primary-light:#e6f3ff;
  --c-text:#1f2d3d;
  --c-text-sec:#5f7085;
  --c-text-muted:#8da1b5;
  --c-success:#38b26f;
  --c-success-bg:#e8f9f0;
  --c-danger:#ff4d4f;
  --c-danger-bg:#fff1f0;
  --shadow-sm:0 4rpx 12rpx rgba(35,72,130,.06);
  --shadow-md:0 8rpx 24rpx rgba(35,72,130,.08);
  --shadow-lg:0 16rpx 48rpx rgba(35,72,130,.12);
  --radius-lg:24rpx;
  --radius-md:16rpx;
  --radius-sm:12rpx;
}

.ud-page{
  min-height:100vh;
  background:linear-gradient(180deg,var(--c-bg-start),var(--c-bg-end));
}

/* ========== 顶部导航 ========== */
.safe-nav{
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

/* ========== 主体 ========== */
.body{
  padding:calc(env(safe-area-inset-top) + 116rpx) 32rpx 120rpx;
  display:flex;
  flex-direction:column;
  gap:28rpx;
}

/* ========== 卡片 ========== */
.card{
  background:var(--c-card);
  border-radius:var(--radius-lg);
  box-shadow:var(--shadow-lg);
  padding:32rpx;
  display:flex;
  flex-direction:column;
  gap:24rpx;
}

.card-header{
  display:flex;
  align-items:center;
  gap:12rpx;
  padding-bottom:16rpx;
  border-bottom:2rpx solid #f0f2f5;
}

.card-icon{
  font-size:32rpx;
  line-height:1;
}

.card-title{
  font-size:32rpx;
  font-weight:600;
  color:var(--c-text);
}

/* ========== 信息展示 ========== */
.info-grid{
  display:flex;
  flex-direction:column;
  gap:20rpx;
}

.info-row{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:20rpx 24rpx;
  background:#f7f9fc;
  border-radius:var(--radius-sm);
  min-height:80rpx;
}

.info-label{
  font-size:26rpx;
  color:var(--c-text-sec);
  font-weight:500;
}

.info-value{
  font-size:28rpx;
  color:var(--c-text);
  font-weight:600;
  text-align:right;
  word-break:break-all;
}

.info-value.primary{
  color:var(--c-primary-dark);
}

.info-value.time{
  font-size:24rpx;
  color:var(--c-text-muted);
  font-weight:400;
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

.status-active{
  background:var(--c-success-bg);
  color:var(--c-success);
}

.status-disabled{
  background:#f0f2f5;
  color:var(--c-text-muted);
}

.roles-wrapper{
  display:flex;
  flex-wrap:wrap;
  gap:8rpx;
  justify-content:flex-end;
}

.role-pill{
  padding:6rpx 14rpx;
  border-radius:999rpx;
  background:var(--c-primary-light);
  color:var(--c-primary-dark);
  font-size:22rpx;
  font-weight:600;
}

.empty-text{
  color:var(--c-text-muted);
  font-size:24rpx;
}

/* ========== 表单 ========== */
.form-fields{
  display:flex;
  flex-direction:column;
  gap:24rpx;
}

.field-group{
  display:flex;
  flex-direction:column;
  gap:12rpx;
}

.field-label{
  display:flex;
  align-items:center;
  gap:8rpx;
  font-size:26rpx;
  font-weight:600;
  color:var(--c-text);
}

.label-icon{
  font-size:28rpx;
  line-height:1;
}

.ipt{
  width:100%;
  padding:20rpx 24rpx;
  font-size:28rpx;
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

.ph{
  color:var(--c-text-muted);
  font-size:26rpx;
}

.picker{
  width:100%;
}

.select{
  padding:20rpx 24rpx;
  background:#f7f9fc;
  border:2rpx solid var(--c-border);
  border-radius:var(--radius-sm);
  color:var(--c-text);
  font-size:28rpx;
  transition:all 0.3s;
}

/* ========== 按钮 ========== */
.action-btn{
  width:100%;
  padding:26rpx 0;
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

.action-btn.primary{
  background:linear-gradient(135deg, #66b4ff 0%, #4a9fff 100%);
  color:#fff;
}

.action-btn.danger{
  background:linear-gradient(135deg, var(--c-danger) 0%, #d73a3c 100%);
  color:#fff;
}

.action-btn.ghost{
  background:#f7f9fc;
  color:var(--c-text-sec);
  border:2rpx solid var(--c-border);
}

.action-btn:active:not([disabled]){
  box-shadow:var(--shadow-md);
  transform:translateY(-2rpx);
}

.action-btn[disabled]{
  opacity:0.6;
}

.btn-icon{
  font-size:32rpx;
  line-height:1;
}

.back-btn{
  margin-top:12rpx;
}

button::after{
  border:none;
}
</style>
