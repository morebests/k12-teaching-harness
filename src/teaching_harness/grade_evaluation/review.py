"""独立模型评阅：按维度装配输入、调用模型，并把回复核实为评价记录。

输入只含候选正文、学校条件、年级标准与公开判据；不含作者对话、作者检查、
先前稿件、其他评阅者结论或校准答案。引用须能在实际原文位置核实。
"""

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Literal

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, messages_to_dict
from pydantic import Field, ValidationError

from teaching_harness.contracts import Contract
from teaching_harness.curriculum_tools import calculate_math
from teaching_harness.grade_evaluation.checks import TEACHER_QUESTIONS, GradeCandidate, checklist
from teaching_harness.grade_evaluation.evidence import EvidenceError, cite, evidence_id
from teaching_harness.grade_evaluation.records import (
    CRITERIA,
    Adjudication,
    CheckStatus,
    Coverage,
    CriterionId,
    CriterionRating,
    EvaluationFinding,
    EvidenceRecord,
    LoadedRubric,
    ObjectCheck,
    ObjectKind,
    ObjectRef,
    ScoreInterval,
    Severity,
    SourceDocument,
)
from teaching_harness.grade_evaluation.scoring import original_rating, rating_triggers

Source = Literal["candidate", "conditions", "standards"]
# 模型只给原文片段；判断保存在所属对象结论、发现或裁定中，不写进提取。
MODEL_EXTRACTION = "模型引用的原文片段；判断见所属结论"


class ModelCitation(Contract):
    source: Source = Field(
        description="candidate 为候选正文；conditions 为学校条件；standards 为标准"
    )
    pointer: str = Field(description="JSON Pointer，指向一个字符串字段，例如 /units/2/exit")
    quote: str = Field(description="从该字段逐字摘录的原文，80 字以内；多段用……连接")


class ModelObjectCheck(Contract):
    kind: ObjectKind
    id: str
    status: CheckStatus
    citations: list[ModelCitation]
    note: str


class ModelFinding(Contract):
    kind: ObjectKind
    id: str
    severity: Severity
    claim: str
    requirement: str
    citations: list[ModelCitation]
    counterexample: str = Field(description="重大失败必填：反例或计算")
    impact: str
    recheck: str


class ModelCriterionReview(Contract):
    criterion_id: CriterionId
    observability: Literal["observable", "partial", "unobservable"]
    score: int | None = Field(description="0–4 单值；未决时为 null 并给 score_low/score_high")
    score_low: int | None
    score_high: int | None
    critical_failure: bool
    critical_failure_reason: str
    strengths: list[str]
    object_checks: list[ModelObjectCheck]
    findings: list[ModelFinding]
    score_rationale: str


class ModelReview(Contract):
    criteria: list[ModelCriterionReview]


class RejectedCitation(Contract):
    criterion_id: str
    object_id: str
    source: str
    pointer: str
    quote: str
    reason: str


class RejectedFinding(Contract):
    criterion_id: str
    finding: dict[str, Any]
    reason: str


class ReviewResult(Contract):
    reviewer_id: str
    candidate_id: str
    content_fingerprint: str
    criteria: list[CriterionId]
    ratings: list[CriterionRating]
    findings: list[EvaluationFinding]
    evidence: list[EvidenceRecord]
    rejected_citations: list[RejectedCitation]
    rejected_findings: list[RejectedFinding]
    problems: list[str]
    usage: dict[str, int]
    # 任一模型回复缺少供应商用量时为 false，usage 只是已知部分之和；None 表示未记录。
    usage_complete: bool | None = None
    repairs: int = 0
    # 补交前的失效引用与问题，用于报告模型首次作答的可靠性。
    first_attempt_problems: list[str] = Field(default_factory=list)
    first_attempt_rejected_citations: int = 0


RULES = Path(__file__).parents[1] / "resources/grade-review.md"


def review_rules() -> str:
    return RULES.read_text()


def model_usage(messages: list[BaseMessage]) -> tuple[dict[str, int], bool]:
    """累计供应商返回的用量；任一回复缺少用量时标为不完整，不按零补齐。"""
    usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    complete = True
    for message in messages:
        if not isinstance(message, AIMessage):
            continue
        if not message.usage_metadata:
            complete = False
            continue
        for key in usage:
            usage[key] += message.usage_metadata[key]  # type: ignore[literal-required]
    return usage, complete


def _interval(score: int | None, low: int | None, high: int | None) -> ScoreInterval | None:
    if score is None and low is not None and high is not None:
        return ScoreInterval(low=low, high=high)
    return None


# 这些数组按对象自身身份呈现；目标分配按“单元:角色”呈现。
KEYED = {"/units": "id", "/goals": "code", "/practices": "code", "/tasks": "id"}


def keyed_view(content: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    """以稳定身份代替数组下标呈现候选，并记录每个位置对应的源文件 JSON Pointer。

    模型按下标数位置容易出错；身份重复时该数组保持下标形式。
    """
    mapping: dict[str, str] = {}

    def key_of(path: str, item: Any) -> str | None:
        if not isinstance(item, dict):
            return None
        if re.fullmatch(r"/goals/\d+/allocations", path):
            return f"{item.get('unit_id')}:{item.get('role')}"
        field = KEYED.get(path)
        return str(item.get(field)) if field else None

    def walk(value: Any, view: str, source: str) -> Any:
        mapping[view] = source
        if isinstance(value, dict):
            return {k: walk(v, f"{view}/{k}", f"{source}/{k}") for k, v in value.items()}
        if not isinstance(value, list):
            return value
        keys = [key_of(source, item) for item in value]
        if None in keys or len(set(keys)) != len(keys):
            return [walk(v, f"{view}/{i}", f"{source}/{i}") for i, v in enumerate(value)]
        return {
            k: walk(v, f"{view}/{k}", f"{source}/{i}")
            for i, (k, v) in enumerate(zip(keys, value, strict=True))
            if k is not None
        }

    return walk(content, "", ""), mapping


def candidate_view(candidate: GradeCandidate) -> tuple[dict[str, Any], dict[str, str]]:
    return keyed_view(candidate.content.model_dump(mode="json"))


def _standards(candidate: GradeCandidate) -> dict[str, list[tuple[int, dict[str, Any]]]]:
    """年级内容目标与数学实践原文；输入中的位置与来源文件节点一一对应。"""
    scope = candidate.scope
    codes = set(scope["target_codes"]) | set(scope["parent_codes"])
    sections: dict[str, list[tuple[int, dict[str, Any]]]] = {"content": [], "practices": []}
    for index, node in enumerate(scope["nodes"]):
        fields = node["detail"]["source_fields"]
        code = fields.get("statementCode") or ""
        entry = {"code": code, "statement": fields.get("description"), "notes": fields.get("notes")}
        if code in codes:
            sections["content"].append((index, entry))
        elif code.startswith(("MP", "8.MP")):
            sections["practices"].append((index, entry))
    return sections


def conditions_view(candidate: GradeCandidate) -> dict[str, Any]:
    """原始任务要求与学校条件；不含请求中的外部内容或修订说明以外的作者记录。"""
    return {
        "grade": candidate.request.grade,
        "instruction": candidate.request.instruction,
        "school": candidate.request.school.model_dump(mode="json"),
    }


def review_packet(
    candidate: GradeCandidate, criteria: list[CriterionId], rubric: LoadedRubric
) -> dict[str, Any]:
    scope = candidate.scope
    return {
        "task": (
            "独立评阅这份八年级 CCSS 年级课程规划候选。只依据本输入；逐个核查清单对象，"
            "按判据给出对象结论、发现和维度分。候选中的单元、目标、实践、探查和目标分配"
            "以稳定身份为键，units 的键顺序就是教学顺序；引用位置用这些身份组成，"
            "例如 /goals/8.F.B.4/allocations/unit_3_linear_functions:teach/opportunity。"
        ),
        "criteria": [
            {
                **c.model_dump(),
                "intermediate_anchors": rubric.intermediate_anchors,
                "dimension_aggregation": rubric.dimension_aggregation,
                "missing_evidence_policy": rubric.missing_evidence_policy,
                "critical_failures": rubric.critical_failures,
                **({"teacher_questions": TEACHER_QUESTIONS} if c.id == "Q8" else {}),
            }
            for c in rubric.criteria
            if c.id in criteria
        ],
        "checklists": {c: [o.model_dump() for o in checklist(candidate, c)] for c in criteria},
        "candidate": candidate_view(candidate)[0],
        "conditions": conditions_view(candidate),
        "standards": {
            "framework": scope.get("framework"),
            "source_snapshot": scope.get("source_snapshot"),
            **{k: [e for _, e in v] for k, v in _standards(candidate).items()},
        },
    }


def source_location(
    candidate: GradeCandidate, citation: ModelCitation
) -> tuple[SourceDocument, str | None]:
    """把模型在输入中引用的位置换算为实际来源文件中的位置；换算不了时位置为 None。"""
    prefix = f"/{citation.source}/"
    pointer = citation.pointer
    if pointer.startswith(prefix):
        pointer = pointer[len(prefix) - 1 :]
    if citation.source == "candidate":
        return candidate.document, candidate_view(candidate)[1].get(pointer)
    if citation.source == "conditions":
        return candidate.conditions, pointer if pointer.startswith("/school/") else None
    fields = {"statement": "description", "notes": "notes"}
    parts = pointer.split("/")
    sections = _standards(candidate)
    if (
        len(parts) == 4
        and parts[1] in sections
        and parts[2].isdigit()
        and int(parts[2]) < len(sections[parts[1]])
        and parts[3] in fields
    ):
        index = sections[parts[1]][int(parts[2])][0]
        return (
            candidate.standards,
            f"/package/year_scope/nodes/{index}/detail/source_fields/{fields[parts[3]]}",
        )
    return candidate.standards, None


class _Normalizer:
    def __init__(self, candidate: GradeCandidate, reviewer: str, criterion: CriterionId) -> None:
        self.candidate, self.reviewer, self.criterion = candidate, reviewer, criterion
        self.evidence: dict[str, EvidenceRecord] = {}
        self.rejected: list[RejectedCitation] = []

    def cite(self, citations: list[ModelCitation], target: ObjectRef) -> list[str]:
        ids = []
        for citation in citations:
            document, locator = source_location(self.candidate, citation)
            try:
                if locator is None:
                    raise EvidenceError("输入中没有这个位置")
                record = cite(
                    document,
                    self.candidate.root,
                    locator,
                    quote=citation.quote,
                    extraction=MODEL_EXTRACTION,
                    recorded_by="model",
                    objects=[target],
                )
            except (EvidenceError, ValidationError) as exc:
                self.rejected.append(
                    RejectedCitation(
                        criterion_id=self.criterion,
                        object_id=target.id,
                        source=citation.source,
                        pointer=citation.pointer,
                        quote=citation.quote,
                        reason=str(exc).splitlines()[0],
                    )
                )
                # 保留失效引用的身份，汇总时据此判为引用失效，而不是改写模型结论。
                ids.append(
                    evidence_id(
                        document.id, locator or citation.pointer, citation.quote, MODEL_EXTRACTION
                    )
                )
                continue
            self.evidence.setdefault(record.id, record)
            ids.append(record.id)
        return ids


async def review_candidate(
    model: BaseChatModel,
    candidate: GradeCandidate,
    criteria: list[CriterionId],
    reviewer_id: str,
    rubric: LoadedRubric,
    *,
    rules: str | None = None,
    packet: dict[str, Any] | None = None,
    transcript: list[dict[str, Any]] | None = None,
) -> ReviewResult:
    """packet 可由调用方先装配并做隔离核对；transcript 接收原始消息以便维护者复核。"""
    packet = packet or review_packet(candidate, criteria, rubric)
    rules = rules or review_rules()
    rules_fingerprint = hashlib.sha256(rules.encode()).hexdigest()
    agent = create_agent(
        model,
        [calculate_math],
        system_prompt=rules,
        response_format=ToolStrategy(ModelReview),
        name=f"grade_reviewer_{reviewer_id}",
    )
    config: Any = {"recursion_limit": 24}
    state = await agent.ainvoke(
        {"messages": [HumanMessage(content=json.dumps(packet, ensure_ascii=False))]}, config
    )
    result = normalize(
        state["structured_response"], candidate, criteria, reviewer_id, rubric, rules_fingerprint
    )
    first = (result.problems, len(result.rejected_citations))
    missing = [p for p in result.problems if p.startswith("模型没有返回维度")]
    repairs = 0
    if result.rejected_citations or missing:
        # 与格式错误同样处理：给出具体位置与原因，在同一会话中补交一次。
        failed = [c.model_dump() for c in result.rejected_citations]
        message = (
            "上次提交有以下问题，请重新提交完整的 ModelReview：包含全部要求的维度与对象结论，"
            "每条引用都从所指字段逐字复制。\n"
            + json.dumps({"missing": missing, "failed_citations": failed}, ensure_ascii=False)
        )
        state = await agent.ainvoke(
            {"messages": [*state["messages"], HumanMessage(content=message)]}, config
        )
        repairs = 1
    if transcript is not None:
        transcript.extend(messages_to_dict(state["messages"]))
    usage, complete = model_usage(state["messages"])
    result = normalize(
        state["structured_response"], candidate, criteria, reviewer_id, rubric, rules_fingerprint
    )
    return result.model_copy(
        update={
            "usage": usage,
            "usage_complete": complete,
            "repairs": repairs,
            "first_attempt_problems": first[0],
            "first_attempt_rejected_citations": first[1],
        }
    )


def normalize(
    review: ModelReview,
    candidate: GradeCandidate,
    criteria: list[CriterionId],
    reviewer_id: str,
    rubric: LoadedRubric,
    rules_fingerprint: str,
) -> ReviewResult:
    """把模型回复核实为评价记录；用量与补交情况由调用方补入。"""
    ratings, findings, problems = [], [], []
    evidence: dict[str, EvidenceRecord] = {}
    rejected_citations: list[RejectedCitation] = []
    rejected_findings: list[RejectedFinding] = []
    known = {(o.kind, o.id) for c in CRITERIA for o in checklist(candidate, c)}
    known |= {("goal", g.code) for g in candidate.content.goals}
    returned = [c.criterion_id for c in review.criteria]
    for extra in sorted(set(returned) - set(criteria)):
        problems.append(f"模型返回了未要求的维度 {extra}，已忽略")
    for missing in [c for c in criteria if c not in returned]:
        problems.append(f"模型没有返回维度 {missing}")
    for item in review.criteria:
        if item.criterion_id not in criteria or returned.count(item.criterion_id) > 1:
            if returned.count(item.criterion_id) > 1:
                problems.append(f"模型重复返回维度 {item.criterion_id}，均未采用")
            continue
        normalizer = _Normalizer(candidate, reviewer_id, item.criterion_id)
        checks = []
        for check in item.object_checks:
            target = ObjectRef(kind=check.kind, id=check.id)
            ids = normalizer.cite(check.citations, target)
            try:
                checks.append(
                    ObjectCheck(
                        object=target, status=check.status, evidence_ids=ids, note=check.note
                    )
                )
            except ValidationError as exc:
                problems.append(
                    f"{item.criterion_id}/{check.id} 对象结论无效：{exc.errors()[0]['msg']}"
                )
        finding_ids = []
        for n, raw in enumerate(item.findings, start=1):
            target = ObjectRef(kind=raw.kind, id=raw.id)
            if (raw.kind, raw.id) not in known:
                problems.append(
                    f"{item.criterion_id} 发现对象 {raw.kind}:{raw.id} 不是应查清单或候选中的实际身份"
                )
            ids = normalizer.cite(raw.citations, target)
            verified = [i for i in ids if i in normalizer.evidence]
            reason = ""
            if not verified:
                reason = "没有能在原文核实的引用"
            else:
                try:
                    finding = EvaluationFinding(
                        id=f"model:{reviewer_id}:{candidate.id}:{item.criterion_id.lower()}:{n}",
                        candidate_id=candidate.id,
                        content_fingerprint=candidate.fingerprint,
                        criterion_id=item.criterion_id,
                        object=target,
                        origin="model",
                        reviewer_id=reviewer_id,
                        severity=raw.severity,
                        claim=raw.claim,
                        requirement=raw.requirement,
                        evidence_ids=verified,
                        counterexample=raw.counterexample,
                        impact=raw.impact,
                        recheck=raw.recheck,
                    )
                except ValidationError as exc:
                    reason = str(exc.errors()[0]["msg"])
            if reason:
                rejected_findings.append(
                    RejectedFinding(
                        criterion_id=item.criterion_id, finding=raw.model_dump(), reason=reason
                    )
                )
                continue
            findings.append(finding)
            finding_ids.append(finding.id)
        evidence.update(normalizer.evidence)
        rejected_citations += normalizer.rejected
        try:
            ratings.append(
                CriterionRating(
                    candidate_id=candidate.id,
                    content_fingerprint=candidate.fingerprint,
                    criterion_id=item.criterion_id,
                    reviewer_id=reviewer_id,
                    rubric_fingerprint=rubric.fingerprint,
                    rules_fingerprint=rules_fingerprint,
                    observability=item.observability,
                    comparability="single_candidate",
                    reviewed_scope=Coverage(expected=checklist(candidate, item.criterion_id)),
                    score=item.score,
                    interval=_interval(item.score, item.score_low, item.score_high),
                    evidence_refs=sorted({e for c in checks for e in c.evidence_ids}),
                    strengths=item.strengths,
                    findings=finding_ids,
                    critical_failure=item.critical_failure,
                    critical_failure_reason=item.critical_failure_reason,
                    object_checks=checks,
                    score_rationale=item.score_rationale,
                )
            )
        except ValidationError as exc:
            problems.append(f"{item.criterion_id} 评分记录无效：{exc.errors()[0]['msg']}")
    return ReviewResult(
        reviewer_id=reviewer_id,
        candidate_id=candidate.id,
        content_fingerprint=candidate.fingerprint,
        criteria=criteria,
        ratings=ratings,
        findings=findings,
        evidence=list(evidence.values()),
        rejected_citations=rejected_citations,
        rejected_findings=rejected_findings,
        problems=problems,
        usage={"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
    )


class ModelAdjudication(Contract):
    criterion_id: CriterionId
    score: int | None = Field(description="0–4 单值；仍无法确定时为 null 并给区间")
    score_low: int | None
    score_high: int | None
    critical_failure: bool
    rationale: str
    supporting: list[ModelCitation]
    needs_more_reading: str


class AdjudicationResult(Contract):
    adjudication: Adjudication | None
    problems: list[str]
    evidence: list[EvidenceRecord]
    usage: dict[str, int]
    usage_complete: bool
    repairs: int


ADJUDICATION_RULES = (
    "你是独立裁定者。输入含同一维度的判据、应查对象、候选原文和两位评阅者的原始评分与引用。"
    "逐项核对双方引用的原文与对象结论，依据判据形成有理由的单一分数；证据仍不足以区分相邻分数时给出区间。"
    "不要取平均，也不要因为一方更自信而采纳。supporting 逐字引用支持裁定的原文，格式同评阅引用。"
    "needs_more_reading 写明还需补读什么，没有则为空。"
)


def _original_view(
    rating: CriterionRating,
    findings: list[EvaluationFinding],
    evidence: dict[str, EvidenceRecord],
) -> dict[str, Any]:
    def quotes(ids: list[str]) -> list[dict[str, str]]:
        return [
            {"pointer": evidence[i].locator, "quote": evidence[i].quote}
            for i in ids
            if i in evidence
        ]

    return {
        "reviewer": rating.reviewer_id,
        "score": rating.score,
        "interval": rating.interval.model_dump() if rating.interval else None,
        "critical_failure": rating.critical_failure,
        "rationale": rating.score_rationale,
        "object_checks": [
            {
                **c.object.model_dump(),
                "status": c.status,
                "note": c.note,
                "quotes": quotes(c.evidence_ids),
            }
            for c in rating.object_checks
        ],
        "findings": [
            {
                "object": f.object.model_dump(),
                "severity": f.severity,
                "claim": f.claim,
                "quotes": quotes(f.evidence_ids),
            }
            for f in findings
            if f.id in rating.findings
        ],
    }


async def adjudicate(
    model: BaseChatModel,
    candidate: GradeCandidate,
    criterion: CriterionId,
    ratings: list[CriterionRating],
    findings: list[EvaluationFinding],
    evidence: list[EvidenceRecord],
    rubric: LoadedRubric,
    adjudicator_id: str,
    transcript: list[dict[str, Any]] | None = None,
) -> AdjudicationResult:
    """裁定输入包含双方原始结论；这是复核本身的需要，原始评分另行保留不被改写。"""
    records = {e.id: e for e in evidence}
    own = sorted((r for r in ratings if r.criterion_id == criterion), key=lambda r: r.reviewer_id)
    packet = {
        **review_packet(candidate, [criterion], rubric),
        "original_ratings": [_original_view(r, findings, records) for r in own],
    }
    agent = create_agent(
        model,
        [calculate_math],
        system_prompt=ADJUDICATION_RULES,
        response_format=ToolStrategy(ModelAdjudication),
        name=f"grade_adjudicator_{adjudicator_id}",
    )
    config: Any = {"recursion_limit": 16}
    state = await agent.ainvoke(
        {"messages": [HumanMessage(content=json.dumps(packet, ensure_ascii=False))]}, config
    )
    target = ObjectRef(kind="grade", id=f"{criterion.lower()}-adjudication")
    normalizer = _Normalizer(candidate, adjudicator_id, criterion)
    normalizer.cite(state["structured_response"].supporting, target)
    repairs = 0
    if normalizer.rejected:
        failed = [c.model_dump() for c in normalizer.rejected]
        message = (
            "以下依据无法在原文核实，请重新提交完整的 ModelAdjudication，每条依据都从所指字段逐字复制。\n"
            + json.dumps(failed, ensure_ascii=False)
        )
        state = await agent.ainvoke(
            {"messages": [*state["messages"], HumanMessage(content=message)]}, config
        )
        repairs = 1
    if transcript is not None:
        transcript.extend(messages_to_dict(state["messages"]))
    usage, complete = model_usage(state["messages"])
    decision: ModelAdjudication = state["structured_response"]
    normalizer = _Normalizer(candidate, adjudicator_id, criterion)
    # 失效依据的身份保留在裁定中，汇总时与评阅一样判为引用失效，不悄悄丢弃。
    ids = normalizer.cite(decision.supporting, target)
    problems = [f"裁定引用无法核实：{r.quote}" for r in normalizer.rejected]
    adjudication = None
    if not any(i in normalizer.evidence for i in ids):
        problems.append("裁定没有能在原文核实的依据，维度保持未决")
    elif decision.criterion_id != criterion:
        problems.append(f"裁定返回了其他维度 {decision.criterion_id}")
    else:
        try:
            adjudication = Adjudication(
                id=f"adjudication:{adjudicator_id}:{candidate.id}:{criterion.lower()}",
                candidate_id=candidate.id,
                content_fingerprint=candidate.fingerprint,
                criterion_id=criterion,
                original_ratings=[original_rating(r) for r in own],
                triggers=rating_triggers(own),
                method="independent_adjudicator",
                adjudicator_id=adjudicator_id,
                score=decision.score,
                interval=_interval(decision.score, decision.score_low, decision.score_high),
                critical_failure=decision.critical_failure,
                supporting_evidence=ids,
                needs_more_reading=decision.needs_more_reading,
                rationale=decision.rationale,
            )
        except ValidationError as exc:
            problems.append(f"裁定记录无效：{exc.errors()[0]['msg']}")
    return AdjudicationResult(
        adjudication=adjudication,
        problems=problems,
        evidence=list(normalizer.evidence.values()),
        usage=usage,
        usage_complete=complete,
        repairs=repairs,
    )
