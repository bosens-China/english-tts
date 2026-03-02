<script setup lang="ts">
import { computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { useSessionStore } from "@/stores/session"
import { useAuthStore } from "@/stores/auth"
import { useReviewStore } from "@/stores/review"

const router = useRouter()
const session = useSessionStore()
const auth = useAuthStore()
const review = useReviewStore()

const reviewQueue = computed(() =>
  review.dueTasks.map((item) => ({
    lessonKey: item.lesson_key,
    title: item.text.slice(0, 42),
    dueIn: "今天",
    scoreGate: "60 分及格",
  })),
)

const levelLabel = computed(() => {
  if (session.level === null) return "未定级"
  return `Level ${session.level}`
})

const membershipLabel = computed(() => (auth.user?.membership === "vip" ? "VIP" : "免费"))

function logout(): void {
  auth.logout()
  session.resetOnboarding()
  router.push("/login")
}

onMounted(async () => {
  await review.fetchTasks(true)
})
</script>

<template>
  <main class="min-h-screen bg-neutral-50 px-4 py-10">
    <section class="container-page space-y-6">
      <header class="card p-6">
        <p class="text-sm text-neutral-500">Dashboard</p>
        <h1 class="mt-1 text-2xl font-bold text-neutral-900">欢迎回来，开始今天的英语训练</h1>
        <p class="mt-2 text-neutral-600">
          用户：<span class="font-semibold text-neutral-900">{{ auth.user?.display_name || "-" }}</span>
          ·
          会员：<span class="font-semibold text-primary-700">{{ membershipLabel }}</span>
        </p>
        <p class="mt-2 text-neutral-600">
          当前等级：<span class="font-semibold text-primary-700">{{ levelLabel }}</span>
        </p>
        <button class="btn-ghost mt-3" @click="logout">退出登录</button>
      </header>

      <section class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <article class="card p-6 lg:col-span-2">
          <h2 class="text-lg font-semibold text-neutral-900">学习日历</h2>
          <p class="mt-2 text-sm text-neutral-600">连续打卡 5 天，保持节奏就会有明显提升。</p>
          <div class="mt-4 grid grid-cols-7 gap-2">
            <div
              v-for="day in 14"
              :key="day"
              class="h-9 rounded-lg"
              :class="day % 3 === 0 ? 'bg-primary-500/80' : 'bg-neutral-200'"
            />
          </div>
        </article>

        <article class="card p-6">
          <h2 class="text-lg font-semibold text-neutral-900">今日新课</h2>
          <p class="mt-2 text-sm text-neutral-600">按 N+1 逻辑动态生成课文。</p>
          <button class="btn-primary mt-5 w-full" @click="router.push('/learn/today')">进入学习空间</button>
        </article>
      </section>

      <section class="card p-6">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-neutral-900">待复习课文</h2>
          <button class="btn-ghost btn-sm" @click="router.push('/reviews')">进入复习模式</button>
        </div>
        <ul class="mt-4 space-y-3">
          <li
            v-for="item in reviewQueue"
            :key="item.lessonKey"
            class="flex items-center justify-between rounded-xl border border-neutral-200 bg-white p-4"
          >
            <div>
              <p class="font-medium text-neutral-900">{{ item.title }}</p>
              <p class="text-sm text-neutral-500">截止：{{ item.dueIn }} · {{ item.scoreGate }}</p>
            </div>
            <button class="btn-secondary btn-sm" @click="router.push('/reviews')">开始复习</button>
          </li>
        </ul>
        <p v-if="reviewQueue.length === 0" class="mt-2 text-sm text-neutral-500">今日暂无待复习内容。</p>
      </section>
    </section>
  </main>
</template>
