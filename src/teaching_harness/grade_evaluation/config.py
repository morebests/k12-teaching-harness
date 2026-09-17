"""评价配置：在新候选生成和保留样本评阅前冻结尺度、范围、参考接触与评阅方式。"""

import hashlib
from datetime import date
from pathlib import Path
from typing import Any, Literal

from pydantic import Field

from teaching_harness.contracts import Contract, Fingerprint, Text
from teaching_harness.grade_evaluation.calibration import DetectionMetrics, Sample, SampleAnswer
from teaching_harness.grade_evaluation.evidence import file_sha256
from teaching_harness.grade_evaluation.records import (
    Adjudication,
    CriterionId,
    CriterionRating,
    EvaluationFinding,
    EvidenceRecord,
    RecordId,
    SourceDocument,
)
from teaching_harness.grade_evaluation.runs import (
    AdjudicationRun,
    CalibrationReport,
    ConstructedFinding,
    EvidenceIndex,
    ExtractionSpec,
    ImSource,
    ReviewRun,
    RevisionRun,
    UsageReport,
    VerificationReport,
)
from teaching_harness.grade_evaluation.scoring import Comparison, GradeSummary


class FileRef(Contract):
    """文件或目录的仓库相对路径与内容指纹；目录按相对路径和各文件字节计算。"""

    path: Text
    fingerprint: Fingerprint


def _digest(path: Path) -> str:
    if path.is_file():
        return file_sha256(path)
    digest = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(item.relative_to(path).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(item.read_bytes()).digest())
    return digest.hexdigest()


def file_ref(path: Path, root: Path) -> FileRef:
    return FileRef(
        path=path.resolve().relative_to(root.resolve()).as_posix(), fingerprint=_digest(path)
    )


def config_drift(refs: dict[str, FileRef], root: Path) -> list[str]:
    """返回自冻结后缺失或内容改变的项目名。"""
    return [
        name
        for name, ref in refs.items()
        if not (root / ref.path).exists() or _digest(root / ref.path) != ref.fingerprint
    ]


class ScopeItem(Contract):
    party: Literal["project", "im"]
    material: Text
    depth: Text
    included: bool
    reason: Text


class Exposure(Contract):
    """已接触的参考材料及其去向；不能据此声称未接触参考的原创。"""

    material: Text
    first_contact: date
    contacted_by: Text
    influence: Text


class ReviewerConfig(Contract):
    id: RecordId
    method: Literal["program", "model"]
    model: str = ""
    criteria_groups: list[list[CriterionId]] = Field(default_factory=list)
    inputs: list[Text]
    excluded_inputs: list[Text]


class EvaluationConfig(Contract):
    schema_version: Literal[1] = 1
    id: RecordId
    status: Literal["draft", "frozen"]
    frozen_on: date | None = None
    purpose: Text
    files: dict[str, FileRef] = Field(
        description="rubric、protocol、conditions、rules、manifest、holdout_answers 等冻结内容"
    )
    rubric_version: Text
    evidence_scope: list[ScopeItem]
    reference_exposure: list[Exposure]
    reviewers: list[ReviewerConfig]
    adjudicator: ReviewerConfig
    debug_samples: list[RecordId]
    holdout_samples: list[RecordId]
    limitations: list[Text]


class GradeEvaluationRecords(Contract):
    """评价运行交换的全部记录类型；只用于导出 JSON Schema。"""

    config: EvaluationConfig
    documents: list[SourceDocument]
    evidence: list[EvidenceRecord]
    findings: list[EvaluationFinding]
    ratings: list[CriterionRating]
    adjudications: list[Adjudication]
    summaries: list[GradeSummary]
    comparisons: list[Comparison]
    samples: list[Sample]
    answers: list[SampleAnswer]
    detection: list[DetectionMetrics]
    review_runs: list[ReviewRun]
    adjudication_runs: list[AdjudicationRun]
    revision_runs: list[RevisionRun]
    constructed_findings: list[ConstructedFinding]
    calibration: CalibrationReport
    usage: UsageReport
    verification: VerificationReport
    extraction_spec: ExtractionSpec
    im_sources: list[ImSource]
    evidence_index: EvidenceIndex


def records_schema() -> dict[str, Any]:
    return GradeEvaluationRecords.model_json_schema()
