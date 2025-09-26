<template>
  <view class="qd-page">
    <view class="card">
      <view class="title">题目详情</view>

      <view class="section">
        <view class="sec-title">题干</view>
        <view class="content">{{ q?.stem || '加载中…' }}</view>
      </view>

      <view class="section">
        <view class="sec-title">选项</view>
        <view v-if="q?.options?.length" class="options">
          <view v-for="(op, idx) in q?.options" :key="idx" class="option">
            <text class="opt-key">{{ op.key || String.fromCharCode(65+idx) }}.</text>
            <text class="opt-text">{{ op.text || op.content }}</text>
          </view>
        </view>
        <view v-else class="content muted">暂无选项</view>
      </view>

      <view class="section">
        <view class="sec-title">解析</view>
        <view class="content">{{ q?.analysis || '暂无解析' }}</view>
      </view>

      <view class="section">
        <view class="sec-title">历史错误次数</view>
        <view class="content strong">{{ wrongCount }}</view>
      </view>

      <button class="btn ghost wide" @tap="goBack">返回</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { api, type QuestionBrief } from '@/utils/api'

const qid = ref<number>(0)
const wrongCount = ref<number>(0)
const q = ref<QuestionBrief | null>(null)

function goBack(){
  try{
    const pages = getCurrentPages?.()
    if(pages && pages.length > 1) return uni.navigateBack()
  }catch(e){}
  uni.reLaunch({ url:'/pages/error-book/error-book' })
}

async function loadDetail(){
  try{
    const d = await api.getQuestionDetail(qid.value)
    const raw: any = d || {}
    // 兼容不同后端字段名
    q.value = {
      id: (raw.id ?? qid.value) as number,
      stem: (raw.stem ?? raw.title ?? '') as string,
      options: (raw.options ?? raw.choices ?? []) as any[],
      analysis: (raw.analysis ?? raw.explanation ?? '') as string,
    }
  }catch{
    // 占位：加载失败也不报错
    q.value = { id: qid.value, stem: `#${qid.value}`, options: [], analysis: '' } as any
  }
}

onLoad((opt:any)=>{
  qid.value = Number(opt?.id || 0)
  wrongCount.value = Number(opt?.wrong || 0)
  if(!qid.value){
    uni.showToast({ icon:'none', title:'参数错误' })
    setTimeout(()=>goBack(), 600)
    return
  }
  loadDetail()
})
</script>

<style scoped>
:root, page, .qd-page{
  --c-bg1:#e8f2ff; --c-bg2:#f5f9ff; --c-panel:#fff; --c-border:#d8e6f5;
  --c-text:#1f2d3d; --c-text-sec:#5f7085; --c-primary:#66b4ff;
  --radius:20rpx; --radius-s:14rpx;
}
.qd-page{
  min-height:100vh;
  background:linear-gradient(180deg,var(--c-bg1),var(--c-bg2));
  padding:24rpx 28rpx 120rpx;
  box-sizing:border-box;
}
.card{
  background:#fff; border:1rpx solid var(--c-border); border-radius:var(--radius);
  box-shadow:0 8rpx 24rpx rgba(35,72,130,.08);
  padding:30rpx 32rpx; display:flex; flex-direction:column; gap:18rpx;
}
.title{ font-size:36rpx; font-weight:700; color:var(--c-text); margin-bottom:6rpx; }
.section{ margin-top:4rpx; }
.sec-title{ font-size:28rpx; color:var(--c-text-sec); margin-bottom:8rpx; }
.content{ font-size:30rpx; color:var(--c-text); line-height:1.6; word-break:break-word; }
.content.muted{ color:#8da1b5; }
.content.strong{ font-weight:700; }
.options{ display:flex; flex-direction:column; gap:12rpx; }
.option{ display:flex; align-items:flex-start; gap:8rpx; }
.opt-key{ font-weight:700; color:#385176; }
.opt-text{ flex:1; color:var(--c-text); }
.btn{ border:1rpx solid var(--c-border); border-radius:10rpx; font-size:30rpx; padding:22rpx 0; background:#f2f6fb; color:#1f2d3d; box-shadow:none; }
.btn.wide{ width:100%; }
button::after{ border:none; }
</style>