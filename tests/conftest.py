"""真实 dev 服务夹具；可控模型只位于 tests。"""

import json
import os
import socket
import subprocess
import time
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def request_data():
    return {
        "event_id": "重复事件",
        "instruction": "设计八年级线性函数的一个有限课段，包含实际关键任务。",
        "target_codes": ["8.F.B.4"],
        "school": {
            "source": {"label": "离线研究条件", "version": "1", "origin": "synthetic"},
            "lesson_count": 3,
            "minutes_per_lesson": 50,
            "class_size": 28,
            "resources": ["纸笔", "方格纸", "直尺", "黑白打印", "普通计算器"],
            "learner_context": "假设有前序年级学习经历；无实际掌握度证据。",
        },
        "limits": {"model_calls": 30, "tool_calls": 80, "total_tokens": 300000, "seconds": 900},
    }


@pytest.fixture(scope="session")
def work_root(tmp_path_factory):
    return tmp_path_factory.mktemp("content")


@pytest.fixture(scope="session")
def server(tmp_path_factory, work_root, request):
    work = tmp_path_factory.mktemp("server")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    config = {
        "dependencies": [str(ROOT)],
        "graphs": {"curriculum": str(ROOT / "tests/fake_graph.py") + ":graph"},
        "auth": {
            "path": str(ROOT / "src/teaching_harness/auth.py") + ":auth",
            "disable_studio_auth": True,
        },
        "http": {
            **json.loads((ROOT / "langgraph.json").read_text())["http"],
            "app": str(ROOT / "src/teaching_harness/api.py") + ":app",
        },
        "env": {
            **json.loads((ROOT / "langgraph.json").read_text())["env"],
            "HARNESS_AUTH_TOKENS": json.dumps(
                {"测试调用方": "test-token", "其他学校": "other-token", "维护者": "debug-token"}
            ),
            "HARNESS_DIAGNOSTICS": "true",
            "HARNESS_DEBUG_IDENTITIES": json.dumps(["维护者"]),
            "HARNESS_WORK_DIR": os.path.relpath(work_root, work),
            "LANGSMITH_TRACING": "false",
            "LANGCHAIN_TRACING_V2": "false",
            "LANGGRAPH_CLI_NO_ANALYTICS": "1",
        },
    }
    diagnostic_mode = getattr(request, "param", "true")
    if diagnostic_mode == "default":
        del config["env"]["HARNESS_DIAGNOSTICS"]
    else:
        config["env"]["HARNESS_DIAGNOSTICS"] = diagnostic_mode
    (work / "langgraph.json").write_text(json.dumps(config))
    environment = os.environ.copy()
    environment.pop("HARNESS_DIAGNOSTICS", None)
    with (work / "server.log").open("w") as log:
        proc = subprocess.Popen(
            [
                str(ROOT / ".venv/bin/langgraph"),
                "dev",
                "--no-browser",
                "--no-reload",
                "--port",
                str(port),
            ],
            cwd=work,
            stdout=log,
            stderr=log,
            env=environment,
        )
        try:
            for _ in range(120):
                try:
                    r = httpx.get(f"http://127.0.0.1:{port}/ok", timeout=1)
                    if r.status_code == 200:
                        yield f"http://127.0.0.1:{port}"
                        return
                except httpx.HTTPError:
                    pass
                if proc.poll() is not None:
                    break
                time.sleep(0.25)
            pytest.fail((work / "server.log").read_text()[-9000:])
        finally:
            proc.terminate()
            proc.wait(timeout=15)
