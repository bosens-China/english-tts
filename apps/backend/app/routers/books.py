"""书籍管理路由"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import cache
from app.database import get_db
from app.models import Book
from app.schemas import BookCreate, BookResponse, BookUpdate, BookWithLessonsResponse

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=list[BookResponse])
async def list_books(db: AsyncSession = Depends(get_db)):
    """获取所有书籍列表"""
    result = await db.execute(select(Book).order_by(Book.created_at.desc()))
    books = result.scalars().all()
    return [b.to_dict() for b in books]


@router.post("", response_model=BookResponse)
async def create_book(book: BookCreate, db: AsyncSession = Depends(get_db)):
    """创建新书籍"""
    new_book = Book(
        id=str(uuid.uuid4()),
        title=book.title,
        description=book.description,
        cover_url=book.cover_url or None,
    )
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    return new_book.to_dict()


@router.get("/{book_id}", response_model=BookWithLessonsResponse)
async def get_book(book_id: str, db: AsyncSession = Depends(get_db)):
    """获取单个书籍详情（包含课文列表）"""
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")

    data = book.to_dict()
    data["lessons"] = [lesson.to_dict() for lesson in book.lessons]
    return data


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: str,
    book_update: BookUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新书籍信息"""
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")

    book.title = book_update.title
    book.description = book_update.description
    book.cover_url = book_update.cover_url or None
    await db.commit()
    await db.refresh(book)
    return book.to_dict()


@router.delete("/{book_id}")
async def delete_book(book_id: str, db: AsyncSession = Depends(get_db)):
    """删除书籍及其关联数据（级联删除由 ORM 处理）"""
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")

    # 收集该书籍下所有课文的音频 ID，用于精确清除缓存
    audio_ids_to_clear = []
    for lesson in book.lessons:
        if lesson.audio:
            audio_ids_to_clear.append(lesson.audio.id)

    await db.delete(book)
    await db.commit()

    # 精确清除相关音频的元数据缓存
    for audio_id in audio_ids_to_clear:
        await cache.invalidate_audio(audio_id)

    return {"message": "书籍已删除"}
