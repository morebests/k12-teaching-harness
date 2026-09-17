"""专项检查：弥补整体评阅在调试与保留样本中系统性漏掉的问题。

- 承诺核查：模型从叙述中抽出后续利用、评价、依赖与课时分项承诺并逐字引用，程序核对位置、先后与合计。
- 探查核查：先只给题面独立求解，再连同程序算出的数据范围核对作者的解答与设计主张。
- 数学表述核查：逐条核对叙述中的数学断言及其必要条件。
"""

import json
import re
from pathlib import Path
from typing import Any, Literal

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, messages_to_dict
from pydantic import Field

from teaching_harness.contracts import Contract, fingerprint
from teaching_harness.grade_evaluation.checks import GradeCandidate
from teaching_harness.grade_evaluation.evidence import EvidenceError, cite
from teaching_harness.grade_evaluation.records import (
    CriterionId,
    EvaluationFinding,
    EvidenceRecord,
    ObjectRef,
    Severity,
)
from teaching_harness.grade_evaluation.review import (
    MODEL_EXTRACTION,
    USAGE_KEYS,
    CallRecorder,
    ModelCitation,
    ModelFinding,
    RejectedCitation,
    RejectedFinding,
    calculate_math,
    candidate_view,
    conditions_view,
    model_usage,
    recorded,
    source_location,
)

RESOURCES = Path(__file__).parents[1] / "resources"
SEVERITY_RANK = {"local": 0, "key_gap": 1, "critical": 2}


def stage_rules(name: str) -> str:
    return (RESOURCES / f"grade-{name}.md").read_text()


class StageResult(Contract):
    stage: Literal["promises", "probes", "statements"]
    candidate_id: str
    findings: list[EvaluationFinding] = Field(default_factory=list)
    evidence: list[EvidenceRecord] = Field(default_factory=list)
    rejected_citations: list[RejectedCitation] = Field(default_factory=list)
    rejected_findings: list[RejectedFinding] = Field(default_factory=list)
    problems: list[str] = Field(default_factory=list)
    usage: dict[str, int] = Field(default_factory=lambda: dict.fromkeys(USAGE_KEYS, 0))
    usage_complete: bool | None = None
    repairs: int = 0

    def add_usage(self, messages: list[BaseMessage]) -> None:
        usage, complete = model_usage(messages)
        for key, value in usage.items():
            self.usage[key] = self.usage.get(key, 0) + value
        self.usage_complete = complete and self.usage_complete is not False


def _cite(
    result: StageResult,
    candidate: GradeCandidate,
    citation: ModelCitation,
    target: ObjectRef,
    criterion: str,
) -> EvidenceRecord | None:
    document, locator = source_location(candidate, citation)
    try:
        if locator is None:
            raise EvidenceError("输入中没有这个位置")
        record = cite(
            document,
            candidate.root,
            locator,
            quote=citation.quote,
            extraction=MODEL_EXTRACTION,
            recorded_by="model",
            objects=[target],
        )
    except EvidenceError as exc:
        result.rejected_citations.append(
            RejectedCitation(
                criterion_id=criterion,
                object_id=target.id,
                source=citation.source,
                pointer=citation.pointer,
                quote=citation.quote,
                reason=str(exc).splitlines()[0],
            )
        )
        return None
    if all(e.id != record.id for e in result.evidence):
        result.evidence.append(record)
    return record


async def _structured(
    model: BaseChatModel,
    schema: type[Contract],
    rules: str,
    packet: dict[str, Any],
    name: str,
    repair: Any = None,
    transcript: list[dict[str, Any]] | None = None,
    recorder: CallRecorder | None = None,
) -> tuple[Any, list[BaseMessage], bool]:
    """调用一次结构化输出；repair(output) 返回补交说明时，在同一会话中补交一次。"""
    agent = create_agent(
        model,
        [calculate_math],
        system_prompt=rules,
        response_format=ToolStrategy(schema),
        name=name,
    )
    config: Any = recorded({"recursion_limit": 16}, recorder)
    state = await agent.ainvoke(
        {"messages": [HumanMessage(content=json.dumps(packet, ensure_ascii=False))]}, config
    )
    repaired = False
    message = repair(state["structured_response"]) if repair else None
    if message:
        state = await agent.ainvoke(
            {"messages": [*state["messages"], HumanMessage(content=message)]}, config
        )
        repaired = True
    if transcript is not None:
        transcript.extend(messages_to_dict(state["messages"]))
    return state["structured_response"], state["messages"], repaired


def _failed_citations(
    candidate: GradeCandidate, citations: list[ModelCitation]
) -> list[dict[str, str]]:
    failed = []
    for citation in citations:
        document, locator = source_location(candidate, citation)
        try:
            if locator is None:
                raise EvidenceError("输入中没有这个位置")
            cite(
                document,
                candidate.root,
                locator,
                quote=citation.quote,
                extraction=MODEL_EXTRACTION,
                recorded_by="model",
            )
        except EvidenceError as exc:
            failed.append({**citation.model_dump(), "reason": str(exc).splitlines()[0]})
    return failed


def _repair_message(failed: list[dict[str, str]]) -> str | None:
    if not failed:
        return None
    return (
        "以下引用无法在原文核实，请重新提交完整结果，每条引用都从所指字段逐字复制。\n"
        + json.dumps(failed, ensure_ascii=False)
    )


class AgreedFinding(Contract):
    """同一输入多次运行中对齐到一起的发现；多数运行都报出的才算稳定。"""

    locator: str
    support: int
    runs: int
    stable: bool
    severities: list[Severity]
    finding: EvaluationFinding


def _alignment(f: EvaluationFinding, evidence: dict[str, EvidenceRecord]) -> tuple[str, ...]:
    parts = f.id.split(":")
    rule = parts[3] if f.id.startswith("promises:") and len(parts) > 3 else ""
    first = next((evidence[e].locator for e in f.evidence_ids if e in evidence), "")
    return (f.criterion_id, f.object.kind, f.object.id, rule, "" if rule else first)


def consensus(
    runs: list[list[EvaluationFinding]], evidence: dict[str, EvidenceRecord]
) -> list[AgreedFinding]:
    """按维度、对象与首条引文位置对齐各次成功运行的发现；承诺核查按规则与对象对齐。

    同一运行中对齐位置相同的多条发现按严重度从高到低依次占位，不合并。
    代表发现取多数运行给出的严重度，票数相同时取更重的一档，并按对齐位置重新编号。
    """
    groups: dict[tuple[str, ...], list[EvaluationFinding]] = {}
    for findings in runs:
        slots: dict[tuple[str, ...], int] = {}
        for f in sorted(findings, key=lambda f: -SEVERITY_RANK[f.severity]):
            base = _alignment(f, evidence)
            slot = slots.get(base, 0)
            slots[base] = slot + 1
            groups.setdefault((*base, str(slot)), []).append(f)
    agreed = []
    for key, members in groups.items():
        severities = [f.severity for f in members]
        modal = max(set(severities), key=lambda v: (severities.count(v), SEVERITY_RANK[v]))
        chosen = next(f for f in members if f.severity == modal)
        agreed_id = (
            f"{chosen.id.split(':')[0]}:{chosen.candidate_id}:agreed:{fingerprint(list(key))[:12]}"
        )
        agreed.append(
            AgreedFinding(
                locator=key[4],
                support=len(members),
                runs=len(runs),
                stable=2 * len(members) > len(runs),
                severities=severities,
                finding=chosen.model_copy(update={"id": agreed_id}),
            )
        )
    return agreed


# 承诺核查 ---------------------------------------------------------------


class ModelPromise(Contract):
    kind: Literal["later_use", "assessment", "dependency", "time_item", "time_total"]
    group: str = Field(
        description="time_item 所属分项的简短名称；分项合计与其细分写同一名称，其他情况为空"
    )
    goal_codes: list[str] = Field(description="涉及的目标代码；原文无法对应到代码时为空")
    unit_id: str = Field(
        description="later_use/assessment：承诺发生的单元；dependency：依赖方单元；time_item：相关单元或 reserve"
    )
    other_unit_id: str = Field(description="dependency：提供所需理解的单元；其他情况为空")
    lessons: int | None = Field(description="time_item 的课时数；其他情况为 null")
    counted_in: list[Literal["unit", "reserve"]] = Field(
        description="time_item 这些课时计入单元课时还是机动课时，原文两处都算时两项都写"
    )
    level: int = Field(description="time_item 的层级：1 为分项合计，2 为其下细分；其他情况为 1")
    summary: str
    citation: ModelCitation


class ModelPromises(Contract):
    promises: list[ModelPromise]


PromiseVerdict = Literal["kept", "broken", "not_checkable"]
# 机动分项只按机动计划本身核对合计；其他字段提到机动课时是在引用这些分项。
RESERVE_PLAN = "/reserve_plan"


class CheckedPromise(Contract):
    promise: ModelPromise
    evidence_id: str
    verdict: PromiseVerdict
    note: str


class PromiseResult(StageResult):
    stage: Literal["promises"] = "promises"
    promises: list[CheckedPromise] = Field(default_factory=list)


def promise_packet(candidate: GradeCandidate) -> dict[str, Any]:
    view = candidate_view(candidate)[0]
    return {
        "task": "从候选正文中抽出所有可核对的承诺，逐字引用出处；只抽取，不评价。",
        "conditions": conditions_view(candidate),
        "candidate": view,
    }


def check_promises(
    candidate: GradeCandidate, output: ModelPromises, reviewer_id: str = "promises"
) -> PromiseResult:
    """程序核对抽出的承诺；引文无法核实或引用了不存在的目标、单元的承诺不参与判定。"""
    result = PromiseResult(candidate_id=candidate.id)
    content = candidate.content
    position = {u.id: i for i, u in enumerate(content.units)}
    goals = {g.code: g for g in content.goals}
    reserve_items: list[tuple[ModelPromise, str]] = []

    def add(
        rule: str,
        criterion: CriterionId,
        target: ObjectRef,
        severity: Severity,
        evidence: list[str],
        *,
        claim: str,
        requirement: str,
        counterexample: str,
        impact: str,
        origin: Literal["program", "model"] = "program",
    ) -> None:
        result.findings.append(
            EvaluationFinding(
                id=(
                    f"promises:{candidate.id}:{len(result.findings) + 1}:{rule}:"
                    + re.sub(r"[^a-z0-9_.:-]+", "-", target.id.lower())
                ),
                candidate_id=candidate.id,
                content_fingerprint=candidate.fingerprint,
                criterion_id=criterion,
                object=target,
                origin=origin,
                reviewer_id=reviewer_id,
                severity=severity,
                claim=claim,
                requirement=requirement,
                evidence_ids=evidence,
                counterexample=counterexample,
                impact=impact,
                recheck="核对承诺所在原文与相应单元、分配或课时",
            )
        )

    def first_teach(code: str) -> int | None:
        taught = [position[a.unit_id] for a in goals[code].allocations if a.role == "teach"]
        return min(taught) if taught else None

    for item in output.promises:
        target = ObjectRef(kind="grade", id=f"promise-{item.kind}")
        record = _cite(result, candidate, item.citation, target, "promises")
        if record is None:
            result.problems.append(f"承诺引用无法核实：{item.citation.pointer}")
            continue
        units = [u for u in (item.unit_id, item.other_unit_id) if u and u != "reserve"]
        unknown = [u for u in units if u not in position]
        unknown += [c for c in item.goal_codes if c not in goals]
        if unknown:
            result.problems.append(f"承诺引用了候选中不存在的单元或目标：{unknown}")
            continue
        verdict: PromiseVerdict = "kept"
        note = ""
        placed = item.unit_id in position
        if item.kind in {"later_use", "assessment", "dependency"} and not placed:
            verdict, note = "not_checkable", "原文没有对应到候选中的单元，程序无法核对"
        elif item.kind == "time_total":
            note = "全年总数，只作对照"
        elif item.kind == "time_item":
            if "reserve" in item.counted_in and record.locator == RESERVE_PLAN:
                reserve_items.append((item, record.id))
            if set(item.counted_in) == {"unit", "reserve"}:
                verdict, note = "broken", "同一批课时同时计入单元与机动"
                add(
                    "time-double",
                    "Q7",
                    ObjectRef(kind="time", id="reserve"),
                    "critical",
                    [record.id],
                    claim=f"{item.lessons} 节课时同时计入单元课时与机动课时",
                    requirement="单元课时与机动课时分别计入，不重复计算",
                    counterexample=f"原文把这 {item.lessons} 节既算在单元内，又算作机动时间",
                    impact="学年实际可用时间少于方案假定",
                    origin="model",
                )
        elif not item.goal_codes and item.kind != "dependency":
            verdict, note = "not_checkable", "原文没有对应到目标代码，程序无法核对"
        elif item.kind == "later_use":
            for code in item.goal_codes:
                roles = [a.role for a in goals[code].allocations if a.unit_id == item.unit_id]
                start = first_teach(code)
                if not roles:
                    verdict, note = "broken", "承诺的单元没有该目标的分配"
                    add(
                        "later-use-missing",
                        "Q5",
                        ObjectRef(kind="revisit", id=f"{code}@{item.unit_id}:apply"),
                        "key_gap",
                        [record.id],
                        claim=f"叙述承诺 {code} 在 {item.unit_id} 再次使用或回访，但该单元没有这项目标的分配",
                        requirement="承诺的回访与后续利用须有实际位置和目的",
                        counterexample=f"{code} 的分配单元为 {[a.unit_id for a in goals[code].allocations]}",
                        impact="承诺的巩固或迁移没有落到安排中",
                    )
                elif start is not None and position[item.unit_id] < start:
                    verdict, note = "broken", "承诺的利用早于首次教学"
                    add(
                        "later-use-early",
                        "Q5",
                        ObjectRef(kind="revisit", id=f"{code}@{item.unit_id}:apply"),
                        "key_gap",
                        [record.id],
                        claim=f"叙述中 {code} 在 {item.unit_id} 的利用早于其首次教学",
                        requirement="后续利用须在首次学习之后",
                        counterexample=(
                            f"{item.unit_id} 排第 {position[item.unit_id] + 1}，首次教学排第 {start + 1}"
                        ),
                        impact="学生在学习之前被要求使用该理解",
                    )
        elif item.kind == "assessment":
            for code in item.goal_codes:
                start = first_teach(code)
                if start is not None and position[item.unit_id] < start:
                    verdict, note = "broken", "评价早于首次教学"
                    add(
                        "assessment-early",
                        "Q6",
                        ObjectRef(kind="assessment", id=f"{code}@{item.unit_id}"),
                        "key_gap",
                        [record.id],
                        claim=f"{item.unit_id} 的评价安排要求 {code}，但该目标到后面的单元才首次教学",
                        requirement="评价要求之前须有相应学习机会",
                        counterexample=(
                            f"{item.unit_id} 排第 {position[item.unit_id] + 1}，{code} 首次教学排第 {start + 1}"
                        ),
                        impact="学生在学习机会之前被评价",
                    )
        elif item.kind == "dependency" and item.other_unit_id:
            if position[item.other_unit_id] >= position[item.unit_id]:
                verdict, note = "broken", "依赖方排在提供方之前"
                add(
                    "dependency-order",
                    "Q3",
                    ObjectRef(kind="dependency", id=f"{item.unit_id}<-{item.other_unit_id}"),
                    "critical",
                    [record.id],
                    claim=f"{item.unit_id} 需要 {item.other_unit_id} 提供的理解，但没有排在它之后",
                    requirement="单元实际需要的理解须先于该单元建立",
                    counterexample=(
                        f"{item.unit_id} 排第 {position[item.unit_id] + 1}，"
                        f"{item.other_unit_id} 排第 {position[item.other_unit_id] + 1}"
                    ),
                    impact="所承诺的学习进程在当前顺序下无法执行",
                )
        elif item.kind == "dependency":
            verdict, note = "not_checkable", "原文没有指明提供所需理解的单元"
        result.promises.append(
            CheckedPromise(promise=item, evidence_id=record.id, verdict=verdict, note=note)
        )
    # 每组有合计时用合计，没有合计时加总细分；各组相加后与机动课时比较。
    groups: dict[str, dict[int, list[tuple[int, str]]]] = {}
    for n, (item, rid) in enumerate(reserve_items):
        if item.lessons is not None:
            key = item.group or f"未分组-{n}"
            groups.setdefault(key, {}).setdefault(item.level, []).append((item.lessons, rid))
    if groups:
        totals, cited = [], []
        for levels in groups.values():
            # 同组重复抽到的合计只算一次；层级不是 1 的都按细分加总。
            details = [x for level, xs in levels.items() if level != 1 for x in xs]
            chosen = levels[1][:1] if 1 in levels else details
            totals.append(sum(count for count, _ in chosen))
            cited += [rid for _, rid in chosen]
        if sum(totals) != content.reserve_lessons:
            add(
                "reserve-total",
                "Q7",
                ObjectRef(kind="time", id="reserve"),
                "critical",
                list(dict.fromkeys(cited)),
                claim="机动时间各分项合计与机动课时不一致",
                requirement="机动时间的安排须与请求的机动课时一致",
                counterexample=(
                    f"{'+'.join(map(str, totals))}={sum(totals)}，"
                    f"机动课时为 {content.reserve_lessons}"
                ),
                impact="机动计划承诺的工作超出或少于可用时间",
            )
    return result


async def review_promises(
    model: BaseChatModel,
    candidate: GradeCandidate,
    *,
    rules: str | None = None,
    transcript: list[dict[str, Any]] | None = None,
    recorder: CallRecorder | None = None,
) -> PromiseResult:
    def repair(output: ModelPromises) -> str | None:
        return _repair_message(_failed_citations(candidate, [p.citation for p in output.promises]))

    output, messages, repaired = await _structured(
        model,
        ModelPromises,
        rules or stage_rules("promises"),
        promise_packet(candidate),
        "grade_promises",
        repair,
        transcript,
        recorder,
    )
    result = check_promises(candidate, output)
    result.repairs = int(repaired)
    result.add_usage(messages)
    return result


# 探查核查 ---------------------------------------------------------------

NUMBER = r"-?\d+(?:\.\d+)?"
LE = r"(?:\\le|\\leq|≤|<=)"
GE = r"(?:\\ge|\\geq|≥|>=)"
# 每种写法给出 (模式, 下界组, 上界组, 变量组)；变量组为 0 表示写法中没有变量。
RANGE_PATTERNS = [
    (re.compile(rf"({NUMBER})\s*(?:~|～|—|–|-|至|到)\s*({NUMBER})"), 1, 2, 0),
    (re.compile(rf"({NUMBER})\s*{LE}\s*([a-zA-Z])\s*{LE}\s*({NUMBER})"), 1, 3, 2),
    (re.compile(rf"({NUMBER})\s*{GE}\s*([a-zA-Z])\s*{GE}\s*({NUMBER})"), 3, 1, 2),
    (
        re.compile(
            rf"([a-zA-Z])\s*{GE}\s*({NUMBER})\s*(?:，|,|且|并且|\\text\{{且\}})\s*\1\s*{LE}\s*({NUMBER})"
        ),
        2,
        3,
        1,
    ),
]
LOWER_BOUND = re.compile(rf"([a-zA-Z])\s*{GE}\s*({NUMBER})")
SINGLE_LETTER = re.compile(r"(?<![A-Za-z\\])([A-Za-z])(?![A-Za-z])")
PARENTHESES = re.compile(r"[（(][^）)]*[）)]")
# 等号右边须是单独的数：排除 y = 2x + 3、d = 60t 这类解析式和 Δx 这类增量。
SUBSTITUTION = re.compile(
    rf"(?<![A-Za-z\\_Δ∆])([A-Za-z])\s*=\s*({NUMBER})(?!\d|\.\d|\s*[A-Za-z(（+\-*/^·×])"
)


def header_variable(header: str) -> str:
    """表头中唯一的单字母变量；括号中的单位不算。"""
    letters = set(SINGLE_LETTER.findall(PARENTHESES.sub("", header)))
    return letters.pop() if len(letters) == 1 else ""


def substitutions(text: str, pointer: str) -> list[tuple[str, "RangeStatement"]]:
    """文中把单独的数代入单字母变量的位置。"""
    found = []
    for match in SUBSTITUTION.finditer(text):
        value = float(match[2])
        snippet = text[max(0, match.start() - 12) : match.end() + 12]
        found.append(
            (
                match[1],
                RangeStatement(
                    pointer=pointer, text=snippet, low=value, high=value, variable=match[1]
                ),
            )
        )
    return found


class ColumnRange(Contract):
    pointer: str
    header: str
    low: float
    high: float
    count: int
    variable: str = Field(default="", description="表头中唯一的单字母变量，没有时为空")


class RangeStatement(Contract):
    pointer: str
    text: str
    low: float
    high: float | None
    variable: str = ""


class RangeIssue(Contract):
    """核查须逐条回应的区间事实：表述超出与之重叠的数据列范围、文中代入的值落在
    数据范围外，或只写了下界。"""

    id: str
    kind: Literal["beyond_data", "outside_data", "no_upper_bound"]
    statement: RangeStatement
    column: ColumnRange | None = None


MATERIAL_WORDS = {
    "figure": re.compile(r"散点图|如图|上图|下图|(?<![试意])图中|统计图|示意图"),
    "table": re.compile(r"下表|上表|(?<![代发])表中|数据表"),
}


class AbsentMaterial(Contract):
    """正文提到、探查中却没有对应图件或表格的材料。"""

    id: str
    kind: Literal["figure", "table"]
    pointer: str
    text: str


class ProbeFacts(Contract):
    """程序从探查正文算出的事实；是否构成问题由核查判断。"""

    task_id: str
    table_ranges: list[ColumnRange]
    range_statements: list[RangeStatement]
    range_issues: list[RangeIssue]
    absent_materials: list[AbsentMaterial]


def range_issues(
    columns: list[ColumnRange],
    statements: list[RangeStatement],
    points: list[tuple[str, RangeStatement]],
) -> list[RangeIssue]:
    """带变量的表述只与同一变量的数据列比较；同一变量对应多列时不作比较。

    不带变量的区间与每个有重叠的数据列比较，超出其范围时列出。
    """
    issues: list[RangeIssue] = []
    named = [c.variable for c in columns if c.variable]
    by_variable = {c.variable: c for c in columns if c.variable and named.count(c.variable) == 1}
    for variable, point in points:
        column = by_variable.get(variable)
        if column and not column.low <= point.low <= column.high:
            issues.append(RangeIssue(id="", kind="outside_data", statement=point, column=column))
    for statement in statements:
        if statement.high is None:
            issues.append(RangeIssue(id="", kind="no_upper_bound", statement=statement))
            continue
        if statement.variable:
            column = by_variable.get(statement.variable)
            if column and (statement.low < column.low or statement.high > column.high):
                issues.append(
                    RangeIssue(id="", kind="beyond_data", statement=statement, column=column)
                )
            continue
        for column in columns:
            overlaps = statement.low <= column.high and statement.high >= column.low
            beyond = statement.low < column.low or statement.high > column.high
            if overlaps and beyond:
                issues.append(
                    RangeIssue(id="", kind="beyond_data", statement=statement, column=column)
                )
    return [i.model_copy(update={"id": f"range-{n}"}) for n, i in enumerate(issues, start=1)]


def _task(candidate: GradeCandidate, task_id: str) -> tuple[int, Any]:
    for index, task in enumerate(candidate.content.tasks):
        if task.id == task_id:
            return index, task
    raise KeyError(f"候选中没有探查 {task_id}")


def probe_facts(candidate: GradeCandidate, task_id: str) -> ProbeFacts:
    _, task = _task(candidate, task_id)
    base = f"/tasks/{task_id}"
    ranges = []
    for j, block in enumerate(task.blocks):
        if block.type != "table":
            continue
        for k, header in enumerate(block.headers):
            values = []
            for row in block.rows:
                match = re.fullmatch(rf"\s*({NUMBER})\s*", row[k])
                if match:
                    values.append(float(match[1]))
            if values and len(values) == len(block.rows):
                ranges.append(
                    ColumnRange(
                        pointer=f"{base}/blocks/{j}/headers/{k}",
                        header=header,
                        low=min(values),
                        high=max(values),
                        count=len(values),
                        variable=header_variable(header),
                    )
                )
    fields: dict[str, str] = {
        name: value for name, value in task.model_dump().items() if isinstance(value, str)
    }
    fields |= {f"blocks/{j}/text": b.text for j, b in enumerate(task.blocks) if b.text}
    statements = []
    points: list[tuple[str, RangeStatement]] = []
    for name, text in fields.items():
        pointer = f"{base}/{name}"
        points += substitutions(text, pointer)
        spans = []
        for pattern, low_group, high_group, variable_group in RANGE_PATTERNS:
            for match in pattern.finditer(text):
                low, high = float(match[low_group]), float(match[high_group])
                if low < high:
                    spans.append(match.span())
                    snippet = text[max(0, match.start() - 12) : match.end() + 12]
                    statements.append(
                        RangeStatement(
                            pointer=pointer,
                            text=snippet,
                            low=low,
                            high=high,
                            variable=match[variable_group] if variable_group else "",
                        )
                    )
        for match in LOWER_BOUND.finditer(text):
            # 双边区间中的下界已按区间记录。
            if any(start <= match.start() < end for start, end in spans):
                continue
            snippet = text[max(0, match.start() - 12) : match.end() + 12]
            statements.append(
                RangeStatement(
                    pointer=pointer,
                    text=snippet,
                    low=float(match[2]),
                    high=None,
                    variable=match[1],
                )
            )
    provided = {
        "figure": any(b.type == "image" for b in task.blocks),
        "table": any(b.type == "table" for b in task.blocks),
    }
    absent: list[AbsentMaterial] = []
    for name, text in fields.items():
        for kind, words in MATERIAL_WORDS.items():
            mention = words.search(text)
            if mention and not provided[kind]:
                at = mention.start()
                absent.append(
                    AbsentMaterial(
                        id=f"material-{len(absent) + 1}",
                        kind=kind,  # type: ignore[arg-type]
                        pointer=f"{base}/{name}",
                        text=text[max(0, at - 20) : at + 20],
                    )
                )
    return ProbeFacts(
        task_id=task_id,
        table_ranges=ranges,
        range_statements=statements,
        range_issues=range_issues(ranges, statements, points),
        absent_materials=absent,
    )


STUDENT_FIELDS = {"id", "prompt", "blocks"}


def solver_packet(candidate: GradeCandidate, task_id: str) -> dict[str, Any]:
    """独立求解只看学生可见的题面与表格，不含作者解答、预判、支持与设计结论。"""
    _, task = _task(candidate, task_id)
    return {
        "task": "独立完成下面的数学任务，写出每一问的答案与过程，并列出求解依赖的条件和题面缺少的信息。",
        "problem": task.model_dump(include=STUDENT_FIELDS),
        "conditions": conditions_view(candidate)["school"],
    }


class SolutionPart(Contract):
    question: str
    answer: str
    work: str


class ModelSolution(Contract):
    parts: list[SolutionPart]
    required_conditions: list[str] = Field(description="求解所依赖的取值范围、单位与假设")
    missing_information: list[str] = Field(description="题面要求使用却没有提供的数据、图或条件")
    notes: str


class ProbeComparison(Contract):
    item: str = Field(description="check_items 中的核对项编号")
    author: Literal["consistent", "contradicted", "omitted", "not_applicable"] = Field(
        description="作者正文相对该项：一致、矛盾、遗漏或不适用"
    )
    matters: bool = Field(description="矛盾或遗漏是否改变数学结论、解释范围或设计判断")
    finding: int | None = Field(
        description="matters 为 true 时，findings 中报告该问题的序号（从 0 开始）；matters 为 false 时必须为 null"
    )
    note: str


class ModelProbeReview(Contract):
    comparisons: list[ProbeComparison]
    findings: list[ModelFinding]
    checked: list[str]


def check_items(solution: ModelSolution, facts: ProbeFacts) -> dict[str, str]:
    """核查必须逐条回应的项：独立解答的每一问、条件与缺失信息，程序算出的区间与缺失材料。"""
    items = {f"answer-{n}": f"{p.question}：{p.answer}" for n, p in enumerate(solution.parts, 1)}
    items |= {f"condition-{n}": c for n, c in enumerate(solution.required_conditions, 1)}
    items |= {f"missing-{n}": m for n, m in enumerate(solution.missing_information, 1)}
    for issue in facts.range_issues:
        where = f"{issue.statement.pointer} 的“{issue.statement.text.strip()}”"
        if issue.column is None:
            items[issue.id] = f"{where}只给出下界 {issue.statement.low:g}，没有上界"
        elif issue.kind == "outside_data":
            items[issue.id] = (
                f"{where}代入 {issue.column.variable} = {issue.statement.low:g}，"
                f"不在表中“{issue.column.header}”的数据范围"
                f" {issue.column.low:g}–{issue.column.high:g} 内"
            )
        else:
            items[issue.id] = (
                f"{where}写的范围 {issue.statement.low:g}–{issue.statement.high:g}"
                f"超出表中“{issue.column.header}”的数据范围"
                f" {issue.column.low:g}–{issue.column.high:g}"
            )
    for material in facts.absent_materials:
        name = "图" if material.kind == "figure" else "表格"
        items[material.id] = (
            f"{material.pointer} 提到“{material.text.strip()}”，但探查中没有提供{name}"
        )
    return items


INCOMPLETE_REVIEW = (
    "核查结果不完整，请重新提交完整结果：每个核对项都要在 comparisons 中回应，"
    "判为影响结论的项要链接到 findings 中报告它的问题。"
)


def comparison_problems(review: ModelProbeReview, items: dict[str, str]) -> list[str]:
    answered = {c.item for c in review.comparisons}
    problems = [f"没有回应核对项 {i}：{text}" for i, text in items.items() if i not in answered]
    for c in review.comparisons:
        if c.item not in items:
            problems.append(f"核对项 {c.item} 不存在")
        elif c.matters and not (c.finding is not None and 0 <= c.finding < len(review.findings)):
            problems.append(f"核对项 {c.item} 判为影响结论，但没有对应 findings 中的问题")
    return problems


class ProbeResult(StageResult):
    stage: Literal["probes"] = "probes"
    task_id: str
    facts: ProbeFacts
    solution: ModelSolution
    check_items: dict[str, str] = Field(default_factory=dict)
    comparisons: list[ProbeComparison] = Field(default_factory=list)
    checked: list[str] = Field(default_factory=list)


def _keep_findings(
    result: StageResult,
    candidate: GradeCandidate,
    raw_findings: list[ModelFinding],
    criterion: CriterionId,
    target_for: Any,
    reviewer_id: str,
    prefix: str,
) -> None:
    for n, raw in enumerate(raw_findings, start=1):
        try:
            target = target_for(raw)
        except ValueError as exc:
            result.rejected_findings.append(
                RejectedFinding(
                    criterion_id=criterion,
                    finding=raw.model_dump(),
                    reason=f"对象身份无效：{str(exc).splitlines()[0]}",
                )
            )
            continue
        records = [
            r for c in raw.citations if (r := _cite(result, candidate, c, target, criterion))
        ]
        reason = "" if records else "没有能在原文核实的引用"
        if not reason:
            try:
                result.findings.append(
                    EvaluationFinding(
                        id=f"{prefix}:{n}",
                        candidate_id=candidate.id,
                        content_fingerprint=candidate.fingerprint,
                        criterion_id=criterion,
                        object=target,
                        origin="model",
                        reviewer_id=reviewer_id,
                        severity=raw.severity,
                        claim=raw.claim,
                        requirement=raw.requirement,
                        evidence_ids=[r.id for r in records],
                        counterexample=raw.counterexample,
                        impact=raw.impact,
                        recheck=raw.recheck,
                    )
                )
                continue
            except ValueError as exc:
                reason = str(exc).splitlines()[0]
        result.rejected_findings.append(
            RejectedFinding(criterion_id=criterion, finding=raw.model_dump(), reason=reason)
        )


class ProbeModelOutput(Contract):
    """一道探查的模型输出；同一题面、条件与规则可在多个样本间复用。"""

    solution: ModelSolution
    review: ModelProbeReview
    usage: dict[str, int]
    usage_complete: bool
    repairs: int
    transcript: list[dict[str, Any]] = Field(default_factory=list, exclude=True)


async def run_probe_models(
    model: BaseChatModel,
    candidate: GradeCandidate,
    task_id: str,
    *,
    rules: str | None = None,
    solver_rules: str | None = None,
    assets: dict[str, Any] | None = None,
    recorder: CallRecorder | None = None,
) -> ProbeModelOutput:
    """assets 为题面图件的绘制参数，随题面一起给独立求解。"""
    transcript: list[dict[str, Any]] = []
    facts = probe_facts(candidate, task_id)
    packet = solver_packet(candidate, task_id)
    if assets:
        packet["figures"] = assets
    solution, solve_messages, _ = await _structured(
        model,
        ModelSolution,
        solver_rules or stage_rules("solver"),
        packet,
        "grade_probe_solver",
        transcript=transcript,
        recorder=recorder,
    )
    view = candidate_view(candidate)[0]
    items = check_items(solution, facts)

    def repair(output: ModelProbeReview) -> str | None:
        failed = _repair_message(
            _failed_citations(candidate, [c for f in output.findings for c in f.citations])
        )
        incomplete = comparison_problems(output, items)
        if not incomplete:
            return failed
        return "\n".join(
            [
                INCOMPLETE_REVIEW,
                *incomplete,
                *([failed] if failed else []),
            ]
        )

    review, messages, repaired = await _structured(
        model,
        ModelProbeReview,
        rules or stage_rules("probe"),
        {
            "task": "核查这个关键探查：逐项回应 check_items，再找出作者题面、解答和设计主张中的问题。",
            "conditions": conditions_view(candidate),
            "candidate": {"tasks": {task_id: view["tasks"][task_id]}},
            "figures": assets or {},
            "independent_solution": solution.model_dump(),
            "program_facts": facts.model_dump(),
            "check_items": items,
        },
        "grade_probe_review",
        repair,
        transcript,
        recorder,
    )
    usage, complete = model_usage([*solve_messages, *messages])
    return ProbeModelOutput(
        solution=solution,
        review=review,
        usage=usage,
        usage_complete=complete,
        repairs=int(repaired),
        transcript=transcript,
    )


def normalize_probe(
    candidate: GradeCandidate,
    task_id: str,
    output: ProbeModelOutput,
    reviewer_id: str = "probes",
) -> ProbeResult:
    """把模型输出按本候选的原文核实为发现；复用缓存时用量只记在首次调用的样本上。"""
    facts = probe_facts(candidate, task_id)
    items = check_items(output.solution, facts)
    result = ProbeResult(
        candidate_id=candidate.id,
        task_id=task_id,
        facts=facts,
        solution=output.solution,
        check_items=items,
        comparisons=output.review.comparisons,
        checked=output.review.checked,
        problems=comparison_problems(output.review, items),
        repairs=output.repairs,
    )
    prefix = f"probes:{candidate.id}:{task_id.lower()}"
    _keep_findings(
        result,
        candidate,
        output.review.findings,
        "Q4",
        lambda _: ObjectRef(kind="probe", id=task_id),
        reviewer_id,
        prefix,
    )
    kept = {f.id for f in result.findings}
    for c in output.review.comparisons:
        if c.matters and c.finding is not None and f"{prefix}:{c.finding + 1}" not in kept:
            result.problems.append(f"核对项 {c.item} 判为影响结论，但它对应的发现未通过核实")
    return result


async def review_probe(
    model: BaseChatModel,
    candidate: GradeCandidate,
    task_id: str,
    *,
    rules: str | None = None,
    solver_rules: str | None = None,
    assets: dict[str, Any] | None = None,
    reviewer_id: str = "probes",
) -> ProbeResult:
    output = await run_probe_models(
        model, candidate, task_id, rules=rules, solver_rules=solver_rules, assets=assets
    )
    result = normalize_probe(candidate, task_id, output, reviewer_id)
    result.usage = dict(output.usage)
    result.usage_complete = output.usage_complete
    return result


def probe_cache_key(
    candidate: GradeCandidate,
    task_id: str,
    assets: dict[str, Any],
    rules: str,
    *,
    model: str,
    repeat: int = 0,
) -> str:
    """同一模型对同一题面、条件、程序事实与规则的输出可在样本间复用；重复运行各自独立。"""
    _, task = _task(candidate, task_id)
    return fingerprint(
        {
            "model": model,
            "repeat": repeat,
            "task": task.model_dump(),
            "conditions": conditions_view(candidate),
            "facts": probe_facts(candidate, task_id).model_dump(),
            "assets": assets,
            "rules": rules,
            "schemas": [ModelSolution.model_json_schema(), ModelProbeReview.model_json_schema()],
        }
    )


# 数学表述核查 -------------------------------------------------------------

UNIT_TEXT = {"title", "narrative", "entry", "exit", "assessment_plan"}
GRADE_TEXT = [
    "narrative",
    "prerequisites",
    "successors",
    "handoff_guidance",
    "design_inferences",
    "teacher_preparation",
]


def statement_packet(candidate: GradeCandidate) -> dict[str, Any]:
    """只给叙述性正文与目标分配；探查题另由探查核查负责。"""
    view = candidate_view(candidate)[0]
    return {
        "task": "逐条核对下面叙述中的数学断言：结论是否正确、是否遗漏必要条件、概念是否混淆。",
        "candidate": {
            **{k: view[k] for k in GRADE_TEXT},
            "units": {
                uid: {k: v for k, v in unit.items() if k in UNIT_TEXT}
                for uid, unit in view["units"].items()
            },
            "goals": view["goals"],
        },
    }


StatementError = Literal[
    "wrong_conclusion", "missing_condition", "concept_confusion", "overgeneralization", "imprecise"
]
# 各类错误的严重度上限：只有在所述条件下本身为假的关键结论才可能是重大失败。
STATEMENT_CEILING: dict[str, Severity] = {
    "wrong_conclusion": "critical",
    "missing_condition": "key_gap",
    "concept_confusion": "key_gap",
    "overgeneralization": "key_gap",
    "imprecise": "local",
}


class ModelStatementFinding(ModelFinding):
    error_type: StatementError = Field(
        description=(
            "wrong_conclusion：在其声明的条件下结论本身为假；missing_condition：缺少限定条件"
            "（包括因漏写限定词而字面为假）；concept_confusion：概念、方法或分类混淆；"
            "overgeneralization：把特定条件下成立的结论写成普遍成立；imprecise：不够精确但不致误解"
        )
    )


class ModelStatementReview(Contract):
    findings: list[ModelStatementFinding]
    checked: list[str]


class StatementResult(StageResult):
    stage: Literal["statements"] = "statements"
    checked: list[str] = Field(default_factory=list)
    error_types: dict[str, StatementError] = Field(default_factory=dict)


async def review_statements(
    model: BaseChatModel,
    candidate: GradeCandidate,
    *,
    rules: str | None = None,
    reviewer_id: str = "statements",
    transcript: list[dict[str, Any]] | None = None,
    recorder: CallRecorder | None = None,
) -> StatementResult:
    def repair(output: ModelStatementReview) -> str | None:
        return _repair_message(
            _failed_citations(candidate, [c for f in output.findings for c in f.citations])
        )

    review, messages, repaired = await _structured(
        model,
        ModelStatementReview,
        rules or stage_rules("statements"),
        statement_packet(candidate),
        "grade_statements",
        repair,
        transcript,
        recorder,
    )
    result = StatementResult(
        candidate_id=candidate.id, checked=review.checked, repairs=int(repaired)
    )
    result.add_usage(messages)
    capped = []
    for raw in review.findings:
        ceiling = STATEMENT_CEILING[raw.error_type]
        if SEVERITY_RANK[raw.severity] > SEVERITY_RANK[ceiling]:
            raw = raw.model_copy(update={"severity": ceiling})
        capped.append(raw)
    prefix = f"statements:{candidate.id}"
    _keep_findings(
        result,
        candidate,
        capped,
        "Q4",
        lambda raw: ObjectRef(kind=raw.kind, id=raw.id),
        reviewer_id,
        prefix,
    )
    result.error_types = {
        f"{prefix}:{n}": raw.error_type
        for n, raw in enumerate(capped, start=1)
        if any(f.id == f"{prefix}:{n}" for f in result.findings)
    }
    return result
