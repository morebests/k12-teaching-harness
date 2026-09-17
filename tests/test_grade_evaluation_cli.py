"""本地命令的补跑：整体评阅只重跑从未成功的维度组并合并；专项检查只重跑失败或过期的运行。"""

import pytest

from teaching_harness.grade_evaluation.cli import combine_retry, stage_action, still_failed
from teaching_harness.grade_evaluation.runs import CallRecord, ReviewRun, StageRun


def call(criteria, error=None, tokens=10):
    usage = (
        None if error else {"input_tokens": tokens, "output_tokens": 1, "total_tokens": tokens + 1}
    )
    return CallRecord(criteria=criteria, seconds=1.0, usage=usage, error=error)


def run(calls, criteria, usage):
    return ReviewRun(
        sample_id="h2-01",
        reviewer_id="rd",
        candidate_id="h2-01",
        content_fingerprint="c" * 64,
        model="deepseek-flash",
        rules_fingerprint="e" * 64,
        criteria=criteria,
        ratings=[],
        findings=[],
        evidence=[],
        rejected_citations=[],
        rejected_findings=[],
        problems=[],
        usage=usage,
        calls=calls,
    )


def test_只补跑从未成功的维度组_重试并入后保留失败记录与用量():
    earlier = run(
        [
            call(["Q1"]),
            call(["Q3", "Q5", "Q6"], error="截断"),
            call(["Q4", "Q7"], error="截断"),
            call(["Q4", "Q7"]),
            call(["Q3", "Q5", "Q6"], error="截断"),
        ],
        ["Q1", "Q4", "Q7"],
        {"input_tokens": 20, "output_tokens": 2, "total_tokens": 22},
    )
    assert still_failed(earlier) == [["Q3", "Q5", "Q6"]]
    retried = run(
        [call(["Q3", "Q5", "Q6"], tokens=30)],
        ["Q3", "Q5", "Q6"],
        {"input_tokens": 30, "output_tokens": 1, "total_tokens": 31},
    )
    merged = combine_retry(earlier, retried)
    assert merged.criteria == ["Q1", "Q4", "Q7", "Q3", "Q5", "Q6"]
    assert len(merged.calls) == 6 and still_failed(merged) == []
    assert merged.usage == {
        "input_tokens": 50,
        "output_tokens": 3,
        "total_tokens": 53,
        "cached_input_tokens": 0,
    }


def test_补跑只取所选维度组_合并时核对候选指纹():
    earlier = run(
        [call(["Q1"], error="截断"), call(["Q2", "Q8"], error="截断")],
        [],
        {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
    )
    assert still_failed(earlier, [["Q2", "Q8"]]) == [["Q2", "Q8"]]
    other = run([call(["Q1"])], ["Q1"], {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2})
    other = other.model_copy(update={"content_fingerprint": "d" * 64})
    with pytest.raises(ValueError, match="指纹"):
        combine_retry(earlier, other)


def stage_run(error=None, rules="e" * 64, model="gemini-3.8-flash", cap=65536):
    return StageRun(
        sample_id="h2-01",
        stage="promises",
        model=model,
        max_output_tokens=cap,
        rules_fingerprint=rules,
        seconds=1.0,
        error=error,
    )


def test_专项检查只重跑失败或设置已变的运行_强制时全部重跑():
    current = ("e" * 64, "gemini-3.8-flash", 65536)
    assert stage_action(None, *current, force=False) == "new"
    assert stage_action(stage_run(), *current, force=False) is None
    assert stage_action(stage_run(error="截断"), *current, force=False) == "retry"
    for changed in [
        stage_run(rules="f" * 64),
        stage_run(model="deepseek-flash"),
        stage_run(cap=32768),
        stage_run(cap=None),
    ]:
        assert stage_action(changed, *current, force=False) == "stale"
    assert stage_action(stage_run(), *current, force=True) == "force"
