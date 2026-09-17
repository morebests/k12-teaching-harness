"""跨模型评阅的 DeepSeek 适配：思考模式下不强制工具调用，没有提交结构化结果时说明原因。"""

import pytest
from langchain_core.messages import AIMessage

from teaching_harness.grade_evaluation.models import ThinkingDeepSeek, diagnose
from teaching_harness.grade_evaluation.review import CallRecorder, ModelReview


@pytest.mark.parametrize("forced", ["any", "required", True, "ModelReview", {"type": "function"}])
def test_强制工具调用的各种写法都改为由模型自行调用(forced):
    model = ThinkingDeepSeek(model="deepseek-flash", api_key="test")
    assert model.bind_tools([ModelReview], tool_choice=forced).kwargs["tool_choice"] == "auto"


def test_没有工具调用的回复给出结束原因与用量_空记录不算完整():
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
    reason = diagnose(truncated)
    assert reason and "length" in reason and "思考 32768" in reason
    called = AIMessage(content="", tool_calls=[{"name": "ModelReview", "args": {}, "id": "c1"}])
    assert diagnose(called) is None
    usage, complete = CallRecorder().usage()
    assert not complete and usage["total_tokens"] == 0
