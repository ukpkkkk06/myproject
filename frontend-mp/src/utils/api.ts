const API_BASE =
  (import.meta as any).env?.VITE_API_BASE_URL
  || (import.meta as any).env?.VITE_API_BASE
  || 'http://localhost:8000'
const API_PREFIX = (import.meta as any).env?.VITE_API_PREFIX || '/api/v1'

function joinUrl(base: string, prefix: string, path: string) {
  const b = (base || '').replace(/\/+$/, '')
  const p = ('/' + (prefix || '').replace(/^\/+|\/+$/g, '')).replace(/\/+$/, '')
  let s = path.startsWith('/') ? path : `/${path}`
  const re = new RegExp(`^${p.replace(/\//g, '\\/')}`)
  if (p !== '/' && re.test(s)) s = s.replace(re, '')
  return b + p + s
}

export interface User {
  id: number
  account: string
  email?: string | null
  nickname?: string | null
  status?: string | null
  last_login_at?: string | null
}

export interface UsersPage {
  total: number
  items: User[]
}

export interface Token { access_token: string; token_type: string }

type RequestOpts = Omit<UniApp.RequestOptions, 'url' | 'success' | 'fail' | 'complete'>

const ALLOWED_METHODS = ['OPTIONS','GET','HEAD','POST','PUT','DELETE','TRACE','CONNECT'] as const
type HttpMethod = typeof ALLOWED_METHODS[number]
function normalizeMethod(m?: string): HttpMethod {
  const up = (m || 'GET').toUpperCase()
  return (ALLOWED_METHODS.includes(up as HttpMethod) ? up : 'GET') as HttpMethod
}

export function request<T = any>(path: string, options: RequestOpts = {}) {
  return new Promise<T>((resolve, reject) => {
    const token = uni.getStorageSync('token')
    const auth = token ? { Authorization: `Bearer ${token}` } : {}
    const url = joinUrl(API_BASE, API_PREFIX, path)
    const method = normalizeMethod(options.method as any)

    console.log(`[API] ${method} ${url}`, { data: options.data })

    uni.request({
      url,
      method,
      header: { 'Content-Type': 'application/json', ...(options.header || {}), ...auth },
      data: options.data || {},
      success: (res) => {
        console.log(`[API Response] ${method} ${url}`, { statusCode: res.statusCode, data: res.data })
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data as T)
        } else {
          console.error(`[API Error] ${method} ${url}`, res)
          reject(res)
        }
      },
      fail: (err) => {
        console.error(`[API Fail] ${method} ${url}`, err)
        reject(err)
      },
    })
  })
}

export interface UserInfo {
  id: number
  account: string
  status: string
  roles: string[]
  role_codes: string[]
  is_admin: boolean
  email?: string | null
  nickname?: string | null
  created_at?: string | null
  updated_at?: string | null
  last_login_at?: string | null
}

export interface CreateSessionResp {
  attempt_id: number
  paper_id: number
  total: number
  // 兼容两种返回字段名
  start_seq?: number
  first_seq?: number
}
export interface QuestionView { seq: number; question_id: number; type: string; difficulty?: number; stem: string; options: string[]; explanation?: string }
export interface SubmitAnswerResp { seq: number; correct: boolean; correct_answer: string; total: number }

export interface ErrorBookItem { 
  id: number
  question_id: number
  wrong_count: number
  first_wrong_time?: string
  last_wrong_time?: string
  next_review_time?: string
  mastered: boolean
  stem: string  // 🔥 题干字段
}

export interface ErrorBookListResponse {
  total: number
  page: number
  size: number
  items: ErrorBookItem[]
}

export interface MyQuestionItem {
  question_id: number
  stem: string
  type?: string
  difficulty?: number
  audit_status?: string
  updated_at?: string
  created_at?: string
}
export interface MyQuestionListResp {
  total: number
  page: number
  size: number
  items: MyQuestionItem[]
}

export interface QuestionOption { key?: string; text?: string; content?: string; is_correct?: boolean }
export interface QuestionBrief { id: number; stem: string; options?: QuestionOption[]; analysis?: string }

// 刷题分页查询 - 题目项
export interface QuestionPageItem {
  id: number
  stem: string
  type: string
  difficulty?: number
  options?: QuestionOption[]
  correct_answer?: string
  analysis?: string
  tags?: string[]
  subject_id?: number
  subject_name?: string
  level_id?: number
  level_name?: string
  is_active?: boolean
  created_by?: number
  created_at?: string
  updated_at?: string
}

// 刷题分页查询 - 响应结构
export interface QuestionsPageResp {
  total: number
  page: number
  size: number
  items: QuestionPageItem[]
}

// 批量获取题干（若后端支持）
async function getQuestionsBrief(ids: number[]) {
  if (!ids?.length) return { items: [] }
  try { return await request<{ items: QuestionBrief[] }>(`/question-bank/questions/brief?ids=${ids.join(',')}`) } catch {}
  try { return await request<{ items: QuestionBrief[] }>(`/questions/brief?ids=${ids.join(',')}`) } catch {}
  return { items: [] }
}

// 获取题目详情（占位：后端路径因项目而异，按常见路径尝试）

export interface QuestionUpdatePayload {
  stem?: string
  options?: { key?: string; text: string }[] | string[]
  analysis?: string
  correct_answer?: string
  is_active?: boolean
}

export interface QuestionDetail {
  id: number
  stem: string
  options?: any
  analysis?: string
  correct_answer?: string
  is_active?: boolean
}

// 标签
export interface TagItem { id: number; type: 'SUBJECT' | 'LEVEL'; name: string }

// 获取标签列表（参数对象）
function listTags(params: { type?: 'SUBJECT' | 'LEVEL' } = {}) {
  return request<TagItem[]>('/tags', { method: 'GET', data: params })
}

// === 新增题目与标签相关 API ===
async function getQuestionDetail(id: number): Promise<QuestionDetail> {
  // 统一保留此实现
  try { return await request<QuestionDetail>(`/question-bank/questions/${id}`, { method: 'GET' }) }
  catch {
    try { return await request<QuestionDetail>(`/questions/${id}`, { method: 'GET' }) }
    catch { return { id, stem: '', options: [], analysis: '', correct_answer: '', is_active: true } }
  }
}
function updateQuestion(id: number, data: any) {
  return request(`/question-bank/questions/${id}`, { method: 'PUT', data })
}
function getQuestionTags(id: number) {
  return request<{ question_id: number; subject_id?: number|null; level_id?: number|null }>(
    `/question-bank/questions/${id}/tags`,
    { method: 'GET' }
  )
}
function setQuestionTags(id: number, data: { subject_id?: number; level_id?: number }) {
  return request(`/question-bank/questions/${id}/tags`, { method: 'PUT', data })
}

export interface ImportResult {
  total_rows: number
  success: number
  failed: number
  errors: { row: number; reason: string }[]
}

function importQuestionsExcel(filePath: string) {
  const token = uni.getStorageSync('token')
  const base = (import.meta.env.VITE_API_BASE_URL || API_BASE).replace(/\/+$/,'')
  return new Promise<ImportResult>((resolve, reject)=>{
    uni.uploadFile({
      url: base + '/api/v1/question-bank/import-excel',
      filePath,
      name: 'file',
      header: token ? { Authorization: 'Bearer '+token } : {},
      success(res){
        if(res.statusCode>=200 && res.statusCode<300){
          try { resolve(JSON.parse(res.data)) } catch { reject(res) }
        } else reject(res)
      },
      fail(err){ reject(err) }
    })
  })
}

export function downloadImportTemplate(): Promise<string> {
  const base = (import.meta.env.VITE_API_BASE_URL || API_BASE).replace(/\/+$/,'')
  const token = uni.getStorageSync('token')
  return new Promise((resolve, reject)=>{
    uni.downloadFile({
      url: base + '/api/v1/question-bank/import-template',
      header: token ? { Authorization: 'Bearer '+token } : {},
      success(res){
        if(res.statusCode === 200 && res.tempFilePath){
          resolve(res.tempFilePath)
        } else reject(res)
      },
      fail(err){ reject(err) }
    })
  })
}

class API {
  // 健康检查
  health() {
    return request<{ status: string; db?: string }>('/health', { method: 'GET' })
  }

  // 用户分页列表
  users(skip = 0, limit = 10, account?: string, email?: string) {
    return request<UsersPage>('/users', { method: 'GET', data: { skip, limit, account, email } })
  }

  // 更新用户
  updateUser(id: number, data: Partial<Pick<User, 'nickname' | 'email' | 'status'>>) {
    return request<User>(`/users/${id}`, { method: 'PUT', data })
  }

  // 删除用户
  deleteUser(id: number) {
    return request<void>(`/users/${id}`, { method: 'DELETE' })
  }

  // 登录/注册
  login(account: string, password: string) {
    return request<Token>('/login', { method: 'POST', data: { account, password } })
  }

  register(account: string, password: string, email?: string, nickname?: string) {
    return request<User>('/register', { method: 'POST', data: { account, password, email, nickname } })
  }

  // 个人信息
  me() {
    return request<UserInfo>('/me', { method: 'GET' })
  }

  updateMyNickname(nickname: string) {
    return request<UserInfo>('/me/nickname', { method: 'PUT', data: { nickname } })
  }

  changeMyPassword(old_password: string, new_password: string) {
    return request<void>('/me/password', { method: 'PUT', data: { old_password, new_password } })
  }

  usersSimple(skip = 0, limit = 20, account?: string, email?: string) {
    return request<UsersSimplePage>('/users/simple', { method: 'GET', data: { skip, limit, account, email } })
  }

  // 创建练习
  createPractice(
    size: number,  // 🔥 移除默认值,强制传参
    subjectId?: number, 
    knowledgeId?: number, 
    includeChildren: boolean = true, 
    questionTypes?: string[],
    practiceMode: 'RANDOM' | 'SMART' | 'WEAK_POINT' = 'RANDOM'  // 🆕 练习模式
  ) {
    console.log('[API.createPractice] 接收到的参数:', { size, subjectId, knowledgeId, includeChildren, questionTypes, practiceMode })
    return request<CreateSessionResp>('/practice/sessions', {
      method: 'POST',
      data: { 
        size, 
        subject_id: subjectId, 
        knowledge_id: knowledgeId, 
        include_children: includeChildren,
        question_types: questionTypes,  // 🆕 题型参数
        practice_mode: practiceMode  // 🆕 练习模式参数
      }
    })
  }

  // 获取学科列表
  listSubjects() {
    return request<Subject[]>('/practice/subjects', { method: 'GET' })
  }

  // 🆕 获取错题统计
  getErrorStats() {
    return request<{ total_errors: number; unmastered: number }>('/practice/error-stats', { method: 'GET' })
  }

  // 获取知识点树
  listKnowledgeTree() {
    return listKnowledgeTree()
  }

  // 获取练习题目
  getPracticeQuestion(attemptId: number, seq: number) {
    return request<QuestionView>(`/practice/sessions/${attemptId}/questions/${seq}`, { method: 'GET' })
  }

  // 提交练习答案
  submitPracticeAnswer(attemptId: number, seq: number, user_answer: string, time_spent_ms?: number) {
    return request<SubmitAnswerResp>(`/practice/sessions/${attemptId}/answers`, { 
      method: 'POST', 
      data: { seq, user_answer, time_spent_ms } 
    })
  }

  // 🆕 通用分页查询题目 - 用于刷题功能,支持用户自选题目数量
  getQuestions(params: {
    page?: number          // 页码,默认 1
    size?: number          // 每页数量,范围 1-100,默认 10
    keyword?: string       // 搜索关键词(题干)
    qtype?: string         // 题型: single_choice, multiple_choice, true_false, fill_blank, short_answer
    difficulty?: number    // 难度: 1-5
    subject_id?: number    // 学科 ID
    level_id?: number      // 知识层级 ID
  } = {}) {
    return request<QuestionsPageResp>('/questions', {
      method: 'GET',
      data: params
    })
  }

  // 完成练习
  finishPractice(attemptId: number) {
    return request<{ 
      total: number
      answered: number
      correct_count: number
      accuracy: number
      duration_seconds: number 
    }>(`/practice/sessions/${attemptId}/finish`, { method: 'POST' })
  }

  // 获取我的错题本
  getMyErrorBook(
    page: number = 1,
    size: number = 10,
    only_due: boolean = false,
    include_mastered: boolean = false
  ) {
    return request<ErrorBookListResponse>('/error-book', { 
      method: 'GET',
      data: { page, size, only_due, include_mastered }
    })
  }

  // 获取我的题目
  getMyQuestions(params: {
    page?: number
    size?: number
    keyword?: string
    qtype?: string
    difficulty?: number
    active_only?: boolean
    subject_id?: number
    level_id?: number
  }) {
    const payload: any = {
      page: params.page || 1,
      size: params.size || 10,
      active_only: params.active_only === true,
    }
    if (params.keyword) payload.keyword = params.keyword
    if (params.qtype) payload.qtype = params.qtype
    if (typeof params.difficulty === 'number') payload.difficulty = params.difficulty
    if (typeof params.subject_id === 'number') payload.subject_id = params.subject_id
    if (typeof params.level_id === 'number') payload.level_id = params.level_id
    return request('/question-bank/my-questions', { method: 'GET', data: payload })
  }

  // 标签相关
  listTags(params: { type?: 'SUBJECT' | 'LEVEL' } = {}) {
    return listTags(params)
  }

  getQuestionDetail(id: number) {
    return getQuestionDetail(id)
  }

  updateQuestion(id: number, data: any) {
    return updateQuestion(id, data)
  }

  getQuestionTags(id: number) {
    return getQuestionTags(id)
  }

  setQuestionTags(id: number, data: { subject_id?: number; level_id?: number }) {
    return setQuestionTags(id, data)
  }

  importQuestionsExcel(filePath: string) {
    return importQuestionsExcel(filePath)
  }

  downloadImportTemplate() {
    return downloadImportTemplate()
  }

  getQuestionKnowledge(qid: number) {
    return getQuestionKnowledge(qid)
  }

  bindQuestionKnowledge(qid: number, items: QuestionKnowledgeItem[]) {
    return bindQuestionKnowledge(qid, items)
  }
}

export const api = new API()

export interface UserSimple {
  id: number
  account: string
  status: string
  role?: string | null
}
export interface UsersSimplePage { total: number; items: UserSimple[] }

export interface AdminUserDetail {
  id: number
  account: string
  nickname?: string
  email?: string
  status?: string
  roles: { code: string; name?: string }[]
  created_at?: string
  updated_at?: string
  last_login_at?: string
}

export async function adminGetUserDetail(uid: number) {
  return await request<AdminUserDetail>(`/admin/users/${uid}`)
}

export async function adminUpdateUser(uid: number, data: { nickname?: string; email?: string | null; status?: string }) {
  return await request<void>(`/admin/users/${uid}`, { method: 'PUT', data })
}

export async function adminResetUserPassword(uid: number, password: string) {
  return await request<void>(`/admin/users/${uid}/password`, { method: 'PUT', data: { password } })
}

// 管理员统计数据
export interface AdminStats {
  users: { total: number }
  questions: { total: number }
  knowledge: { total: number }
}

export async function adminGetStats() {
  return await request<AdminStats>('/admin/stats')
}

export interface Subject { id:number; name:string }

// 知识点树节点
export interface KnowledgeNode {
  id: number
  name: string
  parent_id?: number | null
  depth?: number | null
  children?: KnowledgeNode[]
}

// 题目-知识点绑定项
export interface QuestionKnowledgeItem {
  knowledge_id: number
  weight?: number
}

// 获取知识点树
export function listKnowledgeTree() {
  return request<KnowledgeNode[]>('/knowledge/tree', { method: 'GET' })
}

// 创建知识点
export function createKnowledgePoint(data: { name: string; parent_id?: number | null; description?: string; level?: number }) {
  return request<KnowledgeNode>('/knowledge', { method: 'POST', data })
}

// 获取某题目已绑定的知识点
export function getQuestionKnowledge(qid: number) {
  return request<Array<{ knowledge_id: number; weight?: number; path?: string }>>(
    `/questions/${qid}/knowledge`,
    { method: 'GET' }
  )
}

// 覆盖式绑定题目的知识点
export function bindQuestionKnowledge(qid: number, items: QuestionKnowledgeItem[]) {
  return request<{ ok: boolean }>(`/questions/${qid}/knowledge`, {
    method: 'PUT',
    data: items,
  })
}

// 兼容旧导出：委托到 api（避免外部仍 import 旧方法时报错）
export function listSubjects(): Promise<Subject[]> { return api.listSubjects() }
export function createPractice(
  size: number,
  subjectId?: number,
  knowledgeId?: number,
  includeChildren: boolean = true,
  questionTypes?: string[],
  practiceMode: 'RANDOM' | 'SMART' | 'WEAK_POINT' = 'RANDOM'
): Promise<CreateSessionResp> {
  console.log('⚠️⚠️⚠️ [兼容导出函数.createPractice] 被调用了!', { size, subjectId, knowledgeId, includeChildren, questionTypes, practiceMode })
  return api.createPractice(size, subjectId, knowledgeId, includeChildren, questionTypes, practiceMode)
}