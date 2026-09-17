"""评价用模型的适配：DeepSeek 思考模式下不强制工具调用；没有提交结构化结果或输出被截断时说明原因。

实际发给模型的输出上限与运行记录中的上限一致。
"""

import pytest
from langchain_core.messages import AIMessage

from teaching_harness.grade_evaluation.models import (
    IncompleteReply,
    ThinkingDeepSeek,
    check_complete,
    diagnose,
    evaluation_model,
    max_output_tokens,
)
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


def reply(finish, output=41000, reasoning=33000):
    return AIMessage(
        content="",
        tool_calls=[{"name": "ModelPromises", "args": {}, "id": "c1"}],
        response_metadata={"finish_reason": finish},
        usage_metadata={
            "input_tokens": 24069,
            "output_tokens": output,
            "total_tokens": 24069 + output,
            "output_token_details": {"reasoning": reasoning},
        },
    )


@pytest.mark.parametrize("finish", ["MAX_TOKENS", "length"])
def test_因输出上限结束的回复即使带有结构化结果也按失败处理(finish):
    with pytest.raises(IncompleteReply, match=f"第 2 轮.*输出上限.*{finish}.*思考 33000"):
        check_complete([reply("STOP", 900, 100), reply(finish)])


@pytest.mark.parametrize("finish", ["SAFETY", "MALFORMED_FUNCTION_CALL", "content_filter", None])
def test_其他非正常结束或结束原因缺失也按失败处理(finish):
    with pytest.raises(IncompleteReply, match=f"没有正常结束.*{finish}"):
        check_complete([reply(finish)])


def test_正常结束的各轮回复通过():
    check_complete([reply("STOP"), reply("stop"), reply("tool_calls")])


def test_实际输出上限与记录一致_传入的模型名生效(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test")
    monkeypatch.delenv("HARNESS_MODEL", raising=False)
    gemini = evaluation_model(tmp_path, "gemini-3.8-flash")
    assert gemini.max_output_tokens == max_output_tokens("gemini-3.8-flash") == 65536
    assert evaluation_model(tmp_path, "gemini-3.1-pro").model == "gemini-3.1-pro"
    deepseek = evaluation_model(tmp_path, "deepseek-flash")
    assert deepseek.max_tokens == max_output_tokens("deepseek-flash") == 131072
