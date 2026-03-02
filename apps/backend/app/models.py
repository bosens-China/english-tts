"""SQLAlchemy ORM 模型"""

from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Book(Base):
    """书籍模型（如：新概念英语第一册）"""

    __tablename__ = "books"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # 关联关系
    lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson",
        back_populates="book",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Lesson.sort_order",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "cover_url": self.cover_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Lesson(Base):
    """课文/章节模型（如：Lesson 1 - Excuse me!）"""

    __tablename__ = "lessons"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    book_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # 关联关系
    book: Mapped["Book"] = relationship("Book", back_populates="lessons")
    notes: Mapped[list["Note"]] = relationship(
        "Note",
        back_populates="lesson",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # 每节课只有一个音频
    audio: Mapped["Audio | None"] = relationship(
        "Audio",
        back_populates="lesson",
        cascade="all, delete-orphan",
        lazy="selectin",
        uselist=False,
    )

    def to_dict(self, include_audio: bool = True) -> dict:
        data = {
            "id": self.id,
            "book_id": self.book_id,
            "title": self.title,
            "description": self.description,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_audio and self.audio:
            data["audio"] = self.audio.to_dict(include_dialogue=True)
        else:
            data["audio"] = None
        return data


class Note(Base):
    """笔记模型 - 属于 Lesson"""

    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    lesson_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # 关联关系
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="notes")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "lesson_id": self.lesson_id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Audio(Base):
    """音频模型 - 每节课只有一个音频"""

    __tablename__ = "audios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    lesson_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # 确保一对一关系
    )
    dialogue: Mapped[list[dict]] = mapped_column(JSON, default=list)
    rate: Mapped[str] = mapped_column(String(10), default="+0%")
    pitch: Mapped[str] = mapped_column(String(10), default="+0Hz")
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    file_size: Mapped[int | None] = mapped_column(nullable=True)
    duration: Mapped[float | None] = mapped_column(nullable=True)
    cache_key: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # 关联关系
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="audio")

    def to_dict(self, include_dialogue: bool = False) -> dict:
        data = {
            "id": self.id,
            "lesson_id": self.lesson_id,
            "rate": self.rate,
            "pitch": self.pitch,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "duration": self.duration,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_dialogue:
            data["dialogue"] = self.dialogue
        return data


class ReviewTask(Base):
    """复习任务模型 - 按用户维度存储遗忘曲线任务"""

    __tablename__ = "review_tasks"
    __table_args__ = (UniqueConstraint("user_id", "lesson_key", name="uq_review_user_lesson"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    lesson_key: Mapped[str] = mapped_column(String(120), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    stage: Mapped[int] = mapped_column(nullable=False, default=0)
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "lesson_key": self.lesson_key,
            "text": self.text,
            "stage": self.stage,
            "next_review_at": self.next_review_at.isoformat() if self.next_review_at else None,
            "last_reviewed_at": self.last_reviewed_at.isoformat() if self.last_reviewed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
