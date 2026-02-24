<script setup lang="ts">
import { ref } from 'vue'
import { stringToColor, getContrastColor } from '@/lib/colors'

interface Props {
  dialogue: Array<{
    speaker: string
    text: string
    voice: string
  }>
  currentIndex: number | null
  playingLineIndex: number | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  select: [index: number]
  playLine: [index: number]
}>()

const hoveredIndex = ref<number | null>(null)

const handleClick = (index: number) => {
  emit('select', index)
  emit('playLine', index)
}

const getSpeakerStyle = (speaker: string) => {
  const bgColor = stringToColor(speaker)
  const textColor = getContrastColor(bgColor)

  return {
    backgroundColor: bgColor + '20',
    color: textColor,
    borderColor: bgColor + '40',
  }
}
</script>

<template>
  <div class="space-y-3">
    <div
      v-for="(line, index) in dialogue"
      :key="index"
      class="group relative p-4 rounded-xl transition-all cursor-pointer border-2"
      :class="[
        playingLineIndex === index
          ? 'bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-800 shadow-sm'
          : 'bg-white dark:bg-neutral-800/50 border-transparent hover:border-neutral-200 dark:hover:border-neutral-700 hover:shadow-sm',
      ]"
      @click="handleClick(index)"
      @mouseenter="hoveredIndex = index"
      @mouseleave="hoveredIndex = null"
    >
      <!-- Speaker Badge -->
      <div class="flex items-center gap-3 mb-3">
        <span
          class="text-sm font-medium px-3 py-1.5 rounded-lg border"
          :style="getSpeakerStyle(line.speaker)"
        >
          {{ line.speaker }}
        </span>

        <!-- Playing Indicator -->
        <div
          v-if="playingLineIndex === index"
          class="flex items-center gap-1.5 text-primary-600 dark:text-primary-400 bg-primary-100 dark:bg-primary-900/30 px-2.5 py-1 rounded-lg"
        >
          <div class="i-ph-speaker-high-fill text-sm animate-pulse" />
          <span class="text-xs font-medium">播放中</span>
        </div>
      </div>

      <!-- Text -->
      <p
        class="text-base leading-relaxed text-neutral-700 dark:text-neutral-300 pl-1"
        :class="playingLineIndex === index ? 'text-neutral-900 dark:text-white' : ''"
      >
        {{ line.text }}
      </p>

      <!-- Hover Play Button -->
      <button
        v-if="hoveredIndex === index && playingLineIndex !== index"
        class="absolute right-4 top-1/2 -translate-y-1/2 w-11 h-11 rounded-full bg-primary-500 hover:bg-primary-600 text-white flex items-center justify-center shadow-lg shadow-primary-500/30 transition-all hover:scale-110"
        @click.stop="handleClick(index)"
      >
        <div class="i-ph-play-fill text-lg ml-0.5" />
      </button>

      <!-- Index Number -->
      <span
        class="absolute left-2 top-2 text-xs text-neutral-300 dark:text-neutral-600 font-medium opacity-0 group-hover:opacity-100 transition-opacity"
      >
        {{ index + 1 }}
      </span>
    </div>
  </div>
</template>
