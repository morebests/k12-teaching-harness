"""按评估协议把独立评分收敛为维度结论，并在两份候选之间作可重算的比较。"""

import itertools
import re
from collections.abc import Iterable
from typing import Literal

from pydantic import Field

from teaching_harness.contracts import Contract, Fingerprint
from teaching_harness.grade_evaluation.records import (
    CRITERIA,
    Adjudication,
    CriterionId,
    CriterionRating,
    LoadedRubric,
    OriginalRating,
    RecordId,
    Score,
    ScoreInterval,
    rating_problems,
    score_bounds,
)

Status = Literal[
    "settled",
    "unresolved",
    "unobservable",
    "not_comparable",
    "missing",
    "single_review",
    "invalid",
]
DISAGREEMENT = "评分不一致，须依据对象清单复核后形成共同值或独立裁定"


class CriterionResult(Contract):
    criterion_id: CriterionId
    weight: int
    status: Status
    score: Score | None = None
    interval: ScoreInterval | None = None
    critical_failure: bool = False
    originals: list[OriginalRating] = Field(default_factory=list)
    adjudication_id: RecordId | None = None
    triggers: list[str] = Field(default_factory=list)
    problems: list[str] = Field(default_factory=list)

    def bounds(self) -> tuple[int, int] | None:
        return score_bounds(self.score, self.interval)


class GradeSummary(Contract):
    candidate_id: RecordId
    content_fingerprint: Fingerprint
    rubric_version: str
    rubric_fingerprint: Fingerprint
    criteria: list[CriterionResult]
    critical_failure: bool
    weighted_total: float | None
    equal_weight_total: float | None
    total_withheld: list[str]
    settled_weight: int
    settled_total: float


def original_rating(rating: CriterionRating) -> OriginalRating:
    return OriginalRating(
        reviewer_id=rating.reviewer_id,
        score=rating.score,
        interval=rating.interval,
        critical_failure=rating.critical_failure,
    )


def _citations(rating: CriterionRating) -> set[str]:
    return set(rating.evidence_refs) | {e for c in rating.object_checks for e in c.evidence_ids}


def rating_triggers(ratings: list[CriterionRating]) -> list[str]:
    triggers = []
    if len({r.critical_failure for r in ratings}) > 1:
        triggers.append("重大失败结论不一致")
    bounds = [b for r in ratings for b in _bounds(r)]
    if bounds and max(bounds) - min(bounds) >= 2:
        triggers.append("同维分差至少2分")
    values = {(r.score, r.interval, r.critical_failure) for r in ratings}
    if len(values) > 1 or any(r.interval for r in ratings):
        triggers.append(DISAGREEMENT)
    return triggers


def _bounds(rating: CriterionRating) -> list[int]:
    return list(score_bounds(rating.score, rating.interval) or ())


def _settle(
    criterion: CriterionId,
    weight: int,
    ratings: list[CriterionRating],
    adjudication: Adjudication | None,
    evidence: dict[str, str],
) -> CriterionResult:
    empty = CriterionResult(criterion_id=criterion, weight=weight, status="missing")
    if not ratings:
        return empty
    problems = []
    for rating in ratings:
        problems += [f"{rating.reviewer_id}：{p}" for p in rating_problems(rating)]
        broken = sorted(e for e in _citations(rating) if evidence.get(e) != "verified")
        if broken:
            problems.append(f"{rating.reviewer_id}：引用失效 {broken}")
    triggers = rating_triggers(ratings)
    base = empty.model_copy(
        update={
            "originals": [original_rating(r) for r in ratings],
            "triggers": triggers,
            "problems": problems,
        }
    )

    def result(status: Status, **update: object) -> CriterionResult:
        return base.model_copy(update={"status": status, **update})

    if adjudication is not None:
        broken = [e for e in adjudication.supporting_evidence if evidence.get(e) != "verified"]
        if broken:
            return result("invalid", problems=[*problems, f"裁定引用失效 {broken}"])
        return result(
            "settled" if adjudication.score is not None else "unresolved",
            score=adjudication.score,
            interval=adjudication.interval,
            critical_failure=adjudication.critical_failure,
            adjudication_id=adjudication.id,
        )
    if problems:
        return result("invalid")
    if any(r.observability == "unobservable" for r in ratings):
        return result("unobservable")
    if any(r.comparability == "not_comparable" for r in ratings):
        return result("not_comparable")
    first = ratings[0]
    if len({r.reviewer_id for r in ratings}) < 2:
        return result(
            "single_review",
            score=first.score,
            interval=first.interval,
            critical_failure=first.critical_failure,
        )
    if not triggers:
        return result("settled", score=first.score, critical_failure=first.critical_failure)
    bounds = [b for r in ratings for b in _bounds(r)]
    return result(
        "unresolved",
        interval=ScoreInterval(low=min(bounds), high=max(bounds)),
        critical_failure=all(r.critical_failure for r in ratings),
    )


def _total(results: Iterable[CriterionResult], weights: dict[str, float]) -> float:
    return round(sum(weights[r.criterion_id] * (r.score or 0) / 4 for r in results), 4)


def summarize(
    candidate_id: str,
    content_fingerprint: str,
    ratings: list[CriterionRating],
    adjudications: list[Adjudication],
    rubric: LoadedRubric,
    evidence: dict[str, str],
) -> GradeSummary:
    """evidence 为每条证据的当前核验结果；未核验的引用按失效处理。"""
    own = [
        r
        for r in ratings
        if r.candidate_id == candidate_id and r.content_fingerprint == content_fingerprint
    ]
    if any(r.rubric_fingerprint != rubric.fingerprint for r in own):
        raise ValueError("评分使用的规则版本与本次汇总不一致，须按同一规则重评")
    if len({r.rules_fingerprint for r in own}) > 1:
        raise ValueError("评分来自不同的评阅规则，不能一起汇总")
    decided = {
        a.criterion_id: a
        for a in adjudications
        if a.candidate_id == candidate_id and a.content_fingerprint == content_fingerprint
    }
    results = [
        _settle(
            c.id,
            c.weight,
            [r for r in own if r.criterion_id == c.id],
            decided.get(c.id),
            evidence,
        )
        for c in rubric.criteria
    ]
    settled = [r for r in results if r.status == "settled"]
    withheld = [f"{r.criterion_id}：{r.status}" for r in results if r.status != "settled"]
    weights: dict[str, float] = {c.id: float(c.weight) for c in rubric.criteria}
    complete = not withheld
    return GradeSummary(
        candidate_id=candidate_id,
        content_fingerprint=content_fingerprint,
        rubric_version=rubric.version,
        rubric_fingerprint=rubric.fingerprint,
        criteria=results,
        critical_failure=any(r.critical_failure for r in settled),
        weighted_total=_total(results, weights) if complete else None,
        equal_weight_total=(
            _total(results, {c: 100 / len(CRITERIA) for c in CRITERIA}) if complete else None
        ),
        total_withheld=withheld,
        settled_weight=sum(r.weight for r in settled),
        settled_total=_total(settled, weights),
    )


Judgment = Literal[
    "a_stronger",
    "b_stronger",
    "same_score",
    "no_clear_difference",
    "undetermined",
    "not_comparable",
]
Direction = Literal["a", "b", "tie"]


class DimensionComparison(Contract):
    criterion_id: CriterionId
    judgment: Judgment
    a_status: Status
    b_status: Status
    reason: str


class Comparison(Contract):
    a_id: RecordId
    b_id: RecordId
    rubric_fingerprint: Fingerprint
    dimensions: list[DimensionComparison]
    verdict: str
    winner: RecordId | None
    failing: list[RecordId]
    weighted: dict[str, float] | None
    weighted_direction: Direction | None
    equal_weight_direction: Direction | None
    weight_change_flips: bool | None
    reviewer_direction_conflicts: list[CriterionId]
    notes: list[str]


def _direction(value: float) -> Direction:
    return "a" if value > 1e-9 else "b" if value < -1e-9 else "tie"


def _judge(
    a: CriterionResult, b: CriterionResult, paired: set[str], conflict: bool
) -> tuple[Judgment, str]:
    unusable = {"missing", "unobservable", "not_comparable"}
    if a.status in unusable or b.status in unusable:
        return "not_comparable", "至少一方不可观察、不可比或缺少评分"
    ra, rb = a.bounds(), b.bounds()
    if ra is None or rb is None or conflict:
        return "undetermined", "评阅者方向相反或缺少可用分数" if conflict else "缺少可用分数"
    if ra[0] > rb[1]:
        return "a_stronger", f"{ra} 高于 {rb}"
    if rb[0] > ra[1]:
        return "b_stronger", f"{rb} 高于 {ra}"
    if a.status == b.status == "settled":
        if a.criterion_id in paired:
            return "no_clear_difference", "同分且配对核查未发现明确差异"
        return "same_score", "同分；未做配对核查，不代表等效"
    return "undetermined", f"未决区间 {ra} 与 {rb} 交叠"


def _conflicts(ratings: list[CriterionRating], a_id: str, b_id: str) -> list[CriterionId]:
    found: list[CriterionId] = []
    for criterion in CRITERIA:
        signs = set()
        for reviewer in {r.reviewer_id for r in ratings}:
            pair = [
                next(
                    (
                        r.score
                        for r in ratings
                        if r.candidate_id == side
                        and r.reviewer_id == reviewer
                        and r.criterion_id == criterion
                    ),
                    None,
                )
                for side in (a_id, b_id)
            ]
            if pair[0] is not None and pair[1] is not None and pair[0] != pair[1]:
                signs.add(pair[0] > pair[1])
        if len(signs) > 1:
            found.append(criterion)
    return found


def _change(rubric: LoadedRubric) -> float:
    match = re.search(r"(\d+)%", rubric.sensitivity)
    if not match:
        raise ValueError("规则数据未给出权重浮动幅度")
    return int(match[1]) / 100


def compare(
    a: GradeSummary,
    b: GradeSummary,
    rubric: LoadedRubric,
    *,
    paired_no_difference: set[str] | None = None,
    ratings: list[CriterionRating] | None = None,
) -> Comparison:
    """协议第 6 节的综合裁定；加权结论只作按预定取舍的补充，并报告方向稳定性。"""
    if {a.rubric_fingerprint, b.rubric_fingerprint} != {rubric.fingerprint}:
        raise ValueError("两份候选必须使用同一规则版本评分")
    conflicts = _conflicts(ratings or [], a.candidate_id, b.candidate_id)
    dimensions = []
    for ra, rb in zip(a.criteria, b.criteria, strict=True):
        judgment, reason = _judge(
            ra, rb, paired_no_difference or set(), ra.criterion_id in conflicts
        )
        dimensions.append(
            DimensionComparison(
                criterion_id=ra.criterion_id,
                judgment=judgment,
                a_status=ra.status,
                b_status=rb.status,
                reason=reason,
            )
        )
    judgments = {d.judgment for d in dimensions}
    failing = [s.candidate_id for s in (a, b) if s.critical_failure]
    complete = a.weighted_total is not None and b.weighted_total is not None
    weighted = equal = flips = None
    notes = []
    if complete:
        diffs = {
            x.criterion_id: (x.score or 0) - (y.score or 0)
            for x, y in zip(a.criteria, b.criteria, strict=True)
        }
        base: dict[str, int] = {c.id: c.weight for c in rubric.criteria}
        weighted = _direction(sum(base[k] * d for k, d in diffs.items()))
        equal = _direction(sum(diffs.values()))
        change = _change(rubric)
        # 方向只取决于 Σw·d 的符号；归一不改变符号，线性式的极值在各权重上下限的组合处。
        flips = any(
            _direction(sum(base[k] * f * diffs[k] for k, f in zip(CRITERIA, factors, strict=True)))
            != weighted
            for factors in itertools.product((1 - change, 1 + change), repeat=len(CRITERIA))
        )
    winner = None
    if failing:
        verdict = rubric.verdicts["failing"]
        notes.append("有已确认重大失败的一方在对应范围不合格；另一方未失败不自动证明全部更优")
    elif judgments & {"undetermined", "not_comparable"}:
        verdict = rubric.verdicts["undetermined"]
        notes.append("存在未决区间、不可比或缺失维度，差异不能确定")
    elif "a_stronger" in judgments and "b_stronger" in judgments:
        verdict = rubric.verdicts["mixed"]
    elif judgments & {"a_stronger", "b_stronger"}:
        verdict = rubric.verdicts["better"]
        winner = a.candidate_id if "a_stronger" in judgments else b.candidate_id
    elif judgments == {"no_clear_difference"}:
        verdict = rubric.verdicts["no_difference"]
    else:
        verdict = rubric.verdicts["undetermined"]
        notes.append("同分维度尚未做配对核查")
    return Comparison(
        a_id=a.candidate_id,
        b_id=b.candidate_id,
        rubric_fingerprint=rubric.fingerprint,
        dimensions=dimensions,
        verdict=verdict,
        winner=winner,
        failing=failing,
        weighted=(
            {a.candidate_id: a.weighted_total, b.candidate_id: b.weighted_total}
            if complete and a.weighted_total is not None and b.weighted_total is not None
            else None
        ),
        weighted_direction=weighted,
        equal_weight_direction=equal,
        weight_change_flips=flips,
        reviewer_direction_conflicts=conflicts,
        notes=notes,
    )
