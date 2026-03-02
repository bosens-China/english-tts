"""AI 路由：课文生成、问答评估、助教聊天。"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas import (
    AITutorChatRequest,
    AITutorChatResponse,
    EvaluateQARequest,
    EvaluateQAResponse,
    GenerateLessonRequest,
    GenerateLessonResponse,
    PronunciationAssessmentRequest,
    PronunciationAssessmentResponse,
)
from app.security import CurrentUser, get_current_user
from app.services.llm import llm_service

router = APIRouter(prefix="/ai", tags=["ai"])


def _llm_unavailable_error(exc: Exception) -> HTTPException:
    return HTTPException(
        status_code=503,
        detail=f"LLM 服务不可用，请检查 LLM_BASE_URL / LLM_API_KEY 配置。{exc}",
    )


@router.post("/generate-lesson", response_model=GenerateLessonResponse)
async def generate_lesson(
    payload: GenerateLessonRequest,
    _: CurrentUser = Depends(get_current_user),
):
    """生成课文：支持 level=0 零基础和 level>=1 的 N+1 逻辑。"""
    try:
        data = await llm_service.generate_lesson(level=payload.level, goal=payload.goal)
        return GenerateLessonResponse(**data)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise _llm_unavailable_error(exc) from exc


@router.post("/evaluate-qa", response_model=EvaluateQAResponse)
async def evaluate_qa(
    payload: EvaluateQARequest,
    _: CurrentUser = Depends(get_current_user),
):
    """评估课后问答。"""
    try:
        data = await llm_service.evaluate_qa(
            lesson_text=payload.lesson_text,
            question=payload.question,
            user_answer=payload.user_answer,
        )
        return EvaluateQAResponse(**data)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise _llm_unavailable_error(exc) from exc


@router.post("/evaluate-pronunciation", response_model=PronunciationAssessmentResponse)
async def evaluate_pronunciation(
    payload: PronunciationAssessmentRequest,
    _: CurrentUser = Depends(get_current_user),
):
    """发音评估（当前为本地评分实现，后续可切换 Azure Pronunciation API）。"""
    try:
        data = await llm_service.evaluate_pronunciation(
            reference_text=payload.reference_text,
            spoken_text=payload.spoken_text,
        )
        return PronunciationAssessmentResponse(**data)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise _llm_unavailable_error(exc) from exc


@router.post("/tutor-chat", response_model=AITutorChatResponse)
async def tutor_chat(
    payload: AITutorChatRequest,
    _: CurrentUser = Depends(get_current_user),
):
    """AI 助教问答；支持 stream=true 的流式文本输出。"""
    try:
        history = [item.model_dump() for item in payload.history]
        if payload.stream:
            stream = llm_service.tutor_chat_stream(payload.context, history, payload.message)
            return StreamingResponse(stream, media_type="text/plain; charset=utf-8")

        answer = await llm_service.tutor_chat(payload.context, history, payload.message)
        return AITutorChatResponse(answer=answer)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise _llm_unavailable_error(exc) from exc
