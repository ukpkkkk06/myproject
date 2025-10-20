<template>
  <view class="practice-page" v-if="loaded">
    <!-- 顶部导航栏 -->
    <view class="top-nav">
      <button class="back-btn" @tap="goBack">
        <text class="back-icon">←</text>
      </button>
      <text class="nav-title">智能练习</text>
      <view class="nav-placeholder"></view>
    </view>

    <view class="card">
      <!-- 顶部进度与题号 - 优化样式 -->
      <view class="head">
        <view class="q-index-wrap">
          <text class="q-label">当前进度</text>
          <view class="q-index">
            <text class="current">{{ seq }}</text>
            <text class="sep">/</text>
            <text class="total">{{ total }}</text>
          </view>
        </view>
        <view class="progress-wrap">
          <view class="progress">
            <view class="bar" :style="{ width: progressPct + '%' }">
              <text class="bar-text" v-if="progressPct > 20">{{ progressPct }}%</text>
            </view>
          </view>
          <text class="progress-text">{{ progressPct }}% 完成</text>
        </view>
      </view>

      <!-- 题干 - 添加图标 -->
      <view class="stem-wrap">
        <text class="stem-icon">📝</text>
        <text class="stem">{{ q?.stem }}</text>
      </view>

      <!-- 选项 - 优化布局,支持单选/多选/填空 -->
      <view class="options-title">
        <text class="options-icon">🎯</text>
        <text>{{ q?.type === 'MC' ? '请选择答案（多选）' : (q?.type === 'FILL' ? '请输入答案' : '请选择答案') }}</text>
      </view>
      
      <!-- 单选题 - radio-group -->
      <radio-group v-if="q?.type === 'SC'" @change="onChoose" :disabled="!!feedback">
        <label
          v-for="(opt,i) in q?.options || []"
          :key="i"
          class="opt"
          :class="optionClass(letters[i])"
        >
          <view class="opt-header">
            <view class="bullet" :class="bulletClass(letters[i])">
              <text class="b-text">{{ letters[i] }}</text>
            </view>
            <radio :value="letters[i]" :checked="sel === letters[i]" color="#66b4ff" style="display:none" />
          </view>
          <text class="opt-text">{{ opt }}</text>
          <!-- 添加状态图标 -->
          <view v-if="feedback" class="status-icon">
            <text v-if="feedback.correct_answer.includes(letters[i])">✓</text>
            <text v-else-if="!feedback.correct && sel === letters[i]">✗</text>
          </view>
        </label>
      </radio-group>
      
      <!-- 多选题 - checkbox-group -->
      <checkbox-group v-else-if="q?.type === 'MC'" @change="onChooseMulti" :disabled="!!feedback">
        <label
          v-for="(opt,i) in q?.options || []"
          :key="i"
          class="opt"
          :class="optionClassMulti(letters[i])"
        >
          <view class="opt-header">
            <view class="bullet multi" :class="bulletClassMulti(letters[i])">
              <text class="b-text">{{ letters[i] }}</text>
            </view>
            <checkbox :value="letters[i]" :checked="multiSel.includes(letters[i])" color="#66b4ff" style="display:none" />
          </view>
          <text class="opt-text">{{ opt }}</text>
          <!-- 添加状态图标 -->
          <view v-if="feedback" class="status-icon">
            <text v-if="feedback.correct_answer.includes(letters[i])">✓</text>
            <text v-else-if="!feedback.correct && multiSel.includes(letters[i])">✗</text>
          </view>
        </label>
      </checkbox-group>
      
      <!-- 🆕 填空题 - input输入框 -->
      <view v-else-if="q?.type === 'FILL'" class="fill-input-wrap">
        <input 
          v-model="fillAnswer"
          :disabled="!!feedback"
          class="fill-input"
          :class="{ 'fill-correct': feedback?.correct, 'fill-wrong': feedback && !feedback.correct }"
          placeholder="请输入答案"
          @input="onFillInput"
        />
        <text class="fill-hint">💡 支持多个答案用分号分隔,如: 答案1;答案2</text>
        <view v-if="feedback && !feedback.correct" class="fill-answer-hint">
          <text class="hint-label">正确答案：</text>
          <text class="hint-value">{{ feedback.correct_answer }}</text>
        </view>
      </view>

      <!-- 提交按钮 - 优化样式,支持单选/多选/填空 -->
      <button
        class="btn primary submit"
        :disabled="getSubmitDisabled() || posting || !!feedback"
        @tap="submit"
      >
        <text class="btn-icon" v-if="!posting">✓</text>
        <text>{{ posting ? '提交中…' : '提交答案' }}</text>
      </button>

      <!-- 反馈卡片 - 优化布局 -->
      <view v-if="feedback" class="feedback-card" :class="feedback.correct ? 'ok' : 'bad'">
        <view class="feedback-header">
          <text class="feedback-icon">{{ feedback.correct ? '🎉' : '💡' }}</text>
          <text class="feedback-title">
            {{ feedback.correct ? '回答正确！' : '回答错误' }}
          </text>
        </view>
        <view class="feedback-content">
          <text v-if="!feedback.correct" class="correct-answer">
            正确答案：<text class="answer-letter">{{ feedback.correct_answer }}</text>
          </text>
        </view>
      </view>

      <!-- 解析卡片 -->
      <view v-if="feedback" class="explain-card">
        <view class="explain-header">
          <text class="explain-icon">📖</text>
          <text class="explain-title">题目解析</text>
        </view>
        <text class="explain-text">{{ q?.explanation || '暂无解析' }}</text>
      </view>

      <!-- 操作按钮 - 优化布局 -->
      <view v-if="feedback" class="actions">
        <button class="btn outline redo-btn" @tap="redo">
          <text class="btn-icon">↻</text>
          <text>重做本题</text>
        </button>
        <button
          class="btn primary next-btn"
          v-if="seq < total"
          @tap="next"
        >
          <text>下一题</text>
          <text class="btn-icon">→</text>
        </button>
        <button
          class="btn finish-btn"
          v-else
          @tap="finish"
        >
          <text class="btn-icon">🏁</text>
          <text>完成练习</text>
        </button>
      </view>
    </view>

    <!-- 悬浮提示 - 支持单选/多选/填空 -->
    <view v-if="!feedback && (sel || multiSel.length || fillAnswer.trim())" class="float-tip">
      <text>已{{ q?.type === 'FILL' ? '输入' : '选择' }}：{{ q?.type === 'MC' ? multiSel.sort().join('') : (q?.type === 'FILL' ? fillAnswer : sel) }}</text>
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
const sel = ref('')  // 单选答案
const multiSel = ref<string[]>([])  // 🆕 多选答案数组
const fillAnswer = ref('')  // 🆕 填空题答案
const feedback = ref<SubmitAnswerResp|null>(null)
const loaded = ref(false)
const posting = ref(false)
const letters = ['A','B','C','D','E','F']
let t0 = 0

function toast(t:string){ uni.showToast({ icon:'none', title:t }) }

// 单选事件
function onChoose(e:any){ 
  sel.value = e.detail.value 
}

// 🆕 多选事件
function onChooseMulti(e:any){ 
  multiSel.value = e.detail.value || []
}

// 🆕 填空题输入事件
function onFillInput(e:any){ 
  fillAnswer.value = e.detail.value 
}

// 🆕 判断提交按钮是否禁用
function getSubmitDisabled() {
  if (q.value?.type === 'MC') return !multiSel.value.length
  if (q.value?.type === 'FILL') return !fillAnswer.value.trim()
  return !sel.value
}

const progressPct = computed(()=> {
  if(!total.value) return 0
  const done = seq.value - 1 + (feedback.value ? 1 : 0)
  return Math.min(100, Math.round(done / total.value * 100))
})

// 单选样式
function optionClass(letter:string){
  if(!feedback.value) return { chosen: sel.value === letter }
  const right = feedback.value.correct_answer.includes(letter)
  const wrongChosen = !feedback.value.correct && sel.value === letter
  return { right, wrong: wrongChosen, chosen: sel.value === letter }
}
function bulletClass(letter:string){
  if(!feedback.value) return { chosen: sel.value === letter }
  const right = feedback.value.correct_answer.includes(letter)
  const wrongChosen = !feedback.value.correct && sel.value === letter
  return { right, wrong: wrongChosen, chosen: sel.value === letter }
}

// 🆕 多选样式
function optionClassMulti(letter:string){
  if(!feedback.value) return { chosen: multiSel.value.includes(letter) }
  const right = feedback.value.correct_answer.includes(letter)
  const wrongChosen = !feedback.value.correct && multiSel.value.includes(letter) && !right
  return { right, wrong: wrongChosen, chosen: multiSel.value.includes(letter) }
}
function bulletClassMulti(letter:string){
  if(!feedback.value) return { chosen: multiSel.value.includes(letter) }
  const right = feedback.value.correct_answer.includes(letter)
  const wrongChosen = !feedback.value.correct && multiSel.value.includes(letter) && !right
  return { right, wrong: wrongChosen, chosen: multiSel.value.includes(letter) }
}

async function loadQuestion(s:number){
  uni.showLoading({ title:'加载中' })
  try{
    q.value = await api.getPracticeQuestion(attemptId.value, s)
    seq.value = s
    sel.value = ''
    multiSel.value = []  // 🆕 重置多选
    fillAnswer.value = ''  // 🆕 重置填空
    feedback.value = null
    t0 = Date.now()
    await nextTick()
    uni.pageScrollTo({ scrollTop:0, duration:0 })
  } finally { uni.hideLoading() }
}

async function submit(){
  // 🆕 根据题型获取答案
  let answer = ''
  if(q.value?.type === 'MC') {
    if(!multiSel.value.length) return
    // 多选答案排序后拼接
    answer = multiSel.value.sort().join('')
  } else if(q.value?.type === 'FILL') {
    // 🆕 填空题答案
    if(!fillAnswer.value.trim()) return
    answer = fillAnswer.value.trim()
  } else {
    if(!sel.value) return
    answer = sel.value
  }
  
  if(posting.value) return
  posting.value = true
  try{
    const spent = Date.now()-t0
    feedback.value = await api.submitPracticeAnswer(attemptId.value, seq.value, answer, spent)
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

function goBack(){
  uni.showModal({
    title:'确认退出',
    content:'退出后进度将保存，可稍后继续',
    success(res){
      if(res.confirm) uni.navigateBack()
    }
  })
}

onMounted(async ()=>{
  try{
    const token = uni.getStorageSync('token')
    if(!token) return uni.reLaunch({ url:'/pages/login/login' })
    const resp:CreateSessionResp = await api.createPractice(5)
    attemptId.value = resp.attempt_id
    total.value = resp.total
    // 🔥 修复：使用 ?? 运算符提供默认值
    const startSeq = resp.first_seq ?? resp.start_seq ?? 1
    await loadQuestion(startSeq)
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
  --c-green-border:#b8eed5;
  --c-red:#ff4d4f;
  --c-red-bg:#fff1f0;
  --c-red-border:#ffccc7;
  --radius:24rpx;
  --radius-s:16rpx;
  --shadow-sm:0 4rpx 12rpx rgba(35,72,130,.06);
  --shadow-md:0 8rpx 24rpx rgba(35,72,130,.08),0 2rpx 6rpx rgba(35,72,130,.06);
  --shadow-lg:0 12rpx 36rpx rgba(35,72,130,.12);
}

.practice-page{
  min-height:100vh;
  padding:120rpx 32rpx 140rpx;
  box-sizing:border-box;
  background:linear-gradient(180deg,var(--c-bg-grad-top),var(--c-bg-grad-bottom));
  display:flex;
  flex-direction:column;
  position:relative;
}

/* 🎨 顶部导航 */
.top-nav{
  position:fixed;
  top:0; left:0; right:0;
  height:120rpx;
  padding:40rpx 32rpx 0;
  box-sizing:border-box;
  display:flex;
  align-items:center;
  justify-content:space-between;
  backdrop-filter:blur(20px) saturate(180%);
  background:rgba(255,255,255,.65);
  border-bottom:1rpx solid rgba(214,230,245,.6);
  box-shadow:var(--shadow-sm);
  z-index:100;
}

.back-btn{
  width:72rpx; height:72rpx;
  background:linear-gradient(135deg, var(--c-primary-light), #fff);
  border:2rpx solid var(--c-primary);
  border-radius:50%;
  display:flex;
  align-items:center;
  justify-content:center;
  box-shadow:var(--shadow-sm);
  padding:0;
  transition:all .2s ease;
}
.back-btn:active{
  transform:scale(.92);
  box-shadow:var(--shadow-md);
}
.back-icon{
  font-size:36rpx;
  color:var(--c-primary-dark);
  font-weight:700;
}

.nav-title{
  font-size:36rpx;
  font-weight:700;
  color:var(--c-text);
  letter-spacing:.5rpx;
}

.nav-placeholder{
  width:72rpx;
}

/* 🎨 主卡片 */
.card{
  background:var(--c-panel);
  border:1rpx solid var(--c-border);
  border-radius:var(--radius);
  padding:48rpx 40rpx 60rpx;
  box-shadow:var(--shadow-md);
  flex:1;
  display:flex;
  flex-direction:column;
  animation:fadeInUp .5s ease;
}

@keyframes fadeInUp{
  from{ opacity:0; transform:translateY(30rpx); }
  to{ opacity:1; transform:translateY(0); }
}

/* 🎨 进度区域优化 */
.head{
  display:flex;
  flex-direction:column;
  gap:24rpx;
  margin-bottom:32rpx;
  padding-bottom:28rpx;
  border-bottom:2rpx dashed var(--c-border);
}

.q-index-wrap{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:20rpx;
}

.q-label{
  font-size:26rpx;
  color:var(--c-text-sec);
  font-weight:600;
}

.q-index{
  display:flex;
  align-items:baseline;
  gap:6rpx;
  padding:10rpx 24rpx;
  background:linear-gradient(135deg, var(--c-primary-light), #e8f5ff);
  border-radius:30rpx;
  box-shadow:var(--shadow-sm);
}

.current{
  font-size:36rpx;
  font-weight:700;
  color:var(--c-primary-dark);
}

.sep{
  font-size:28rpx;
  color:var(--c-text-sec);
  font-weight:600;
}

.total{
  font-size:28rpx;
  color:var(--c-text-sec);
  font-weight:600;
}

.progress-wrap{
  display:flex;
  flex-direction:column;
  gap:12rpx;
}

.progress{
  width:100%;
  height:20rpx;
  background:#edf3f9;
  border-radius:12rpx;
  overflow:hidden;
  box-shadow:inset 0 2rpx 4rpx rgba(0,0,0,.06);
}

.bar{
  height:100%;
  background:linear-gradient(90deg,#a9d6ff,#66b4ff,#4b9ef0);
  border-radius:12rpx;
  display:flex;
  align-items:center;
  justify-content:flex-end;
  padding-right:16rpx;
  transition:width .4s cubic-bezier(.4,0,.2,1);
  box-shadow:0 2rpx 8rpx rgba(102,180,255,.4);
}

.bar-text{
  font-size:20rpx;
  color:#fff;
  font-weight:700;
  text-shadow:0 1rpx 2rpx rgba(0,0,0,.2);
}

.progress-text{
  font-size:24rpx;
  color:var(--c-primary-dark);
  font-weight:600;
  text-align:right;
}

/* 🎨 题干优化 */
.stem-wrap{
  display:flex;
  align-items:flex-start;
  gap:16rpx;
  margin-bottom:40rpx;
  padding:28rpx;
  background:linear-gradient(135deg, #f8fafc, #fff);
  border:1rpx solid var(--c-border);
  border-radius:var(--radius-s);
  box-shadow:var(--shadow-sm);
}

.stem-icon{
  font-size:44rpx;
  line-height:1;
  flex-shrink:0;
}

.stem{
  flex:1;
  font-size:32rpx;
  font-weight:600;
  line-height:1.65;
  color:var(--c-text);
  letter-spacing:.5rpx;
}

/* 🎨 选项标题 */
.options-title{
  display:flex;
  align-items:center;
  gap:12rpx;
  margin-bottom:24rpx;
  font-size:28rpx;
  color:var(--c-text-sec);
  font-weight:600;
}

.options-icon{
  font-size:32rpx;
}

/* 🎨 选项优化 */
.opt{
  display:flex;
  align-items:flex-start;
  gap:20rpx;
  padding:28rpx 32rpx;
  border:2rpx solid var(--c-border);
  border-radius:var(--radius-s);
  background:#fff;
  margin-bottom:20rpx;
  line-height:1.6;
  position:relative;
  font-size:30rpx;
  transition:all .25s cubic-bezier(.4,0,.2,1);
  box-shadow:var(--shadow-sm);
}

.opt:last-child{margin-bottom:0;}

.opt:active{
  transform:translateY(2rpx);
}

.opt.chosen{
  background:linear-gradient(135deg, #f5fbff, #fff);
  border-color:var(--c-primary);
  box-shadow:0 0 0 6rpx var(--c-primary-light), var(--shadow-md);
}

.opt.right{
  background:linear-gradient(135deg, var(--c-green-bg), #fff);
  border-color:var(--c-green);
  box-shadow:0 0 0 6rpx rgba(56,178,111,.15), var(--shadow-md);
  animation:pulse .5s ease;
}

.opt.wrong{
  background:linear-gradient(135deg, var(--c-red-bg), #fff);
  border-color:var(--c-red);
  box-shadow:0 0 0 6rpx rgba(255,77,79,.15), var(--shadow-md);
  animation:shake .5s ease;
}

@keyframes pulse{
  0%, 100%{ transform:scale(1); }
  50%{ transform:scale(1.02); }
}

@keyframes shake{
  0%, 100%{ transform:translateX(0); }
  25%{ transform:translateX(-8rpx); }
  75%{ transform:translateX(8rpx); }
}

.opt-header{
  display:flex;
  align-items:center;
  gap:20rpx;
  flex-shrink:0;
}

.opt-text{
  flex:1;
  color:var(--c-text);
  font-weight:500;
  word-break:break-all;
}

.opt.right .opt-text{
  color:var(--c-green);
  font-weight:600;
}

.opt.wrong .opt-text{
  color:var(--c-red);
  font-weight:600;
}

.bullet{
  width:56rpx;
  height:56rpx;
  border:3rpx solid var(--c-border-strong);
  border-radius:50%;
  display:flex;
  align-items:center;
  justify-content:center;
  font-size:28rpx;
  background:#fff;
  color:var(--c-text-sec);
  flex-shrink:0;
  transition:all .25s cubic-bezier(.4,0,.2,1);
  font-weight:700;
}

/* 🆕 多选题方形样式 */
.bullet.multi{
  border-radius:12rpx;
}

.bullet.chosen{
  border-color:var(--c-primary);
  background:linear-gradient(135deg,#a9d6ff,#66b4ff);
  color:#fff;
  box-shadow:0 4rpx 12rpx rgba(102,180,255,.4);
  transform:scale(1.1);
}

/* 🆕 填空题样式 */
.fill-input-wrap{
  margin-bottom:32rpx;
  display:flex;
  flex-direction:column;
  gap:16rpx;
}

.fill-input{
  width:100%;
  padding:24rpx 32rpx;
  border:2rpx solid var(--c-border);
  border-radius:var(--radius);
  font-size:28rpx;
  background:#fff;
  color:var(--c-text);
  transition:all .25s ease;
  box-shadow:var(--shadow-sm);
}

.fill-input:focus{
  border-color:var(--c-primary);
  box-shadow:0 0 0 4rpx var(--c-primary-light), var(--shadow-md);
  outline:none;
}

.fill-input.fill-correct{
  border-color:var(--c-green);
  background:var(--c-green-bg);
  color:var(--c-green);
  font-weight:600;
}

.fill-input.fill-wrong{
  border-color:var(--c-red);
  background:var(--c-red-bg);
  color:var(--c-red);
  font-weight:600;
}

.fill-hint{
  display:block;
  font-size:24rpx;
  color:var(--c-text-sec);
  padding-left:8rpx;
}

.fill-answer-hint{
  display:flex;
  align-items:center;
  gap:12rpx;
  padding:20rpx 24rpx;
  background:var(--c-green-bg);
  border:2rpx solid var(--c-green-border);
  border-radius:var(--radius-s);
}

.hint-label{
  font-size:26rpx;
  color:var(--c-text-sec);
  font-weight:600;
}

.hint-value{
  font-size:28rpx;
  color:var(--c-green);
  font-weight:700;
}

.bullet.right{
  border-color:var(--c-green);
  background:var(--c-green);
  color:#fff;
  box-shadow:0 4rpx 12rpx rgba(56,178,111,.35);
  transform:scale(1.1);
}

.bullet.wrong{
  border-color:var(--c-red);
  background:var(--c-red);
  color:#fff;
  box-shadow:0 4rpx 12rpx rgba(255,77,79,.35);
  transform:scale(1.1);
}

.status-icon{
  position:absolute;
  right:28rpx;
  top:28rpx;
  font-size:40rpx;
  line-height:1;
  animation:zoomIn .3s ease;
}

@keyframes zoomIn{
  from{ opacity:0; transform:scale(.5); }
  to{ opacity:1; transform:scale(1); }
}

/* 🎨 按钮优化 */
.btn{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:10rpx;
  width:100%;
  border:none;
  border-radius:var(--radius-s);
  font-size:32rpx;
  font-weight:700;
  padding:32rpx 0;
  letter-spacing:1rpx;
  color:#fff;
  background:#ccc;
  box-shadow:var(--shadow-md);
  margin-top:32rpx;
  transition:all .25s cubic-bezier(.4,0,.2,1);
  position:relative;
  overflow:hidden;
}

.btn::before{
  content:'';
  position:absolute;
  top:0; left:0; right:0; bottom:0;
  background:linear-gradient(135deg, rgba(255,255,255,.2), transparent);
  opacity:0;
  transition:opacity .25s ease;
}

.btn:active::before{
  opacity:1;
}

.btn-icon{
  font-size:36rpx;
  line-height:1;
}

.btn.primary{
  background:linear-gradient(135deg,#a9d6ff,#66b4ff,#4b9ef0);
  box-shadow:0 8rpx 20rpx rgba(102,180,255,.4), var(--shadow-md);
}

.btn.outline{
  background:#fff;
  color:var(--c-primary-dark);
  border:3rpx solid var(--c-primary);
  box-shadow:var(--shadow-sm);
}

.btn.finish-btn{
  background:linear-gradient(135deg,#ffd666,#ffa940,#ff8533);
  box-shadow:0 8rpx 20rpx rgba(255,169,64,.4), var(--shadow-md);
}

.btn:active{
  opacity:.9;
  transform:translateY(2rpx) scale(.98);
}

.btn[disabled]{
  opacity:.5;
  transform:none;
}

.submit{margin-top:12rpx;}

button::after{border:none;}

/* 🎨 反馈卡片优化 */
.feedback-card{
  margin-top:40rpx;
  padding:32rpx;
  border-radius:var(--radius);
  display:flex;
  flex-direction:column;
  gap:16rpx;
  box-shadow:var(--shadow-md);
  animation:slideInUp .4s ease;
}

@keyframes slideInUp{
  from{ opacity:0; transform:translateY(20rpx); }
  to{ opacity:1; transform:translateY(0); }
}

.feedback-card.ok{
  background:linear-gradient(135deg, var(--c-green-bg), #f0fff9);
  border:2rpx solid var(--c-green-border);
}

.feedback-card.bad{
  background:linear-gradient(135deg, var(--c-red-bg), #fff5f5);
  border:2rpx solid var(--c-red-border);
}

.feedback-header{
  display:flex;
  align-items:center;
  gap:16rpx;
}

.feedback-icon{
  font-size:48rpx;
  line-height:1;
}

.feedback-title{
  font-size:32rpx;
  font-weight:700;
  letter-spacing:.5rpx;
}

.feedback-card.ok .feedback-title{
  color:var(--c-green);
}

.feedback-card.bad .feedback-title{
  color:var(--c-red);
}

.feedback-content{
  font-size:28rpx;
  line-height:1.6;
  padding-left:64rpx;
}

.correct-answer{
  color:var(--c-text-sec);
  font-weight:500;
}

.answer-letter{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  width:48rpx;
  height:48rpx;
  background:var(--c-red);
  color:#fff;
  border-radius:50%;
  font-weight:700;
  margin:0 8rpx;
  font-size:26rpx;
  box-shadow:0 4rpx 12rpx rgba(255,77,79,.3);
}

/* 🎨 解析卡片 */
.explain-card{
  margin-top:24rpx;
  padding:32rpx;
  background:linear-gradient(135deg, #f8fafc, #fff);
  border:1rpx solid var(--c-border);
  border-radius:var(--radius);
  box-shadow:var(--shadow-sm);
  display:flex;
  flex-direction:column;
  gap:20rpx;
  animation:slideInUp .4s ease .1s backwards;
}

.explain-header{
  display:flex;
  align-items:center;
  gap:12rpx;
  padding-bottom:16rpx;
  border-bottom:1rpx dashed var(--c-border);
}

.explain-icon{
  font-size:36rpx;
  line-height:1;
}

.explain-title{
  font-size:28rpx;
  font-weight:700;
  color:var(--c-text);
}

.explain-text{
  font-size:28rpx;
  line-height:1.75;
  color:var(--c-text-sec);
  font-weight:500;
  text-indent:2em;
}

/* 🎨 操作按钮区域 */
.actions{
  display:flex;
  gap:24rpx;
  margin-top:40rpx;
  flex-wrap:wrap;
}

.actions .btn{
  flex:1;
  margin-top:0;
  min-width:240rpx;
}

/* 🎨 悬浮提示 */
.float-tip{
  position:fixed;
  bottom:60rpx;
  left:50%;
  transform:translateX(-50%);
  padding:20rpx 40rpx;
  background:rgba(31,45,61,.92);
  color:#fff;
  font-size:26rpx;
  font-weight:600;
  border-radius:60rpx;
  box-shadow:0 8rpx 24rpx rgba(0,0,0,.25);
  backdrop-filter:blur(10px);
  z-index:50;
  animation:slideUp .3s ease;
}

@keyframes slideUp{
  from{ opacity:0; transform:translate(-50%, 20rpx); }
  to{ opacity:1; transform:translate(-50%, 0); }
}

/* 响应式 */
@media (min-width:700rpx){
  .card{
    max-width:840rpx;
    margin:0 auto;
  }
  .actions .btn{
    flex:0 0 calc(50% - 12rpx);
  }
}
</style>
