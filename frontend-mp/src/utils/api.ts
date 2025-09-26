const API_BASE =
  (import.meta as any).env?.VITE_API_BASE_URL
  || (import.meta as any).env?.VITE_API_BASE
  || 'http://127.0.0.1:8000'
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
        if (res.statusCode >= 200 && res.statusCode < 300) resolve(res.data as T)
        else reject(res)
      },
      fail: (err) => reject(err),
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

export interface CreateSessionResp { attempt_id: number; paper_id: number; total: number; first_seq: number }
export interface QuestionView { seq: number; question_id: number; type: string; difficulty?: number; stem: string; options: string[]; explanation?: string }
export interface SubmitAnswerResp { seq: number; correct: boolean; correct_answer: string; total: number }

export interface ErrorBookItem { id: number; question_id: number; wrong_count: number; first_wrong_time?: string; last_wrong_time?: string; next_review_time?: string; mastered: boolean }
export interface ErrorBookListResp { total: number; page: number; size: number; items: ErrorBookItem[] }

export interface MyQuestionItem {
  question_id: number
  type: string
  difficulty?: number
  stem: string
  audit_status: string
  is_active: boolean
  created_at: string
  updated_at: string
}
export interface MyQuestionListResp {
  total: number
  page: number
  size: number
  items: MyQuestionItem[]
}

export interface QuestionOption { key?: string; text?: string; content?: string; is_correct?: boolean }
export interface QuestionBrief { id: number; stem: string; options?: QuestionOption[]; analysis?: string }

// 批量获取题干（若后端支持）
async function getQuestionsBrief(ids: number[]) {
  if (!ids?.length) return { items: [] }
  // 尝试多个常见路径，任一成功即可
  try { return await request<{ items: QuestionBrief[] }>(`/question-bank/questions/brief?ids=${ids.join(',')}`) } catch {}
  try { return await request<{ items: QuestionBrief[] }>(`/questions/brief?ids=${ids.join(',')}`) } catch {}
  // 兜底：返回空
  return { items: [] }
}

// 获取题目详情（占位：后端路径因项目而异，按常见路径尝试）
async function getQuestionDetail(id: number) {
  try { return await request<QuestionBrief>(`/question-bank/questions/${id}`) } catch {}
  try { return await request<QuestionBrief>(`/questions/${id}`) } catch {}
  // 兜底：占位
  return { id, stem: `#${id}`, options: [], analysis: '' }
}

export const api = {
  // 健康检查
  health: () => request<{ status: string; db?: string }>('/health', { method: 'GET' }),

  // 用户分页列表
  users: (skip = 0, limit = 10, account?: string, email?: string) =>
    request<UsersPage>('/users', { method: 'GET', data: { skip, limit, account, email } }),

  // 更新用户（示例：昵称/邮箱/状态）
  updateUser: (id: number, data: Partial<Pick<User, 'nickname' | 'email' | 'status'>>) =>
    request<User>(`/users/${id}`, { method: 'PUT', data }),

  // 删除用户
  deleteUser: (id: number) =>
    request<void>(`/users/${id}`, { method: 'DELETE' }),

  // 登录/注册
  login: (account: string, password: string) =>
    request<Token>('/login', { method: 'POST' as const, data: { account, password } }),

  register: (account: string, password: string, email?: string, nickname?: string) =>
    request<User>('/register', { method: 'POST' as const, data: { account, password, email, nickname } }),

  // 个人信息
  me: () => request<UserInfo>('/me', { method: 'GET' }),
  updateMyNickname: (nickname: string) =>
    request<UserInfo>('/me/nickname', { method: 'PUT', data: { nickname } }),
  changeMyPassword: (old_password: string, new_password: string) =>
    request<void>('/me/password', { method: 'PUT', data: { old_password, new_password } }),
  // 简化用户列表（去掉 URLSearchParams，直接用 data）
  usersSimple: (skip = 0, limit = 20, account?: string, email?: string) =>
    request<UsersSimplePage>('/users/simple', { method: 'GET', data: { skip, limit, account, email } }),

  // 创建练习
  createPractice: (size = 5) => request<CreateSessionResp>('/practice/sessions', { method: 'POST', data: { size } }),
  // 获取练习题目
  getPracticeQuestion: (attemptId: number, seq: number) =>
    request<QuestionView>(`/practice/sessions/${attemptId}/questions/${seq}`, { method: 'GET' }),
  // 提交练习答案
  submitPracticeAnswer: (attemptId: number, seq: number, user_answer: string, time_spent_ms?: number) =>
    request<SubmitAnswerResp>(`/practice/sessions/${attemptId}/answers`, { method: 'POST', data: { seq, user_answer, time_spent_ms } }),
  // 完成练习
  finishPractice: (attemptId: number) =>
    request<{ total: number; answered: number; correct_count: number; accuracy: number; duration_seconds: number }>(
      `/practice/sessions/${attemptId}/finish`, { method: 'POST' }
    ),
  // 获取我的错题本（使用通用 request 封装，避免未定义变量）
  getMyErrorBook: (page = 1, size = 10, onlyDue = false, includeMastered = false) =>
    request<ErrorBookListResp>('/error-book', {
      method: 'GET',
      data: { page, size, only_due: onlyDue, include_mastered: includeMastered }
    }),
  // 获取我的题目
  getMyQuestions: (params: {
    page?: number
    size?: number
    keyword?: string
    qtype?: string
    difficulty?: number
    active_only?: boolean
  }) => {
    const payload: any = {
      page: params.page || 1,
      size: params.size || 10,
      active_only: params.active_only === true ? true : false,
    }
    if (params.keyword) payload.keyword = params.keyword
    if (params.qtype) payload.qtype = params.qtype
    if (typeof params.difficulty === 'number') payload.difficulty = params.difficulty
    return request<MyQuestionListResp>('/my-questions', { method: 'GET', data: payload })
  },
  getQuestionsBrief,
  getQuestionDetail,
}

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