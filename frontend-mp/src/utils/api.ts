const API_BASE = import.meta.env?.VITE_API_BASE_URL || ''
const API_PREFIX = import.meta.env?.VITE_API_PREFIX || '/api/v1'

function joinUrl(base: string, prefix: string, path: string) {
  const b = (base || '').replace(/\/+$/, '')
  const p = ('/' + (prefix || '').replace(/^\/+|\/+$/g, '')).replace(/\/+$/, '')
  let s = path.startsWith('/') ? path : `/${path}`
  const re = new RegExp(`^${p.replace(/\//g, '\\/')}`)
  if (p !== '/' && re.test(s)) s = s.replace(re, '')
  return b + p + s
}

type RequestOpts = Omit<UniApp.RequestOptions, 'url' | 'success' | 'fail' | 'complete'>
const ALLOWED = ['OPTIONS','GET','HEAD','POST','PUT','DELETE','TRACE','CONNECT'] as const
type HttpMethod = typeof ALLOWED[number]
const norm = (m?: string) => (ALLOWED.includes((m || 'GET').toUpperCase() as HttpMethod) ? (m || 'GET').toUpperCase() : 'GET') as HttpMethod

export function request<T = any>(path: string, options: RequestOpts = {}) {
  return new Promise<T>((resolve, reject) => {
    const token = uni.getStorageSync('token')
    const auth = token ? { Authorization: `Bearer ${token}` } : {}
    const url = joinUrl(API_BASE, API_PREFIX, path)
    const method = norm(options.method as any)

    console.log(`[API] ${method} ${url}`, { data: options.data })

    uni.request({
      url,
      method,
      header: { 'Content-Type': 'application/json', ...(options.header || {}), ...auth },
      data: options.data || {},
      success: (res) => {
        console.log(`[API] <= ${method} ${url} ${res.statusCode}`, res.data)
        if (res.statusCode >= 200 && res.statusCode < 300) resolve(res.data as T)
        else reject(res)
      },
      fail: (err) => reject(err),
    })
  })
}

export interface Token { access_token: string; token_type: string }

export const api = {
  login: (account: string, password: string) =>
    request<Token>('/login', { method: 'POST' as const, data: { account, password } }),
  register: (account: string, password: string, email?: string, nickname?: string) =>
    request<any>('/register', { method: 'POST' as const, data: { account, password, email, nickname } }),
}