<template>
  <div class="card flex items-center gap-4 p-4">
    <!-- Number skeleton -->
    <div class="w-12 h-12 rounded-xl skeleton-shimmer flex-shrink-0" />

    <!-- Content -->
    <div class="flex-1 space-y-2 min-w-0">
      <div class="h-5 w-2/3 skeleton-shimmer rounded" />
      <div class="h-4 w-1/2 skeleton-shimmer rounded" />
    </div>

    <!-- Action skeleton -->
    <div class="w-8 h-8 rounded-lg skeleton-shimmer flex-shrink-0" />
  </div>
</template>
