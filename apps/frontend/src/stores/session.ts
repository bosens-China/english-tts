import { computed, ref, watch } from "vue"
import { defineStore } from "pinia"
import type { LearningGoal } from "@/types/onboarding"

const STORAGE_KEY = "english-tts-session-v1"

interface SessionState {
  goal: LearningGoal | null
  level: number | null
  trialStartedAt: string | null
  subscribed: boolean
}

function loadSession(): SessionState {
  if (typeof window === "undefined") {
    return {
      goal: null,
      level: null,
      trialStartedAt: null,
      subscribed: false,
    }
  }

  const raw = window.localStorage.getItem(STORAGE_KEY)
  if (!raw) {
    return {
      goal: null,
      level: null,
      trialStartedAt: null,
      subscribed: false,
    }
  }

  try {
    const parsed = JSON.parse(raw) as SessionState
    return {
      goal: parsed.goal ?? null,
      level: parsed.level ?? null,
      trialStartedAt: parsed.trialStartedAt ?? null,
      subscribed: Boolean(parsed.subscribed),
    }
  } catch {
    return {
      goal: null,
      level: null,
      trialStartedAt: null,
      subscribed: false,
    }
  }
}

export const useSessionStore = defineStore("session", () => {
  const initial = loadSession()
  const goal = ref<LearningGoal | null>(initial.goal)
  const level = ref<number | null>(initial.level)
  const trialStartedAt = ref<string | null>(initial.trialStartedAt)
  const subscribed = ref<boolean>(initial.subscribed)

  const hasGoal = computed(() => goal.value !== null)
  const hasLevel = computed(() => level.value !== null)
  const onboardingCompleted = computed(() => hasGoal.value && hasLevel.value)

  function setGoal(value: LearningGoal): void {
    goal.value = value
  }

  function setLevel(value: number): void {
    level.value = value
  }

  function startTrial(): void {
    if (!trialStartedAt.value) {
      trialStartedAt.value = new Date().toISOString()
    }
  }

  function activateSubscription(): void {
    subscribed.value = true
  }

  function resetOnboarding(): void {
    goal.value = null
    level.value = null
    trialStartedAt.value = null
    subscribed.value = false
  }

  watch(
    [goal, level, trialStartedAt, subscribed],
    () => {
      if (typeof window === "undefined") return
      const payload: SessionState = {
        goal: goal.value,
        level: level.value,
        trialStartedAt: trialStartedAt.value,
        subscribed: subscribed.value,
      }
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
    },
    { deep: false },
  )

  return {
    goal,
    level,
    trialStartedAt,
    subscribed,
    hasGoal,
    hasLevel,
    onboardingCompleted,
    setGoal,
    setLevel,
    startTrial,
    activateSubscription,
    resetOnboarding,
  }
})
