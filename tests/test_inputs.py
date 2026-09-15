import pytest
from pydantic import ValidationError

from teaching_harness.contracts import TaskRequest, fingerprint
from teaching_harness.mathematics import calculate


@pytest.mark.parametrize(
    "change",
    [
        {"capability": "lesson_prep"},
        {"scope": "grade"},
        {"instruction": "使用 Illustrative Mathematics 的对应课程"},
        {"owner": "管理员"},
    ],
)
def test_未实现范围与正文自授权限会被拒绝(request_data, change):
    with pytest.raises(ValidationError):
        TaskRequest.model_validate({**request_data, **change})


def test_接收外部实际原课但拒绝错误指纹(request_data):
    source = "这是一份由调用方规范化的实际原课，包含 $y=3x+5$。"
    item = {
        "id": "external",
        "source": {"label": "教师原课", "origin": "caller", "version": "1"},
        "content": source,
        "fingerprint": fingerprint(source),
    }
    request_data["external_content"] = [item]
    assert TaskRequest.model_validate(request_data).external_content[0].content == source
    item["content"] += "改变正文"
    with pytest.raises(ValidationError):
        TaskRequest.model_validate(request_data)


def test_受限算术核对不等间隔变化率并拒绝代码():
    assert calculate("(23-11)/(6-2)") == "3"
    assert calculate("11-3*2") == "5"
    for expression in ["__import__('os')", "2**1000000", "2**(2**12)"]:
        with pytest.raises(ValueError):
            calculate(expression)
