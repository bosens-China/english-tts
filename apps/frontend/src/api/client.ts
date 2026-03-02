import { fetchApi } from '@/lib/http'
import type {
  Book,
  BookWithLessons,
  Lesson,
  Note,
  DialogueLine,
  CreateBookData,
  CreateLessonData,
  UpdateLessonData,
  CreateNoteData,
  UpdateAudioData,
} from '@/lib/schemas'
import type { LoginResponse, UserProfile } from '@/types/auth'
import type {
  ChatMessage,
  EvaluateQAResponse,
  GenerateLessonResponse,
  PronunciationAssessmentResponse,
} from '@/types/ai'
import type { ReviewTask } from '@/types/review'

// ==================== Book API ====================
export const booksApi = {
  list: () => fetchApi<Book[]>('/books'),
  get: (id: string) => fetchApi<BookWithLessons>(`/books/${id}`),
  create: (data: CreateBookData) => fetchApi<Book>('/books', {
    method: 'POST',
    body: data,
  }),
  update: (id: string, data: CreateBookData) => fetchApi<Book>(`/books/${id}`, {
    method: 'PUT',
    body: data,
  }),
  delete: (id: string) => fetchApi<void>(`/books/${id}`, {
    method: 'DELETE',
  }),
}

// ==================== Lesson API ====================
export const lessonsApi = {
  list: (bookId?: string) => fetchApi<Lesson[]>(`/lessons${bookId ? `?book_id=${bookId}` : ''}`),
  get: (id: string) => fetchApi<Lesson>(`/lessons/${id}`),
  create: (data: CreateLessonData) => fetchApi<Lesson>('/lessons', {
    method: 'POST',
    body: data,
  }),
  update: (id: string, data: UpdateLessonData) => fetchApi<Lesson>(`/lessons/${id}`, {
    method: 'PUT',
    body: data,
  }),
  delete: (id: string) => fetchApi<void>(`/lessons/${id}`, {
    method: 'DELETE',
  }),
  // 音频相关
  generateAudio: (id: string) => fetchApi<{ message: string }>(`/lessons/${id}/audio/generate`, {
    method: 'POST',
  }),
  updateAudio: (id: string, data: UpdateAudioData) => fetchApi<Lesson>(`/lessons/${id}/audio`, {
    method: 'PUT',
    body: data,
  }),
  downloadAudio: (id: string) => `${API_BASE}/lessons/${id}/audio/download`,
}

const API_BASE = '/api'

// ==================== Auth API ====================
export const authApi = {
  login: (data: { username: string; password: string }) => fetchApi<LoginResponse>('/auth/login', {
    method: 'POST',
    body: data,
  }),
  me: () => fetchApi<UserProfile>('/auth/me'),
}

// ==================== AI API ====================
export const aiApi = {
  generateLesson: (data: { level: number; goal: string }) =>
    fetchApi<GenerateLessonResponse>('/ai/generate-lesson', {
      method: 'POST',
      body: data,
    }),
  evaluateQA: (data: { lesson_text: string; question: string; user_answer: string }) =>
    fetchApi<EvaluateQAResponse>('/ai/evaluate-qa', {
      method: 'POST',
      body: data,
    }),
  evaluatePronunciation: (data: { reference_text: string; spoken_text: string }) =>
    fetchApi<PronunciationAssessmentResponse>('/ai/evaluate-pronunciation', {
      method: 'POST',
      body: data,
    }),
  tutorChat: (data: { context: string; message: string; history: ChatMessage[]; stream?: boolean }) =>
    fetchApi<{ answer: string }>('/ai/tutor-chat', {
      method: 'POST',
      body: data,
    }),
}

// ==================== Review API ====================
export const reviewApi = {
  list: (dueOnly = false) => fetchApi<ReviewTask[]>(`/reviews${dueOnly ? '?due_only=true' : ''}`),
  create: (data: { text: string; lesson_key?: string }) =>
    fetchApi<ReviewTask>('/reviews', {
      method: 'POST',
      body: data,
    }),
  pass: (taskId: string) =>
    fetchApi<ReviewTask>(`/reviews/${taskId}/pass`, {
      method: 'POST',
    }),
}

// ==================== Note API ====================
export const notesApi = {
  list: (lessonId?: string) => fetchApi<Note[]>(`/notes${lessonId ? `?lesson_id=${lessonId}` : ''}`),
  get: (id: string) => fetchApi<Note>(`/notes/${id}`),
  create: (data: CreateNoteData) => fetchApi<Note>('/notes', {
    method: 'POST',
    body: data,
  }),
  update: (id: string, data: { title: string; content: string }) => fetchApi<Note>(`/notes/${id}`, {
    method: 'PUT',
    body: data,
  }),
  delete: (id: string) => fetchApi<void>(`/notes/${id}`, {
    method: 'DELETE',
  }),
}

// ==================== TTS API ====================
export const ttsApi = {
  synthesize: async (data: {
    title?: string
    scene?: string
    dialogue: DialogueLine[]
    rate?: string
    pitch?: string
  }): Promise<Blob> => {
    const response = await fetch(`${API_BASE}/tts/synthesize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || `HTTP ${response.status}`)
    }

    return response.blob()
  },
}
