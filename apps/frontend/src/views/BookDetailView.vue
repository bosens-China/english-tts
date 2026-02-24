<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { booksApi, lessonsApi } from '@/api/client'
import { LessonItemSkeleton, Modal, Button } from '@/components/ui'
import type { BookWithLessons } from '@/lib/schemas'
import type { DialogueLine } from '@/lib/schemas'

const route = useRoute()
const router = useRouter()
const bookId = route.params.id as string

const book = ref<BookWithLessons | null>(null)
const loading = ref(false)
const showCreateModal = ref(false)
const creating = ref(false)
const activeTab = ref<'json' | 'config'>('json')

const newLessonTitle = ref('')
const newLessonDesc = ref('')
const newLessonSort = ref(0)
const dialogueJson = ref('')
const dialogueError = ref('')
const extractedDialogue = ref<DialogueLine[] | null>(null)

const audioRate = ref('+0%')
const audioPitch = ref('+0Hz')

const rateOptions = [
  { value: '-50%', label: '很慢' },
  { value: '-30%', label: '慢' },
  { value: '-10%', label: '稍慢' },
  { value: '+0%', label: '正常' },
  { value: '+10%', label: '稍快' },
  { value: '+30%', label: '快' },
  { value: '+50%', label: '很快' },
]

const pitchOptions = [
  { value: '-100Hz', label: '很低' },
  { value: '-50Hz', label: '低' },
  { value: '-20Hz', label: '稍低' },
  { value: '+0Hz', label: '正常' },
  { value: '+20Hz', label: '稍高' },
  { value: '+50Hz', label: '高' },
  { value: '+100Hz', label: '很高' },
]

// Auto-calculate sort order
watch(showCreateModal, (show) => {
  if (show && book.value) {
    newLessonSort.value = book.value.lessons.length
    activeTab.value = 'json'
    dialogueJson.value = ''
    dialogueError.value = ''
    extractedDialogue.value = null
    newLessonTitle.value = ''
    newLessonDesc.value = ''
  }
})

const parseDialogueJson = () => {
  if (!dialogueJson.value.trim()) {
    dialogueError.value = ''
    extractedDialogue.value = null
    return
  }
  try {
    const parsed = JSON.parse(dialogueJson.value)

    let dialogue: DialogueLine[] | null = null
    let title = ''
    let scene = ''

    if (Array.isArray(parsed)) {
      dialogue = parsed as DialogueLine[]
    } else if (parsed.dialogue && Array.isArray(parsed.dialogue)) {
      dialogue = parsed.dialogue as DialogueLine[]
      title = parsed.title || ''
      scene = parsed.scene || ''
    } else {
      dialogueError.value = 'JSON 格式错误：必须是数组或包含 dialogue 字段的对象'
      extractedDialogue.value = null
      return
    }

    for (const line of dialogue) {
      if (!line.speaker || !line.voice || !line.text) {
        dialogueError.value = '每行必须包含 speaker, voice, text 字段'
        extractedDialogue.value = null
        return
      }
    }

    dialogueError.value = ''
    extractedDialogue.value = dialogue

    if (title && !newLessonTitle.value) {
      newLessonTitle.value = title
    }
    if (scene && !newLessonDesc.value) {
      newLessonDesc.value = scene
    }
  } catch {
    dialogueError.value = 'JSON 格式错误'
    extractedDialogue.value = null
  }
}

const sortedLessons = computed(() => {
  if (!book.value) return []
  return [...book.value.lessons].sort((a, b) => a.sort_order - b.sort_order)
})

const fetchData = async () => {
  loading.value = true
  try {
    book.value = await booksApi.get(bookId)
  } catch {
    toast.error('获取书籍失败')
    router.push('/')
  } finally {
    loading.value = false
  }
}

const createLesson = async () => {
  if (!newLessonTitle.value.trim()) {
    toast.error('请输入课文标题')
    return
  }

  if (activeTab.value === 'json' && dialogueJson.value.trim()) {
    parseDialogueJson()
  }

  creating.value = true
  try {
    await lessonsApi.create({
      book_id: bookId,
      title: newLessonTitle.value,
      description: newLessonDesc.value,
      sort_order: newLessonSort.value,
      audio: extractedDialogue.value && extractedDialogue.value.length > 0
        ? {
            dialogue: extractedDialogue.value,
            rate: audioRate.value,
            pitch: audioPitch.value,
          }
        : undefined,
    })

    showCreateModal.value = false
    newLessonTitle.value = ''
    newLessonDesc.value = ''
    newLessonSort.value = 0
    dialogueJson.value = ''
    extractedDialogue.value = null
    audioRate.value = '+0%'
    audioPitch.value = '+0Hz'
    await fetchData()
    toast.success('课文创建成功')
  } catch {
    // Error handled by http client
  } finally {
    creating.value = false
  }
}

const deleteLesson = async (id: string) => {
  if (!confirm('确定要删除这个课文吗？笔记和音频也会被删除。')) return

  try {
    await lessonsApi.delete(id)
    await fetchData()
    toast.success('课文已删除')
  } catch {
    // Error handled by http client
  }
}

const goToLesson = (id: string) => {
  router.push(`/lessons/${id}`)
}

onMounted(fetchData)
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100 dark:from-neutral-950 dark:to-neutral-900">
    <!-- Header -->
    <header class="sticky top-0 z-30 glass border-b border-neutral-200/50 dark:border-neutral-800/50">
      <div class="container-page">
        <div class="flex items-center gap-4 h-16">
          <button
            class="btn-ghost btn-icon-sm"
            @click="router.push('/')"
          >
            <div class="i-ph-arrow-left-bold text-lg" />
          </button>

          <div v-if="book" class="flex-1 min-w-0">
            <h1 class="text-lg font-bold text-neutral-900 dark:text-white truncate">
              {{ book.title }}
            </h1>
            <p v-if="book.description" class="text-xs text-neutral-500 truncate hidden sm:block">
              {{ book.description }}
            </p>
          </div>
          <div v-else class="flex-1 h-6 w-32 skeleton rounded" />
        </div>
      </div>
    </header>

    <main class="container-page py-8">
      <!-- Loading State -->
      <div v-if="loading" class="space-y-4">
        <div class="flex items-center justify-between mb-6">
          <div class="h-7 w-40 skeleton rounded" />
          <div class="h-10 w-28 skeleton rounded-xl" />
        </div>
        <LessonItemSkeleton v-for="n in 5" :key="n" />
      </div>

      <template v-else-if="book">
        <!-- Book Info Card -->
        <div class="card card-elevated mb-8 overflow-hidden">
          <div class="p-6 sm:p-8">
            <div class="flex items-start gap-6">
              <!-- Cover -->
              <div class="hidden sm:block w-24 h-24 rounded-2xl flex-shrink-0 overflow-hidden">
                <img
                  v-if="book.cover_url"
                  :src="book.cover_url"
                  class="w-full h-full object-cover"
                />
                <div
                  v-else
                  class="w-full h-full bg-gradient-to-br from-primary-100 to-primary-200 dark:from-primary-900/30 dark:to-primary-800/20 flex items-center justify-center"
                >
                  <div class="i-ph-book-bookmark-fill text-4xl text-primary-400" />
                </div>
              </div>

              <!-- Info -->
              <div class="flex-1 min-w-0">
                <h1 class="text-2xl sm:text-3xl font-bold text-neutral-900 dark:text-white mb-2">
                  {{ book.title }}
                </h1>
                <p v-if="book.description" class="text-neutral-500 dark:text-neutral-400 mb-4">
                  {{ book.description }}
                </p>
                <div class="flex items-center gap-4 text-sm text-neutral-400">
                  <span class="badge badge-secondary">
                    <div class="i-ph-book-open" />
                    {{ book.lessons.length }} 篇课文
                  </span>
                  <span class="flex items-center gap-1">
                    <div class="i-ph-calendar-blank" />
                    {{ new Date(book.created_at).toLocaleDateString('zh-CN') }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Lessons Section -->
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-xl font-bold text-neutral-900 dark:text-white">课文列表</h2>
            <p class="text-sm text-neutral-500 mt-0.5">共 {{ book.lessons.length }} 篇课文</p>
          </div>
          <Button @click="showCreateModal = true">
            <div class="i-ph-plus-bold" />
            <span class="hidden sm:inline">新建课文</span>
          </Button>
        </div>

        <!-- Empty State -->
        <div v-if="sortedLessons.length === 0" class="card py-16 text-center">
          <div class="w-20 h-20 rounded-2xl bg-primary-100 dark:bg-primary-900/20 flex items-center justify-center mx-auto mb-4">
            <div class="i-ph-book-open text-4xl text-primary-500" />
          </div>
          <h3 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200 mb-2">
            还没有课文
          </h3>
          <p class="text-neutral-500 mb-6">创建第一课开始学习吧</p>
          <Button @click="showCreateModal = true">
            <div class="i-ph-plus-bold" />
            添加第一课
          </Button>
        </div>

        <!-- Lessons List -->
        <div v-else class="space-y-3">
          <div
            v-for="(lesson, index) in sortedLessons"
            :key="lesson.id"
            class="group card card-hover card-interactive flex items-center gap-4 p-4 animate-fade-in-up"
            :style="{ animationDelay: `${index * 30}ms` }"
            @click="goToLesson(lesson.id)"
          >
            <!-- Number -->
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary-500/25">
              <span class="text-lg font-bold text-white">{{ index + 1 }}</span>
            </div>

            <!-- Content -->
            <div class="flex-1 min-w-0">
              <h3 class="font-semibold text-neutral-800 dark:text-neutral-200 truncate group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                {{ lesson.title }}
              </h3>
              <p v-if="lesson.description" class="text-sm text-neutral-500 truncate">
                {{ lesson.description }}
              </p>
              <div v-else class="flex items-center gap-2 mt-1">
                <span
                  v-if="lesson.audio"
                  class="badge badge-success text-xs"
                >
                  <div class="i-ph-speaker-high" />
                  音频就绪
                </span>
                <span v-else class="badge badge-secondary text-xs">
                  <div class="i-ph-speaker-slash" />
                  无音频
                </span>
              </div>
            </div>

            <!-- Actions -->
            <button
              class="p-2 rounded-lg text-neutral-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 opacity-0 group-hover:opacity-100 transition-all flex-shrink-0"
              @click.stop="deleteLesson(lesson.id)"
            >
              <div class="i-ph-trash-fill" />
            </button>

            <div class="i-ph-caret-right text-neutral-300 dark:text-neutral-600 opacity-0 group-hover:opacity-100 transition-all -translate-x-2 group-hover:translate-x-0" />
          </div>
        </div>
      </template>
    </main>

    <!-- Create Lesson Modal -->
    <Modal
      v-model:open="showCreateModal"
      title="新建课文"
      description="添加一篇新课文"
      size="lg"
    >
      <!-- Tabs -->
      <div class="flex gap-1 p-1 bg-neutral-100 dark:bg-neutral-800 rounded-xl mb-6">
        <button
          class="flex-1 px-4 py-2 text-sm font-medium rounded-lg transition-all"
          :class="activeTab === 'json' ? 'bg-white dark:bg-neutral-700 text-primary-600 dark:text-primary-400 shadow-sm' : 'text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300'"
          @click="activeTab = 'json'"
        >
          <span class="flex items-center justify-center gap-2">
            <div class="i-ph-code" />
            JSON 配置
          </span>
        </button>
        <button
          class="flex-1 px-4 py-2 text-sm font-medium rounded-lg transition-all"
          :class="activeTab === 'config' ? 'bg-white dark:bg-neutral-700 text-primary-600 dark:text-primary-400 shadow-sm' : 'text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300'"
          @click="activeTab = 'config'"
        >
          <span class="flex items-center justify-center gap-2">
            <div class="iph-sliders-horizontal" />
            详细设置
          </span>
        </button>
      </div>

      <!-- Tab Content: JSON -->
      <div v-if="activeTab === 'json'" class="space-y-5">
        <div>
          <label class="label">
            对话 JSON
            <span class="text-neutral-400 font-normal ml-1">（粘贴后会自动提取信息）</span>
          </label>
          <textarea
            v-model="dialogueJson"
            class="textarea h-56 font-mono text-sm"
            placeholder='{
  "title": "Is this your laptop?",
  "scene": "First day at work...",
  "dialogue": [
    {
      "speaker": "Colleague",
      "voice": "en-US-JennyNeural",
      "text": "Excuse me. Are you the new programmer?",
      "pause_ms": 600
    }
  ]
}'
            @blur="parseDialogueJson"
          />
          <p v-if="dialogueError" class="text-red-500 text-sm mt-2 flex items-center gap-1">
            <div class="i-ph-warning-circle" />
            {{ dialogueError }}
          </p>
          <p v-else class="text-xs text-neutral-400 mt-2">
            支持格式：数组 或 包含 dialogue 字段的对象（可含 title 和 scene）
          </p>
        </div>

        <!-- Parse Success -->
        <div
          v-if="extractedDialogue"
          class="p-4 rounded-xl bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800"
        >
          <div class="flex items-center gap-2 text-green-700 dark:text-green-400">
            <div class="i-ph-check-circle-fill" />
            <span class="font-medium">解析成功</span>
            <span class="text-green-600 dark:text-green-500">· {{ extractedDialogue.length }} 行对话</span>
          </div>
          <div v-if="newLessonTitle" class="mt-2 text-sm text-green-600 dark:text-green-500">
            标题：{{ newLessonTitle }}
          </div>
        </div>
      </div>

      <!-- Tab Content: Config -->
      <div v-else class="space-y-5">
        <div>
          <label class="label">
            课文标题
            <span v-if="newLessonTitle" class="badge badge-success text-xs ml-2">已自动提取</span>
          </label>
          <input
            v-model="newLessonTitle"
            class="input"
            placeholder="例如：Lesson 1 - Excuse me!"
          />
        </div>

        <div>
          <label class="label">
            描述
            <span v-if="newLessonDesc" class="badge badge-success text-xs ml-2">已自动提取</span>
          </label>
          <textarea
            v-model="newLessonDesc"
            class="textarea h-20"
            placeholder="输入课文描述..."
          />
        </div>

        <div>
          <label class="label">排序序号</label>
          <input
            v-model.number="newLessonSort"
            type="number"
            min="0"
            class="input"
            placeholder="0"
          />
          <p class="text-xs text-neutral-400 mt-1.5">数字越小排序越靠前</p>
        </div>

        <!-- Audio Settings -->
        <div v-if="extractedDialogue" class="pt-4 border-t border-neutral-200 dark:border-neutral-800">
          <h4 class="font-medium text-neutral-900 dark:text-white mb-4">音频生成参数</h4>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="label">语速</label>
              <select v-model="audioRate" class="select">
                <option v-for="opt in rateOptions" :key="opt.value" :value="opt.value">
                  {{ opt.label }} ({{ opt.value }})
                </option>
              </select>
            </div>
            <div>
              <label class="label">音调</label>
              <select v-model="audioPitch" class="select">
                <option v-for="opt in pitchOptions" :key="opt.value" :value="opt.value">
                  {{ opt.label }} ({{ opt.value }})
                </option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <Button
          variant="secondary"
          @click="showCreateModal = false"
        >
          取消
        </Button>
        <Button
          :loading="creating"
          :disabled="!newLessonTitle.trim()"
          @click="createLesson"
        >
          创建
        </Button>
      </template>
    </Modal>
  </div>
</template>
