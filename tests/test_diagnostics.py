"""经原生服务验证维护者诊断能力与教学调用权限。"""

import asyncio
import json
import os
from pathlib import Path

import httpx
import pytest
from websockets.asyncio.client import connect
from websockets.exceptions import InvalidStatus

from teaching_harness.client import HarnessClient
from teaching_harness.contracts import TaskRequest, task_id


@pytest.mark.parametrize(
    "identity,token", [("测试调用方", "test-token"), ("维护者", "debug-token")]
)
async def test_未开放的事件命令协议不能绕过运行与诊断限制(server, request_data, identity, token):
    request_data["event_id"] = f"未开放协议-{identity}"
    request = TaskRequest.model_validate(request_data)
    tid = task_id(identity, request.event_id)
    async with HarnessClient(server, identity, token) as client:
        await client.native.threads.create(
            thread_id=tid, metadata={"request": request.model_dump()}
        )
        async with client.http.stream(
            "POST",
            f"/threads/{tid}/stream/events",
            json={"channels": ["messages", "tools"], "depth": 10},
        ) as response:
            assert response.status_code == 404
        response = await client.http.post(
            f"/threads/{tid}/commands",
            json={
                "id": 2,
                "method": "run.start",
                "params": {
                    "assistant_id": "curriculum",
                    "input": {"request": request.model_dump()},
                    "multitaskStrategy": "reject",
                    "config": {"recursion_limit": 1},
                    "metadata": {"caller_override": True},
                },
            },
        )
        assert response.status_code == 404
        assert await client.native.runs.list(tid) == []
    with pytest.raises(InvalidStatus) as error:
        async with connect(
            server.replace("http://", "ws://") + f"/threads/{tid}/stream/events",
            additional_headers={"Authorization": f"Bearer {token}"},
        ):
            pytest.fail("未开放的 WebSocket 协议不应握手成功")
    assert error.value.response.status_code == 403


async def test_维护者取得原生模型工具请求和对应返回(server, request_data):
    request_data["event_id"] = "维护者工具追踪"
    request = TaskRequest.model_validate(request_data)
    tid = task_id("维护者", request.event_id)
    async with HarnessClient(server, "维护者", "debug-token") as client:
        await client.native.threads.create(
            thread_id=tid, metadata={"request": request.model_dump()}
        )
        chunks = [
            chunk
            async for chunk in client.native.runs.stream(
                tid,
                "curriculum",
                input={"request": request.model_dump()},
                multitask_strategy="reject",
                stream_mode=["messages-tuple", "updates", "debug", "custom"],
                stream_subgraphs=True,
            )
        ]
        payload = json.dumps([chunk.data for chunk in chunks], ensure_ascii=False)
        assert '"tool_call_id": "math"' in payload
        assert '"expression": "(23-11)/(6-2)"' in payload
        assert '"content": "3"' in payload
        assert "debug-token" not in payload
        assert (await client.query(tid))["status"] == "completed"
        state = await client.native.threads.get_state(tid, subgraphs=True)
        assert state["values"]["status"] == "completed"


async def test_普通调用方不能通过重连请求详细流(server, request_data):
    request_data["event_id"] = "重连诊断隔离"
    async with HarnessClient(server, "测试调用方", "test-token") as client:
        receipt = await client.submit(TaskRequest.model_validate(request_data))
        await client.native.runs.join(receipt.task_id, receipt.run_id)
        with pytest.raises(httpx.HTTPStatusError) as error:
            async for _ in client.native.runs.join_stream(
                receipt.task_id, receipt.run_id, stream_mode="messages-tuple"
            ):
                pass
        assert error.value.response.status_code == 422
        response = await client.http.get(f"/threads/{receipt.task_id}/stream")
        assert response.status_code == 422
    async with HarnessClient(server, "维护者", "debug-token") as maintainer:
        response = await maintainer.http.get(f"/threads/{receipt.task_id}/state?subgraphs=true")
        assert response.status_code in {403, 404}
        # 原生 SSE 开始响应后以 error 事件报告授权失败，HTTP 头可能已经是 200。
        chunks = [
            chunk
            async for chunk in maintainer.native.runs.join_stream(
                receipt.task_id, receipt.run_id, stream_mode="messages-tuple", last_event_id="0-0"
            )
        ]
        assert chunks and all(chunk.event == "error" for chunk in chunks), chunks
        assert "404" in json.dumps([chunk.data for chunk in chunks]), chunks


async def test_诊断消费者结束后仍可重连取得最初工具往返(server, request_data):
    request_data["event_id"] = "诊断消费者重连"
    async with HarnessClient(server, "维护者", "debug-token") as client:
        request = TaskRequest.model_validate(request_data)
        receipt = await client.submit(request, diagnostics=True)
        await client.native.runs.join(receipt.task_id, receipt.run_id)
        chunks = [
            chunk
            async for chunk in client.native.runs.join_stream(
                receipt.task_id, receipt.run_id, last_event_id="0-0"
            )
        ]
        payload = json.dumps([chunk.data for chunk in chunks], ensure_ascii=False)
        assert '"tool_call_id": "math"' in payload
        assert '"content": "3"' in payload
        assert "curriculum_author" in payload
        assert "curriculum_reviewer" in payload
        assert await client.submit(request, diagnostics=True) == receipt


async def test_普通重连省略过滤器也只收到教学事件(server, request_data):
    request_data["event_id"] = "普通重连默认过滤"
    request = TaskRequest.model_validate(request_data)
    tid = task_id("测试调用方", request.event_id)
    async with HarnessClient(server, "测试调用方", "test-token") as client:
        await client.native.threads.create(
            thread_id=tid, metadata={"request": request.model_dump()}
        )
        run = await client.native.runs.create(
            tid,
            "curriculum",
            input={"request": request.model_dump()},
            multitask_strategy="reject",
            stream_mode=["custom", "updates"],
            stream_resumable=True,
        )
        await client.native.runs.join(tid, run["run_id"])
        chunks = [
            chunk
            async for chunk in client.native.runs.join_stream(
                tid, run["run_id"], last_event_id="0-0"
            )
        ]
        assert chunks and all(chunk.event == "custom" for chunk in chunks)


@pytest.mark.parametrize("server", ["default", "false"], indirect=True)
async def test_生产默认和显式关闭都拒绝维护者详细流但保留基础记录(server, request_data):
    request_data["event_id"] = f"关闭维护者诊断-{server.rsplit(':', 1)[-1]}"
    request = TaskRequest.model_validate(request_data)
    async with HarnessClient(server, "维护者", "debug-token") as client:
        tid = task_id("维护者", request.event_id)
        await client.native.threads.create(
            thread_id=tid, metadata={"request": request.model_dump()}
        )
        with pytest.raises(httpx.HTTPStatusError) as error:
            await client.native.runs.create(
                tid,
                "curriculum",
                input={"request": request.model_dump()},
                multitask_strategy="reject",
                stream_mode="messages-tuple",
            )
        assert error.value.response.status_code == 422
        receipt = await client.submit(request)
        await client.native.runs.join(receipt.task_id, receipt.run_id)
        result = await client.query(tid)
        assert result["status"] == "completed"
        assert result["usage"]["model_calls"] > 0
        for path in [
            f"/threads/{tid}/state?subgraphs=true",
            f"/threads/{tid}/runs/{receipt.run_id}/stream?stream_mode=messages-tuple",
        ]:
            response = await client.http.get(path)
            assert response.status_code == 422


async def test_命令行诊断文件包含失败工具往返且仅本机用户可读(server, tmp_path):
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "result.json"
    trace = tmp_path / "trace.jsonl"
    environment = os.environ.copy()
    environment["HARNESS_AUTH_TOKENS"] = json.dumps({"维护者": "debug-token"})
    process = await asyncio.create_subprocess_exec(
        str(root / ".venv/bin/python"),
        str(root / "examples/live_curriculum.py"),
        "--url",
        server,
        "--event",
        "命令行失败工具追踪",
        "--instruction",
        "验证失败工具追踪",
        "--diagnostics",
        str(trace),
        "--output",
        str(output),
        cwd=tmp_path,
        env=environment,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
    assert process.returncode == 0, stderr.decode()
    lines = [json.loads(line) for line in trace.read_text().splitlines()]
    assert lines[0]["receipt"]["run_id"]
    payload = json.dumps(lines, ensure_ascii=False)
    assert '"expression": "1/0"' in payload
    assert '"tool_call_id": "math"' in payload
    assert "工具未完成" in payload
    assert "curriculum_author" in payload and "curriculum_reviewer" in payload
    assert "debug-token" not in payload
    assert b"tool_call_id" not in stdout
    assert trace.stat().st_mode & 0o777 == 0o600
    assert json.loads(output.read_text())["status"] == "completed"
