<template>
  <view class="qe-page">
    <view class="card">
      <view class="title">编辑题目</view>

      <view class="form">
        <view class="label">题干</view>
        <textarea class="ipt area" v-model="form.stem" placeholder="请输入题干" />

        <view class="label">选项</view>
        <view class="opts">
          <view class="opt" v-for="(op, i) in form.options" :key="i">
            <input class="ipt" v-model="op.text" :placeholder="'选项 ' + keyOf(i)" />
            <label class="correct">
              <radio :checked="form.correct_answer===keyOf(i)" @tap="setCorrect(i)" /> 正确
            </label>
            <button class="mini danger" @tap="removeOpt(i)">删除</button>
          </view>
          <button class="mini ghost" @tap="addOpt">新增选项</button>
        </view>

        <view class="label">解析</view>
        <textarea class="ipt area" v-model="form.analysis" placeholder="请输入解析（可选）" />

        <view class="label">状态</view>
        <view class="switch-wrap">
          <switch :checked="form.is_active" @change="e=>form.is_active=!!e.detail.value" color="#66b4ff" />
          <text class="sw-label">{{ form.is_active ? '启用' : '停用' }}</text>
        </view>

        <button class="btn primary wide" :disabled="saving" @tap="save">{{ saving ? '保存中…' : '保存' }}</button>
        <button class="btn ghost wide" @tap="goBack">返回</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { api, type QuestionOption } from '@/utils/api'

const qid = ref<number>(0)
const saving = ref(false)
const form = ref<{
  stem: string
  options: { key?: string; text: string }[]
  correct_answer: string
  analysis: string
  is_active: boolean
}>({
  stem: '',
  options: [],
  correct_answer: 'A',
  analysis: '',
  is_active: true,
})

function keyOf(i:number){ return String.fromCharCode(65 + i) }
function setCorrect(i:number){ form.value.correct_answer = keyOf(i) }
function addOpt(){ form.value.options.push({ text: '' }) }
function removeOpt(i:number){
  form.value.options.splice(i,1)
  if(form.value.correct_answer === keyOf(i)) form.value.correct_answer = keyOf(0)
}

function normalizeOptions(raw:any): {key?:string; text:string}[] {
  if(!raw) return []
  if(Array.isArray(raw)){
    return raw.map((it:any, i:number)=> {
      if(typeof it === 'string') return { key: keyOf(i), text: it }
      return { key: it.key ?? keyOf(i), text: it.text ?? it.content ?? '' }
    })
  }
  if(typeof raw === 'object'){
    return Object.entries(raw).map(([k,v]:any)=> ({ key: k, text: String(v) }))
  }
  return []
}

async function load(){
  const d:any = await api.getQuestionDetail(qid.value)
  form.value.stem = d?.stem ?? d?.title ?? ''
  form.value.options = normalizeOptions(d?.options ?? d?.choices)
  if(form.value.options.length===0) form.value.options = [{text:''},{text:''}]
  form.value.analysis = d?.analysis ?? d?.explanation ?? ''
  form.value.correct_answer = (d?.correct_answer ?? 'A')
  form.value.is_active = !!(d?.is_active ?? true)
}

async function save(){
  if(!form.value.stem.trim()){ return uni.showToast({ icon:'none', title:'请填写题干' }) }
  if(form.value.options.length<2){ return uni.showToast({ icon:'none', title:'至少两个选项' }) }
  saving.value = true
  try{
    const payload = {
      stem: form.value.stem,
      options: form.value.options.map((o,i)=> ({ key: o.key ?? keyOf(i), text: o.text })),
      correct_answer: form.value.correct_answer,
      analysis: form.value.analysis,
      is_active: form.value.is_active,
    }
    await api.updateQuestion(qid.value, payload)
    uni.showToast({ icon:'success', title:'已保存' })
    setTimeout(()=>goBack(), 400)
  }catch(e:any){
    uni.showToast({ icon:'none', title: e?.data?.message || '保存失败' })
  }finally{ saving.value=false }
}

function goBack(){
  try{
    const pages = getCurrentPages?.()
    if(pages && pages.length>1) return uni.navigateBack()
  }catch(e){}
  uni.reLaunch({ url:'/pages/question-bank/question-bank' })
}

onLoad((opt:any)=>{
  qid.value = Number(opt?.id || 0)
  if(!qid.value){ uni.showToast({ icon:'none', title:'参数错误' }); return setTimeout(()=>goBack(),500) }
  load()
})
</script>

<style scoped>
:root, page, .qe-page{
  --c-bg1:#e8f2ff; --c-bg2:#f5f9ff; --c-panel:#fff; --c-border:#d8e6f5;
  --c-text:#1f2d3d; --c-text-sec:#5f7085; --c-primary:#66b4ff;
  --radius:20rpx; --radius-s:14rpx;
}
.qe-page{ min-height:100vh; background:linear-gradient(180deg,var(--c-bg1),var(--c-bg2)); padding:24rpx 26rpx 120rpx; box-sizing:border-box; }
.card{ background:#fff; border:1rpx solid var(--c-border); border-radius:var(--radius); box-shadow:0 8rpx 24rpx rgba(35,72,130,.08); padding:30rpx; }
.title{ font-size:36rpx; font-weight:700; color:var(--c-text); margin-bottom:16rpx; }
.form{ display:flex; flex-direction:column; gap:18rpx; }
.label{ color:var(--c-text-sec); font-size:26rpx; }
.ipt{ width:100%; min-height:86rpx; padding:16rpx 18rpx; font-size:30rpx; border:1rpx solid var(--c-border); border-radius:var(--radius-s); box-sizing:border-box; }
.area{ min-height:140rpx; }
.opts{ display:flex; flex-direction:column; gap:14rpx; }
.opt{ display:flex; gap:12rpx; align-items:center; }
.correct{ color:var(--c-text-sec); font-size:26rpx; }
.mini{ padding:10rpx 18rpx; border-radius:10rpx; border:1rpx solid var(--c-border); background:#f2f6fb; font-size:26rpx; }
.mini.danger{ border-color:#ffb3b4; color:#ff4d4f; background:#fff5f5; }
.switch-wrap{ display:flex; align-items:center; gap:10rpx; }
.sw-label{ font-size:26rpx; color:var(--c-text-sec); }
.btn{ border:1rpx solid var(--c-border); border-radius:10rpx; font-size:30rpx; padding:22rpx 0; }
.btn.primary{ background:#66b4ff; color:#fff; border-color:#66b4ff; }
.btn.ghost{ background:#f2f6fb; color:#1f2d3d; }
.btn.wide{ width:100%; }
button::after{ border:none; }
</style>
```