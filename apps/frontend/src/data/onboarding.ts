import type { LearningGoal, LevelCard } from "@/types/onboarding"

export interface GoalOption {
  id: LearningGoal
  title: string
  description: string
  icon: string
}

export const goalOptions: GoalOption[] = [
  {
    id: "daily",
    title: "日常沟通",
    description: "从打招呼、购物、问路开始，优先生活场景表达。",
    icon: "ph:chat-circle-text",
  },
  {
    id: "travel",
    title: "出国旅行",
    description: "机场、酒店、点餐、问路等高频旅行英语。",
    icon: "ph:airplane-tilt",
  },
  {
    id: "work",
    title: "职场表达",
    description: "会议、邮件、汇报、协作常用表达。",
    icon: "ph:briefcase",
  },
  {
    id: "exam",
    title: "考试提升",
    description: "针对听说读写训练，强化语法和答题表达。",
    icon: "ph:exam",
  },
]

export const levelCards: LevelCard[] = [
  {
    id: 0,
    title: "Level 0",
    cefr: "Pre-A1",
    label: "完全零基础",
    previewText: "Hi. I am Tom. This is my book. I like apple.",
    zhHint: "你好。我是 Tom。这是我的书。我喜欢苹果。",
  },
  {
    id: 1,
    title: "Level 1",
    cefr: "A1",
    label: "基础起步",
    previewText: "Hello, my name is Lucy. I work in a coffee shop near my home.",
    zhHint: "你好，我叫 Lucy。我在家附近的一家咖啡店工作。",
  },
  {
    id: 2,
    title: "Level 2",
    cefr: "A2",
    label: "日常交流",
    previewText: "I usually take the subway to work, but today I rode my bike because the weather is great.",
    zhHint: "我通常坐地铁上班，但今天天气很好，所以骑了自行车。",
  },
  {
    id: 3,
    title: "Level 3",
    cefr: "B1",
    label: "表达观点",
    previewText: "In my opinion, learning English every day is more effective than studying only on weekends.",
    zhHint: "我认为每天学英语比只在周末学习更有效。",
  },
  {
    id: 4,
    title: "Level 4",
    cefr: "B2",
    label: "深入沟通",
    previewText: "Although the project faced delays, the team adapted quickly and delivered a better solution.",
    zhHint: "虽然项目一度延迟，但团队迅速调整并交付了更好的方案。",
  },
  {
    id: 5,
    title: "Level 5",
    cefr: "C1",
    label: "流利进阶",
    previewText: "What ultimately drives long-term progress is not intensity, but consistent and deliberate practice.",
    zhHint: "真正驱动长期进步的不是强度，而是持续且刻意的练习。",
  },
]
