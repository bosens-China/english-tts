# English TTS

英语学习产品原型（本地验证版）：登录、定级、每日学习、跟读评分、问答评估、遗忘曲线复习、AI 助教。

## 当前可验证能力

- 测试账号登录（free / vip）
- Onboarding 目标选择 + 等级选择
- 今日新课生成（LangChain + OpenAI 兼容接口，支持本地 mock）
- 跟读评分（语音识别转文本 + 后端评分，>=60 通过）
- 课后问答评分（后端 `/ai/evaluate-qa`）
- 复习任务持久化（SQLite，按用户维度）与复习推进
- 全局悬浮 AI Tutor

## 快速启动

```bash
pnpm install
cd apps/backend && uv sync
pnpm dev
```

- 前端: [http://localhost:5173](http://localhost:5173)
- 后端: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- API 文档: [http://localhost:8000/docs](http://localhost:8000/docs)

## 测试账号

- `test_vip / 123456`
- `test_free / 123456`

## 本地验证路径

1. 登录（任一测试账号）
2. 选择学习目标与等级
3. 进入「今日学习」并生成课文
4. Step2 点击「开始录音识别」，提交评分（>=60）
5. Step3 回答 3 题，至少通过 2 题
6. 完成后自动写入复习任务
7. 进入「复习模式」执行复习并推进阶段

## 关键 API

### Auth

- `POST /auth/login`
- `GET /auth/me`

### AI

- `POST /ai/generate-lesson`
- `POST /ai/evaluate-qa`
- `POST /ai/evaluate-pronunciation`
- `POST /ai/tutor-chat`

### Reviews

- `GET /reviews`
- `GET /reviews?due_only=true`
- `POST /reviews`
- `POST /reviews/{task_id}/pass`

## 环境变量（后端）

`apps/backend/.env`：

```bash
# DB / Redis
DATABASE_URL=sqlite+aiosqlite:///data/app.db
REDIS_URL=redis://localhost:7009/0
REDIS_ENABLED=true
DATA_DIR=data

# Auth
AUTH_SECRET=dev-only-secret-change-in-prod
TOKEN_EXPIRE_SECONDS=2592000

# LLM (OpenAI compatible)
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.3
LLM_MOCK_ENABLED=true
```

> 未配置 `LLM_API_KEY` 时会走本地 mock，方便直接演示流程。

## 计划概览

- 已完成：本地可验证主流程（登录→定级→学习→复习→助教）
- 下一阶段：
  - Azure Speech / Pronunciation 真接口替换 mock
  - Onboarding 用户状态落库
  - 流式 AI Tutor 前端展示优化
  - Playground / 个人中心模块
