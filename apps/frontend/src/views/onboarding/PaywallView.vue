<script setup lang="ts">
import { useRouter } from "vue-router"
import { useSessionStore } from "@/stores/session"

const router = useRouter()
const session = useSessionStore()

function continueWithTrial(): void {
  session.startTrial()
  router.push("/dashboard")
}

function subscribeNow(): void {
  session.startTrial()
  session.activateSubscription()
  router.push("/dashboard")
}
</script>

<template>
  <main class="min-h-screen bg-gradient-to-b from-secondary-50 to-white px-4 py-10">
    <section class="mx-auto max-w-5xl">
      <header class="mb-8 text-center">
        <p class="text-sm font-medium text-secondary-700">Onboarding 3/3</p>
        <h1 class="mt-2 text-3xl font-bold text-neutral-900">领取试用并解锁 AI 学习全流程</h1>
        <p class="mt-2 text-neutral-600">你已完成定级，下一步开始每日新课与复习任务。</p>
      </header>

      <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
        <article class="rounded-2xl border border-neutral-200 bg-white p-6">
          <h2 class="text-xl font-semibold text-neutral-900">免费试用</h2>
          <p class="mt-2 text-sm text-neutral-600">7 天完整体验：听力、跟读打分、课后问答、AI 助教。</p>
          <p class="mt-6 text-3xl font-bold text-neutral-900">¥0</p>
          <p class="text-sm text-neutral-500">到期后可随时续订</p>
          <button class="btn-secondary mt-6 w-full" @click="continueWithTrial">开始 7 天试用</button>
        </article>

        <article class="rounded-2xl border border-primary-300 bg-primary-50 p-6 shadow-sm">
          <span class="badge-primary">推荐</span>
          <h2 class="mt-2 text-xl font-semibold text-neutral-900">VIP 年度</h2>
          <p class="mt-2 text-sm text-neutral-600">包含所有学习模块、复习引擎和 AI 助教高频调用。</p>
          <p class="mt-6 text-3xl font-bold text-neutral-900">¥299/年</p>
          <p class="text-sm text-neutral-500">折合每天不到 1 元</p>
          <button class="btn-primary mt-6 w-full" @click="subscribeNow">立即订阅</button>
        </article>
      </div>

      <footer class="mt-6 text-center text-sm text-neutral-500">支付接入占位：后续对接 Stripe SDK。</footer>
    </section>
  </main>
</template>
