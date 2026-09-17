"""跨模型评阅的 DeepSeek 适配：思考模式下不强制工具调用，没有提交结构化结果时报出原因。"""

import pytest
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from teaching_harness.grade_evaluation.models import MissingToolCall, ThinkingDeepSeek, diagnose
from teaching_harness.grade_evaluation.review import ModelReview


def test_强制工具调用改为由模型自行调用():
    model = ThinkingDeepSeek(model="deepseek-flash", api_key="test")
    bound = model.bind_tools([ModelReview], tool_choice="any")
    assert bound.kwargs["tool_choice"] == "auto"


def result(message):
    return ChatResult(generations=[ChatGeneration(message=message)])


def test_没有工具调用的回复报出结束原因与用量():
    truncated = AIMessage(
        content="",
        response_metadata={"finish_reason": "length"},
        usage_metadata={
            "input_tokens": 29888,
            "output_tokens": 32768,
            "total_tokens": 62656,
            "output_token_details": {"reasoning": 32768},
        },
    )
    with pytest.raises(MissingToolCall, match="length.*32768.*思考 32768"):
        diagnose(result(truncated))
    called = AIMessage(content="", tool_calls=[{"name": "ModelReview", "args": {}, "id": "call-1"}])
    diagnose(result(called))
