# English TTS - AI Agent Guide

## Project Overview

English TTS 是一个基于 `edge-tts` 的英文学习平台，提供课程管理、Markdown 笔记编辑和多角色对话音频合成功能。

项目采用 Monorepo 结构，包含 FastAPI 后端和 Vue 3 前端。

## Technology Stack

### 后端 (apps/backend/)
- **框架**: FastAPI (异步 Python Web 框架)
- **ORM**: SQLAlchemy 2.0 + aiosqlite (异步 SQLite)
- **缓存**: Redis (用于 TTS 音频缓存和元数据缓存)
- **TTS 引擎**: edge-tts (Microsoft Edge 在线 TTS，免费)
- **音频处理**: pydub (合并音频片段)
- **类型检查**: Pyright
- **代码风格**: Ruff (linter + formatter)

### 前端 (apps/frontend/)
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **CSS 框架**: UnoCSS (原子化 CSS)
- **图标**: Iconify (Phosphor Icons)
- **路由**: Vue Router 4
- **工具库**: VueUse
- **Markdown 渲染**: marked

### 包管理
- **Python**: uv (现代 Python 包管理器)
- **Node.js**: pnpm + workspace

## Project Structure

```
english-tts/
├── apps/
│   ├── backend/              # FastAPI 后端
│   │   ├── app/
│   │   │   ├── main.py       # FastAPI 应用入口
│   │   │   ├── models.py     # SQLAlchemy ORM 模型 (Course, Note, Audio)
│   │   │   ├── schemas.py    # Pydantic 数据验证模型
│   │   │   ├── database.py   # 异步 SQLite 配置
│   │   │   ├── cache.py      # Redis 缓存管理器
│   │   │   ├── routers/      # API 路由
│   │   │   │   ├── courses.py    # 课程 CRUD
│   │   │   │   ├── notes.py      # 笔记 CRUD
│   │   │   │   └── audios.py     # 音频管理与生成
│   │   │   └── services/
│   │   │       └── tts.py        # TTS 合成服务 (带缓存)
│   │   ├── data/             # SQLite 数据库和音频文件
│   │   ├── pyproject.toml    # Python 依赖和工具配置
│   │   └── docker-compose.yml # Redis 服务定义
│   └── frontend/             # Vue 3 前端
│       ├── src/
│       │   ├── api/
│       │   │   └── client.ts     # API 客户端封装
│       │   ├── router/
│       │   │   └── index.ts      # 路由配置
│       │   ├── views/            # 页面组件
│       │   ├── types/
│       │   │   └── index.ts      # TypeScript 类型定义
│       │   └── utils/
│       │       └── markdown.ts   # Markdown 渲染
│       ├── vite.config.ts      # Vite 配置 (含代理)
│       └── uno.config.ts       # UnoCSS 配置
├── package.json            # 根目录 pnpm 脚本
├── pnpm-workspace.yaml     # pnpm workspace 配置
└── pyproject.toml          # uv workspace 配置
```

## Development Commands

### 快速启动（推荐）
```bash
# 一键启动：数据库 + 后端 + 前端
pnpm dev
```

### 单独启动服务

#### 1. 启动数据库 (Redis)
```bash
pnpm dev:db        # 使用 Docker 启动 Redis
pnpm stop:db       # 停止 Redis
```

Redis 配置：
- 端口映射: 7009 (主机) → 6379 (容器)
- 数据持久化: 启用 AOF

#### 2. 启动后端
```bash
# 首次安装依赖
cd apps/backend && uv sync

# 启动开发服务器（热重载）
pnpm dev:backend
```
后端服务:
- URL: http://127.0.0.1:8000
- API 文档: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

#### 3. 启动前端
```bash
# 首次安装依赖
pnpm install

# 启动开发服务器
pnpm dev:frontend
```
前端服务:
- URL: http://localhost:5173
- API 代理: `/api/*` → `http://127.0.0.1:8000/*`

### 代码质量检查

#### 后端 (Python)
```bash
# 代码检查 (Ruff linter + Pyright 类型检查)
pnpm check:backend

# 自动修复代码问题
pnpm fix:backend      # lint + format
pnpm lint:backend:fix # 仅自动修复 lint 问题
pnpm format:backend   # 仅格式化
```

Ruff 配置位于 `apps/backend/pyproject.toml`:
- Target Python: 3.11+
- Line length: 100
- 启用规则: E, F, I, N, W, UP, B, C4, SIM, ASYNC

Pyright 配置位于 `apps/backend/pyrightconfig.json`:
- Python version: 3.11
- Type checking mode: basic

#### 前端
前端使用 Vite 内置的 TypeScript 检查 (`vue-tsc`)，在 build 时执行。

## Architecture Details

### 数据模型

项目使用 3 个核心模型：

1. **Course (课程)**
   - id, title, description
   - 关联: notes (一对多), audios (一对多)
   - 级联删除启用

2. **Note (笔记)**
   - id, course_id, title, content (Markdown)
   - 支持双栏编辑器 (左编辑，右预览)

3. **Audio (音频)**
   - id, course_id, title, dialogue (JSON)
   - rate (语速), pitch (音调)
   - file_path, file_size, duration, cache_key

### TTS 缓存策略

多级缓存设计（L1 + L2 + L3）：

1. **L1: 单句缓存** (Redis)
   - 键: `sha256(text:voice:rate:pitch)`
   - 缓存每个独立句子的音频数据
   - TTL: 7 天

2. **L2: 整段对话缓存** (Redis)
   - 键: `sha256(dialogue_str:full:rate:pitch)`
   - 缓存完整对话的音频数据
   - TTL: 7 天

3. **L3: 文件系统缓存**
   - 位置: `apps/backend/data/audio_files/`
   - 命名: `{audio_id}_{cache_key[:8]}.mp3`

4. **元数据缓存** (Redis)
   - 键: `english_tts:audio_meta:{audio_id}`
   - 缓存音频记录信息
   - TTL: 24 小时

### TTS 合成流程

1. 客户端 POST `/audios/{id}/generate`
2. 检查整段对话缓存 (L2)
3. 若未命中，并行合成所有句子（利用 L1 缓存）
4. 使用 pydub 合并音频片段（添加停顿）
5. 写入文件并更新 L2 缓存
6. 返回结果

### API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/courses` | 课程列表 |
| POST | `/courses` | 创建课程 |
| GET | `/courses/{id}` | 课程详情 |
| PUT | `/courses/{id}` | 更新课程 |
| DELETE | `/courses/{id}` | 删除课程 |
| GET | `/notes?course_id={id}` | 笔记列表 |
| POST | `/notes` | 创建笔记 |
| GET | `/notes/{id}` | 笔记详情 |
| PUT | `/notes/{id}` | 更新笔记 |
| DELETE | `/notes/{id}` | 删除笔记 |
| GET | `/audios?course_id={id}` | 音频列表 |
| POST | `/audios` | 创建音频配置 |
| GET | `/audios/{id}` | 音频详情（含对话） |
| PUT | `/audios/{id}` | 更新音频 |
| DELETE | `/audios/{id}` | 删除音频 |
| POST | `/audios/{id}/generate` | 生成音频文件 |
| GET | `/audios/{id}/download` | 下载音频文件 |
| POST | `/audios/{id}/regenerate` | 重新生成音频（清除缓存） |

## Environment Configuration

### 后端环境变量 (apps/backend/.env)

复制 `apps/backend/.env.example` 创建 `.env`:

```bash
# 数据库
DATABASE_URL=sqlite+aiosqlite:///data/app.db

# Redis
REDIS_URL=redis://localhost:7009/0
REDIS_ENABLED=true

# 数据目录
DATA_DIR=data
```

### 前端代理配置

开发模式下，前端通过 Vite 代理访问后端 API:

```javascript
// apps/frontend/vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
    },
  },
}
```

## Code Style Guidelines

### Python (Ruff 配置)

- **引号**: 双引号
- **缩进**: 4 空格
- **行长**: 100 字符
- **导入排序**: 自动排序 (isort 规则)
- **文档字符串**: Google 风格

常用命令:
```bash
cd apps/backend
uv run ruff check app          # 检查
uv run ruff check --fix app    # 自动修复
uv run ruff format app         # 格式化
uv run pyright                 # 类型检查
```

### TypeScript / Vue

- 使用 Composition API
- 类型定义位于 `apps/frontend/src/types/`
- API 调用封装在 `apps/frontend/src/api/client.ts`

## Deployment Notes

### 生产环境建议

1. **数据库**: SQLite → PostgreSQL
   - 修改 `DATABASE_URL` 环境变量

2. **缓存**: 单 Redis → Redis Cluster
   - 修改 `REDIS_URL` 环境变量

3. **文件存储**: 本地 → 对象存储 (S3/OSS)
   - 修改 `app/services/tts.py` 中的文件操作逻辑

4. **静态文件**: 使用 CDN 或反向代理

### Docker Compose 部署

```bash
# 启动 Redis
docker compose -f apps/backend/docker-compose.yml up -d

# 启动后端 (需先进入 backend 目录安装依赖)
cd apps/backend
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# 前端构建
cd apps/frontend
pnpm build
# 部署 dist/ 目录到静态服务器
```

## Development Tips

1. **首次设置**
   ```bash
   # 安装 Python 依赖
   cd apps/backend && uv sync
   
   # 安装 Node 依赖
   pnpm install
   
   # 启动所有服务
   pnpm dev
   ```

2. **重置数据库**
   - 删除 `apps/backend/data/app.db`
   - 重启后端服务，数据库会自动重建

3. **清除 Redis 缓存**
   ```bash
   redis-cli -p 7009 FLUSHDB
   ```

4. **查看 API 文档**
   - 启动后端后访问 http://localhost:8000/docs
   - 包含交互式 Swagger UI

## Security Considerations

- 当前为本地开发配置，CORS 允许 `localhost:5173`
- 生产环境需要：
  - 修改 `allow_origins` 为实际域名
  - 添加身份验证和授权
  - 使用 HTTPS
  - 限制文件上传大小和类型
  - 配置适当的 Redis 访问控制
