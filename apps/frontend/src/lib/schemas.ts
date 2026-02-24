import { z } from 'zod'

// 基础 ID 校验
const idSchema = z.string().min(1, 'ID 不能为空')

// Book Schemas
export const bookSchema = z.object({
  id: idSchema,
  title: z.string().min(1).max(255),
  description: z.string(),
  cover_url: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
})

export const createBookSchema = z.object({
  title: z.string().min(1, '请输入书名').max(255),
  description: z.string().default(''),
  cover_url: z.string().default(''),
})

// Dialogue Line
export const dialogueLineSchema = z.object({
  speaker: z.string().min(1),
  voice: z.string().min(1),
  text: z.string().min(1),
  pause_ms: z.number().default(500),
})

// Audio Schema (作为课文的子资源)
export const audioSchema = z.object({
  id: idSchema,
  rate: z.string().default('+0%'),
  pitch: z.string().default('+0Hz'),
  file_size: z.number().nullable(),
  duration: z.number().nullable(),
  dialogue: z.array(dialogueLineSchema),
  created_at: z.string(),
  updated_at: z.string(),
})

// Audio Config (创建/更新时使用)
export const audioConfigSchema = z.object({
  dialogue: z.array(dialogueLineSchema).min(1, '至少需要一行对话'),
  rate: z.string().regex(/^[+-]\d+%$/).default('+0%'),
  pitch: z.string().regex(/^[+-]\d+Hz$/).default('+0Hz'),
})

// Lesson Schemas
export const lessonSchema = z.object({
  id: idSchema,
  book_id: idSchema,
  title: z.string().min(1).max(255),
  description: z.string(),
  sort_order: z.number().default(0),
  audio: audioSchema.nullable(),
  created_at: z.string(),
  updated_at: z.string(),
})

export const createLessonSchema = z.object({
  book_id: idSchema,
  title: z.string().min(1, '请输入课文标题'),
  description: z.string().default(''),
  sort_order: z.number().default(0),
  audio: audioConfigSchema.optional(),
})

export const updateLessonSchema = z.object({
  title: z.string().min(1, '请输入课文标题'),
  description: z.string().default(''),
  sort_order: z.number().default(0),
})

// Note Schemas
export const noteSchema = z.object({
  id: idSchema,
  lesson_id: idSchema,
  title: z.string().min(1),
  content: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
})

export const createNoteSchema = z.object({
  lesson_id: idSchema,
  title: z.string().min(1, '请输入笔记标题'),
  content: z.string().default(''),
})

// Audio Update Schema
export const updateAudioSchema = z.object({
  dialogue: z.array(dialogueLineSchema).optional(),
  rate: z.string().regex(/^[+-]\d+%$/).optional(),
  pitch: z.string().regex(/^[+-]\d+Hz$/).optional(),
})

// TTS Schemas
export const synthesizeRequestSchema = z.object({
  title: z.string().default(''),
  scene: z.string().default(''),
  dialogue: z.array(dialogueLineSchema).min(1),
  rate: z.string().regex(/^[+-]\d+%$/).default('+0%'),
  pitch: z.string().regex(/^[+-]\d+Hz$/).default('+0Hz'),
})

// 类型导出
export type Book = z.infer<typeof bookSchema>
export type CreateBookData = z.infer<typeof createBookSchema>
export type Lesson = z.infer<typeof lessonSchema>
export type CreateLessonData = z.infer<typeof createLessonSchema>
export type UpdateLessonData = z.infer<typeof updateLessonSchema>
export type Note = z.infer<typeof noteSchema>
export type CreateNoteData = z.infer<typeof createNoteSchema>
export type DialogueLine = z.infer<typeof dialogueLineSchema>
export type Audio = z.infer<typeof audioSchema>
export type AudioConfig = z.infer<typeof audioConfigSchema>
export type UpdateAudioData = z.infer<typeof updateAudioSchema>
export type SynthesizeRequest = z.infer<typeof synthesizeRequestSchema>

// BookWithLessons 类型
export interface BookWithLessons extends Book {
  lessons: Lesson[]
}
