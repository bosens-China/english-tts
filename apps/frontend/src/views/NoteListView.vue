<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { notesApi, booksApi } from '@/api/client'
import { Skeleton, Button } from '@/components/ui'
import { formatRelativeTime } from '@/lib/utils'
import type { Note, Book, Lesson } from '@/lib/schemas'

const router = useRouter()

const notes = ref<Note[]>([])
const books = ref<Book[]>([])
const lessonsMap = ref<Map<string, Lesson>>(new Map())
const loading = ref(false)
const searchQuery = ref('')
const sortBy = ref<'updated' | 'created' | 'title'>('updated')

// Fetch all notes
const fetchNotes = async () => {
  loading.value = true
  try {
    const booksData = await booksApi.list()
    books.value = booksData

    const allNotes: Note[] = []
    for (const book of booksData) {
      const bookDetail = await booksApi.get(book.id)
      for (const lesson of bookDetail.lessons || []) {
        const lessonNotes = await notesApi.list(lesson.id)
        allNotes.push(...lessonNotes)
        lessonsMap.value.set(lesson.id, lesson)
      }
    }
    notes.value = allNotes
  } catch {
    toast.error('获取笔记失败')
  } finally {
    loading.value = false
  }
}

// Filtered and sorted notes
const filteredNotes = computed(() => {
  let result = notes.value

  // Search filter
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(
      note =>
        note.title.toLowerCase().includes(query) ||
        note.content.toLowerCase().includes(query),
    )
  }

  // Sort
  result = [...result].sort((a, b) => {
    switch (sortBy.value) {
      case 'updated':
        return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
      case 'created':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      case 'title':
        return a.title.localeCompare(b.title)
      default:
        return 0
    }
  })

  return result
})

// Get preview text
const getPreview = (note: Note) => {
  const text = note.content.replace(/<[^>]*>/g, '')
  return text.slice(0, 120) + (text.length > 120 ? '...' : '')
}

// Get lesson title
const getLessonTitle = (lessonId: string) => {
  return lessonsMap.value.get(lessonId)?.title || '未知课程'
}

// Delete note
const deleteNote = async (id: string) => {
  if (!confirm('确定要删除这个笔记吗？')) return
  try {
    await notesApi.delete(id)
    notes.value = notes.value.filter((n) => n.id !== id)
    toast.success('笔记已删除')
  } catch {
    // Error handled by http client
  }
}

// Stats
const stats = computed(() => {
  const totalNotes = notes.value.length
  const totalWords = notes.value.reduce((sum, note) => {
    return sum + note.content.replace(/<[^>]*>/g, '').length
  }, 0)

  return {
    totalNotes,
    totalWords,
    thisWeekNotes: notes.value.filter((n) => {
      const date = new Date(n.updated_at)
      const now = new Date()
      const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))
      return diffDays < 7
    }).length,
  }
})

onMounted(fetchNotes)
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100 dark:from-neutral-950 dark:to-neutral-900">
    <!-- Header -->
    <header class="sticky top-0 z-30 glass border-b border-neutral-200/50 dark:border-neutral-800/50">
      <div class="container-page">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 py-4">
          <div class="flex items-center gap-3">
            <button
              class="btn-ghost btn-icon-sm"
              @click="router.push('/')"
            >
              <div class="i-ph-arrow-left-bold text-lg" />
            </button>
            <div>
              <h1 class="text-xl font-bold text-neutral-900 dark:text-white">我的笔记</h1>
              <p class="text-sm text-neutral-500">共 {{ stats.totalNotes }} 篇笔记</p>
            </div>
          </div>

          <!-- Search -->
          <div class="relative max-w-xs w-full">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <div class="i-ph-magnifying-glass text-neutral-400" />
            </div>
            <input
              v-model="searchQuery"
              type="text"
              class="input pl-10 pr-10"
              placeholder="搜索笔记..."
            />
            <button
              v-if="searchQuery"
              class="absolute inset-y-0 right-0 pr-3 flex items-center"
              @click="searchQuery = ''"
            >
              <div class="i-ph-x text-neutral-400 hover:text-neutral-600" />
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="container-page py-8">
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div class="card p-5 bg-gradient-to-br from-primary-500 to-primary-600 text-white border-0">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center">
              <div class="i-ph-notebook-fill text-2xl" />
            </div>
            <div>
              <p class="text-sm text-white/80">总笔记数</p>
              <p class="text-2xl font-bold">{{ stats.totalNotes }}</p>
            </div>
          </div>
        </div>

        <div class="card p-5 bg-gradient-to-br from-accent-500 to-accent-600 text-white border-0">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center">
              <div class="i-ph-text-t-fill text-2xl" />
            </div>
            <div>
              <p class="text-sm text-white/80">总字数</p>
              <p class="text-2xl font-bold">{{ stats.totalWords.toLocaleString() }}</p>
            </div>
          </div>
        </div>

        <div class="card p-5 bg-gradient-to-br from-secondary-500 to-secondary-600 text-white border-0">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center">
              <div class="i-ph-calendar-check-fill text-2xl" />
            </div>
            <div>
              <p class="text-sm text-white/80">本周更新</p>
              <p class="text-2xl font-bold">{{ stats.thisWeekNotes }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Toolbar -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div class="flex items-center gap-2">
          <span class="text-sm text-neutral-500">排序：</span>
          <div class="flex gap-1 p-1 bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700">
            <button
              class="px-3 py-1.5 text-sm font-medium rounded-lg transition-all"
              :class="sortBy === 'updated' ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400' : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700'"
              @click="sortBy = 'updated'"
            >
              最近更新
            </button>
            <button
              class="px-3 py-1.5 text-sm font-medium rounded-lg transition-all"
              :class="sortBy === 'created' ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400' : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700'"
              @click="sortBy = 'created'"
            >
              创建时间
            </button>
            <button
              class="px-3 py-1.5 text-sm font-medium rounded-lg transition-all"
              :class="sortBy === 'title' ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400' : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700'"
              @click="sortBy = 'title'"
            >
              标题
            </button>
          </div>
        </div>

        <p class="text-sm text-neutral-500">
          找到 {{ filteredNotes.length }} 篇笔记
        </p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Skeleton v-for="n in 6" :key="n" variant="card" height="180px" />
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredNotes.length === 0" class="card card-elevated py-16 text-center">
        <div class="w-20 h-20 rounded-2xl bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center mx-auto mb-4">
          <div
            :class="searchQuery ? 'i-ph-magnifying-glass' : 'i-ph-notebook'"
            class="text-4xl text-neutral-400"
          />
        </div>
        <h3 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200 mb-2">
          {{ searchQuery ? '没有找到匹配的笔记' : '还没有笔记' }}
        </h3>
        <p class="text-neutral-500 mb-6">
          {{ searchQuery ? '换个关键词试试' : '去课程页面创建一篇吧' }}
        </p>
        <Button @click="router.push('/')">
          浏览课程
        </Button>
      </div>

      <!-- Notes Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="(note, index) in filteredNotes"
          :key="note.id"
          class="group card card-hover card-interactive animate-fade-in-up"
          :style="{ animationDelay: `${index * 30}ms` }"
          @click="router.push(`/notes/${note.id}`)"
        >
          <div class="p-5">
            <div class="flex items-start justify-between mb-3">
              <h3 class="font-semibold text-neutral-800 dark:text-neutral-200 line-clamp-1 flex-1 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                {{ note.title }}
              </h3>
              <button
                class="p-1.5 rounded-lg text-neutral-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 opacity-0 group-hover:opacity-100 transition-all flex-shrink-0"
                @click.stop="deleteNote(note.id)"
              >
                <div class="i-ph-trash-bold" />
              </button>
            </div>

            <p class="text-sm text-neutral-500 dark:text-neutral-400 line-clamp-3 mb-4 h-[60px]">
              {{ getPreview(note) || '暂无内容' }}
            </p>

            <div class="flex items-center justify-between text-xs text-neutral-400">
              <div class="flex items-center gap-1.5 min-w-0">
                <div class="i-ph-book-open" />
                <span class="truncate max-w-[120px]">{{ getLessonTitle(note.lesson_id) }}</span>
              </div>
              <div class="flex items-center gap-1.5 flex-shrink-0">
                <div class="i-ph-clock" />
                <span>{{ formatRelativeTime(note.updated_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
