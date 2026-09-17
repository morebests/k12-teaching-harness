"""校准样本由记录在案的改动生成；统计区分漏报、误报与定位，评阅输入不得带答案。"""

import hashlib
import json
from pathlib import Path

import pytest

from teaching_harness.grade_evaluation.calibration import (
    ExpectedIssue,
    IsolationError,
    MutationError,
    Sample,
    SampleAnswer,
    assert_isolated,
    materialize,
    score_detection,
)
from teaching_harness.grade_evaluation.records import EvaluationFinding, EvidenceRecord

ROOT = Path(__file__).resolve().parents[1]
BASE = (
    ".scratch/math-harness-delivery/evidence/15-full-year-blueprint/final/content/curriculum.json"
)


def sample(mutations, **change):
    value = {
        "id": "h-sample",
        "split": "holdout",
        "kind": "injected",
        "base": BASE,
        "base_fingerprint": hashlib.sha256((ROOT / BASE).read_bytes()).hexdigest(),
        "standards": BASE.replace("content/curriculum.json", "knowledge.json"),
        "mutations": mutations,
        "note": "对终稿的一处改动",
    }
    return Sample.model_validate({**value, **change})


def test_改动按记录生成候选副本_原文不符或结构无效时拒绝(tmp_path):
    mutations = [
        {
            "op": "replace_text",
            "path": "/units/7/exit",
            "old": "能通过双向列联表分析分类数据的相关性。",
            "new": "",
        },
        {"op": "move", "path": "/units/5", "from_path": "/units/4"},
        {"op": "remove", "path": "/tasks/3/blocks/0"},
        {"op": "rename", "path": "", "old": "unit_8_bivariate_stats", "new": "u08"},
    ]
    path = materialize(sample(mutations), ROOT, tmp_path)
    content = json.loads(path.read_text())
    original = json.loads((ROOT / BASE).read_text())
    assert "列联表" not in content["units"][7]["exit"]
    assert content["units"][5]["id"] == original["units"][4]["id"]
    assert len(content["tasks"][3]["blocks"]) == len(original["tasks"][3]["blocks"]) - 1
    assert "unit_8_bivariate_stats" not in json.dumps(content)
    assert content["units"][7]["id"] == "u08"
    assert content["tasks"][3]["unit_ids"] == ["u08"]
    assert json.loads((ROOT / BASE).read_text()) == original
    with pytest.raises(MutationError, match="原文"):
        materialize(
            sample([{"op": "replace_text", "path": "/units/7/exit", "old": "不存在", "new": ""}]),
            ROOT,
            tmp_path,
        )
    with pytest.raises(MutationError, match="年级课程"):
        materialize(sample([{"op": "remove", "path": "/units"}]), ROOT, tmp_path)
    with pytest.raises(MutationError, match="没有"):
        materialize(
            sample([{"op": "rename", "path": "", "old": "unit_99", "new": "u99"}]), ROOT, tmp_path
        )
    with pytest.raises(MutationError, match="指纹"):
        materialize(sample([], base_fingerprint="0" * 64), ROOT, tmp_path)


def finding(id, criterion, object_id, severity="key_gap", evidence=("ev:1",), origin="model"):
    return EvaluationFinding.model_validate(
        {
            "id": id,
            "candidate_id": "s",
            "content_fingerprint": "d" * 64,
            "criterion_id": criterion,
            "object": {"kind": "goal", "id": object_id},
            "origin": origin,
            "reviewer_id": "r1",
            "severity": severity,
            "claim": "问题",
            "requirement": "要求",
            "evidence_ids": list(evidence),
            "counterexample": "反例",
            "impact": "影响",
            "recheck": "复查",
        }
    )


def evidence(id, locator):
    return EvidenceRecord(
        id=id,
        document_id="s",
        document_fingerprint="d" * 64,
        locator=locator,
        quote="原文",
        extraction="提取",
        recorded_by="model",
    )


def answer(sample_id, kind, expected=(), protected=()):
    return SampleAnswer.model_validate(
        {
            "sample_id": sample_id,
            "kind": kind,
            "expected": list(expected),
            "protected_pointers": list(protected),
            "rationale": f"{sample_id} 的答案说明，评阅时不可见",
        }
    )


def issue(id, criteria, object_id, pointer, severity="key_gap", keywords=()):
    return ExpectedIssue.model_validate(
        {
            "id": id,
            "criteria": criteria,
            "objects": [{"kind": "goal", "id": object_id}],
            "pointers": [pointer],
            "severity": severity,
            "detectable_by": ["model"],
            "description": f"{id}：评价安排早于学习机会",
            "keywords": list(keywords),
        }
    )


def test_检出统计区分定位正确_漏报_合法对照误报与其他发现():
    samples = [
        sample([], id="found", split="debug"),
        sample([], id="missed"),
        sample([], id="control", kind="control"),
    ]
    answers = [
        answer("found", "injected", [issue("e-found", ["Q6"], "8.G.B.8", "/goals/26")]),
        answer(
            "missed", "injected", [issue("e-missed", ["Q1"], "8.SP.A.4", "/goals/33", "critical")]
        ),
        answer("control", "control", protected=["/units/4"]),
    ]
    records = {
        e.id: e
        for e in [
            evidence("ev:1", "/goals/26/allocations/1/opportunity"),
            evidence("ev:2", "/units/4/narrative"),
            evidence("ev:3", "/units/0/exit"),
        ]
    }
    findings = {
        "found": [
            finding("f1", "Q5", "8.G.B.8"),
            finding("f2", "Q2", "8.EE.A.1", evidence=["ev:3"]),
        ],
        "missed": [finding("f3", "Q6", "8.F.B.4", evidence=["ev:3"])],
        "control": [
            finding("f4", "Q3", "unit_5", evidence=["ev:2"]),
            finding("f5", "Q3", "unit_5", severity="local", evidence=["ev:2"]),
            finding("f6", "Q1", "8.G.A.1", evidence=["ev:1"], origin="program"),
        ],
    }
    metrics = {m.split: m for m in score_detection(samples, answers, findings, records, "model")}
    debug, holdout = metrics["debug"], metrics["holdout"]
    # 定位在答案位置且对象一致，即使维度不同也算检出。
    assert (debug.expected, debug.detected, debug.location_correct) == (1, 1, 1)
    assert debug.other_findings == ["f2"]
    assert holdout.missed == ["e-missed"] and holdout.critical_missed == ["e-missed"]
    assert holdout.false_positives == ["f4"] and holdout.control_samples == 1
    # 程序发现不计入模型统计；程序只对标明可由程序发现的问题负责。
    assert "f6" not in holdout.other_findings
    # 组合检查：模型负责的问题，由模型与程序发现合并判定。
    combined = {
        m.split: m
        for m in score_detection(
            samples, answers, findings, records, "model", origins={"model", "program"}
        )
    }
    assert "f6" in combined["holdout"].other_findings
    program = {m.split: m for m in score_detection(samples, answers, findings, records, "program")}
    assert program["debug"].expected == 0 and program["holdout"].expected == 0
    assert program["holdout"].other_findings == ["f6"]


def test_答案关键词用于区分同一位置的不同问题():
    samples = [sample([], id="stats")]
    answers = [
        answer(
            "stats",
            "known_miss",
            [
                issue("e-data", ["Q4"], "task_4", "/tasks/3", "critical", ["数据", "调查"]),
                issue("e-causal", ["Q4"], "task_4", "/tasks/3", keywords=["因果"]),
            ],
        )
    ]
    records = {"ev:1": evidence("ev:1", "/tasks/3/solution")}
    found = finding("f-causal", "Q4", "task_4")
    found = found.model_copy(update={"claim": "把斜率解释成个体因果效应"})
    [metrics] = score_detection(samples, answers, {"stats": [found]}, records, "model")
    assert metrics.missed == ["e-data"] and metrics.detected == 1


def test_一条发现只计入一个预期问题():
    samples = [sample([], id="stats")]
    both = ["范围", "调查"]
    answers = [
        answer(
            "stats",
            "known_miss",
            [
                issue("e-range", ["Q4"], "task_4", "/tasks/3", keywords=both),
                issue("e-survey", ["Q4"], "task_4", "/tasks/3", "critical", both),
            ],
        )
    ]
    records = {"ev:1": evidence("ev:1", "/tasks/3/solution")}
    first = finding("f-1", "Q4", "task_4").model_copy(update={"claim": "把调查的样本范围写错"})
    [single] = score_detection(samples, answers, {"stats": [first]}, records, "model")
    assert (single.detected, single.missed) == (1, ["e-survey"])
    second = first.model_copy(update={"id": "f-2"})
    [pair] = score_detection(samples, answers, {"stats": [first, second]}, records, "model")
    assert (pair.detected, pair.missed) == (2, [])
    # 在检出数最多的分配中，再让位置正确的发现尽量多。
    wide = [
        issue("e-range", ["Q4"], "task_4", "/tasks/3/solution", keywords=both),
        issue("e-survey", ["Q4"], "task_4", "/tasks/3", "critical", both),
    ]
    records["ev:2"] = evidence("ev:2", "/tasks/3/evidence")
    only_wide = second.model_copy(update={"evidence_ids": ["ev:2"]})
    [best] = score_detection(
        samples,
        [answer("stats", "known_miss", wide)],
        {"stats": [first, only_wide]},
        records,
        "model",
    )
    assert (best.detected, best.location_correct) == (2, 2)


def test_评阅输入含样本答案说明时拒绝调用():
    answers = [answer("h-sample", "injected", [issue("e-hidden", ["Q6"], "8.G.B.8", "/goals/26")])]
    clean = {"candidate": {"units": ["第 1 单元"]}, "rules": "按判据评阅"}
    assert_isolated(clean, answers)
    for leaked in [
        {"note": "e-hidden：评价安排早于学习机会"},
        {"hint": ["h-sample 的答案说明，评阅时不可见"]},
    ]:
        with pytest.raises(IsolationError):
            assert_isolated({**clean, **leaked}, answers)
