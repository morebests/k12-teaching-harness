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
from teaching_harness.grade_evaluation.stages import (
    ProbeModelOutput,
    ProbeResult,
    PromiseResult,
    StatementResult,
)

# 供应商返回的 input_tokens、output_tokens、total_tokens。
# 键见 review.USAGE_KEYS；较早的记录没有 cached_input_tokens。
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
    max_output_tokens: int | None = None
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
    cached_input_tokens: int = 0
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
    """两位评阅者在共同样本上的逐维评分一致性。"""

    first: RecordId
    second: RecordId
    scope: Literal["pair", "all"] = Field(
        description="pair：这两位的共同样本；all：所有评阅者都评过的样本"
    )
    samples: int
    pairs: int
    exact: int
    differ_by_1: int
    differ_by_2_or_more: int
    critical_disagreements: int


class StageRun(Contract):
    """一个样本的一项专项检查。探查的模型输出按题面缓存，用量只记在缓存条目上。"""

    schema_version: Literal[1] = 1
    sample_id: RecordId
    stage: Literal["promises", "probes", "statements"]
    model: Text
    max_output_tokens: int | None = None
    rules_fingerprint: Fingerprint
    seconds: float
    error: str | None = None
    # 失败时已经消耗的用量；成功时用量在各项结果或探查缓存条目上。
    failed_usage: Usage | None = None
    promises: PromiseResult | None = None
    statements: StatementResult | None = None
    probes: list[ProbeResult] = Field(default_factory=list)
    probe_cache: list[Fingerprint] = Field(default_factory=list)

    def results(self) -> list[PromiseResult | StatementResult | ProbeResult]:
        return [r for r in (self.promises, self.statements) if r] + list(self.probes)

    def findings(self) -> list[EvaluationFinding]:
        return [f for r in self.results() for f in r.findings]

    def evidence(self) -> list[EvidenceRecord]:
        return [e for r in self.results() for e in r.evidence]


class ProbeCacheEntry(Contract):
    schema_version: Literal[1] = 1
    key: Fingerprint
    task_id: Text
    first_sample: RecordId
    model: Text
    output: ProbeModelOutput


class SetReport(Contract):
    """一个样本集的检出统计；combined 为整体评阅加程序与专项检查的合并结果。"""

    samples: list[RecordId]
    program: DetectionMetrics | None
    stages: dict[str, DetectionMetrics]
    reviewers: dict[str, DetectionMetrics]
    combined: dict[str, DetectionMetrics]
    per_sample: dict[str, dict[str, DetectionMetrics]]


class StageLabels(Contract):
    samples: int
    runs: int = Field(default=1, description="全部运行次数，含重复运行")
    errors: int
    findings: int
    rejected_findings: int
    rejected_citations: int
    problems: int
    repairs: int
    agreed: int = Field(default=0, description="重复运行对齐后的发现数")
    stable: int = Field(default=0, description="其中多数运行都报出的发现数")


class CalibrationReport(Contract):
    schema_version: Literal[3] = 3
    sets: dict[str, SetReport]
    labels: dict[str, ReviewerLabels]
    stage_labels: dict[str, StageLabels]
    agreements: list[Agreement]


class UsageTotal(Contract):
    calls: int = 0
    failed_calls: int = 0
    incomplete_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cached_input_tokens: int = 0


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
