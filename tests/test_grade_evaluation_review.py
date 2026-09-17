"""模型评阅只接收候选、条件、标准与判据；返回的引用须能在原文核实。"""

import hashlib
import json
import shutil
from pathlib import Path

import pytest
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_google_genai._function_utils import convert_to_genai_function_declarations

from teaching_harness.grade_evaluation.checks import load_candidate
from teaching_harness.grade_evaluation.evidence import verify
from teaching_harness.grade_evaluation.records import load_rubric
from teaching_harness.grade_evaluation.review import (
    ModelCitation,
    ModelReview,
    adjudicate,
    review_candidate,
    review_packet,
    source_location,
)
from teaching_harness.grade_evaluation.scoring import summarize

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ".scratch/math-harness-delivery/evidence/15-full-year-blueprint/final"
RUBRIC = load_rubric(ROOT / ".scratch/math-harness-delivery/year-planning-rubric.json")


@pytest.fixture
def candidate(tmp_path):
    for name in ["knowledge.json", "checks.json", "context.json"]:
        shutil.copy(BASE / name, tmp_path / name)
    # 评价条件取初稿请求：只有原始任务与学校条件，不含修订反馈或旧稿。
    shutil.copy(BASE.parent / "initial/request.json", tmp_path / "request.json")
    shutil.copy(BASE / "content/curriculum.json", tmp_path / "candidate.json")
    return load_candidate(
        "holdout-assess-early",
        tmp_path / "candidate.json",
        request=tmp_path / "request.json",
        knowledge=tmp_path / "knowledge.json",
        root=tmp_path,
    )


def test_评阅输入不含作者检查_修订来源或样本身份(candidate):
    packet = review_packet(candidate, ["Q3", "Q6"], RUBRIC)
    text = json.dumps(packet, ensure_ascii=False)
    assert set(packet) == {"task", "criteria", "checklists", "candidate", "conditions", "standards"}
    # 候选按稳定身份呈现，单元顺序即键顺序；位置可换算回源文件。
    view = packet["candidate"]
    assert list(view["units"]) == [u.id for u in candidate.content.units]
    assert view["goals"]["8.SP.A.4"]["allocations"]["unit_8_bivariate_stats:teach"]["opportunity"]
    assert source_location(
        candidate,
        ModelCitation(
            source="candidate",
            pointer="/goals/8.SP.A.4/allocations/unit_8_bivariate_stats:teach/opportunity",
            quote="双向列联表",
        ),
    ) == (candidate.document, "/goals/32/allocations/0/opportunity")
    assert (
        source_location(
            candidate, ModelCitation(source="candidate", pointer="/goals/32/code", quote="x")
        )[1]
        is None
    )
    # 模型常把输入中的部分名写进位置；按所属部分去掉前缀后再换算。
    assert source_location(
        candidate,
        ModelCitation(source="standards", pointer="/standards/content/0/statement", quote="x"),
    )[1].endswith("/detail/source_fields/description")
    assert source_location(
        candidate,
        ModelCitation(
            source="candidate", pointer="/candidate/units/unit_8_bivariate_stats/exit", quote="x"
        ),
    ) == (candidate.document, "/units/7/exit")
    assert [c["id"] for c in packet["criteria"]] == ["Q3", "Q6"]
    assert {o["id"] for o in packet["checklists"]["Q6"]} >= {"unit_3_linear_functions"}
    assert "external_content" not in text and "holdout" not in text
    final_request = json.loads((BASE / "request.json").read_text())
    assert final_request["instruction"][300:360] not in text
    # 作者流程的模型检查结论与 Context 不进入独立评阅。
    checks = json.loads((candidate.root / "checks.json").read_text())
    assert checks["evidence"]["coverage"] not in text
    assert "prepared_context" not in text
    assert packet["conditions"]["school"]["lesson_count"] == 180
    codes = {s["code"] for s in packet["standards"]["content"]}
    assert {"8.SP.A.4", "8.EE.C.7"} <= codes and len(codes) == 36


class ScriptedModel(BaseChatModel):
    output: dict
    retry: dict | None = None
    calls: int = 0
    report_usage: bool = True

    @property
    def _llm_type(self):
        return "仅测试用评阅模型"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        self.calls += 1
        output = self.retry if self.retry is not None and self.calls > 1 else self.output
        message = AIMessage(
            content="",
            tool_calls=[{"name": "ModelReview", "id": f"review-{self.calls}", "args": output}],
            usage_metadata=(
                {"input_tokens": 30, "output_tokens": 12, "total_tokens": 42}
                if self.report_usage
                else None
            ),
        )
        return ChatResult(generations=[ChatGeneration(message=message)])


def cited(pointer, quote, source="candidate"):
    return {"source": source, "pointer": pointer, "quote": quote}


def model_output():
    real = cited("/units/unit_3_linear_functions/assessment_plan", "单元末通过真实情境建模")
    fake = cited("/units/unit_6_exponents_sci_notation/assessment_plan", "单元末以小组海报展示评价")
    checks = [
        {"kind": "unit", "id": u, "status": "supported", "citations": [real], "note": "有评价位置"}
        for u in [
            "unit_1_geom_transform",
            "unit_2_linear_eq",
            "unit_3_linear_functions",
            "unit_4_linear_systems",
            "unit_5_real_numbers_pythagoras",
            "unit_7_volume_3d",
            "unit_8_bivariate_stats",
        ]
    ]
    checks.append(
        {
            "kind": "unit",
            "id": "unit_6_exponents_sci_notation",
            "status": "supported",
            "citations": [fake],
            "note": "引用了原文中不存在的句子",
        }
    )
    finding = {
        "kind": "unit",
        "id": "unit_3_linear_functions",
        "severity": "local",
        "claim": "单元末评价没有说明困难后的响应",
        "requirement": "评价要连接后续教学响应",
        "citations": [real],
        "counterexample": "",
        "impact": "教师难以据结果调整",
        "recheck": "查看评价安排",
    }
    unsupported = {**finding, "severity": "critical", "claim": "评价早于学习机会"}
    return {
        "criteria": [
            {
                "criterion_id": "Q6",
                "observability": "observable",
                "score": 3,
                "score_low": None,
                "score_high": None,
                "critical_failure": False,
                "critical_failure_reason": "",
                "strengths": ["各单元有评价位置"],
                "object_checks": checks,
                "findings": [finding, unsupported],
                "score_rationale": "对象已核完",
            }
        ]
    }


async def test_核实模型引用_伪造原文使该维不能采用_重大发现缺反例被拒收(candidate):
    model = ScriptedModel(output=model_output())
    result = await review_candidate(model, candidate, ["Q6"], "r1", RUBRIC, rules="规则")
    [rating] = result.ratings
    assert rating.reviewer_id == "r1" and rating.content_fingerprint == candidate.fingerprint
    assert len(result.rejected_citations) == 1
    assert "小组海报" in result.rejected_citations[0].quote
    [finding] = result.findings
    assert finding.origin == "model" and finding.object.id == "unit_3_linear_functions"
    records = {e.id: e for e in result.evidence}
    assert verify(records[finding.evidence_ids[0]], candidate.documents, candidate.root) == (
        "verified"
    )
    assert "反例" in result.rejected_findings[0].reason
    # 引用失效触发一次补交；脚本模型重复原答，失效仍保留并如实计入两次用量。
    assert result.repairs == 1 and result.first_attempt_rejected_citations == 1
    assert result.usage == {"input_tokens": 60, "output_tokens": 24, "total_tokens": 84}
    status = {e.id: "verified" for e in result.evidence}
    summary = summarize(
        candidate.id,
        candidate.fingerprint,
        [rating, rating.model_copy(update={"reviewer_id": "r2"})],
        [],
        RUBRIC,
        status,
    )
    q6 = next(c for c in summary.criteria if c.criterion_id == "Q6")
    assert q6.status == "invalid" and "引用失效" in " ".join(q6.problems)


async def test_引用失效或漏交维度时在同一会话中要求补交一次(candidate):
    corrected = model_output()
    for check in corrected["criteria"][0]["object_checks"]:
        check["citations"] = [cited("/units/unit_3_linear_functions/assessment_plan", "单元末通过")]
    model = ScriptedModel(output=model_output(), retry=corrected)
    result = await review_candidate(model, candidate, ["Q6"], "r1", RUBRIC, rules="规则")
    assert model.calls == 2
    assert result.rejected_citations == [] and result.repairs == 1
    assert result.usage["total_tokens"] == 84 and result.usage_complete
    assert result.ratings[0].rules_fingerprint == hashlib.sha256("规则".encode()).hexdigest()


async def test_模型未返回用量时标为不完整而不是记作零(candidate):
    model = ScriptedModel(output=model_output(), retry=model_output(), report_usage=False)
    result = await review_candidate(model, candidate, ["Q6"], "r1", RUBRIC, rules="规则")
    assert not result.usage_complete


async def test_发现对象不是实际身份时记录问题(candidate):
    output = model_output()
    output["criteria"][0]["findings"][0]["id"] = "finding-made-up"
    result = await review_candidate(
        ScriptedModel(output=output, retry=output), candidate, ["Q6"], "r1", RUBRIC, rules="规则"
    )
    assert any("finding-made-up" in p for p in result.problems)


async def test_模型漏交维度或越出范围时记录问题(candidate):
    output = model_output()
    output["criteria"][0]["criterion_id"] = "Q2"
    result = await review_candidate(
        ScriptedModel(output=output), candidate, ["Q6"], "r1", RUBRIC, rules="规则"
    )
    assert result.ratings == []
    assert any("Q6" in p for p in result.problems) and any("Q2" in p for p in result.problems)


def test_Gemini工具格式保留对象结论与引用字段():
    schema = convert_to_genai_function_declarations([ModelReview])[0].function_declarations[0]
    criterion = schema.parameters.properties["criteria"].items
    check = criterion.properties["object_checks"].items
    assert {"status", "citations", "kind", "id"} <= set(check.properties)
    assert check.properties["status"].enum
    assert {"pointer", "quote", "source"} <= set(check.properties["citations"].items.properties)


class ScriptedAdjudicator(ScriptedModel):
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        self.calls += 1
        if self.calls == 1:
            self.output["_seen"] = json.loads(messages[-1].content)
        source = self.retry if self.retry is not None and self.calls > 1 else self.output
        args = {k: v for k, v in source.items() if k != "_seen"}
        message = AIMessage(
            content="",
            tool_calls=[{"name": "ModelAdjudication", "id": f"adj-{self.calls}", "args": args}],
            usage_metadata={"input_tokens": 3, "output_tokens": 2, "total_tokens": 5},
        )
        return ChatResult(generations=[ChatGeneration(message=message)])


async def test_裁定者读取双方原始评分并以可核实原文给出裁定(candidate):
    first = await review_candidate(
        ScriptedModel(output=model_output()), candidate, ["Q6"], "r1", RUBRIC, rules="规则"
    )
    second_output = model_output()
    second_output["criteria"][0]["score"] = 1
    second = await review_candidate(
        ScriptedModel(output=second_output), candidate, ["Q6"], "r2", RUBRIC, rules="规则"
    )
    ratings = first.ratings + second.ratings
    decision = {
        "criterion_id": "Q6",
        "score": 2,
        "score_low": None,
        "score_high": None,
        "critical_failure": False,
        "rationale": "单元评价有位置，但响应安排不足",
        "supporting": [
            cited("/units/unit_3_linear_functions/assessment_plan", "单元末通过真实情境建模")
        ],
        "needs_more_reading": "",
        "finding_verdicts": [],
    }
    model = ScriptedAdjudicator(output=dict(decision))
    result = await adjudicate(
        model,
        candidate,
        "Q6",
        ratings,
        first.findings + second.findings,
        first.evidence + second.evidence,
        RUBRIC,
        "r3",
    )
    seen = model.output["_seen"]
    assert [r["reviewer"] for r in seen["original_ratings"]] == ["r1", "r2"]
    assert result.adjudication.score == 2
    assert sorted(o.score for o in result.adjudication.original_ratings) == [1, 3]
    fake = {
        **decision,
        "supporting": [
            cited("/units/unit_3_linear_functions/assessment_plan", "单元末通过真实情境建模"),
            cited("/units/unit_3_linear_functions/assessment_plan", "不存在的说法"),
        ],
    }
    # 失效引用触发一次补交；仍失效时保留其身份，汇总据此判为引用失效，与评阅一致。
    stubborn = ScriptedAdjudicator(output=fake, retry=fake)
    failed = await adjudicate(stubborn, candidate, "Q6", ratings, [], [], RUBRIC, "r3")
    assert stubborn.calls == 2 and failed.problems
    status = {e.id: "verified" for e in failed.evidence}
    assert set(failed.adjudication.supporting_evidence) - set(status)
    repaired = ScriptedAdjudicator(output=fake, retry=dict(decision))
    fixed = await adjudicate(repaired, candidate, "Q6", ratings, [], [], RUBRIC, "r3")
    assert repaired.calls == 2 and fixed.problems == []
    assert set(fixed.adjudication.supporting_evidence) <= {e.id for e in fixed.evidence}


async def test_裁定者可用原文驳回已确认发现_引文不实时驳回不成立(candidate):
    from teaching_harness.grade_evaluation.records import EvaluationFinding

    first = await review_candidate(
        ScriptedModel(output=model_output()), candidate, ["Q6"], "r1", RUBRIC, rules="规则"
    )
    second = await review_candidate(
        ScriptedModel(output=model_output()), candidate, ["Q6"], "r2", RUBRIC, rules="规则"
    )
    record = first.evidence[0]
    gap = EvaluationFinding(
        id="promises:x:1:assessment-early:unit_3",
        candidate_id=candidate.id,
        content_fingerprint=candidate.fingerprint,
        criterion_id="Q6",
        object={"kind": "unit", "id": "unit_3_linear_functions"},
        origin="program",
        reviewer_id="promises",
        severity="key_gap",
        claim="评价早于学习机会",
        requirement="评价前须有学习机会",
        evidence_ids=[record.id],
        impact="影响",
        recheck="复查",
    )
    real = cited("/units/unit_3_linear_functions/assessment_plan", "单元末通过真实情境建模")
    decision = {
        "criterion_id": "Q6",
        "score": 3,
        "score_low": None,
        "score_high": None,
        "critical_failure": False,
        "rationale": "评价内容在本单元已学习",
        "supporting": [real],
        "needs_more_reading": "",
        "finding_verdicts": [
            {
                "finding_id": gap.id,
                "upheld": False,
                "reason": "评价的是本单元内容",
                "citations": [real],
            }
        ],
    }
    model = ScriptedAdjudicator(output=dict(decision))
    ratings = first.ratings + second.ratings
    outcome = await adjudicate(
        model, candidate, "Q6", ratings, [], first.evidence, RUBRIC, "r3", established=[gap]
    )
    assert [f["id"] for f in model.output["_seen"]["established_findings"]] == [gap.id]
    assert outcome.adjudication.rejected_findings == [gap.id]
    fake = {
        **decision,
        "finding_verdicts": [
            {
                "finding_id": gap.id,
                "upheld": False,
                "reason": "无据",
                "citations": [cited("/units/unit_3_linear_functions/assessment_plan", "编造的话")],
            }
        ],
    }
    failed = await adjudicate(
        ScriptedAdjudicator(output=fake, retry=fake),
        candidate,
        "Q6",
        ratings,
        [],
        first.evidence,
        RUBRIC,
        "r3",
        established=[gap],
    )
    assert failed.adjudication.rejected_findings == []
    assert any(gap.id in p for p in failed.problems)
    # 程序核对的结构事实标为不可驳回；即使给出真实原文也不记为驳回。
    fact = gap.model_copy(update={"id": "program:x:order:unit_3", "reviewer_id": "program"})
    on_fact = {
        **decision,
        "finding_verdicts": [{**decision["finding_verdicts"][0], "finding_id": fact.id}],
    }
    model = ScriptedAdjudicator(output=on_fact)
    kept = await adjudicate(
        model, candidate, "Q6", ratings, [], first.evidence, RUBRIC, "r3", established=[fact]
    )
    assert model.output["_seen"]["established_findings"][0]["rebuttable"] is False
    assert kept.adjudication.rejected_findings == []
    assert any(fact.id in p and "程序" in p for p in kept.problems)


def test_评价调用的计算工具出错时返回原因而不中断():
    from teaching_harness.grade_evaluation.review import calculate_math

    assert calculate_math.invoke({"expression": "(23-11)/(6-2)"}) == "3"
    assert calculate_math.invoke({"expression": "x+1"}).startswith("工具未完成")
    assert calculate_math.invoke({"expression": "1/0"}).startswith("工具未完成")
