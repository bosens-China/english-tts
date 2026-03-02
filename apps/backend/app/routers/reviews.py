"""复习路由：按用户存储遗忘曲线复习任务。"""

import hashlib
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import ReviewTask
from app.schemas import ReviewTaskCreateRequest, ReviewTaskResponse
from app.security import CurrentUser, get_current_user

router = APIRouter(prefix="/reviews", tags=["reviews"])

REVIEW_INTERVALS = [1, 2, 3, 5, 7, 15, 30]


def _gen_lesson_key(text: str) -> str:
    digest = hashlib.sha256(text.encode()).hexdigest()[:16]
    return f"lesson_{digest}"


def _next_review_time(stage: int) -> datetime | None:
    if stage >= len(REVIEW_INTERVALS):
        return None
    return datetime.now(UTC) + timedelta(days=REVIEW_INTERVALS[stage])


def _base_query(user_id: str) -> Select[tuple[ReviewTask]]:
    return select(ReviewTask).where(ReviewTask.user_id == user_id)


@router.get("", response_model=list[ReviewTaskResponse])
async def list_reviews(
    due_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """列出当前用户复习任务，可选只返回今日到期任务。"""
    query = _base_query(current_user.id)
    if due_only:
        now = datetime.now(UTC)
        query = query.where(ReviewTask.next_review_at.is_not(None), ReviewTask.next_review_at <= now)

    result = await db.execute(query.order_by(ReviewTask.updated_at.desc()))
    tasks = result.scalars().all()
    return [item.to_dict() for item in tasks]


@router.post("", response_model=ReviewTaskResponse)
async def create_review_task(
    payload: ReviewTaskCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """创建复习任务（若同 lesson_key 已存在则直接返回）。"""
    lesson_key = payload.lesson_key or _gen_lesson_key(payload.text)

    result = await db.execute(
        _base_query(current_user.id).where(ReviewTask.lesson_key == lesson_key)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing.to_dict()

    now = datetime.now(UTC)
    task = ReviewTask(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        lesson_key=lesson_key,
        text=payload.text,
        stage=0,
        next_review_at=_next_review_time(0),
        last_reviewed_at=now,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task.to_dict()


@router.post("/{task_id}/pass", response_model=ReviewTaskResponse)
async def pass_review_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """标记任务通过，推进到下一复习阶段。"""
    result = await db.execute(
        _base_query(current_user.id).where(ReviewTask.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="复习任务不存在")

    task.stage += 1
    task.last_reviewed_at = datetime.now(UTC)
    task.next_review_at = _next_review_time(task.stage)
    await db.commit()
    await db.refresh(task)
    return task.to_dict()
