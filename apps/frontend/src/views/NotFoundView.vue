<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui'

const router = useRouter()
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100 dark:from-neutral-950 dark:to-neutral-900 flex items-center justify-center p-4">
    <div class="text-center max-w-md">
      <!-- 404 Icon -->
      <div class="relative mb-8">
        <div class="w-32 h-32 rounded-full bg-gradient-to-br from-primary-100 to-primary-200 dark:from-primary-900/30 dark:to-primary-800/20 flex items-center justify-center mx-auto">
          <div class="i-ph-question-fill text-6xl text-primary-500" />
        </div>
        <div class="absolute -bottom-2 -right-2 w-12 h-12 rounded-full bg-white dark:bg-neutral-800 shadow-lg flex items-center justify-center">
          <span class="text-xl font-bold text-primary-600">404</span>
        </div>
      </div>

      <!-- Title -->
      <h1 class="text-4xl font-bold text-neutral-900 dark:text-white mb-3">
        页面不存在
      </h1>
      <p class="text-neutral-500 dark:text-neutral-400 mb-8">
        抱歉，您访问的页面可能已经删除或不存在
      </p>

      <!-- Actions -->
      <div class="flex flex-col sm:flex-row gap-3 justify-center">
        <Button
          variant="secondary"
          @click="router.back()"
        >
          <div class="i-ph-arrow-left-bold" />
          返回上一页
        </Button>
        <Button @click="router.push('/')">
          <div class="i-ph-house-fill" />
          回到首页
        </Button>
      </div>
    </div>
  </div>
</template>
