<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { toast } from 'vue-sonner'
import { aiApi } from '@/api/client'
import { useLearningStore } from '@/stores/learning'
import { usePlayerStore } from '@/stores/player'
import { useReviewStore } from '@/stores/review'
import { useSpeechRecognition } from '@/composables/useSpeechRecognition'

const learning = useLearningStore()
const player = usePlayerStore()
const review = useReviewStore()

const step = ref<'listen' | 'shadowing' | 'qa' | 'done'>('listen')
const activeQuestion = ref(0)
const answerInput = ref('')
const spokenText = ref('')
const pronunciationScore = ref<number | null>(null)
const pronunciationFeedback = ref('')
const qaFeedback = ref('')
const qaScore = ref<number | null>(null)
const qaPassCount = ref(0)
const completionSaved = ref(false)
const submittingShadowing = ref(false)
const submittingQA = ref(false)
const {
  listening: shadowingListening,
  start: startShadowingRaw,
  stop: stopShadowing,
} = useSpeechRecognition('en-US')

const lesson = computed(() => learning.currentLesson)
const currentQuestion = computed(() => lesson.value?.questions[activeQuestion.value] ?? '')

async function generateLesson(force = false): Promise<void> {
  if (!force && lesson.value) return
  try {
    await learning.generateTodayLesson()
    step.value = 'listen'
    activeQuestion.value = 0
    answerInput.value = ''
    spokenText.value = ''
    pronunciationScore.value = null
    pronunciationFeedback.value = ''
    qaFeedback.value = ''
    qaScore.value = null
    qaPassCount.value = 0
    completionSaved.value = false
    toast.success('今日新课已生成')
  } catch {
    toast.error('课文生成失败，请稍后重试')
  }
}

function playLesson(): void {
  if (!lesson.value) return
  const text = lesson.value.audio_script.map((line) => line.text).join(' ')
  player.preview(text || lesson.value.text)
}

async function submitShadowing(): Promise<void> {
  if (!lesson.value || !spokenText.value.trim()) return
  submittingShadowing.value = true
  try {
    const res = await aiApi.evaluatePronunciation({
      reference_text: lesson.value.text,
      spoken_text: spokenText.value,
    })
    pronunciationScore.value = res.score
    pronunciationFeedback.value = res.feedback
    if (res.passed) {
      step.value = 'qa'
      toast.success('跟读通过，进入问答环节')
    } else {
      toast.error('跟读未达标，请再试一次')
    }
  } catch {
    toast.error('跟读评分失败，请重试')
  } finally {
    submittingShadowing.value = false
  }
}

async function startShadowingRecognition(): Promise<void> {
  const text = await startShadowingRaw()
  if (text) spokenText.value = text
}

async function submitAnswer(): Promise<void> {
  if (!lesson.value || !answerInput.value.trim() || !currentQuestion.value) return
  submittingQA.value = true
  try {
    const res = await aiApi.evaluateQA({
      lesson_text: lesson.value.text,
      question: currentQuestion.value,
      user_answer: answerInput.value,
    })
    qaScore.value = res.score
    qaFeedback.value = res.feedback
    if (res.passed) qaPassCount.value += 1
  } catch {
    qaFeedback.value = '评估失败，请稍后重试'
  } finally {
    submittingQA.value = false
  }

  answerInput.value = ''
  if (activeQuestion.value < 2) {
    activeQuestion.value += 1
  } else if (qaPassCount.value >= 2) {
    step.value = 'done'
    if (lesson.value && !completionSaved.value) {
      await review.recordNewLesson(lesson.value.text)
      completionSaved.value = true
    }
  }
}

onMounted(async () => {
  await review.fetchTasks()
  await generateLesson()
})
</script>

<template>
  <main class="min-h-screen bg-gradient-to-b from-neutral-50 to-white px-4 py-10">
    <section class="container-page space-y-6">
      <header class="card p-6">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p class="text-sm text-neutral-500">Daily Learning</p>
            <h1 class="mt-1 text-2xl font-bold text-neutral-900">今日学习主界面</h1>
          </div>
          <button class="btn-secondary" :disabled="learning.generating" @click="generateLesson(true)">
            {{ learning.generating ? '生成中...' : '重新生成课文' }}
          </button>
        </div>
      </header>

      <section v-if="lesson" class="card p-6">
        <div class="mb-5 flex flex-wrap gap-2">
          <button
            class="btn-sm rounded-lg px-3 py-1.5"
            :class="step === 'listen' ? 'bg-primary-600 text-white' : 'bg-neutral-100 text-neutral-700'"
            @click="step = 'listen'"
          >
            Step1 磨耳朵
          </button>
          <button
            class="btn-sm rounded-lg px-3 py-1.5"
            :class="step === 'shadowing' ? 'bg-primary-600 text-white' : 'bg-neutral-100 text-neutral-700'"
            @click="step = 'shadowing'"
          >
            Step2 跟读
          </button>
          <button
            class="btn-sm rounded-lg px-3 py-1.5"
            :class="step === 'qa' ? 'bg-primary-600 text-white' : 'bg-neutral-100 text-neutral-700'"
            @click="step = 'qa'"
          >
            Step3 问答
          </button>
          <button
            class="btn-sm rounded-lg px-3 py-1.5"
            :class="step === 'done' ? 'bg-primary-600 text-white' : 'bg-neutral-100 text-neutral-700'"
            @click="step = 'done'"
          >
            Step4 结算
          </button>
        </div>

        <div v-if="step === 'listen'" class="space-y-4">
          <h2 class="text-xl font-semibold text-neutral-900">课文内容</h2>
          <p class="leading-8 text-neutral-800">{{ lesson.text }}</p>
          <button class="btn-primary" @click="playLesson">播放课文音频</button>
          <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <article class="rounded-xl border border-neutral-200 p-4">
              <h3 class="font-semibold text-neutral-900">新词</h3>
              <p class="mt-2 text-sm text-neutral-600">{{ lesson.new_words.join(' / ') }}</p>
            </article>
            <article class="rounded-xl border border-neutral-200 p-4">
              <h3 class="font-semibold text-neutral-900">语法点</h3>
              <p class="mt-2 text-sm text-neutral-600">{{ lesson.grammar.join(' / ') }}</p>
            </article>
            <article class="rounded-xl border border-neutral-200 p-4">
              <h3 class="font-semibold text-neutral-900">文化补充</h3>
              <p class="mt-2 text-sm text-neutral-600">{{ lesson.culture_notes.join(' / ') }}</p>
            </article>
          </div>
        </div>

        <div v-else-if="step === 'shadowing'" class="space-y-4">
          <h2 class="text-xl font-semibold text-neutral-900">跟读打分</h2>
          <p class="text-neutral-600">可直接语音识别成文本，再提交后端评分。</p>
          <div class="flex items-center gap-3">
            <button class="btn-secondary" :disabled="shadowingListening" @click="startShadowingRecognition">
              {{ shadowingListening ? '识别中...' : '开始录音识别' }}
            </button>
            <button class="btn-ghost" :disabled="!shadowingListening" @click="stopShadowing">
              停止
            </button>
          </div>
          <textarea
            v-model="spokenText"
            class="textarea h-28"
            placeholder="输入你的跟读文本..."
          />
          <button class="btn-primary" :disabled="submittingShadowing" @click="submitShadowing">
            {{ submittingShadowing ? '评分中...' : '提交跟读评分' }}
          </button>
          <p v-if="pronunciationScore !== null" class="text-sm text-neutral-700">
            得分：{{ pronunciationScore }}，{{ pronunciationFeedback }}
          </p>
        </div>

        <div v-else-if="step === 'qa'" class="space-y-4">
          <h2 class="text-xl font-semibold text-neutral-900">课后问答</h2>
          <p class="rounded-xl bg-neutral-100 p-4 text-neutral-800">{{ currentQuestion }}</p>
          <textarea
            v-model="answerInput"
            class="textarea h-28"
            placeholder="输入你的回答..."
          />
          <div class="flex items-center gap-3">
            <button class="btn-primary" :disabled="submittingQA" @click="submitAnswer">
              {{ submittingQA ? '评估中...' : '提交回答' }}
            </button>
            <p class="text-sm text-neutral-600">{{ qaFeedback }}</p>
          </div>
          <p v-if="qaScore !== null" class="text-sm text-neutral-600">本题得分：{{ qaScore }}</p>
        </div>

        <div v-else class="space-y-3">
          <h2 class="text-xl font-semibold text-neutral-900">通关结算</h2>
          <p class="text-neutral-700">已完成今日学习流程，继续保持。</p>
          <p class="text-sm text-neutral-500">问答通过题数：{{ qaPassCount }}/3</p>
        </div>
      </section>

      <section v-else class="card p-6">
        <p class="text-neutral-600">暂无课文，点击上方“重新生成课文”开始。</p>
      </section>
    </section>
  </main>
</template>
