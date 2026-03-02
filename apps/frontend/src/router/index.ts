import { createRouter, createWebHistory } from "vue-router"
import BookListView from "@/views/BookListView.vue"
import BookDetailView from "@/views/BookDetailView.vue"
import DashboardView from "@/views/DashboardView.vue"
import LessonDetailView from "@/views/LessonDetailView.vue"
import NoteEditView from "@/views/NoteEditView.vue"
import NoteListView from "@/views/NoteListView.vue"
import NoteView from "@/views/NoteView.vue"
import DailyLearningView from "@/views/DailyLearningView.vue"
import ReviewView from "@/views/ReviewView.vue"
import LevelSelectorView from "@/views/onboarding/LevelSelectorView.vue"
import GoalSelectionView from "@/views/onboarding/GoalSelectionView.vue"
import PaywallView from "@/views/onboarding/PaywallView.vue"
import NotFoundView from "@/views/NotFoundView.vue"
import LoginView from "@/views/LoginView.vue"
import { useSessionStore } from "@/stores/session"
import { useAuthStore } from "@/stores/auth"

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      redirect: () => "/dashboard",
    },
    {
      path: "/login",
      name: "login",
      component: LoginView,
      meta: { guestOnly: true },
    },
    {
      path: "/onboarding/goal",
      name: "onboarding-goal",
      component: GoalSelectionView,
      meta: { onboardingStep: "goal" },
    },
    {
      path: "/onboarding/level",
      name: "onboarding-level",
      component: LevelSelectorView,
      meta: { onboardingStep: "level" },
    },
    {
      path: "/onboarding/paywall",
      name: "onboarding-paywall",
      component: PaywallView,
      meta: { onboardingStep: "paywall" },
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: DashboardView,
    },
    {
      path: "/learn/today",
      name: "daily-learning",
      component: DailyLearningView,
    },
    {
      path: "/reviews",
      name: "reviews",
      component: ReviewView,
    },
    {
      path: "/library",
      name: "books",
      component: BookListView,
    },
    {
      path: "/books/:id",
      name: "book-detail",
      component: BookDetailView,
    },
    {
      path: "/lessons/:id",
      name: "lesson-detail",
      component: LessonDetailView,
    },
    {
      path: "/lessons/:lessonId/notes/new",
      name: "note-create",
      component: NoteEditView,
    },
    {
      path: "/notes",
      name: "note-list",
      component: NoteListView,
    },
    {
      path: "/notes/:id",
      name: "note-view",
      component: NoteView,
    },
    {
      path: "/notes/:id/edit",
      name: "note-edit",
      component: NoteEditView,
    },
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: NotFoundView,
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  const session = useSessionStore()
  const inOnboarding = to.path.startsWith("/onboarding")
  const isLogin = to.path === "/login"

  if (!auth.isAuthenticated && !isLogin) {
    return "/login"
  }

  if (auth.isAuthenticated && isLogin) {
    return "/dashboard"
  }

  if (!session.hasGoal && to.path !== "/onboarding/goal") {
    return "/onboarding/goal"
  }

  if (session.hasGoal && !session.hasLevel && to.path !== "/onboarding/level") {
    return "/onboarding/level"
  }
  if (session.onboardingCompleted && inOnboarding && to.path !== "/onboarding/paywall") return "/dashboard"

  return true
})

export default router
