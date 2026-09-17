"""程序检查逐对象定位结构问题：注入的问题被找出，合法改动不被误报。"""

import json
import shutil
from pathlib import Path

import pytest

from teaching_harness.grade_evaluation.checks import checklist, load_candidate, program_review
from teaching_harness.grade_evaluation.evidence import verify

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ".scratch/math-harness-delivery/evidence/15-full-year-blueprint/final"


def unit_index(content, unit_id):
    return next(i for i, u in enumerate(content["units"]) if u["id"] == unit_id)


def goal(content, code):
    return next(g for g in content["goals"] if g["code"] == code)


@pytest.fixture
def variant(tmp_path):
    shutil.copy(BASE / "request.json", tmp_path / "request.json")
    shutil.copy(BASE / "knowledge.json", tmp_path / "knowledge.json")
    base = json.loads((BASE / "content/curriculum.json").read_text())

    def build(change=None):
        content = json.loads(json.dumps(base))
        if change:
            change(content)
        (tmp_path / "candidate.json").write_text(json.dumps(content, ensure_ascii=False))
        candidate = load_candidate(
            "variant",
            tmp_path / "candidate.json",
            request=tmp_path / "request.json",
            knowledge=tmp_path / "knowledge.json",
            root=tmp_path,
        )
        return candidate, program_review(candidate)

    return build


def located(review, finding):
    records = {e.id: e for e in review.evidence}
    return [records[i] for i in finding.evidence_ids]


def test_15终稿通过结构检查_应查对象来自完整范围与实际单元(variant):
    candidate, review = variant()
    assert review.findings == []
    q1 = checklist(candidate, "Q1")
    assert len([o for o in q1 if o.kind == "goal"]) == 36
    assert {o.id for o in q1 if o.kind == "practice"} == {f"MP{i}" for i in range(1, 9)}
    q3 = checklist(candidate, "Q3")
    assert len([o for o in q3 if o.kind == "unit"]) == 8
    assert {"unit_4_linear_systems<-unit_3_linear_functions"} <= {
        o.id for o in q3 if o.kind == "dependency"
    }
    assert len([o for o in q3 if o.kind == "dependency"]) == 7


def test_评价早于首次教学被定位到具体分配(variant):
    def assess_early(content):
        goal(content, "8.G.B.8")["allocations"].append(
            {
                "unit_id": "unit_2_linear_eq",
                "role": "assess",
                "opportunity": "单元末测验",
                "evidence": "坐标距离计算",
            }
        )

    candidate, review = variant(assess_early)
    [finding] = review.findings
    assert (finding.criterion_id, finding.severity) == ("Q6", "key_gap")
    assert finding.object.id == "8.G.B.8"
    [evidence] = located(review, finding)
    assert evidence.locator.endswith("/allocations/1/unit_id")
    assert verify(evidence, candidate.documents, candidate.root) == "verified"


def test_声明的依赖被反转与课时重复计算属于重大失败并给出计算(variant):
    def reverse(content):
        units = content["units"]
        units.insert(2, units.pop(unit_index(content, "unit_4_linear_systems")))

    _, review = variant(reverse)
    [finding] = review.findings
    assert (finding.criterion_id, finding.severity) == ("Q3", "critical")
    assert finding.object.id == "unit_4_linear_systems<-unit_3_linear_functions"
    assert "第 3" in finding.counterexample and "第 4" in finding.counterexample

    def double_count(content):
        content["units"][0]["lesson_count"] += 10

    _, review = variant(double_count)
    [finding] = review.findings
    assert (finding.criterion_id, finding.severity) == ("Q7", "critical")
    assert "170+20=190" in finding.counterexample and "180" in finding.counterexample


def test_遗漏目标以标准原文为证_虚构的知识条目被阻断(variant):
    def drop(content):
        content["goals"] = [g for g in content["goals"] if g["code"] != "8.SP.A.4"]

    candidate, review = variant(drop)
    [finding] = review.findings
    assert (finding.criterion_id, finding.severity, finding.object.id) == (
        "Q1",
        "critical",
        "8.SP.A.4",
    )
    [evidence] = located(review, finding)
    assert evidence.document_id == candidate.standards.id
    assert "two-way table" in evidence.quote

    def invent(content):
        content["knowledge_uses"][0]["record_ids"].append("made-up-record")

    _, review = variant(invent)
    [finding] = review.findings
    assert finding.severity == "critical" and "made-up-record" in finding.claim


@pytest.mark.parametrize("control", ["renumber", "swap", "revisit"])
def test_合法对照不产生程序发现(variant, control):
    def renumber(content):
        text = json.dumps(content, ensure_ascii=False)
        for i, unit in enumerate(list(content["units"]), start=1):
            text = text.replace(f'"{unit["id"]}"', f'"u{i:02d}"')
        content.clear()
        content.update(json.loads(text))

    def swap(content):
        units = content["units"]
        five, six = (
            unit_index(content, u)
            for u in ["unit_5_real_numbers_pythagoras", "unit_6_exponents_sci_notation"]
        )
        units[five], units[six] = units[six], units[five]

    def revisit(content):
        goal(content, "8.F.B.4")["allocations"].append(
            {
                "unit_id": "unit_4_linear_systems",
                "role": "revisit",
                "opportunity": "用两条线性函数的图象比较方案",
                "evidence": "解释交点两侧的函数值关系",
            }
        )

    _, review = variant({"renumber": renumber, "swap": swap, "revisit": revisit}[control])
    assert review.findings == []
