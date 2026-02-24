# English TTS Backend

基于 FastAPI + edge-tts + SQLite + Redis 的英文学习平台 API。

## 数据模型

```
Book (书籍)
  └── Lesson (课文)
        ├── Note (笔记)
        └── Audio (音频)
```

## 技术栈

- **FastAPI**: Web 框架
- **SQLAlchemy 2.0**: ORM + 异步 SQLite
- **Pydantic**: 数据验证
- **Redis**: TTS 音频缓存
- **edge-tts**: 微软 Edge 免费 TTS

## 安装

```bash
uv sync
```

## 启动 Redis

```bash
# Docker (端口 7009)
docker compose up -d

# 或本地 Redis
redis-server --port 7009
```

## 运行

```bash
# 开发模式
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用脚本
pnpm dev:backend
```

API 文档: http://localhost:8000/docs

## 环境变量

```bash
# 复制示例配置
cp .env.example .env
```

配置项：

- `DATABASE_URL`: SQLite 路径（默认: `sqlite+aiosqlite:///data/app.db`）
- `REDIS_URL`: Redis 地址（默认: `redis://localhost:7009/0`）
- `REDIS_ENABLED`: 是否启用 Redis（默认: `true`）

## API 结构

### 书籍 (Books)
- `GET /books` - 书籍列表
- `POST /books` - 创建书籍
- `GET /books/{id}` - 书籍详情（含课文列表）
- `PUT /books/{id}` - 更新书籍
- `DELETE /books/{id}` - 删除书籍

### 课文 (Lessons)
- `GET /lessons?book_id={id}` - 课文列表
- `POST /lessons` - 创建课文
- `GET /lessons/{id}` - 课文详情
- `PUT /lessons/{id}` - 更新课文
- `DELETE /lessons/{id}` - 删除课文

### 笔记 (Notes)
- `GET /notes?lesson_id={id}` - 笔记列表
- `POST /notes` - 创建笔记
- `GET /notes/{id}` - 笔记详情
- `PUT /notes/{id}` - 更新笔记
- `DELETE /notes/{id}` - 删除笔记

### 音频 (Audios)
- `GET /audios?lesson_id={id}` - 音频列表
- `POST /audios` - 创建音频配置
- `POST /audios/{id}/generate` - 生成音频文件
- `GET /audios/{id}/download` - 下载音频
- `POST /audios/{id}/regenerate` - 重新生成音频
- `DELETE /audios/{id}` - 删除音频

## TTS 缓存机制

### 多级缓存

1. **L1 - 单句缓存**: 同一句话只生成一次
   - 键: `sha256(text:voice:rate:pitch)`
   - TTL: 7 天

2. **L2 - 整段缓存**: 整段对话的哈希缓存
   - 键: `sha256(dialogue:full:rate:pitch)`
   - TTL: 7 天

3. **L3 - 元数据缓存**: 音频信息缓存
   - 键: `english_tts:audio_meta:{audio_id}`
   - TTL: 24 小时

## 代码检查

```bash
# Ruff 检查
uv run ruff check app

# Ruff 自动修复
uv run ruff check --fix app

# 格式化
uv run ruff format app

# 类型检查
uv run pyright
```

## 数据验证

使用 Pydantic Field 进行严格验证：

```python
class AudioCreate(BaseModel):
    lesson_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=255)
    rate: str = Field(default="+0%")
    
    @field_validator("rate")
    def validate_rate(cls, v: str) -> str:
        if not re.match(r"^[+-]\d+%$", v):
            raise ValueError("语速格式错误")
        return v
```
