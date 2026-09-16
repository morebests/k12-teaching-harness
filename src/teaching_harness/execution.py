"""跨阶段累计执行证据与 Agent 调用边界；调度和检查点由 LangGraph 管理。"""

import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from langchain.agents.middleware import AgentMiddleware, AgentState
from langchain.agents.middleware.types import ModelRequest, ModelResponse
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage, messages_to_dict

from teaching_harness.content import ContentStore
from teaching_harness.contracts import TaskRequest, fingerprint

WORKFLOW_VERSION = "curriculum-stages-v1"


class ResourceStop(Exception):
    """已触及明确资源／重放边界，保留当前成果。"""


@dataclass
class AgentContext:
    emit: Callable[[Any], None]


class TeachingAgentState(AgentState):
    work: dict[str, Any]


class Ledger:
    """只记录用量和操作证据，不决定图的下一节点。"""

    def __init__(self, work: dict[str, Any]) -> None:
        self.work = work
        self.store = ContentStore(Path(work["root"]), work["task_id"])
        self.limits = TaskRequest.model_validate(work["request"]).limits
        self.stage = work["stage"]
        self.round = work["round"]

    def _update(self, update: Callable[[dict[str, Any]], Any]) -> Any:
        def apply(value: dict[str, Any]) -> Any:
            if not value:
                value.update(
                    workflow_version=WORKFLOW_VERSION,
                    usage={
                        "model_calls": 0,
                        "tool_calls": 0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0,
                        "unknown_usage": False,
                        "cost": None,
                        "seconds": 0.0,
                    },
                    events=[],
                    operations={},
                    active_since=None,
                )
            if value.get("active_since") is not None:
                now = time.time()
                value["usage"]["seconds"] += max(0, now - value["active_since"])
                value["active_since"] = now
            return update(value)

        return self.store.update_record("execution.json", apply)

    def _guard(self, value: dict[str, Any]) -> None:
        usage = value["usage"]
        if value.get("workflow_version") != WORKFLOW_VERSION:
            raise ResourceStop("检测到旧图执行证据，保留累计用量并停止自动重放")
        if usage["seconds"] >= self.limits.seconds:
            raise ResourceStop("达到活动时间上限，已保存的草稿保留")

    def begin_stage(self) -> None:
        def begin(value: dict[str, Any]) -> str | None:
            pending = [
                op for op in value.get("operations", {}).values() if op["status"] == "started"
            ]
            if pending:
                if any(op["kind"] == "model" for op in pending):
                    value["usage"]["unknown_usage"] = True
                return "上次调用结果未确认，停止自动重放；已保存成果和累计消耗保留"
            self._guard(value)
            value["active_since"] = time.time()
            self._event(value, "stage_started")
            return None

        reason = self._update(begin)
        if reason:
            raise ResourceStop(reason)

    def _event(self, value: dict[str, Any], kind: str, **data: Any) -> None:
        value["events"].append({"kind": kind, "stage": self.stage, "round": self.round, **data})

    def record(self, kind: str, **data: Any) -> None:
        self._update(lambda v: self._event(v, kind, **data))

    def end_stage(self) -> None:
        def end(value: dict[str, Any]) -> None:
            self._event(value, "stage_finished")
            value["active_since"] = None

        self._update(end)

    def usage(self) -> dict[str, Any]:
        return self._update(lambda v: dict(v["usage"]))

    def start(self, kind: str, key: str, signature: str) -> dict[str, Any]:
        operation_id = f"{self.stage}/{self.round}/{kind}/{key}"

        def start(value: dict[str, Any]) -> dict[str, Any]:
            self._guard(value)
            previous = value["operations"].get(operation_id)
            if previous:
                if (
                    kind == "tool"
                    and previous["signature"] == signature
                    and previous["status"] == "finished"
                ):
                    return {"cached": previous["result"], "id": operation_id}
                raise ResourceStop("该调用已有执行证据，无法确认检查点交接，停止重复调用")
            usage = value["usage"]
            if self.limits.total_tokens is not None:
                if usage["unknown_usage"]:
                    raise ResourceStop("模型消耗未知，无法核对调用方明确设置的累计 token 阈值")
                if usage["total_tokens"] >= self.limits.total_tokens:
                    raise ResourceStop("已达到调用方设置的累计 token 阈值，停止后续调用")
            if usage[kind + "_calls"] >= getattr(self.limits, kind + "_calls"):
                raise ResourceStop("达到模型调用上限" if kind == "model" else "达到工具调用上限")
            usage[kind + "_calls"] += 1
            value["operations"][operation_id] = {
                "kind": kind,
                "signature": signature,
                "status": "started",
            }
            self._event(value, kind + "_started", operation_id=operation_id, signature=signature)
            return {"id": operation_id}

        return self._update(start)

    def finish(self, operation_id: str, result: Any, usage: dict[str, int] | None = None) -> None:
        def finish(value: dict[str, Any]) -> None:
            op = value["operations"][operation_id]
            if op["kind"] == "model":
                if usage is None:
                    value["usage"]["unknown_usage"] = True
                else:
                    for key in ("input_tokens", "output_tokens", "total_tokens"):
                        value["usage"][key] += usage[key]
            op.update(status="finished", result=result)
            self._event(value, op["kind"] + "_finished", operation_id=operation_id)

        self._update(finish)

    def unfinished(self, operation_id: str) -> None:
        def unfinished(value: dict[str, Any]) -> None:
            op = value["operations"][operation_id]
            if op["kind"] == "model":
                value["usage"]["unknown_usage"] = True
            self._event(value, op["kind"] + "_unfinished", operation_id=operation_id)

        self._update(unfinished)


class ExecutionMiddleware(AgentMiddleware[TeachingAgentState, AgentContext]):
    state_schema = TeachingAgentState

    async def awrap_model_call(
        self,
        request: ModelRequest[AgentContext],
        handler: Callable[[ModelRequest[AgentContext]], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        work = request.state["work"]  # type: ignore[typeddict-item]
        ledger = Ledger(work)
        request = request.override(system_message=SystemMessage(content=work["rules"]))
        signature = fingerprint([work["rules"], messages_to_dict(request.messages)])
        started = await asyncio.to_thread(ledger.start, "model", signature, signature)
        request.runtime.context.emit(
            {"type": "progress", "step": "model", "message": "正在推敲课程或检查实际内容"}
        )
        try:
            result = await handler(request)
        except BaseException:
            await asyncio.to_thread(ledger.unfinished, started["id"])
            raise
        usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
        known = False
        for message in result.result:
            if isinstance(message, AIMessage):
                if not message.usage_metadata:
                    known = False
                    break
                known = True
                for key in usage:
                    usage[key] += message.usage_metadata[key]  # type: ignore[literal-required]
        await asyncio.to_thread(ledger.finish, started["id"], None, usage if known else None)
        return result

    async def awrap_tool_call(self, request: Any, handler: Any) -> Any:
        ledger = Ledger(request.runtime.state["work"])
        call = request.tool_call
        signature = fingerprint([call["name"], call["args"]])
        started = await asyncio.to_thread(ledger.start, "tool", call["id"], signature)
        if "cached" in started:
            return ToolMessage.model_validate(started["cached"])
        request.runtime.context.emit(
            {"type": "progress", "step": call["name"], "message": "正在执行教学工具"}
        )
        try:
            result = await handler(request)
        except (ValueError, ArithmeticError) as exc:
            await asyncio.to_thread(
                ledger.record, "tool_error", tool=call["name"], exception_type=type(exc).__name__
            )
            result = ToolMessage(
                content="工具未完成：" + str(exc),
                tool_call_id=call["id"],
                name=call["name"],
                status="error",
            )
        except BaseException:
            await asyncio.to_thread(ledger.unfinished, started["id"])
            raise
        await asyncio.to_thread(ledger.finish, started["id"], result.model_dump(mode="json"))
        return result
