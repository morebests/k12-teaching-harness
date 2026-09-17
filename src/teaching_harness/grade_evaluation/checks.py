"""年级课程候选的逐对象结构检查与各维应查对象清单。

与生成阶段的 check_year 核对同类结构事实（覆盖、先后、课时、知识条目），
但每项发现都落到具体对象和原文位置，并增加分配先后的检查；
check_year 仍是 15 生成图的放行规则，24 定型新阶段契约时再统一。
程序只判断结构；目标是否有实质学习机会等语义问题由模型和人工判断。
"""

import json
import re
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any

from pydantic import Field

from teaching_harness.contracts import (
    Contract,
    Fingerprint,
    TaskRequest,
    YearBlueprint,
    fingerprint,
)
from teaching_harness.grade_evaluation.evidence import cite, register
from teaching_harness.grade_evaluation.records import (
    CriterionId,
    EvaluationFinding,
    EvidenceRecord,
    ObjectRef,
    Severity,
    SourceDocument,
)
from teaching_harness.mathematics import calculate

# 固定的教师规划问题（协议 Q8）；每份候选都用同一组问题查找依据。
TEACHER_QUESTIONS = {
    "tq-shorten-unit": "若一个单元缩短，哪些后续安排会受影响，依据在哪里？",
    "tq-goal-trace": "某项年度目标在哪里首次学习、在哪里巩固、在哪里被评价？",
    "tq-reserve": "机动时间用于什么，何时使用，挪用后会失去什么？",
}


@dataclass(frozen=True)
class GradeCandidate:
    """一份被评的年级课程候选及其评价时实际使用的条件和标准来源。"""

    id: str
    content: YearBlueprint
    document: SourceDocument
    conditions: SourceDocument
    standards: SourceDocument
    root: Path
    request: TaskRequest = field(repr=False)
    knowledge: dict[str, Any] = field(repr=False)

    @property
    def documents(self) -> dict[str, SourceDocument]:
        return {d.id: d for d in (self.document, self.conditions, self.standards)}

    @cached_property
    def fingerprint(self) -> str:
        return fingerprint(self.content.model_dump(mode="json"))

    @property
    def scope(self) -> dict[str, Any]:
        return self.knowledge["package"]["year_scope"]


def load_candidate(
    candidate_id: str,
    content: Path,
    *,
    request: Path,
    knowledge: Path,
    root: Path,
    title: str | None = None,
) -> GradeCandidate:
    documents = {
        "document": register(
            content,
            root=root,
            id=candidate_id,
            party="project",
            role="candidate",
            title=title or f"年级课程候选 {candidate_id}",
        ),
        "conditions": register(
            request,
            root=root,
            id=f"{candidate_id}.conditions",
            party="school",
            role="condition",
            title="评价所用的学校条件与请求",
        ),
        "standards": register(
            knowledge,
            root=root,
            id=f"{candidate_id}.standards",
            party="ccss",
            role="standard",
            title="评价所用的 CCSS 年级范围与知识查询记录",
        ),
    }
    return GradeCandidate(
        id=candidate_id,
        content=YearBlueprint.model_validate(json.loads(content.read_text())),
        root=root,
        request=TaskRequest.model_validate(json.loads(request.read_text())),
        knowledge=json.loads(knowledge.read_text()),
        **documents,
    )


def _dependencies(content: YearBlueprint) -> list[tuple[int, str, str]]:
    return [
        (i, unit.id, prerequisite)
        for i, unit in enumerate(content.units)
        for prerequisite in unit.prerequisite_units
    ]


def scope_codes(candidate: GradeCandidate) -> list[str]:
    return [*candidate.scope["target_codes"], *candidate.scope["parent_codes"]]


def checklist(candidate: GradeCandidate, criterion: CriterionId) -> list[ObjectRef]:
    """各维应查对象；Q1 按完整来源范围而非候选自报的目标列出。"""
    content = candidate.content
    units = [ObjectRef(kind="unit", id=u.id) for u in content.units]
    dependencies = [
        ObjectRef(kind="dependency", id=f"{unit}<-{prerequisite}")
        for _, unit, prerequisite in _dependencies(content)
    ]
    later_uses = [
        ObjectRef(kind="revisit", id=f"{g.code}@{a.unit_id}:{a.role}")
        for g in content.goals
        for a in g.allocations
        if a.role in {"apply", "revisit"}
    ]
    assessments = [
        ObjectRef(kind="assessment", id=f"{g.code}@{a.unit_id}")
        for g in content.goals
        for a in g.allocations
        if a.role == "assess"
    ]
    objects = {
        "Q1": [ObjectRef(kind="goal", id=code) for code in scope_codes(candidate)]
        + [ObjectRef(kind="practice", id=f"MP{i}") for i in range(1, 9)],
        "Q2": [ObjectRef(kind="grade", id="mainline"), *units],
        "Q3": [*units, *dependencies],
        "Q4": [*units, *[ObjectRef(kind="probe", id=t.id) for t in content.tasks]],
        "Q5": [*units, *later_uses],
        "Q6": [*units, *assessments],
        # 资源按实际使用位置逐项核对，避免只对“资源符合条件”作一次总体判断。
        "Q7": [
            ObjectRef(kind="time", id="grade-total"),
            ObjectRef(kind="time", id="reserve"),
            *units,
            *[ObjectRef(kind="resource", id=u.id) for u in content.units],
            *[ObjectRef(kind="resource", id=t.id) for t in content.tasks],
            ObjectRef(kind="resource", id="teacher_preparation"),
        ],
        "Q8": [ObjectRef(kind="teacher_question", id=k) for k in TEACHER_QUESTIONS],
    }
    return objects[criterion]


class ProgramReview(Contract):
    candidate_id: str
    content_fingerprint: Fingerprint
    findings: list[EvaluationFinding] = Field(default_factory=list)
    evidence: list[EvidenceRecord] = Field(default_factory=list)


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9_.:-]+", "-", text.lower()).strip("-")


class _Recorder:
    def __init__(self, candidate: GradeCandidate) -> None:
        self.candidate = candidate
        self.review = ProgramReview(
            candidate_id=candidate.id, content_fingerprint=candidate.fingerprint
        )

    def evidence(
        self, document: SourceDocument, locator: str, extraction: str, target: ObjectRef
    ) -> str:
        record = cite(
            document,
            self.candidate.root,
            locator,
            extraction=extraction,
            recorded_by="program",
            objects=[target],
        )
        if all(e.id != record.id for e in self.review.evidence):
            self.review.evidence.append(record)
        return record.id

    def finding(
        self,
        rule: str,
        criterion: CriterionId,
        target: ObjectRef,
        severity: Severity,
        *,
        claim: str,
        requirement: str,
        evidence: list[str],
        counterexample: str,
        impact: str,
        recheck: str,
    ) -> None:
        self.review.findings.append(
            EvaluationFinding(
                id=f"program:{_slug(self.candidate.id)}:{rule}:{_slug(target.id)}",
                candidate_id=self.candidate.id,
                content_fingerprint=self.candidate.fingerprint,
                criterion_id=criterion,
                object=target,
                origin="program",
                reviewer_id="program",
                severity=severity,
                claim=claim,
                requirement=requirement,
                evidence_ids=evidence,
                counterexample=counterexample,
                impact=impact,
                recheck=recheck,
            )
        )


def _coverage(recorder: _Recorder) -> None:
    candidate = recorder.candidate
    content, document = candidate.content, candidate.document
    nodes = {
        n["detail"]["source_fields"].get("statementCode"): i
        for i, n in enumerate(candidate.scope["nodes"])
    }
    present = {g.code for g in content.goals}
    for code in scope_codes(candidate):
        if code in present:
            continue
        target = ObjectRef(kind="goal", id=code)
        pointer = f"/package/year_scope/nodes/{nodes[code]}/detail/source_fields/description"
        recorder.finding(
            "goal-missing",
            "Q1",
            target,
            "critical",
            claim=f"年级必需目标 {code} 没有任何年度责任安排",
            requirement="完整年级范围内的每项内容目标及父项整合要求都需有责任位置",
            evidence=[
                recorder.evidence(candidate.standards, pointer, f"{code} 的标准原文", target)
            ],
            counterexample=f"候选 goals 中找不到 {code}",
            impact="该目标在全年没有学习机会与评价依据",
            recheck="在 goals 中查找该代码及其分配",
        )
    for i, goal in enumerate(content.goals):
        target = ObjectRef(kind="goal", id=goal.code)
        base = f"/goals/{i}/allocations"
        teach = [j for j, a in enumerate(goal.allocations) if a.role == "teach"]
        if not teach:
            recorder.finding(
                "goal-untaught",
                "Q1",
                target,
                "critical",
                claim=f"{goal.code} 只有应用、回访或评价，没有教学承担位置",
                requirement="每项目标需要明确首次学习的位置",
                evidence=[recorder.evidence(document, base, f"{goal.code} 的全部分配", target)],
                counterexample=f"{goal.code} 的分配角色为 {[a.role for a in goal.allocations]}",
                impact="评价或应用缺少学习机会支撑",
                recheck="核对该目标是否有 teach 分配",
            )
            continue
        _order(recorder, goal.code, i, teach)
        pairs = [(a.unit_id, a.role) for a in goal.allocations]
        if len(pairs) != len(set(pairs)):
            recorder.finding(
                "allocation-duplicate",
                "Q1",
                target,
                "local",
                claim=f"{goal.code} 在同一单元重复登记同一角色",
                requirement="同单元同角色不重复计入",
                evidence=[recorder.evidence(document, base, f"{goal.code} 的全部分配", target)],
                counterexample="",
                impact="可能重复计算学习机会",
                recheck="合并重复分配",
            )
    practices = {p.code for p in content.practices}
    for i in range(1, 9):
        if f"MP{i}" in practices:
            continue
        target = ObjectRef(kind="practice", id=f"MP{i}")
        # 请求要求说明数学实践的学习机会；整项缺失属于协议所列的必需要求遗漏。
        recorder.finding(
            "practice-missing",
            "Q1",
            target,
            "critical",
            claim=f"数学实践 MP{i} 没有学生数学工作与观察证据",
            requirement="八项数学实践分别落实到学生工作",
            evidence=[recorder.evidence(document, "/practices", "候选列出的数学实践", target)],
            counterexample=f"候选 practices 中没有 MP{i}",
            impact="数学实践只剩标签或缺失",
            recheck="补充该实践的单元、学生行动与证据",
        )
    for unit in content.units:
        if any(a.unit_id == unit.id for g in content.goals for a in g.allocations):
            continue
        target = ObjectRef(kind="unit", id=unit.id)
        index = next(i for i, u in enumerate(content.units) if u.id == unit.id)
        recorder.finding(
            "unit-without-goal",
            "Q3",
            target,
            "key_gap",
            claim=f"{unit.id} 没有承担任何内容目标",
            requirement="每个单元都有新增的目标职责",
            evidence=[recorder.evidence(document, f"/units/{index}/id", "单元身份", target)],
            counterexample="",
            impact="单元职责与时间无法由目标解释",
            recheck="核对目标分配",
        )


def _order(recorder: _Recorder, code: str, goal_index: int, teach: list[int]) -> None:
    """应用、回访与评价不应早于该目标首次教学的单元。"""
    content = recorder.candidate.content
    position = {u.id: i for i, u in enumerate(content.units)}
    goal = content.goals[goal_index]
    first = min(position[goal.allocations[j].unit_id] for j in teach)
    for j, allocation in enumerate(goal.allocations):
        if allocation.role == "teach" or position[allocation.unit_id] >= first:
            continue
        assess = allocation.role == "assess"
        target = ObjectRef(kind="goal", id=code)
        recorder.finding(
            f"{allocation.role}-before-teach",
            "Q6" if assess else "Q5",
            target,
            "key_gap",
            claim=(
                f"{code} 在第 {position[allocation.unit_id] + 1} 单元安排{'评价' if assess else '应用／回访'}，"
                f"早于第 {first + 1} 单元的首次教学"
            ),
            requirement="评价与后续利用须有此前的学习机会",
            evidence=[
                recorder.evidence(
                    recorder.candidate.document,
                    f"/goals/{goal_index}/allocations/{j}/unit_id",
                    f"{code} 的{allocation.role}分配所在单元",
                    target,
                )
            ],
            counterexample=(
                f"{allocation.unit_id} 排第 {position[allocation.unit_id] + 1}，"
                f"首次 teach 排第 {first + 1}"
            ),
            impact="学生在学习机会之前被要求表现或使用该目标",
            recheck="调整分配单元或补充此前的学习机会",
        )


def _sequence(recorder: _Recorder) -> None:
    content, document = recorder.candidate.content, recorder.candidate.document
    position = {u.id: i for i, u in enumerate(content.units)}
    for index, unit_id, prerequisite in _dependencies(content):
        if position[prerequisite] < index:
            continue
        j = content.units[index].prerequisite_units.index(prerequisite)
        target = ObjectRef(kind="dependency", id=f"{unit_id}<-{prerequisite}")
        recorder.finding(
            "dependency-reversed",
            "Q3",
            target,
            "critical",
            claim=f"{unit_id} 声明依赖 {prerequisite}，但先备单元没有排在它之前",
            requirement="本设计声明的先备单元必须先于依赖它的单元",
            evidence=[
                recorder.evidence(
                    document,
                    f"/units/{index}/prerequisite_units/{j}",
                    f"{unit_id} 声明的先备单元",
                    target,
                )
            ],
            counterexample=(
                f"{unit_id} 位于第 {index + 1} 单元，先备 {prerequisite} 位于第 "
                f"{position[prerequisite] + 1} 单元"
            ),
            impact="所承诺的依赖在当前顺序下无法满足",
            recheck="调整顺序或修正依赖声明",
        )


def _time(recorder: _Recorder) -> None:
    candidate = recorder.candidate
    content, school = candidate.content, candidate.request.school
    counts = [u.lesson_count for u in content.units]
    total = calculate("+".join(map(str, counts)))
    target = ObjectRef(kind="time", id="grade-total")
    planned = calculate(f"{total}+{content.reserve_lessons}")
    if content.reserve_lessons == school.reserve_lessons and int(planned) == school.lesson_count:
        return
    recorder.finding(
        "time-total",
        "Q7",
        target,
        "critical",
        claim="单元课时与机动课时不符合学年课时条件",
        requirement="各单元课时与机动课时分别计入，合计等于学年课时，机动课时等于请求",
        evidence=[
            recorder.evidence(candidate.document, "/reserve_lessons", "候选机动课时", target),
            recorder.evidence(
                candidate.conditions, "/school/lesson_count", "学年总课时条件", target
            ),
            recorder.evidence(
                candidate.conditions, "/school/reserve_lessons", "请求的机动课时", target
            ),
        ],
        counterexample=(
            f"{'+'.join(map(str, counts))}={total}；{total}+{content.reserve_lessons}={planned}，"
            f"条件为 {school.lesson_count} 课时、机动 {school.reserve_lessons}"
        ),
        impact="承诺的学习工作在学年时间内无法全部安排",
        recheck="重算单元与机动课时",
    )


def _sources(recorder: _Recorder) -> None:
    candidate = recorder.candidate
    queried = {
        (r["code"], r["operation"], item["id"])
        for r in candidate.knowledge.get("additional", [])
        for item in r.get("records", [])
    }
    for i, use in enumerate(candidate.content.knowledge_uses):
        invented = [rid for rid in use.record_ids if (use.code, use.operation, rid) not in queried]
        if not invented:
            continue
        target = ObjectRef(kind="goal", id=use.code)
        recorder.finding(
            f"knowledge-unqueried-{use.operation}-{fingerprint(use.record_ids)[:8]}",
            "Q1",
            target,
            "critical",
            claim=f"知识采用条目 {invented} 不在本次实际查询结果中",
            requirement="方案依据的知识条目必须来自实际查询",
            evidence=[
                recorder.evidence(
                    candidate.document, f"/knowledge_uses/{i}/record_ids", "采用的知识条目", target
                )
            ],
            counterexample=f"{use.code}/{use.operation} 的实际查询结果不含 {invented}",
            impact="设计依据可能是虚构的来源",
            recheck="重新查询或删除该依据",
        )


# 边界只按 ASCII 判断，紧挨汉字的代码也能识别；子项可写作 .a 或 a。
STANDARD_CODE = re.compile(r"\b8\.[A-Z]{1,2}\.[A-C]\.\d+(?:\.?[a-c])?\b", re.ASCII)


def _focus(recorder: _Recorder) -> None:
    """焦点单元须讲授交接所围绕的目标。

    年级范围的请求没有结构化的焦点目标字段，暂从任务说明中取唯一的标准代码；
    没有或有多个代码时不核对。
    """
    candidate = recorder.candidate
    content = candidate.content
    codes = set(STANDARD_CODE.findall(candidate.request.instruction))
    goals = {g.code: (i, g) for i, g in enumerate(content.goals)}
    if len(codes) != 1 or (code := codes.pop()) not in goals:
        return
    index, goal = goals[code]
    teach = [a.unit_id for a in goal.allocations if a.role == "teach"]
    if not teach or content.focus_unit_id in teach:
        return
    target = ObjectRef(kind="unit", id=content.focus_unit_id)
    recorder.finding(
        "focus-not-teaching",
        "Q8",
        target,
        "key_gap",
        claim=f"焦点单元 {content.focus_unit_id} 没有讲授交接所围绕的目标 {code}",
        requirement="目标单元交接须落在实际讲授该目标的单元",
        evidence=[
            recorder.evidence(candidate.document, "/focus_unit_id", "候选的焦点单元", target),
            recorder.evidence(
                candidate.document, f"/goals/{index}/allocations", f"{code} 的全部分配", target
            ),
            recorder.evidence(candidate.conditions, "/instruction", "原始任务说明", target),
        ],
        counterexample=f"{code} 的讲授单元为 {teach}，焦点单元为 {content.focus_unit_id}",
        impact="焦点单元与交接说明、目标分配相互矛盾，单元级工作的对象不明",
        recheck="核对焦点单元与交接说明",
    )


def program_review(candidate: GradeCandidate) -> ProgramReview:
    recorder = _Recorder(candidate)
    _focus(recorder)
    _coverage(recorder)
    _sequence(recorder)
    _time(recorder)
    _sources(recorder)
    return recorder.review
