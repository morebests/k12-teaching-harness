"""仅增加教学内容与契约读取；运行操作使用 Agent Server 原生 API。"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from uuid import UUID

import httpx
from fastapi import FastAPI, HTTPException, Request
from langgraph_sdk import get_client
from langgraph_sdk.schema import Thread
from starlette.responses import HTMLResponse, JSONResponse

from teaching_harness.auth import authenticated_identity, diagnostics_allowed
from teaching_harness.content import ContentError, ContentStore
from teaching_harness.contracts import Curriculum, Review, TaskRequest, TaskView, fingerprint

app = FastAPI(title="数学教学内容契约", version="0.1.0")


@app.middleware("http")
async def protect_runtime_options(request: Request, call_next: Any) -> Any:
    path = request.url.path
    # 自定义 middleware 在框架认证之前运行；用同一凭据核验函数，不能信任请求正文。
    diagnostic = diagnostics_allowed(authenticated_identity(request.headers.get("authorization")))
    if request.method == "GET" and path.endswith("/stream") and not diagnostic:
        # 原生重连不指定过滤器会继承所有已发布事件；普通订阅固定为教学 custom 流。
        if "/runs/" not in path:
            return JSONResponse({"detail": "线程详细流需要维护者诊断权限"}, status_code=422)
        modes = request.query_params.get("stream_mode") or "custom"
        try:
            selected = json.loads(modes) if modes.startswith("[") else [modes]
        except ValueError:
            selected = []
        if selected != ["custom"]:
            return JSONResponse({"detail": "普通重连仅开放 custom 教学流"}, status_code=422)
        params = dict(request.query_params)
        params["stream_mode"] = "custom"
        request.scope["query_string"] = urlencode(params).encode()
    if request.method == "POST" and path.endswith(("/state/checkpoint", "/history")):
        body = await request.json()
        if not diagnostic and (
            body.get("subgraphs") or (body.get("checkpoint") or {}).get("checkpoint_ns")
        ):
            return JSONResponse({"detail": "不开放内部模型子图状态"}, status_code=422)
    if not diagnostic and request.query_params.get("subgraphs", "false").lower() == "true":
        return JSONResponse({"detail": "不开放内部模型子图状态"}, status_code=422)
    if request.method == "POST" and "/runs" in path and not path.endswith(("/cancel", "/search")):
        body = await request.json()
        forbidden = {
            "config",
            "context",
            "command",
            "checkpoint",
            "checkpoint_id",
            "interrupt_before",
            "interrupt_after",
            "webhook",
            "langsmith_tracing",
            "metadata",
        }
        if forbidden.intersection(body) or body.get("on_completion") == "delete":
            return JSONResponse(
                {"detail": "当前切片不接受自定义运行配置或状态改写"}, status_code=422
            )
    if path == "/threads" and request.method == "POST":
        body = await request.json()
        if body.get("supersteps") or body.get("ttl"):
            return JSONResponse({"detail": "教学任务不接受外部预填状态或自动删除"}, status_code=422)
    return await call_next(request)


@app.get("/v1/contracts")
async def contracts() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "capabilities": ["curriculum_design:grade8:section"],
        "request": TaskRequest.model_json_schema(),
        "curriculum": Curriculum.model_json_schema(),
        "review": Review.model_json_schema(),
        "task_view": TaskView.model_json_schema(),
    }


async def authorized_thread(thread_id: UUID, request: Request) -> tuple[Thread, ContentStore]:
    client = get_client(headers={"Authorization": request.headers.get("authorization", "")})
    # 先通过框架核验 thread 所属身份，再接触其文件。
    try:
        thread = await client.threads.get(str(thread_id))
    except httpx.HTTPStatusError as exc:
        raise HTTPException(exc.response.status_code, "任务不存在或无权读取") from None
    if (thread.get("metadata") or {}).get("owner") != getattr(request.user, "identity", None):
        raise HTTPException(404, "任务不存在或无权读取")
    store = await asyncio.to_thread(
        ContentStore, Path(os.environ.get("HARNESS_WORK_DIR", "work")), str(thread_id)
    )
    return thread, store


@app.get("/v1/threads/{thread_id}/content", response_model=TaskView)
async def content(
    thread_id: UUID, request: Request, expected_fingerprint: str | None = None
) -> Any:
    thread, store = await authorized_thread(thread_id, request)
    client = get_client(headers={"Authorization": request.headers.get("authorization", "")})
    try:
        snapshot = await asyncio.to_thread(store.snapshot)
    except (ContentError, ValueError):
        raise HTTPException(409, "当前产物或引用不可用") from None
    if expected_fingerprint and snapshot["fingerprint"] != expected_fingerprint:
        raise HTTPException(409, "内容指纹已过期；当前阶段不提供历史正文")
    if snapshot["checks"]:
        current_rules = await asyncio.to_thread(
            (Path(__file__).with_name("resources") / "review.md").read_text
        )
        if snapshot["checks"]["rules_fingerprint"] != fingerprint(current_rules):
            snapshot["checks"].update(applicable=False, passed=False)
    runs = await client.runs.list(str(thread_id), limit=1)
    evidence = await asyncio.to_thread(store.evidence)
    state = thread.get("values") or {}
    status = state.get("status", "pending")
    if thread["status"] == "busy":
        status = "running"
    if runs and runs[0]["status"] in {"interrupted", "error", "timeout"}:
        status = "cancelled" if runs[0]["status"] == "interrupted" else "failed"
    if status == "completed" and (
        not snapshot["checks"]
        or not snapshot["checks"]["passed"]
        or state.get("content_fingerprint") != snapshot["fingerprint"]
    ):
        status = "incomplete"
    return {
        "task_id": str(thread_id),
        "status": status,
        "native_status": thread["status"],
        "request": (thread["metadata"] or {})["request"],
        "request_fingerprint": (thread["metadata"] or {})["request_fingerprint"],
        "unresolved": state.get("unresolved", []),
        "usage": (evidence.get("execution") or {}).get("usage", state.get("usage", {})),
        **snapshot,
    }


@app.get("/v1/threads/{thread_id}/reading", response_class=HTMLResponse)
async def reading(thread_id: UUID, request: Request, expected_fingerprint: str) -> HTMLResponse:
    await content(thread_id, request, expected_fingerprint)
    _, store = await authorized_thread(thread_id, request)
    try:
        html = await asyncio.to_thread(store.rendered, expected_fingerprint)
    except ContentError:
        raise HTTPException(409, "当前稿尚无有效阅读稿") from None
    return HTMLResponse(
        html,
        headers={
            "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; img-src 'none'; base-uri 'none'; frame-ancestors 'none'",
            "X-Content-Type-Options": "nosniff",
        },
    )


@app.get("/v1/threads/{thread_id}/evidence")
async def evidence(thread_id: UUID, request: Request) -> dict[str, Any]:
    _, store = await authorized_thread(thread_id, request)
    result = await asyncio.to_thread(store.evidence)
    if result.get("execution"):
        # 重放缓存含完整 ToolMessage；教学证据只返回用量和事件，详细消息走维护者原生诊断。
        result["execution"].pop("operations", None)
    return result
