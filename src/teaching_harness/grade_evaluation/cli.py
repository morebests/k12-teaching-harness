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
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel, TypeAdapter

from teaching_harness.grade_evaluation import review as review_module
from teaching_harness.grade_evaluation import revision as revision_module
from teaching_harness.grade_evaluation import stages as stages_module
from teaching_harness.grade_evaluation.calibration import (
    DetectionMetrics,
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
    Origin,
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
    ProbeCacheEntry,
    RecheckRecord,
    ReviewerLabels,
    ReviewRun,
    RevisionRun,
    SetReport,
    StageLabels,
    StageRun,
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
from teaching_harness.grade_evaluation.stages import (
    ModelPromises,
    ProbeModelOutput,
    check_promises,
    normalize_probe,
    probe_cache_key,
    promise_packet,
    review_promises,
    review_statements,
    run_probe_models,
    solver_packet,
    stage_rules,
    statement_packet,
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


# 样本集：调试集；第一版保留集（由规则作者设计，第一轮校准后已公开，v2 中只作调试）；
# 第二版保留集（由不接触规则与检查实现的子代理设计）。
SETS = {
    "debug": ("samples/debug.json", "samples/debug-answers.json"),
    "holdout-v1": ("holdout/samples.json", "holdout/answers.json"),
    "holdout-v2": ("holdout-2/samples.json", "holdout-2/answers.json"),
}
STAGES = ("promises", "probes", "statements")


def sample_sets() -> dict[str, list[Sample]]:
    adapter = TypeAdapter(list[Sample])
    return {
        label: adapter.validate_json((EVAL / paths[0]).read_bytes())
        for label, paths in SETS.items()
        if (EVAL / paths[0]).exists()
    }


def samples() -> list[Sample]:
    return [s for group in sample_sets().values() for s in group]


def answers() -> list[SampleAnswer]:
    adapter = TypeAdapter(list[SampleAnswer])
    return [
        a
        for _, path in SETS.values()
        if (EVAL / path).exists()
        for a in adapter.validate_json((EVAL / path).read_bytes())
    ]


def _selected(args: argparse.Namespace) -> list[Sample]:
    return [
        s
        for label, group in sample_sets().items()
        for s in group
        if (not args.only or s.id in args.only.split(","))
        and args.split in {"all", label, s.split, s.kind}
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


def model_name() -> str:
    return os.environ.get("HARNESS_MODEL", "gemini-3.8-flash")


def model() -> BaseChatModel:
    # 离线评价允许一次传输重试并放宽超时；生成图保持不重试。
    load_dotenv(ROOT / ".env")
    return gemini(timeout=900, max_retries=1)


def require_frozen(chosen: Iterable[Sample] = ()) -> EvaluationConfig:
    """保留样本与裁定、修订只在冻结配置下运行；冻结内容改变后必须另建配置版本。

    所选保留样本还须列在该配置中，旧配置不能放行新保留集。
    """
    config = EvaluationConfig.model_validate_json((EVAL / "config.json").read_bytes())
    drift = config_drift(config.files, ROOT)
    if config.status != "frozen" or drift:
        raise SystemExit(f"评价配置未冻结或冻结内容已改变：{drift}")
    listed = set(config.debug_samples + config.holdout_samples)
    unlisted = [s.id for s in chosen if s.split == "holdout" and s.id not in listed]
    if unlisted:
        raise SystemExit(f"冻结配置 {config.id} 没有列出这些保留样本：{unlisted}")
    return config


def visible() -> set[str]:
    """可以运行程序检查和统计结果的样本：调试样本，以及冻结配置已列出的样本。"""
    config = EvaluationConfig.model_validate_json((EVAL / "config.json").read_bytes())
    listed = config.debug_samples + config.holdout_samples if config.status == "frozen" else []
    return {s.id for s in samples() if s.split != "holdout"} | set(listed)


def _rules_fingerprint(path: Path) -> str:
    return file_ref(path, ROOT).fingerprint


def cmd_materialize(_: argparse.Namespace) -> None:
    for sample in samples():
        path = materialize(sample, ROOT, EVAL / "candidates")
        print(sample.id, _rel(path))


PROGRAM = TypeAdapter(dict[str, ProgramReview])


def cmd_program(_: argparse.Namespace) -> None:
    output = {}
    shown = visible()
    for sample in samples():
        if sample.id not in shown:
            continue
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
        model=model_name(),
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
    chosen = _selected(args)
    if any(s.split == "holdout" for s in chosen):
        require_frozen(chosen)
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


STAGE_RULES = {
    "promises": ["promises"],
    "statements": ["statements"],
    "probes": ["solver", "probe"],
}


def _stage_rules(stage: str) -> tuple[list[str], str]:
    """专项检查使用的各份规则正文及合并指纹；探查核查依次为求解与核查规则。"""
    texts = [stage_rules(name) for name in STAGE_RULES[stage]]
    return texts, hashlib.sha256("\n".join(texts).encode()).hexdigest()


def _figures(sample: Sample, cand: GradeCandidate, task_id: str) -> dict[str, Any]:
    """题面图件的绘制参数；图件与该底稿生成时的资源放在同一运行目录。"""
    assets = (ROOT / sample.standards).parent / "assets"
    task = next(t for t in cand.content.tasks if t.id == task_id)
    figures = {}
    for block in task.blocks:
        if block.type != "image":
            continue
        path = assets / Path(block.src).with_suffix(".json").name
        if path.exists():
            figures[block.src] = {"alt": block.alt, "parameters": json.loads(path.read_text())}
    return figures


def cmd_stages(args: argparse.Namespace) -> None:
    chosen = _selected(args)
    stages = args.stage.split(",") if args.stage != "all" else list(STAGES)
    if unknown := set(stages) - set(STAGES):
        raise SystemExit(f"未知的专项检查：{sorted(unknown)}")
    if args.recheck:
        # 重新判定只处理已有的承诺抽取，不调用模型。
        for sample in chosen:
            target = RESULTS / f"stages/promises/{sample.id}.json"
            if target.exists():
                recheck(sample, target)
        return
    if any(s.split == "holdout" for s in chosen):
        require_frozen(chosen)
    hidden = answers()
    llm = model()
    gate = asyncio.Semaphore(args.concurrency)
    locks: dict[str, asyncio.Lock] = {}

    async def probe_output(
        sample: Sample, cand: GradeCandidate, task_id: str, texts: list[str]
    ) -> tuple[str, ProbeModelOutput]:
        solver, reviewer = texts
        figures = _figures(sample, cand, task_id)
        key = probe_cache_key(cand, task_id, figures, "\n".join(texts), model=model_name())
        path = RESULTS / f"stages/probes/cache/{key}.json"
        async with locks.setdefault(key, asyncio.Lock()):
            if path.exists():
                return key, _load(path, ProbeCacheEntry).output
            assert_isolated({**solver_packet(cand, task_id), "figures": figures}, hidden)
            async with gate:
                output = await run_probe_models(
                    llm, cand, task_id, rules=reviewer, solver_rules=solver, assets=figures
                )
            _save_transcript(WORK / f"transcripts/stages/probes/{key[:12]}.json", output.transcript)
            _write(
                path,
                ProbeCacheEntry(
                    key=key,
                    task_id=task_id,
                    first_sample=sample.id,
                    model=model_name(),
                    output=output,
                ),
            )
            return key, output

    async def one(sample: Sample, stage: str) -> None:
        target = RESULTS / f"stages/{stage}/{sample.id}.json"
        if target.exists() and not args.force:
            return
        cand = candidate(sample)
        texts, fingerprint_ = _stage_rules(stage)
        text = "\n".join(texts)
        run = StageRun(
            sample_id=sample.id,
            stage=stage,  # type: ignore[arg-type]
            model=model_name(),  # type: ignore[arg-type]
            rules_fingerprint=fingerprint_,
            seconds=0,
        )
        started = time.monotonic()
        transcript: list[dict[str, Any]] = []
        try:
            if stage == "promises":
                assert_isolated(promise_packet(cand), hidden)
                async with gate:
                    run.promises = await review_promises(
                        llm, cand, rules=text, transcript=transcript
                    )
            elif stage == "statements":
                assert_isolated(statement_packet(cand), hidden)
                async with gate:
                    run.statements = await review_statements(
                        llm, cand, rules=text, transcript=transcript
                    )
            else:
                for task in cand.content.tasks:
                    key, output = await probe_output(sample, cand, task.id, texts)
                    run.probe_cache.append(key)
                    run.probes.append(normalize_probe(cand, task.id, output))
        except Exception as exc:  # noqa: BLE001 — 保留失败，继续其他样本。
            run.error = f"{type(exc).__name__}: {str(exc)[:300]}"
        run.seconds = round(time.monotonic() - started, 1)
        if transcript:
            _save_transcript(
                WORK / f"transcripts/stages/{stage}/{fingerprint_[:12]}/{sample.id}.json",
                transcript,
            )
        _write(target, run)
        print(sample.id, stage, run.error or f"{len(run.findings())} 条发现")

    async def main() -> None:
        await asyncio.gather(*(one(sample, stage) for sample in chosen for stage in stages))

    asyncio.run(main())


def recheck(sample: Sample, target: Path) -> None:
    """只改了程序判定时，用已保存的承诺抽取重新判定。

    抽取时引用失效或单元不存在的承诺没有保存，它们的问题记录沿用；其余问题按本次判定。
    """
    run = _load(target, StageRun)
    if run.error or run.promises is None:
        return
    old = run.promises
    extracted = ModelPromises(promises=[c.promise for c in old.promises])
    fresh = check_promises(candidate(sample), extracted)
    run.promises = fresh.model_copy(
        update={
            "rejected_citations": old.rejected_citations,
            "problems": list(dict.fromkeys([*old.problems, *fresh.problems])),
            "usage": old.usage,
            "usage_complete": old.usage_complete,
            "repairs": old.repairs,
        }
    )
    _write(target, run)
    print(sample.id, "promises 重新判定", f"{len(run.findings())} 条发现")


def _stage_runs(stage: str) -> dict[str, StageRun]:
    return {
        p.stem: _load(p, StageRun) for p in sorted((RESULTS / f"stages/{stage}").glob("*.json"))
    }


def _established(sample_id: str) -> tuple[list[EvaluationFinding], list[EvidenceRecord]]:
    """程序与专项检查得出、未被驳回的发现；它们按协议限制评分。"""
    program = PROGRAM.validate_json((RESULTS / "program.json").read_bytes()).get(sample_id)
    findings = list(program.findings) if program else []
    evidence = list(program.evidence) if program else []
    for stage in STAGES:
        path = RESULTS / f"stages/{stage}/{sample_id}.json"
        if path.exists():
            run = _load(path, StageRun)
            findings += run.findings()
            evidence += run.evidence()
    return [f for f in findings if f.status not in {"rebutted", "resolved"}], evidence


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


def _stage_labels(runs: dict[str, StageRun]) -> StageLabels:
    results = [r for run in runs.values() for r in run.results()]
    return StageLabels(
        samples=len(runs),
        errors=sum(bool(run.error) for run in runs.values()),
        findings=sum(len(r.findings) for r in results),
        rejected_findings=sum(len(r.rejected_findings) for r in results),
        rejected_citations=sum(len(r.rejected_citations) for r in results),
        problems=sum(len(r.problems) for r in results),
        repairs=sum(r.repairs for r in results),
    )


def cmd_calibrate(_: argparse.Namespace) -> None:
    hidden = answers()
    # 保留集只在冻结配置列出它之后统计，冻结前不能看到其任何结果。
    shown = visible()
    program = PROGRAM.validate_json((RESULTS / "program.json").read_bytes())
    stages = {
        stage: {k: v for k, v in _stage_runs(stage).items() if k in shown} for stage in STAGES
    }
    reviewers = _reviewers()
    runs = {
        reviewer: {k: v for k, v in _runs(reviewer).items() if k in shown} for reviewer in reviewers
    }
    report = CalibrationReport(
        sets={},
        labels={},
        stage_labels={stage: _stage_labels(r) for stage, r in stages.items() if r},
        agreement=_agreement(runs[reviewers[0]], runs[reviewers[1]])
        if len(reviewers) >= 2
        else None,
    )

    def detect(
        label: str,
        chosen: list[Sample],
        findings: dict[str, list[EvaluationFinding]],
        evidence: list[EvidenceRecord],
        responsible: Origin,
    ) -> DetectionMetrics:
        [metrics] = score_detection(
            chosen,
            hidden,
            findings,
            {e.id: e for e in evidence},
            responsible,
            origins={"model", "program"} if responsible == "model" else {"program"},
            group=label,
        )
        return metrics

    for label, group in sample_sets().items():
        chosen = [s for s in group if s.kind != "base"]
        if not chosen or not {s.id for s in chosen} <= shown:
            continue
        ids = [s.id for s in chosen]
        checks: dict[str, list[EvaluationFinding]] = {
            i: list(program[i].findings) for i in ids if i in program
        }
        check_evidence = [e for i in ids if i in program for e in program[i].evidence]
        entry = SetReport(
            samples=ids,
            program=detect(label, chosen, checks, check_evidence, "program"),
            stages={},
            reviewers={},
            combined={},
            per_sample={},
        )
        for stage, stage_runs in stages.items():
            done = [s for s in chosen if s.id in stage_runs]
            if not done:
                continue
            entry.stages[stage] = detect(
                label,
                done,
                {s.id: stage_runs[s.id].findings() for s in done},
                [e for s in done for e in stage_runs[s.id].evidence()],
                "model",
            )
            for s in done:
                checks.setdefault(s.id, []).extend(stage_runs[s.id].findings())
                check_evidence += stage_runs[s.id].evidence()
        for reviewer in reviewers:
            done = [s for s in chosen if s.id in runs[reviewer]]
            if not done:
                continue
            own = {s.id: runs[reviewer][s.id].findings for s in done}
            own_evidence = [e for s in done for e in runs[reviewer][s.id].evidence]
            entry.reviewers[reviewer] = detect(label, done, own, own_evidence, "model")
            merged = {s.id: [*own[s.id], *checks.get(s.id, [])] for s in done}
            entry.combined[reviewer] = detect(
                label, done, merged, own_evidence + check_evidence, "model"
            )
            entry.per_sample[reviewer] = {
                s.id: detect(s.id, [s], own, own_evidence, "model") for s in done
            }
            entry.per_sample[f"{reviewer}+checks"] = {
                s.id: detect(s.id, [s], merged, own_evidence + check_evidence, "model")
                for s in done
            }
        report.sets[label] = entry
    for reviewer in reviewers:
        non_base = {k: v for k, v in runs[reviewer].items() if sample_by_id(k).kind != "base"}
        report.labels[reviewer] = _labels(non_base)
    _write(RESULTS / "calibration.json", report)
    print(
        json.dumps(
            {k: {r: m.detected for r, m in v.combined.items()} for k, v in report.sets.items()},
            ensure_ascii=False,
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
    established, checked = _established(sample.id)
    evidence += checked
    adjudications = []
    stored = RESULTS / f"adjudications/{sample.id}.json"
    if stored.exists():
        run = _load(stored, AdjudicationRun)
        evidence += run.evidence
        adjudications = run.adjudications
    status = _status(evidence, cand.documents)
    return summarize(
        sample.id,
        cand.fingerprint,
        ratings,
        adjudications,
        load_rubric(RUBRIC),
        status,
        established=established,
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
    sample = sample_by_id(args.candidate)
    require_frozen([sample])
    reviewers = args.reviewers.split(",")
    cand = candidate(sample)
    ratings, findings, evidence = _ratings(sample.id, reviewers)
    established, checked = _established(sample.id)
    evidence += checked
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
    pending = [r.criterion_id for r in summary.criteria if r.status in {"unresolved", "conflict"}]

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
                established=established,
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
    sample = sample_by_id(args.candidate)
    require_frozen([sample])
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
    for sample_id, review in PROGRAM.validate_json((RESULTS / "program.json").read_bytes()).items():
        add("program", review.evidence, candidate(sample_by_id(sample_id)).documents)
    for stage in STAGES:
        for stage_run in _stage_runs(stage).values():
            add(
                stage,
                stage_run.evidence(),
                candidate(sample_by_id(stage_run.sample_id)).documents,
            )
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


def cmd_freeze(args: argparse.Namespace) -> None:
    draft = json.loads((EVAL / args.draft).read_text())
    package = Path(__file__).parent
    holdout = args.holdout_sets.split(",")
    files = {
        "rubric": RUBRIC,
        "protocol": DELIVERY / "year-planning-evaluation.md",
        "conditions": CONDITIONS,
        "review_rules": review_module.RULES,
        "revision_rules": revision_module.RULES,
        # 装配评阅输入与应查清单的代码；改动它们等于改变评阅条件。
        "review_code": package / "review.py",
        "checklist_code": package / "checks.py",
        "stage_code": package / "stages.py",
        "scoring_code": package / "scoring.py",
        **{
            f"stage_rules_{n}": stages_module.RESOURCES / f"grade-{n}.md"
            for n in ("promises", "solver", "probe", "statements")
        },
        "debug_samples": EVAL / "samples/debug.json",
        "debug_answers": EVAL / "samples/debug-answers.json",
        **{
            label.replace("-", "_"): (EVAL / SETS[label][0]).parent
            for label in SETS
            if label != "debug" and (EVAL / SETS[label][0]).exists()
        },
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
            "debug_samples": [
                s.id for label, g in sample_sets().items() if label not in holdout for s in g
            ],
            "holdout_samples": [
                s.id for label, g in sample_sets().items() if label in holdout for s in g
            ],
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
    for stage in ("promises", "statements"):
        for stage_run in _stage_runs(stage).values():
            for result in stage_run.results():
                add(stage, result.usage, result.usage_complete)
    # 探查按题面缓存，用量只在缓存条目上计一次。
    for path in sorted((RESULTS / "stages/probes/cache").glob("*.json")):
        entry = _load(path, ProbeCacheEntry)
        add("probes", entry.output.usage, entry.output.usage_complete)
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


def _metric_row(name: str, m: DetectionMetrics) -> list[Any]:
    return [
        name,
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


def cmd_report(_: argparse.Namespace) -> None:
    """由结果文件生成报告表格；叙述与人工核对写在证据 README。"""
    calibration = _load(RESULTS / "calibration.json", CalibrationReport)
    parts = ["# 23 校准结果表（由 `evaluate_grade.py report` 生成；自动匹配，人工核对见 README）"]
    headers = [
        "检查",
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
    ]
    for label, entry in calibration.sets.items():
        rows = []
        if entry.program:
            rows.append(_metric_row("程序", entry.program))
        rows += [_metric_row(f"专项：{k}", m) for k, m in entry.stages.items()]
        rows += [_metric_row(f"整体评阅 {k}", m) for k, m in entry.reviewers.items()]
        rows += [_metric_row(f"{k}＋程序＋专项", m) for k, m in entry.combined.items()]
        parts.append(f"## 样本集 {label}\n\n" + _table(headers, rows))
        sample_rows = [
            [
                who,
                sample_id,
                m.expected,
                m.detected,
                ", ".join(m.missed) or "—",
                ", ".join(m.false_positives) or "—",
                len(m.other_findings),
            ]
            for who, per in entry.per_sample.items()
            for sample_id, m in per.items()
        ]
        parts.append(
            f"### {label} 逐样本\n\n"
            + _table(
                ["检查", "样本", "应检出", "检出", "漏报", "误报候选", "其他发现"], sample_rows
            )
        )
    fields = list(ReviewerLabels.model_fields)
    parts.append(
        "## 整体评阅的作答可靠性\n\n"
        + _table(
            ["评阅", *fields],
            [[k, *v.model_dump().values()] for k, v in calibration.labels.items()],
        )
    )
    stage_fields = list(StageLabels.model_fields)
    parts.append(
        "## 专项检查的作答可靠性\n\n"
        + _table(
            ["专项", *stage_fields],
            [[k, *v.model_dump().values()] for k, v in calibration.stage_labels.items()],
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
                "；".join(c.problems) or "—",
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
                    "问题",
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
    review.add_argument(
        "--split",
        default="debug",
        help="all、样本集名（debug／holdout-v1／holdout-v2）、holdout 或 base",
    )
    review.add_argument("--only", default="")
    review.add_argument("--groups", default="", help="例如 Q1;Q3,Q5,Q6")
    review.add_argument("--concurrency", type=int, default=3)
    review.add_argument("--force", action="store_true")
    review.set_defaults(run=cmd_review)
    stages = sub.add_parser("stages", help="专项检查：承诺、探查、数学表述")
    stages.add_argument(
        "--stage", default="all", help="promises、probes、statements，逗号分隔或 all"
    )
    stages.add_argument("--split", default="debug", help="all、样本集名、holdout 或 base")
    stages.add_argument("--only", default="")
    stages.add_argument("--concurrency", type=int, default=3)
    stages.add_argument("--force", action="store_true")
    stages.add_argument(
        "--recheck", action="store_true", help="承诺核查只按已保存的抽取重新判定，不调用模型"
    )
    stages.set_defaults(run=cmd_stages)
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
    freeze = sub.add_parser("freeze", help="冻结评价配置")
    freeze.add_argument("--draft", default="config-draft.json")
    freeze.add_argument("--holdout-sets", default="holdout-v1", help="作为保留集的样本集，逗号分隔")
    freeze.set_defaults(run=cmd_freeze)
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
