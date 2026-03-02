export type LearningGoal = "daily" | "travel" | "work" | "exam"

export interface LevelCard {
  id: number
  title: string
  cefr: string
  label: string
  previewText: string
  zhHint: string
}
