<template>
  <view class="wrap" v-if="loaded">
    <view class="topbar">
      <view class="meta">第 {{ seq }}/{{ total }} 题</view>
      <view class="progress">
        <view class="bar" :style="{ width: Math.round((seq-1 + (feedback?1:0)) / total * 100) + '%' }"></view>
      </view>
    </view>

    <view class="stem">{{ q?.stem }}</view>

    <radio-group @change="onChoose" :disabled="!!feedback">
      <label v-for="(opt, i) in q?.options || []" :key="i" class="opt"
             :class="optionClass(letters[i])">
        <radio :value="letters[i]" :checked="sel === letters[i]" color="#1677ff" />
        <text>{{ opt }}</text>
      </label>
    </radio-group>

    <button class="btn" :disabled="!sel || posting || !!feedback" @tap="submit">
      {{ posting ? '提交中...' : '提交' }}
    </button>

    <view v-if="feedback" class="fb" :class="feedback.correct ? 'ok' : 'bad'">
      {{ feedback.correct ? '答对啦' : '答错啦，正确答案：' + feedback.correct_answer }}
    </view>

    <view v-if="feedback" class="exp">
      解析：{{ q?.explanation || '暂无解析' }}
    </view>

    <view class="btn-row" v-if="feedback">
      <button class="btn ghost" @tap="redo">重做本题</button>
      <button class="btn" v-if="seq < total" @tap="next">下一题</button>
      <button class="btn danger" v-else @tap="finish">完成</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api, type QuestionView, type SubmitAnswerResp, type CreateSessionResp } from '@/utils/api'

const attemptId = ref<number>(0)
const total = ref<number>(0)
const seq = ref<number>(1)
const q = ref<QuestionView | null>(null)
const sel = ref<string>('')
const feedback = ref<SubmitAnswerResp | null>(null)
const loaded = ref<boolean>(false)
const posting = ref<boolean>(false)
const letters = ['A', 'B', 'C', 'D', 'E', 'F']
let t0 = 0  // 计时起点

function toast(t: string) { uni.showToast({ icon: 'none', title: t }) }
function onChoose(e: any) { sel.value = e.detail.value }

function optionClass(letter: string) {
  if (!feedback.value) return { chosen: sel.value === letter }
  const right = feedback.value.correct_answer === letter
  const wrongChosen = !feedback.value.correct && sel.value === letter
  return { right, wrong: wrongChosen }
}

async function loadQuestion(s: number) {
  uni.showLoading({ title: '加载中' })
  try {
    q.value = await api.getPracticeQuestion(attemptId.value, s)
    seq.value = s
    sel.value = ''
    feedback.value = null
    t0 = Date.now()
  } finally {
    uni.hideLoading()
  }
}

async function submit() {
  if (!sel.value || posting.value) return
  posting.value = true
  try {
    const spent = Date.now() - t0
    feedback.value = await api.submitPracticeAnswer(attemptId.value, seq.value, sel.value, spent)
  } catch (e: any) {
    toast(e?.data?.message || '提交失败')
  } finally {
    posting.value = false
  }
}

async function redo() {
  await loadQuestion(seq.value)
}

async function next() {
  if (seq.value < total.value) await loadQuestion(seq.value + 1)
}

async function finish() {
  try {
    const r = await api.finishPractice(attemptId.value)
    toast(`完成：正确${r.correct_count}/${r.total}，${Math.round(r.accuracy * 100)}%`)
    setTimeout(() => uni.navigateBack(), 800)
  } catch (e: any) {
    toast(e?.data?.message || '结束失败')
  }
}

onMounted(async () => {
  try {
    const token = uni.getStorageSync('token')
    if (!token) return uni.reLaunch({ url: '/pages/login/login' })
    const resp: CreateSessionResp = await api.createPractice(5)
    attemptId.value = resp.attempt_id
    total.value = resp.total
    await loadQuestion(resp.first_seq)
    loaded.value = true
  } catch (e: any) {
    if (e?.statusCode === 401) uni.reLaunch({ url: '/pages/login/login' })
    else toast(e?.data?.message || '加载失败')
  }
})
</script>

<style scoped>
.wrap { padding: 24rpx; }
.topbar { display: flex; flex-direction: column; gap: 12rpx; }
.meta { color: #666; }
.progress { width: 100%; height: 8rpx; background: #f0f0f0; border-radius: 8rpx; overflow: hidden; }
.progress .bar { height: 100%; background: #1677ff; }

.stem { font-size: 32rpx; margin: 20rpx 0; }
.opt { display: flex; align-items: center; padding: 12rpx 0; gap: 12rpx; border-radius: 8rpx; }
.opt.chosen { background: #f5faff; }
.opt.right { background: #e6fffb; color: #096dd9; }
.opt.wrong { background: #fff1f0; color: #cf1322; }

.btn { background: #1677ff; color: #fff; padding: 18rpx; border-radius: 8rpx; margin-top: 16rpx; }
.btn.ghost { background: #fff; color: #1677ff; border: 2rpx solid #1677ff; }
.btn.danger { background: #ff4d4f; }
.btn-row { display: flex; gap: 16rpx; margin-top: 12rpx; }

.fb { margin-top: 12rpx; padding: 12rpx; border-radius: 8rpx; }
.fb.ok { background: #e6fffb; color: #389e0d; }
.fb.bad { background: #fff1f0; color: #cf1322; }
.exp { margin-top: 8rpx; color: #666; line-height: 1.6; }
</style>
