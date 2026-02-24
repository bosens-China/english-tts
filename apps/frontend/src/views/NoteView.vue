<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { notesApi, lessonsApi } from '@/api/client'
import { Button } from '@/components/ui'
import { formatFullDate } from '@/lib/utils'
import type { Note, Lesson } from '@/lib/schemas'

const route = useRoute()
const router = useRouter()
const noteId = route.params.id as string

const note = ref<Note | null>(null)
const lesson = ref<Lesson | null>(null)
const loading = ref(false)
const showToc = ref(false)

const tableOfContents = ref<Array<{ level: number, text: string, id: string }>>([])
const activeHeading = ref('')

// Extract TOC from HTML
const extractToc = (html: string) => {
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')
  const headings = doc.querySelectorAll('h1, h2, h3')

  return Array.from(headings).map((h, index) => {
    const heading = h as HTMLHeadingElement
    const id = `heading-${index}`
    const level = parseInt(heading.tagName.charAt(1))
    return {
      level,
      text: heading.textContent || '',
      id,
    }
  })
}

// Process content with anchor IDs
const processedContent = computed(() => {
  if (!note.value) return ''
  let html = note.value.content

  let index = 0
  html = html.replace(/<(h[123])([^>]*)>/g, (_, tag, attrs) => {
    return `<${tag}${attrs} id="heading-${index++}">`
  })

  return html
})

const fetchData = async () => {
  if (!noteId) return
  loading.value = true
  try {
    const noteData = await notesApi.get(noteId)
    note.value = noteData

    tableOfContents.value = extractToc(noteData.content)

    const lessonData = await lessonsApi.get(noteData.lesson_id)
    lesson.value = lessonData
  } catch {
    toast.error('获取笔记失败')
    router.back()
  } finally {
    loading.value = false
  }
}

const goToEdit = () => {
  router.push(`/notes/${noteId}/edit`)
}

const goBack = () => {
  if (lesson.value) {
    router.push(`/lessons/${lesson.value.id}`)
  } else {
    router.back()
  }
}

const scrollToHeading = (id: string) => {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    activeHeading.value = id
    showToc.value = false
  }
}

// Scroll spy
const handleScroll = () => {
  const headings = tableOfContents.value
    .map(t => document.getElementById(t.id))
    .filter((el): el is HTMLElement => el !== null)

  for (const heading of headings) {
    const rect = heading.getBoundingClientRect()
    if (rect.top >= 0 && rect.top <= 150) {
      activeHeading.value = heading.id
      break
    }
  }
}

// Word count
const wordCount = computed(() => {
  if (!note.value) return 0
  const text = note.value.content.replace(/<[^>]*>/g, '')
  return text.trim().length
})

// Read time
const readTime = computed(() => {
  const words = wordCount.value
  const minutes = Math.ceil(words / 300)
  return minutes < 1 ? '1 分钟' : `${minutes} 分钟`
})

onMounted(() => {
  fetchData()
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100 dark:from-neutral-950 dark:to-neutral-900">
    <!-- Header -->
    <header class="sticky top-0 z-30 glass border-b border-neutral-200/50 dark:border-neutral-800/50">
      <div class="container-page">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center gap-3 min-w-0">
            <button
              class="btn-ghost btn-icon-sm flex-shrink-0"
              @click="goBack"
            >
              <div class="i-ph-arrow-left-bold text-lg" />
            </button>

            <div v-if="!loading && note" class="min-w-0">
              <h1 class="text-lg font-bold text-neutral-900 dark:text-white truncate">
                {{ note.title }}
              </h1>
              <p v-if="lesson" class="text-xs text-neutral-500 truncate hidden sm:block">
                {{ lesson.title }}
              </p>
            </div>
            <div v-else class="h-6 w-32 skeleton rounded" />
          </div>

          <div class="flex items-center gap-2">
            <!-- TOC toggle (mobile) -->
            <button
              v-if="tableOfContents.length > 0"
              class="lg:hidden btn-ghost btn-icon-sm"
              :class="{ 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400': showToc }"
              @click="showToc = !showToc"
            >
              <div class="i-ph-list-dashes-bold text-lg" />
            </button>

            <Button @click="goToEdit">
              <div class="i-ph-pencil-simple-fill" />
              <span class="hidden sm:inline">编辑</span>
            </Button>
          </div>
        </div>
      </div>
    </header>

    <main class="container-page py-8">
      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-20">
        <div class="i-ph-spinner animate-spin text-4xl text-primary-500" />
      </div>

      <div v-else-if="note" class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <!-- Left: TOC -->
        <aside
          class="lg:col-span-3"
          :class="showToc ? 'block' : 'hidden lg:block'"
        >
          <div class="sticky top-24 space-y-4">
            <!-- TOC Card -->
            <div class="card card-elevated p-4">
              <h3 class="font-semibold text-neutral-900 dark:text-white mb-4 flex items-center gap-2">
                <div class="i-ph-list-dashes-bold text-primary-500" />
                目录
              </h3>

              <nav v-if="tableOfContents.length > 0" class="space-y-1">
                <button
                  v-for="item in tableOfContents"
                  :key="item.id"
                  class="w-full text-left text-sm py-2 px-3 rounded-lg transition-all"
                  :class="[
                    item.level === 1 ? 'font-medium' : '',
                    item.level === 2 ? 'pl-6' : '',
                    item.level === 3 ? 'pl-9 text-neutral-500' : '',
                    activeHeading === item.id
                      ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400'
                      : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800',
                  ]"
                  @click="scrollToHeading(item.id)"
                >
                  {{ item.text }}
                </button>
              </nav>

              <p v-else class="text-sm text-neutral-400">
                暂无目录
              </p>
            </div>

            <!-- Actions Card -->
            <div class="card p-4">
              <h3 class="font-semibold text-neutral-900 dark:text-white mb-3 text-sm">快捷操作</h3>
              <div class="space-y-1">
                <button
                  class="w-full flex items-center gap-3 px-3 py-2 text-sm text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-colors"
                  @click="goToEdit"
                >
                  <div class="i-ph-pencil-simple-bold" />
                  编辑笔记
                </button>
                <button
                  v-if="lesson"
                  class="w-full flex items-center gap-3 px-3 py-2 text-sm text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-colors"
                  @click="router.push(`/lessons/${lesson.id}`)"
                >
                  <div class="i-ph-book-open-bold" />
                  返回课程
                </button>
              </div>
            </div>
          </div>
        </aside>

        <!-- Center: Content -->
        <article class="lg:col-span-9">
          <!-- Meta Card -->
          <div class="card card-elevated p-6 sm:p-8 mb-6">
            <h1 class="text-2xl sm:text-3xl font-bold text-neutral-900 dark:text-white mb-4">
              {{ note.title }}
            </h1>

            <div class="flex flex-wrap items-center gap-4 text-sm text-neutral-500">
              <span class="flex items-center gap-1.5">
                <div class="i-ph-calendar-blank-bold" />
                {{ formatFullDate(note.updated_at) }}
              </span>
              <span class="flex items-center gap-1.5">
                <div class="i-ph-text-t-bold" />
                {{ wordCount }} 字
              </span>
              <span class="flex items-center gap-1.5">
                <div class="i-ph-clock-bold" />
                阅读约 {{ readTime }}
              </span>
            </div>
          </div>

          <!-- Content -->
          <div class="card card-elevated p-6 sm:p-10">
            <div class="prose prose-slate dark:prose-invert max-w-none" v-html="processedContent" />
          </div>

          <!-- Footer Actions -->
          <div class="mt-8 flex items-center justify-between">
            <button
              class="flex items-center gap-2 text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300 transition-colors"
              @click="goBack"
            >
              <div class="i-ph-arrow-left-bold" />
              返回
            </button>

            <Button variant="secondary" @click="goToEdit">
              <div class="i-ph-pencil-simple-bold" />
              编辑笔记
            </Button>
          </div>
        </article>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Prose styles */
:deep(.prose h1) {
  @apply text-3xl font-bold mb-4 mt-6 text-neutral-900 dark:text-white;
  scroll-margin-top: 6rem;
}

:deep(.prose h2) {
  @apply text-2xl font-bold mb-3 mt-5 text-neutral-800 dark:text-neutral-100;
  scroll-margin-top: 6rem;
}

:deep(.prose h3) {
  @apply text-xl font-semibold mb-2 mt-4 text-neutral-800 dark:text-neutral-100;
  scroll-margin-top: 6rem;
}

:deep(.prose p) {
  @apply mb-4 leading-relaxed text-neutral-700 dark:text-neutral-300;
}

:deep(.prose ul) {
  @apply list-disc pl-6 mb-4;
}

:deep(.prose ol) {
  @apply list-decimal pl-6 mb-4;
}

:deep(.prose li) {
  @apply mb-1;
}

:deep(.prose ul[data-type="taskList"]) {
  @apply list-none pl-0;
}

:deep(.prose ul[data-type="taskList"] li) {
  @apply flex items-start gap-2;
}

:deep(.prose ul[data-type="taskList"] input[type="checkbox"]) {
  @apply w-4 h-4 mt-1 cursor-default;
}

:deep(.prose pre) {
  @apply bg-neutral-900 text-neutral-100 p-4 rounded-xl overflow-x-auto mb-4 text-sm;
}

:deep(.prose pre code) {
  @apply bg-transparent p-0 text-sm;
}

:deep(.prose code) {
  @apply bg-neutral-100 dark:bg-neutral-800 px-1.5 py-0.5 rounded text-sm text-primary-600 dark:text-primary-400;
}

:deep(.prose blockquote) {
  @apply border-l-4 border-primary-500 pl-4 italic text-neutral-600 dark:text-neutral-400 bg-neutral-50 dark:bg-neutral-800/50 py-3 pr-4 rounded-r-xl mb-4;
}

:deep(.prose a) {
  @apply text-primary-600 dark:text-primary-400 no-underline hover:underline;
}

:deep(.prose img) {
  @apply max-w-full h-auto rounded-xl my-6;
}

:deep(.prose mark) {
  @apply bg-yellow-200 dark:bg-yellow-900/50 px-1 rounded;
}

:deep(.prose table) {
  @apply w-full border-collapse mb-4;
}

:deep(.prose th, .prose td) {
  @apply border border-neutral-200 dark:border-neutral-700 px-4 py-2 text-left;
}

:deep(.prose th) {
  @apply bg-neutral-50 dark:bg-neutral-800 font-semibold;
}

:deep(.prose hr) {
  @apply border-neutral-200 dark:border-neutral-700 my-8;
}

:deep(.prose ::selection) {
  @apply bg-primary-200 dark:bg-primary-900;
}
</style>
