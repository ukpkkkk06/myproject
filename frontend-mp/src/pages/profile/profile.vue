<template>
  <view class="container">
    <view class="title">个人信息</view>
    <view class="info">
      <view class="row"><text class="label">账号</text><text class="val">{{ user?.account }}</text></view>
      <view class="row"><text class="label">昵称</text><text class="val">{{ user?.nickname || '—' }}</text></view>
      <view class="row"><text class="label">邮箱</text><text class="val">{{ user?.email || '—' }}</text></view>
      <view class="row"><text class="label">状态</text><text class="val">{{ user?.status?.toLowerCase() }}</text></view>
      <view class="row"><text class="label">角色</text><text class="val">{{ (user?.roles || []).join('、') || '—' }}</text></view>
    </view>

    <view class="title">修改昵称</view>
    <view class="form">
      <input class="ipt" placeholder="新的昵称" v-model="nickname" />
      <button class="btn" :disabled="savingNick" @tap="saveNickname">保存昵称</button>
    </view>

    <view class="title">修改密码</view>
    <view class="form">
      <input class="ipt" placeholder="原密码" password v-model="oldPwd" />
      <input class="ipt" placeholder="新密码（至少6位）" password v-model="newPwd" />
      <input class="ipt" placeholder="确认新密码" password v-model="confirmPwd" />
      <button class="btn danger" :disabled="savingPwd" @tap="savePassword">更新密码</button>
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

function toast(t: string) { uni.showToast({ icon: 'none', title: t }) }

async function loadMe() {
  try {
    user.value = await api.me()
    nickname.value = user.value.nickname || ''
  } catch (e: any) {
    toast(e?.data?.message || '加载失败')
    if (e?.statusCode === 401) uni.reLaunch({ url: '/pages/login/login' })
  }
}

async function saveNickname() {
  const n = nickname.value.trim()
  if (!n) return toast('昵称不能为空')
  if (n.length > 50) return toast('昵称过长')
  savingNick.value = true
  try {
    user.value = await api.updateMyNickname(n)
    toast('已保存')
  } catch (e: any) {
    toast(e?.data?.message || '保存失败')
  } finally {
    savingNick.value = false
  }
}

async function savePassword() {
  if (!oldPwd.value || !newPwd.value) return toast('请输入原/新密码')
  if (newPwd.value.length < 6) return toast('新密码至少6位')
  if (newPwd.value !== confirmPwd.value) return toast('两次新密码不一致')
  savingPwd.value = true
  try {
    await api.changeMyPassword(oldPwd.value, newPwd.value)
    toast('密码已更新，请重新登录')
    uni.removeStorageSync('token')
    setTimeout(() => uni.reLaunch({ url: '/pages/login/login' }), 800)
  } catch (e: any) {
    toast(e?.data?.message || '修改失败')
  } finally {
    savingPwd.value = false
  }
}

onMounted(loadMe)
</script>

<style scoped>
.container { padding: 24rpx; }
.title { font-size: 32rpx; font-weight: 600; margin: 24rpx 0 12rpx; }
.info { background: #fff; border: 1px solid #eee; border-radius: 12rpx; padding: 16rpx; }
.row { display: flex; justify-content: space-between; padding: 8rpx 0; }
.label { color: #666; }
.val { color: #111; }
.form { display: flex; flex-direction: column; gap: 12rpx; }
.ipt { border: 1px solid #ddd; border-radius: 8rpx; padding: 16rpx 12rpx; }
.btn { background: #1677ff; color: #fff; padding: 18rpx; border-radius: 8rpx; }
.btn.danger { background: #ff4d4f; }
</style>
