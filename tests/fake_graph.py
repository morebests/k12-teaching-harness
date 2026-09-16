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


def sample_year():
    return {
        "kind": "grade",
        "title": "合成全年方案",
        "narrative": "先比较数量，再解释关系。",
        "units": [
            {
                "id": "u1",
                "title": "数量关系",
                "lesson_count": 160,
                "narrative": "通过表征发展模型理解。",
                "prerequisite_units": [],
                "entry": "以任务检查比例知识，不假定已掌握。",
                "exit": "解释变化率与初始值。",
                "assessment_plan": "从新数据建模并解释参数。",
            }
        ],
        "goals": [
            {
                "code": "8.F.B.4",
                "allocations": [
                    {
                        "unit_id": "u1",
                        "role": "teach",
                        "opportunity": "比较数据与函数表征。",
                        "evidence": "解释变化率与初始值。",
                    }
                ],
            }
        ],
        "practices": [
            {
                "code": f"MP{i}",
                "unit_ids": ["u1"],
                "student_actions": "核验模型适用条件。",
                "evidence": "解释限制。",
            }
            for i in range(1, 9)
        ],
        "tasks": [
            {
                **sample_content()["tasks"][0],
                "unit_ids": ["u1"],
                "design_consequence": "先诊断比例关系，再进入非比例关系。",
            }
        ],
        "knowledge_uses": [
            {
                "code": "8.F.B.4",
                "operation": "components",
                "record_ids": ["lc1"],
                "unit_ids": ["u1"],
                "decision": "组件提示变化率和初始值分别检查。",
            },
            {
                "code": "8.F.B.4",
                "operation": "prerequisites",
                "record_ids": ["edge1"],
                "unit_ids": ["u1"],
                "decision": "支持联系仅作为进入诊断的理由。",
            },
        ],
        "design_inferences": ["单元排序为本设计推断。"],
        "prerequisites": "前序年级经历待诊断。",
        "successors": "为后续建模提供依据。",
        "reserve_lessons": 20,
        "reserve_plan": "机动课时按进入诊断安排，不重复计算。",
        "focus_unit_id": "u1",
        "handoff_guidance": "保留目标；课段和逐课材料尚待展开。",
        "teacher_preparation": "方格纸与黑白打印。",
        "assumptions": ["合成学校条件。"],
        "limitations": ["尚无完整 Lesson 材料或课堂验证。"],
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
        year = json.loads(messages[1].content)["request"].get("scope") == "year"
        review = str(messages[0].content).startswith(("# 有限课段检查规则", "# 全年蓝图检查规则"))
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
        elif year and not any(isinstance(m, ToolMessage) for m in messages):
            calls = [
                {"name": "browse", "id": op, "args": {"code": "8.F.B.4", "operation": op}}
                for op in ["components", "prerequisites"]
            ]
        elif not any(isinstance(m, ToolMessage) for m in messages):
            expression = (
                "1/0" if "验证失败工具追踪" in str(messages[1].content) else "(23-11)/(6-2)"
            )
            calls = [{"name": "calculate_math", "id": "math", "args": {"expression": expression}}]
        elif not any(
            isinstance(m, ToolMessage) and m.name in {"save_curriculum", "save_year_blueprint"}
            for m in messages
        ):
            payload = json.loads(messages[1].content)

            candidate = sample_year() if year else sample_content()
            if year and "缺少目标" in payload["request"]["instruction"]:
                candidate["goals"][0]["code"] = "8.F.B.5"
            calls = [
                {
                    "name": "save_year_blueprint" if year else "save_curriculum",
                    "id": "save",
                    "args": {
                        "content": candidate,
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
    async def prepare_year(self, grade):
        self.identity = {"namespace": "test", "version": "1"}
        return {"year_scope": {"complete": True, "target_codes": ["8.F.B.4"], "parent_codes": []}}

    async def lookup(self, code, operation):
        result = {
            "code": code,
            "operation": operation,
            "records": [{"id": "lc1" if operation == "components" else "edge1"}],
        }
        self.records.append(result)
        return result

    async def prepare(self, targets: list[str]) -> dict[str, Any]:
        if targets == ["8.F.A.2"]:
            raise KnowledgeError("测试知识源缺失目标")
        self.identity = {"namespace": "test", "version": "1"}
        return {"targets": targets, "source": "可控知识边界，不是实际 LC"}


graph = build_graph(TestModel, TestKnowledge)
