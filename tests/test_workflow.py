"""通过 LangGraph 公共检查点接口验证阶段交接；外部依赖使用可控模型与知识。"""

import asyncio
import json
from uuid import uuid4

import pytest
from fake_graph import TestKnowledge as ControlledKnowledge
from fake_graph import TestModel as ControlledModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import Field, PrivateAttr

from teaching_harness.content import ContentStore
from teaching_harness.contracts import Curriculum, Review, fingerprint
from teaching_harness.graph import build_graph


@pytest.mark.parametrize("token_limit", [None, 1000])
async def test_累计token只计量且仅在调用方明确设限时停止(
    tmp_path, monkeypatch, request_data, token_limit
):
    monkeypatch.setenv("HARNESS_WORK_DIR", str(tmp_path))
    request_data["limits"].pop("total_tokens")
    if token_limit is not None:
        request_data["limits"]["total_tokens"] = token_limit

    class LargeUsageModel(ControlledModel):
        def _generate(self, messages, **kwargs):
            result = super()._generate(messages, **kwargs)
            result.generations[0].message.usage_metadata = {
                "input_tokens": 2900000,
                "output_tokens": 100000,
                "total_tokens": 3000000,
            }
            return result

    graph = build_graph(LargeUsageModel, ControlledKnowledge)
    result = await graph.ainvoke(
        {"request": request_data}, {"configurable": {"thread_id": str(uuid4())}}
    )
    assert result["status"] == ("completed" if token_limit is None else "stopped")
    assert result["usage"]["model_calls"] == (4 if token_limit is None else 1)
    assert result["usage"]["total_tokens"] == (12000000 if token_limit is None else 3000000)


async def test_作者完成后可从送审继续而不重复生成(tmp_path, monkeypatch, request_data):
    monkeypatch.setenv("HARNESS_WORK_DIR", str(tmp_path))
    graph = build_graph(ControlledModel, ControlledKnowledge)
    assert {name for name, _ in graph.get_subgraphs()} == {"author", "reviewer"}
    graph.checkpointer = InMemorySaver()
    config = {"configurable": {"thread_id": str(uuid4())}}
    paused = await graph.ainvoke(
        {"request": request_data}, config, interrupt_after=["author"], durability="sync"
    )
    assert "messages" not in paused
    state = await graph.aget_state(config, subgraphs=True)
    assert state.next == ("prepare_review",)
    assert paused["usage"]["model_calls"] == 3
    result = await graph.ainvoke(None, config, durability="sync")
    assert result["status"] == "completed"
    assert result["usage"]["model_calls"] == 4
    assert "messages" not in result


async def test_最后审阅越过显式token阈值仍提交已完成的检查(tmp_path, monkeypatch, request_data):
    monkeypatch.setenv("HARNESS_WORK_DIR", str(tmp_path))
    request_data["limits"]["total_tokens"] = 1000

    class ReviewUsageModel(ControlledModel):
        def _generate(self, messages, **kwargs):
            result = super()._generate(messages, **kwargs)
            if str(messages[0].content).startswith("# 有限课段检查规则"):
                result.generations[0].message.usage_metadata = {
                    "input_tokens": 900,
                    "output_tokens": 100,
                    "total_tokens": 1000,
                }
            return result

    graph = build_graph(ReviewUsageModel, ControlledKnowledge)
    tid = str(uuid4())
    result = await graph.ainvoke({"request": request_data}, {"configurable": {"thread_id": tid}})
    assert result["status"] == "completed"
    assert result["usage"]["total_tokens"] == 1060
    assert ContentStore(tmp_path, tid).snapshot()["checks"]["passed"]


@pytest.mark.parametrize("changed", [False, True])
async def test_审阅后续作只提交同一版本检查(tmp_path, monkeypatch, request_data, changed):
    monkeypatch.setenv("HARNESS_WORK_DIR", str(tmp_path))
    graph = build_graph(ControlledModel, ControlledKnowledge)
    graph.checkpointer = InMemorySaver()
    tid = str(uuid4())
    config = {"configurable": {"thread_id": tid}}
    paused = await graph.ainvoke({"request": request_data}, config, interrupt_after=["reviewer"])
    assert (await graph.aget_state(config)).next == ("record_review",)
    assert paused["usage"]["model_calls"] == 4
    if changed:
        store = ContentStore(tmp_path, tid)
        snapshot = store.snapshot()
        content = Curriculum.model_validate(snapshot["content"])
        content.narrative += "外部修改后的叙述。"
        store.save(content, snapshot["fingerprint"])
    result = await graph.ainvoke(None, config)
    assert result["status"] == ("incomplete" if changed else "completed")
    assert result["usage"]["model_calls"] == 4
    if changed:
        assert ContentStore(tmp_path, tid).snapshot()["checks"] is None


async def test_送审后图件引用损坏仍可保留未完成结果(tmp_path, monkeypatch, request_data):
    monkeypatch.setenv("HARNESS_WORK_DIR", str(tmp_path))
    graph = build_graph(ControlledModel, ControlledKnowledge)
    graph.checkpointer = InMemorySaver()
    tid = str(uuid4())
    config = {"configurable": {"thread_id": tid}}
    await graph.ainvoke({"request": request_data}, config, interrupt_after=["reviewer"])
    path = tmp_path / tid / "content/curriculum.json"
    content = json.loads(path.read_text())
    content["tasks"][0]["blocks"] = [
        {"type": "image", "src": "assets/missing.svg", "alt": "缺失图"}
    ]
    path.write_text(json.dumps(content))
    result = await graph.ainvoke(None, config)
    assert result["status"] == "incomplete"
    assert result["content_fingerprint"] is None
    assert result["usage"]["model_calls"] == 4
    assert "图件" in "".join(result["unresolved"])


async def test_检查文件先于检查点保存时幂等提交(tmp_path, monkeypatch, request_data):
    monkeypatch.setenv("HARNESS_WORK_DIR", str(tmp_path))
    graph = build_graph(ControlledModel, ControlledKnowledge)
    graph.checkpointer = InMemorySaver()
    tid = str(uuid4())
    config = {"configurable": {"thread_id": tid}}
    paused = await graph.ainvoke({"request": request_data}, config, interrupt_after=["reviewer"])
    store = ContentStore(tmp_path, tid)
    checked = store.check(
        paused["review_input"]["fingerprint"],
        Review.model_validate(paused["review_result"]),
        fingerprint(paused["prepared_context"]["rules"]["review"]),
    )
    result = await graph.ainvoke(None, config)
    assert result["status"] == "completed"
    assert result["usage"]["model_calls"] == 4
    assert store.snapshot()["checks"] == checked["checks"]


async def test_已固定依据的检查点跨构图继续不重新查询知识(tmp_path, monkeypatch, request_data):
    monkeypatch.setenv("HARNESS_WORK_DIR", str(tmp_path))
    saver = InMemorySaver()
    graph = build_graph(ControlledModel, ControlledKnowledge)
    graph.checkpointer = saver
    config = {"configurable": {"thread_id": str(uuid4())}}
    prepared = await graph.ainvoke(
        {"request": request_data}, config, interrupt_after=["prepare_task"]
    )

    class UnavailableKnowledge(ControlledKnowledge):
        async def prepare(self, targets):
            raise RuntimeError("知识服务已经不可用，不应重新查取")

    resumed = build_graph(ControlledModel, UnavailableKnowledge)
    resumed.checkpointer = saver
    result = await resumed.ainvoke(None, config)
    assert result["status"] == "completed"
    assert result["prepared_context"] == prepared["prepared_context"]


class SupplementaryModel(ControlledModel):
    review_knowledge: dict = Field(default_factory=dict)

    def _generate(self, messages, **kwargs):
        review = str(messages[0].content).startswith("# 有限课段检查规则")
        if review:
            self.review_knowledge = json.loads(messages[1].content)["knowledge"]
        elif len(messages) == 2:
            return ChatResult(
                generations=[
                    ChatGeneration(
                        message=AIMessage(
                            content="",
                            tool_calls=[
                                {
                                    "name": "browse",
                                    "id": "supplement",
                                    "args": {"code": "7.RP.A.2", "operation": "standard"},
                                }
                            ],
                            usage_metadata={
                                "input_tokens": 10,
                                "output_tokens": 10,
                                "total_tokens": 20,
                            },
                        )
                    )
                ]
            )
        return super()._generate(messages, **kwargs)


class SupplementaryKnowledge(ControlledKnowledge):
    async def lookup(self, code, operation):
        assert self.identity == {"namespace": "test", "version": "1"}
        result = {
            "code": code,
            "operation": operation,
            "source_snapshot": self.identity,
            "standard": "用于本次补查交接测试的比例关系标准",
        }
        self.records.append(result)
        return result


async def test_作者补查的固定版本依据进入独立送审输入(tmp_path, monkeypatch, request_data):
    monkeypatch.setenv("HARNESS_WORK_DIR", str(tmp_path))
    model = SupplementaryModel()
    graph = build_graph(lambda: model, SupplementaryKnowledge)
    result = await graph.ainvoke(
        {"request": request_data}, {"configurable": {"thread_id": str(uuid4())}}
    )
    assert result["status"] == "completed"
    assert model.review_knowledge["additional"][0]["code"] == "7.RP.A.2"


class RevisingModel(ControlledModel):
    reviews: int = 0
    author_inputs: list[dict] = Field(default_factory=list)

    def _generate(self, messages, **kwargs):
        review = str(messages[0].content).startswith("# 有限课段检查规则")
        result = super()._generate(messages, **kwargs)
        message = result.generations[0].message
        payload = json.loads(messages[1].content)
        if review:
            self.reviews += 1
            assert "review_feedback" not in payload
            assert len(messages) == 2
            if self.reviews == 1:
                message.tool_calls[0]["args"]["findings"] = [
                    {
                        "criterion": "evidence",
                        "target": "tank",
                        "detail": "补充水箱任务的解题说明",
                        "blocking": True,
                    }
                ]
        elif len(messages) == 2:
            self.author_inputs.append(payload)
        elif payload.get("review_feedback"):
            for call in message.tool_calls:
                if call["name"] == "save_curriculum":
                    call["args"]["content"]["tasks"][0]["solution"] += "代入两组数据均成立。"
        return result


async def test_阻断检查通过条件边修订且每轮消息独立(tmp_path, monkeypatch, request_data):
    monkeypatch.setenv("HARNESS_WORK_DIR", str(tmp_path))
    model = RevisingModel()
    graph = build_graph(lambda: model, ControlledKnowledge)
    graph.checkpointer = InMemorySaver()
    result = await graph.ainvoke(
        {"request": request_data}, {"configurable": {"thread_id": str(uuid4())}}
    )
    assert result["status"] == "completed"
    assert result["round_index"] == 1
    assert result["usage"]["model_calls"] == 8
    assert model.reviews == 2 and len(model.author_inputs) == 2
    assert model.author_inputs[0]["review_feedback"] is None
    assert model.author_inputs[1]["review_feedback"]["findings"][0]["blocking"]


class UnfinishedModel(ControlledModel):
    calls: int = 0
    _started: asyncio.Event = PrivateAttr(default_factory=asyncio.Event)

    async def _agenerate(self, messages, **kwargs):
        self.calls += 1
        self._started.set()
        await asyncio.Event().wait()


async def test_未知模型消耗恢复时停止而不重复调用(tmp_path, monkeypatch, request_data):
    monkeypatch.setenv("HARNESS_WORK_DIR", str(tmp_path))
    model = UnfinishedModel()
    graph = build_graph(lambda: model, ControlledKnowledge)
    graph.checkpointer = InMemorySaver()
    config = {"configurable": {"thread_id": str(uuid4())}}
    running = asyncio.create_task(graph.ainvoke({"request": request_data}, config))
    await asyncio.wait_for(model._started.wait(), timeout=5)
    running.cancel()
    with pytest.raises(asyncio.CancelledError):
        await running
    result = await graph.ainvoke(None, config)
    assert result["status"] == "stopped"
    assert result["usage"]["unknown_usage"]
    assert result["usage"]["model_calls"] == model.calls == 1


class ParallelModel(ControlledModel):
    def _generate(self, messages, **kwargs):
        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(
                        content="",
                        tool_calls=[
                            {
                                "name": "calculate_math",
                                "id": f"parallel-{i}",
                                "args": {"expression": "1+1"},
                            }
                            for i in range(4)
                        ],
                        usage_metadata={
                            "input_tokens": 10,
                            "output_tokens": 10,
                            "total_tokens": 20,
                        },
                    )
                )
            ]
        )


async def test_同轮并行工具共享额度不会超额或丢失计量(tmp_path, monkeypatch, request_data):
    monkeypatch.setenv("HARNESS_WORK_DIR", str(tmp_path))
    request_data["limits"]["tool_calls"] = 2
    graph = build_graph(ParallelModel, ControlledKnowledge)
    result = await graph.ainvoke(
        {"request": request_data}, {"configurable": {"thread_id": str(uuid4())}}
    )
    assert result["status"] == "stopped"
    assert result["usage"]["model_calls"] == 1
    assert result["usage"]["tool_calls"] == 2
