## 项目计划与执行清单（更新于 2026-03-02）

### 当前结论

- 本地产品主流程已可验证：`登录 -> 定级 -> 今日学习 -> 跟读评分 -> 问答评估 -> 复习任务 -> AI 助教`
- 目前以“本地验证产品形态”为目标，注册/支付/订阅先不做

### Epic 1: 基础设施

- [x] Task 1.2: Pinia 全局状态管理（session/auth/player/learning/review）
- [~] Task 1.3: 后端数据结构
  - 已完成：`ReviewTask`（用户维度复习任务）
  - 待完成：`Users / User_Vocabulary / Playground_History` 正式表结构
- [~] Task 1.4: Auth / 支付
  - 已完成：测试账号登录、`/auth/login`、`/auth/me`
  - 暂缓：注册、Stripe 支付与订阅系统

### Epic 2: AI 与语音引擎

- [x] Task 2.1: `generateLesson` API（LangChain + OpenAI 兼容；含 Level0/N+1 约束）
- [x] Task 2.2: `evaluateQA` API
- [~] Task 2.3: `aiTutorChat`
  - 已完成：非流式 + 后端流式接口
  - 待完成：前端完整流式渲染
- [ ] Task 2.4: Azure TTS 真接口
- [~] Task 2.5: 发音评估
  - 已完成：`/ai/evaluate-pronunciation` + 本地评分策略
  - 待完成：Azure Pronunciation Assessment 真打分

### Epic 3: 引导流与状态管理

- [x] Task 3.1: 目标选择 UI
- [x] Task 3.2: 水平滑动选择器（原生轮播实现）
- [~] Task 3.3: Level 状态写入
  - 已完成：Pinia 存储与路由流程
  - 待完成：同步写入后端用户配置

### Epic 4: 学习流核心组件

- [x] Task 4.1: 主页学习日历 + 今日任务
- [x] Task 4.2: 听力学习区（课文 + 新词/语法/文化点 + 播放）
- [x] Task 4.3: 跟读打分（录音识别文本 + 评分 + 60 分放行）
- [x] Task 4.4: 课后问答 + 结算
- [x] Task 4.5: 全局悬浮 AI Tutor

### Epic 5: 遗忘曲线复习机制

- [x] Task 5.1: [1,2,3,5,7,15,30] 复习队列逻辑（后端持久化）
- [x] Task 5.2: 复习视图 + 全文朗读评分 + 60 分验证

### Epic 6: 游乐园与个人中心

- [ ] Task 6.1: 游乐园引擎（50题抽取）
- [ ] Task 6.2: 游乐园交互卡片
- [ ] Task 6.3: 个人中心（笔记/错题/单词/订阅状态）

---

## 下一阶段执行计划（建议）

### Phase A（优先，1-2 天）

- [ ] A1: Azure Pronunciation Assessment 接入（替换本地评分）
- [ ] A2: Onboarding 目标/等级写后端用户配置（`/user/profile`）
- [ ] A3: AI Tutor 前端流式渲染（消费 `stream=true`）

### Phase B（并行，2-3 天）

- [ ] B1: Azure TTS 接入与回退策略（Azure 失败时回退 edge-tts）
- [ ] B2: 复习任务仪表盘（下一次复习时间、阶段、通过率）
- [ ] B3: 学习记录表（每日完成状态，供日历真实展示）

### Phase C（后续）

- [ ] C1: 游乐园模块 MVP
- [ ] C2: 个人中心 MVP
- [ ] C3: 注册/支付/订阅完整闭环
