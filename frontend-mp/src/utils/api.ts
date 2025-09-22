const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || ''
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

  // 简化用户列表（去掉 URLSearchParams，直接用 data）
  usersSimple: (skip = 0, limit = 20, account?: string, email?: string) =>
    request<UsersSimplePage>('/users/simple', { method: 'GET', data: { skip, limit, account, email } }),
}

export interface UserSimple {
  id: number
  account: string
  status: string
  role?: string | null
}
export interface UsersSimplePage { total: number; items: UserSimple[] }