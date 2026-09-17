"""发现交回模型核实：修订只改副本中的具体文字并保留其余内容，驳回须有可核实的原文。"""

import json
import shutil
from pathlib import Path

import pytest
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from teaching_harness.grade_evaluation.calibration import IsolationError, SampleAnswer
from teaching_harness.grade_evaluation.checks import load_candidate
from teaching_harness.grade_evaluation.evidence import cite
from teaching_harness.grade_evaluation.records import EvaluationFinding, ObjectRef
from teaching_harness.grade_evaluation.revision import close_after_recheck, revise, revision_packet

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ".scratch/math-harness-delivery/evidence/15-full-year-blueprint"
UNIT8 = ObjectRef(kind="unit", id="unit_8_bivariate_stats")


@pytest.fixture
def case(tmp_path):
    shutil.copy(BASE / "final/knowledge.json", tmp_path / "knowledge.json")
    shutil.copy(BASE / "initial/request.json", tmp_path / "request.json")
    shutil.copy(BASE / "final/content/curriculum.json", tmp_path / "candidate.json")
    candidate = load_candidate(
        "base",
        tmp_path / "candidate.json",
        request=tmp_path / "request.json",
        knowledge=tmp_path / "knowledge.json",
        root=tmp_path,
    )
    record = cite(
        candidate.document,
        tmp_path,
        "/units/7/assessment_plan",
        quote="以课内双变量统计分析报告进行个人或同伴评估",
        extraction="第 8 单元以统计分析报告作评价",
        recorded_by="model",
        objects=[UNIT8],
    )
    finding = EvaluationFinding(
        id="model:r1:base:q6:1",
        candidate_id="base",
        content_fingerprint=candidate.fingerprint,
        criterion_id="Q6",
        object=UNIT8,
        origin="model",
        reviewer_id="r1",
        severity="local",
        claim="统计分析报告没有说明评价后怎样回应困难",
        requirement="评价要连接后续教学响应",
        evidence_ids=[record.id],
        impact="教师难以据结果调整",
        recheck="查看第 8 单元评价安排",
    )
    return candidate, finding, [record]


class Scripted(BaseChatModel):
    output: dict

    @property
    def _llm_type(self):
        return "仅测试用修订模型"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        message = AIMessage(
            content="",
            tool_calls=[{"name": "ModelRevision", "id": "revise", "args": self.output}],
            usage_metadata={"input_tokens": 5, "output_tokens": 5, "total_tokens": 10},
        )
        return ChatResult(generations=[ChatGeneration(message=message)])


def edit(new):
    return {
        "pointer": "/units/unit_8_bivariate_stats/assessment_plan",
        "old": "以课内双变量统计分析报告进行个人或同伴评估",
        "new": new,
    }


async def test_接受发现后只修改副本中的指定文字(case, tmp_path):
    candidate, finding, evidence = case
    original = (tmp_path / "candidate.json").read_text()
    model = Scripted(
        output={
            "verdict": "revise",
            "verification": "原文确实只写评价形式，没有后续响应",
            "edits": [
                edit(
                    "以课内双变量统计分析报告进行个人或同伴评估，"
                    "报告暴露的关联与因果混淆在机动课时中用新数据再练习"
                )
            ],
            "rebuttal": [],
        }
    )
    outcome = await revise(model, candidate, finding, evidence, tmp_path / "revised", answers=[])
    assert outcome.accepted and outcome.problems == []
    assert outcome.changed_pointers == ["/units/7/assessment_plan"]
    assert outcome.unchanged_outside
    assert outcome.program_findings_after == []
    revised = json.loads(Path(tmp_path / outcome.revised_path).read_text())
    assert "机动课时中用新数据再练习" in revised["units"][7]["assessment_plan"]
    assert (tmp_path / "candidate.json").read_text() == original
    assert outcome.revised_fingerprint != candidate.fingerprint


async def test_删空原文或改动不存在的文字不被接受(case, tmp_path):
    candidate, finding, evidence = case
    for bad in [edit(""), {**edit("新文字"), "old": "原文没有这句"}]:
        model = Scripted(
            output={"verdict": "revise", "verification": "核实", "edits": [bad], "rebuttal": []}
        )
        outcome = await revise(model, candidate, finding, evidence, tmp_path / "bad", answers=[])
        assert not outcome.accepted and outcome.problems and outcome.revised_path is None


async def test_驳回必须引用可核实的原文(case, tmp_path):
    candidate, finding, evidence = case
    real = {
        "source": "candidate",
        "pointer": "/reserve_plan",
        "quote": "作为依据诊断实施课内干预与针对性巩固的资源",
    }
    fake = {**real, "quote": "统计报告后安排两节针对性补救"}
    for citation, rebutted in [(fake, False), (real, True)]:
        model = Scripted(
            output={
                "verdict": "rebut",
                "verification": "机动课时已承担诊断后的巩固",
                "edits": [],
                "rebuttal": [citation],
            }
        )
        outcome = await revise(model, candidate, finding, evidence, tmp_path / "r", answers=[])
        assert (outcome.finding.status == "rebutted") is rebutted
        assert outcome.revised_path is None


async def test_修订输入只含候选_条件与该条发现且拒绝答案泄漏(case):
    candidate, finding, evidence = case
    packet = revision_packet(candidate, finding, evidence)
    assert set(packet) == {"task", "candidate", "conditions", "finding"}
    # 发现的引用也按稳定身份呈现，与候选视图一致。
    citation = packet["finding"]["citations"][0]
    assert citation["pointer"] == "/units/unit_8_bivariate_stats/assessment_plan"
    assert packet["candidate"]["units"]["unit_8_bivariate_stats"]["assessment_plan"]
    assert "reviewer_id" not in json.dumps(packet["finding"])
    leak = SampleAnswer(
        sample_id="h1",
        kind="injected",
        rationale="统计分析报告没有说明评价后怎样回应困难",
    )
    with pytest.raises(IsolationError):
        await revise(Scripted(output={}), candidate, finding, evidence, Path("unused"), [leak])


def test_复查不再报告同一对象的问题时才关闭发现(case):
    _, finding, evidence = case
    same = finding.model_copy(update={"id": "model:r1-recheck:x:q6:1"})
    assert close_after_recheck(finding, [same], evidence).status == "open"
    closed = close_after_recheck(finding, [], evidence)
    assert closed.status == "resolved" and closed.status_evidence_ids == finding.evidence_ids
