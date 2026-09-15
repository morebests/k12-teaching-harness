"""开发阶段的可信调用身份；密钥与角色只从服务配置取得。"""

import hmac
import json
import os
from typing import Any

from langgraph_sdk import Auth, get_client
from pydantic import ValidationError

from teaching_harness.contracts import TaskRequest, fingerprint, task_id

auth = Auth()


@auth.authenticate
async def authenticate(authorization: str | None) -> dict[str, Any]:
    configured = json.loads(os.environ.get("HARNESS_AUTH_TOKENS", "{}"))
    supplied = (authorization or "").removeprefix("Bearer ")
    for identity, token in configured.items():
        if token and hmac.compare_digest(supplied, token):
            return {"identity": identity, "is_authenticated": True}
    raise Auth.exceptions.HTTPException(status_code=401, detail="调用凭据无效")


@auth.on
async def deny(ctx: Any, value: dict[str, Any]) -> None:
    raise Auth.exceptions.HTTPException(status_code=403, detail="当前切片不支持此操作")


@auth.on.threads.create
async def create_thread(
    *, ctx: Auth.types.AuthContext, value: Auth.types.ThreadsCreate
) -> dict[str, str]:
    metadata = value.get("metadata") or {}
    value["metadata"] = metadata
    try:
        request = TaskRequest.model_validate(metadata.get("request"))
    except ValidationError:
        raise Auth.exceptions.HTTPException(
            status_code=422, detail="教学请求不受支持或输入无效"
        ) from None
    if str(value["thread_id"]) != task_id(ctx.user.identity, request.event_id):
        raise Auth.exceptions.HTTPException(
            status_code=422, detail="任务身份必须由调用身份与事件确定"
        )
    digest = fingerprint(request.model_dump())
    metadata.clear()
    metadata.update(
        request=request.model_dump(), owner=ctx.user.identity, request_fingerprint=digest
    )
    return {"owner": ctx.user.identity, "request_fingerprint": digest}


async def read_thread(*, ctx: Auth.types.AuthContext, value: Any) -> dict[str, str]:
    return {"owner": ctx.user.identity}


auth.on.threads.read(read_thread)
auth.on.threads.search(read_thread)


@auth.on.threads.create_run
async def create_run(
    *, ctx: Auth.types.AuthContext, value: Auth.types.RunsCreate
) -> dict[str, str]:
    if not value.get("thread_id") or value.get("multitask_strategy") != "reject":
        raise Auth.exceptions.HTTPException(
            status_code=422, detail="必须先创建教学 thread，并拒绝同线程并发"
        )
    # 原生服务的 loopback SDK 继承当前认证上下文；不创建第二套状态存储。
    client = get_client()
    thread_id = str(value["thread_id"])
    thread = await client.threads.get(thread_id)
    kwargs = value["kwargs"]
    if set(kwargs.get("stream_mode", [])) - {"custom", "values", "updates"} or kwargs.get(
        "subgraphs"
    ):
        raise Auth.exceptions.HTTPException(status_code=422, detail="仅开放教学进度、草稿和结果流")
    expected = {"request": (thread["metadata"] or {})["request"]}
    if kwargs.get("input") != expected or kwargs.get("command"):
        raise Auth.exceptions.HTTPException(status_code=409, detail="运行输入必须等于已接收事件")
    if await client.runs.list(thread_id, limit=1):
        raise Auth.exceptions.HTTPException(status_code=409, detail="此事件已有运行，请查询原任务")
    return {"owner": ctx.user.identity}


@auth.on.threads.update
async def cancel_run(
    *, ctx: Auth.types.AuthContext, value: Auth.types.ThreadsUpdate
) -> dict[str, str]:
    if value.get("action") != "interrupt":
        raise Auth.exceptions.HTTPException(status_code=403, detail="仅支持原生 interrupt 取消")
    return {"owner": ctx.user.identity}
