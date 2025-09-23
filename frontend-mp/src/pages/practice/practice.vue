
<template>
  <view class="wrap" v-if="loaded">
    <view class="meta">第 {{ seq }}/{{ total }} 题</view>
    <view class="stem">{{ q?.stem }}</view>
    <radio-group @change="onChoose">
      <label v-for="(opt, i) in q?.options || []" :key="i" class="opt">
        <radio :value="letters[i]" :checked="sel === letters[i]" color="#1677ff" /><text>{{ opt }}</text>
      </label>
    </radio-group>
    <button class="btn" :disabled="!sel" @tap="submit">提交</button>
    <view v-if="feedback" class="fb" :class="feedback.correct ? 'ok' : 'bad'">
      {{ feedback.correct ? '答对啦' : '答错啦，正确答案：' + feedback.correct_answer }}
    </view>
    <button class="btn" v-if="feedback && seq < total" @tap="next">下一题</button>
    <button class="btn danger" v-if="feedback && seq === total" @tap="finish">完成</button>
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
const letters = ['A', 'B', 'C', 'D', 'E', 'F']

function toast(t: string) { uni.showToast({ icon: 'none', title: t }) }

function onChoose(e: any) { sel.value = e.detail.value }

async function loadQuestion(s: number) {
  q.value = await api.getPracticeQuestion(attemptId.value, s)
  seq.value = s
  sel.value = ''
  feedback.value = null
}

async function submit() {
  if (!sel.value) return
  feedback.value = await api.submitPracticeAnswer(attemptId.value, seq.value, sel.value)
}

async function next() {
  if (seq.value < total.value) await loadQuestion(seq.value + 1)
}

async function finish() {
  const r = await api.finishPractice(attemptId.value)
  toast(`完成：正确${r.correct_count}/${r.total}，准确率${Math.round(r.accuracy * 100)}%`)
  setTimeout(() => uni.navigateBack(), 800)
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
.meta { color: #666; margin-bottom: 12rpx; }
.stem { font-size: 32rpx; margin: 16rpx 0; }
.opt { display: flex; align-items: center; padding: 12rpx 0; gap: 12rpx; }
.btn { background: #1677ff; color: #fff; padding: 18rpx; border-radius: 8rpx; margin-top: 16rpx; }
.btn.danger { background: #ff4d4f; }
.fb { margin-top: 12rpx; padding: 12rpx; border-radius: 8rpx; }
.fb.ok { background: #e6fffb; color: #389e0d; }
.fb.bad { background: #fff1f0; color: #cf1322; }
</style>
