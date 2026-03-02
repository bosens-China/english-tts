<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { toast } from 'vue-sonner'
import { aiApi } from '@/api/client'
import { useReviewStore } from '@/stores/review'
import { useSpeechRecognition } from '@/composables/useSpeechRecognition'

const review = useReviewStore()
const activeTaskId = ref<string | null>(null)
const spokenText = ref('')
const checking = ref(false)
const result = ref<{ score: number; feedback: string } | null>(null)
const {
  listening: reviewListening,
  start: startReviewRaw,
  stop: stopReviewRecognition,
} = useSpeechRecognition('en-US')

const activeTask = computed(() => review.dueTasks.find((item) => item.id === activeTaskId.value) ?? null)

function startTask(taskId: string): void {
  activeTaskId.value = taskId
  spokenText.value = ''
  result.value = null
}

async function startRecognition(): Promise<void> {
  const text = await startReviewRaw()
  if (text) spokenText.value = text
}

async function submitReview(): Promise<void> {
  if (!activeTask.value || !spokenText.value.trim()) return
  checking.value = true
  try {
    const res = await aiApi.evaluatePronunciation({
      reference_text: activeTask.value.text,
      spoken_text: spokenText.value,
    })
    result.value = { score: res.score, feedback: res.feedback }
    if (res.passed) {
      await review.passReview(activeTask.value.id)
      toast.success('复习通过，已更新下一次复习时间')
      await review.fetchTasks(true)
    } else {
      toast.error('复习未通过，请再读一次')
    }
  } finally {
    checking.value = false
  }
}

onMounted(async () => {
  await review.fetchTasks(true)
})
</script>

<template>
  <main class="min-h-screen bg-neutral-50 px-4 py-10">
    <section class="container-page space-y-6">
      <header class="card p-6">
        <h1 class="text-2xl font-bold text-neutral-900">复习模式</h1>
        <p class="mt-2 text-neutral-600">按遗忘曲线执行全文朗读，达到 60 分即通过。</p>
      </header>

      <section class="card p-6">
        <h2 class="text-lg font-semibold text-neutral-900">今日待复习</h2>
        <ul class="mt-4 space-y-3">
          <li
            v-for="item in review.dueTasks"
            :key="item.id"
            class="flex items-center justify-between rounded-xl border border-neutral-200 bg-white p-4"
          >
            <p class="line-clamp-2 text-sm text-neutral-800">{{ item.text }}</p>
            <button class="btn-secondary btn-sm" @click="startTask(item.id)">开始</button>
          </li>
        </ul>
        <p v-if="review.dueTasks.length === 0" class="mt-3 text-sm text-neutral-500">今天没有待复习课文。</p>
      </section>

      <section v-if="activeTask" class="card p-6 space-y-4">
        <h2 class="text-lg font-semibold text-neutral-900">当前复习课文</h2>
        <p class="rounded-xl bg-neutral-100 p-4 leading-8 text-neutral-800">{{ activeTask.text }}</p>
        <div class="flex items-center gap-3">
          <button class="btn-secondary" :disabled="reviewListening" @click="startRecognition">
            {{ reviewListening ? '识别中...' : '开始录音识别' }}
          </button>
          <button class="btn-ghost" :disabled="!reviewListening" @click="stopReviewRecognition">
            停止
          </button>
        </div>
        <textarea
          v-model="spokenText"
          class="textarea h-28"
          placeholder="输入你本次朗读的文本..."
        />
        <button class="btn-primary" :disabled="checking" @click="submitReview">
          {{ checking ? '评分中...' : '提交评分' }}
        </button>
        <p v-if="result" class="text-sm text-neutral-700">得分：{{ result.score }}，{{ result.feedback }}</p>
      </section>
    </section>
  </main>
</template>
