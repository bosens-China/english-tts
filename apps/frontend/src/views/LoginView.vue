<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const username = ref('test_vip')
const password = ref('123456')

function fillTestAccount(type: 'vip' | 'free'): void {
  if (type === 'vip') {
    username.value = 'test_vip'
    password.value = '123456'
    return
  }
  username.value = 'test_free'
  password.value = '123456'
}

async function submit(): Promise<void> {
  if (!username.value || !password.value) return
  try {
    await auth.login(username.value, password.value)
    toast.success('登录成功')
    router.push('/dashboard')
  } catch {
    // Error handled by http.ts
  }
}
</script>

<template>
  <main class="min-h-screen bg-gradient-to-b from-neutral-100 to-white px-4 py-12">
    <section class="mx-auto max-w-md rounded-2xl border border-neutral-200 bg-white p-6 shadow-lg">
      <h1 class="text-2xl font-bold text-neutral-900">登录体验版</h1>
      <p class="mt-2 text-sm text-neutral-600">当前版本仅支持测试账号登录，不含注册与订阅流程。</p>

      <div class="mt-5 flex flex-wrap gap-2">
        <button class="btn-secondary btn-sm" @click="fillTestAccount('vip')">填充 VIP 测试账号</button>
        <button class="btn-secondary btn-sm" @click="fillTestAccount('free')">填充免费测试账号</button>
      </div>

      <form class="mt-6 space-y-4" @submit.prevent="submit">
        <div>
          <label class="label">用户名</label>
          <input v-model="username" class="input" placeholder="test_vip / test_free" />
        </div>
        <div>
          <label class="label">密码</label>
          <input v-model="password" class="input" type="password" placeholder="123456" />
        </div>
        <button class="btn-primary w-full" :disabled="auth.loading">
          {{ auth.loading ? '登录中...' : '登录' }}
        </button>
      </form>
    </section>
  </main>
</template>
