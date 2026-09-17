"""证据必须能回到实际文件位置、原文与指纹；来源改变或原文不符时明确失效。"""

import hashlib
import shutil
from pathlib import Path

import pytest

from teaching_harness.grade_evaluation.evidence import EvidenceError, cite, register, verify
from teaching_harness.grade_evaluation.records import ObjectRef

ROOT = Path(__file__).resolve().parents[1]
FINAL = (
    ".scratch/math-harness-delivery/evidence/15-full-year-blueprint/final/content/curriculum.json"
)
UNIT3 = [ObjectRef(kind="unit", id="unit_3_linear_functions")]


def project_document(root=ROOT, path=FINAL):
    return register(
        root / path,
        root=root,
        id="project-15-final",
        party="project",
        role="candidate",
        title="15 全年蓝图终稿",
    )


def test_本项目候选按_JSON_位置回取原文片段并保留提取():
    document = project_document()
    record = cite(
        document,
        ROOT,
        "/units/2/assessment_plan",
        quote="单元末通过真实情境建模（含 Task 1 类似题）进行终结性闭卷评价",
        extraction="第 3 单元以真实情境建模的闭卷任务作单元末评价",
        objects=UNIT3,
        recorded_by="program",
    )
    assert document.fingerprint == hashlib.sha256((ROOT / FINAL).read_bytes()).hexdigest()
    assert record.document_fingerprint == document.fingerprint
    assert verify(record, {document.id: document}, ROOT) == "verified"
    # 不给片段时，结构值以紧凑 JSON 原样保存。
    whole = cite(
        document,
        ROOT,
        "/units/3/prerequisite_units",
        extraction="第 4 单元的先备单元",
        objects=[ObjectRef(kind="unit", id="unit_4_linear_systems")],
        recorded_by="program",
    )
    assert whole.quote == '["unit_2_linear_eq","unit_3_linear_functions"]'


def test_省略号分隔的片段须按顺序出现_伪造原文被拒绝():
    document = project_document()
    cite(
        document,
        ROOT,
        "/units/2/assessment_plan",
        quote="入单元前测……单元末通过真实情境建模",
        extraction="有前测和单元末评价",
        recorded_by="model",
    )
    for quote in ["单元末通过真实情境建模……入单元前测", "单元末以小组海报评价"]:
        with pytest.raises(EvidenceError, match="原文"):
            cite(
                document,
                ROOT,
                "/units/2/assessment_plan",
                quote=quote,
                extraction="伪造",
                recorded_by="model",
            )
    with pytest.raises(EvidenceError, match="位置"):
        cite(document, ROOT, "/units/20/exit", extraction="不存在", recorded_by="model")


def test_来源文件改变或缺失后证据不再被当作有效(tmp_path):
    copy = tmp_path / "candidate.json"
    shutil.copy(ROOT / FINAL, copy)
    document = project_document(tmp_path, "candidate.json")
    record = cite(
        document, tmp_path, "/units/2/title", extraction="第 3 单元标题", recorded_by="program"
    )
    assert verify(record, {document.id: document}, tmp_path) == "verified"
    copy.write_text(copy.read_text().replace("函数", "关系", 1))
    assert verify(record, {document.id: document}, tmp_path) == "document_changed"
    copy.unlink()
    assert verify(record, {document.id: document}, tmp_path) == "snapshot_missing"
    assert verify(record, {}, tmp_path) == "document_unknown"


def test_外部网页按快照字符区间回取_受限材料记录缺口(tmp_path):
    snapshot = tmp_path / "unit.txt"
    snapshot.write_text(
        "Unit overview\nStudents compare proportional relationships.\nLogin required."
    )
    document = register(
        snapshot,
        root=tmp_path,
        id="im-unit-3",
        party="im",
        role="reference",
        title="单元总页",
        locator="https://example.org/unit-3",
        retrieved="2026-09-17",
        access="partial",
        access_note="练习答案需要登录",
    )
    assert document.locator == "https://example.org/unit-3" and document.snapshot == "unit.txt"
    record = cite(
        document,
        tmp_path,
        None,
        quote="compare proportional relationships",
        extraction="单元比较比例关系",
        recorded_by="program",
    )
    assert record.locator == "chars:23-57"
    assert verify(record, {document.id: document}, tmp_path) == "verified"
    shifted = record.model_copy(update={"locator": "chars:0-10"})
    assert verify(shifted, {document.id: document}, tmp_path) == "quote_mismatch"
    with pytest.raises(ValueError, match="说明"):
        register(
            snapshot,
            root=tmp_path,
            id="im-x",
            party="im",
            role="reference",
            title="x",
            access="unavailable",
        )


def test_原文比对容忍空白与转义层差异但不容忍改写():
    from teaching_harness.grade_evaluation.evidence import quote_found

    source = "对无理数（如 $\\sqrt{2}$、$\\pi$）进行有理数小数估算"
    assert quote_found("如 $\\\\sqrt{2}$、$\\\\pi$）进行", source)
    assert quote_found("对无理数（如 $\\sqrt{2}$、 $\\pi$）", source)
    assert not quote_found("对无理数（如根号 2）进行估算", source)


def test_引文中转义的换行按换行比对_不影响以n开头的LaTeX命令():
    from teaching_harness.grade_evaluation.evidence import quote_found

    source = "单元前置诊断（共 3 节）：\n   - 在 Unit 2 前，若 $a \\neq 0$ 则取倒数"
    assert quote_found("（共 3 节）：\\n   - 在 Unit 2 前", source)
    assert quote_found("若 $a \\neq 0$ 则", source)
    assert not quote_found("（共 3 节）：\\n   - 在 Unit 3 前", source)
