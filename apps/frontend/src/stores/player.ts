import { ref } from "vue"
import { defineStore } from "pinia"

export const usePlayerStore = defineStore("player", () => {
  const currentText = ref("")
  const speaking = ref(false)
  const rate = ref(1)

  function preview(text: string): void {
    currentText.value = text
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      return
    }

    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = "en-US"
    utterance.rate = rate.value
    utterance.onstart = () => {
      speaking.value = true
    }
    utterance.onend = () => {
      speaking.value = false
    }
    utterance.onerror = () => {
      speaking.value = false
    }
    window.speechSynthesis.speak(utterance)
  }

  function stop(): void {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel()
    }
    speaking.value = false
  }

  return {
    currentText,
    speaking,
    rate,
    preview,
    stop,
  }
})
