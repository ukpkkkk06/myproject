<template>
  <view class="profile-page">
    <!-- 顶部安全区导航 -->
    <view class="safe-nav">
      <text class="nav-title">个人中心</text>
    </view>

    <!-- 主体（留出导航高度） -->
    <view class="body">

      <!-- 个人信息 -->
      <view class="card">
        <view class="card-title">个人信息</view>
        <view class="info-list">
          <view class="row"><text class="label">账号</text><text class="val">{{ user?.account || '—' }}</text></view>
            <view class="row"><text class="label">昵称</text><text class="val">{{ user?.nickname || '—' }}</text></view>
            <view class="row"><text class="label">邮箱</text><text class="val">{{ user?.email || '—' }}</text></view>
            <view class="row"><text class="label">状态</text><text class="val stat">{{ user?.status?.toLowerCase() }}</text></view>
            <view class="row"><text class="label">角色</text><text class="val">{{ (user?.roles || []).join('、') || '—' }}</text></view>
        </view>
      </view>

      <!-- 修改昵称 -->
      <view class="card">
        <view class="card-title small">修改昵称</view>
        <input
          v-model="nickname"
          class="ipt"
          placeholder="新的昵称"
          placeholder-class="ph"
        />
        <button class="btn primary" :disabled="savingNick" @tap="saveNickname">
          {{ savingNick ? '保存中…' : '保存昵称' }}
        </button>
      </view>

      <!-- 修改密码 -->
      <view class="card">
        <view class="card-title small">修改密码</view>
        <input class="ipt" v-model="oldPwd" password placeholder="原密码" placeholder-class="ph" />
        <input class="ipt" v-model="newPwd" password placeholder="新密码（至少6位）" placeholder-class="ph" />
        <input class="ipt" v-model="confirmPwd" password placeholder="确认新密码" placeholder-class="ph" />
        <button class="btn danger" :disabled="savingPwd" @tap="savePassword">
          {{ savingPwd ? '提交中…' : '更新密码' }}
        </button>
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
  --radius:20rpx;
  --radius-s:14rpx;
}

.profile-page{
  min-height:100vh;
  background:linear-gradient(180deg,var(--c-bg-grad-top),var(--c-bg-grad-bottom));
  display:flex;
  flex-direction:column;
}

/* 安全区导航 */
.safe-nav{
  position:fixed;
  top:0; left:0; right:0;
  padding-top:env(safe-area-inset-top);
  padding-top:constant(safe-area-inset-top);
  height:calc(env(safe-area-inset-top) + 88rpx);
  height:calc(constant(safe-area-inset-top) + 88rpx);
  box-sizing:border-box;
  display:flex;
  align-items:flex-end;
  justify-content:center;
  padding-bottom:16rpx;
  background:rgba(255,255,255,0.55);
  backdrop-filter:blur(10px);
  border-bottom:1rpx solid rgba(214,230,245,0.8);
  z-index:10;
}
.nav-title{
  font-size:40rpx;
  font-weight:700;
  color:var(--c-text);
  letter-spacing:1rpx;
}

.body{
  padding:calc(env(safe-area-inset-top) + 88rpx) 40rpx 140rpx;
  box-sizing:border-box;
  display:flex;
  flex-direction:column;
  gap:40rpx;
}

.card{
  background:var(--c-panel);
  border:1rpx solid var(--c-border);
  border-radius:var(--radius);
  padding:40rpx 38rpx 48rpx;
  box-shadow:0 8rpx 24rpx rgba(35,72,130,0.08),0 2rpx 6rpx rgba(35,72,130,0.06);
  display:flex;
  flex-direction:column;
  gap:34rpx;
}

.card-title{
  font-size:40rpx;
  font-weight:600;
  color:var(--c-text);
  margin:0;
}
.card-title.small{ font-size:34rpx; }

.info-list{
  border:1rpx solid var(--c-border);
  border-radius:var(--radius-s);
  overflow:hidden;
  background:#fff;
}
.row{
  display:flex;
  justify-content:space-between;
  padding:24rpx 28rpx;
  border-bottom:1rpx solid var(--c-border);
  font-size:28rpx;
}
.row:last-child{ border-bottom:none; }
.label{ color:var(--c-text-sec); }
.val{ color:var(--c-text); font-weight:500; }
.val.stat{ text-transform:lowercase; }
.val:empty::after{ content:'—'; color:var(--c-text-sec); }

.ipt{
  width:100%;
  height:92rpx;
  line-height:92rpx;
  padding:0 30rpx;
  font-size:30rpx;
  background:#fff;
  border:1rpx solid var(--c-border);
  border-radius:var(--radius-s);
  box-sizing:border-box;
  color:var(--c-text);
  transition:border-color .18s, box-shadow .18s;
}
.ipt:focus{
  border-color:var(--c-primary);
  box-shadow:0 0 0 4rpx var(--c-primary-light);
}
.ph{
  color:#9ab2c7;
  font-size:30rpx;
  line-height:92rpx;
}

.btn{
  width:100%;
  border:none;
  border-radius:var(--radius-s);
  font-size:30rpx;
  font-weight:600;
  padding:28rpx 0;
  letter-spacing:1rpx;
  color:#fff;
  background:#ccc;
  box-shadow:0 4rpx 10rpx rgba(0,0,0,0.08);
  transition:opacity .18s;
}
.btn.primary{
  background:linear-gradient(90deg,#a9d6ff,#66b4ff);
  box-shadow:0 6rpx 14rpx rgba(102,180,255,.35);
}
.btn.danger{
  background:linear-gradient(90deg,#ff6a6c,#ff4d4f);
  box-shadow:0 6rpx 14rpx rgba(255,77,79,.30);
}
.btn:active{ opacity:.86; }
.btn[disabled]{ opacity:.55; }

@media (min-width:750rpx){
  .body{ max-width:920rpx; margin:0 auto; }
}
</style>
