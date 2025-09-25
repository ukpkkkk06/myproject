<template>
  <view class="practice-page" v-if="loaded">
    <view class="card">

      <!-- 顶部进度与题号 -->
      <view class="head">
        <view class="q-index">
          第 <text class="strong">{{ seq }}</text>/<text class="total">{{ total }}</text> 题
        </view>
        <view class="progress">
          <view class="bar" :style="{ width: progressPct + '%' }"></view>
        </view>
      </view>

      <!-- 题干 -->
      <view class="stem">{{ q?.stem }}</view>

      <!-- 选项 -->
      <radio-group @change="onChoose" :disabled="!!feedback">
        <label
          v-for="(opt,i) in q?.options || []"
          :key="i"
          class="opt"
          :class="optionClass(letters[i])"
        >
          <view class="bullet" :class="bulletClass(letters[i])">
            <text class="b-text">{{ letters[i] }}</text>
          </view>
          <radio :value="letters[i]" :checked="sel === letters[i]" color="#66b4ff" style="display:none" />
          <text class="opt-text">{{ opt }}</text>
        </label>
      </radio-group>

      <!-- 提交按钮 -->
      <button
        class="btn primary submit"
        :disabled="!sel || posting || !!feedback"
        @tap="submit"
      >
        {{ posting ? '提交中…' : '提交答案' }}
      </button>

      <!-- 反馈 -->
      <view v-if="feedback" class="feedback" :class="feedback.correct ? 'ok' : 'bad'">
        <text v-if="feedback.correct">答对啦 ✔</text>
        <text v-else>答错啦，正确答案：{{ feedback.correct_answer }}</text>
      </view>
      <view v-if="feedback" class="explain">
        解析：{{ q?.explanation || '暂无解析' }}
      </view>

      <!-- 操作按钮 -->
      <view v-if="feedback" class="actions">
        <button class="btn outline" @tap="redo">重做本题</button>
        <button
          class="btn primary"
          v-if="seq < total"
          @tap="next"
        >下一题</button>
        <button
          class="btn danger"
          v-else
          @tap="finish"
        >完成练习</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { api, type QuestionView, type SubmitAnswerResp, type CreateSessionResp } from '@/utils/api'

const attemptId = ref(0)
const total = ref(0)
const seq = ref(1)
const q = ref<QuestionView|null>(null)
const sel = ref('')
const feedback = ref<SubmitAnswerResp|null>(null)
const loaded = ref(false)
const posting = ref(false)
const letters = ['A','B','C','D','E','F']
let t0 = 0

function toast(t:string){ uni.showToast({ icon:'none', title:t }) }
function onChoose(e:any){ sel.value = e.detail.value }
const progressPct = computed(()=> {
  if(!total.value) return 0
  const done = seq.value - 1 + (feedback.value ? 1 : 0)
  return Math.min(100, Math.round(done / total.value * 100))
})

function optionClass(letter:string){
  if(!feedback.value) return { chosen: sel.value === letter }
  const right = feedback.value.correct_answer === letter
  const wrongChosen = !feedback.value.correct && sel.value === letter
  return { right, wrong: wrongChosen, chosen: sel.value === letter }
}
function bulletClass(letter:string){
  if(!feedback.value) return { chosen: sel.value === letter }
  const right = feedback.value.correct_answer === letter
  const wrongChosen = !feedback.value.correct && sel.value === letter
  return { right, wrong: wrongChosen, chosen: sel.value === letter }
}

async function loadQuestion(s:number){
  uni.showLoading({ title:'加载中' })
  try{
    q.value = await api.getPracticeQuestion(attemptId.value, s)
    seq.value = s
    sel.value = ''
    feedback.value = null
    t0 = Date.now()
    await nextTick()
    uni.pageScrollTo({ scrollTop:0, duration:0 })
  } finally { uni.hideLoading() }
}

async function submit(){
  if(!sel.value || posting.value) return
  posting.value = true
  try{
    const spent = Date.now()-t0
    feedback.value = await api.submitPracticeAnswer(attemptId.value, seq.value, sel.value, spent)
  } catch(e:any){
    toast(e?.data?.message || '提交失败')
  } finally { posting.value = false }
}

async function redo(){ await loadQuestion(seq.value) }
async function next(){ if(seq.value < total.value) await loadQuestion(seq.value+1) }
async function finish(){
  try{
    const r = await api.finishPractice(attemptId.value)
    toast(`正确 ${r.correct_count}/${r.total}（${Math.round(r.accuracy*100)}%）`)
    setTimeout(()=> uni.navigateBack(), 800)
  } catch(e:any){
    toast(e?.data?.message || '结束失败')
  }
}

onMounted(async ()=>{
  try{
    const token = uni.getStorageSync('token')
    if(!token) return uni.reLaunch({ url:'/pages/login/login' })
    const resp:CreateSessionResp = await api.createPractice(5)
    attemptId.value = resp.attempt_id
    total.value = resp.total
    await loadQuestion(resp.first_seq)
    loaded.value = true
  } catch(e:any){
    if(e?.statusCode === 401) uni.reLaunch({ url:'/pages/login/login' })
    else toast(e?.data?.message || '加载失败')
  }
})
</script>

<style scoped>
:root, page, .practice-page {
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
  --c-green:#38b26f;
  --c-green-bg:#e6fff5;
  --c-red:#ff4d4f;
  --c-red-bg:#fff1f0;
  --radius:20rpx;
  --radius-s:14rpx;
}
.practice-page{
  min-height:100vh;
  padding:40rpx 32rpx 120rpx;
  box-sizing:border-box;
  background:linear-gradient(180deg,var(--c-bg-grad-top),var(--c-bg-grad-bottom));
  display:flex;
  flex-direction:column;
}
.card{
  background:var(--c-panel);
  border:1rpx solid var(--c-border);
  border-radius:var(--radius);
  padding:46rpx 40rpx 60rpx;
  box-shadow:0 8rpx 24rpx rgba(35,72,130,0.08),0 2rpx 6rpx rgba(35,72,130,0.06);
  flex:1;
  display:flex;
  flex-direction:column;
}
.head{display:flex; flex-direction:column; gap:20rpx; margin-bottom:12rpx;}
.q-index{font-size:30rpx; color:var(--c-text-sec);}
.q-index .strong{font-weight:600; color:var(--c-text);}
.progress{width:100%; height:12rpx; background:#edf3f9; border-radius:8rpx; overflow:hidden;}
.bar{height:100%; background:linear-gradient(90deg,#a9d6ff,#66b4ff); transition:width .28s;}
.stem{font-size:34rpx; font-weight:600; line-height:1.55; margin:8rpx 0 32rpx; color:var(--c-text);}

.opt{
  display:flex;
  align-items:flex-start;
  gap:20rpx;
  padding:24rpx 22rpx;
  border:1rpx solid var(--c-border);
  border-radius:var(--radius-s);
  background:#fff;
  margin-bottom:20rpx;
  line-height:1.5;
  position:relative;
  font-size:30rpx;
  transition:background .15s,border-color .15s,box-shadow .15s;
}
.opt:last-child{margin-bottom:0;}
.opt.chosen{background:#f5fbff; border-color:var(--c-primary-light);}
.opt.right{background:var(--c-green-bg); border-color:var(--c-green);}
.opt.wrong{background:var(--c-red-bg); border-color:var(--c-red);}
.opt-text{flex:1; color:var(--c-text);}
.opt.right .opt-text{color:var(--c-green);}
.opt.wrong .opt-text{color:var(--c-red);}

.bullet{
  width:48rpx; height:48rpx;
  border:2rpx solid var(--c-border-strong);
  border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  font-size:26rpx;
  background:#fff;
  color:var(--c-text-sec);
  flex-shrink:0;
  transition:all .18s;
}
.bullet.chosen{
  border-color:var(--c-primary);
  background:linear-gradient(135deg,#a9d6ff,#66b4ff);
  color:#fff;
  box-shadow:0 4rpx 10rpx rgba(102,180,255,.35);
}
.bullet.right{
  border-color:var(--c-green);
  background:var(--c-green);
  color:#fff;
  box-shadow:0 4rpx 10rpx rgba(56,178,111,.28);
}
.bullet.wrong{
  border-color:var(--c-red);
  background:var(--c-red);
  color:#fff;
  box-shadow:0 4rpx 10rpx rgba(255,77,79,.28);
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
  margin-top:24rpx;
  transition:opacity .18s;
}
.btn.primary{
  background:linear-gradient(90deg,#a9d6ff,#66b4ff);
  box-shadow:0 6rpx 14rpx rgba(102,180,255,.35);
}
.btn.outline{
  background:#fff;
  color:var(--c-primary-dark);
  border:2rpx solid var(--c-primary);
  box-shadow:none;
}
.btn.danger{
  background:linear-gradient(90deg,#ff6a6c,#ff4d4f);
  box-shadow:0 6rpx 14rpx rgba(255,77,79,.3);
}
.btn:active{opacity:.86;}
.btn[disabled]{opacity:.5;}

.submit{margin-top:8rpx;}

.feedback{
  margin-top:30rpx;
  padding:22rpx 26rpx;
  border-radius:var(--radius-s);
  font-size:30rpx;
  font-weight:500;
  line-height:1.4;
  display:flex;
  align-items:center;
  gap:8rpx;
}
.feedback.ok{background:var(--c-green-bg); color:var(--c-green);}
.feedback.bad{background:var(--c-red-bg); color:var(--c-red);}
.explain{
  margin-top:18rpx;
  font-size:26rpx;
  line-height:1.6;
  color:var(--c-text-sec);
  background:#f6f9fc;
  border:1rpx solid var(--c-border);
  padding:20rpx 24rpx;
  border-radius:var(--radius-s);
}

.actions{
  display:flex;
  gap:28rpx;
  margin-top:34rpx;
  flex-wrap:wrap;
}
.actions .btn{
  flex:1;
  margin-top:0;
  min-width:240rpx;
}

@media (min-width:700rpx){
  .card{max-width:840rpx; margin:0 auto;}
  .actions .btn{flex:0 0 calc(50% - 14rpx);}
}
</style>
