export const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

// 仅保留我们需要的字段，避免要求 url/success/fail/complete
type RequestOpts = Omit<UniApp.RequestOptions, 'url' | 'success' | 'fail' | 'complete'>

export interface User {
  id: number
  account: string
  email?: string
  nickname?: string
  status: string
}
export interface UsersPage {
  total: number
  items: User[]
}

// 简单 Toast
function toast(msg: string) {
  uni.showToast({ title: msg, icon: 'none', duration: 2000 })
}

// 新增：过滤 undefined/null/空字符串的查询参数
function buildFilters(params: Record<string, any>) {
  const out: Record<string, any> = {}
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null) continue
    if (typeof v === 'string' && v.trim() === '') continue
    out[k] = v
  }
  return out
}

// GET 用 data 自动拼 query；其他方法走 body
export function request<T = any>(path: string, options: RequestOpts = {}) {
  return new Promise<T>((resolve, reject) => {
    const token = uni.getStorageSync('token')
    const auth = token ? { Authorization: `Bearer ${token}` } : {}
    uni.request({
      url: API_BASE + path,
      method: options.method || 'GET',
      header: { 'Content-Type': 'application/json', ...(options.header || {}), ...auth },
      data: options.data || {},
      success: (res) => {
        const code = res.statusCode || 0
        if (code === 401) {
          uni.removeStorageSync('token')
          uni.showToast({ title: '请先登录', icon: 'none' })
          setTimeout(() => uni.reLaunch({ url: '/pages/login/login' }), 300)
          return reject(new Error('401'))
        }
        if (code >= 200 && code < 300) return resolve(res.data as T)
        let msg = '网络错误'
        const body = res.data as any
        if (body && typeof body === 'object' && 'message' in body) msg = String(body.message)
        uni.showToast({ title: `${msg} (${code})`, icon: 'none' })
        reject(new Error(msg))
      },
      fail: (err) => { uni.showToast({ title: '请求失败', icon: 'none' }); reject(err) },
    })
  })
}

export const api = {
  health: () => request<{ status: string; db: string }>('/api/v1/health'),

  // 返回分页对象 { total, items }
  users: (skip = 0, limit = 10, account?: string, email?: string) =>
    request<UsersPage>('/api/v1/users', {
      method: 'GET',
      data: buildFilters({ skip, limit, account, email }),
    }),

  updateUser: (id: number, body: Partial<Pick<User, 'email' | 'nickname' | 'status'>>) =>
    request<User>(`/api/v1/users/${id}`, { method: 'PUT', data: body }),

  deleteUser: (id: number) =>
    request<void>(`/api/v1/users/${id}`, { method: 'DELETE' }),

  login: (account: string, password: string) =>
    request<{ access_token: string; token_type: string }>('/api/v1/login', { method: 'POST', data: { account, password } }),
}