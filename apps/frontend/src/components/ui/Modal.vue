<script setup lang="ts">
import { DialogContent, DialogDescription, DialogTitle, DialogRoot, DialogOverlay, DialogPortal } from 'reka-ui'
import { cn } from '@/lib/utils'

interface Props {
  open: boolean
  title?: string
  description?: string
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  showClose?: boolean
}

withDefaults(defineProps<Props>(), {
  size: 'md',
  showClose: true,
})

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const sizeClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-2xl',
  full: 'max-w-[90vw]',
}
</script>

<template>
  <DialogRoot :open="open" @update:open="emit('update:open', $event)">
    <DialogPortal>
      <DialogOverlay
        class="fixed inset-0 bg-black/50 z-50 data-[state=open]:animate-[fade-in_0.2s_ease-out]"
      />
      <DialogContent
        :class="cn(
          'fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50',
          'p-0 gap-0 overflow-hidden',
          'bg-white dark:bg-neutral-900 rounded-2xl',
          'shadow-2xl shadow-black/10',
          'data-[state=open]:animate-[scale-in_0.2s_ease-out]',
          'focus:outline-none',
          sizeClasses[size],
        )"
      >
        <div
          v-if="title || description"
          :class="cn(
            'px-6 py-4 border-b border-neutral-100 dark:border-neutral-800',
            'bg-gradient-to-r from-neutral-50/50 to-transparent dark:from-neutral-800/30',
          )"
        >
          <DialogTitle
            v-if="title"
            class="text-lg font-semibold text-neutral-900 dark:text-neutral-100"
          >
            {{ title }}
          </DialogTitle>
          <DialogDescription
            v-if="description"
            class="text-sm text-neutral-500 dark:text-neutral-400 mt-1"
          >
            {{ description }}
          </DialogDescription>
        </div>

        <div class="px-6 py-5">
          <slot />
        </div>

        <div
          v-if="$slots.footer"
          class="px-6 py-4 border-t border-neutral-100 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-800/30 flex justify-end gap-3"
        >
          <slot name="footer" />
        </div>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
