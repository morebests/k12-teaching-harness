"""有限课段 Agent 的工具；任务输入由框架注入，不保存共享可变会话。"""

import asyncio
import os
from collections.abc import Callable
from typing import Any

import httpx
from langchain.tools import ToolRuntime, tool
from langchain_core.tools import BaseTool

from teaching_harness.contracts import Curriculum, YearBlueprint
from teaching_harness.execution import AgentContext, Ledger, TeachingAgentState
from teaching_harness.knowledge import Knowledge, Operation
from teaching_harness.mathematics import calculate


@tool
async def calculate_math(expression: str) -> str:
    """用有理数核对有限加减乘除和整数幂，例如 (23-11)/(6-2)。"""
    return calculate(expression)


def author_tools(knowledge_factory: Callable[[httpx.AsyncClient], Knowledge]) -> list[BaseTool]:
    @tool
    async def browse(
        code: str, operation: Operation, runtime: ToolRuntime[AgentContext, TeachingAgentState]
    ) -> dict[str, Any]:
        """读取真实 CCSS 原文、支持组件、前驱或后继；不能查询课程材料。"""
        work = runtime.state["work"]
        async with httpx.AsyncClient(
            base_url=os.environ.get("HARNESS_LC_URL", "http://127.0.0.1:8000"), timeout=30
        ) as http:
            knowledge = knowledge_factory(http)
            source = work["knowledge_source"]
            knowledge.identity = source["identity"]
            knowledge.framework = source["framework"]
            knowledge.snapshot_id = source["snapshot_id"]
            try:
                return await knowledge.lookup(code, operation)
            finally:

                def append(value: dict[str, Any]) -> None:
                    value.setdefault("additional", []).extend(knowledge.records)
                    value.setdefault("audit", []).extend(knowledge.audit)

                await asyncio.to_thread(Ledger(work).store.update_record, "knowledge.json", append)

    @tool
    async def read_curriculum(
        runtime: ToolRuntime[AgentContext, TeachingAgentState],
    ) -> dict[str, Any]:
        """读取当前实际课程与指纹；当前无内容时 fingerprint 为 null。"""
        return await asyncio.to_thread(Ledger(runtime.state["work"]).store.snapshot)

    async def save(
        content: Curriculum | YearBlueprint,
        expected_fingerprint: str | None,
        runtime: ToolRuntime[AgentContext, TeachingAgentState],
    ) -> dict[str, Any]:
        scope = runtime.state["work"]["request"].get("scope", "section")
        if (scope == "year") != isinstance(content, YearBlueprint):
            raise ValueError("内容层级与当前任务范围不符，请使用对应的保存工具")
        result = await asyncio.to_thread(
            Ledger(runtime.state["work"]).store.save, content, expected_fingerprint
        )
        runtime.context.emit(
            {
                "type": "draft",
                "checked": False,
                "fingerprint": result["fingerprint"],
                "content": content.model_dump(),
            }
        )
        return {
            "fingerprint": result["fingerprint"],
            "rendered": result.get("rendered", False),
            "render_errors": result.get("render_errors", []),
            "message": "当前草稿已保存；rendered=false 时按 render_errors 修复源后再次保存，成功后送审",
        }

    @tool
    async def save_curriculum(
        content: Curriculum,
        expected_fingerprint: str | None,
        runtime: ToolRuntime[AgentContext, TeachingAgentState],
    ) -> dict[str, Any]:
        """保存完整当前课段草稿；须用刚读取的指纹，首次保存用 null。"""
        return await save(content, expected_fingerprint, runtime)

    @tool
    async def save_year_blueprint(
        content: YearBlueprint,
        expected_fingerprint: str | None,
        runtime: ToolRuntime[AgentContext, TeachingAgentState],
    ) -> dict[str, Any]:
        """保存完整全年蓝图；含单元组织、全部内容和实践目标、知识采用与探查。首次指纹为 null。"""
        return await save(content, expected_fingerprint, runtime)

    @tool
    async def plot_linear(
        name: str,
        slope: float,
        intercept: float,
        x_max: float,
        y_max: float,
        x_label: str,
        y_label: str,
        runtime: ToolRuntime[AgentContext, TeachingAgentState],
        expected_fingerprint: str | None = None,
    ) -> dict[str, Any]:
        """绘制第一象限内 y=slope*x+intercept 的 SVG，图含刻度与单位。

        name 用 rainwater_tank 这样的文件名主体，不含 assets/ 或 .svg。
        返回 fingerprint 属于图件；保存课程前请 read_curriculum 取得当前稿指纹。
        """
        return await asyncio.to_thread(
            Ledger(runtime.state["work"]).store.plot_linear,
            name,
            slope=slope,
            intercept=intercept,
            x_max=x_max,
            y_max=y_max,
            x_label=x_label,
            y_label=y_label,
            expected_fingerprint=expected_fingerprint,
        )

    return [
        browse,
        calculate_math,
        read_curriculum,
        save_curriculum,
        save_year_blueprint,
        plot_linear,
    ]
