import { ofetch, type FetchOptions } from 'ofetch'
import { toast } from 'vue-sonner'

const API_BASE = '/api'
const TOKEN_KEY = 'english-tts-token-v1'

// 创建 ofetch 实例
export const http = ofetch.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  async onRequest({ options }) {
    if (typeof window === 'undefined') return
    const token = window.localStorage.getItem(TOKEN_KEY)
    if (!token) return
    const headers = new Headers(options.headers as HeadersInit)
    headers.set('Authorization', `Bearer ${token}`)
    options.headers = headers
  },
  async onRequestError({ error }) {
    console.error('Request error:', error)
    toast.error('网络连接失败，请检查网络')
  },
  async onResponseError({ response }) {
    const status = response.status
    const message = response._data?.detail || response.statusText || '请求失败'

    switch (status) {
      case 400:
        toast.error(`请求错误: ${message}`)
        break
      case 404:
        toast.error('资源不存在')
        break
      case 422:
        toast.error(`数据验证失败: ${message}`)
        break
      case 401:
        if (typeof window !== 'undefined') {
          window.localStorage.removeItem(TOKEN_KEY)
          window.localStorage.removeItem('english-tts-user-v1')
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
        }
        toast.error('登录状态已失效，请重新登录')
        break
      case 500:
        toast.error('服务器错误，请稍后重试')
        break
      default:
        toast.error(message)
    }
  },
})

// 导出类型安全的 fetch 方法
export function fetchApi<T>(path: string, options?: FetchOptions): Promise<T> {
  return http(path, options) as Promise<T>
}

// 下载文件专用（不使用 ofetch 的 JSON 解析）
export async function downloadFile(path: string): Promise<Blob> {
  const response = await fetch(`${API_BASE}${path}`)
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }
  return response.blob()
}
