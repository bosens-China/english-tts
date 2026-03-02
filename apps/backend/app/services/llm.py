"""LangChain LLM 服务（OpenAI 兼容接口）。"""

import json
import os
import re
from typing import Any, cast


class LLMService:
    """基于 LangChain 的 LLM 调用封装。"""

    def __init__(self) -> None:
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))
        self.mock_enabled = os.getenv("LLM_MOCK_ENABLED", "true").lower() == "true"

    def _build_client(self):
        # 延迟导入，避免未安装依赖时导致服务无法启动
        from langchain_openai import ChatOpenAI

        if not self.api_key:
            raise RuntimeError("LLM_API_KEY 未配置")

        return ChatOpenAI(
            model=self.model,
            api_key=cast(Any, self.api_key),
            base_url=self.base_url,
            temperature=self.temperature,
        )

    def _extract_json(self, content: str) -> dict[str, Any]:
        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            text = text.replace("json\n", "", 1).strip()
        return json.loads(text)

    async def generate_lesson(self, level: int, goal: str) -> dict[str, Any]:
        """生成课文（Level 0 与 Level 1+ N+1 均在 Prompt 里约束）。"""
        if not self.api_key and self.mock_enabled:
            return self._mock_lesson(level=level, goal=goal)
        model = self._build_client()
        prompt = f"""
你是英语学习课程生成器。请严格输出 JSON，不要输出额外文本。
用户 level={level}, goal={goal}

要求：
1) level=0 时，内容必须极简、强中文引导，句子很短。
2) level>=1 时，遵循 N+1：大部分词汇在当前难度，少量新词+下一个语法点。
3) questions 必须是 3 个题目。
4) audio_script 是数组，每项含 speaker, voice, text, pause_ms。

JSON 字段：
{{
  "text": "完整课文",
  "audio_script": [{{"speaker":"Narrator","voice":"en-US-AriaNeural","text":"...","pause_ms":500}}],
  "new_words": ["..."],
  "grammar": ["..."],
  "culture_notes": ["..."],
  "questions": ["...", "...", "..."]
}}
"""
        result = await model.ainvoke(prompt)
        content = str(result.content)
        return self._extract_json(content)

    async def evaluate_qa(self, lesson_text: str, question: str, user_answer: str) -> dict[str, Any]:
        """判定问答表现。"""
        if not self.api_key and self.mock_enabled:
            score = 80 if len(user_answer.strip()) >= 8 else 45
            return {
                "score": score,
                "passed": score >= 60,
                "feedback": "回答较完整，继续保持。" if score >= 60 else "回答偏短，建议补充细节。",
            }
        model = self._build_client()
        prompt = f"""
你是英语老师。根据课文和问题判断回答是否正确。
请严格输出 JSON:
{{
  "score": 0-100 的整数,
  "passed": true/false,
  "feedback": "简短反馈（中文）"
}}

课文:
{lesson_text}

问题:
{question}

用户回答:
{user_answer}
"""
        result = await model.ainvoke(prompt)
        return self._extract_json(str(result.content))

    async def evaluate_pronunciation(self, reference_text: str, spoken_text: str) -> dict[str, Any]:
        """发音评估（本地 mock 评分，后续可替换 Azure API）。"""
        ref_words = re.findall(r"[a-zA-Z']+", reference_text.lower())
        spoken_words = re.findall(r"[a-zA-Z']+", spoken_text.lower())
        if not ref_words:
            return {"score": 0, "passed": False, "accuracy": 0.0, "feedback": "参考文本为空。"}

        ref_set = set(ref_words)
        spoken_set = set(spoken_words)
        overlap = len(ref_set & spoken_set)
        accuracy = overlap / max(len(ref_set), 1)
        score = int(round(accuracy * 100))
        passed = score >= 60
        feedback = "跟读通过，继续下一步。" if passed else "跟读未达标，建议放慢语速再读一次。"

        return {
            "score": score,
            "passed": passed,
            "accuracy": round(accuracy, 2),
            "feedback": feedback,
        }

    async def tutor_chat(self, context: str, history: list[dict], message: str) -> str:
        """AI 助教聊天（非流式）。"""
        if not self.api_key and self.mock_enabled:
            return f"这是本地 Mock 助教回复：你问的是“{message}”。建议先跟读 3 遍，再复述 1 次。"
        model = self._build_client()
        from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

        messages: list[BaseMessage] = [
            SystemMessage(content="你是英语助教，优先用简洁中文解释，保留关键英文表达。")
        ]
        if context:
            messages.append(SystemMessage(content=f"当前课文上下文：\n{context}"))
        for item in history:
            role = item.get("role")
            content = item.get("content", "")
            if role == "assistant":
                messages.append(AIMessage(content=content))
            elif role == "user":
                messages.append(HumanMessage(content=content))
        messages.append(HumanMessage(content=message))

        result = await model.ainvoke(messages)
        return str(result.content)

    async def tutor_chat_stream(self, context: str, history: list[dict], message: str):
        """AI 助教聊天（流式，按 token 输出文本）。"""
        if not self.api_key and self.mock_enabled:
            reply = f"这是本地 Mock 流式回复：关于“{message}”，先听后说，注意连读和停顿。"
            for chunk in reply.split("，"):
                yield f"{chunk}，"
            return
        model = self._build_client()
        from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

        messages: list[BaseMessage] = [
            SystemMessage(content="你是英语助教，优先用简洁中文解释，保留关键英文表达。")
        ]
        if context:
            messages.append(SystemMessage(content=f"当前课文上下文：\n{context}"))
        for item in history:
            role = item.get("role")
            content = item.get("content", "")
            if role == "assistant":
                messages.append(AIMessage(content=content))
            elif role == "user":
                messages.append(HumanMessage(content=content))
        messages.append(HumanMessage(content=message))

        async for chunk in model.astream(messages):
            text = getattr(chunk, "content", "")
            if text:
                yield text

    def _mock_lesson(self, level: int, goal: str) -> dict[str, Any]:
        if level == 0:
            text = "Hi. I am Amy. I am from China. Nice to meet you."
            new_words = ["hi", "from", "meet"]
            grammar = ["I am ...", "be 动词基础"]
        else:
            text = (
                "Today I took the subway to work, but I got off one station early and walked to the office. "
                "It helped me relax before a busy meeting."
            )
            new_words = ["subway", "station", "relax"]
            grammar = ["一般过去时", "and/but 连接句"]

        return {
            "text": text,
            "audio_script": [
                {
                    "speaker": "Narrator",
                    "voice": "en-US-AriaNeural",
                    "text": sentence.strip(),
                    "pause_ms": 500,
                }
                for sentence in text.split(".")
                if sentence.strip()
            ],
            "new_words": new_words + [goal],
            "grammar": grammar,
            "culture_notes": ["英语口语中常用短句表达，不追求长难句。"],
            "questions": [
                "Where did the speaker go today?",
                "Why did the speaker walk to the office?",
                "Can you retell the story in your own words?",
            ],
        }


llm_service = LLMService()
