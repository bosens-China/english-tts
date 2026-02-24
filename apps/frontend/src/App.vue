<template>
  <div class="antialiased text-neutral-900 dark:text-neutral-100">
    <RouterView v-slot="{ Component }">
      <Transition
        name="page"
        mode="out-in"
      >
        <component :is="Component" />
      </Transition>
    </RouterView>
    <Toaster
      position="top-center"
      :rich-colors="true"
      :close-button="true"
    />
  </div>
</template>

<style>
/* Page transition */
.page-enter-active,
.page-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.dark ::-webkit-scrollbar-thumb {
  background: #475569;
}

.dark ::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}

/* Selection */
::selection {
  background: #c7d2fe;
  color: #1e1b4b;
}

.dark ::selection {
  background: #4338ca;
  color: #e0e7ff;
}

/* Focus outline */
:focus-visible {
  outline: 2px solid #6366f1;
  outline-offset: 2px;
}

/* Smooth scroll */
html {
  scroll-behavior: smooth;
}

/* Disable smooth scroll for reduced motion preference */
@media (prefers-reduced-motion: reduce) {
  html {
    scroll-behavior: auto;
  }
  
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
