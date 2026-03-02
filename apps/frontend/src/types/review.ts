export interface ReviewTask {
  id: string
  user_id: string
  lesson_key: string
  text: string
  stage: number
  next_review_at: string | null
  last_reviewed_at: string | null
  created_at: string
  updated_at: string
}
