<template>
  <view class="profile-page">
    <!-- 优化导航栏 -->
    <view class="safe-nav">
      <text class="nav-title">👤 个人中心</text>
      <view class="nav-badge">Profile</view>
    </view>

    <view class="body">
      <!-- 用户头像卡片 -->
      <view class="avatar-card">
        <view class="avatar">
          <text class="avatar-text">{{ (user?.account || 'U').charAt(0).toUpperCase() }}</text>
        </view>
        <view class="avatar-info">
          <text class="username">{{ user?.nickname || user?.account || '未登录' }}</text>
          <text class="user-email">{{ user?.email || '未绑定邮箱' }}</text>
        </view>
      </view>

      <!-- 个人信息卡片 -->
      <view class="card">
        <view class="card-header">
          <text class="card-icon">📋</text>
          <text class="card-title">基本信息</text>
        </view>
        <view class="info-list">
          <view class="info-item">
            <view class="item-left">
              <text class="item-icon">👨</text>
              <text class="label">账号</text>
            </view>
            <text class="val">{{ user?.account || '—' }}</text>
          </view>
          <view class="info-item">
            <view class="item-left">
              <text class="item-icon">✏️</text>
              <text class="label">昵称</text>
            </view>
            <text class="val">{{ user?.nickname || '—' }}</text>
          </view>
          <view class="info-item">
            <view class="item-left">
              <text class="item-icon">📧</text>
              <text class="label">邮箱</text>
            </view>
            <text class="val">{{ user?.email || '—' }}</text>
          </view>
          <view class="info-item">
            <view class="item-left">
              <text class="item-icon">🔰</text>
              <text class="label">状态</text>
            </view>
            <view class="status-badge" :class="user?.status?.toLowerCase()">
              {{ user?.status?.toLowerCase() || '—' }}
            </view>
          </view>
          <view class="info-item">
            <view class="item-left">
              <text class="item-icon">🎭</text>
              <text class="label">角色</text>
            </view>
            <view class="roles">
              <text
                v-for="(role, idx) in (user?.roles || [])"
                :key="idx"
                class="role-tag"
              >
                {{ role }}
              </text>
              <text v-if="!(user?.roles || []).length" class="val">—</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 修改昵称卡片 -->
      <view class="card">
        <view class="card-header">
          <text class="card-icon">✨</text>
          <text class="card-title small">修改昵称</text>
        </view>
        <view class="input-wrap">
          <text class="input-label">新昵称</text>
          <input
            v-model="nickname"
            class="ipt"
            placeholder="请输入新的昵称"
            placeholder-class="ph"
          />
        </view>
        <button class="btn primary" :disabled="savingNick" @tap="saveNickname">
          <text class="btn-icon" v-if="!savingNick">💾</text>
          <text>{{ savingNick ? '保存中…' : '保存昵称' }}</text>
        </button>
      </view>

      <!-- 修改密码卡片 -->
      <view class="card">
        <view class="card-header">
          <text class="card-icon">🔒</text>
          <text class="card-title small">修改密码</text>
        </view>
        <view class="input-wrap">
          <text class="input-label">原密码</text>
          <input class="ipt" v-model="oldPwd" password placeholder="请输入原密码" placeholder-class="ph" />
        </view>
        <view class="input-wrap">
          <text class="input-label">新密码</text>
          <input class="ipt" v-model="newPwd" password placeholder="至少6位字符" placeholder-class="ph" />
        </view>
        <view class="input-wrap">
          <text class="input-label">确认密码</text>
          <input class="ipt" v-model="confirmPwd" password placeholder="再次输入新密码" placeholder-class="ph" />
        </view>
        <button class="btn danger" :disabled="savingPwd" @tap="savePassword">
          <text class="btn-icon" v-if="!savingPwd">🔐</text>
          <text>{{ savingPwd ? '提交中…' : '更新密码' }}</text>
        </button>
      </view>

      <!-- 快捷操作 -->
      <view class="card actions-card">
        <view class="action-grid">
          <button class="action-item" @tap="goBack">
            <text class="action-icon">🏠</text>
            <text class="action-text">返回大厅</text>
          </button>
          <button class="action-item" @tap="logout">
            <text class="action-icon">🚪</text>
            <text class="action-text">退出登录</text>
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api, type UserInfo } from '@/utils/api'

const user = ref<UserInfo | null>(null)
const nickname = ref('')
const savingNick = ref(false)

const oldPwd = ref('')
const newPwd = ref('')
const confirmPwd = ref('')
const savingPwd = ref(false)

function toast(t:string){ uni.showToast({ icon:'none', title:t }) }

async function loadMe(){
  try {
    user.value = await api.me()
    nickname.value = user.value.nickname || ''
  } catch(e:any){
    toast(e?.data?.message || '加载失败')
    if(e?.statusCode===401) uni.reLaunch({ url:'/pages/login/login' })
  }
}

async function saveNickname(){
  const n = nickname.value.trim()
  if(!n) return toast('昵称不能为空')
  if(n.length>50) return toast('昵称过长')
  savingNick.value = true
  try {
    user.value = await api.updateMyNickname(n)
    toast('已保存')
  } catch(e:any){
    toast(e?.data?.message || '保存失败')
  } finally { savingNick.value=false }
}

async function savePassword(){
  if(!oldPwd.value || !newPwd.value) return toast('请输入原/新密码')
  if(newPwd.value.length<6) return toast('新密码至少6位')
  if(newPwd.value !== confirmPwd.value) return toast('两次新密码不一致')
  savingPwd.value = true
  try {
    await api.changeMyPassword(oldPwd.value, newPwd.value)
    toast('已更新，请重新登录')
    uni.removeStorageSync('token')
    setTimeout(()=> uni.reLaunch({ url:'/pages/login/login' }), 800)
  } catch(e:any){
    toast(e?.data?.message || '修改失败')
  } finally { savingPwd.value=false }
}

function goBack(){
  uni.navigateBack()
}

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

onMounted(loadMe)
</script>

<style scoped>
:root, page, .profile-page {
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
  --c-green:#38b26f;
  --c-green-light:#d4f5e7;
  --radius:24rpx;
  --radius-s:16rpx;
  --shadow-sm:0 4rpx 12rpx rgba(35,72,130,.06);
  --shadow-md:0 8rpx 24rpx rgba(35,72,130,.08),0 2rpx 6rpx rgba(35,72,130,.06);
  --shadow-lg:0 12rpx 36rpx rgba(35,72,130,.12);
}

.profile-page{
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
  box-sizing:border-box;
  display:flex;
  flex-direction:column;
  gap:32rpx;
  animation:fadeIn .5s ease;
}

@keyframes fadeIn{
  from{ opacity:0; transform:translateY(20rpx); }
  to{ opacity:1; transform:translateY(0); }
}

/* 🎨 新增头像卡片 */
.avatar-card{
  background:linear-gradient(135deg, var(--c-primary-light), #e8f5ff);
  border:1rpx solid var(--c-primary);
  border-radius:var(--radius);
  padding:40rpx;
  display:flex;
  align-items:center;
  gap:28rpx;
  box-shadow:var(--shadow-md);
  animation:slideInDown .5s ease;
}

@keyframes slideInDown{
  from{ opacity:0; transform:translateY(-20rpx); }
  to{ opacity:1; transform:translateY(0); }
}

.avatar{
  width:120rpx;
  height:120rpx;
  border-radius:50%;
  background:linear-gradient(135deg, var(--c-primary), var(--c-primary-dark));
  color:#fff;
  display:flex;
  align-items:center;
  justify-content:center;
  font-size:56rpx;
  font-weight:700;
  box-shadow:0 8rpx 24rpx rgba(102,180,255,.35);
  flex-shrink:0;
  border:4rpx solid #fff;
}

.avatar-text{
  line-height:1;
}

.avatar-info{
  flex:1;
  display:flex;
  flex-direction:column;
  gap:8rpx;
  min-width:0;
}

.username{
  font-size:36rpx;
  font-weight:700;
  color:var(--c-primary-dark);
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
}

.user-email{
  font-size:24rpx;
  color:var(--c-text-sec);
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
}

/* 🎨 优化卡片 */
.card{
  background:var(--c-panel);
  border:1rpx solid var(--c-border);
  border-radius:var(--radius);
  padding:40rpx;
  box-shadow:var(--shadow-md);
  display:flex;
  flex-direction:column;
  gap:28rpx;
  transition:box-shadow .3s ease;
}

.card:active{
  box-shadow:var(--shadow-lg);
}

/* 🎨 卡片头部 */
.card-header{
  display:flex;
  align-items:center;
  gap:12rpx;
  padding-bottom:20rpx;
  border-bottom:2rpx dashed var(--c-border);
}

.card-icon{
  font-size:44rpx;
  line-height:1;
}

.card-title{
  font-size:36rpx;
  font-weight:700;
  color:var(--c-text);
  letter-spacing:.5rpx;
}
.card-title.small{ font-size:32rpx; }

/* 🎨 信息列表优化 */
.info-list{
  display:flex;
  flex-direction:column;
  gap:16rpx;
}

.info-item{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:20rpx;
  padding:24rpx 28rpx;
  background:linear-gradient(135deg, #f8fafc, #fff);
  border:1rpx solid var(--c-border);
  border-radius:var(--radius-s);
  font-size:28rpx;
  transition:all .2s ease;
}

.info-item:active{
  transform:translateY(2rpx);
  box-shadow:var(--shadow-sm);
}

.item-left{
  display:flex;
  align-items:center;
  gap:12rpx;
  flex-shrink:0;
}

.item-icon{
  font-size:32rpx;
  line-height:1;
}

.label{
  color:var(--c-text-sec);
  font-weight:600;
}

.val{
  color:var(--c-text);
  font-weight:500;
  text-align:right;
  word-break:break-all;
}

/* 🎨 状态徽章 */
.status-badge{
  padding:8rpx 20rpx;
  background:#f0f2f5;
  color:var(--c-text-sec);
  font-size:24rpx;
  font-weight:600;
  border-radius:20rpx;
  text-transform:uppercase;
}

.status-badge.active{
  background:var(--c-green-light);
  color:var(--c-green);
}

/* 🎨 角色标签 */
.roles{
  display:flex;
  flex-wrap:wrap;
  gap:12rpx;
  justify-content:flex-end;
}

.role-tag{
  padding:8rpx 20rpx;
  background:var(--c-primary-light);
  color:var(--c-primary-dark);
  font-size:24rpx;
  font-weight:600;
  border-radius:20rpx;
  border:1rpx solid var(--c-primary);
}

/* 🎨 输入框包装 */
.input-wrap{
  display:flex;
  flex-direction:column;
  gap:12rpx;
}

.input-label{
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

/* 🎨 按钮优化 */
.btn{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:10rpx;
  width:100%;
  border:none;
  border-radius:var(--radius-s);
  font-size:30rpx;
  font-weight:700;
  padding:28rpx 0;
  letter-spacing:1rpx;
  color:#fff;
  background:#ccc;
  box-shadow:var(--shadow-md);
  transition:all .25s ease;
  position:relative;
  overflow:hidden;
}

.btn::before{
  content:'';
  position:absolute;
  top:0; left:0; right:0; bottom:0;
  background:linear-gradient(135deg, rgba(255,255,255,.2), transparent);
  opacity:0;
  transition:opacity .25s ease;
}

.btn:active::before{
  opacity:1;
}

.btn-icon{
  font-size:32rpx;
  line-height:1;
}

.btn.primary{
  background:linear-gradient(135deg,#a9d6ff,#66b4ff,#4b9ef0);
  box-shadow:0 8rpx 20rpx rgba(102,180,255,.4);
}
.btn.danger{
  background:linear-gradient(135deg,#ff6a6c,#ff4d4f,var(--c-danger-dark));
  box-shadow:0 8rpx 20rpx rgba(255,77,79,.4);
}
.btn:active{
  opacity:.9;
  transform:translateY(2rpx) scale(.98);
}
.btn[disabled]{
  opacity:.5;
  transform:none;
}

button::after{border:none;}

/* 🎨 快捷操作 */
.actions-card{
  padding:32rpx;
}

.action-grid{
  display:grid;
  grid-template-columns:repeat(2, 1fr);
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
  transform:translateY(2rpx) scale(.98);
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

/* 响应式 */
@media (min-width:750rpx){
  .body{
    max-width:920rpx;
    margin:0 auto;
  }
}
</style>
