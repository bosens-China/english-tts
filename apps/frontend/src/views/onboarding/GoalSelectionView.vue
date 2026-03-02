<script setup lang="ts">
import { computed } from "vue"
import { useRouter } from "vue-router"
import { goalOptions } from "@/data/onboarding"
import { useSessionStore } from "@/stores/session"
import type { LearningGoal } from "@/types/onboarding"

const router = useRouter()
const session = useSessionStore()

const selectedGoal = computed(() => session.goal)

function selectGoal(goal: LearningGoal): void {
  session.setGoal(goal)
}

function goNext(): void {
  if (!selectedGoal.value) return
  router.push("/onboarding/level")
}
</script>

<template>
  <main class="min-h-screen bg-gradient-to-b from-primary-50 to-white px-4 py-10">
    <section class="mx-auto max-w-4xl">
      <header class="mb-8">
        <p class="text-sm font-medium text-primary-600">Onboarding 1/3</p>
        <h1 class="mt-2 text-3xl font-bold text-neutral-900">你学英语最主要的目标是？</h1>
        <p class="mt-2 text-neutral-600">先选一个主要目标，系统会用它来组织后续课文场景。</p>
      </header>

      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <button
          v-for="goal in goalOptions"
          :key="goal.id"
          class="w-full rounded-2xl border p-5 text-left transition"
          :class="
            selectedGoal === goal.id
              ? 'border-primary-500 bg-primary-50 shadow-md'
              : 'border-neutral-200 bg-white hover:border-primary-300 hover:shadow-sm'
          "
          @click="selectGoal(goal.id)"
        >
          <div class="mb-3 flex items-center gap-3">
            <span class="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-neutral-100">
              <span :class="goal.icon" class="text-lg text-neutral-700" />
            </span>
            <h2 class="text-lg font-semibold text-neutral-900">{{ goal.title }}</h2>
          </div>
          <p class="text-sm text-neutral-600">{{ goal.description }}</p>
        </button>
      </div>

      <footer class="mt-8 flex items-center justify-end">
        <button class="btn-primary" :disabled="!selectedGoal" @click="goNext">下一步：选择等级</button>
      </footer>
    </section>
  </main>
</template>
