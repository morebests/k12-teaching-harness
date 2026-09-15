"""课程任务的原生模型循环、独立检查及有限修订。"""

import asyncio
import json
import os
import time
import traceback
from collections.abc import Awaitable, Callable
from importlib.metadata import version
from pathlib import Path
from typing import Any, TypedDict

import httpx
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware
from langchain.agents.middleware.types import ModelRequest, ModelResponse
from langchain.agents.structured_output import ToolStrategy
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph
from langsmith import tracing_context

from teaching_harness.content import ContentStore
from teaching_harness.contracts import Curriculum, Finding, Review, TaskRequest, fingerprint
from teaching_harness.knowledge import Knowledge, Operation
from teaching_harness.mathematics import calculate

RESOURCES = Path(__file__).with_name("resources")


class State(TypedDict, total=False):
    request: dict[str, Any]
    status: str
    unresolved: list[str]
    usage: dict[str, Any]
    content_fingerprint: str | None


class ResourceStop(Exception):
    pass


class Budget(AgentMiddleware):
    def __init__(
        self, request: TaskRequest, store: ContentStore, emit: Callable[[Any], None]
    ) -> None:
        self.limits = request.limits
        self.store = store
        self.emit = emit
        self.start = time.monotonic()
        self.usage: dict[str, Any] = {
            "model_calls": 0,
            "tool_calls": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "unknown_usage": False,
            "cost": None,
            "seconds": 0.0,
        }
        self.events: list[dict[str, Any]] = []

    async def record(self, kind: str, **data: Any) -> None:
        self.usage["seconds"] = round(time.monotonic() - self.start, 3)
        self.events.append({"kind": kind, **data})
        await asyncio.to_thread(
            self.store.record, "execution.json", {"usage": self.usage, "events": self.events}
        )

    def guard(self) -> None:
        if (
            time.monotonic() - self.start >= self.limits.seconds
            or self.usage["total_tokens"] >= self.limits.total_tokens
        ):
            raise ResourceStop("达到运行资源上限，已保存的草稿保留")

    async def awrap_model_call(
        self, request: ModelRequest, handler: Callable[[ModelRequest], Awaitable[ModelResponse]]
    ) -> ModelResponse:
        self.guard()
        if self.usage["model_calls"] >= self.limits.model_calls:
            raise ResourceStop("达到模型调用上限")
        # 以 UTF-8 字节作保守输入预留，含消息、规则和工具 Schema；供应商实际消耗另记。
        reserve = (
            len(str([request.system_message, request.messages, request.tools]).encode()) + 2048
        )
        remaining = self.limits.total_tokens - self.usage["total_tokens"] - reserve
        if remaining < 512 or self.usage["unknown_usage"]:
            raise ResourceStop("剩余 token 不足以安全发起下一调用，或上次消耗未知")
        request = request.override(
            model_settings={**request.model_settings, "max_output_tokens": min(16000, remaining)}
        )
        self.usage["model_calls"] += 1
        self.emit({"type": "progress", "step": "model", "message": "正在推敲课程或检查实际内容"})
        await self.record("model_started", call=self.usage["model_calls"])
        try:
            result = await handler(request)
        except BaseException:
            self.usage["unknown_usage"] = True
            await self.record("model_unfinished", call=self.usage["model_calls"])
            raise
        for message in result.result:
            if isinstance(message, AIMessage) and message.usage_metadata:
                for key in ("input_tokens", "output_tokens", "total_tokens"):
                    self.usage[key] += message.usage_metadata[key]
            elif isinstance(message, AIMessage):
                self.usage["unknown_usage"] = True
        await self.record("model_finished", call=self.usage["model_calls"])
        return result

    async def awrap_tool_call(self, request: Any, handler: Any) -> Any:
        try:
            return await handler(request)
        except (ValueError, ArithmeticError) as exc:
            # 参数／引用错误交回模型修复，资源停止与取消不转成可继续的工具回复。
            await self.record(
                "tool_error", tool=request.tool_call["name"], exception_type=type(exc).__name__
            )
            return ToolMessage(
                content="工具未完成：" + str(exc), tool_call_id=request.tool_call["id"]
            )

    async def tool_started(self, name: str) -> None:
        self.guard()
        if self.usage["tool_calls"] >= self.limits.tool_calls:
            raise ResourceStop("达到工具调用上限")
        self.usage["tool_calls"] += 1
        self.emit({"type": "progress", "step": name, "message": "正在执行教学工具"})
        await self.record("tool_started", tool=name)


def deterministic_findings(content: Curriculum, request: TaskRequest) -> list[Finding]:
    findings = []
    if {g.code for g in content.goals} != set(request.target_codes):
        findings.append(
            Finding(
                criterion="coverage", target="goals", detail="目标集合与本次请求不同", blocking=True
            )
        )
    if len(content.lessons) != request.school.lesson_count:
        findings.append(
            Finding(
                criterion="conditions",
                target="lessons",
                detail="课时数量与已给条件不同",
                blocking=True,
            )
        )
    for lesson in content.lessons:
        if (
            lesson.student_minutes + lesson.discussion_minutes + lesson.other_minutes
            > request.school.minutes_per_lesson
        ):
            findings.append(
                Finding(
                    criterion="conditions",
                    target=lesson.title,
                    detail="学生工作、讨论与其他时间超过课时预算",
                    blocking=True,
                )
            )
    return findings


def build_graph(
    model_factory: Callable[[], BaseChatModel],
    knowledge_factory: Callable[[httpx.AsyncClient], Knowledge] = Knowledge,
) -> Any:
    async def execute(state: State, config: RunnableConfig) -> dict[str, Any]:
        request = TaskRequest.model_validate(state["request"])
        tid = config["configurable"]["thread_id"]
        store = await asyncio.to_thread(
            ContentStore, Path(os.environ.get("HARNESS_WORK_DIR", "work")), tid
        )
        emit = get_stream_writer()
        budget = Budget(request, store, emit)
        rules = await asyncio.to_thread((RESOURCES / "curriculum.md").read_text)
        review_rules = await asyncio.to_thread((RESOURCES / "review.md").read_text)
        manifest = {
            "request_fingerprint": fingerprint(request.model_dump()),
            "rules": {
                "curriculum": fingerprint(rules),
                "review": fingerprint(review_rules),
            },
            "external_content": [x.model_dump() for x in request.external_content],
            "identity": config["configurable"].get("langgraph_auth_user", {}).get("identity"),
            "versions": {
                name: version(name)
                for name in [
                    "k12-teaching-harness",
                    "langchain",
                    "langgraph",
                    "langgraph-api",
                    "langchain-google-genai",
                ]
            },
            "model": os.environ.get("HARNESS_MODEL", "gemini-3.8-flash"),
            "tools_version": 1,
        }
        await asyncio.to_thread(store.record, "context.json", manifest)
        status, unresolved = "incomplete", []
        try:
            async with (
                asyncio.timeout(request.limits.seconds),
                httpx.AsyncClient(
                    base_url=os.environ.get("HARNESS_LC_URL", "http://127.0.0.1:8000"), timeout=30
                ) as http,
            ):
                knowledge = knowledge_factory(http)
                emit(
                    {
                        "type": "progress",
                        "step": "knowledge",
                        "message": "正在核对本次 CCSS、组件与前后联系",
                    }
                )
                try:
                    package = await knowledge.prepare(request.target_codes)
                except Exception:  # noqa: BLE001 — 失败仍保存已完成的来源查询，随后交给任务边界。
                    await asyncio.to_thread(
                        store.record, "knowledge.json", {"audit": knowledge.audit}
                    )
                    raise
                await asyncio.to_thread(
                    store.record, "knowledge.json", {"package": package, "audit": knowledge.audit}
                )
                manifest.update(
                    knowledge_fingerprint=fingerprint(package),
                    source_snapshot=knowledge.identity,
                )
                await asyncio.to_thread(store.record, "context.json", manifest)

                @tool
                async def browse(code: str, operation: Operation) -> dict[str, Any]:
                    """读取真实 CCSS 原文、支持组件、前驱或后继；不能查询课程材料。"""
                    await budget.tool_started("browse")
                    result = await knowledge.lookup(code, operation)
                    await asyncio.to_thread(
                        store.record,
                        "knowledge.json",
                        {
                            "package": package,
                            "additional": knowledge.records,
                            "audit": knowledge.audit,
                        },
                    )
                    await budget.record(
                        "tool_finished", tool="browse", result_fingerprint=fingerprint(result)
                    )
                    return result

                @tool
                async def calculate_math(expression: str) -> str:
                    """用有理数核对有限加减乘除和整数幂，例如 (23-11)/(6-2)。"""
                    await budget.tool_started("calculate")
                    result = calculate(expression)
                    await budget.record(
                        "tool_finished", tool="calculate", expression=expression, result=result
                    )
                    return result

                @tool
                async def read_curriculum() -> dict[str, Any]:
                    """读取当前实际课程与指纹；当前无内容时 fingerprint 为 null。"""
                    await budget.tool_started("read_curriculum")
                    return await asyncio.to_thread(store.snapshot)

                @tool
                async def save_curriculum(
                    content: Curriculum, expected_fingerprint: str | None
                ) -> dict[str, Any]:
                    """保存完整当前课段草稿；须用刚读取的指纹，首次保存用 null。"""
                    await budget.tool_started("save_curriculum")
                    result = await asyncio.to_thread(store.save, content, expected_fingerprint)
                    emit(
                        {
                            "type": "draft",
                            "checked": False,
                            "fingerprint": result["fingerprint"],
                            "content": content.model_dump(),
                        }
                    )
                    await budget.record(
                        "tool_finished",
                        tool="save_curriculum",
                        content_fingerprint=result["fingerprint"],
                    )
                    return {
                        "fingerprint": result["fingerprint"],
                        "rendered": result.get("rendered", False),
                        "message": "当前草稿已保存，尚未通过检查；rendered=false 时需修复排版",
                    }

                model = await asyncio.to_thread(model_factory)

                @tool
                async def plot_linear(
                    name: str,
                    slope: float,
                    intercept: float,
                    x_max: float,
                    y_max: float,
                    x_label: str,
                    y_label: str,
                    expected_fingerprint: str | None = None,
                ) -> dict[str, Any]:
                    """绘制第一象限内 y=slope*x+intercept 的真实 SVG，图含坐标刻度与单位。"""
                    await budget.tool_started("plot_linear")
                    result = await asyncio.to_thread(
                        store.plot_linear,
                        name,
                        slope=slope,
                        intercept=intercept,
                        x_max=x_max,
                        y_max=y_max,
                        x_label=x_label,
                        y_label=y_label,
                        expected_fingerprint=expected_fingerprint,
                    )
                    await budget.record("tool_finished", tool="plot_linear", **result)
                    return result

                tools = [browse, calculate_math, read_curriculum, save_curriculum, plot_linear]
                author = create_agent(model, tools, system_prompt=rules, middleware=[budget])
                reviewer = create_agent(
                    model,
                    [calculate_math],
                    system_prompt=review_rules,
                    response_format=ToolStrategy(Review),
                    middleware=[budget],
                )
                feedback: dict[str, Any] | None = None
                while True:
                    budget.guard()
                    current = await asyncio.to_thread(store.snapshot)
                    message = {
                        "request": request.model_dump(),
                        "knowledge": package,
                        "current": current,
                        "review_feedback": feedback,
                    }
                    # 独立审阅不带生成对话，且当前关闭内容上报；平台 trace 在后续票验证。
                    with tracing_context(enabled=False):
                        await author.ainvoke(
                            {
                                "messages": [
                                    {
                                        "role": "user",
                                        "content": json.dumps(message, ensure_ascii=False),
                                    }
                                ]
                            },
                            config={"recursion_limit": 500},
                        )
                    current = await asyncio.to_thread(store.snapshot)
                    if current["content"] is None:
                        raise ResourceStop("模型尚未保存实际课程，不能宣称完成")
                    emit(
                        {
                            "type": "progress",
                            "step": "check",
                            "message": "正在独立核对数学、目标与课堂条件",
                        }
                    )
                    with tracing_context(enabled=False):
                        checked = await reviewer.ainvoke(
                            {
                                "messages": [
                                    {
                                        "role": "user",
                                        "content": json.dumps(
                                            {
                                                "request": request.model_dump(),
                                                "knowledge": package,
                                                "content": current["content"],
                                                "assets": await asyncio.to_thread(
                                                    store.review_assets
                                                ),
                                            },
                                            ensure_ascii=False,
                                        ),
                                    }
                                ]
                            },
                            config={"recursion_limit": 500},
                        )
                    review = Review.model_validate(checked["structured_response"])
                    review.findings.extend(
                        deterministic_findings(
                            Curriculum.model_validate(current["content"]), request
                        )
                    )
                    if not current.get("rendered"):
                        review.findings.append(
                            Finding(
                                criterion="mathematics",
                                target="rendering",
                                detail="当前内容未成功排版，核对公式或图件",
                                blocking=True,
                            )
                        )
                    current = await asyncio.to_thread(
                        store.check, current["fingerprint"], review, fingerprint(review_rules)
                    )
                    await budget.record(
                        "review_finished",
                        fingerprint=current["fingerprint"],
                        findings=review.model_dump()["findings"],
                    )
                    if current["checks"]["passed"]:
                        status = "completed"
                        break
                    feedback = review.model_dump()
                    unresolved = [f.detail for f in review.findings if f.blocking]
                    emit(
                        {
                            "type": "progress",
                            "step": "revision",
                            "message": "正在核实检查问题并修订当前稿",
                        }
                    )
        except (ResourceStop, TimeoutError) as exc:
            status, unresolved = "stopped", [*unresolved, str(exc) or "达到活动时间上限"]
        except asyncio.CancelledError:
            await budget.record("cancelled")
            raise
        except Exception as exc:  # noqa: BLE001 — 任务边界保存外部模型／知识故障，绝不提升为成功。
            # 外部异常文本可能包含请求和凭据；只返回类别与通用说明。
            status, unresolved = (
                "failed",
                [f"{type(exc).__name__}：执行失败，当前工作已保留，请核对知识或模型配置"],
            )
            await budget.record(
                "failure",
                exception_type=type(exc).__name__,
                locations=[
                    {
                        "file": Path(frame.filename).name,
                        "line": frame.lineno,
                        "function": frame.name,
                    }
                    for frame in traceback.extract_tb(exc.__traceback__)
                ],
            )
        finally:
            await budget.record("work_finished")
        current = await asyncio.to_thread(store.snapshot)
        result = {
            "status": status,
            "unresolved": [] if status == "completed" else unresolved,
            "usage": budget.usage,
            "content_fingerprint": current["fingerprint"],
        }
        emit({"type": "result", **result})
        return result

    builder = StateGraph(State)
    builder.add_node("curriculum_work", execute)
    builder.add_edge(START, "curriculum_work")
    builder.add_edge("curriculum_work", END)
    return builder.compile()


def gemini() -> BaseChatModel:
    return ChatGoogleGenerativeAI(
        model=os.environ.get("HARNESS_MODEL", "gemini-3.8-flash"),
        api_key=os.environ.get("GEMINI_API_KEY"),
        max_retries=0,
        max_output_tokens=16000,
        timeout=120,
    )


graph = build_graph(gemini)
