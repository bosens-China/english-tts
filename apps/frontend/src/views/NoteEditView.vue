<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLocalStorage, useDebounceFn } from '@vueuse/core'
import { toast } from 'vue-sonner'
import { TiptapEditor } from '@/components/editor'
import { notesApi, lessonsApi } from '@/api/client'
import { Button } from '@/components/ui'
import type { Note, Lesson } from '@/lib/schemas'
import type { JSONContent } from '@tiptap/vue-3'

const route = useRoute()
const router = useRouter()

const noteId = route.params.id as string | undefined
const lessonId = route.params.lessonId as string | undefined

const note = ref<Note | null>(null)
const lesson = ref<Lesson | null>(null)
const loading = ref(false)
const saving = ref(false)
const lastSaved = ref<Date | null>(null)

const isNew = computed(() => !noteId)
const isDirty = ref(false)

// Draft with localStorage auto-save
const draftKey = noteId ? `draft-${noteId}` : `draft-new-${lessonId}`
const draft = useLocalStorage(draftKey, {
  title: '',
  content: '<p></p>',
  savedAt: 0,
})

const title = ref(draft.value.title)
const content = ref(draft.value.content)
const jsonContent = ref<JSONContent | null>(null)

// Word count
const wordCount = computed(() => {
  const text = content.value.replace(/<[^>]*>/g, '')
  return text.trim().length
})

// Auto-save draft (debounced 2s)
const saveDraft = useDebounceFn(() => {
  draft.value = {
    title: title.value,
    content: content.value,
    savedAt: Date.now(),
  }
  isDirty.value = true
}, 2000)

// Watch changes for auto-save
watch([title, content], saveDraft)

const fetchData = async () => {
  if (!isNew.value && noteId) {
    loading.value = true
    try {
      const noteData = await notesApi.get(noteId)
      note.value = noteData

      // Check for unsaved draft (within 24h)
      const hoursSince = (Date.now() - draft.value.savedAt) / (1000 * 60 * 60)
      if (draft.value.savedAt && hoursSince < 24 && (draft.value.title || draft.value.content !== '<p></p>')) {
        if (confirm('发现有未保存的草稿，是否恢复？')) {
          title.value = draft.value.title
          content.value = draft.value.content
        } else {
          title.value = noteData.title
          content.value = noteData.content
        }
      } else {
        title.value = noteData.title
        content.value = noteData.content
      }

      const lessonData = await lessonsApi.get(noteData.lesson_id)
      lesson.value = lessonData
      lastSaved.value = new Date(noteData.updated_at)
    } catch {
      toast.error('获取笔记失败')
      router.back()
    } finally {
      loading.value = false
    }
  } else if (lessonId) {
    try {
      const lessonData = await lessonsApi.get(lessonId)
      lesson.value = lessonData
      // Try restore draft for new note
      const hoursSince = (Date.now() - draft.value.savedAt) / (1000 * 60 * 60)
      if (draft.value.savedAt && hoursSince < 24 && (draft.value.title || draft.value.content !== '<p></p>')) {
        if (confirm('发现有未保存的草稿，是否恢复？')) {
          title.value = draft.value.title
          content.value = draft.value.content
        }
      }
    } catch {
      toast.error('获取课文失败')
      router.back()
    }
  }
}

const saveNote = async () => {
  if (!title.value.trim()) {
    toast.error('请输入标题')
    return
  }

  saving.value = true
  try {
    if (isNew.value && lessonId) {
      await notesApi.create({
        lesson_id: lessonId,
        title: title.value,
        content: content.value,
      })
      toast.success('笔记创建成功')
    } else if (noteId) {
      await notesApi.update(noteId, {
        title: title.value,
        content: content.value,
      })
      toast.success('笔记保存成功')
      lastSaved.value = new Date()
    }
    // Clear draft
    draft.value = { title: '', content: '<p></p>', savedAt: 0 }
    isDirty.value = false
    router.back()
  } catch {
    // Error handled by http client
  } finally {
    saving.value = false
  }
}

const handleContentUpdate = (value: string) => {
  content.value = value
}

const handleJsonUpdate = (json: JSONContent) => {
  jsonContent.value = json
}

const goBack = () => {
  if (isDirty.value) {
    if (confirm('有未保存的更改，确定要离开吗？')) {
      router.back()
    }
  } else {
    router.back()
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
          <div class="flex items-center gap-3">
            <button
              class="btn-ghost btn-icon-sm"
              @click="goBack"
            >
              <div class="i-ph-arrow-left-bold text-lg" />
            </button>

            <div>
              <h1 class="text-lg font-bold text-neutral-900 dark:text-white">
                {{ isNew ? '新建笔记' : '编辑笔记' }}
              </h1>
              <p v-if="lesson" class="text-xs text-neutral-500">
                {{ lesson.title }}
              </p>
            </div>
          </div>

          <div class="flex items-center gap-4">
            <!-- Status -->
            <div class="hidden sm:flex items-center gap-3 text-sm text-neutral-500">
              <span class="flex items-center gap-1.5">
                <div class="i-ph-text-t" />
                {{ wordCount }} 字
              </span>
              <span v-if="lastSaved" class="text-neutral-400">
                保存于 {{ lastSaved.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) }}
              </span>
              <span v-else-if="isDirty" class="text-primary-600 dark:text-primary-400 flex items-center gap-1">
                <div class="i-ph-circle-fill text-[6px] animate-pulse" />
                未保存
              </span>
            </div>

            <Button
              :loading="saving"
              :disabled="!title.trim()"
              @click="saveNote"
            >
              <div class="i-ph-check-bold" />
              保存
            </Button>
          </div>
        </div>
      </div>
    </header>

    <main class="container-page py-6 max-w-4xl">
      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-20">
        <div class="i-ph-spinner animate-spin text-4xl text-primary-500" />
      </div>

      <div v-else class="space-y-4">
        <!-- Title Input -->
        <div class="card card-elevated p-6">
          <input
            v-model="title"
            class="w-full text-2xl sm:text-3xl font-bold bg-transparent border-0 outline-none placeholder:text-neutral-300 dark:placeholder:text-neutral-700 text-neutral-900 dark:text-white"
            placeholder="输入笔记标题..."
          />
        </div>

        <!-- Editor -->
        <TiptapEditor
          v-model="content"
          :placeholder="'开始写作...\n\n支持：\n- 标题、列表、任务清单\n- 代码块、引用\n- 表格、图片\n- 选中文字查看浮动工具栏'"
          @update:model-value="handleContentUpdate"
          @update:json="handleJsonUpdate"
        />

        <!-- Mobile Status -->
        <div class="sm:hidden flex items-center justify-between text-sm text-neutral-500 px-2">
          <span>{{ wordCount }} 字</span>
          <span v-if="lastSaved" class="text-neutral-400">
            保存于 {{ lastSaved.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) }}
          </span>
        </div>
      </div>
    </main>
  </div>
</template>
