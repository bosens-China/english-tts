<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { toast } from 'vue-sonner'
import { lessonsApi, ttsApi } from '@/api/client'
import { Button } from '@/components/ui'
import type { DialogueLine } from '@/lib/schemas'

interface Props {
  audioId: string
  audioUrl: string
  dialogue: DialogueLine[]
  initialRate: string
  initialPitch: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  playing: [index: number | null]
  regenerated: [rate: string, pitch: string]
}>()

// Local playback controls
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(1.0)
const playbackRate = ref(1.0)

const audioElement = ref<HTMLAudioElement | null>(null)

// Audio generation params
const editRate = ref(props.initialRate)
const editPitch = ref(props.initialPitch)
const isRegenerating = ref(false)
const showSettings = ref(false)

// Current line index
const currentLineIndex = ref<number | null>(null)
const isLinePlaying = ref(false)
let lineAudio: HTMLAudioElement | null = null

const progress = computed(() => {
  if (!duration.value) return 0
  return (currentTime.value / duration.value) * 100
})

// Playback controls
const togglePlay = () => {
  if (!audioElement.value) return
  if (isPlaying.value) {
    audioElement.value.pause()
  } else {
    if (lineAudio) {
      stopLinePlay()
    }
    audioElement.value.play()
  }
}

const setVolume = (vol: number) => {
  volume.value = vol
  if (audioElement.value) {
    audioElement.value.volume = vol
  }
}

const setPlaybackRate = (rate: number) => {
  playbackRate.value = rate
  if (audioElement.value) {
    audioElement.value.playbackRate = rate
  }
}

// Single line playback
const stopLinePlay = () => {
  if (lineAudio) {
    lineAudio.pause()
    lineAudio = null
  }
  isLinePlaying.value = false
  currentLineIndex.value = null
  emit('playing', null)
}

const playLine = async (index: number) => {
  if (audioElement.value && !audioElement.value.paused) {
    audioElement.value.pause()
  }

  if (currentLineIndex.value === index && lineAudio) {
    stopLinePlay()
    return
  }

  stopLinePlay()

  const line = props.dialogue[index]
  if (!line) return

  isLinePlaying.value = true
  currentLineIndex.value = index
  emit('playing', index)

  try {
    const blob = await ttsApi.synthesize({
      title: '',
      dialogue: [{
        speaker: line.speaker,
        voice: line.voice,
        text: line.text,
        pause_ms: 0,
      }],
      rate: editRate.value,
      pitch: editPitch.value,
    })

    const url = URL.createObjectURL(blob)
    const audio = new Audio(url)
    lineAudio = audio

    audio.volume = volume.value
    audio.playbackRate = playbackRate.value

    audio.onended = () => {
      stopLinePlay()
      URL.revokeObjectURL(url)
    }

    audio.onerror = () => {
      toast.error('播放失败')
      stopLinePlay()
      URL.revokeObjectURL(url)
    }

    await audio.play()
  } catch {
    toast.error('生成音频失败')
    stopLinePlay()
  }
}

// Audio generation params
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

const saveAndRegenerate = async () => {
  if (editRate.value === props.initialRate && editPitch.value === props.initialPitch) {
    showSettings.value = false
    return
  }

  isRegenerating.value = true
  try {
    await lessonsApi.updateAudio(props.audioId, {
      rate: editRate.value,
      pitch: editPitch.value,
    })

    await lessonsApi.generateAudio(props.audioId)

    emit('regenerated', editRate.value, editPitch.value)

    if (audioElement.value) {
      audioElement.value.load()
      currentTime.value = 0
      isPlaying.value = false
    }

    toast.success('音频已重新生成')
    showSettings.value = false
  } catch {
    toast.error('重新生成失败')
  } finally {
    isRegenerating.value = false
  }
}

// Navigation
const prevLine = () => {
  if (currentLineIndex.value === null) {
    playLine(props.dialogue.length - 1)
  } else if (currentLineIndex.value > 0) {
    playLine(currentLineIndex.value - 1)
  } else {
    playLine(props.dialogue.length - 1)
  }
}

const nextLine = () => {
  if (currentLineIndex.value === null) {
    playLine(0)
  } else if (currentLineIndex.value < props.dialogue.length - 1) {
    playLine(currentLineIndex.value + 1)
  } else {
    playLine(0)
  }
}

const formatTime = (time: number) => {
  if (!time || isNaN(time)) return '0:00'
  const mins = Math.floor(time / 60)
  const secs = Math.floor(time % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// Audio event handlers
const onTimeUpdate = () => {
  if (audioElement.value) {
    currentTime.value = audioElement.value.currentTime
    duration.value = audioElement.value.duration || 0
  }
}

const onEnded = () => {
  isPlaying.value = false
}

// Lifecycle
onMounted(() => {
  if (props.audioUrl) {
    audioElement.value = new Audio(props.audioUrl)
    audioElement.value.volume = volume.value
    audioElement.value.playbackRate = playbackRate.value
    audioElement.value.addEventListener('timeupdate', onTimeUpdate)
    audioElement.value.addEventListener('ended', onEnded)
    audioElement.value.addEventListener('play', () => isPlaying.value = true)
    audioElement.value.addEventListener('pause', () => isPlaying.value = false)
  }
})

onUnmounted(() => {
  if (audioElement.value) {
    audioElement.value.pause()
    audioElement.value.removeEventListener('timeupdate', onTimeUpdate)
    audioElement.value.removeEventListener('ended', onEnded)
  }
  stopLinePlay()
})

// Watch URL changes
watch(() => props.audioUrl, (newUrl) => {
  if (audioElement.value && newUrl) {
    audioElement.value.src = newUrl
    audioElement.value.load()
    isPlaying.value = false
    currentTime.value = 0
  }
})

defineExpose({
  playLine,
})
</script>

<template>
  <div class="space-y-6">
    <!-- Main Player Card -->
    <div class="card card-elevated sticky top-24">
      <!-- Play Controls -->
      <div class="p-6 text-center">
        <div class="flex items-center justify-center gap-4">
          <!-- Prev -->
          <button
            class="w-12 h-12 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-200 dark:hover:bg-neutral-700 transition-all flex items-center justify-center"
            title="上一句"
            @click="prevLine"
          >
            <div class="i-ph-skip-back-fill text-xl" />
          </button>

          <!-- Play/Pause -->
          <button
            class="w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white flex items-center justify-center transition-all hover:scale-105 shadow-lg shadow-primary-500/25 disabled:opacity-50"
            :disabled="isRegenerating"
            @click="togglePlay"
          >
            <div v-if="isRegenerating" class="i-ph-spinner animate-spin text-2xl" />
            <div v-else-if="isPlaying" class="i-ph-pause-fill text-3xl" />
            <div v-else class="i-ph-play-fill text-3xl ml-1" />
          </button>

          <!-- Next -->
          <button
            class="w-12 h-12 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-200 dark:hover:bg-neutral-700 transition-all flex items-center justify-center"
            title="下一句"
            @click="nextLine"
          >
            <div class="i-ph-skip-forward-fill text-xl" />
          </button>
        </div>
      </div>

      <!-- Progress -->
      <div class="px-6 pb-4">
        <div class="flex items-center justify-between text-sm text-neutral-500 mb-2">
          <span>{{ formatTime(currentTime) }}</span>
          <span>{{ formatTime(duration) }}</span>
        </div>
        <div class="h-2 bg-neutral-200 dark:bg-neutral-800 rounded-full overflow-hidden">
          <div
            class="h-full bg-gradient-to-r from-primary-500 to-primary-600 rounded-full transition-all duration-100"
            :style="{ width: `${progress}%` }"
          />
        </div>
      </div>

      <!-- Volume & Speed -->
      <div class="px-6 pb-6 space-y-4">
        <!-- Volume -->
        <div class="flex items-center gap-3">
          <button
            class="text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300"
            @click="setVolume(volume === 0 ? 1 : 0)"
          >
            <div :class="volume === 0 ? 'i-ph-speaker-slash-fill' : volume < 0.5 ? 'i-ph-speaker-low-fill' : 'i-ph-speaker-high-fill'" />
          </button>
          <input
            v-model.number="volume"
            type="range"
            min="0"
            max="1"
            step="0.1"
            class="flex-1 h-1.5 bg-neutral-200 dark:bg-neutral-800 rounded-lg appearance-none cursor-pointer accent-primary-500"
            @input="setVolume(volume)"
          />
          <span class="text-sm text-neutral-500 w-10 text-right">{{ Math.round(volume * 100) }}%</span>
        </div>

        <!-- Speed -->
        <div class="flex items-center justify-center gap-2">
          <span class="text-sm text-neutral-500">速度:</span>
          <div class="flex gap-1 p-1 bg-neutral-100 dark:bg-neutral-800 rounded-lg">
            <button
              v-for="rate in [0.5, 0.8, 1.0, 1.2, 1.5]"
              :key="rate"
              class="px-3 py-1 text-sm rounded-md transition-all"
              :class="playbackRate === rate ? 'bg-white dark:bg-neutral-700 text-primary-600 dark:text-primary-400 shadow-sm' : 'text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300'"
              @click="setPlaybackRate(rate)"
            >
              {{ rate }}x
            </button>
          </div>
        </div>
      </div>

      <!-- Audio Settings -->
      <div class="px-6 py-4 border-t border-neutral-100 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-800/30">
        <div class="flex items-center justify-between">
          <div class="text-sm text-neutral-500">
            <span class="mr-4">
              语速: <span class="font-medium text-neutral-700 dark:text-neutral-300">{{ initialRate }}</span>
            </span>
            <span>
              音调: <span class="font-medium text-neutral-700 dark:text-neutral-300">{{ initialPitch }}</span>
            </span>
          </div>
          <div class="flex gap-2">
            <button
              class="btn-ghost text-sm"
              @click="showSettings = true"
            >
              <div class="i-ph-gear-fill" />
              调整参数
            </button>
            <a
              :href="audioUrl"
              download
              class="btn-ghost text-sm"
              title="下载音频"
            >
              <div class="i-ph-download-simple-fill" />
              下载
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Modal -->
    <div
      v-if="showSettings"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      @click.self="showSettings = false"
    >
      <div class="card w-full max-w-md animate-scale-in">
        <div class="p-6 border-b border-neutral-100 dark:border-neutral-800">
          <h2 class="text-xl font-bold text-neutral-900 dark:text-white">调整音频生成参数</h2>
          <p class="text-sm text-neutral-500 mt-1">
            修改参数后会重新生成音频文件
          </p>
        </div>

        <div class="p-6 space-y-5">
          <div>
            <label class="label">生成语速</label>
            <select v-model="editRate" class="select">
              <option v-for="opt in rateOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }} ({{ opt.value }})
              </option>
            </select>
          </div>

          <div>
            <label class="label">生成音调</label>
            <select v-model="editPitch" class="select">
              <option v-for="opt in pitchOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }} ({{ opt.value }})
              </option>
            </select>
          </div>
        </div>

        <div class="p-6 border-t border-neutral-100 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-800/30 flex justify-end gap-3">
          <Button
            variant="secondary"
            @click="showSettings = false"
          >
            取消
          </Button>
          <Button
            :loading="isRegenerating"
            @click="saveAndRegenerate"
          >
            保存并重新生成
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
