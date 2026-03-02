"""Pydantic 数据验证模型"""

import re

from pydantic import BaseModel, Field, field_validator


# ==================== Auth ====================
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100, description="测试账号用户名")
    password: str = Field(..., min_length=1, max_length=100, description="测试账号密码")


class UserProfile(BaseModel):
    id: str
    username: str
    display_name: str
    membership: str
    level: int


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


# ==================== Book ====================
class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="书名")
    description: str = Field(default="", max_length=1000, description="书籍描述")
    cover_url: str = Field(default="", max_length=512, description="封面图片URL")


class BookUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="书名")
    description: str = Field(default="", max_length=1000, description="书籍描述")
    cover_url: str = Field(default="", max_length=512, description="封面图片URL")


class BookResponse(BaseModel):
    id: str
    title: str
    description: str
    cover_url: str | None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class BookWithLessonsResponse(BookResponse):
    lessons: list[dict] = []


# ==================== Audio (作为课文的子资源) ====================
class DialogueLine(BaseModel):
    speaker: str = Field(..., min_length=1, max_length=100, description="说话人")
    voice: str = Field(
        ..., min_length=1, max_length=100, description="语音类型，如 en-US-AriaNeural"
    )
    text: str = Field(..., min_length=1, max_length=5000, description="文本内容")
    pause_ms: int = Field(default=500, ge=0, le=10000, description="停顿毫秒数")


class AudioConfig(BaseModel):
    """音频配置 - 创建/更新课文时使用"""
    dialogue: list[DialogueLine] = Field(..., min_length=1, max_length=100, description="对话列表")
    rate: str = Field(default="+0%", description="语速，格式如 +10% 或 -20%")
    pitch: str = Field(default="+0Hz", description="音调，格式如 +20Hz 或 -50Hz")

    @field_validator("rate")
    @classmethod
    def validate_rate(cls, v: str) -> str:
        if not re.match(r"^[+-]\d+%$", v):
            raise ValueError("语速格式错误，必须使用 +0% 或 -10% 格式")
        return v

    @field_validator("pitch")
    @classmethod
    def validate_pitch(cls, v: str) -> str:
        if not re.match(r"^[+-]\d+Hz$", v):
            raise ValueError("音调格式错误，必须使用 +0Hz 或 -50Hz 格式")
        return v


class AudioResponse(BaseModel):
    """音频响应"""
    id: str
    rate: str
    pitch: str
    file_size: int | None
    duration: float | None
    dialogue: list[dict] = []
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class AudioUpdate(BaseModel):
    """更新音频参数"""
    dialogue: list[DialogueLine] | None = Field(default=None, description="对话列表")
    rate: str | None = Field(default=None, description="语速")
    pitch: str | None = Field(default=None, description="音调")

    @field_validator("rate")
    @classmethod
    def validate_rate(cls, v: str | None) -> str | None:
        if v is not None and not re.match(r"^[+-]\d+%$", v):
            raise ValueError("语速格式错误")
        return v

    @field_validator("pitch")
    @classmethod
    def validate_pitch(cls, v: str | None) -> str | None:
        if v is not None and not re.match(r"^[+-]\d+Hz$", v):
            raise ValueError("音调格式错误")
        return v


# ==================== Lesson ====================
class LessonCreate(BaseModel):
    book_id: str = Field(..., min_length=1, description="所属书籍ID")
    title: str = Field(..., min_length=1, max_length=255, description="课文标题")
    description: str = Field(default="", max_length=1000, description="课文描述")
    sort_order: int = Field(default=0, ge=0, description="排序顺序")
    audio: AudioConfig | None = Field(default=None, description="音频配置（可选）")


class LessonUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="课文标题")
    description: str = Field(default="", max_length=1000, description="课文描述")
    sort_order: int = Field(default=0, ge=0, description="排序顺序")


class LessonResponse(BaseModel):
    id: str
    book_id: str
    title: str
    description: str
    sort_order: int
    audio: AudioResponse | None = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# ==================== Note ====================
class NoteCreate(BaseModel):
    lesson_id: str = Field(..., min_length=1, description="所属课文ID")
    title: str = Field(..., min_length=1, max_length=255, description="笔记标题")
    content: str = Field(default="", max_length=100000, description="笔记内容（Markdown）")


class NoteUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="笔记标题")
    content: str = Field(..., max_length=100000, description="笔记内容（Markdown）")


class NoteResponse(BaseModel):
    id: str
    lesson_id: str
    title: str
    content: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# ==================== AI / LLM ====================
class GenerateLessonRequest(BaseModel):
    level: int = Field(..., ge=0, le=5, description="用户当前等级，0 为零基础")
    goal: str = Field(default="daily", min_length=1, max_length=30, description="学习目标")


class GenerateLessonResponse(BaseModel):
    text: str
    audio_script: list[DialogueLine]
    new_words: list[str]
    grammar: list[str]
    culture_notes: list[str]
    questions: list[str]


class EvaluateQARequest(BaseModel):
    lesson_text: str = Field(..., min_length=1, max_length=10000)
    question: str = Field(..., min_length=1, max_length=1000)
    user_answer: str = Field(..., min_length=1, max_length=5000)


class EvaluateQAResponse(BaseModel):
    score: int = Field(..., ge=0, le=100)
    passed: bool
    feedback: str


class PronunciationAssessmentRequest(BaseModel):
    reference_text: str = Field(..., min_length=1, max_length=10000)
    spoken_text: str = Field(..., min_length=1, max_length=10000)


class PronunciationAssessmentResponse(BaseModel):
    score: int = Field(..., ge=0, le=100)
    passed: bool
    accuracy: float = Field(..., ge=0, le=1)
    feedback: str


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str = Field(..., min_length=1, max_length=5000)


class AITutorChatRequest(BaseModel):
    context: str = Field(default="", max_length=10000)
    message: str = Field(..., min_length=1, max_length=5000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)
    stream: bool = Field(default=False, description="是否流式返回")


class AITutorChatResponse(BaseModel):
    answer: str


class ReviewTaskCreateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    lesson_key: str | None = Field(default=None, min_length=1, max_length=120)


class ReviewTaskResponse(BaseModel):
    id: str
    user_id: str
    lesson_key: str
    text: str
    stage: int
    next_review_at: str | None
    last_reviewed_at: str | None
    created_at: str
    updated_at: str


# 旧的 Audio schemas 已删除，现在 Audio 作为 Lesson 的子资源
