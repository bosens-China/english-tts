<template>
  <div
    :class="[
      'skeleton-shimmer',
      variantClass,
      { 'rounded-full': circle }
    ]"
    :style="{ width, height }"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  variant?: 'text' | 'rect' | 'circle' | 'card' | 'avatar'
  width?: string
  height?: string
  circle?: boolean
}>()

const variantClass = computed(() => {
  switch (props.variant) {
    case 'text':
      return 'h-4 w-full rounded'
    case 'card':
      return 'h-40 w-full rounded-2xl'
    case 'avatar':
      return 'w-10 h-10 rounded-full'
    case 'circle':
      return 'w-10 h-10 rounded-full'
    default:
      return 'rounded-xl'
  }
})
</script>
