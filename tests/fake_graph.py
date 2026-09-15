"""只在测试配置中把正式图的外部模型与知识边界换为可控输入。"""

import asyncio
import json
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from teaching_harness.graph import build_graph
from teaching_harness.knowledge import Knowledge, KnowledgeError


def sample_content():
    return {
        "title": "变化率与初始值",
        "narrative": "从变化率的比较走向含初始值的线性建模。",
        "goals": [
            {
                "code": "8.F.B.4",
                "responsibility": "解释并构建线性函数",
                "task_ids": ["tank"],
                "evidence": "解释变化率与初始值",
                "knowledge_use": "组件支持变化率解释；进程是设计推断",
            }
        ],
        "prerequisites": "比例关系是待诊断假设",
        "successors": "后续比较不同函数",
        "lessons": [
            {
                "title": f"第{i}课",
                "understanding_shift": "从表格识别变化走向函数表达",
                "task_ids": ["tank"],
                "student_minutes": 25,
                "discussion_minutes": 15,
                "other_minutes": 10,
            }
            for i in range(1, 4)
        ],
        "tasks": [
            {
                "id": "tank",
                "purpose": "解释变化率和初始值",
                "prompt": "水箱第2分钟有11升水，第6分钟有23升水。假设匀速注水，求线性模型并解释。",
                "solution": "(23-11)/(6-2)=3 升/分钟；初始5升，y=3x+5。",
                "student_work": "比较差分并解释单位",
                "evidence": "核对模型在两时刻的水量",
                "anticipated_response": "可能错用水量比，这是预判",
                "support": "提供差分表但不代算",
            }
        ],
        "practice_connections": "MP2 解释数量和单位，MP4 建模",
        "teacher_preparation": "准备纸笔",
        "assumptions": ["无实际学生证据"],
        "limitations": ["仅有限课段构想，未形成全年权威方案"],
    }


class TestModel(BaseChatModel):
    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        await asyncio.sleep(0.1)
        return self._generate(messages, stop=stop, **kwargs)

    @property
    def _llm_type(self):
        return "仅测试用可控模型"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        review = str(messages[0].content).startswith("# 有限课段检查规则")
        calls = []
        if review:
            calls = [
                {
                    "name": "Review",
                    "id": "check",
                    "args": {
                        "findings": [],
                        "evidence": {
                            k: "固定样本的有限控制检查"
                            for k in [
                                "coverage",
                                "mathematics",
                                "progression",
                                "conditions",
                                "evidence",
                                "sources",
                            ]
                        },
                    },
                }
            ]
        elif not any(isinstance(m, ToolMessage) for m in messages):
            calls = [
                {"name": "calculate_math", "id": "math", "args": {"expression": "(23-11)/(6-2)"}}
            ]
        elif not any(isinstance(m, ToolMessage) and m.name == "save_curriculum" for m in messages):
            payload = json.loads(messages[1].content)
            calls = [
                {
                    "name": "save_curriculum",
                    "id": "save",
                    "args": {
                        "content": sample_content(),
                        "expected_fingerprint": payload["current"]["fingerprint"],
                    },
                }
            ]
        message = AIMessage(
            content="有限草稿已保存" if not calls else "",
            tool_calls=calls,
            usage_metadata={"input_tokens": 10, "output_tokens": 10, "total_tokens": 20},
        )
        return ChatResult(generations=[ChatGeneration(message=message)])


class TestKnowledge(Knowledge):
    async def prepare(self, targets: list[str]) -> dict[str, Any]:
        if targets == ["8.F.A.2"]:
            raise KnowledgeError("测试知识源缺失目标")
        self.identity = {"namespace": "test", "version": "1"}
        return {"targets": targets, "source": "可控知识边界，不是实际 LC"}


graph = build_graph(TestModel, TestKnowledge)
