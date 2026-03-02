import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { aiApi } from '@/api/client'
import { useSessionStore } from '@/stores/session'
import type { ChatMessage, GenerateLessonResponse } from '@/types/ai'

export const useLearningStore = defineStore('learning', () => {
  const session = useSessionStore()

  const currentLesson = ref<GenerateLessonResponse | null>(null)
  const generating = ref(false)
  const chatLoading = ref(false)
  const chatHistory = ref<ChatMessage[]>([])

  const lessonContext = computed(() => currentLesson.value?.text ?? '')

  async function generateTodayLesson(): Promise<void> {
    const level = session.level ?? 0
    const goal = session.goal ?? 'daily'
    generating.value = true
    try {
      currentLesson.value = await aiApi.generateLesson({ level, goal })
    } finally {
      generating.value = false
    }
  }

  async function askTutor(message: string): Promise<string> {
    chatLoading.value = true
    try {
      chatHistory.value.push({ role: 'user', content: message })
      const res = await aiApi.tutorChat({
        context: lessonContext.value,
        message,
        history: chatHistory.value.filter((item) => item.role !== 'system'),
        stream: false,
      })
      chatHistory.value.push({ role: 'assistant', content: res.answer })
      return res.answer
    } finally {
      chatLoading.value = false
    }
  }

  function clearLesson(): void {
    currentLesson.value = null
  }

  function clearChat(): void {
    chatHistory.value = []
  }

  return {
    currentLesson,
    generating,
    chatLoading,
    chatHistory,
    lessonContext,
    generateTodayLesson,
    askTutor,
    clearLesson,
    clearChat,
  }
})
