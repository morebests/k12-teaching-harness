"""独立后端消费者；thread／run 由官方 SDK 承载。"""

from typing import Any, Self

import httpx
from langgraph_sdk import get_client

from .contracts import Receipt, TaskRequest, fingerprint, task_id


class HarnessClient:
    def __init__(self, url: str, identity: str, token: str) -> None:
        self.identity = identity
        self.http = httpx.AsyncClient(
            base_url=url, headers={"Authorization": f"Bearer {token}"}, timeout=60
        )
        self.native = get_client(url=url, headers={"Authorization": f"Bearer {token}"})

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.http.aclose()

    async def submit(self, request: TaskRequest) -> Receipt:
        tid = task_id(self.identity, request.event_id)
        thread = await self.native.threads.create(
            thread_id=tid, if_exists="do_nothing", metadata={"request": request.model_dump()}
        )
        runs = await self.native.runs.list(tid, limit=1)
        if runs:
            rid = runs[0]["run_id"]
        else:
            try:
                # SDK 0.4.4 的实现支持 durability，overload 声明遗漏该参数。
                run = await self.native.runs.create(
                    tid,
                    "curriculum",
                    input={"request": request.model_dump()},  # type: ignore[call-overload]
                    multitask_strategy="reject",
                    stream_mode="custom",
                    durability="sync",
                )
                rid = run["run_id"]
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code != 409:
                    raise
                runs = await self.native.runs.list(tid, limit=1)
                if not runs:
                    raise
                rid = runs[0]["run_id"]
        return Receipt(
            task_id=thread["thread_id"],
            run_id=rid,
            request_fingerprint=fingerprint(request.model_dump()),
        )

    async def query(self, tid: str) -> dict[str, Any]:
        response = await self.http.get(f"/v1/threads/{tid}/content")
        response.raise_for_status()
        return response.json()
