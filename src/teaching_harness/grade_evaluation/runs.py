"""本地评价命令读写的运行记录；与评价记录一起导出为契约。

较早的调试运行没有补交次数与用量完整性字段，这些字段为 None 表示当时未记录，不按零解释。
"""

from typing import Literal

from pydantic import Field

from teaching_harness.contracts import Contract, Fingerprint, Text
from teaching_harness.grade_evaluation.calibration import DetectionMetrics
from teaching_harness.grade_evaluation.records import (
    Adjudication,
    CriterionId,
    CriterionRating,
    EvaluationFinding,
    EvidenceRecord,
    ObjectRef,
    RecordId,
    SourceDocument,
)
from teaching_harness.grade_evaluation.review import (
    RejectedCitation,
    RejectedFinding,
    ReviewResult,
)
from teaching_harness.grade_evaluation.revision import RevisionOutcome

# 供应商返回的 input_tokens、output_tokens、total_tokens。
Usage = dict[str, int]


class CallRecord(Contract):
    """一个维度组的一次评阅调用，含同一会话内的补交。"""

    criteria: list[CriterionId]
    seconds: float
    usage: Usage | None
    usage_complete: bool | None = None
    repairs: int | None = None
    first_attempt_rejected_citations: int | None = None
    error: str | None


class ReviewRun(Contract):
    schema_version: Literal[1] = 1
    sample_id: RecordId
    reviewer_id: RecordId
    candidate_id: RecordId
    content_fingerprint: Fingerprint
    model: Text
    rules_fingerprint: Fingerprint
    criteria: list[CriterionId]
    ratings: list[CriterionRating]
    findings: list[EvaluationFinding]
    evidence: list[EvidenceRecord]
    rejected_citations: list[RejectedCitation]
    rejected_findings: list[RejectedFinding]
    problems: list[str]
    usage: Usage
    calls: list[CallRecord]

    def bound_ratings(self) -> list[CriterionRating]:
        """评分补上所属运行的规则指纹，使汇总能拒绝混用不同规则的评分。"""
        return [
            r
            if r.rules_fingerprint
            else r.model_copy(update={"rules_fingerprint": self.rules_fingerprint})
            for r in self.ratings
        ]


class AdjudicationCall(Contract):
    criterion: CriterionId
    input_tokens: int
    output_tokens: int
    total_tokens: int
    usage_complete: bool | None = None
    repairs: int | None = None


class AdjudicationRun(Contract):
    schema_version: Literal[1] = 1
    adjudicator: RecordId
    rules_fingerprint: Fingerprint | None = None
    adjudications: list[Adjudication]
    evidence: list[EvidenceRecord]
    problems: list[str]
    usage: list[AdjudicationCall]


class RecheckRecord(Contract):
    candidate: Literal["original", "revised"]
    same_object_findings: list[EvaluationFinding]
    review: ReviewResult


class RevisionRun(Contract):
    schema_version: Literal[1] = 1
    sample_id: RecordId
    outcome: RevisionOutcome
    recheck: list[RecheckRecord] = Field(default_factory=list)


class ConstructedFinding(Contract):
    """人工构造的发现，例如用来检验误报能否被原文驳回。"""

    note: Text
    finding: EvaluationFinding
    evidence: list[EvidenceRecord]


class ReviewerLabels(Contract):
    samples: int
    failed_calls: int
    incomplete_usage_calls: int
    findings: int
    rejected_findings: int
    rejected_citations: int
    unverified_objects: int
    unobservable_ratings: int
    problems: int
    repairs: int
    first_attempt_rejected_citations: int


class Agreement(Contract):
    pairs: int
    exact: int
    differ_by_1: int
    differ_by_2_or_more: int
    critical_disagreements: int


class CalibrationReport(Contract):
    schema_version: Literal[1] = 1
    program: list[DetectionMetrics]
    model: dict[str, list[DetectionMetrics]]
    per_sample: dict[str, dict[str, DetectionMetrics]]
    labels: dict[str, ReviewerLabels]
    agreement: Agreement | None


class UsageTotal(Contract):
    calls: int = 0
    incomplete_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class UsageReport(Contract):
    schema_version: Literal[1] = 1
    totals: dict[str, UsageTotal]


class VerificationReport(Contract):
    schema_version: Literal[1] = 1
    counts: dict[str, dict[str, int]]


class ImSource(Contract):
    id: RecordId
    title: Text
    url: Text
    retrieved: Text
    snapshot: Text
    sha256: Fingerprint
    characters: int
    html_sha256: Fingerprint
    sign_in_prompt: bool


class DocumentSpec(Contract):
    id: RecordId
    party: Literal["project", "im", "ccss", "school"]
    role: Literal["candidate", "reference", "standard", "condition"]
    title: Text
    snapshot: Text
    locator: str | None = None
    retrieved: str | None = None
    access: Literal["complete", "partial", "unavailable"] = "complete"
    access_note: str = ""


class SpotCheck(Contract):
    faithful: bool
    note: Text


class ExtractionEntry(Contract):
    document: RecordId
    locator: str | None = None
    quote: str | None = None
    extraction: Text
    objects: list[ObjectRef]
    spot_check: SpotCheck


class Unobservable(Contract):
    object: ObjectRef
    document: RecordId
    quote: str = ""
    note: Text


class ExtractionSpec(Contract):
    attribution: Text
    documents: list[DocumentSpec]
    entries: list[ExtractionEntry]
    unobservable: list[Unobservable]


class IndexCheck(Contract):
    document: RecordId
    party: str
    objects: list[ObjectRef]
    status: str
    evidence_id: RecordId | None = None
    spot_check: SpotCheck


class EvidenceIndex(Contract):
    schema_version: Literal[1] = 1
    attribution: Text
    documents: list[SourceDocument]
    evidence: list[EvidenceRecord]
    checks: list[IndexCheck]
    unobservable: list[Unobservable]
    problems: list[str]
