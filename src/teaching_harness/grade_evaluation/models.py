"""离线评价使用的模型：默认 Gemini，跨模型对照用 DeepSeek。"""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_deepseek import ChatDeepSeek

from teaching_harness.graph import gemini

DEFAULT_MODEL = "gemini-3.8-flash"
GEMINI_MAX_OUTPUT = 32768
DEEPSEEK_MAX_OUTPUT = 131072


def model_name() -> str:
    return os.environ.get("HARNESS_MODEL", DEFAULT_MODEL)


def max_output_tokens(name: str) -> int:
    return DEEPSEEK_MAX_OUTPUT if name.startswith("deepseek") else GEMINI_MAX_OUTPUT


class ThinkingDeepSeek(ChatDeepSeek):
    """DeepSeek 思考模式不接受强制工具调用，改由模型自行调用结构化结果工具。

    模型没有提交结构化结果时评阅调用失败，原因由 diagnose 从记下的回复中给出；
    接口不回传思考内容，工具调用后的下一轮看不到上一轮的思考。
    """

    def bind_tools(self, tools: Any, *, tool_choice: Any = None, **kwargs: Any) -> Any:
        if not (tool_choice is None or tool_choice in ("auto", "none")):
            tool_choice = "auto"
        return super().bind_tools(tools, tool_choice=tool_choice, **kwargs)


def diagnose(message: BaseMessage) -> str | None:
    """不含工具调用的回复是终止回复，意味着没有提交结构化结果；说明结束原因与用量。"""
    if getattr(message, "tool_calls", None):
        return None
    usage = getattr(message, "usage_metadata", None) or {}
    details = usage.get("output_token_details") or {}
    invalid = getattr(message, "invalid_tool_calls", None) or []
    text = message.content if isinstance(message.content, str) else str(message.content)
    return (
        f"未提交结构化结果：结束原因 {message.response_metadata.get('finish_reason')}，"
        f"输出 {usage.get('output_tokens')}（思考 {details.get('reasoning')}），"
        f"无法解析的工具调用 {len(invalid)} 个{('：' + str(invalid[0])[:120]) if invalid else ''}，"
        f"文字开头：{text[:120]!r}"
    )


def evaluation_model(root: Path, name: str | None = None) -> BaseChatModel:
    # 离线评价允许一次传输重试并放宽超时；生成图保持不重试。
    load_dotenv(root / ".env")
    name = name or model_name()
    if name.startswith("deepseek"):
        # 默认思考强度 high 常把 32,768 的输出全部用于思考而来不及提交结果，放宽上限。
        return ThinkingDeepSeek(
            model=name, timeout=1800, max_retries=1, max_tokens=DEEPSEEK_MAX_OUTPUT
        )
    return gemini(timeout=900, max_retries=1)
