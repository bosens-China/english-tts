import { defineConfig, presetUno, presetIcons, transformerDirectives, transformerVariantGroup } from 'unocss'

export default defineConfig({
  presets: [
    presetUno({
      darkMode: 'class',
    }),
    presetIcons({
      scale: 1.2,
      warn: true,
    }),
  ],
  transformers: [
    transformerDirectives(),
    transformerVariantGroup(),
  ],
  theme: {
    colors: {
      // Primary palette - Modern Indigo
      primary: {
        50: '#eef2ff',
        100: '#e0e7ff',
        200: '#c7d2fe',
        300: '#a5b4fc',
        400: '#818cf8',
        500: '#6366f1',
        600: '#4f46e5',
        700: '#4338ca',
        800: '#3730a3',
        900: '#312e81',
        950: '#1e1b4b',
      },
      // Secondary palette - Warm Coral
      secondary: {
        50: '#fff1f2',
        100: '#ffe4e6',
        200: '#fecdd3',
        300: '#fda4af',
        400: '#fb7185',
        500: '#f43f5e',
        600: '#e11d48',
        700: '#be123c',
        800: '#9f1239',
        900: '#881337',
        950: '#4c0519',
      },
      // Accent - Fresh Teal
      accent: {
        50: '#f0fdfa',
        100: '#ccfbf1',
        200: '#99f6e4',
        300: '#5eead4',
        400: '#2dd4bf',
        500: '#14b8a6',
        600: '#0d9488',
        700: '#0f766e',
        800: '#115e59',
        900: '#134e4a',
        950: '#042f2e',
      },
      // Neutral - Slate
      neutral: {
        50: '#f8fafc',
        100: '#f1f5f9',
        200: '#e2e8f0',
        300: '#cbd5e1',
        400: '#94a3b8',
        500: '#64748b',
        600: '#475569',
        700: '#334155',
        800: '#1e293b',
        900: '#0f172a',
        950: '#020617',
      },
    },
  },
  shortcuts: {
    // Base
    'text-base': 'text-neutral-700 dark:text-neutral-300',
    'text-muted': 'text-neutral-500 dark:text-neutral-400',
    'bg-surface': 'bg-white dark:bg-neutral-900',
    'bg-subtle': 'bg-neutral-50 dark:bg-neutral-800',

    // Layout
    'container-page': 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8',
    'section-padding': 'py-8 sm:py-12',

    // Cards
    'card': 'bg-white dark:bg-neutral-900 rounded-2xl shadow-sm border border-neutral-200 dark:border-neutral-800',
    'card-hover': 'hover:shadow-lg hover:border-neutral-300 dark:hover:border-neutral-700 transition-all duration-300',
    'card-interactive': 'cursor-pointer hover:-translate-y-1 active:translate-y-0',
    'card-elevated': 'shadow-lg shadow-neutral-200/50 dark:shadow-black/20',

    // Glass effect
    'glass': 'bg-white/80 dark:bg-neutral-900/80 backdrop-blur-xl border border-white/20 dark:border-neutral-800/50',
    'glass-strong': 'bg-white/90 dark:bg-neutral-900/90 backdrop-blur-2xl',

    // Buttons - Primary
    'btn-primary': 'inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-xl transition-all duration-200 shadow-sm hover:shadow-md hover:shadow-primary-500/25 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100',
    'btn-secondary': 'inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-neutral-100 hover:bg-neutral-200 dark:bg-neutral-800 dark:hover:bg-neutral-700 text-neutral-700 dark:text-neutral-200 font-medium rounded-xl transition-all duration-200 border border-neutral-200 dark:border-neutral-700 hover:border-neutral-300 dark:hover:border-neutral-600 active:scale-[0.98] disabled:opacity-50',
    'btn-ghost': 'inline-flex items-center justify-center gap-2 px-4 py-2.5 text-neutral-600 dark:text-neutral-400 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 font-medium rounded-xl transition-all duration-200 active:scale-[0.98]',
    'btn-danger': 'inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-red-50 hover:bg-red-100 dark:bg-red-900/20 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400 font-medium rounded-xl transition-all duration-200 border border-red-200 dark:border-red-800 active:scale-[0.98]',

    // Buttons - Sizes
    'btn-sm': 'px-3 py-1.5 text-sm',
    'btn-lg': 'px-6 py-3 text-lg',
    'btn-icon': 'p-2.5',
    'btn-icon-sm': 'p-2',

    // Form elements
    'input': 'w-full px-4 py-3 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl text-neutral-800 dark:text-neutral-200 placeholder:text-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-200',
    'input-error': 'border-red-300 dark:border-red-700 focus:ring-red-500/20 focus:border-red-500',
    'textarea': 'w-full px-4 py-3 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl text-neutral-800 dark:text-neutral-200 placeholder:text-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-200 resize-none',
    'select': 'w-full px-4 py-3 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl text-neutral-800 dark:text-neutral-200 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-200 appearance-none cursor-pointer',
    'label': 'block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1.5',

    // Status badges
    'badge': 'inline-flex items-center gap-1.5 px-2.5 py-0.5 text-xs font-medium rounded-full',
    'badge-primary': 'badge bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400',
    'badge-secondary': 'badge bg-neutral-100 text-neutral-700 dark:bg-neutral-800 dark:text-neutral-300',
    'badge-success': 'badge bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    'badge-warning': 'badge bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
    'badge-danger': 'badge bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',

    // Animations
    'animate-fade-in': 'animate-[fade-in_0.3s_ease-out]',
    'animate-fade-in-up': 'animate-[fade-in-up_0.4s_ease-out]',
    'animate-scale-in': 'animate-[scale-in_0.2s_ease-out]',
    'animate-slide-in': 'animate-[slide-in-right_0.3s_ease-out]',
    'animate-bounce-soft': 'animate-[bounce-soft_2s_ease-in-out_infinite]',
    'animate-pulse-soft': 'animate-[pulse-soft_2s_ease-in-out_infinite]',

    // Skeleton
    'skeleton': 'bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded-lg',
    'skeleton-shimmer': 'bg-gradient-to-r from-neutral-200 via-neutral-300 to-neutral-200 dark:from-neutral-800 dark:via-neutral-700 dark:to-neutral-800 bg-[length:200%_100%] animate-[shimmer_2s_linear_infinite]',

    // Focus rings
    'focus-ring': 'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-neutral-900',
  },
  rules: [
    ['scrollbar-hide', { 'scrollbar-width': 'none', '-ms-overflow-style': 'none' }],
    ['scrollbar-hide::-webkit-scrollbar', { display: 'none' }],
  ],
})
