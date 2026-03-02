import { ref } from 'vue'

type SpeechRecognitionCtor = new () => {
  lang: string
  interimResults: boolean
  continuous: boolean
  onresult: ((event: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null
  onerror: ((event: { error?: string }) => void) | null
  onend: (() => void) | null
  start: () => void
  stop: () => void
}

type SpeechRecognitionInstance = {
  lang: string
  interimResults: boolean
  continuous: boolean
  onresult: ((event: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null
  onerror: ((event: { error?: string }) => void) | null
  onend: (() => void) | null
  start: () => void
  stop: () => void
}

function getSpeechCtor(): SpeechRecognitionCtor | null {
  if (typeof window === 'undefined') return null
  const ctor = (window as Window & { SpeechRecognition?: SpeechRecognitionCtor; webkitSpeechRecognition?: SpeechRecognitionCtor })
    .SpeechRecognition
    ?? (window as Window & { webkitSpeechRecognition?: SpeechRecognitionCtor }).webkitSpeechRecognition
  return ctor ?? null
}

export function useSpeechRecognition(lang = 'en-US') {
  const listening = ref(false)
  const supported = ref(Boolean(getSpeechCtor()))

  let recognition: SpeechRecognitionInstance | null = null
  let resolver: ((value: string) => void) | null = null

  async function start(): Promise<string> {
    const Ctor = getSpeechCtor()
    if (!Ctor) {
      supported.value = false
      return ''
    }
    supported.value = true
    recognition = new Ctor()
    recognition.lang = lang
    recognition.interimResults = false
    recognition.continuous = false

    return new Promise<string>((resolve) => {
      resolver = resolve
      recognition!.onresult = (event: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => {
        const transcript = event.results?.[0]?.[0]?.transcript ?? ''
        resolve(transcript.trim())
      }
      recognition!.onerror = () => {
        resolve('')
      }
      recognition!.onend = () => {
        listening.value = false
      }
      listening.value = true
      recognition!.start()
    })
  }

  function stop(): void {
    recognition?.stop()
    listening.value = false
    if (resolver) {
      resolver('')
      resolver = null
    }
  }

  return {
    listening,
    supported,
    start,
    stop,
  }
}
