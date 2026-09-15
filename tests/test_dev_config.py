"""启动进程边界：开发默认诊断，尊重显式关闭与云端追踪配置。"""

import os
import runpy
from pathlib import Path

import pytest
from langsmith.utils import get_env_var, tracing_is_enabled


@pytest.mark.parametrize(
    ("settings", "diagnostics", "tracing"),
    [
        ({}, "true", "false"),
        ({"HARNESS_DIAGNOSTICS": "false", "LANGSMITH_TRACING": "true"}, "false", "true"),
        ({"LANGCHAIN_TRACING_V2": "true"}, "true", "true"),
        ({"LANGSMITH_TRACING": "false", "LANGCHAIN_TRACING_V2": "true"}, "true", "false"),
        ({"LANGSMITH_TRACING_V2": "true"}, "true", "true"),
        ({"LANGSMITH_TRACING": "false", "LANGSMITH_TRACING_V2": "true"}, "true", "false"),
        ({"LANGCHAIN_TRACING": "true"}, "true", "true"),
    ],
)
def test_开发启动保留服务端诊断和追踪开关(monkeypatch, settings, diagnostics, tracing):
    # 不读取真实本机配置，也不启动外部服务；只拦截 dotenv 与 execv 进程边界。
    monkeypatch.setattr(os, "environ", os.environ.copy())
    monkeypatch.setattr("dotenv.load_dotenv", lambda *args: None)
    for key in (
        "HARNESS_DIAGNOSTICS",
        "LANGSMITH_TRACING",
        "LANGSMITH_TRACING_V2",
        "LANGCHAIN_TRACING_V2",
        "LANGCHAIN_TRACING",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("HARNESS_AUTH_TOKENS", '{"测试调用方":"test-token"}')
    for key, value in settings.items():
        monkeypatch.setenv(key, value)
    captured = {}
    monkeypatch.setattr(os, "execv", lambda *args: captured.update(os.environ))
    runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/dev.py"))
    assert captured["HARNESS_DIAGNOSTICS"] == diagnostics
    assert captured["LANGSMITH_TRACING"] == tracing
    get_env_var.cache_clear()
    try:
        assert tracing_is_enabled() is (tracing == "true")
    finally:
        get_env_var.cache_clear()
