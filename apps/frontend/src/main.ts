import { createApp } from 'vue'
import { Toaster } from 'vue-sonner'
import '@unocss/reset/tailwind.css'
import 'virtual:uno.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(router)
app.component('Toaster', Toaster)

// Global error handler
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue Error:', err, instance, info)
}

app.mount('#app')
