<template>
  <view class="container">
    <view class="title">后端健康状态</view>
    <text>{{ JSON.stringify(health) }}</text>

    <view class="title">筛选</view>
    <view class="row">
      <input class="ipt" placeholder="账号关键词" v-model="account" />
      <input class="ipt" placeholder="邮箱关键词" v-model="email" />
      <button size="mini" @tap="onSearch">搜索</button>
    </view>

    <view class="title">用户列表（共 {{ total }} 条）</view>
    <view v-for="u in users" :key="u.id" class="item">
      <template v-if="editingId === u.id">
        {{ u.id }} - {{ u.account }} - {{ u.email }}
        <input class="ipt" v-model="editNickname" placeholder="昵称" />
        <button size="mini" @tap="saveEdit(u.id)">保存</button>
        <button size="mini" @tap="cancelEdit">取消</button>
      </template>
      <template v-else>
        {{ u.id }} - {{ u.account }} - {{ u.email }} - {{ u.status }} - {{ u.nickname }}
        <button size="mini" @tap="startEdit(u)">编辑</button>
        <button size="mini" class="btn-warn" @tap="removeUser(u.id)">删除</button>
      </template>
    </view>

    <view class="footer">
      <button :disabled="loading || finished" @tap="onLoadMore">
        {{ finished ? '没有更多了' : (loading ? '加载中…' : '加载更多') }}
      </button>
    </view>

    <button size="mini" @tap="logout">退出登录</button>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api, type User } from '@/utils/api'

const health = ref<any>(null);
const users = ref<User[]>([]);
const total = ref(0);

const account = ref('');
const email = ref('');
const skip = ref(0);
const limit = ref(10);
const loading = ref(false);
const finished = ref(false);

// 编辑状态
const editingId = ref<number | null>(null);
const editNickname = ref('');

async function load(reset = false) {
  if (loading.value) return;
  loading.value = true;
  try {
    if (reset) {
      skip.value = 0;
      finished.value = false;
      users.value = [];
    }
    const page = await api.users(skip.value, limit.value, account.value, email.value);
    total.value = page.total ?? 0;
    users.value = users.value.concat(page.items ?? []);
    skip.value += page.items?.length ?? 0;
    if ((users.value.length >= total.value) || (page.items?.length ?? 0) < limit.value) {
      finished.value = true;
    }
  } finally {
    loading.value = false;
  }
}

function onSearch() { load(true); }
function onLoadMore() { if (!finished.value) load(false); }

function startEdit(u: User) {
  editingId.value = u.id;
  editNickname.value = u.nickname ?? '';
}
async function saveEdit(id: number) {
  await api.updateUser(id, { nickname: editNickname.value });
  editingId.value = null;
  await load(true);
}
function cancelEdit() { editingId.value = null; }

function showModal(message: string) {
  return new Promise<UniApp.ShowModalRes>((resolve) => {
    uni.showModal({ title: '确认', content: message, success: resolve });
  });
}
async function removeUser(id: number) {
  const res = await showModal(`确定删除用户 #${id} 吗？`);
  if (res.confirm) {
    await api.deleteUser(id);
    await load(true);
  }
}

const ensureLogin = () => {
  const token = uni.getStorageSync('token')
  if (!token) { uni.reLaunch({ url: '/pages/login/login' }); return false }
  return true
}

// 新增：退出登录
function logout() {
  uni.removeStorageSync('token')
  uni.reLaunch({ url: '/pages/login/login' })
}

onMounted(async () => {
  if (!ensureLogin()) return
  health.value = await api.health()
  await load(true);
});
</script>

<style scoped>
.container { padding: 24rpx; }
.title { margin: 24rpx 0 12rpx; font-weight: bold; }
.row { display: flex; gap: 12rpx; align-items: center; }
.ipt { flex: 1; border: 1px solid #ddd; padding: 8rpx 12rpx; border-radius: 6rpx; }
.item { padding: 8rpx 0; border-bottom: 1px dashed #eee; }
.footer { margin-top: 24rpx; }
.btn-warn { background-color: #e54d42; color:#fff; border:none; padding: 8rpx 16rpx; border-radius: 6rpx; }
</style>
