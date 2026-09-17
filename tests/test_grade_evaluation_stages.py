"""专项检查：叙述承诺由程序核对位置，探查先独立求解再核查，数学表述逐条核对。"""

import json
import shutil
from pathlib import Path

import pytest
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field

from teaching_harness.grade_evaluation.calibration import Mutation, apply_mutations
from teaching_harness.grade_evaluation.checks import load_candidate
from teaching_harness.grade_evaluation.stages import (
    ModelPromises,
    check_promises,
    probe_cache_key,
    probe_facts,
    review_probe,
    review_statements,
    solver_packet,
)

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / ".scratch/math-harness-delivery/evidence/15-full-year-blueprint"


@pytest.fixture
def load(tmp_path):
    shutil.copy(BLUEPRINT / "final/knowledge.json", tmp_path / "knowledge.json")
    shutil.copy(BLUEPRINT / "initial/request.json", tmp_path / "request.json")

    def build(draft="final", mutations=()):
        content = json.loads((BLUEPRINT / f"{draft}/content/curriculum.json").read_text())
        content = apply_mutations(content, [Mutation.model_validate(m) for m in mutations])
        (tmp_path / "candidate.json").write_text(json.dumps(content, ensure_ascii=False))
        return load_candidate(
            "sample",
            tmp_path / "candidate.json",
            request=tmp_path / "request.json",
            knowledge=tmp_path / "knowledge.json",
            root=tmp_path,
        )

    return build


def promise(
    kind, unit, quote, pointer, codes=(), other="", lessons=None, counted=(), level=1, group=""
):
    return {
        "kind": kind,
        "group": group,
        "goal_codes": list(codes),
        "unit_id": unit,
        "other_unit_id": other,
        "lessons": lessons,
        "counted_in": list(counted),
        "level": level,
        "summary": "承诺摘要",
        "citation": {"source": "candidate", "pointer": pointer, "quote": quote},
    }


HANDOFF = "/handoff_guidance"
RESERVE = "/reserve_plan"


def test_叙述承诺的后续利用没有对应分配时报告_有分配时不报告(load):
    candidate = load()
    output = ModelPromises.model_validate(
        {
            "promises": [
                promise("later_use", "unit_4_linear_systems", "将在 Unit 4", HANDOFF, ["8.F.B.4"]),
                promise("later_use", "unit_8_bivariate_stats", "并在 Unit 8", HANDOFF, ["8.F.B.4"]),
            ]
        }
    )
    result = check_promises(candidate, output)
    [finding] = result.findings
    assert (finding.criterion_id, finding.severity, finding.object.id) == (
        "Q5",
        "key_gap",
        "8.F.B.4@unit_4_linear_systems:apply",
    )
    assert "unit_4_linear_systems" in finding.claim
    locators = {e.locator for e in result.evidence if e.id in finding.evidence_ids}
    assert HANDOFF in locators
    assert len(result.promises) == 2 and result.problems == []


def test_文字中的评价早于首次教学与依赖倒置由程序判定(load):
    systems_first = [
        {"op": "move", "path": "/units/2", "from_path": "/units/3"},
        {"op": "remove", "path": "/units/2/prerequisite_units/1"},
    ]
    candidate = load(mutations=systems_first)
    output = ModelPromises.model_validate(
        {
            "promises": [
                promise(
                    "assessment",
                    "unit_3_linear_functions",
                    "单元末通过真实情境建模",
                    "/units/unit_3_linear_functions/assessment_plan",
                    ["8.EE.C.8"],
                ),
                promise(
                    "dependency",
                    "unit_4_linear_systems",
                    "掌握线性函数作图与解析式求解",
                    "/units/unit_4_linear_systems/entry",
                    other="unit_3_linear_functions",
                ),
            ]
        }
    )
    findings = {f.criterion_id: f for f in check_promises(candidate, output).findings}
    # 方程组单元移到函数单元之前后，函数单元评价方程组已在其首次教学之后，只剩依赖倒置。
    assert set(findings) == {"Q3"}
    assert findings["Q3"].severity == "critical"
    assert "unit_4_linear_systems" in findings["Q3"].counterexample

    base = load()
    early = check_promises(
        base,
        ModelPromises.model_validate(
            {
                "promises": [
                    promise(
                        "assessment",
                        "unit_3_linear_functions",
                        "单元末通过真实情境建模",
                        "/units/unit_3_linear_functions/assessment_plan",
                        ["8.EE.C.8"],
                    )
                ]
            }
        ),
    )
    [finding] = early.findings
    assert (finding.criterion_id, finding.severity) == ("Q6", "key_gap")


def test_机动分项按组合计_全年总数不参与相加_重复计时由程序发现(load):
    candidate = load()
    reserve = ["reserve"]

    def item(quote, lessons, group, level=1, counted=reserve):
        return promise(
            "time_item",
            "reserve",
            quote,
            RESERVE,
            lessons=lessons,
            counted=counted,
            level=level,
            group=group,
        )

    items = [
        promise("time_total", "reserve", "20 节机动课时", RESERVE, lessons=20, counted=reserve),
        item("共 3 节", 3, "前置"),
        item("共 8 节", 8, "终结后"),
        item("投放 2 节", 2, "综合", level=2),
        item("投放 3 节", 3, "综合", level=2),
        item("投放 4 节", 4, "综合", level=2),
    ]
    # 单元自身课时、其他字段提到的机动课时是对机动计划的引用，不参与合计。
    unit_lessons = promise(
        "time_item",
        "unit_3_linear_functions",
        "本单元分配 22 课时",
        HANDOFF,
        lessons=22,
        counted=["unit"],
    )
    referenced = promise(
        "time_item",
        "unit_3_linear_functions",
        "投放 1 节全年机动课时",
        HANDOFF,
        lessons=1,
        counted=reserve,
    )
    items += [unit_lessons, referenced]
    # “综合”组没有写出合计时按细分 2+3+4 计；写出合计后只用合计。
    assert check_promises(candidate, ModelPromises(promises=items)).findings == []
    with_total = [*items, item("共 9 节", 9, "综合")]
    assert check_promises(candidate, ModelPromises(promises=with_total)).findings == []
    doubled = [*with_total, item("共 8 节", 8, "单元末测试", counted=["unit", "reserve"])]
    findings = check_promises(candidate, ModelPromises(promises=doubled)).findings
    assert {f.severity for f in findings} == {"critical"}
    assert any("3+8+9+8=28" in f.counterexample and "20" in f.counterexample for f in findings)
    # 是否同时计入两处完全取决于模型对原文的归类，发现来源记为模型。
    assert [f.origin for f in findings if "同时计入" in f.claim] == ["model"]
    # 层级写成 1、2 以外的值时按细分处理，不让该组合计变成 0。
    odd = [i if i["lessons"] != 4 else {**i, "level": 3} for i in items]
    assert check_promises(candidate, ModelPromises(promises=odd)).findings == []


def test_引用不实或目标代码不存在的承诺不参与判定(load):
    candidate = load()
    output = ModelPromises.model_validate(
        {
            "promises": [
                promise("later_use", "unit_4_linear_systems", "原文没有这句", HANDOFF, ["8.F.B.4"]),
                promise("later_use", "unit_4_linear_systems", "将在 Unit 4", HANDOFF, ["8.X.Y.9"]),
                promise("later_use", "unit_9", "将在 Unit 4", HANDOFF, ["8.F.B.4"]),
                # 缺少承诺发生的单元：不能核对，也不能中断核查。
                promise("later_use", "", "将在 Unit 4", HANDOFF, ["8.F.B.4"]),
                promise("assessment", "reserve", "将在 Unit 4", HANDOFF, ["8.F.B.4"]),
                promise("dependency", "", "将在 Unit 4", HANDOFF, other="unit_3_linear_functions"),
            ]
        }
    )
    result = check_promises(candidate, output)
    assert result.findings == []
    assert len(result.problems) == 3
    assert [c.verdict for c in result.promises] == ["not_checkable"] * 3


def test_探查的程序事实列出超出数据的区间_没有上界的区间与未提供的材料(load):
    candidate = load("revision")
    facts = probe_facts(candidate, "task_4_stats_linear_interpretation")
    column = next(c for c in facts.table_ranges if "复习时间" in c.header)
    assert (column.low, column.high, column.count) == (1.0, 7.0, 10)
    beyond = [i for i in facts.range_issues if i.kind == "beyond_data"]
    # 作者在题面与解答中写的 0~7.5 超出了表中复习时间 1–7 的范围。
    assert beyond and {(i.statement.low, i.statement.high) for i in beyond} == {(0.0, 7.5)}
    assert all(i.column and "复习时间" in i.column.header for i in beyond)
    assert len({i.id for i in facts.range_issues}) == len(facts.range_issues)

    initial = load("initial")
    rain = probe_facts(initial, "task_1_linear_modeling")
    [open_range] = [i for i in rain.range_issues if i.kind == "no_upper_bound"]
    assert (open_range.statement.low, open_range.statement.high) == (0.0, None)
    # 初稿统计探查说绘制了散点图、支持语让学生看散点图，但题面没有图也没有数据表。
    stats = probe_facts(initial, "task_4_stats_linear_interpretation")
    absent = {(m.kind, m.pointer.rsplit("/", 1)[-1]) for m in stats.absent_materials}
    assert {("figure", "text"), ("figure", "support")} <= absent
    assert all(m.id.startswith("material-") and "散点图" in m.text for m in stats.absent_materials)
    assert rain.absent_materials == []  # 雨水题的关系图象作为图件提供了

    rewritten = load(
        "initial",
        [
            {
                "op": "replace_text",
                "path": "/tasks/0/solution",
                "old": "(x \\ge 0)",
                "new": "(10 \\ge x \\ge 0)",
            },
            {
                "op": "replace_text",
                "path": "/tasks/0/prompt",
                "old": "实际物理意义",
                "new": "实际物理意义，截距代表中午之前的蓄水",
            },
        ],
    )
    facts = probe_facts(rewritten, "task_1_linear_modeling")
    assert [i.kind for i in facts.range_issues] == []
    assert (0.0, 10.0) in {(s.low, s.high) for s in facts.range_statements}
    assert facts.absent_materials == []


class Scripted(BaseChatModel):
    outputs: list[tuple[str, dict]]
    seen: list[str] = Field(default_factory=list)
    calls: int = 0

    @property
    def _llm_type(self):
        return "仅测试用专项检查模型"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        name, args = self.outputs[min(self.calls, len(self.outputs) - 1)]
        self.calls += 1
        self.seen.append(messages[-1].content)
        message = AIMessage(
            content="",
            tool_calls=[{"name": name, "id": f"call-{self.calls}", "args": args}],
            usage_metadata={"input_tokens": 4, "output_tokens": 2, "total_tokens": 6},
        )
        return ChatResult(generations=[ChatGeneration(message=message)])


def finding(pointer, quote, claim="统计解释把关联说成个体因果", severity="key_gap"):
    return {
        "kind": "probe",
        "id": "task_4_stats_linear_interpretation",
        "severity": severity,
        "claim": claim,
        "requirement": "统计解释不得超出数据与模型支持",
        "citations": [{"source": "candidate", "pointer": pointer, "quote": quote}],
        "counterexample": "",
        "impact": "学生形成错误的统计推断",
        "recheck": "核对斜率解释",
    }


async def test_探查先独立求解_核查须逐项回应求解与程序事实_发现归到该探查(load):
    candidate = load("revision")
    task = "task_4_stats_linear_interpretation"
    packet = solver_packet(candidate, task)
    text = json.dumps(packet, ensure_ascii=False)
    for hidden in [
        "solution",
        "student_work",
        "anticipated_response",
        "design_consequence",
        "support",
    ]:
        assert f'"{hidden}"' not in text
    assert "S01" in text
    solution = {
        "parts": [
            {"question": "斜率含义", "answer": "模型预测值每小时相差 6.5 分", "work": "读方程"}
        ],
        "required_conditions": ["仅在样本范围 1–7 小时内解释"],
        "missing_information": [],
        "notes": "",
    }
    ranges = [i.id for i in probe_facts(candidate, task).range_issues]
    valid = finding(f"/tasks/{task}/solution", "约 0~7.5 小时", claim="有效范围超出数据")

    def compare(item, author="consistent", matters=False, linked=None):
        return {"item": item, "author": author, "matters": matters, "finding": linked, "note": ""}

    incomplete = {
        # 漏了程序事实；条件被判为矛盾且重要，却没有对应发现；另有一条引文不实。
        "comparisons": [
            compare("answer-1"),
            compare("condition-1", "contradicted", True),
        ],
        "findings": [valid, finding(f"/tasks/{task}/solution", "原文里没有的话")],
        "checked": ["独立求解对照", "数据范围"],
    }
    complete = {
        "comparisons": [
            compare("answer-1", "contradicted", True, 1),
            compare("condition-1", "contradicted", True, 0),
            *[compare(r, "contradicted", True, 0) for r in ranges],
        ],
        # 第二条发现的引文仍不实；链接到它的核对项要留下记录，不能静默消失。
        "findings": [valid, finding(f"/tasks/{task}/solution", "仍然没有的话")],
        "checked": ["独立求解对照", "数据范围"],
    }
    model = Scripted(
        outputs=[
            ("ModelSolution", solution),
            ("ModelProbeReview", incomplete),
            ("ModelProbeReview", complete),
        ]
    )
    result = await review_probe(model, candidate, task, rules="规则")
    assert model.calls == 3  # 一次求解；核查不完整后补交一次
    assert "1–7 小时" in model.seen[1] and "0~7.5" in model.seen[1]
    assert "condition-1" in model.seen[1] and ranges[0] in model.seen[1]
    for missing in [ranges[0], "condition-1", "原文里没有的话"]:
        assert missing in model.seen[2]
    [kept] = result.findings
    assert (kept.criterion_id, kept.object.kind, kept.object.id) == ("Q4", "probe", task)
    assert len(result.comparisons) == 2 + len(ranges)
    assert len(result.problems) == 1 and "answer-1" in result.problems[0]
    assert result.solution.required_conditions == ["仅在样本范围 1–7 小时内解释"]
    assert result.usage["total_tokens"] == 18


def statement(quote, severity, error_type, counterexample=""):
    return {
        "kind": "unit",
        "id": "unit_2_linear_eq",
        "severity": severity,
        "error_type": error_type,
        "claim": "把恒等式说成无解",
        "requirement": "数学表述须正确",
        "citations": [
            {
                "source": "candidate",
                "pointer": "/units/unit_2_linear_eq/narrative",
                "quote": quote,
            }
        ],
        "counterexample": counterexample,
        "impact": "学生混淆解的类型",
        "recheck": "核对解的分类",
    }


def test_探查缓存按模型区分(load):
    candidate = load()
    task = "task_4_stats_linear_interpretation"
    keys = {probe_cache_key(candidate, task, {}, "规则", model=m) for m in ["m1", "m2"]}
    assert len(keys) == 2


async def test_数学表述核查只接收叙述性字段_严重度不超过错误类型的上限(load):
    candidate = load("initial")
    quote = "唯一解、恒等无解与无穷多解"
    output = {
        "findings": [
            statement(quote, "critical", "concept_confusion", "0x=0 对任意 x 成立"),
            statement(quote, "critical", "wrong_conclusion", "0x=0 对任意 x 成立，不是无解"),
            statement(quote, "key_gap", "wrong_conclusion"),
            statement(quote, "key_gap", "imprecise"),
            {**statement(quote, "key_gap", "imprecise"), "id": ""},
        ],
        "checked": ["单元叙述"],
    }
    model = Scripted(outputs=[("ModelStatementReview", output)])
    result = await review_statements(model, candidate, rules="规则")
    assert [f.severity for f in result.findings] == ["key_gap", "critical", "key_gap", "local"]
    # 对象身份为空的一条被拒收，其余照常保留。
    assert len(result.rejected_findings) == 1
    assert {f.criterion_id for f in result.findings} == {"Q4"}
    assert result.findings[0].object.id == "unit_2_linear_eq"
    assert list(result.error_types.values()) == [
        "concept_confusion",
        "wrong_conclusion",
        "wrong_conclusion",
        "imprecise",
    ]
    sent = json.loads(model.seen[0])
    assert (
        "tasks" not in sent["candidate"]
        and "narrative" in sent["candidate"]["units"]["unit_2_linear_eq"]
    )
