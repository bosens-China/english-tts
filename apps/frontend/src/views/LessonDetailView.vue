<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { lessonsApi, notesApi } from '@/api/client'
import { AudioPlayer, DialogueList } from '@/components/audio'
import { Skeleton, Button } from '@/components/ui'
import type { Lesson, Note } from '@/lib/schemas'

const route = useRoute()
const router = useRouter()
const lessonId = route.params.id as string

const lesson = ref<Lesson | null>(null)
const notes = ref<Note[]>([])
const loading = ref(false)
const activeTab = ref<'learn' | 'notes'>('learn')
const currentLineIndex = ref<number | null>(null)

const audioUrl = computed(() => {
  if (!lesson.value?.audio) return ''
  return lessonsApi.downloadAudio(lessonId)
})

const hasAudio = computed(() => !!lesson.value?.audio)

const fetchData = async () => {
  loading.value = true
  try {
    const [lessonData, notesData] = await Promise.all([
      lessonsApi.get(lessonId),
      notesApi.list(lessonId),
    ])
    lesson.value = lessonData
    notes.value = notesData
  } catch {
    toast.error('获取课文数据失败')
  } finally {
    loading.value = false
  }
}

const handlePlayLine = (index: number) => {
  currentLineIndex.value = index
}

const handleRegenerated = async () => {
  await fetchData()
}

const deleteNote = async (id: string) => {
  if (!confirm('确定要删除这个笔记吗？')) return
  try {
    await notesApi.delete(id)
    await fetchData()
    toast.success('笔记已删除')
  } catch {
    // Error handled by http client
  }
}

const goBack = () => {
  if (lesson.value) {
    router.push(`/books/${lesson.value.book_id}`)
  }
}

onMounted(fetchData)
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

            <div v-if="lesson" class="min-w-0">
              <h1 class="text-lg font-bold text-neutral-900 dark:text-white truncate">
                {{ lesson.title }}
              </h1>
              <p v-if="lesson.description" class="text-xs text-neutral-500 truncate hidden sm:block">
                {{ lesson.description }}
              </p>
            </div>
            <div v-else class="h-6 w-32 skeleton rounded" />
          </div>

          <!-- Tab Switcher -->
          <div class="flex gap-1 p-1 bg-neutral-100 dark:bg-neutral-800 rounded-xl">
            <button
              class="px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2"
              :class="activeTab === 'learn' ? 'bg-white dark:bg-neutral-700 text-primary-600 dark:text-primary-400 shadow-sm' : 'text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300'"
              @click="activeTab = 'learn'"
            >
              <div class="i-ph-book-open-fill" />
              <span class="hidden sm:inline">学习</span>
            </button>
            <button
              class="px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2"
              :class="activeTab === 'notes' ? 'bg-white dark:bg-neutral-700 text-primary-600 dark:text-primary-400 shadow-sm' : 'text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300'"
              @click="activeTab = 'notes'"
            >
              <div class="iph-notebook-fill" />
              <span class="hidden sm:inline">笔记</span>
              <span
                v-if="notes.length > 0"
                class="badge badge-primary"
              >
                {{ notes.length }}
              </span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="container-page py-6">
      <!-- Loading State -->
      <div v-if="loading" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="space-y-4">
          <Skeleton variant="card" v-for="n in 5" :key="n" />
        </div>
        <div>
          <Skeleton variant="card" height="400px" />
        </div>
      </div>

      <!-- Learn Tab -->
      <template v-else-if="lesson && activeTab === 'learn'">
        <!-- No Audio Warning -->
        <div v-if="!hasAudio" class="card card-elevated py-16 text-center mb-6">
          <div class="w-20 h-20 rounded-2xl bg-amber-100 dark:bg-amber-900/20 flex items-center justify-center mx-auto mb-4">
            <div class="i-ph-speaker-slash text-4xl text-amber-500" />
          </div>
          <h3 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200 mb-2">
            这节课还没有音频
          </h3>
          <p class="text-neutral-500 mb-6">请在创建课文时添加对话内容</p>
        </div>

        <!-- Learning Content -->
        <div v-else class="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <!-- Left: Dialogue List -->
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <h2 class="text-lg font-bold text-neutral-900 dark:text-white flex items-center gap-2">
                <div class="i-ph-chat-circle-text-fill text-primary-500" />
                课文内容
              </h2>
              <span class="text-sm text-neutral-400">点击句子播放</span>
            </div>

            <div class="card card-elevated p-5">
              <DialogueList
                :dialogue="lesson.audio!.dialogue"
                :current-index="currentLineIndex"
                :playing-line-index="currentLineIndex"
                @select="handlePlayLine"
                @play-line="handlePlayLine"
              />
            </div>
          </div>

          <!-- Right: Audio Player -->
          <div class="xl:sticky xl:top-24 xl:self-start">
            <AudioPlayer
              :audio-id="lessonId"
              :audio-url="audioUrl"
              :dialogue="lesson.audio!.dialogue"
              :initial-rate="lesson.audio!.rate"
              :initial-pitch="lesson.audio!.pitch"
              @playing="currentLineIndex = $event"
              @regenerated="handleRegenerated"
            />
          </div>
        </div>
      </template>

      <!-- Notes Tab -->
      <template v-else-if="activeTab === 'notes'">
        <div class="max-w-4xl mx-auto">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h2 class="text-lg font-bold text-neutral-900 dark:text-white">学习笔记</h2>
              <p class="text-sm text-neutral-500 mt-0.5">共 {{ notes.length }} 篇笔记</p>
            </div>
            <Button @click="router.push(`/lessons/${lessonId}/notes/new`)">
              <div class="i-ph-plus-bold" />
              新建笔记
            </Button>
          </div>

          <!-- Empty State -->
          <div v-if="notes.length === 0" class="card card-elevated py-16 text-center">
            <div class="w-20 h-20 rounded-2xl bg-primary-100 dark:bg-primary-900/20 flex items-center justify-center mx-auto mb-4">
              <div class="i-ph-notebook text-4xl text-primary-500" />
            </div>
            <h3 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200 mb-2">
              还没有笔记
            </h3>
            <p class="text-neutral-500 mb-6">记录学习心得，加深记忆</p>
            <Button @click="router.push(`/lessons/${lessonId}/notes/new`)">
              <div class="i-ph-plus-bold" />
              创建第一篇笔记
            </Button>
          </div>

          <!-- Notes Grid -->
          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="(note, index) in notes"
              :key="note.id"
              class="group card card-hover card-interactive animate-fade-in-up"
              :style="{ animationDelay: `${index * 50}ms` }"
              @click="router.push(`/notes/${note.id}`)"
            >
              <div class="p-5">
                <div class="flex items-start justify-between mb-3">
                  <div class="flex items-center gap-3 min-w-0">
                    <div class="w-10 h-10 rounded-xl bg-primary-100 dark:bg-primary-900/20 flex items-center justify-center flex-shrink-0">
                      <div class="i-ph-file-text-fill text-xl text-primary-500" />
                    </div>
                    <h3 class="font-semibold text-neutral-800 dark:text-neutral-200 truncate group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                      {{ note.title }}
                    </h3>
                  </div>
                  <button
                    class="p-2 rounded-lg text-neutral-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 opacity-0 group-hover:opacity-100 transition-all flex-shrink-0"
                    @click.stop="deleteNote(note.id)"
                  >
                    <div class="i-ph-trash-fill" />
                  </button>
                </div>

                <p class="text-sm text-neutral-500 dark:text-neutral-400 line-clamp-2 mb-4">
                  {{ note.content.replace(/<[^>]*>/g, '').slice(0, 100) || '暂无内容' }}
                </p>

                <div class="flex items-center justify-between text-xs text-neutral-400">
                  <span class="flex items-center gap-1">
                    <div class="i-ph-clock" />
                    {{ new Date(note.updated_at).toLocaleString('zh-CN') }}
                  </span>
                  <span class="flex items-center gap-1 text-primary-600 dark:text-primary-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    查看详情
                    <div class="i-ph-arrow-right" />
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </main>
  </div>
</template>
