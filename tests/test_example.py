"""外部调用示例必须保留调用方明确传入的实际旧稿。"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest


async def test_全年请求与source组合不会静默丢弃旧稿(tmp_path, monkeypatch, request_data):
    path = Path(__file__).resolve().parents[1] / "examples/live_curriculum.py"
    spec = importlib.util.spec_from_file_location("example_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    request_data.update(scope="year", target_codes=[])
    request_data["school"].update(lesson_count=180, reserve_lessons=20)
    request_path = tmp_path / "request.json"
    request_path.write_text(json.dumps(request_data))
    source_path = tmp_path / "draft.json"
    source_path.write_text(json.dumps({"narrative": "调用方明确提供的旧稿"}))
    monkeypatch.setenv("HARNESS_AUTH_TOKENS", '{"测试":"test-token"}')
    monkeypatch.setattr(module, "load_dotenv", lambda *a: None)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(path),
            "--event",
            "全年修订",
            "--request",
            str(request_path),
            "--source",
            str(source_path),
        ],
    )
    captured = []

    class Captured(Exception):
        pass

    class Client:
        def __init__(self, *args):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def submit(self, request, **kwargs):
            captured.append(request)
            raise Captured

    monkeypatch.setattr(module, "HarnessClient", Client)
    with pytest.raises(Captured):
        await module.main()
    assert captured[0].scope == "year"
    assert captured[0].external_content[0].content == {"narrative": "调用方明确提供的旧稿"}
