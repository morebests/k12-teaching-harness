"""通过真实 Agent Server 的原生接口验证教学任务。"""

import asyncio
import json
from contextlib import aclosing

import httpx
import pytest

from teaching_harness.client import HarnessClient
from teaching_harness.contracts import TaskRequest, task_id


@pytest.mark.asyncio
async def test_重送同一发起事件取得同一任务且不同正文冲突(server, request_data):
    async with HarnessClient(server, "测试调用方", "test-token") as client:
        request = TaskRequest.model_validate(request_data)
        first = await client.submit(request)
        second = await client.submit(request)
        assert second == first
        changed = request.model_copy(update={"instruction": "改为只设计一个任务"})
        with pytest.raises(httpx.HTTPStatusError) as error:
            await client.submit(changed)
        assert error.value.response.status_code == 409


async def test_实际课程与检查可以查询且查询不启动新运行(server, request_data):
    request_data["event_id"] = "当前内容"
    async with HarnessClient(server, "测试调用方", "test-token") as client:
        receipt = await client.submit(TaskRequest.model_validate(request_data))
        await client.native.runs.join(receipt.task_id, receipt.run_id)
        result = await client.query(receipt.task_id)
        assert result["status"] == "completed"
        assert "变化率" in result["content"]["narrative"]
        assert result["checks"]["applicable"] is True
        assert result["checks"]["passed"] is True
        assert result["content"]["tasks"][0]["solution"]
        assert await client.query(receipt.task_id) == result
        assert len(await client.native.runs.list(receipt.task_id)) == 1


async def test_不能通过原生流索取模型原始消息(server, request_data):
    request_data["event_id"] = "原始消息隔离"
    request = TaskRequest.model_validate(request_data)
    tid = task_id("测试调用方", request.event_id)
    async with HarnessClient(server, "测试调用方", "test-token") as client:
        await client.native.threads.create(
            thread_id=tid, metadata={"request": request.model_dump()}
        )
        with pytest.raises(httpx.HTTPStatusError) as error:
            await client.native.runs.create(
                tid,
                "curriculum",
                input={"request": request.model_dump()},
                multitask_strategy="reject",
                stream_mode="messages",
            )
        assert error.value.response.status_code == 422


async def test_资源触限保留未检查草稿(server, request_data):
    request_data["event_id"] = "保存后触限"
    request_data["limits"]["model_calls"] = 2
    async with HarnessClient(server, "测试调用方", "test-token") as client:
        receipt = await client.submit(TaskRequest.model_validate(request_data))
        await client.native.runs.join(receipt.task_id, receipt.run_id)
        result = await client.query(receipt.task_id)
        assert result["status"] == "stopped"
        assert result["content"]["tasks"]
        assert result["checks"] is None
        assert result["usage"]["model_calls"] == 2


async def test_缺失知识与越权读取有明确结果(server, request_data):
    request_data["event_id"] = "缺失知识"
    request_data["target_codes"] = ["8.F.A.2"]
    async with HarnessClient(server, "测试调用方", "test-token") as client:
        receipt = await client.submit(TaskRequest.model_validate(request_data))
        await client.native.runs.join(receipt.task_id, receipt.run_id)
        result = await client.query(receipt.task_id)
        assert result["status"] == "failed" and result["content"] is None
    async with HarnessClient(server, "其他学校", "other-token") as other:
        for read in [other.query, other.native.threads.get]:
            with pytest.raises(httpx.HTTPStatusError) as error:
                await read(receipt.task_id)
            assert error.value.response.status_code in {403, 404}


async def test_当前源被改写不能沿用旧检查坏图件不能交付(server, request_data, work_root):
    request_data["event_id"] = "文件变化"
    async with HarnessClient(server, "测试调用方", "test-token") as client:
        receipt = await client.submit(TaskRequest.model_validate(request_data))
        await client.native.runs.join(receipt.task_id, receipt.run_id)
        path = work_root / receipt.task_id / "content/curriculum.json"
        source = json.loads(path.read_text())
        source["narrative"] += "外部改写。"
        path.write_text(json.dumps(source))
        changed = await client.query(receipt.task_id)
        assert changed["status"] == "incomplete"
        assert changed["checks"]["applicable"] is False
        source["tasks"][0]["blocks"] = [
            {"type": "image", "src": "assets/missing.svg", "alt": "缺失图"}
        ]
        path.write_text(json.dumps(source))
        with pytest.raises(httpx.HTTPStatusError) as error:
            await client.query(receipt.task_id)
        assert error.value.response.status_code == 409


async def test_并行重送仍指向同一运行(server, request_data):
    request_data["event_id"] = "同时重送"
    async with HarnessClient(server, "测试调用方", "test-token") as client:
        receipts = await asyncio.gather(
            *[client.submit(TaskRequest.model_validate(request_data)) for _ in range(3)]
        )
        assert receipts[0] == receipts[1] == receipts[2]
        assert len(await client.native.runs.list(receipts[0].task_id)) == 1


@pytest.mark.parametrize("cancel", [False, True])
async def test_真实流展示未检查草稿断流后查询原任务或取消(server, request_data, cancel):
    request_data["event_id"] = "取消" if cancel else "断流"
    request = TaskRequest.model_validate(request_data)
    tid = task_id("测试调用方", request.event_id)
    async with HarnessClient(server, "测试调用方", "test-token") as client:
        await client.native.threads.create(
            thread_id=tid, metadata={"request": request.model_dump()}
        )
        stream = client.native.runs.stream(
            tid,
            "curriculum",
            input={"request": request.model_dump()},
            stream_mode="custom",
            multitask_strategy="reject",
            on_disconnect="continue",
        )
        draft = None
        async with aclosing(stream):
            async for event in stream:
                if event.event == "custom" and event.data.get("type") == "draft":
                    draft = event.data
                    break
        assert draft and draft["checked"] is False and draft["content"]["tasks"]
        run = (await client.native.runs.list(tid))[0]
        if cancel:
            await client.native.runs.cancel(tid, run["run_id"], action="interrupt", wait=True)
        else:
            await client.native.runs.join(tid, run["run_id"])
        result = await client.query(tid)
        assert result["status"] == ("cancelled" if cancel else "completed")
        assert result["content"]["tasks"]
        assert len(await client.native.runs.list(tid)) == 1


async def test_无凭据和开发工具后门不能读取任务(server):
    async with httpx.AsyncClient(base_url=server) as http:
        for headers in [{}, {"x-api-key": "invalid-studio-token"}]:
            response = await http.post("/threads/search", json={}, headers=headers)
            assert response.status_code == 401
