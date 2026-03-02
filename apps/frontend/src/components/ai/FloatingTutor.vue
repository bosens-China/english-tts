<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useLearningStore } from '@/stores/learning'

const route = useRoute()
const auth = useAuthStore()
const learning = useLearningStore()

const open = ref(false)
const input = ref('')

const visible = computed(() => auth.isAuthenticated && route.path !== '/login')

async function send(): Promise<void> {
  const message = input.value.trim()
  if (!message) return
  input.value = ''
  await learning.askTutor(message)
}
</script>

<template>
  <div v-if="visible">
    <button
      class="fixed bottom-6 right-6 z-40 rounded-full bg-primary-600 px-4 py-3 text-sm font-semibold text-white shadow-xl"
      @click="open = !open"
    >
      AI 助教
    </button>

    <section
      v-if="open"
      class="fixed bottom-22 right-6 z-50 w-[360px] max-w-[calc(100vw-32px)] rounded-2xl border border-neutral-200 bg-white p-4 shadow-2xl"
    >
      <header class="mb-3 flex items-center justify-between">
        <h3 class="text-base font-semibold text-neutral-900">AI Tutor</h3>
        <button class="btn-ghost btn-sm" @click="open = false">关闭</button>
      </header>

      <div class="mb-3 h-72 overflow-y-auto rounded-xl bg-neutral-50 p-3">
        <p v-if="learning.chatHistory.length === 0" class="text-sm text-neutral-500">
          可以问：这篇课文怎么记？这个句子怎么说更自然？
        </p>
        <div v-for="(msg, idx) in learning.chatHistory" :key="idx" class="mb-2">
          <div
            class="rounded-lg px-3 py-2 text-sm"
            :class="msg.role === 'assistant' ? 'bg-primary-50 text-neutral-800' : 'bg-neutral-200 text-neutral-900'"
          >
            <p class="mb-1 text-xs text-neutral-500">{{ msg.role === 'assistant' ? '助教' : '你' }}</p>
            <p class="whitespace-pre-wrap">{{ msg.content }}</p>
          </div>
        </div>
      </div>

      <form class="flex items-center gap-2" @submit.prevent="send">
        <input
          v-model="input"
          class="input py-2"
          placeholder="输入问题..."
        />
        <button class="btn-primary btn-sm" :disabled="learning.chatLoading">
          {{ learning.chatLoading ? '发送中' : '发送' }}
        </button>
      </form>
    </section>
  </div>
</template>
