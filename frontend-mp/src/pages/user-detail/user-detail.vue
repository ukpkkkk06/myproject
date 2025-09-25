<template>
  <view class="ud-page">
    <!-- 顶部仅保留标题 -->
    <view class="safe-nav">
      <text class="nav-title">用户详情</text>
    </view>

    <view class="body">
      <!-- 基本信息 -->
      <view class="card">
        <view class="card-title">基本信息</view>
        <view class="info">
          <view class="row"><text class="label">用户ID</text><text class="val">{{ u?.id }}</text></view>
          <view class="row"><text class="label">账号</text><text class="val">{{ u?.account }}</text></view>
          <view class="row"><text class="label">昵称</text><text class="val">{{ u?.nickname || '—' }}</text></view>
          <view class="row"><text class="label">邮箱</text><text class="val">{{ u?.email || '—' }}</text></view>
          <view class="row"><text class="label">状态</text><text class="val">{{ (u?.status || '').toLowerCase() || '—' }}</text></view>
          <view class="row"><text class="label">角色</text>
            <text class="val">
              <text v-for="r in (u?.roles || [])" :key="r.code" class="pill">{{ r.name || r.code }}</text>
              <text v-if="!u?.roles?.length" class="muted">—</text>
            </text>
          </view>
          <view class="row"><text class="label">注册时间</text><text class="val">{{ dt(u?.created_at) || '—' }}</text></view>
          <view class="row"><text class="label">最近登录</text><text class="val">{{ dt(u?.last_login_at) || '—' }}</text></view>
        </view>
      </view>

      <!-- 编辑资料 -->
      <view class="card">
        <view class="card-title small">修改资料</view>
        <input class="ipt" v-model="form.nickname" placeholder="昵称" placeholder-class="ph" />
        <input class="ipt" v-model="form.email" placeholder="邮箱（可选）" placeholder-class="ph" />
        <picker class="picker" mode="selector" :range="statusOptions" @change="onPickStatus">
          <view class="select">状态：{{ form.status || '未选择' }}</view>
        </picker>
        <button class="btn primary wide" :disabled="savingInfo" @tap="saveInfo">
          {{ savingInfo ? '保存中…' : '保存资料' }}
        </button>
      </view>

      <!-- 重置密码 -->
      <view class="card">
        <view class="card-title small">重置密码</view>
        <input class="ipt" v-model="pwd1" password placeholder="新密码（至少6位）" placeholder-class="ph" />
        <input class="ipt" v-model="pwd2" password placeholder="确认新密码" placeholder-class="ph" />
        <button class="btn danger wide" :disabled="savingPwd" @tap="resetPwd">
          {{ savingPwd ? '提交中…' : '更新密码' }}
        </button>

        <!-- 返回控件（扁平通栏） -->
        <button class="btn ghost wide back-under" @tap="goBack">返回后台</button>
      </view>
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
const statusOptions = ['active', 'disabled']  // 可按后端实际扩展：active/disabled/locked 等
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
    // 传给后端时把状态转为大写（若后端用大写）
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
  --c-bg1:#e8f2ff; --c-bg2:#f5f9ff; --c-panel:#fff; --c-border:#d8e6f5;
  --c-primary:#66b4ff; --c-text:#1f2d3d; --c-text-sec:#5f7085;
  --c-danger:#ff4d4f; --radius:20rpx; --radius-s:14rpx;
}
.ud-page{ min-height:100vh; background:linear-gradient(180deg,var(--c-bg1),var(--c-bg2)); }
.safe-nav{ position:fixed; left:0; right:0; top:0; padding-top:env(safe-area-inset-top); height:calc(env(safe-area-inset-top) + 88rpx); display:flex; align-items:flex-end; justify-content:center; padding-bottom:16rpx; background:rgba(255,255,255,.55); border-bottom:1rpx solid rgba(214,230,245,.8); }
.nav-title{ font-size:40rpx; font-weight:700; color:var(--c-text); }

/* 移除顶部 back-btn 的样式 */
.body{ padding:calc(env(safe-area-inset-top)+88rpx) 36rpx 120rpx; display:flex; flex-direction:column; gap:34rpx; }
.card{ background:#fff; border:1rpx solid var(--c-border); border-radius:var(--radius); padding:36rpx; box-shadow:0 8rpx 24rpx rgba(35,72,130,.08); display:flex; flex-direction:column; gap:24rpx; }
.card-title{ font-size:36rpx; font-weight:600; }
.card-title.small{ font-size:32rpx; }
.info{ border:1rpx solid var(--c-border); border-radius:var(--radius-s); overflow:hidden; }
.row{ display:flex; justify-content:space-between; padding:22rpx 24rpx; border-bottom:1rpx solid var(--c-border); font-size:28rpx; }
.row:last-child{ border-bottom:none; }
.label{ color:var(--c-text-sec); }
.val{ color:var(--c-text); }
.pill{ display:inline-block; margin-right:10rpx; padding:8rpx 16rpx; border-radius:999rpx; background:#eef6ff; color:#4b9ef0; font-size:24rpx; }
.muted{ color:#9aa6b2; }
.ipt{ width:100%; height:92rpx; line-height:92rpx; padding:0 30rpx; font-size:30rpx; background:#fff; border:1rpx solid var(--c-border); border-radius:var(--radius-s); box-sizing:border-box; color:var(--c-text); }
.ipt:focus{ border-color:var(--c-primary); box-shadow:0 0 0 4rpx #d4ecff; }
.ph{ color:#9ab2c7; font-size:30rpx; }
.picker{ width:100%; }
.select{
  height:92rpx;
  line-height:92rpx;
  padding:0 30rpx;
  border:1rpx solid var(--c-border);
  border-radius:var(--radius-s);
  background:#f7f9fc;
  color:var(--c-text);
  font-size:30rpx;
}

/* 公共按钮样式 */
.btn{
  width:auto;
  border:1rpx solid transparent;
  border-radius:10rpx;
  font-size:30rpx;
  font-weight:600;
  padding:24rpx 0;
  box-shadow:none;               /* 去阴影 */
  transition:opacity .18s;
}
.btn.wide{ width:100%; }         /* 通栏 */
.btn.primary{
  color:#fff;
  background:#66b4ff;            /* 纯色，非渐变 */
  border-color:#66b4ff;
}
.btn.danger{
  color:#fff;
  background:#ff4d4f;            /* 纯色红 */
  border-color:#ff4d4f;
}
.btn.ghost{
  color:#1f2d3d;
  background:#f2f6fb;            /* 浅灰填充 */
  border-color:var(--c-border);
}
.btn:active{ opacity:.92; }
.btn[disabled]{ opacity:.55; }

/* 移除小程序 button 默认描边（必须） */
button::after{ border:none; }
</style>
