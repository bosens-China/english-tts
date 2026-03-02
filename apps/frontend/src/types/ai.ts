import type { DialogueLine } from '@/lib/schemas'

export interface GenerateLessonResponse {
  text: string
  audio_script: DialogueLine[]
  new_words: string[]
  grammar: string[]
  culture_notes: string[]
  questions: string[]
}

export interface EvaluateQAResponse {
  score: number
  passed: boolean
  feedback: string
}

export interface PronunciationAssessmentResponse {
  score: number
  passed: boolean
  accuracy: number
  feedback: string
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}
