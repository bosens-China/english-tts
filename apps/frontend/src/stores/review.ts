import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { reviewApi } from '@/api/client'
import type { ReviewTask } from '@/types/review'

export const useReviewStore = defineStore('review', () => {
  const tasks = ref<ReviewTask[]>([])
  const loading = ref(false)

  const dueTasks = computed(() =>
    tasks.value.filter((item) => item.next_review_at && new Date(item.next_review_at) <= new Date()),
  )

  async function fetchTasks(dueOnly = false): Promise<void> {
    loading.value = true
    try {
      tasks.value = await reviewApi.list(dueOnly)
    } finally {
      loading.value = false
    }
  }

  async function recordNewLesson(text: string): Promise<void> {
    const task = await reviewApi.create({ text })
    const exists = tasks.value.some((item) => item.id === task.id)
    if (!exists) tasks.value.unshift(task)
  }

  async function passReview(taskId: string): Promise<void> {
    const updated = await reviewApi.pass(taskId)
    const idx = tasks.value.findIndex((item) => item.id === updated.id)
    if (idx >= 0) {
      tasks.value[idx] = updated
      return
    }
    tasks.value.unshift(updated)
  }

  return {
    tasks,
    loading,
    dueTasks,
    fetchTasks,
    recordNewLesson,
    passReview,
  }
})
