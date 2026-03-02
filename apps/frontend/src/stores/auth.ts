import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'
import { authApi } from '@/api/client'
import type { UserProfile } from '@/types/auth'

const TOKEN_KEY = 'english-tts-token-v1'
const USER_KEY = 'english-tts-user-v1'

function loadToken(): string {
  if (typeof window === 'undefined') return ''
  return window.localStorage.getItem(TOKEN_KEY) ?? ''
}

function loadUser(): UserProfile | null {
  if (typeof window === 'undefined') return null
  const raw = window.localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as UserProfile
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(loadToken())
  const user = ref<UserProfile | null>(loadUser())
  const loading = ref(false)

  const isAuthenticated = computed(() => Boolean(token.value && user.value))

  async function login(username: string, password: string): Promise<void> {
    loading.value = true
    try {
      const res = await authApi.login({ username, password })
      token.value = res.access_token
      user.value = res.user
    } finally {
      loading.value = false
    }
  }

  async function refreshMe(): Promise<void> {
    if (!token.value) return
    const profile = await authApi.me()
    user.value = profile
  }

  function logout(): void {
    token.value = ''
    user.value = null
  }

  watch(token, (value) => {
    if (typeof window === 'undefined') return
    if (!value) {
      window.localStorage.removeItem(TOKEN_KEY)
      return
    }
    window.localStorage.setItem(TOKEN_KEY, value)
  })

  watch(user, (value) => {
    if (typeof window === 'undefined') return
    if (!value) {
      window.localStorage.removeItem(USER_KEY)
      return
    }
    window.localStorage.setItem(USER_KEY, JSON.stringify(value))
  })

  return {
    token,
    user,
    loading,
    isAuthenticated,
    login,
    refreshMe,
    logout,
  }
})
