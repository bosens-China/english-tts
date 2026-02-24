"""FastAPI 主应用"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.cache import cache
from app.database import init_db
from app.routers import books, lessons, notes, tts


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    print("🚀 Starting up...")

    # 初始化数据库
    await init_db()
    print("✅ Database initialized")

    # 连接 Redis
    await cache.connect()

    yield

    # 关闭时清理
    print("🛑 Shutting down...")
    await cache.disconnect()


app = FastAPI(
    title="English TTS API",
    description="基于 edge-tts 的英文学习平台 API - Book → Lesson → Note/Audio",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(books.router)
app.include_router(lessons.router)
app.include_router(notes.router)
app.include_router(tts.router)


@app.get("/")
async def root():
    return {
        "message": "English TTS API",
        "version": "3.0.0",
        "docs": "/docs",
        "structure": "Book → Lesson → Note/Audio",
        "endpoints": {
            "books": "/books",
            "lessons": "/lessons",
            "notes": "/notes",
            "tts": "/tts",
        },
    }


async def _check_redis() -> str:
    """检查 Redis 连接状态"""
    if not cache._enabled or not cache._redis:
        return "disabled"
    try:
        result = await cache._redis.ping()  # type: ignore[misc]
        return "connected" if result else "disconnected"
    except Exception:
        return "disconnected"


async def _check_database() -> str:
    """检查数据库连接状态"""
    from app.database import engine
    try:
        async with engine.connect() as conn:
            result = await conn.execute(select(1))  # type: ignore[func-returns-value]
            return "connected" if result.scalar() == 1 else "disconnected"
    except Exception:
        return "disconnected"


@app.get("/health")
async def health_check():
    """健康检查端点"""
    redis_status = await _check_redis()
    db_status = await _check_database()

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "redis": redis_status,
    }
