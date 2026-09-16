"""LangGraph 编排课程阶段；生成和独立审阅各使用一个静态 Agent 子图。"""

import asyncio
import json
import os
import traceback
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from importlib.metadata import version
from pathlib import Path
from typing import Any, TypedDict

import httpx
from langchain.agents import create_agent
from langchain.agents.middleware.types import InputAgentState
from langchain.agents.structured_output import ToolStrategy
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph

from teaching_harness.content import ContentError
from teaching_harness.contracts import (
    Curriculum,
    Finding,
    Review,
    TaskRequest,
    YearBlueprint,
    fingerprint,
    parse_content,
)
from teaching_harness.curriculum_tools import author_tools, calculate_math
from teaching_harness.execution import (
    WORKFLOW_VERSION,
    AgentContext,
    ExecutionMiddleware,
    Ledger,
    ResourceStop,
)
from teaching_harness.knowledge import Knowledge
from teaching_harness.year import check_year

RESOURCES = Path(__file__).with_name("resources")


def rule_files(scope: str) -> list[tuple[str, str]]:
    return (
        [("curriculum", "year.md"), ("review", "year-review.md")]
        if scope == "year"
        else [("curriculum", "curriculum.md"), ("review", "review.md")]
    )


class State(TypedDict, total=False):
    request: dict[str, Any]
    request_fingerprint: str
    workflow_version: str
    prepared_context: dict[str, Any]
    round_index: int
    candidate_ref: str | None
    review_input: dict[str, Any]
    program_findings: list[dict[str, Any]]
    review_result: dict[str, Any]
    feedback: dict[str, Any] | None
    previous_review_ref: str
    status: str
    unresolved: list[str]
    usage: dict[str, Any]
    content_fingerprint: str | None
    stop_reason: str | None


def work(state: State, config: RunnableConfig, stage: str, root: Path) -> dict[str, Any]:
    context = state.get("prepared_context", {})
    return {
        "root": context.get("root", str(root)),
        "task_id": config["configurable"]["thread_id"],
        "request": state["request"],
        "stage": stage,
        "round": state.get("round_index", 0),
        "rules": context.get("rules", {}).get(
            "review" if stage == "reviewer" else "curriculum", ""
        ),
        "knowledge_source": context.get("knowledge_source", {}),
    }


def stopped(exc: Exception, status: str = "stopped") -> dict[str, Any]:
    reason = str(exc) or "达到活动时间上限"
    return {"status": status, "stop_reason": reason, "unresolved": [reason]}


@asynccontextmanager
async def stage(ledger: Ledger) -> AsyncIterator[None]:
    """节点边界记活动时间；取消与故障继续交给原生 run 处理。"""
    try:
        await asyncio.to_thread(ledger.begin_stage)
        get_stream_writer()(
            {
                "type": "progress",
                "step": ledger.stage,
                "message": {
                    "prepare_task": "正在核对本次 CCSS、组件与前后联系",
                    "author": "正在生成或修订当前课程方案",
                    "prepare_review": "正在固定实际送审内容",
                    "reviewer": "正在独立核对数学、目标与课堂条件",
                    "record_review": "正在核对版本并提交检查",
                }[ledger.stage],
            }
        )
        usage = await asyncio.to_thread(ledger.usage)
        async with asyncio.timeout(max(0, ledger.limits.seconds - usage["seconds"])):
            yield
    except (ResourceStop, TimeoutError, ContentError):
        raise
    except asyncio.CancelledError:
        await asyncio.to_thread(ledger.record, "cancelled")
        raise
    except Exception as exc:  # noqa: BLE001 — 记录安全故障位置后保留原生失败状态。
        await asyncio.to_thread(
            ledger.record,
            "failure",
            exception_type=type(exc).__name__,
            locations=[
                {"file": Path(f.filename).name, "line": f.lineno, "function": f.name}
                for f in traceback.extract_tb(exc.__traceback__)
            ],
        )
        # 原生状态仍为 error；外部异常文本可能含供应商请求和凭据。
        raise RuntimeError(
            f"{type(exc).__name__}：执行失败，当前工作已保留，请核对知识或模型配置"
        ) from None
    finally:
        await asyncio.to_thread(ledger.end_stage)


class TeachingAgentInput(InputAgentState):
    work: dict[str, Any]


def agent_input(
    state: State, config: RunnableConfig, name: str, payload: dict[str, Any], root: Path
) -> TeachingAgentInput:
    return {
        "work": work(state, config, name, root),
        "messages": [HumanMessage(content=json.dumps(payload, ensure_ascii=False))],
    }


async def final_result(state: State, ledger: Ledger) -> dict[str, Any]:
    await asyncio.to_thread(ledger.record, "work_finished")
    unresolved = list(state.get("unresolved", []))
    status = state.get("status", "incomplete")
    stop_reason = state.get("stop_reason")
    try:
        content_fingerprint = (await asyncio.to_thread(ledger.store.snapshot))["fingerprint"]
    except ContentError as exc:
        # 停止出口不修复文件；损坏的引用不能把已判定的未完成结果再变成异常。
        content_fingerprint = None
        status = "incomplete"
        stop_reason = str(exc)
        if str(exc) not in unresolved:
            unresolved.append(str(exc))
    result = {
        "status": status,
        "unresolved": unresolved,
        "usage": await asyncio.to_thread(ledger.usage),
        "content_fingerprint": content_fingerprint,
        "stop_reason": stop_reason,
    }
    get_stream_writer()({"type": "result", **result})
    return result


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


def gemini() -> BaseChatModel:
    return ChatGoogleGenerativeAI(
        model=os.environ.get("HARNESS_MODEL", "gemini-3.8-flash"),
        api_key=os.environ.get("GEMINI_API_KEY"),
        max_retries=0,
        max_output_tokens=32768,
        timeout=120,
    )


def build_graph(
    model_factory: Callable[[], BaseChatModel],
    knowledge_factory: Callable[[httpx.AsyncClient], Knowledge] = Knowledge,
) -> Any:
    root = Path(os.environ.get("HARNESS_WORK_DIR", "work")).resolve()
    model = model_factory()
    author_agent = create_agent(
        model,
        author_tools(knowledge_factory),
        middleware=[ExecutionMiddleware()],
        context_schema=AgentContext,
        name="curriculum_author",
    )
    reviewer_agent = create_agent(
        model,
        [calculate_math],
        middleware=[ExecutionMiddleware()],
        context_schema=AgentContext,
        response_format=ToolStrategy(Review),
        name="curriculum_reviewer",
    )

    async def prepare_task(state: State, config: RunnableConfig) -> dict[str, Any]:
        request = TaskRequest.model_validate(state["request"])
        ledger = Ledger(work(state, config, "prepare_task", root))
        try:
            async with stage(ledger):
                evidence = await asyncio.to_thread(ledger.store.evidence)
                previous = evidence.get("context")
                request_fp = fingerprint(request.model_dump())
                if previous and previous.get("request_fingerprint") != request_fp:
                    raise ResourceStop("任务请求与已有执行证据不一致")
                if previous and previous.get("prepared_context"):
                    prepared = previous["prepared_context"]
                else:
                    rules = {
                        name: await asyncio.to_thread((RESOURCES / file).read_text)
                        for name, file in rule_files(request.scope)
                    }
                    async with httpx.AsyncClient(
                        base_url=os.environ.get("HARNESS_LC_URL", "http://127.0.0.1:8000"),
                        timeout=30,
                    ) as http:
                        knowledge = knowledge_factory(http)
                        try:
                            package = (
                                await knowledge.prepare_year(request.grade)
                                if request.scope == "year"
                                else await knowledge.prepare(request.target_codes)
                            )
                        finally:
                            await asyncio.to_thread(
                                ledger.store.update_record,
                                "knowledge.json",
                                lambda v: v.update(
                                    audit=knowledge.audit, preparation=knowledge.preparation
                                ),
                            )
                    await asyncio.to_thread(
                        ledger.store.record,
                        "knowledge.json",
                        {
                            "package": package,
                            "audit": knowledge.audit,
                            "preparation": knowledge.preparation,
                        },
                    )
                    prepared = {
                        "root": ledger.work["root"],
                        "rules": rules,
                        "knowledge": package,
                        "knowledge_source": {
                            "identity": knowledge.identity,
                            "framework": knowledge.framework,
                            "snapshot_id": knowledge.snapshot_id,
                        },
                    }
                    manifest = {
                        "workflow_version": WORKFLOW_VERSION,
                        "request_fingerprint": request_fp,
                        "rules": {name: fingerprint(text) for name, text in rules.items()},
                        "external_content": [x.model_dump() for x in request.external_content],
                        "identity": config["configurable"]
                        .get("langgraph_auth_user", {})
                        .get("identity"),
                        "versions": {
                            name: await asyncio.to_thread(version, name)
                            for name in [
                                "k12-teaching-harness",
                                "langchain",
                                "langgraph",
                                "langgraph-api",
                                "langchain-google-genai",
                            ]
                        },
                        "model": os.environ.get("HARNESS_MODEL", "gemini-3.8-flash"),
                        "tools_version": 3,
                        "source_snapshot": knowledge.identity,
                        "knowledge_fingerprint": fingerprint(package),
                        "prepared_context": prepared,
                    }
                    await asyncio.to_thread(ledger.store.record, "context.json", manifest)
            return {
                "workflow_version": WORKFLOW_VERSION,
                "request_fingerprint": request_fp,
                "prepared_context": prepared,
                "round_index": 0,
                "status": "running",
                "unresolved": [],
                "stop_reason": None,
                "usage": await asyncio.to_thread(ledger.usage),
            }
        except (ResourceStop, TimeoutError) as exc:
            return stopped(exc)

    async def author(state: State, config: RunnableConfig) -> dict[str, Any]:
        ledger = Ledger(work(state, config, "author", root))
        try:
            async with stage(ledger):
                current = await asyncio.to_thread(ledger.store.snapshot)
                await author_agent.ainvoke(
                    agent_input(
                        state,
                        config,
                        "author",
                        {
                            "request": state["request"],
                            "knowledge": state.get("review_input", {}).get(
                                "knowledge", state["prepared_context"]["knowledge"]
                            ),
                            "current": current,
                            "review_feedback": state.get("feedback"),
                        },
                        root,
                    ),
                    config=RunnableConfig(
                        **{**config, "recursion_limit": 500, "run_name": "curriculum_author"}
                    ),
                    context=AgentContext(get_stream_writer()),
                )
                current = await asyncio.to_thread(ledger.store.snapshot)
                if current["content"] is None:
                    return stopped(ResourceStop("模型尚未保存实际课程，不能宣称完成"), "incomplete")
            return {
                "candidate_ref": current["fingerprint"],
                "content_fingerprint": current["fingerprint"],
                "usage": await asyncio.to_thread(ledger.usage),
            }
        except (ResourceStop, TimeoutError) as exc:
            return stopped(exc)
        except ContentError as exc:
            return stopped(exc, "incomplete")

    async def prepare_review(state: State, config: RunnableConfig) -> dict[str, Any]:
        ledger = Ledger(work(state, config, "prepare_review", root))
        try:
            async with stage(ledger):
                current = await asyncio.to_thread(ledger.store.review_input)
                current["knowledge"] = {
                    **state["prepared_context"]["knowledge"],
                    "additional": current["knowledge"].get("additional", []),
                }
                if current["fingerprint"] != state["candidate_ref"]:
                    raise ContentError("候选稿在送审前已改变，停止本次检查")
                content = parse_content(current["content"])
                request = TaskRequest.model_validate(state["request"])
                if (request.scope == "year") != isinstance(content, YearBlueprint):
                    raise ContentError("候选内容层级与本次任务不符")
                findings = (
                    check_year(content, request, current["knowledge"])
                    if isinstance(content, YearBlueprint)
                    else deterministic_findings(content, request)
                )
                if not current.get("rendered"):
                    errors = current.get("render_errors") or [
                        {"location": "rendering", "message": "当前阅读稿缺失或已不适用于当前源"}
                    ]
                    findings.extend(
                        Finding(
                            criterion="mathematics",
                            target=error["location"],
                            detail="当前阅读稿未生成，修复后重新保存："
                            + error["message"]
                            + (
                                "；公式：" + error["formula"][:4000] if error.get("formula") else ""
                            ),
                            blocking=True,
                        )
                        for error in errors
                    )
            return {
                "review_input": current,
                "review_result": {},
                "program_findings": [f.model_dump() for f in findings],
                "usage": await asyncio.to_thread(ledger.usage),
            }
        except (ResourceStop, TimeoutError) as exc:
            return stopped(exc)
        except ContentError as exc:
            return stopped(exc, "incomplete")

    async def reviewer(state: State, config: RunnableConfig) -> dict[str, Any]:
        ledger = Ledger(work(state, config, "reviewer", root))
        try:
            async with stage(ledger):
                current = state["review_input"]
                result = await reviewer_agent.ainvoke(
                    agent_input(
                        state,
                        config,
                        "reviewer",
                        {
                            "request": state["request"],
                            "knowledge": current["knowledge"],
                            "content": current["content"],
                            "assets": current["review_assets"],
                            "render_identity": current["render_identity"],
                        },
                        root,
                    ),
                    config=RunnableConfig(
                        **{**config, "recursion_limit": 500, "run_name": "curriculum_reviewer"}
                    ),
                    context=AgentContext(get_stream_writer()),
                )
                review = Review.model_validate(result["structured_response"])
            return {
                "review_result": review.model_dump(),
                "usage": await asyncio.to_thread(ledger.usage),
            }
        except (ResourceStop, TimeoutError) as exc:
            return stopped(exc)

    async def record_review(state: State, config: RunnableConfig) -> dict[str, Any]:
        ledger = Ledger(work(state, config, "record_review", root))
        try:
            async with stage(ledger):
                for name, filename in rule_files(state["request"].get("scope", "section")):
                    current_rules = await asyncio.to_thread((RESOURCES / filename).read_text)
                    if fingerprint(current_rules) != fingerprint(
                        state["prepared_context"]["rules"][name]
                    ):
                        raise ContentError("执行规则在本次任务中已改变，旧检查不能应用")
                review = Review.model_validate(state["review_result"])
                review.findings.extend(Finding.model_validate(f) for f in state["program_findings"])
                current = await asyncio.to_thread(
                    ledger.store.check,
                    state["review_input"]["fingerprint"],
                    review,
                    fingerprint(state["prepared_context"]["rules"]["review"]),
                )
                await asyncio.to_thread(
                    ledger.record,
                    "review_finished",
                    fingerprint=current["fingerprint"],
                    program_findings=state["program_findings"],
                    model_review=state["review_result"],
                )
            if current["checks"]["passed"]:
                return await final_result(
                    {**state, "status": "completed", "unresolved": []}, ledger
                )
            blocking = [f.detail for f in review.findings if f.blocking]
            review_ref = fingerprint([current["fingerprint"], review.model_dump()])
            if review_ref == state.get("previous_review_ref"):
                return stopped(ResourceStop("稿件及阻断检查与上一轮相同，未取得修订进展"))
            get_stream_writer()(
                {"type": "progress", "step": "revision", "message": "正在核实检查问题并修订当前稿"}
            )
            return {
                "feedback": review.model_dump(),
                "unresolved": blocking,
                "previous_review_ref": review_ref,
                "round_index": state["round_index"] + 1,
                "usage": await asyncio.to_thread(ledger.usage),
            }
        except (ResourceStop, TimeoutError) as exc:
            return stopped(exc)
        except ContentError as exc:
            return stopped(exc, "incomplete")

    async def finish_incomplete(state: State, config: RunnableConfig) -> dict[str, Any]:
        return await final_result(state, Ledger(work(state, config, "finish_incomplete", root)))

    def advance(next_node: str) -> Callable[[State], str]:
        return lambda state: "finish_incomplete" if state.get("stop_reason") else next_node

    builder = StateGraph(State)
    for name, node in [
        ("prepare_task", prepare_task),
        ("author", author),
        ("prepare_review", prepare_review),
        ("reviewer", reviewer),
        ("record_review", record_review),
        ("finish_incomplete", finish_incomplete),
    ]:
        builder.add_node(name, node)
    builder.add_edge(START, "prepare_task")
    for name, next_node in [
        ("prepare_task", "author"),
        ("author", "prepare_review"),
        ("prepare_review", "reviewer"),
        ("reviewer", "record_review"),
    ]:
        builder.add_conditional_edges(name, advance(next_node), [next_node, "finish_incomplete"])
    builder.add_conditional_edges(
        "record_review",
        lambda state: (
            END
            if state.get("status") == "completed"
            else "finish_incomplete"
            if state.get("stop_reason")
            else "author"
        ),
        [END, "finish_incomplete", "author"],
    )
    builder.add_edge("finish_incomplete", END)
    return builder.compile().with_config(recursion_limit=500)


async def graph(config: RunnableConfig) -> Any:
    """原生 Agent Server 图工厂：在服务请求时构造模型，不在模块导入时读取凭据。"""
    return await asyncio.to_thread(build_graph, gemini)
