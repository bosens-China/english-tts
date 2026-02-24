"""Redis 缓存配置"""

import hashlib
import os
import pickle
from typing import Any

import redis.asyncio as redis

# Redis 配置
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:7009/0")
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "true").lower() == "true"

# 缓存键前缀
CACHE_PREFIX = "english_tts:"
CACHE_TTS_PREFIX = f"{CACHE_PREFIX}tts:"
CACHE_AUDIO_META_PREFIX = f"{CACHE_PREFIX}audio_meta:"

# 缓存过期时间（秒）
CACHE_TTL_TTS = 60 * 60 * 24 * 7  # TTS 缓存 7 天
CACHE_TTL_DEFAULT = 60 * 60 * 24  # 默认 24 小时


class CacheManager:
    """缓存管理器"""

    def __init__(self):
        self._redis: redis.Redis | None = None
        self._enabled = REDIS_ENABLED

    async def connect(self):
        """连接 Redis"""
        if not self._enabled:
            return
        try:
            self._redis = await redis.from_url(REDIS_URL, decode_responses=False)
            await self._redis.ping()  # type: ignore
            print(f"✅ Redis connected: {REDIS_URL}")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
            self._enabled = False
            self._redis = None

    async def disconnect(self):
        """断开 Redis 连接"""
        if self._redis:
            await self._redis.close()
            self._redis = None

    def _make_key(self, prefix: str, key: str) -> str:
        """生成缓存键"""
        return f"{prefix}{key}"

    def _hash_content(self, content: str) -> str:
        """生成内容哈希（用于 TTS 缓存键）"""
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    async def get(self, key: str, prefix: str = CACHE_PREFIX) -> Any | None:
        """获取缓存值"""
        if not self._enabled or not self._redis:
            return None

        full_key = self._make_key(prefix, key)
        data = await self._redis.get(full_key)
        if data:
            return pickle.loads(data)
        return None

    async def set(
        self,
        key: str,
        value: Any,
        prefix: str = CACHE_PREFIX,
        ttl: int = CACHE_TTL_DEFAULT,
    ) -> bool:
        """设置缓存值"""
        if not self._enabled or not self._redis:
            return False

        full_key = self._make_key(prefix, key)
        data = pickle.dumps(value)
        await self._redis.setex(full_key, ttl, data)
        return True

    async def delete(self, key: str, prefix: str = CACHE_PREFIX) -> bool:
        """删除缓存值"""
        if not self._enabled or not self._redis:
            return False

        full_key = self._make_key(prefix, key)
        await self._redis.delete(full_key)
        return True

    async def clear_prefix(self, prefix: str = CACHE_PREFIX) -> bool:
        """清空指定前缀的所有缓存"""
        if not self._enabled or not self._redis:
            return False

        pattern = f"{prefix}*"
        cursor = 0
        while True:
            cursor, keys = await self._redis.scan(cursor, match=pattern, count=100)
            if keys:
                await self._redis.delete(*keys)
            if cursor == 0:
                break
        return True

    # TTS 专用缓存方法
    def get_tts_cache_key(
        self,
        text: str,
        voice: str,
        rate: str,
        pitch: str,
    ) -> str:
        """生成 TTS 缓存键"""
        content = f"{text}:{voice}:{rate}:{pitch}"
        return self._hash_content(content)

    async def get_tts_audio(self, cache_key: str) -> bytes | None:
        """获取缓存的 TTS 音频"""
        return await self.get(cache_key, prefix=CACHE_TTS_PREFIX)

    async def set_tts_audio(
        self,
        cache_key: str,
        audio_data: bytes,
        ttl: int = CACHE_TTL_TTS,
    ) -> bool:
        """缓存 TTS 音频"""
        return await self.set(cache_key, audio_data, prefix=CACHE_TTS_PREFIX, ttl=ttl)

    async def get_audio_meta(self, audio_id: str) -> dict | None:
        """获取音频元数据缓存"""
        return await self.get(audio_id, prefix=CACHE_AUDIO_META_PREFIX)

    async def set_audio_meta(
        self,
        audio_id: str,
        meta: dict,
        ttl: int = CACHE_TTL_DEFAULT,
    ) -> bool:
        """设置音频元数据缓存"""
        return await self.set(audio_id, meta, prefix=CACHE_AUDIO_META_PREFIX, ttl=ttl)

    async def invalidate_audio(self, audio_id: str) -> None:
        """使音频相关缓存失效"""
        await self.delete(audio_id, prefix=CACHE_AUDIO_META_PREFIX)


# 全局缓存实例
cache = CacheManager()
