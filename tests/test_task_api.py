"""通过真实 Agent Server 的原生接口验证教学任务。"""

import asyncio
import json
from contextlib import aclosing

import httpx
import pytest

from teaching_harness.client import HarnessClient
from teaching_harness.content import ContentStore
from teaching_harness.contracts import TaskRequest, task_id


async def test_单元交接带出实际图件与分配在其他单元的必要父标准(server, request_data, work_root):
    from teaching_harness.contracts import YearBlueprint

    request_data.update(event_id="完整单元交接材料", scope="year", target_codes=[])
    request_data["school"].update(lesson_count=180, reserve_lessons=20)
    async with HarnessClient(server, "测试调用方", "test-token") as client:
        receipt = await client.submit(TaskRequest.model_validate(request_data))
        await client.native.runs.join(receipt.task_id, receipt.run_id)
        result = await client.query(receipt.task_id)
        store = ContentStore(work_root, receipt.task_id)
        c = result["content"]
        c["units"][0]["lesson_count"] = 100
        c["units"].append({**c["units"][0], "id": "u2", "lesson_count": 60})
        c["goals"].extend(
            [
                {
                    "code": "8.EE.C.7",
                    "allocations": [{**c["goals"][0]["allocations"][0], "unit_id": "u1"}],
                },
                {
                    "code": "8.EE.C.7.a",
                    "allocations": [{**c["goals"][0]["allocations"][0], "unit_id": "u2"}],
                },
            ]
        )
        asset = store.plot_linear(
            "handoff", slope=3, intercept=5, x_max=8, y_max=30, x_label="分钟", y_label="升"
        )
        c["tasks"][0]["unit_ids"] = ["u2"]
        c["tasks"][0]["blocks"] = [{"type": "image", "src": asset["src"], "alt": "合成水量图"}]
        current = store.save(YearBlueprint.model_validate(c), result["fingerprint"])

        def add_scope(value):
            value["package"]["year_scope"]["nodes"] = [
                {
                    "detail": {
                        "ref": {"identifier": "parent"},
                        "source_fields": {"statementCode": "8.EE.C.7", "description": "完整父标准"},
                    },
                    "parent_ids": [],
                },
                {
                    "detail": {
                        "ref": {"identifier": "child"},
                        "source_fields": {"statementCode": "8.EE.C.7.a", "description": "实际子项"},
                    },
                    "parent_ids": ["parent"],
                },
            ]

        store.update_record("knowledge.json", add_scope)
        response = await client.http.get(
            f"/v1/threads/{receipt.task_id}/units/u2",
            params={"expected_fingerprint": current["fingerprint"]},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["assets"][asset["src"]]["fingerprint"] == asset["fingerprint"]
        assert "<svg" in data["assets"][asset["src"]]["svg"]
        assert data["assets"][asset["src"]]["parameters"]["slope"] == 3
        assert {n["detail"]["source_fields"]["statementCode"] for n in data["standards"]} == {
            "8.EE.C.7",
            "8.EE.C.7.a",
        }
        assert data["standards"][1]["parent_ids"] == ["parent"]
        assert data["status"] == "incomplete" and not data["checks"]["passed"]


async def test_全年由同一任务接口交付且单元交接绑定实际版本与身份(server, request_data):
    request_data.update(event_id="全年交接", scope="year", target_codes=[])
    request_data["school"].update(lesson_count=180, reserve_lessons=20)
    async with HarnessClient(server, "测试调用方", "test-token") as client:
        receipt = await client.submit(TaskRequest.model_validate(request_data))
        await client.native.runs.join(receipt.task_id, receipt.run_id)
        result = await client.query(receipt.task_id)
        assert result["status"] == "completed" and result["checks"]["passed"]
        path = f"/v1/threads/{receipt.task_id}/units/u1"
        handoff = await client.http.get(
            path, params={"expected_fingerprint": result["fingerprint"]}
        )
        assert handoff.status_code == 200, handoff.text
        data = handoff.json()
        assert data["parent_fingerprint"] == result["fingerprint"]
        assert data["unit"] == result["content"]["units"][0]
        assert data["school"]["source"]["origin"] == "synthetic"
        assert data["goals"][0]["code"] == "8.F.B.4"
        assert (
            await client.http.get(path, params={"expected_fingerprint": "旧版本"})
        ).status_code == 409
    async with HarnessClient(server, "其他学校", "other-token") as other:
        response = await other.http.get(
            path, params={"expected_fingerprint": result["fingerprint"]}
        )
        assert response.status_code in {403, 404}


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
        evidence = (await client.http.get(f"/v1/threads/{receipt.task_id}/evidence")).json()
        assert "operations" not in evidence["execution"]


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


async def test_框架重入已有调用证据时不归零或重复调用(server, request_data, work_root):
    request_data["event_id"] = "未完成节点重入"
    request = TaskRequest.model_validate(request_data)
    tid = task_id("测试调用方", request.event_id)
    ContentStore(work_root, tid).record(
        "execution.json",
        {
            "usage": {
                "model_calls": 3,
                "tool_calls": 2,
                "total_tokens": 900,
                "input_tokens": 600,
                "output_tokens": 300,
                "unknown_usage": True,
                "seconds": 4.0,
                "cost": None,
            },
            "events": [{"kind": "model_unfinished", "call": 3}],
        },
    )
    async with HarnessClient(server, "测试调用方", "test-token") as client:
        receipt = await client.submit(request)
        await client.native.runs.join(tid, receipt.run_id)
        result = await client.query(tid)
        assert result["status"] == "stopped"
        assert result["usage"]["model_calls"] == 3
        assert result["usage"]["total_tokens"] == 900
        assert result["usage"]["unknown_usage"] is True
        assert result["content"] is None
