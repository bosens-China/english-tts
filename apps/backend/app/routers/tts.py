"""TTS 路由 - 直接合成音频"""

import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.services.tts import synthesize_dialogue

router = APIRouter(prefix="/tts", tags=["tts"])


class DialogueLine(BaseModel):
    speaker: str
    voice: str
    text: str
    pause_ms: int = 500


class SynthesizeRequest(BaseModel):
    title: str = ""
    scene: str = ""
    dialogue: list[DialogueLine]
    # 可选配置参数
    rate: str = Field(default="+0%", pattern=r"^[+-]\d+%$")
    pitch: str = Field(default="+0Hz", pattern=r"^[+-]\d+Hz$")


@router.post("/synthesize")
async def synthesize(request: SynthesizeRequest):
    """
    接收对话 JSON，生成 MP3 并返回文件。
    格式: { "title": "...", "scene": "...", "dialogue": [ {"speaker", "voice", "text", "pause_ms"} ], "rate": "+0%", "pitch": "+0Hz" }
    """
    if not request.dialogue:
        raise HTTPException(status_code=400, detail="dialogue 为空")

    with tempfile.TemporaryDirectory(prefix="tts_") as tmpdir:
        out_path = await synthesize_dialogue(
            request.model_dump(),
            output_dir=Path(tmpdir),
            rate=request.rate,
            pitch=request.pitch,
        )
        if out_path is None or not out_path.exists():
            raise HTTPException(status_code=500, detail="合成失败，未生成有效音频")

        content = out_path.read_bytes()
        return Response(
            content=content,
            media_type="audio/mpeg",
            headers={"Content-Disposition": f'attachment; filename="{out_path.name}"'},
        )
