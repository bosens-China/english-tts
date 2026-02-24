"""课文管理路由"""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import cache
from app.database import get_db
from app.models import Audio, Book, Lesson
from app.schemas import AudioUpdate, LessonCreate, LessonResponse, LessonUpdate
from app.services.tts import synthesize_dialogue_with_cache

router = APIRouter(prefix="/lessons", tags=["lessons"])

AUDIO_DIR = Path("data/audio_files")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


@router.get("", response_model=list[LessonResponse])
async def list_lessons(book_id: str | None = None, db: AsyncSession = Depends(get_db)):
    """获取课文列表，可按书籍筛选"""
    query = select(Lesson).order_by(Lesson.sort_order, Lesson.created_at)
    if book_id:
        query = query.where(Lesson.book_id == book_id)

    result = await db.execute(query)
    lessons = result.scalars().all()
    return [lesson.to_dict() for lesson in lessons]


@router.post("", response_model=LessonResponse)
async def create_lesson(lesson: LessonCreate, db: AsyncSession = Depends(get_db)):
    """创建新课文，可同时创建音频"""
    # 验证书籍存在
    result = await db.execute(select(Book).where(Book.id == lesson.book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")

    new_lesson = Lesson(
        id=str(uuid.uuid4()),
        book_id=lesson.book_id,
        title=lesson.title,
        description=lesson.description,
        sort_order=lesson.sort_order,
    )
    db.add(new_lesson)
    await db.commit()
    await db.refresh(new_lesson)

    # 如果提供了音频配置，创建音频
    if lesson.audio and lesson.audio.dialogue:
        await _create_or_update_audio(db, new_lesson.id, lesson.audio)
        await db.refresh(new_lesson)

    return new_lesson.to_dict()


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(lesson_id: str, db: AsyncSession = Depends(get_db)):
    """获取单个课文详情（包含音频）"""
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="课文不存在")
    return lesson.to_dict()


@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: str,
    lesson_update: LessonUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新课文信息"""
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="课文不存在")

    lesson.title = lesson_update.title
    lesson.description = lesson_update.description
    lesson.sort_order = lesson_update.sort_order
    await db.commit()
    await db.refresh(lesson)
    return lesson.to_dict()


@router.delete("/{lesson_id}")
async def delete_lesson(lesson_id: str, db: AsyncSession = Depends(get_db)):
    """删除课文及其关联数据（级联删除由 ORM 处理）"""
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="课文不存在")

    # 清除音频缓存
    if lesson.audio:
        await cache.invalidate_audio(lesson.audio.id)

    await db.delete(lesson)
    await db.commit()

    return {"message": "课文已删除"}


# ==================== 音频相关接口 ====================

@router.post("/{lesson_id}/audio/generate")
async def generate_lesson_audio(lesson_id: str, db: AsyncSession = Depends(get_db)):
    """生成课文音频（如果音频不存在则创建）"""
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="课文不存在")

    if not lesson.audio:
        raise HTTPException(status_code=400, detail="课文没有配置音频")

    try:
        # 重新生成音频文件
        audio_file_path, cache_key = await synthesize_dialogue_with_cache(
            lesson.audio.dialogue,
            lesson.audio.rate,
            lesson.audio.pitch,
        )

        # 复制到目标位置
        target_path = AUDIO_DIR / f"{lesson.audio.id}.mp3"
        import shutil

        shutil.copy(str(audio_file_path), str(target_path))

        # 更新音频记录
        lesson.audio.file_path = str(target_path)
        lesson.audio.file_size = target_path.stat().st_size
        lesson.audio.cache_key = cache_key
        await db.commit()

        # 更新缓存
        await cache.set_audio_meta(
            lesson.audio.id,
            {
                "id": lesson.audio.id,
                "rate": lesson.audio.rate,
                "pitch": lesson.audio.pitch,
                "dialogue": lesson.audio.dialogue,
            },
        )

        return {"message": "音频生成成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"音频生成失败: {str(e)}")


@router.put("/{lesson_id}/audio")
async def update_lesson_audio(
    lesson_id: str,
    audio_update: AudioUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新课文音频配置并重新生成"""
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="课文不存在")

    # 更新音频配置
    if lesson.audio:
        if audio_update.dialogue is not None:
            lesson.audio.dialogue = audio_update.dialogue
        if audio_update.rate is not None:
            lesson.audio.rate = audio_update.rate
        if audio_update.pitch is not None:
            lesson.audio.pitch = audio_update.pitch

        # 清除旧文件
        if lesson.audio.file_path:
            import os

            try:
                os.remove(lesson.audio.file_path)
            except:
                pass

        lesson.audio.file_path = None
        lesson.audio.file_size = None

        await db.commit()
        await db.refresh(lesson)

        return lesson.to_dict()
    else:
        raise HTTPException(status_code=404, detail="课文没有音频")


@router.get("/{lesson_id}/audio/download")
async def download_lesson_audio(lesson_id: str, db: AsyncSession = Depends(get_db)):
    """下载课文音频"""
    from fastapi.responses import FileResponse

    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="课文不存在")

    if not lesson.audio or not lesson.audio.file_path:
        raise HTTPException(status_code=404, detail="音频文件不存在")

    file_path = Path(lesson.audio.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="音频文件不存在")

    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=f"{lesson.title}.mp3",
    )


# ==================== 辅助函数 ====================

async def _create_or_update_audio(db: AsyncSession, lesson_id: str, audio_config):
    """创建或更新音频"""
    # 创建音频记录
    new_audio = Audio(
        id=str(uuid.uuid4()),
        lesson_id=lesson_id,
        dialogue=audio_config.dialogue,
        rate=audio_config.rate,
        pitch=audio_config.pitch,
    )
    db.add(new_audio)
    await db.commit()
    await db.refresh(new_audio)

    # 异步生成音频文件
    try:
        audio_file_path, cache_key = await synthesize_dialogue_with_cache(
            audio_config.dialogue,
            audio_config.rate,
            audio_config.pitch,
        )

        # 复制到目标位置
        target_path = AUDIO_DIR / f"{new_audio.id}.mp3"
        import shutil

        shutil.copy(str(audio_file_path), str(target_path))

        # 更新音频记录
        new_audio.file_path = str(target_path)
        new_audio.file_size = target_path.stat().st_size
        new_audio.cache_key = cache_key
        await db.commit()
    except Exception:
        # 音频生成失败不影响课文创建
        pass
