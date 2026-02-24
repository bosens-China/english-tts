# English TTS

基于 `edge-tts` 的英文学习平台：支持书籍管理、课文学习、Markdown 笔记和 AI 语音合成。

## 技术栈

- **后端**: FastAPI + SQLAlchemy (SQLite) + Redis 缓存
- **前端**: Vue 3 + Vite + UnoCSS + VueUse
- **TTS**: edge-tts (免费) + 多级缓存策略

## 项目结构

```
english-tts/
├── apps/
│   ├── backend/              # FastAPI 后端
│   │   ├── app/
│   │   │   ├── models.py       # SQLAlchemy ORM (Book, Lesson, Note, Audio)
│   │   │   ├── schemas.py      # Pydantic 数据验证
│   │   │   ├── database.py     # SQLite 配置
│   │   │   ├── cache.py        # Redis 缓存管理
│   │   │   ├── routers/        # API 路由
│   │   │   │   ├── books.py      # 书籍 CRUD
│   │   │   │   ├── lessons.py    # 课文 CRUD
│   │   │   │   ├── notes.py      # 笔记 CRUD
│   │   │   │   └── audios.py     # 音频管理与生成
│   │   │   └── services/
│   │   │       └── tts.py        # TTS 合成服务
│   │   ├── docker-compose.yml  # Redis 服务
│   │   └── pyproject.toml
│   └── frontend/             # Vue 3 前端
│       ├── src/
│       │   ├── views/
│       │   │   ├── BookListView.vue     # 书籍列表
│       │   │   ├── BookDetailView.vue   # 书籍详情（课文列表）
│       │   │   ├── LessonDetailView.vue # 课文详情（笔记/音频）
│       │   │   ├── NoteEditView.vue     # 笔记编辑
│       │   │   └── AudioCreateView.vue  # 音频创建
│       │   ├── api/client.ts     # API 客户端
│       │   └── types/index.ts    # TypeScript 类型
│       └── vite.config.ts
└── package.json
```

## 数据层级

```
📚 Book (书籍/教材)
  └── 📖 Lesson (课文/章节)
        ├── 📝 Note (学习笔记)
        └── 🔊 Audio (朗读音频)
```

**示例：**
- Book: 《新概念英语第一册》
- Lesson: "Lesson 1 - Excuse me!"
- Audio: 课文对话朗读（A: Excuse me! B: Yes?）
- Note: 学习要点、词汇笔记

## 快速开始

### 1. 启动数据库

```bash
# 启动 Redis (端口 7009)
pnpm dev:db
```

### 2. 启动后端

```bash
# 安装依赖（首次）
cd apps/backend && uv sync

# 启动服务
pnpm dev:backend
```

后端: http://127.0.0.1:8000
API 文档: http://localhost:8000/docs

### 3. 启动前端

```bash
# 安装依赖（首次）
pnpm install

# 启动服务
pnpm dev:frontend
```

前端: http://localhost:5173

### 4. 一键启动

```bash
pnpm dev
```

## 功能特性

### 📚 书籍管理
- 创建/编辑/删除书籍
- 支持封面图片
- 展示书籍列表（卡片式）

### 📖 课文管理
- 每个书籍下可创建多个课文
- 支持排序（sort_order）
- 课文列表带序号展示

### 📝 Markdown 笔记
- 双栏编辑器（左编辑，右预览）
- 使用 VueUse 自动保存草稿到 localStorage
- 完整的 Markdown 样式支持

### 🔊 TTS 音频
- 支持多角色对话
- 可配置语速（-50% ~ +30%）和音调（-100Hz ~ +100Hz）
- **多级缓存策略**：
  - L1: 单句缓存（Redis，7天）
  - L2: 整段对话缓存（Redis，7天）
  - L3: 文件系统缓存

## 使用流程

1. **创建书籍** → 首页点击"新建书籍"
2. **添加课文** → 进入书籍，点击"新建课文"
3. **创建内容** → 进入课文：
   - "笔记" Tab：创建 Markdown 笔记
   - "音频" Tab：创建对话音频

## API 端点

### 书籍
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/books` | 书籍列表 |
| POST | `/books` | 创建书籍 |
| GET | `/books/{id}` | 书籍详情（含课文列表） |
| PUT | `/books/{id}` | 更新书籍 |
| DELETE | `/books/{id}` | 删除书籍 |

### 课文
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/lessons?book_id={id}` | 课文列表 |
| POST | `/lessons` | 创建课文 |
| GET | `/lessons/{id}` | 课文详情 |
| PUT | `/lessons/{id}` | 更新课文 |
| DELETE | `/lessons/{id}` | 删除课文 |

### 笔记
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/notes?lesson_id={id}` | 笔记列表 |
| POST | `/notes` | 创建笔记 |
| GET | `/notes/{id}` | 笔记详情 |
| PUT | `/notes/{id}` | 更新笔记 |
| DELETE | `/notes/{id}` | 删除笔记 |

### 音频
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/audios?lesson_id={id}` | 音频列表 |
| POST | `/audios` | 创建音频配置 |
| POST | `/audios/{id}/generate` | 生成音频文件 |
| GET | `/audios/{id}/download` | 下载音频 |
| POST | `/audios/{id}/regenerate` | 重新生成音频 |

## 代码质量检查

### 后端
```bash
# 检查代码
pnpm check:backend

# 自动修复
pnpm fix:backend
```

### 前端
```bash
# 构建时自动检查类型
pnpm build:frontend
```

## 环境变量

后端 (`apps/backend/.env`):

```bash
# 数据库
DATABASE_URL=sqlite+aiosqlite:///data/app.db

# Redis（端口 7009）
REDIS_URL=redis://localhost:7009/0
REDIS_ENABLED=true

# 数据目录
DATA_DIR=data
```

## 开发提示

1. **重置数据库**：删除 `apps/backend/data/app.db`，重启后端自动重建
2. **清除 Redis**：`redis-cli -p 7009 FLUSHDB`
3. **查看 API 文档**：http://localhost:8000/docs

## 部署建议

1. **SQLite → PostgreSQL**: 修改 `DATABASE_URL`
2. **单 Redis → Redis Cluster**: 修改 `REDIS_URL`
3. **本地存储 → 对象存储**: 修改 `app/services/tts.py`
4. **添加身份认证**: 当前为本地开发配置，生产环境需添加登录

## License

MIT
