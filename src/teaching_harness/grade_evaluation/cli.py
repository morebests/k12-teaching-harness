"""年级课程评价与检查校准的本地命令；不依赖 LangSmith 或 Agent Server。

运行：uv run python scripts/evaluate_grade.py <命令>。结果按 runs.py 的记录类型写入
23 证据目录；模型原始消息只写入被忽略的 work/grade-evaluation/。
"""

import argparse
import asyncio
import hashlib
import json
import os
import re
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel, TypeAdapter

from teaching_harness.grade_evaluation import review as review_module
from teaching_harness.grade_evaluation import revision as revision_module
from teaching_harness.grade_evaluation.calibration import (
    Sample,
    SampleAnswer,
    assert_isolated,
    materialize,
    score_detection,
)
from teaching_harness.grade_evaluation.checks import (
    GradeCandidate,
    ProgramReview,
    load_candidate,
    program_review,
)
from teaching_harness.grade_evaluation.config import EvaluationConfig, config_drift, file_ref
from teaching_harness.grade_evaluation.evidence import cite, register, verify
from teaching_harness.grade_evaluation.records import (
    CriterionId,
    CriterionRating,
    EvaluationFinding,
    EvidenceRecord,
    SourceDocument,
    load_rubric,
)
from teaching_harness.grade_evaluation.review import (
    ADJUDICATION_RULES,
    ReviewResult,
    adjudicate,
    review_candidate,
    review_packet,
)
from teaching_harness.grade_evaluation.revision import close_after_recheck, revise
from teaching_harness.grade_evaluation.runs import (
    AdjudicationCall,
    AdjudicationRun,
    Agreement,
    CalibrationReport,
    CallRecord,
    ConstructedFinding,
    EvidenceIndex,
    ExtractionSpec,
    ImSource,
    IndexCheck,
    RecheckRecord,
    ReviewerLabels,
    ReviewRun,
    RevisionRun,
    UsageReport,
    UsageTotal,
    VerificationReport,
)
from teaching_harness.grade_evaluation.scoring import (
    Comparison,
    GradeSummary,
    compare,
    summarize,
)
from teaching_harness.graph import gemini

ROOT = Path(__file__).resolve().parents[3]
DELIVERY = ROOT / ".scratch/math-harness-delivery"
EVAL = DELIVERY / "evidence/23-grade-evaluation"
RESULTS = EVAL / "results"
WORK = ROOT / "work/grade-evaluation"
RUBRIC = DELIVERY / "year-planning-rubric.json"
BLUEPRINT = DELIVERY / "evidence/15-full-year-blueprint"
# 评价条件取初稿请求：原始任务要求与合成学校条件，不含修订反馈或旧稿。
CONDITIONS = BLUEPRINT / "initial/request.json"
# Q4／Q7 单独一组：调试轮显示与 Q2／Q8 合并时，探查与资源只得到概括性判断。
GROUPS: list[list[CriterionId]] = [["Q1"], ["Q3", "Q5", "Q6"], ["Q4", "Q7"], ["Q2", "Q8"]]


def _rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _write(path: Path, value: BaseModel) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.model_dump_json(indent=2) + "\n")


def _load[ModelT: BaseModel](path: Path, kind: type[ModelT]) -> ModelT:
    return kind.model_validate_json(path.read_bytes())


def _save_transcript(path: Path, messages: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(messages, ensure_ascii=False, indent=2) + "\n")


def samples() -> list[Sample]:
    adapter = TypeAdapter(list[Sample])
    return [
        *adapter.validate_json((EVAL / "samples/debug.json").read_bytes()),
        *adapter.validate_json((EVAL / "holdout/samples.json").read_bytes()),
    ]


def answers() -> list[SampleAnswer]:
    adapter = TypeAdapter(list[SampleAnswer])
    return [
        *adapter.validate_json((EVAL / "samples/debug-answers.json").read_bytes()),
        *adapter.validate_json((EVAL / "holdout/answers.json").read_bytes()),
    ]


def sample_by_id(sample_id: str) -> Sample:
    return next(s for s in samples() if s.id == sample_id)


def candidate(sample: Sample) -> GradeCandidate:
    return load_candidate(
        sample.id,
        EVAL / f"candidates/{sample.id}.json",
        request=CONDITIONS,
        knowledge=ROOT / sample.standards,
        root=ROOT,
        title=sample.note,
    )


def model() -> BaseChatModel:
    # 离线评价允许一次传输重试并放宽超时；生成图保持不重试。
    load_dotenv(ROOT / ".env")
    return gemini(timeout=900, max_retries=1)


def require_frozen() -> EvaluationConfig:
    """保留样本与裁定、修订只在冻结配置下运行；冻结内容改变后必须另建配置版本。"""
    config = EvaluationConfig.model_validate_json((EVAL / "config.json").read_bytes())
    drift = config_drift(config.files, ROOT)
    if config.status != "frozen" or drift:
        raise SystemExit(f"评价配置未冻结或冻结内容已改变：{drift}")
    return config


def _rules_fingerprint(path: Path) -> str:
    return file_ref(path, ROOT).fingerprint


def cmd_materialize(_: argparse.Namespace) -> None:
    for sample in samples():
        path = materialize(sample, ROOT, EVAL / "candidates")
        print(sample.id, _rel(path))


PROGRAM = TypeAdapter(dict[str, ProgramReview])


def cmd_program(_: argparse.Namespace) -> None:
    output = {}
    for sample in samples():
        output[sample.id] = program_review(candidate(sample))
        print(sample.id, len(output[sample.id].findings))
    (RESULTS / "program.json").parent.mkdir(parents=True, exist_ok=True)
    (RESULTS / "program.json").write_bytes(PROGRAM.dump_json(output, indent=2) + b"\n")


def _call(
    group: list[CriterionId], seconds: float, result: ReviewResult | None, error: str | None
) -> CallRecord:
    return CallRecord(
        criteria=group,
        seconds=round(seconds, 1),
        usage=result.usage if result else None,
        usage_complete=result.usage_complete if result else None,
        repairs=result.repairs if result else None,
        first_attempt_rejected_citations=(
            result.first_attempt_rejected_citations if result else None
        ),
        error=error,
    )


def _merge(
    results: list[ReviewResult],
    calls: list[CallRecord],
    sample: Sample,
    reviewer: str,
    cand: GradeCandidate,
    rules_fingerprint: str,
) -> ReviewRun:
    evidence = {e.id: e for r in results for e in r.evidence}
    return ReviewRun(
        sample_id=sample.id,
        reviewer_id=reviewer,
        candidate_id=cand.id,
        content_fingerprint=cand.fingerprint,
        model=os.environ.get("HARNESS_MODEL", "gemini-3.8-flash"),
        rules_fingerprint=rules_fingerprint,
        criteria=[c for r in results for c in r.criteria],
        ratings=[x for r in results for x in r.ratings],
        findings=[x for r in results for x in r.findings],
        evidence=list(evidence.values()),
        rejected_citations=[x for r in results for x in r.rejected_citations],
        rejected_findings=[x for r in results for x in r.rejected_findings],
        problems=[x for r in results for x in r.problems],
        usage={
            key: sum(r.usage[key] for r in results)
            for key in ("input_tokens", "output_tokens", "total_tokens")
        },
        calls=calls,
    )


def cmd_review(args: argparse.Namespace) -> None:
    chosen = [
        s
        for s in samples()
        if (not args.only or s.id in args.only.split(","))
        and (args.split == "all" or s.split == args.split or s.kind == args.split)
    ]
    if any(s.split == "holdout" for s in chosen):
        require_frozen()
    hidden = answers()
    rubric = load_rubric(RUBRIC)
    rules = review_module.RULES.read_text()
    rules_fingerprint = _rules_fingerprint(review_module.RULES)
    groups = [g for g in GROUPS if not args.groups or ",".join(g) in args.groups.split(";")]
    llm = model()
    # 原始消息按规则版本分目录，调试轮之间不互相覆盖。
    transcripts = WORK / f"transcripts/{args.reviewer}/{rules_fingerprint[:12]}"
    gate = asyncio.Semaphore(args.concurrency)

    async def one(sample: Sample) -> None:
        target = RESULTS / f"model/{args.reviewer}/{sample.id}.json"
        if target.exists() and not args.force:
            print("已有结果，跳过", target.name)
            return
        cand = candidate(sample)
        results, calls = [], []
        for group in groups:
            packet = review_packet(cand, group, rubric)
            # 装配后逐次核对：任何样本答案说明出现在输入中都拒绝调用。
            assert_isolated(packet, hidden)
            transcript: list[dict[str, Any]] = []
            started = time.monotonic()
            result, error = None, None
            try:
                async with gate:
                    result = await review_candidate(
                        llm,
                        cand,
                        group,
                        args.reviewer,
                        rubric,
                        rules=rules,
                        packet=packet,
                        transcript=transcript,
                    )
                results.append(result)
            except Exception as exc:  # noqa: BLE001 — 保留失败调用，继续其他维度组。
                error = f"{type(exc).__name__}: {str(exc)[:300]}"
            calls.append(_call(group, time.monotonic() - started, result, error))
            _save_transcript(transcripts / f"{sample.id}-{'-'.join(group)}.json", transcript)
            print(sample.id, group, error or "完成")
        _write(target, _merge(results, calls, sample, args.reviewer, cand, rules_fingerprint))

    async def run() -> None:
        await asyncio.gather(*(one(s) for s in chosen))

    asyncio.run(run())


def _runs(reviewer: str, directory: Path | None = None) -> dict[str, ReviewRun]:
    base = directory or RESULTS / f"model/{reviewer}"
    return {p.stem: _load(p, ReviewRun) for p in sorted(base.glob("*.json"))}


def _reviewers() -> list[str]:
    # 带连字符的是复查等附属运行，不参与校准统计。
    return sorted(p.name for p in (RESULTS / "model").iterdir() if p.is_dir() and "-" not in p.name)


def _status(records: list[EvidenceRecord], documents: dict[str, SourceDocument]) -> dict[str, str]:
    return {r.id: verify(r, documents, ROOT) for r in records}


def _agreement(first: dict[str, ReviewRun], second: dict[str, ReviewRun]) -> Agreement:
    pairs = []
    for sample_id, run in first.items():
        if sample_id not in second:
            continue
        peers = {r.criterion_id: r for r in second[sample_id].ratings}
        for rating in run.ratings:
            peer = peers.get(rating.criterion_id)
            if peer and rating.score is not None and peer.score is not None:
                pairs.append(
                    (rating.score, peer.score, rating.critical_failure != peer.critical_failure)
                )
    return Agreement(
        pairs=len(pairs),
        exact=sum(a == b for a, b, _ in pairs),
        differ_by_1=sum(abs(a - b) == 1 for a, b, _ in pairs),
        differ_by_2_or_more=sum(abs(a - b) >= 2 for a, b, _ in pairs),
        critical_disagreements=sum(c for _, _, c in pairs),
    )


def _labels(runs: dict[str, ReviewRun]) -> ReviewerLabels:
    calls = [c for r in runs.values() for c in r.calls]
    ratings = [rating for r in runs.values() for rating in r.ratings]
    return ReviewerLabels(
        samples=len(runs),
        failed_calls=sum(bool(c.error) for c in calls),
        incomplete_usage_calls=sum(c.usage_complete is False for c in calls),
        findings=sum(len(r.findings) for r in runs.values()),
        rejected_findings=sum(len(r.rejected_findings) for r in runs.values()),
        rejected_citations=sum(len(r.rejected_citations) for r in runs.values()),
        unverified_objects=sum(
            c.status == "unverified" for rating in ratings for c in rating.object_checks
        ),
        unobservable_ratings=sum(r.observability == "unobservable" for r in ratings),
        problems=sum(len(r.problems) for r in runs.values()),
        repairs=sum(c.repairs or 0 for c in calls),
        first_attempt_rejected_citations=sum(
            c.first_attempt_rejected_citations or 0 for c in calls
        ),
    )


def cmd_calibrate(_: argparse.Namespace) -> None:
    chosen = [s for s in samples() if s.kind != "base"]
    hidden = answers()
    program = PROGRAM.validate_json((RESULTS / "program.json").read_bytes())
    evidence = {e.id: e for r in program.values() for e in r.evidence}
    findings = {k: v.findings for k, v in program.items()}
    report = CalibrationReport(
        program=score_detection(chosen, hidden, findings, evidence, "program"),
        model={},
        per_sample={},
        labels={},
        agreement=None,
    )
    reviewers = _reviewers()
    for reviewer in reviewers:
        runs = {k: v for k, v in _runs(reviewer).items() if k in {s.id for s in chosen}}
        evidence = {e.id: e for r in runs.values() for e in r.evidence}
        findings = {k: v.findings for k, v in runs.items()}
        scored = [s for s in chosen if s.id in runs]
        report.model[reviewer] = score_detection(scored, hidden, findings, evidence, "model")
        report.labels[reviewer] = _labels(runs)
        report.per_sample[reviewer] = {
            s.id: next(iter(score_detection([s], hidden, findings, evidence, "model")))
            for s in scored
        }
    if len(reviewers) >= 2:
        report.agreement = _agreement(_runs(reviewers[0]), _runs(reviewers[1]))
    _write(RESULTS / "calibration.json", report)
    print(
        json.dumps(
            {k: v.model_dump() for k, v in report.labels.items()}, ensure_ascii=False, indent=2
        )
    )


def _ratings(
    sample_id: str, reviewers: list[str]
) -> tuple[list[CriterionRating], list[EvaluationFinding], list[EvidenceRecord]]:
    frozen = require_frozen().files["review_rules"].fingerprint
    ratings, findings, evidence = [], [], {}
    for reviewer in reviewers:
        run = _load(RESULTS / f"model/{reviewer}/{sample_id}.json", ReviewRun)
        if run.rules_fingerprint != frozen:
            raise SystemExit(f"{reviewer} 的评分不是按冻结规则产生的，不能汇总")
        ratings += run.bound_ratings()
        findings += run.findings
        evidence.update({e.id: e for e in run.evidence})
    return ratings, findings, list(evidence.values())


def _summary(sample: Sample, reviewers: list[str]) -> GradeSummary:
    cand = candidate(sample)
    ratings, _, evidence = _ratings(sample.id, reviewers)
    adjudications = []
    stored = RESULTS / f"adjudications/{sample.id}.json"
    if stored.exists():
        run = _load(stored, AdjudicationRun)
        evidence += run.evidence
        adjudications = run.adjudications
    status = _status(evidence, cand.documents)
    return summarize(
        sample.id, cand.fingerprint, ratings, adjudications, load_rubric(RUBRIC), status
    )


def cmd_summarize(args: argparse.Namespace) -> None:
    reviewers = args.reviewers.split(",")
    summaries = []
    for sample_id in args.candidates.split(","):
        summary = _summary(sample_by_id(sample_id), reviewers)
        summaries.append(summary)
        _write(RESULTS / f"summaries/{sample_id}.json", summary)
        print(sample_id, summary.weighted_total, summary.total_withheld)
    if len(summaries) == 2:
        a, b = summaries
        ratings = [*_ratings(a.candidate_id, reviewers)[0], *_ratings(b.candidate_id, reviewers)[0]]
        comparison = compare(a, b, load_rubric(RUBRIC), ratings=ratings)
        _write(RESULTS / f"comparisons/{a.candidate_id}--{b.candidate_id}.json", comparison)
        print(comparison.verdict, comparison.notes)


def cmd_adjudicate(args: argparse.Namespace) -> None:
    require_frozen()
    sample = sample_by_id(args.candidate)
    reviewers = args.reviewers.split(",")
    cand = candidate(sample)
    ratings, findings, evidence = _ratings(sample.id, reviewers)
    target = RESULTS / f"adjudications/{sample.id}.json"
    target.unlink(missing_ok=True)  # 按当前评分重新找未决维度，不沿用旧裁定。
    summary = _summary(sample, reviewers)
    rubric = load_rubric(RUBRIC)
    llm = model()
    stored = AdjudicationRun(
        adjudicator=args.adjudicator,
        rules_fingerprint=hashlib.sha256(ADJUDICATION_RULES.encode()).hexdigest(),
        adjudications=[],
        evidence=[],
        problems=[],
        usage=[],
    )
    pending = [r.criterion_id for r in summary.criteria if r.status == "unresolved"]

    async def run() -> None:
        # 同一事件循环内逐维裁定；模型客户端不能跨事件循环复用。
        for criterion in pending:
            transcript: list[dict[str, Any]] = []
            outcome = await adjudicate(
                llm,
                cand,
                criterion,
                ratings,
                findings,
                evidence,
                rubric,
                args.adjudicator,
                transcript,
            )
            _save_transcript(
                WORK / f"transcripts/{args.adjudicator}/{sample.id}-{criterion}.json", transcript
            )
            if outcome.adjudication:
                stored.adjudications.append(outcome.adjudication)
            stored.evidence += outcome.evidence
            stored.problems += [f"{criterion}：{p}" for p in outcome.problems]
            stored.usage.append(
                AdjudicationCall(
                    criterion=criterion,
                    usage_complete=outcome.usage_complete,
                    repairs=outcome.repairs,
                    **outcome.usage,
                )
            )
            print(
                criterion, outcome.adjudication.score if outcome.adjudication else outcome.problems
            )

    asyncio.run(run())
    _write(target, stored)


def _finding(
    args: argparse.Namespace, sample: Sample
) -> tuple[EvaluationFinding, list[EvidenceRecord]]:
    if args.finding_file:
        constructed = _load(Path(args.finding_file), ConstructedFinding)
        return constructed.finding, constructed.evidence
    run = _load(RESULTS / f"model/{args.reviewer}/{sample.id}.json", ReviewRun)
    return next(f for f in run.findings if f.id == args.finding), run.evidence


def _close(record: RevisionRun, sample: Sample) -> RevisionRun:
    """依修订稿复查结果决定发现是否关闭；可从已保存的复查结果重算。"""
    outcome = record.outcome
    revised = next((r for r in record.recheck if r.candidate == "revised"), None)
    if not (outcome.verdict == "revise" and outcome.accepted and revised and outcome.revised_path):
        return record
    changed = load_candidate(
        f"{sample.id}.revised",
        ROOT / outcome.revised_path,
        request=CONDITIONS,
        knowledge=ROOT / sample.standards,
        root=ROOT,
    )
    resolution = [
        cite(changed.document, ROOT, pointer, extraction="修订后的原文", recorded_by="program")
        for pointer in outcome.changed_pointers
    ]
    finding = close_after_recheck(outcome.finding, revised.review.findings, resolution)
    return record.model_copy(
        update={
            "outcome": outcome.model_copy(
                update={"finding": finding, "resolution_evidence": resolution}
            )
        }
    )


def cmd_revise(args: argparse.Namespace) -> None:
    require_frozen()
    sample = sample_by_id(args.candidate)
    slug = re.sub(r"[^a-z0-9]+", "-", args.finding).strip("-")
    out = RESULTS / f"revision/{slug}"
    if (out / "outcome.json").exists() and not args.force:
        # 已有真实修订与复查时不再调用模型，只按保存的复查结果重算发现状态。
        record = _close(_load(out / "outcome.json", RevisionRun), sample)
        _write(out / "outcome.json", record)
        print("已按保存的复查结果重算", record.outcome.finding.status)
        return
    cand = candidate(sample)
    finding, evidence = _finding(args, sample)
    outcome = asyncio.run(revise(model(), cand, finding, evidence, out, answers()))
    _save_transcript(WORK / f"transcripts/reviser/{slug}.json", outcome.transcript)
    record = RevisionRun(sample_id=sample.id, outcome=outcome)
    if outcome.revised_path and outcome.accepted:
        revised = load_candidate(
            f"{sample.id}.revised",
            ROOT / outcome.revised_path,
            request=CONDITIONS,
            knowledge=ROOT / sample.standards,
            root=ROOT,
        )
        group = next(g for g in GROUPS if finding.criterion_id in g)
        rubric = load_rubric(RUBRIC)
        for label, target in [("original", cand), ("revised", revised)]:
            packet = review_packet(target, group, rubric)
            assert_isolated(packet, answers())
            transcript: list[dict[str, Any]] = []
            reviewed = asyncio.run(
                review_candidate(
                    model(),
                    target,
                    group,
                    f"{args.reviewer}-recheck",
                    rubric,
                    packet=packet,
                    transcript=transcript,
                )
            )
            _save_transcript(WORK / f"transcripts/reviser/{slug}-{label}-recheck.json", transcript)
            same = [
                f
                for f in reviewed.findings
                if f.object == finding.object and f.criterion_id == finding.criterion_id
            ]
            record.recheck.append(
                RecheckRecord(candidate=label, same_object_findings=same, review=reviewed)  # type: ignore[arg-type]
            )
        record = _close(record, sample)
    _write(out / "outcome.json", record)
    print(outcome.verdict, outcome.accepted, outcome.problems, record.outcome.finding.status)


def cmd_index(_: argparse.Namespace) -> None:
    """IM 与本项目规划材料按同一证据契约登记、抽查和核验。"""
    spec = _load(EVAL / "extractions.json", ExtractionSpec)
    sources = {
        s.id: s
        for s in TypeAdapter(list[ImSource]).validate_json((EVAL / "im-sources.json").read_bytes())
    }
    documents: dict[str, SourceDocument] = {}
    problems = []
    for item in spec.documents:
        path = ROOT / item.snapshot
        if not path.exists():
            problems.append(f"{item.id}：本机缺少快照 {item.snapshot}")
            continue
        document = register(
            path,
            root=ROOT,
            id=item.id,
            party=item.party,
            role=item.role,
            title=item.title,
            locator=item.locator,
            retrieved=item.retrieved,
            access=item.access,
            access_note=item.access_note,
        )
        if item.id in sources and sources[item.id].sha256 != document.fingerprint:
            problems.append(f"{item.id}：快照与取得时的指纹不符")
        documents[document.id] = document
    evidence, checks = [], []
    for entry in spec.entries:
        source = documents.get(entry.document)
        if source is None:
            checks.append(
                IndexCheck(
                    document=entry.document,
                    party="unknown",
                    objects=entry.objects,
                    status="document_missing",
                    spot_check=entry.spot_check,
                )
            )
            continue
        record = cite(
            source,
            ROOT,
            entry.locator,
            quote=entry.quote,
            extraction=entry.extraction,
            recorded_by="human",
            objects=entry.objects,
        )
        evidence.append(record)
        checks.append(
            IndexCheck(
                document=source.id,
                party=source.party,
                objects=entry.objects,
                status=verify(record, documents, ROOT),
                evidence_id=record.id,
                spot_check=entry.spot_check,
            )
        )
    _write(
        RESULTS / "index.json",
        EvidenceIndex(
            attribution=spec.attribution,
            documents=list(documents.values()),
            evidence=evidence,
            checks=checks,
            unobservable=spec.unobservable,
            problems=problems,
        ),
    )
    print(len(evidence), "条证据", problems)


def cmd_verify(_: argparse.Namespace) -> None:
    """重新核验所有已保存证据；快照缺失与原文变化分别报告。"""
    counts: dict[str, dict[str, int]] = {}

    def add(
        label: str, records: list[EvidenceRecord], documents: dict[str, SourceDocument]
    ) -> None:
        for status in _status(records, documents).values():
            counts.setdefault(label, {}).setdefault(status, 0)
            counts[label][status] += 1

    for reviewer in _reviewers():
        for run in _runs(reviewer).values():
            add(reviewer, run.evidence, candidate(sample_by_id(run.sample_id)).documents)
    index = _load(RESULTS / "index.json", EvidenceIndex)
    add("index", index.evidence, {d.id: d for d in index.documents})
    for path in sorted((RESULTS / "adjudications").glob("*.json")):
        add(
            "adjudications",
            _load(path, AdjudicationRun).evidence,
            candidate(sample_by_id(path.stem)).documents,
        )
    report = VerificationReport(counts=counts)
    _write(RESULTS / "verification.json", report)
    print(json.dumps(counts, ensure_ascii=False, indent=2))


def cmd_freeze(_: argparse.Namespace) -> None:
    draft = json.loads((EVAL / "config-draft.json").read_text())
    package = Path(__file__).parent
    files = {
        "rubric": RUBRIC,
        "protocol": DELIVERY / "year-planning-evaluation.md",
        "conditions": CONDITIONS,
        "review_rules": review_module.RULES,
        "revision_rules": revision_module.RULES,
        # 装配评阅输入与应查清单的代码；改动它们等于改变评阅条件。
        "review_code": package / "review.py",
        "checklist_code": package / "checks.py",
        "debug_samples": EVAL / "samples/debug.json",
        "debug_answers": EVAL / "samples/debug-answers.json",
        "holdout": EVAL / "holdout",
        "extractions": EVAL / "extractions.json",
        "im_sources": EVAL / "im-sources.json",
    }
    config = EvaluationConfig.model_validate(
        {
            **draft,
            "status": "frozen",
            "frozen_on": datetime.now(UTC).astimezone().date(),
            "rubric_version": load_rubric(RUBRIC).version,
            "files": {k: file_ref(v, ROOT) for k, v in files.items()},
            "debug_samples": [s.id for s in samples() if s.split == "debug"],
            "holdout_samples": [s.id for s in samples() if s.split == "holdout"],
        }
    )
    _write(EVAL / "config.json", config)
    print("已冻结", {k: v.fingerprint[:12] for k, v in config.files.items()})


def cmd_usage(_: argparse.Namespace) -> None:
    totals: dict[str, UsageTotal] = {}

    def add(label: str, usage: dict[str, int] | None, complete: bool | None) -> None:
        if usage is None:
            return
        total = totals.setdefault(label, UsageTotal())
        total.calls += 1
        total.incomplete_calls += complete is False
        total.input_tokens += usage["input_tokens"]
        total.output_tokens += usage["output_tokens"]
        total.total_tokens += usage["total_tokens"]

    for reviewer in _reviewers():
        for run in _runs(reviewer).values():
            for call in run.calls:
                add(reviewer, call.usage, call.usage_complete)
    # 调试轮存档只保存规则冻结前的结果；冻结后的调试结果就在 model/ 中，不重复计。
    for directory in sorted((RESULTS / "debug-rounds").glob("*/*")):
        for run in _runs("", directory).values():
            for call in run.calls:
                add(f"{directory.name}-{directory.parent.name}", call.usage, call.usage_complete)
    for path in sorted((RESULTS / "adjudications").glob("*.json")):
        stored = _load(path, AdjudicationRun)
        for adjudication_call in stored.usage:
            add(
                stored.adjudicator,
                adjudication_call.model_dump(
                    include={"input_tokens", "output_tokens", "total_tokens"}
                ),
                adjudication_call.usage_complete,
            )
    for path in sorted((RESULTS / "revision").glob("*/outcome.json")):
        record = _load(path, RevisionRun)
        add("reviser", record.outcome.usage, record.outcome.usage_complete)
        for item in record.recheck:
            add("recheck", item.review.usage, item.review.usage_complete)
    report = UsageReport(totals=totals)
    _write(RESULTS / "usage.json", report)
    print(report.model_dump_json(indent=2))


def cmd_show(args: argparse.Namespace) -> None:
    """逐条列出一次评阅的维度分、对象结论、发现及其原文位置，并与样本答案对照。"""
    directory = RESULTS / f"debug-rounds/{args.round}/{args.reviewer}" if args.round else None
    run = _runs(args.reviewer, directory)[args.sample]
    evidence = {e.id: e for e in run.evidence}

    def quotes(ids: list[str]) -> list[str]:
        return [f"{evidence[i].locator}「{evidence[i].quote[:60]}」" for i in ids if i in evidence]

    print(
        f"样本 {args.sample}｜评阅 {args.reviewer}｜模型 {run.model}｜规则指纹 {run.rules_fingerprint[:12]}"
    )
    print(
        f"原始消息：work/grade-evaluation/transcripts/{args.reviewer}/{run.rules_fingerprint[:12]}/{args.sample}-<维度组>.json"
    )
    for call in run.calls:
        print(
            f"调用 {call.criteria}：{call.seconds} 秒，用量 {call.usage}，补交 {call.repairs}，错误 {call.error}"
        )
    for problem in run.problems:
        print("问题：", problem)
    for rating in run.ratings:
        print(
            f"\n[{rating.criterion_id}] 分数 {rating.score} 区间 {rating.interval} 重大失败 {rating.critical_failure}"
        )
        print("  理由：", rating.score_rationale)
        for check in rating.object_checks:
            if args.all or check.status != "supported":
                print(
                    f"  - {check.object.kind}:{check.object.id} {check.status}：{check.note} {quotes(check.evidence_ids)}"
                )
    print("\n发现：")
    for f in run.findings:
        print(
            f"  - {f.id} [{f.criterion_id}/{f.severity}] {f.object.kind}:{f.object.id}：{f.claim} {quotes(f.evidence_ids)}"
        )
    for c in run.rejected_citations:
        print(f"  × 失效引用 {c.criterion_id} {c.pointer}「{c.quote[:60]}」：{c.reason}")
    for rejected in run.rejected_findings:
        print(
            f"  × 拒收发现 {rejected.criterion_id}：{rejected.finding.get('claim')}（{rejected.reason}）"
        )
    sample = sample_by_id(args.sample)
    answer = next((a for a in answers() if a.sample_id == args.sample), None)
    if answer and sample.kind != "base":
        [metrics] = score_detection(
            [sample], [answer], {sample.id: run.findings}, evidence, "model"
        )
        print(
            f"\n对照答案：应检出 {metrics.expected}，检出 {metrics.detected}，漏报 {metrics.missed}，误报候选 {metrics.false_positives}"
        )
        for issue in answer.expected:
            print(f"  答案 {issue.id}（{issue.severity}，{issue.pointers}）：{issue.description}")


def _table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(lines)


def cmd_report(_: argparse.Namespace) -> None:
    """由结果文件生成报告表格；叙述与人工核对写在证据 README。"""
    calibration = _load(RESULTS / "calibration.json", CalibrationReport)
    parts = ["# 23 校准结果表（由 `evaluate_grade.py report` 生成）"]
    rows = [
        [
            origin,
            m.split,
            m.samples,
            m.control_samples,
            m.expected,
            m.detected,
            m.location_correct,
            m.severity_matched,
            ", ".join(m.missed) or "—",
            ", ".join(m.critical_missed) or "—",
            len(m.false_positives),
            len(m.other_findings),
        ]
        for origin, metrics in [("program", calibration.program), *calibration.model.items()]
        for m in metrics
    ]
    parts.append(
        "## 检出、漏报与误报候选（自动匹配；人工核对见 README）\n\n"
        + _table(
            [
                "检查",
                "样本集",
                "样本",
                "合法对照",
                "应检出",
                "检出",
                "位置正确",
                "严重度一致",
                "漏报",
                "重大漏报",
                "误报候选",
                "其他发现",
            ],
            rows,
        )
    )
    rows = [
        [
            reviewer,
            sample_id,
            m.expected,
            m.detected,
            ", ".join(m.missed) or "—",
            ", ".join(m.false_positives) or "—",
            len(m.other_findings),
        ]
        for reviewer, per_sample in calibration.per_sample.items()
        for sample_id, m in per_sample.items()
    ]
    parts.append(
        "## 模型逐样本\n\n"
        + _table(["评阅", "样本", "应检出", "检出", "漏报", "误报候选", "其他发现"], rows)
    )
    fields = list(ReviewerLabels.model_fields)
    parts.append(
        "## 模型作答可靠性\n\n"
        + _table(
            ["评阅", *fields],
            [[k, *v.model_dump().values()] for k, v in calibration.labels.items()],
        )
    )
    if calibration.agreement:
        a = calibration.agreement.model_dump()
        parts.append("## r1 与 r2 的逐维评分一致性\n\n" + _table(list(a), [list(a.values())]))
    for path in sorted((RESULTS / "summaries").glob("*.json")):
        summary = _load(path, GradeSummary)
        rows = [
            [
                c.criterion_id,
                c.status,
                c.score,
                c.interval.low if c.interval else "—",
                c.interval.high if c.interval else "—",
                c.critical_failure,
                "; ".join(f"{o.reviewer_id}={o.score}" for o in c.originals),
                "; ".join(c.triggers) or "—",
                len(c.problems),
            ]
            for c in summary.criteria
        ]
        parts.append(
            f"## 汇总：{summary.candidate_id}\n\n加权总分：{summary.weighted_total}；等权：{summary.equal_weight_total}；"
            f"重大失败：{summary.critical_failure}；已定维度权重 {summary.settled_weight}，其加权分 {summary.settled_total}；"
            f"未出总分原因：{'、'.join(summary.total_withheld) or '—'}\n\n"
            + _table(
                [
                    "维度",
                    "状态",
                    "分数",
                    "区间下限",
                    "区间上限",
                    "重大失败",
                    "原始分",
                    "复核触发",
                    "问题数",
                ],
                rows,
            )
        )
    for path in sorted((RESULTS / "comparisons").glob("*.json")):
        c = _load(path, Comparison)
        rows = [
            [d.criterion_id, d.judgment, d.a_status, d.b_status, d.reason] for d in c.dimensions
        ]
        parts.append(
            f"## 比较：{c.a_id} 对 {c.b_id}\n\n裁定：{c.verdict}；加权方向 {c.weighted_direction}；等权方向 {c.equal_weight_direction}；"
            f"权重浮动翻转 {c.weight_change_flips}；评阅方向冲突 {c.reviewer_direction_conflicts or '—'}；说明：{'；'.join(c.notes) or '—'}\n\n"
            + _table(["维度", "判断", "a 状态", "b 状态", "理由"], rows)
        )
    usage_path = RESULTS / "usage.json"
    if usage_path.exists():
        usage = _load(usage_path, UsageReport)
        parts.append(
            "## 模型用量\n\n"
            + _table(
                ["角色", "调用", "用量不完整", "输入", "输出", "合计"],
                [
                    [
                        k,
                        v.calls,
                        v.incomplete_calls,
                        v.input_tokens,
                        v.output_tokens,
                        v.total_tokens,
                    ]
                    for k, v in usage.totals.items()
                ],
            )
        )
    (RESULTS / "report-tables.md").write_text("\n\n".join(parts) + "\n")
    print(_rel(RESULTS / "report-tables.md"))


def main() -> None:
    parser = argparse.ArgumentParser(description="年级课程评价与检查校准")
    sub = parser.add_subparsers(required=True)
    sub.add_parser("materialize", help="按样本记录生成候选副本").set_defaults(run=cmd_materialize)
    sub.add_parser("program", help="对全部样本运行程序检查").set_defaults(run=cmd_program)
    review = sub.add_parser("review", help="模型独立评阅")
    review.add_argument("--reviewer", required=True)
    review.add_argument("--split", default="debug", choices=["debug", "holdout", "base", "all"])
    review.add_argument("--only", default="")
    review.add_argument("--groups", default="", help="例如 Q1;Q3,Q5,Q6")
    review.add_argument("--concurrency", type=int, default=3)
    review.add_argument("--force", action="store_true")
    review.set_defaults(run=cmd_review)
    sub.add_parser("calibrate", help="统计程序与模型的检出、漏报和误报").set_defaults(
        run=cmd_calibrate
    )
    summary = sub.add_parser("summarize", help="汇总独立评分，两份候选时同时比较")
    summary.add_argument("--candidates", required=True)
    summary.add_argument("--reviewers", default="r1,r2")
    summary.set_defaults(run=cmd_summarize)
    adj = sub.add_parser("adjudicate", help="对未决维度做模型辅助独立裁定")
    adj.add_argument("--candidate", required=True)
    adj.add_argument("--reviewers", default="r1,r2")
    adj.add_argument("--adjudicator", default="r3")
    adj.set_defaults(run=cmd_adjudicate)
    rev = sub.add_parser("revise", help="把一条发现交回模型核实并修订副本")
    rev.add_argument("--candidate", required=True)
    rev.add_argument("--reviewer", required=True)
    rev.add_argument("--finding", required=True)
    rev.add_argument("--finding-file", default="", help="人工构造发现的 JSON 文件")
    rev.add_argument("--force", action="store_true", help="重新调用模型，覆盖已有修订结果")
    rev.set_defaults(run=cmd_revise)
    sub.add_parser("index", help="登记并核验 IM 与本项目的规划证据").set_defaults(run=cmd_index)
    sub.add_parser("verify", help="重新核验全部证据").set_defaults(run=cmd_verify)
    sub.add_parser("freeze", help="冻结评价配置").set_defaults(run=cmd_freeze)
    sub.add_parser("usage", help="汇总模型调用用量").set_defaults(run=cmd_usage)
    sub.add_parser("report", help="由结果文件生成校准表格").set_defaults(run=cmd_report)
    show = sub.add_parser("show", help="查看一次模型评阅的逐条结论并对照答案")
    show.add_argument("--reviewer", required=True)
    show.add_argument("--sample", required=True)
    show.add_argument("--round", default="", help="查看调试轮存档，例如 round-1")
    show.add_argument("--all", action="store_true", help="同时列出 supported 对象")
    show.set_defaults(run=cmd_show)
    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
