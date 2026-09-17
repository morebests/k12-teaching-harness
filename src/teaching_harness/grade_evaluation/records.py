"""年级课程评价的证据、发现、独立评分与复核记录；由这些类型导出 JSON Schema。

尺度只从评价规则数据读取；本模块只规定记录怎样定位证据、保持自洽。
"""

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import Field, model_validator

from teaching_harness.contracts import Contract, Fingerprint, Text

CriterionId = Literal["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8"]
CRITERIA: tuple[CriterionId, ...] = ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8")
RecordId = Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9_.:-]{0,159}$")]
# JSON 文档用 JSON Pointer；文本快照用字符区间。
Locator = Annotated[str, Field(pattern=r"^(?:(?:/(?:[^/~]|~[01])*)*|chars:\d+-\d+)$")]
Score = Annotated[int, Field(ge=0, le=4)]
ObjectKind = Literal[
    "grade",
    "goal",
    "practice",
    "unit",
    "dependency",
    "revisit",
    "assessment",
    "probe",
    "time",
    "resource",
    "teacher_question",
]
CheckStatus = Literal[
    "supported", "local_gap", "key_gap", "critical", "unverified", "not_applicable"
]
Severity = Literal["critical", "key_gap", "local"]
Origin = Literal["program", "model", "human"]


class ObjectRef(Contract):
    """评价对象：目标、单元、依赖或安排；身份沿用被评材料自己的编号。"""

    kind: ObjectKind
    id: Annotated[str, Field(min_length=1, max_length=160)]


class SourceDocument(Contract):
    """一份被引用材料；指纹针对 snapshot 的实际字节。"""

    id: RecordId
    party: Literal["project", "im", "ccss", "school"]
    role: Literal["candidate", "reference", "standard", "condition"]
    title: Text
    locator: Annotated[str, Field(min_length=1, max_length=500)]
    snapshot: Annotated[str, Field(min_length=1, max_length=500)]
    media: Literal["json", "text"]
    fingerprint: Fingerprint
    retrieved: date | None = None
    access: Literal["complete", "partial", "unavailable"] = "complete"
    access_note: str = ""

    @model_validator(mode="after")
    def explain_access(self) -> "SourceDocument":
        if self.access != "complete" and not self.access_note:
            raise ValueError("部分或无法取得的材料必须说明缺少什么")
        return self


class EvidenceRecord(Contract):
    """quote 是来源原文，extraction 是不补写的提取；判断写在对象结论或发现中。"""

    id: RecordId
    document_id: RecordId
    document_fingerprint: Fingerprint
    locator: Locator
    quote: Annotated[str, Field(min_length=1, max_length=4000)]
    extraction: Text
    objects: list[ObjectRef] = Field(default_factory=list)
    recorded_by: Origin


class ObjectCheck(Contract):
    object: ObjectRef
    status: CheckStatus
    evidence_ids: list[RecordId] = Field(default_factory=list)
    note: Text

    @model_validator(mode="after")
    def cite(self) -> "ObjectCheck":
        if self.status not in {"unverified", "not_applicable"} and not self.evidence_ids:
            raise ValueError("有依据、缺口或重大失败的结论必须引用证据")
        return self


class EvaluationFinding(Contract):
    id: RecordId
    candidate_id: RecordId
    content_fingerprint: Fingerprint
    criterion_id: CriterionId
    object: ObjectRef
    origin: Origin
    reviewer_id: RecordId
    severity: Severity
    claim: Text
    requirement: Text
    evidence_ids: list[RecordId] = Field(min_length=1)
    counterexample: str = ""
    impact: Text
    recheck: Text
    status: Literal["open", "confirmed", "rebutted", "resolved"] = "open"
    status_note: str = ""
    status_evidence_ids: list[RecordId] = Field(default_factory=list)

    @model_validator(mode="after")
    def substantiate(self) -> "EvaluationFinding":
        if self.severity == "critical" and not self.counterexample:
            raise ValueError("重大失败必须给出反例或计算")
        if self.status in {"rebutted", "resolved"} and not (
            self.status_note and self.status_evidence_ids
        ):
            raise ValueError("驳回或解决必须说明理由并引用当前证据")
        return self


class ScoreInterval(Contract):
    low: Score
    high: Score

    @model_validator(mode="after")
    def ordered(self) -> "ScoreInterval":
        if self.low >= self.high:
            raise ValueError("未决区间的下限必须小于上限")
        return self


class Coverage(Contract):
    expected: list[ObjectRef] = Field(min_length=1)
    note: str = ""


def _one_value(score: int | None, interval: ScoreInterval | None, observable: bool) -> None:
    if score is not None and interval is not None:
        raise ValueError("分数只能是单值或未决区间之一")
    if observable and score is None and interval is None:
        raise ValueError("可观察维度必须给出单值或未决区间")
    if not observable and (score is not None or interval is not None):
        raise ValueError("不可观察维度不能计分")


def score_bounds(score: int | None, interval: ScoreInterval | None) -> tuple[int, int] | None:
    if score is not None:
        return score, score
    return (interval.low, interval.high) if interval else None


class CriterionRating(Contract):
    candidate_id: RecordId
    content_fingerprint: Fingerprint
    criterion_id: CriterionId
    reviewer_id: RecordId
    rubric_fingerprint: Fingerprint
    # 评阅规则正文的指纹；早于该字段的记录由所属运行记录补入。
    rules_fingerprint: Fingerprint | None = None
    observability: Literal["observable", "partial", "unobservable"]
    comparability: Literal["comparable", "not_comparable", "single_candidate"]
    reviewed_scope: Coverage
    score: Score | None
    interval: ScoreInterval | None = None
    evidence_refs: list[RecordId] = Field(default_factory=list)
    strengths: list[Text] = Field(default_factory=list)
    findings: list[RecordId] = Field(default_factory=list)
    critical_failure: bool
    critical_failure_reason: str = ""
    object_checks: list[ObjectCheck]
    score_rationale: Text

    @model_validator(mode="after")
    def consistent_value(self) -> "CriterionRating":
        _one_value(self.score, self.interval, self.observability != "unobservable")
        if self.critical_failure and not self.critical_failure_reason:
            raise ValueError("重大失败必须说明理由")
        return self


def rating_problems(rating: CriterionRating) -> list[str]:
    """按协议的维度收敛规则核对分数与对象级结论；返回的问题使评分不能直接采用。"""
    problems = []
    statuses = {check.status for check in rating.object_checks}
    bounds = score_bounds(rating.score, rating.interval)
    high = bounds[1] if bounds else None
    checked = {(c.object.kind, c.object.id) for c in rating.object_checks}
    missing = [o for o in rating.reviewed_scope.expected if (o.kind, o.id) not in checked]
    if missing:
        problems.append(f"覆盖未完：{len(missing)} 个应查对象没有结论")
    if (rating.critical_failure or "critical" in statuses) and high != 0:
        problems.append("重大失败对应维度应为 0 分")
    if rating.critical_failure != ("critical" in statuses):
        problems.append("重大失败标记与对象级结论不一致")
    if high is not None and high > 2 and "key_gap" in statuses:
        problems.append("仍有关键缺口时最高 2 分")
    if high is not None and high >= 3 and "unverified" in statuses:
        problems.append("存在未核实对象，不能给 3 分以上")
    return problems


class OriginalRating(Contract):
    reviewer_id: RecordId
    score: Score | None
    interval: ScoreInterval | None = None
    critical_failure: bool


class Adjudication(Contract):
    id: RecordId
    candidate_id: RecordId
    content_fingerprint: Fingerprint
    criterion_id: CriterionId
    original_ratings: list[OriginalRating] = Field(min_length=2)
    triggers: list[Text]
    method: Literal["joint_review", "independent_adjudicator"]
    adjudicator_id: RecordId
    score: Score | None
    interval: ScoreInterval | None = None
    critical_failure: bool
    supporting_evidence: list[RecordId] = Field(min_length=1)
    # 以可核实原文驳回的已确认发现；其余已确认发现仍限制该维分数。
    rejected_findings: list[RecordId] = Field(default_factory=list)
    # 维持但按原文调整了严重度的已确认发现。可调整的是专项检查的发现（含程序依据模型抽取作出的判定）；
    # 程序检查（reviewer_id 为 program）的结构事实不可驳回、不可调整。
    adjusted_findings: dict[RecordId, Severity] = Field(default_factory=dict)
    needs_more_reading: str = ""
    rationale: Text

    @model_validator(mode="after")
    def consistent_value(self) -> "Adjudication":
        _one_value(self.score, self.interval, True)
        if len({r.reviewer_id for r in self.original_ratings}) != len(self.original_ratings):
            raise ValueError("原始评分必须来自不同评阅者")
        return self


class RubricCriterion(Contract):
    id: CriterionId
    name: Text
    weight: Annotated[int, Field(ge=1, le=100)]
    anchors: dict[Literal["0", "2", "4"], Text]
    review_scope: Text


class Rubric(Contract):
    version: Text
    status: Text
    scope: Text
    protocol: Text
    weight_basis: Text
    score_range: list[int]
    intermediate_anchors: dict[Literal["1", "3"], Text]
    missing_evidence_policy: Text
    criteria: list[RubricCriterion]
    critical_failures: list[Text]
    rating_record_required: list[Text]
    adjudication_triggers: list[Text]
    aggregate: dict[str, Any]
    verdicts: list[Text]
    current_scores: Any
    dimension_aggregation: dict[str, Text]
    adjudication_policy: Text
    equal_score_policy: Text


# 比较按裁定含义取规则数据中的文本；键与协议第 6 节的五种结论一一对应。
VERDICT_KEYS = ("better", "mixed", "no_difference", "undetermined", "failing")
VERDICT_MARKERS = ("更优", "各有优劣", "未见明确差异", "尚不能分出", "不合格")


class LoadedRubric(Contract):
    path: Text
    version: Text
    fingerprint: Fingerprint
    criteria: list[RubricCriterion]
    intermediate_anchors: dict[Literal["1", "3"], Text]
    dimension_aggregation: dict[str, Text]
    missing_evidence_policy: Text
    required_fields: list[Text]
    critical_failures: list[Text]
    adjudication_triggers: list[Text]
    sensitivity: Text
    verdicts: dict[str, Text]

    def weight(self, criterion: str) -> int:
        return next(c.weight for c in self.criteria if c.id == criterion)


def protocol_weights(path: Path) -> dict[str, int]:
    """协议正文第 4 节的权重表；规则数据须与之一致，代码不另存权重。"""
    rows = re.findall(r"^\| (Q[1-8]) [^|]+\| (\d+) \|", path.read_text(), re.MULTILINE)
    return {code: int(weight) for code, weight in rows}


def load_rubric(path: Path) -> LoadedRubric:
    """读取评价规则数据并核对它与评估协议仍是同一个八维 0–4 尺度。"""
    raw = path.read_bytes()
    rubric = Rubric.model_validate(json.loads(raw))
    if [c.id for c in rubric.criteria] != list(CRITERIA):
        raise ValueError("规则数据必须按 Q1–Q8 各列一次")
    weights = {c.id: c.weight for c in rubric.criteria}
    if protocol_weights(path.parent / rubric.protocol) != weights or sum(weights.values()) != 100:
        raise ValueError("规则数据的权重与评估协议不一致，或合计不是 100")
    if rubric.score_range != [0, 1, 2, 3, 4]:
        raise ValueError("规则数据的分数范围必须是 0–4")
    if len(rubric.verdicts) != len(VERDICT_KEYS) or any(
        marker not in text for marker, text in zip(VERDICT_MARKERS, rubric.verdicts, strict=False)
    ):
        raise ValueError("规则数据的裁定结论与协议第 6 节的五种结论不对应")
    return LoadedRubric(
        path=str(path),
        version=rubric.version,
        fingerprint=hashlib.sha256(raw).hexdigest(),
        criteria=rubric.criteria,
        intermediate_anchors=rubric.intermediate_anchors,
        dimension_aggregation=rubric.dimension_aggregation,
        missing_evidence_policy=rubric.missing_evidence_policy,
        required_fields=rubric.rating_record_required,
        critical_failures=rubric.critical_failures,
        adjudication_triggers=rubric.adjudication_triggers,
        sensitivity=rubric.aggregate["sensitivity"],
        verdicts=dict(zip(VERDICT_KEYS, rubric.verdicts, strict=True)),
    )
