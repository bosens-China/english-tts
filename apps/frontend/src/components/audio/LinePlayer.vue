<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { toast } from 'vue-sonner'
import { ttsApi } from '@/api/client'
import type { DialogueLine } from '@/lib/schemas'

interface Props {
  dialogue: DialogueLine[]
  rate: string
  pitch: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  playing: [index: number | null]
}>()

// 播放状态
const playingLineIndex = ref<number | null>(null)
const isLoading = ref(false)
let currentAudio: HTMLAudioElement | null = null

// 播放单句
const playLine = async (index: number) => {
  // 如果正在播放同一句话，则停止
  if (playingLineIndex.value === index && currentAudio) {
    stopPlaying()
    return
  }

  // 停止之前的播放
  stopPlaying()

  const line = props.dialogue[index]
  if (!line) return

  isLoading.value = true
  playingLineIndex.value = index
  emit('playing', index)

  try {
    // 调用后端 TTS API 生成单句音频
    const blob = await ttsApi.synthesize({
      title: '',
      dialogue: [{
        speaker: line.speaker,
        voice: line.voice,
        text: line.text,
        pause_ms: 0,
      }],
      rate: props.rate,
      pitch: props.pitch,
    })

    // 创建音频 URL 并播放
    const url = URL.createObjectURL(blob)
    const audio = new Audio(url)
    currentAudio = audio

    audio.onended = () => {
      cleanup()
    }

    audio.onerror = () => {
      toast.error('音频播放失败')
      cleanup()
    }

    await audio.play()
    isLoading.value = false
  } catch (e) {
    toast.error('生成音频失败')
    cleanup()
    isLoading.value = false
  }
}

// 停止播放
const stopPlaying = () => {
  if (currentAudio) {
    currentAudio.pause()
    currentAudio = null
  }
  cleanup()
}

// 清理状态
const cleanup = () => {
  playingLineIndex.value = null
  emit('playing', null)
}

// 组件卸载时清理
onUnmounted(() => {
  stopPlaying()
})

// 暴露方法给父组件
defineExpose({
  playLine,
  stopPlaying,
  playingLineIndex,
  isLoading,
})
</script>

<template>
  <div class="hidden">
    <!-- 这是一个逻辑组件，不渲染任何可见内容 -->
  </div>
</template>
