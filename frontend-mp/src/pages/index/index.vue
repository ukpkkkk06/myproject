<template>
  <view class="admin-page">
    <!-- 自定义安全区导航，防止被灵动岛遮挡 -->
    <view class="safe-nav">
      <text class="nav-title">管理员后台</text>
    </view>

    <!-- 主体 -->
    <view class="body" v-if="ready">
      <!-- 健康状态 -->
      <view class="card">
        <view class="card-title">系统健康状态</view>
        <view class="health">
          <view class="kv" v-for="(v,k) in health" :key="k">
            <text class="k">{{ k }}</text>
            <text class="v" :class="{ ok: v==='ok' }">{{ v }}</text>
          </view>
        </view>
      </view>

      <!-- 筛选 -->
      <view class="card">
        <view class="card-title small">用户筛选</view>
        <view class="filters">
          <input
            class="ipt"
            v-model="account"
            placeholder="账号关键词"
            placeholder-class="ph"
            @confirm="onSearch"
          />
          <input
            class="ipt"
            v-model="email"
            placeholder="邮箱关键词"
            placeholder-class="ph"
            @confirm="onSearch"
          />
          <button class="btn primary search" :disabled="loading" @tap="onSearch">
            {{ loading ? '搜索中…' : '搜索' }}
          </button>
        </view>
        <view class="desc">结果：{{ total }} 条</view>

        <view class="list">
          <view v-for="u in items" :key="u.id" class="user-row">
            <text class="acc">{{ u.account }}</text>
            <text class="role">{{ u.role || '—' }}</text>
            <!-- 将原状态显示替换为“查看”控件 -->
            <button class="view-btn" @tap="openDetail(u)">查看</button>
          </view>
          <view v-if="!loading && items.length===0" class="empty">暂无数据</view>
        </view>

        <!-- 分页控件 -->
        <view class="pager" v-if="total > 0">
          <button class="pg-btn" :disabled="page<=1 || loading" @tap="goPrev">上一页</button>
          <text class="pg-info">第 {{ page }} / {{ totalPages }} 页</text>
          <button class="pg-btn" :disabled="page>=totalPages || loading" @tap="goNext">下一页</button>
        </view>
      </view>

      <!-- 操作 -->
      <view class="card actions">
        <button class="btn danger wide" @tap="logout">退出登录</button>
      </view>
    </view>

    <!-- 加载占位，避免进入前闪现后台内容 -->
    <view v-else class="boot">
      <text class="boot-text">加载中…</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { api, type UserSimple } from '@/utils/api'

const health = ref<any>({})
const items = ref<UserSimple[]>([])
const total = ref(0)

const account = ref('')
const email = ref('')

const page = ref(1)
const limit = ref(5)           // 每页固定 5 条
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

function openDetail(u: UserSimple){
  uni.navigateTo({ url: `/pages/user-detail/user-detail?uid=${u.id}` })
}

onMounted(async ()=>{
  if(!(await guardAdmin())) return
  try { health.value = await api.health() } catch {}
  ready.value = true
  load(1)
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
  --radius:20rpx;
  --radius-s:14rpx;
}

.admin-page{
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
  background:rgba(255,255,255,.55);
  backdrop-filter:blur(10px);
  border-bottom:1rpx solid rgba(214,230,245,.8);
  z-index:10;
}
.nav-title{
  font-size:40rpx;
  font-weight:700;
  color:var(--c-text);
}

.body{
  padding:calc(env(safe-area-inset-top) + 88rpx) 40rpx 140rpx;
  display:flex;
  flex-direction:column;
  gap:40rpx;
  box-sizing:border-box;
}

.card{
  background:var(--c-panel);
  border:1rpx solid var(--c-border);
  border-radius:var(--radius);
  padding:40rpx 38rpx 46rpx;
  box-shadow:0 8rpx 24rpx rgba(35,72,130,.08),0 2rpx 6rpx rgba(35,72,130,.06);
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

.health{
  display:flex;
  flex-wrap:wrap;
  gap:18rpx 30rpx;
}
.kv{ display:flex; align-items:center; gap:10rpx; background:#f6f9fc; padding:14rpx 20rpx; border-radius:var(--radius-s); font-size:26rpx; }
.k{ color:var(--c-text-sec); }
.v{ color:var(--c-text); font-weight:600; }
.v.ok{ color:#38b26f; }

.filters{
  display:flex;
  flex-direction:column;
  gap:26rpx;
}
@media (min-width:700rpx){
  .filters{ flex-direction:row; align-items:center; }
}

.ipt{
  flex:1;
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

.desc{
  font-size:24rpx;
  color:var(--c-text-sec);
  margin-top:-10rpx;
}

.list{
  display:flex;
  flex-direction:column;
  border:1rpx solid var(--c-border);
  border-radius:var(--radius-s);
  overflow:hidden;
  background:#fff;
}
.user-row{
  display:grid;
  grid-template-columns: 1fr 180rpx 160rpx; /* 第3列为按钮列 */
  gap:12rpx;
  padding:24rpx 28rpx;
  border-bottom:1rpx solid var(--c-border);
  font-size:28rpx;
  align-items:center;
}
.user-row:last-child{ border-bottom:none; }
.acc{ font-weight:600; color:var(--c-text); }
.role{ color:var(--c-primary-dark); text-align:center; font-size:26rpx; }
.status{ text-align:right; font-size:26rpx; color:var(--c-text-sec); text-transform:lowercase; }

.empty{
  text-align:center;
  padding:100rpx 0;
  font-size:30rpx;
  color:var(--c-text-sec);
}

/* 统一扁平化按钮样式（与用户详情页一致） */
.btn{
  width:auto;
  border:1rpx solid transparent;
  border-radius:10rpx;
  font-size:30rpx;
  font-weight:600;
  padding:24rpx 0;
  color:#fff;
  background:#ccc;
  box-shadow:none;
  transition:opacity .18s;
}
.btn.wide{ width:100%; }              /* 通栏 */
.btn.primary{
  background:#66b4ff;                 /* 纯色主色 */
  border-color:#66b4ff;
}
.btn.danger{
  background:#ff4d4f;                 /* 纯色红 */
  border-color:#ff4d4f;
}
button::after{ border:none; }         /* 去小程序默认描边 */

.btn:active{ opacity:.86; }
.btn[disabled]{ opacity:.55; }
.search{ width:100%; }
@media (min-width:700rpx){
  .search{ width:auto; padding:0 60rpx; }
}

.actions{ gap:28rpx; }
.boot{
  min-height:100vh;
  display:flex;
  align-items:center;
  justify-content:center;
  background:linear-gradient(180deg,var(--c-bg-grad-top),var(--c-bg-grad-bottom));
}
.boot-text{ font-size:30rpx; color:var(--c-text-sec); }

/* 分页控件（扁平） */
.pager{
  margin-top:18rpx;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:24rpx;
}
.pg-btn{
  padding:18rpx 28rpx;
  font-size:28rpx;
  color:var(--c-text);
  background:#f2f6fb;
  border:1rpx solid var(--c-border);
  border-radius:10rpx;
  box-shadow:none;
}
.pg-btn:active{ opacity:.92; }
.pg-btn[disabled]{ color:#9aa6b2; background:#f7f9fc; border-color:#e6eef6; }
.pg-info{ font-size:26rpx; color:var(--c-text-sec); }

@media (min-width:880rpx){
  .body{ max-width:960rpx; margin:0 auto; }
}
.view-btn{
  justify-self:end;
  padding:12rpx 22rpx;
  font-size:26rpx;
  color:#1f2d3d;
  background:#f2f6fb;
  border:1rpx solid var(--c-border);
  border-radius:10rpx;
  box-shadow:none;
}
.view-btn:active{ opacity:.92; }
</style>
