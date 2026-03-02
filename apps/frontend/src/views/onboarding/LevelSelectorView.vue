<script setup lang="ts">
import { computed, ref } from "vue"
import { useRouter } from "vue-router"
import { levelCards } from "@/data/onboarding"
import { usePlayerStore } from "@/stores/player"
import { useSessionStore } from "@/stores/session"
import type { LevelCard } from "@/types/onboarding"

const router = useRouter()
const player = usePlayerStore()
const session = useSessionStore()

const activeIndex = ref(session.level ?? 0)
const fallbackCard = levelCards[0] as LevelCard
const activeCard = computed(() => levelCards[activeIndex.value] ?? fallbackCard)

function prevCard(): void {
  activeIndex.value = (activeIndex.value - 1 + levelCards.length) % levelCards.length
}

function nextCard(): void {
  activeIndex.value = (activeIndex.value + 1) % levelCards.length
}

function playPreview(): void {
  player.preview(activeCard.value.previewText)
}

function confirmLevel(): void {
  if (!activeCard.value) return
  session.setLevel(activeCard.value.id)
  router.push("/dashboard")
}
</script>

<template>
  <main class="min-h-screen bg-gradient-to-b from-white to-accent-50 px-4 py-10">
    <section class="mx-auto max-w-4xl">
      <header class="mb-8">
        <p class="text-sm font-medium text-accent-700">Onboarding 2/3</p>
        <h1 class="mt-2 text-3xl font-bold text-neutral-900">滑动试听，选择你的起始等级</h1>
        <p class="mt-2 text-neutral-600">建议选择“刚好能听懂但有点吃力”的等级。</p>
      </header>

      <div class="rounded-3xl border border-neutral-200 bg-white p-6 shadow-xl">
        <div class="mb-4 flex items-center justify-between">
          <span class="badge-primary">{{ activeCard.title }}</span>
          <span class="text-sm text-neutral-500">{{ activeCard.cefr }} · {{ activeCard.label }}</span>
        </div>

        <p class="text-lg leading-8 text-neutral-900">{{ activeCard.previewText }}</p>
        <p class="mt-3 text-sm leading-7 text-neutral-600">{{ activeCard.zhHint }}</p>

        <div class="mt-6 flex flex-wrap items-center gap-3">
          <button class="btn-secondary btn-sm" @click="playPreview">
            <span class="ph:speaker-high-fill text-base" />
            试听
          </button>
          <button class="btn-secondary btn-sm" @click="prevCard">
            <span class="ph:caret-left-bold text-base" />
            上一档
          </button>
          <button class="btn-secondary btn-sm" @click="nextCard">
            下一档
            <span class="ph:caret-right-bold text-base" />
          </button>
        </div>
      </div>

      <footer class="mt-8 flex items-center justify-between">
        <button class="btn-ghost" @click="router.push('/onboarding/goal')">返回目标选择</button>
        <button class="btn-primary" @click="confirmLevel">就从这里开始</button>
      </footer>
    </section>
  </main>
</template>
