<script setup lang="ts">
import { cn } from '@/lib/utils'

interface Props {
  icon?: string
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
  class?: string
}

withDefaults(defineProps<Props>(), {
  icon: 'i-ph-question',
})
</script>

<template>
  <div :class="cn('flex flex-col items-center justify-center py-16 px-4 text-center', $props.class)">
    <div
      :class="cn(
        'w-20 h-20 rounded-2xl flex items-center justify-center mb-5',
        'bg-gradient-to-br from-neutral-100 to-neutral-200 dark:from-neutral-800 dark:to-neutral-900',
        'shadow-inner',
      )"
    >
      <div :class="cn(icon, 'text-4xl text-neutral-400 dark:text-neutral-500')" />
    </div>

    <h3 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200 mb-2">
      {{ title }}
    </h3>

    <p v-if="description" class="text-sm text-neutral-500 dark:text-neutral-400 max-w-sm mb-6">
      {{ description }}
    </p>

    <button
      v-if="action"
      class="btn-primary"
      @click="action.onClick"
    >
      {{ action.label }}
    </button>

    <slot />
  </div>
</template>
