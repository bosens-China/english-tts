"""TTS 服务，带缓存支持"""

import asyncio
import io
import random
import re
from pathlib import Path

import edge_tts
from pydub import AudioSegment

from app.cache import cache

# 默认值
DEFAULT_RATE = "+0%"
DEFAULT_PITCH = "+0Hz"

# 重试配置
MAX_RETRIES = 3
BASE_DELAY = 1.0  # 基础延迟（秒）
MAX_DELAY = 10.0  # 最大延迟（秒）


async def _synthesize_with_retry(
    text: str,
    voice: str,
    rate: str = DEFAULT_RATE,
    pitch: str = DEFAULT_PITCH,
) -> bytes:
    """合成单句，带重试机制"""
    last_exception = None

    for attempt in range(MAX_RETRIES):
        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
                pitch=pitch,
            )

            # 使用内存临时存储，确保资源正确关闭
            with io.BytesIO() as audio_buffer:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_buffer.write(chunk["data"])
                return audio_buffer.getvalue()

        except Exception as e:
            last_exception = e
            if attempt < MAX_RETRIES - 1:
                # 指数退避 + 随机抖动
                delay = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
                delay += random.uniform(0, 1)  # 添加随机抖动避免惊群
                await asyncio.sleep(delay)
            else:
                break

    raise last_exception or RuntimeError("TTS synthesis failed after retries")


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除不合法的字符"""
    clean = re.sub(r'[\\/*?:"<>|]', "_", filename)
    clean = clean.strip()
    # 如果清理后为空，使用默认名
    if not clean:
        clean = "audio"
    return clean


async def synthesize_single_line(
    text: str,
    voice: str,
    rate: str = DEFAULT_RATE,
    pitch: str = DEFAULT_PITCH,
) -> bytes:
    """合成单句，带缓存和重试"""
    # 生成缓存键
    cache_key = cache.get_tts_cache_key(text, voice, rate, pitch)

    # 尝试从缓存获取
    cached_audio = await cache.get_tts_audio(cache_key)
    if cached_audio:
        return cached_audio

    # 缓存未命中，生成音频（带重试）
    audio_data = await _synthesize_with_retry(text, voice, rate, pitch)

    # 存入缓存
    await cache.set_tts_audio(cache_key, audio_data)

    return audio_data


def ms_silence(ms: int) -> AudioSegment:
    """生成指定毫秒数静音"""
    return AudioSegment.silent(duration=ms)


async def synthesize_dialogue(
    json_data: dict,
    output_dir: Path,
    rate: str = DEFAULT_RATE,
    pitch: str = DEFAULT_PITCH,
) -> Path | None:
    """
    根据对话数据生成完整 MP3。
    每一句都会使用缓存避免重复生成。
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    dialogue = json_data.get("dialogue", [])
    if not dialogue:
        return None

    title = json_data.get("title", "").strip()
    safe_title = sanitize_filename(title) if title else "final"
    output_file = output_dir / f"{safe_title}.mp3"

    # 收集需要合成的句子
    lines_to_synthesize = []
    for idx, line in enumerate(dialogue, start=1):
        speaker = line.get("speaker", f"Speaker{idx}")
        voice = line.get("voice", "en-US-AriaNeural")
        text = line.get("text", "")
        pause_ms = line.get("pause_ms", 500)

        if not text.strip():
            continue

        lines_to_synthesize.append(
            {
                "idx": idx,
                "speaker": speaker,
                "voice": voice,
                "text": text,
                "pause_ms": pause_ms,
            }
        )

    if not lines_to_synthesize:
        return None

    # 并行合成所有句子（利用缓存）
    async def synthesize_line_task(line_info: dict) -> tuple[int, bytes, int]:
        """合成单句任务，返回 (索引, 音频数据, 停顿时间)"""
        audio_data = await synthesize_single_line(
            line_info["text"],
            line_info["voice"],
            rate,
            pitch,
        )
        return line_info["idx"], audio_data, line_info["pause_ms"]

    results = await asyncio.gather(*[synthesize_line_task(line) for line in lines_to_synthesize])

    # 按原始顺序合并音频
    sorted_results = sorted(results, key=lambda x: x[0])
    segments: list[AudioSegment] = []
    for i, (_idx, audio_data, pause_ms) in enumerate(sorted_results):
        # 从 bytes 加载音频
        segment = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
        segments.append(segment)
        # 最后一句后面不需要加静音
        if i < len(sorted_results) - 1:
            segments.append(ms_silence(pause_ms))

    if not segments:
        return None

    # 合并并导出
    final_audio: AudioSegment = segments[0]
    for segment in segments[1:]:
        final_audio += segment
    final_audio.export(output_file, format="mp3")

    return output_file


import json as json_module  # 避免与参数名冲突


async def synthesize_dialogue_with_cache(
    audio_id: str,
    json_data: dict,
    output_dir: Path,
    rate: str = DEFAULT_RATE,
    pitch: str = DEFAULT_PITCH,
) -> tuple[Path | None, str]:
    """
    带完整音频缓存的对话合成。
    如果整段对话已缓存，直接返回缓存文件。
    返回: (文件路径, 缓存键)
    """
    # 生成整段对话的缓存键（使用稳定排序的 JSON）
    dialogue = json_data.get("dialogue", [])
    dialogue_str = json_module.dumps(dialogue, sort_keys=True, separators=(',', ':'))
    full_cache_key = cache.get_tts_cache_key(dialogue_str, "full", rate, pitch)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{audio_id}_{full_cache_key[:8]}.mp3"

    # 检查缓存
    cached_data = await cache.get_tts_audio(full_cache_key)
    if cached_data:
        # 缓存命中，写入文件
        output_file.write_bytes(cached_data)
        return output_file, full_cache_key

    # 缓存未命中，合成
    result = await synthesize_dialogue(json_data, output_dir, rate, pitch)

    if result and result.exists():
        # 存入缓存
        audio_data = result.read_bytes()
        await cache.set_tts_audio(full_cache_key, audio_data)
        return result, full_cache_key

    return None, full_cache_key
