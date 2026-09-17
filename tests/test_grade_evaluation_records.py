"""年级课程评价记录的契约：证据、发现、独立评分与复核必须能定位并自洽。"""

import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from teaching_harness.grade_evaluation.config import config_drift, file_ref, records_schema
from teaching_harness.grade_evaluation.records import (
    Adjudication,
    CriterionRating,
    EvaluationFinding,
    EvidenceRecord,
    ObjectCheck,
    load_rubric,
    rating_problems,
)

ROOT = Path(__file__).resolve().parents[1]
RUBRIC = ROOT / ".scratch/math-harness-delivery/year-planning-rubric.json"
FINAL = "b1351a76cc1323cbdccc0717a2e3f393943f9e7ee733fc135aaff55a047b8d2d"
DOC = "a" * 64


def evidence(**change):
    # 15 终稿第 3 单元评价安排的真实原文片段。
    value = {
        "id": "ev-final-u3-assessment",
        "document_id": "project-15-final",
        "document_fingerprint": DOC,
        "locator": "/units/2/assessment_plan",
        "quote": "单元末通过真实情境建模（含 Task 1 类似题）进行终结性闭卷评价",
        "extraction": "第 3 单元的单元末评价采用真实情境建模的闭卷任务",
        "objects": [{"kind": "unit", "id": "unit_3_linear_functions"}],
        "recorded_by": "program",
    }
    return {**value, **change}


def check(status="supported", evidence_ids=("ev-final-u3-assessment",), note="单元末评价有位置"):
    return {
        "object": {"kind": "unit", "id": "unit_3_linear_functions"},
        "status": status,
        "evidence_ids": list(evidence_ids),
        "note": note,
    }


def rating(**change):
    value = {
        "candidate_id": "project-15-final",
        "content_fingerprint": FINAL,
        "criterion_id": "Q6",
        "reviewer_id": "r1",
        "rubric_fingerprint": DOC,
        "observability": "observable",
        "comparability": "single_candidate",
        "reviewed_scope": {"expected": [{"kind": "unit", "id": "unit_3_linear_functions"}]},
        "score": 3,
        "interval": None,
        "evidence_refs": ["ev-final-u3-assessment"],
        "strengths": ["单元末评价与建模目标对应"],
        "findings": [],
        "critical_failure": False,
        "critical_failure_reason": "",
        "object_checks": [check()],
        "score_rationale": "应查单元已核完，评价位置与目标一致；距 4 分缺少响应安排",
    }
    return {**value, **change}


def test_证据记录保留原文位置与提取且拒绝无效定位():
    record = EvidenceRecord.model_validate(evidence())
    assert record.quote.startswith("单元末") and record.locator == "/units/2/assessment_plan"
    EvidenceRecord.model_validate(evidence(document_id="im-unit-3", locator="chars:120-260"))
    with pytest.raises(ValidationError):
        EvidenceRecord.model_validate(evidence(locator="units.2.assessment_plan"))


def test_有证据的对象结论必须引用证据_未核实与不适用必须说明理由():
    ObjectCheck.model_validate(check(status="unverified", evidence_ids=(), note="受保护材料未取得"))
    for status in ["supported", "local_gap", "key_gap", "critical"]:
        with pytest.raises(ValidationError):
            ObjectCheck.model_validate(check(status=status, evidence_ids=()))


def test_重大失败需要反例或计算_驳回需要反证():
    finding = {
        "id": "f-time",
        "candidate_id": "project-15-final",
        "content_fingerprint": FINAL,
        "criterion_id": "Q7",
        "object": {"kind": "time", "id": "grade-total"},
        "origin": "program",
        "reviewer_id": "program",
        "severity": "critical",
        "claim": "单元课时与机动课时合计超过学年课时",
        "requirement": "各单元与机动课时合计等于请求课时",
        "evidence_ids": ["ev-final-u3-assessment"],
        "counterexample": "",
        "impact": "全年安排不可执行",
        "recheck": "重算合计",
    }
    with pytest.raises(ValidationError):
        EvaluationFinding.model_validate(finding)
    EvaluationFinding.model_validate({**finding, "counterexample": "170+20=190≠180"})
    with pytest.raises(ValidationError):
        EvaluationFinding.model_validate(
            {**finding, "counterexample": "170+20=190≠180", "status": "rebutted"}
        )


def test_评分与对象级结论矛盾时列出问题():
    assert rating_problems(CriterionRating.model_validate(rating())) == []
    gap = rating(object_checks=[check(status="key_gap", note="评价缺少响应")])
    assert "关键缺口" in " ".join(rating_problems(CriterionRating.model_validate(gap)))
    critical = rating(critical_failure=True, critical_failure_reason="评价早于学习机会")
    assert "重大失败" in " ".join(rating_problems(CriterionRating.model_validate(critical)))
    uncovered = rating(
        reviewed_scope={
            "expected": [
                {"kind": "unit", "id": "unit_3_linear_functions"},
                {"kind": "unit", "id": "unit_4_linear_systems"},
            ]
        }
    )
    assert "覆盖未完" in " ".join(rating_problems(CriterionRating.model_validate(uncovered)))
    unverified = rating(
        object_checks=[check(status="unverified", evidence_ids=(), note="未取得原文")]
    )
    assert "未核实" in " ".join(rating_problems(CriterionRating.model_validate(unverified)))


def test_分数只能是单值或区间_不可观察时不给分():
    with pytest.raises(ValidationError):
        CriterionRating.model_validate(rating(score=None))
    with pytest.raises(ValidationError):
        CriterionRating.model_validate(rating(score=3, interval={"low": 2, "high": 3}))
    CriterionRating.model_validate(rating(score=None, interval={"low": 2, "high": 3}))
    CriterionRating.model_validate(rating(score=None, observability="unobservable"))
    with pytest.raises(ValidationError):
        CriterionRating.model_validate(rating(observability="unobservable"))


def test_复核记录保留原始评分():
    record = {
        "id": "adj-q6",
        "candidate_id": "project-15-final",
        "content_fingerprint": FINAL,
        "criterion_id": "Q6",
        "original_ratings": [
            {"reviewer_id": "r1", "score": 3, "interval": None, "critical_failure": False}
        ],
        "triggers": ["同维分差至少2分"],
        "method": "independent_adjudicator",
        "adjudicator_id": "r3",
        "score": 2,
        "interval": None,
        "critical_failure": False,
        "supporting_evidence": ["ev-final-u3-assessment"],
        "rationale": "单元末评价存在，但缺少响应安排",
    }
    with pytest.raises(ValidationError):
        Adjudication.model_validate(record)
    record["original_ratings"].append(
        {"reviewer_id": "r2", "score": 1, "interval": None, "critical_failure": False}
    )
    Adjudication.model_validate(record)


def test_规则数据是唯一尺度且记录类型覆盖规则要求的字段():
    rubric = load_rubric(RUBRIC)
    assert rubric.version == "year-planning-v1"
    assert [c.id for c in rubric.criteria] == [f"Q{i}" for i in range(1, 9)]
    assert sum(c.weight for c in rubric.criteria) == 100
    assert rubric.fingerprint == hashlib.sha256(RUBRIC.read_bytes()).hexdigest()
    # 单条评分承担多数字段；原始评分与裁定由复核记录保存。
    rating_fields = set(CriterionRating.model_fields) | {"score_or_interval"}
    assert "original_ratings" in Adjudication.model_fields
    missing = set(rubric.required_fields) - rating_fields - {"original_ratings", "adjudication"}
    assert missing == set()


def test_规则数据被改动时拒绝与协议不一致的权重(tmp_path):
    protocol = RUBRIC.parent / "year-planning-evaluation.md"
    (tmp_path / protocol.name).write_text(protocol.read_text())
    data = json.loads(RUBRIC.read_text())
    data["criteria"][0]["weight"] = 20
    changed = tmp_path / "rubric.json"
    changed.write_text(json.dumps(data, ensure_ascii=False))
    with pytest.raises(ValueError, match="权重"):
        load_rubric(changed)
    data["criteria"][0]["weight"] = 15
    changed.write_text(json.dumps(data, ensure_ascii=False))
    assert load_rubric(changed).weight("Q1") == 15
    # 比较按裁定的含义取文本，顺序被改时拒绝而不是悄悄换义。
    data["verdicts"] = list(reversed(data["verdicts"]))
    changed.write_text(json.dumps(data, ensure_ascii=False))
    with pytest.raises(ValueError, match="裁定"):
        load_rubric(changed)


def test_冻结的评价配置在规则或保留答案改变后拒绝继续(tmp_path):
    rules = tmp_path / "rules.md"
    answers = tmp_path / "answers"
    answers.mkdir()
    rules.write_text("规则 v1")
    (answers / "h1.json").write_text("{}")
    refs = {"rules": file_ref(rules, tmp_path), "holdout_answers": file_ref(answers, tmp_path)}
    assert config_drift(refs, tmp_path) == []
    rules.write_text("规则 v2")
    (answers / "h2.json").write_text("{}")
    assert sorted(config_drift(refs, tmp_path)) == ["holdout_answers", "rules"]
    (answers / "h2.json").unlink()
    rules.unlink()
    assert config_drift(refs, tmp_path) == ["rules"]


def test_评价记录契约由正式类型导出且与仓库文件一致():
    exported = ROOT / "docs/contracts/grade-evaluation.schema.json"
    assert json.loads(exported.read_text()) == records_schema()
    names = set(records_schema()["$defs"])
    assert {
        "EvaluationConfig",
        "EvidenceRecord",
        "EvaluationFinding",
        "CriterionRating",
        "Adjudication",
        "GradeSummary",
        "SampleAnswer",
    } <= names
