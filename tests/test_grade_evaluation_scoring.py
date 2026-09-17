"""汇总与比较遵守协议：重大失败不被总分抵消，分歧不平均，缺维不出总分。"""

from pathlib import Path

from teaching_harness.grade_evaluation.records import Adjudication, CriterionRating, load_rubric
from teaching_harness.grade_evaluation.scoring import compare, summarize

ROOT = Path(__file__).resolve().parents[1]
RUBRIC = load_rubric(ROOT / ".scratch/math-harness-delivery/year-planning-rubric.json")
FP = "c" * 64
EVIDENCE = {"ev:doc:1": "verified", "ev:doc:bad": "quote_mismatch"}


def rating(criterion, score, reviewer="r1", candidate="a", **change):
    status = "critical" if change.get("critical_failure") else "supported"
    value = {
        "candidate_id": candidate,
        "content_fingerprint": FP,
        "criterion_id": criterion,
        "reviewer_id": reviewer,
        "rubric_fingerprint": RUBRIC.fingerprint,
        "observability": "observable",
        "comparability": "comparable",
        "reviewed_scope": {"expected": [{"kind": "grade", "id": "g8"}]},
        "score": score,
        "evidence_refs": ["ev:doc:1"],
        "critical_failure": False,
        "critical_failure_reason": "反例" if change.get("critical_failure") else "",
        "object_checks": [
            {
                "object": {"kind": "grade", "id": "g8"},
                "status": status,
                "evidence_ids": ["ev:doc:1"],
                "note": "对象结论",
            }
        ],
        "score_rationale": "依据对象结论",
    }
    return CriterionRating.model_validate({**value, **change})


def agreed(scores, candidate="a", **per_criterion):
    ratings = []
    for i, score in enumerate(scores, start=1):
        change = per_criterion.get(f"Q{i}", {})
        for reviewer in ["r1", "r2"]:
            ratings.append(rating(f"Q{i}", score, reviewer, candidate, **change))
    return ratings


def result(summary, criterion):
    return next(c for c in summary.criteria if c.criterion_id == criterion)


def run(ratings, adjudications=(), candidate="a"):
    return summarize(candidate, FP, ratings, list(adjudications), RUBRIC, EVIDENCE)


def test_八维均经两次独立评分一致时按预定权重和等权分别汇总():
    summary = run(agreed([3, 3, 2, 2, 3, 2, 3, 4]))
    # (15·3+15·3+15·2+15·2+10·3+15·2+10·3+5·4)/4 = 65；等权 12.5·22/4 = 68.75
    assert summary.weighted_total == 65.0
    assert summary.equal_weight_total == 68.75
    assert summary.total_withheld == [] and not summary.critical_failure


def test_重大失败单独标记_总分再高也使比较判为对应范围不合格():
    failing = run(agreed([4, 4, 4, 4, 4, 4, 0, 4], Q7={"critical_failure": True}))
    assert failing.critical_failure and failing.weighted_total == 90.0
    other = run(agreed([2] * 8, candidate="b"), candidate="b")
    comparison = compare(failing, other, RUBRIC)
    assert comparison.verdict == "对应范围不合格" and comparison.failing == ["a"]


def test_两分分歧不平均_未裁定只给区间且不出总分_裁定后保留原始分():
    ratings = agreed([3] * 8)
    ratings[5] = rating("Q3", 1, "r2")
    summary = run(ratings)
    q3 = result(summary, "Q3")
    assert q3.status == "unresolved" and q3.score is None
    assert (q3.interval.low, q3.interval.high) == (1, 3)
    assert "同维分差至少2分" in q3.triggers
    assert summary.weighted_total is None and any("Q3" in r for r in summary.total_withheld)
    adjudication = {
        "id": "adj-q3",
        "candidate_id": "a",
        "content_fingerprint": FP,
        "criterion_id": "Q3",
        "original_ratings": [
            {"reviewer_id": "r1", "score": 3, "critical_failure": False},
            {"reviewer_id": "r2", "score": 1, "critical_failure": False},
        ],
        "triggers": ["同维分差至少2分"],
        "method": "independent_adjudicator",
        "adjudicator_id": "r3",
        "score": 2,
        "critical_failure": False,
        "supporting_evidence": ["ev:doc:1"],
        "rationale": "依赖有说明但强度不清",
    }
    settled = run(ratings, [Adjudication.model_validate(adjudication)])
    q3 = result(settled, "Q3")
    assert q3.status == "settled" and q3.score == 2
    assert sorted(o.score for o in q3.originals) == [1, 3]
    # (45+45+30+45+30+45+30+15)/4
    assert settled.weighted_total == 71.25


def test_一分差异也不平均():
    ratings = agreed([3] * 8)
    ratings[1] = rating("Q1", 2, "r2")
    q1 = result(run(ratings), "Q1")
    assert q1.status == "unresolved" and (q1.interval.low, q1.interval.high) == (2, 3)
    assert "同维分差至少2分" not in q1.triggers and q1.triggers


def test_缺维_不可观察_单次评分_引用失效都不计零也不出总分():
    ratings = [r for r in agreed([3] * 8) if r.criterion_id != "Q8"]
    ratings = [r for r in ratings if not (r.criterion_id == "Q6" and r.reviewer_id == "r2")]
    unobservable = {
        "observability": "unobservable",
        "object_checks": [
            {"object": {"kind": "grade", "id": "g8"}, "status": "unverified", "note": "受保护材料"}
        ],
    }
    ratings = [r for r in ratings if r.criterion_id != "Q2"] + [
        rating("Q2", None, reviewer, **unobservable) for reviewer in ["r1", "r2"]
    ]
    ratings = [r for r in ratings if r.criterion_id != "Q4"] + [
        rating("Q4", 3, reviewer, evidence_refs=["ev:doc:bad"]) for reviewer in ["r1", "r2"]
    ]
    summary = run(ratings)
    statuses = {c.criterion_id: c.status for c in summary.criteria}
    assert statuses == {
        "Q1": "settled",
        "Q2": "unobservable",
        "Q3": "settled",
        "Q4": "invalid",
        "Q5": "settled",
        "Q6": "single_review",
        "Q7": "settled",
        "Q8": "missing",
    }
    assert all(result(summary, c).score is None for c in ["Q2", "Q4", "Q8"])
    assert "引用失效" in " ".join(result(summary, "Q4").problems)
    assert summary.weighted_total is None and summary.equal_weight_total is None
    # 只报告已定维度及其覆盖权重，不重新归一为 100 分。
    assert summary.settled_weight == 15 + 15 + 10 + 10 and summary.settled_total == 50 * 3 / 4


def test_逐维不弱且至少一维更强时才判完整可比范围内更优():
    a = run(agreed([3] * 8))
    b = run(agreed([2] + [3] * 7, candidate="b"), candidate="b")
    comparison = compare(a, b, RUBRIC)
    assert comparison.verdict == "在完整可比范围内更优" and comparison.winner == "a"
    assert comparison.dimensions[0].judgment == "a_stronger"


def test_各有优劣时报告预定权重_等权与权重浮动后的方向():
    a = run(agreed([4, 2, 2, 2, 2, 2, 2, 2]))
    b = run(agreed([2, 2, 2, 2, 4, 2, 2, 2], candidate="b"), candidate="b")
    comparison = compare(a, b, RUBRIC)
    assert comparison.verdict == "各有优劣" and comparison.winner is None
    assert (comparison.weighted["a"], comparison.weighted["b"]) == (57.5, 55.0)
    # 等权时两者相同；Q1、Q5 各浮动 20% 后可相等，方向不稳。
    assert comparison.equal_weight_direction == "tie"
    assert comparison.weight_change_flips
    c = run(agreed([2, 2, 2, 2, 2, 2, 2, 4], candidate="c"), candidate="c")
    stable = compare(a, c, RUBRIC)
    assert stable.weighted_direction == "a" and not stable.weight_change_flips


def test_区间交叠不算确定优势_同分须经配对核查才称未见明确差异():
    ratings = agreed([3] * 8)
    ratings[1] = rating("Q1", 2, "r2")
    a = run(ratings)
    b = run(agreed([2] + [3] * 7, candidate="b"), candidate="b")
    comparison = compare(a, b, RUBRIC)
    assert comparison.dimensions[0].judgment == "undetermined"
    assert comparison.verdict == "尚不能分出优劣"
    same_a, same_b = run(agreed([3] * 8)), run(agreed([3] * 8, candidate="b"), candidate="b")
    assert compare(same_a, same_b, RUBRIC).verdict == "尚不能分出优劣"
    paired = compare(same_a, same_b, RUBRIC, paired_no_difference={f"Q{i}" for i in range(1, 9)})
    assert paired.verdict == "按当前判据未见明确差异"


def test_同一评阅者对两份方案的优劣方向相反时列为复核触发():
    a = agreed([3] * 8)
    b = agreed([3] * 8, candidate="b")
    a[2], a[3] = rating("Q2", 3, "r1"), rating("Q2", 2, "r2")
    b[2], b[3] = rating("Q2", 2, "r1", "b"), rating("Q2", 3, "r2", "b")
    comparison = compare(run(a), run(b, candidate="b"), RUBRIC, ratings=a + b)
    assert comparison.reviewer_direction_conflicts == ["Q2"]
    assert comparison.dimensions[1].judgment == "undetermined"


def test_不同评阅规则产生的评分不能一起汇总():
    import pytest

    ratings = agreed([3] * 8)
    ratings = [r.model_copy(update={"rules_fingerprint": "e" * 64}) for r in ratings]
    assert run(ratings).weighted_total is not None
    ratings[0] = ratings[0].model_copy(update={"rules_fingerprint": "f" * 64})
    with pytest.raises(ValueError, match="评阅规则"):
        run(ratings)


def established(criterion="Q5", severity="key_gap", id="promises:a:1:later-use-missing:x"):
    from teaching_harness.grade_evaluation.records import EvaluationFinding

    return EvaluationFinding.model_validate(
        {
            "id": id,
            "candidate_id": "a",
            "content_fingerprint": FP,
            "criterion_id": criterion,
            "object": {"kind": "revisit", "id": "8.F.B.4@unit_4:apply"},
            "origin": "program",
            "reviewer_id": "promises",
            "severity": severity,
            "claim": "承诺的回访没有位置",
            "requirement": "回访须有位置",
            "evidence_ids": ["ev:doc:1"],
            "counterexample": "反例" if severity == "critical" else "",
            "impact": "影响",
            "recheck": "复查",
        }
    )


def adjudicated(criterion, score, rejected=()):
    return Adjudication.model_validate(
        {
            "id": f"adj-{criterion.lower()}",
            "candidate_id": "a",
            "content_fingerprint": FP,
            "criterion_id": criterion,
            "original_ratings": [
                {"reviewer_id": "r1", "score": 4, "critical_failure": False},
                {"reviewer_id": "r2", "score": 4, "critical_failure": False},
            ],
            "triggers": ["已确认发现限制该维分数"],
            "method": "independent_adjudicator",
            "adjudicator_id": "r3",
            "score": score,
            "critical_failure": False,
            "supporting_evidence": ["ev:doc:1"],
            "rejected_findings": list(rejected),
            "rationale": "依据对象结论",
        }
    )


def test_已确认发现限制维度分_评分高于上限时判为冲突而不出总分():
    gap = established()
    summary = summarize("a", FP, agreed([4] * 8), [], RUBRIC, EVIDENCE, established=[gap])
    q5 = result(summary, "Q5")
    assert q5.status == "conflict" and "不高于 2" in " ".join(q5.problems)
    assert summary.weighted_total is None
    critical = established("Q7", "critical", "program:a:time-total:grade-total")
    q7 = result(
        summarize("a", FP, agreed([4] * 8), [], RUBRIC, EVIDENCE, established=[critical]), "Q7"
    )
    assert q7.status == "conflict" and "不高于 0" in " ".join(q7.problems)


def test_裁定只有用原文驳回发现后才能高于其上限():
    gap = established()
    ratings = agreed([4] * 8)
    kept = summarize("a", FP, ratings, [adjudicated("Q5", 4)], RUBRIC, EVIDENCE, established=[gap])
    assert result(kept, "Q5").status == "conflict"
    lowered = summarize(
        "a", FP, ratings, [adjudicated("Q5", 2)], RUBRIC, EVIDENCE, established=[gap]
    )
    assert result(lowered, "Q5").status == "settled" and result(lowered, "Q5").score == 2
    rebutted = summarize(
        "a", FP, ratings, [adjudicated("Q5", 4, [gap.id])], RUBRIC, EVIDENCE, established=[gap]
    )
    assert result(rebutted, "Q5").status == "settled" and rebutted.weighted_total == 100.0


def test_已确认重大发现使整体标记成立_冲突维度不参与比较():
    critical = established("Q7", "critical", "promises:a:2:time-double:reserve")
    # 评阅给 0 分但没有标重大失败时，已确认的重大发现仍触发整体标记。
    zero = summarize(
        "a", FP, agreed([4] * 6 + [0, 4]), [], RUBRIC, EVIDENCE, established=[critical]
    )
    assert result(zero, "Q7").status == "settled" and result(zero, "Q7").critical_failure
    assert zero.critical_failure
    # 评分高于上限时维度待裁定，但重大问题标记不等裁定。
    high = summarize("a", FP, agreed([4] * 8), [], RUBRIC, EVIDENCE, established=[critical])
    assert result(high, "Q7").status == "conflict" and high.critical_failure
    b = run(agreed([4] * 6 + [1, 4], candidate="b"), candidate="b")
    comparison = compare(high, b, RUBRIC)
    q7 = next(d for d in comparison.dimensions if d.criterion_id == "Q7")
    assert q7.judgment == "undetermined"
    assert comparison.winner != "a" and "a" in comparison.failing


def test_程序核对的结构事实不因裁定驳回而解除上限():
    fact = established("Q7", "critical", "program:a:time-total:grade-total")
    fact = fact.model_copy(update={"reviewer_id": "program"})
    ratings = agreed([4] * 8)
    summary = summarize(
        "a", FP, ratings, [adjudicated("Q7", 4, [fact.id])], RUBRIC, EVIDENCE, established=[fact]
    )
    assert result(summary, "Q7").status == "conflict"


def test_裁定可把依赖模型判断的发现降级_程序事实的严重度不可调整():
    probe = established("Q4", "critical", "probes:a:task_4:1").model_copy(
        update={"reviewer_id": "probes", "origin": "model"}
    )
    lowered = adjudicated("Q4", 2).model_copy(update={"adjusted_findings": {probe.id: "key_gap"}})
    summary = summarize("a", FP, agreed([2] * 8), [lowered], RUBRIC, EVIDENCE, established=[probe])
    q4 = result(summary, "Q4")
    assert (q4.status, q4.established_cap, q4.critical_failure) == ("settled", 2, False)
    assert not summary.critical_failure
    fact = established("Q7", "critical", "program:a:time-total:grade-total").model_copy(
        update={"reviewer_id": "program"}
    )
    ignored = adjudicated("Q7", 0).model_copy(update={"adjusted_findings": {fact.id: "local"}})
    kept = summarize("a", FP, agreed([2] * 8), [ignored], RUBRIC, EVIDENCE, established=[fact])
    assert result(kept, "Q7").established_cap == 0 and kept.critical_failure
