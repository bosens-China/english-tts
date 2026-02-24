<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { booksApi } from '@/api/client'
import { BookCardSkeleton, Modal, Button } from '@/components/ui'
import type { Book } from '@/lib/schemas'

const router = useRouter()
const books = ref<Book[]>([])
const loading = ref(false)
const showCreateModal = ref(false)
const creating = ref(false)

const newBookTitle = ref('')
const newBookDesc = ref('')
const newBookCover = ref('')

const fetchBooks = async () => {
  loading.value = true
  try {
    books.value = await booksApi.list()
  } catch {
    toast.error('获取书籍列表失败')
  } finally {
    loading.value = false
  }
}

const createBook = async () => {
  if (!newBookTitle.value.trim()) return

  creating.value = true
  try {
    await booksApi.create({
      title: newBookTitle.value,
      description: newBookDesc.value,
      cover_url: newBookCover.value,
    })
    showCreateModal.value = false
    newBookTitle.value = ''
    newBookDesc.value = ''
    newBookCover.value = ''
    await fetchBooks()
    toast.success('书籍创建成功')
  } catch {
    // Error handled by http client
  } finally {
    creating.value = false
  }
}

const deleteBook = async (id: string) => {
  if (!confirm('确定要删除这本书吗？所有课文和关联数据都会被删除。')) return

  try {
    await booksApi.delete(id)
    await fetchBooks()
    toast.success('书籍已删除')
  } catch {
    // Error handled by http client
  }
}

const goToBook = (id: string) => {
  router.push(`/books/${id}`)
}

onMounted(fetchBooks)
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100 dark:from-neutral-950 dark:to-neutral-900">
    <!-- Header -->
    <header class="sticky top-0 z-30 glass border-b border-neutral-200/50 dark:border-neutral-800/50">
      <div class="container-page">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-lg shadow-primary-500/25">
              <div class="i-ph-books-fill text-xl text-white" />
            </div>
            <div>
              <h1 class="text-xl font-bold bg-gradient-to-r from-neutral-900 to-neutral-600 dark:from-white dark:to-neutral-400 bg-clip-text text-transparent">
                英语学习平台
              </h1>
              <p class="text-xs text-neutral-500 hidden sm:block">English Learning Hub</p>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2">
            <button
              class="btn-ghost hidden sm:flex"
              @click="router.push('/notes')"
            >
              <div class="i-ph-notebook-bold" />
              <span>我的笔记</span>
            </button>
            <button
              class="btn-ghost sm:hidden p-2.5"
              @click="router.push('/notes')"
            >
              <div class="i-ph-notebook-bold text-lg" />
            </button>

            <Button
              @click="showCreateModal = true"
            >
              <div class="i-ph-plus-bold" />
              <span class="hidden sm:inline">新建书籍</span>
            </Button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container-page py-8">
      <!-- Stats Banner -->
      <div
        v-if="!loading && books.length > 0"
        class="mb-8 p-6 rounded-2xl bg-gradient-to-r from-primary-500/10 via-primary-500/5 to-transparent border border-primary-500/10"
      >
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-primary-500/20 flex items-center justify-center">
            <div class="i-ph-books text-2xl text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <p class="text-2xl font-bold text-neutral-900 dark:text-white">{{ books.length }}</p>
            <p class="text-sm text-neutral-500">本学习书籍</p>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <BookCardSkeleton v-for="n in 6" :key="n" />
      </div>

      <!-- Empty State -->
      <div
        v-else-if="books.length === 0"
        class="card card-elevated py-20"
      >
        <div class="text-center">
          <div class="w-24 h-24 rounded-3xl bg-gradient-to-br from-primary-100 to-primary-200 dark:from-primary-900/30 dark:to-primary-800/20 flex items-center justify-center mx-auto mb-6">
            <div class="i-ph-books text-5xl text-primary-500" />
          </div>
          <h2 class="text-xl font-semibold text-neutral-800 dark:text-neutral-200 mb-2">
            开启你的学习之旅
          </h2>
          <p class="text-neutral-500 dark:text-neutral-400 mb-6 max-w-sm mx-auto">
            还没有书籍，创建第一本开始你的英语学习吧
          </p>
          <Button @click="showCreateModal = true">
            <div class="i-ph-plus-bold" />
            创建第一本书
          </Button>
        </div>
      </div>

      <!-- Books Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="(book, index) in books"
          :key="book.id"
          class="group card card-hover card-interactive overflow-hidden animate-fade-in-up"
          :style="{ animationDelay: `${index * 50}ms` }"
          @click="goToBook(book.id)"
        >
          <!-- Cover -->
          <div class="aspect-[16/10] relative overflow-hidden">
            <div
              v-if="book.cover_url"
              class="absolute inset-0 bg-cover bg-center transition-transform duration-500 group-hover:scale-105"
              :style="{ backgroundImage: `url(${book.cover_url})` }"
            />
            <div
              v-else
              class="absolute inset-0 bg-gradient-to-br from-primary-100 via-primary-50 to-neutral-100 dark:from-primary-900/30 dark:via-primary-800/20 dark:to-neutral-800 flex items-center justify-center"
            >
              <div class="i-ph-book-bookmark-fill text-6xl text-primary-300 dark:text-primary-700" />
            </div>

            <!-- Gradient overlay -->
            <div class="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

            <!-- Delete button -->
            <button
              class="absolute top-3 right-3 p-2 rounded-lg bg-white/90 dark:bg-neutral-900/90 text-neutral-400 hover:text-red-500 shadow-sm opacity-0 group-hover:opacity-100 transition-all duration-200 translate-y-2 group-hover:translate-y-0"
              @click.stop="deleteBook(book.id)"
            >
              <div class="i-ph-trash-fill" />
            </button>
          </div>

          <!-- Content -->
          <div class="p-5">
            <h2 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200 mb-2 line-clamp-1 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
              {{ book.title }}
            </h2>
            <p
              v-if="book.description"
              class="text-sm text-neutral-500 dark:text-neutral-400 line-clamp-2 mb-4"
            >
              {{ book.description }}
            </p>
            <div v-else class="h-10 mb-4" />

            <div class="flex items-center justify-between text-xs text-neutral-400">
              <span class="flex items-center gap-1">
                <div class="i-ph-calendar-blank" />
                {{ new Date(book.created_at).toLocaleDateString('zh-CN') }}
              </span>
              <span class="flex items-center gap-1 text-primary-600 dark:text-primary-400 font-medium">
                开始学习
                <div class="i-ph-arrow-right transition-transform group-hover:translate-x-1" />
              </span>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Create Book Modal -->
    <Modal
      v-model:open="showCreateModal"
      title="新建书籍"
      description="创建一本新的英语学习书籍"
      size="md"
    >
      <div class="space-y-5">
        <div>
          <label class="label">
            书名 <span class="text-red-500">*</span>
          </label>
          <input
            v-model="newBookTitle"
            class="input"
            placeholder="例如：新概念英语第一册"
            @keyup.enter="createBook"
          />
        </div>

        <div>
          <label class="label">描述（可选）</label>
          <textarea
            v-model="newBookDesc"
            class="textarea h-24"
            placeholder="输入书籍描述..."
          />
        </div>

        <div>
          <label class="label">封面 URL（可选）</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <div class="iph-image text-neutral-400" />
            </div>
            <input
              v-model="newBookCover"
              class="input pl-10"
              placeholder="https://example.com/cover.jpg"
            />
          </div>
          <p class="text-xs text-neutral-400 mt-1.5">留空将使用默认封面</p>
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
          :disabled="!newBookTitle.trim()"
          @click="createBook"
        >
          创建
        </Button>
      </template>
    </Modal>
  </div>
</template>
