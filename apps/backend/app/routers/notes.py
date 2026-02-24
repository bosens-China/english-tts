"""笔记管理路由"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Lesson, Note
from app.schemas import NoteCreate, NoteResponse, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=list[NoteResponse])
async def list_notes(lesson_id: str | None = None, db: AsyncSession = Depends(get_db)):
    """获取笔记列表，可按课文筛选"""
    query = select(Note).order_by(Note.updated_at.desc())
    if lesson_id:
        query = query.where(Note.lesson_id == lesson_id)

    result = await db.execute(query)
    notes = result.scalars().all()
    return [n.to_dict() for n in notes]


@router.post("", response_model=NoteResponse)
async def create_note(note: NoteCreate, db: AsyncSession = Depends(get_db)):
    """创建新笔记"""
    # 验证课文存在
    result = await db.execute(select(Lesson).where(Lesson.id == note.lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="课文不存在")

    new_note = Note(
        id=str(uuid.uuid4()),
        lesson_id=note.lesson_id,
        title=note.title,
        content=note.content,
    )
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return new_note.to_dict()


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str, db: AsyncSession = Depends(get_db)):
    """获取单个笔记详情"""
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return note.to_dict()


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    note_update: NoteUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新笔记"""
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")

    note.title = note_update.title
    note.content = note_update.content
    await db.commit()
    await db.refresh(note)
    return note.to_dict()


@router.delete("/{note_id}")
async def delete_note(note_id: str, db: AsyncSession = Depends(get_db)):
    """删除笔记"""
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")

    await db.delete(note)
    await db.commit()
    return {"message": "笔记已删除"}
