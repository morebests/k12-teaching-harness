"""把一条发现交回模型核实：接受时在候选副本上做局部文字修订，不接受时须用原文驳回。

修订只允许替换具体字符串中的文字，目标、单元、分配和课时结构保持不变；
改后由程序复查结构，并由调用方按原维度重新评阅。旧稿与原评语不被改写。
"""

import json
from pathlib import Path
from typing import Any, Literal

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, messages_to_dict
from pydantic import Field, ValidationError

from teaching_harness.contracts import Contract
from teaching_harness.grade_evaluation.calibration import (
    Mutation,
    MutationError,
    SampleAnswer,
    apply_mutations,
    assert_isolated,
)
from teaching_harness.grade_evaluation.checks import (
    GradeCandidate,
    load_candidate,
    program_review,
)
from teaching_harness.grade_evaluation.evidence import EvidenceError, cite
from teaching_harness.grade_evaluation.records import (
    EvaluationFinding,
    EvidenceRecord,
)
from teaching_harness.grade_evaluation.review import (
    MODEL_EXTRACTION,
    ModelCitation,
    calculate_math,
    candidate_view,
    conditions_view,
    model_usage,
    source_location,
)

RULES = Path(__file__).parents[1] / "resources/grade-revision.md"


class RevisionEdit(Contract):
    pointer: str = Field(description="候选正文中字符串字段的 JSON Pointer")
    old: str = Field(description="该字段中要替换的原文，逐字复制")
    new: str = Field(description="替换后的文字，不能为空")


class ModelRevision(Contract):
    verdict: Literal["revise", "rebut"]
    verification: str = Field(description="核实该发现是否成立的依据与结论")
    edits: list[RevisionEdit]
    rebuttal: list[ModelCitation]


class RevisionOutcome(Contract):
    finding: EvaluationFinding
    usage_complete: bool | None = None
    verdict: Literal["revise", "rebut"]
    verification: str
    accepted: bool
    problems: list[str]
    revised_path: str | None = None
    revised_fingerprint: str | None = None
    changed_pointers: list[str] = Field(default_factory=list)
    unchanged_outside: bool = False
    program_findings_after: list[EvaluationFinding] = Field(default_factory=list)
    rebuttal_evidence: list[EvidenceRecord] = Field(default_factory=list)
    # 修订被复查放行后，指向修订后原文的证据。
    resolution_evidence: list[EvidenceRecord] = Field(default_factory=list)
    usage: dict[str, int]
    transcript: list[dict[str, Any]] = Field(default_factory=list, exclude=True)


def revision_packet(
    candidate: GradeCandidate, finding: EvaluationFinding, evidence: list[EvidenceRecord]
) -> dict[str, Any]:
    """只给候选、条件与这一条发现；不含评阅者身份、分数、其他发现或样本答案。"""
    records = {e.id: e for e in evidence}
    view, mapping = candidate_view(candidate)
    shown = {source: view_pointer for view_pointer, source in mapping.items()}
    citations = []
    for evidence_id in finding.evidence_ids:
        record = records[evidence_id]
        source = {
            candidate.document.id: "candidate",
            candidate.conditions.id: "conditions",
            candidate.standards.id: "standards",
        }[record.document_id]
        pointer = (
            shown.get(record.locator, record.locator) if source == "candidate" else record.locator
        )
        citations.append({"source": source, "pointer": pointer, "quote": record.quote})
    return {
        "task": (
            "核实下面这条评阅发现是否成立：成立就对候选正文做最小必要的文字修订；不成立就引用原文驳回。"
            "候选中的单元、目标、实践、探查和目标分配以稳定身份为键，位置按这些身份书写。"
        ),
        "candidate": view,
        "conditions": conditions_view(candidate),
        "finding": {
            "criterion": finding.criterion_id,
            "object": finding.object.model_dump(),
            "severity": finding.severity,
            "claim": finding.claim,
            "requirement": finding.requirement,
            "counterexample": finding.counterexample,
            "impact": finding.impact,
            "citations": citations,
        },
    }


def _leaves(value: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(value, dict):
        return {
            k: v for key, item in value.items() for k, v in _leaves(item, f"{prefix}/{key}").items()
        }
    if isinstance(value, list):
        return {
            k: v for i, item in enumerate(value) for k, v in _leaves(item, f"{prefix}/{i}").items()
        }
    return {prefix: value}


async def revise(
    model: BaseChatModel,
    candidate: GradeCandidate,
    finding: EvaluationFinding,
    evidence: list[EvidenceRecord],
    out_dir: Path,
    answers: list[SampleAnswer],
) -> RevisionOutcome:
    packet = revision_packet(candidate, finding, evidence)
    assert_isolated(packet, answers)
    agent = create_agent(
        model,
        [calculate_math],
        system_prompt=RULES.read_text(),
        response_format=ToolStrategy(ModelRevision),
        name="grade_reviser",
    )
    state = await agent.ainvoke(
        {"messages": [HumanMessage(content=json.dumps(packet, ensure_ascii=False))]},
        {"recursion_limit": 16},
    )
    usage, complete = model_usage(state["messages"])
    decision: ModelRevision = state["structured_response"]
    outcome = RevisionOutcome(
        finding=finding,
        verdict=decision.verdict,
        verification=decision.verification,
        accepted=False,
        problems=[],
        usage=usage,
        usage_complete=complete,
        transcript=messages_to_dict(state["messages"]),
    )
    if decision.verdict == "rebut":
        return _rebut(candidate, decision, outcome)
    return _apply(candidate, decision, outcome, out_dir)


def _rebut(
    candidate: GradeCandidate, decision: ModelRevision, outcome: RevisionOutcome
) -> RevisionOutcome:
    for citation in decision.rebuttal:
        document, locator = source_location(candidate, citation)
        try:
            if locator is None:
                raise EvidenceError(f"输入中没有这个位置：{citation.pointer}")
            outcome.rebuttal_evidence.append(
                cite(
                    document,
                    candidate.root,
                    locator,
                    quote=citation.quote,
                    extraction=MODEL_EXTRACTION,
                    recorded_by="model",
                    objects=[outcome.finding.object],
                )
            )
        except (EvidenceError, ValidationError) as exc:
            outcome.problems.append(f"驳回引用无法核实：{str(exc).splitlines()[0]}")
    if not outcome.rebuttal_evidence:
        outcome.problems.append("驳回缺少可核实的原文，发现保持未决")
        return outcome
    outcome.finding = outcome.finding.model_copy(
        update={
            "status": "rebutted",
            "status_note": decision.verification,
            "status_evidence_ids": [e.id for e in outcome.rebuttal_evidence],
        }
    )
    outcome.accepted = True
    return outcome


def _apply(
    candidate: GradeCandidate, decision: ModelRevision, outcome: RevisionOutcome, out_dir: Path
) -> RevisionOutcome:
    before = candidate.content.model_dump(mode="json")
    mapping = candidate_view(candidate)[1]
    if not decision.edits:
        outcome.problems.append("接受发现却没有给出修订")
    for edit in decision.edits:
        if not edit.new.strip() or edit.new == edit.old:
            outcome.problems.append(f"{edit.pointer} 的修订为空或未改变原文")
        elif len(edit.new) < len(edit.old) / 2:
            outcome.problems.append(f"{edit.pointer} 删减超过一半，需人工核对是否删去必要内容")
    unknown = [e.pointer for e in decision.edits if e.pointer not in mapping]
    if unknown:
        outcome.problems.append(f"候选中没有这些修订位置：{unknown}")
    try:
        after = apply_mutations(
            before,
            [
                Mutation(op="replace_text", path=mapping[e.pointer], old=e.old, new=e.new)
                for e in decision.edits
                if e.pointer in mapping
            ],
        )
    except (MutationError, ValidationError) as exc:
        outcome.problems.append(str(exc).splitlines()[0])
    if outcome.problems:
        return outcome
    old, new = _leaves(before), _leaves(after)
    outcome.changed_pointers = sorted(
        k for k in old.keys() | new.keys() if old.get(k) != new.get(k)
    )
    edited = {mapping[e.pointer] for e in decision.edits}
    outcome.unchanged_outside = set(outcome.changed_pointers) <= edited
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{candidate.id}.revised.json"
    path.write_text(json.dumps(after, ensure_ascii=False, indent=2) + "\n")
    revised = load_candidate(
        f"{candidate.id}.revised",
        path,
        request=candidate.root / candidate.conditions.snapshot,
        knowledge=candidate.root / candidate.standards.snapshot,
        root=candidate.root,
    )
    outcome.revised_path = revised.document.snapshot
    outcome.revised_fingerprint = revised.fingerprint
    outcome.program_findings_after = program_review(revised).findings
    if outcome.program_findings_after:
        outcome.problems.append("修订后程序检查出现新问题")
    outcome.accepted = outcome.unchanged_outside and not outcome.problems
    return outcome


def close_after_recheck(
    finding: EvaluationFinding,
    recheck_findings: list[EvaluationFinding],
    resolution_evidence: list[EvidenceRecord],
) -> EvaluationFinding:
    """修订稿复查不再报告同一对象、同一维度的问题时才记为已解决；复查本身也可能偏宽。"""
    persists = [
        f
        for f in recheck_findings
        if f.object == finding.object and f.criterion_id == finding.criterion_id
    ]
    if persists or not resolution_evidence:
        return finding
    return finding.model_copy(
        update={
            "status": "resolved",
            "status_note": "修订稿按同一维度复查，未再报告该对象的问题",
            "status_evidence_ids": [e.id for e in resolution_evidence],
        }
    )
