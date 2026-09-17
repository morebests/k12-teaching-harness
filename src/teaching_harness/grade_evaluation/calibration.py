"""检查器校准：由记录在案的改动生成样本，按答案统计检出、漏报与误报。

答案与样本分开保存；评阅和修订输入在装配后须通过隔离核对。
"""

import copy
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, ValidationError

from teaching_harness.contracts import Contract, Fingerprint, Text, YearBlueprint
from teaching_harness.grade_evaluation.evidence import file_sha256, pointer_parts
from teaching_harness.grade_evaluation.records import (
    CriterionId,
    EvaluationFinding,
    EvidenceRecord,
    Locator,
    ObjectRef,
    Origin,
    RecordId,
)


class MutationError(ValueError):
    pass


class IsolationError(ValueError):
    pass


class Mutation(Contract):
    op: Literal["replace", "add", "remove", "move", "replace_text", "rename"]
    path: Locator
    value: Any = None
    from_path: Locator = ""
    old: str = ""
    new: str = ""


class Sample(Contract):
    """note 只作中性标签，不写改动意图或答案。"""

    id: RecordId
    split: Literal["debug", "holdout"]
    kind: Literal["base", "known_miss", "injected", "control"]
    base: Text
    base_fingerprint: Fingerprint
    # 该底稿生成时实际查询的知识记录；来源检查必须对照同一次查询。
    standards: Text
    mutations: list[Mutation] = Field(default_factory=list)
    note: Text


class ExpectedIssue(Contract):
    id: RecordId
    criteria: list[CriterionId] = Field(min_length=1)
    objects: list[ObjectRef] = Field(default_factory=list)
    pointers: list[Locator] = Field(min_length=1)
    severity: Literal["critical", "key_gap"]
    detectable_by: list[Literal["program", "model"]] = Field(min_length=1)
    description: Text
    # 非空时，发现的判断、要求、反例或影响须含其中之一，用来区分同一位置的不同问题。
    keywords: list[str] = Field(default_factory=list)


class SampleAnswer(Contract):
    sample_id: RecordId
    kind: Literal["base", "known_miss", "injected", "control"]
    expected: list[ExpectedIssue] = Field(default_factory=list)
    protected_pointers: list[Locator] = Field(default_factory=list)
    rationale: Text


def _parent(document: Any, pointer: str) -> tuple[Any, str]:
    parts = pointer_parts(pointer)
    if not parts:
        raise MutationError("不能改动整份文档")
    node = document
    for key in parts[:-1]:
        try:
            node = node[int(key)] if isinstance(node, list) else node[key]
        except (KeyError, IndexError, ValueError):
            raise MutationError(f"改动位置不存在：{pointer}") from None
    return node, parts[-1]


def _take(document: Any, pointer: str) -> Any:
    node, key = _parent(document, pointer)
    try:
        return node.pop(int(key)) if isinstance(node, list) else node.pop(key)
    except (KeyError, IndexError, ValueError):
        raise MutationError(f"改动位置不存在：{pointer}") from None


def _put(document: Any, pointer: str, value: Any, *, insert: bool) -> None:
    node, key = _parent(document, pointer)
    if isinstance(node, list):
        index = len(node) if key == "-" else int(key)
        if insert:
            node.insert(index, value)
        elif index < len(node):
            node[index] = value
        else:
            raise MutationError(f"改动位置不存在：{pointer}")
    elif insert or key in node:
        node[key] = value
    else:
        raise MutationError(f"改动位置不存在：{pointer}")


def _rename(value: Any, old: str, new: str) -> tuple[Any, int]:
    if value == old:
        return new, 1
    if isinstance(value, dict):
        pairs = {k: _rename(v, old, new) for k, v in value.items()}
        return {k: v for k, (v, _) in pairs.items()}, sum(n for _, n in pairs.values())
    if isinstance(value, list):
        items = [_rename(v, old, new) for v in value]
        return [v for v, _ in items], sum(n for _, n in items)
    return value, 0


def apply_mutations(document: dict[str, Any], mutations: Iterable[Mutation]) -> dict[str, Any]:
    result = copy.deepcopy(document)
    for m in mutations:
        if m.op == "rename":
            # 只替换与 old 完全相同的字符串值，例如单元身份；正文中的叙述不变。
            result, count = _rename(result, m.old, m.new)
            if not count:
                raise MutationError(f"文档中没有值为 {m.old} 的字段")
        elif m.op == "remove":
            _take(result, m.path)
        elif m.op == "move":
            _put(result, m.path, _take(result, m.from_path), insert=True)
        elif m.op in {"add", "replace"}:
            _put(result, m.path, copy.deepcopy(m.value), insert=m.op == "add")
        else:
            node, key = _parent(result, m.path)
            text = node[int(key)] if isinstance(node, list) else node.get(key)
            if not isinstance(text, str) or m.old not in text:
                raise MutationError(f"原文不含要替换的文字：{m.path}")
            _put(result, m.path, text.replace(m.old, m.new, 1), insert=False)
    return result


def materialize(sample: Sample, root: Path, out_dir: Path) -> Path:
    """在副本上执行改动；样本仍须是合法的年级课程，才能检验内容问题而非格式错误。"""
    base = root / sample.base
    if file_sha256(base) != sample.base_fingerprint:
        raise MutationError("样本底稿指纹与记录不符")
    content = apply_mutations(json.loads(base.read_bytes()), sample.mutations)
    try:
        YearBlueprint.model_validate(content)
    except ValidationError as exc:
        raise MutationError(f"改动后不再是合法的年级课程：{exc.errors()[0]['msg']}") from None
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{sample.id}.json"
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n")
    return path


class DetectionMetrics(Contract):
    origin: Origin
    split: Text
    samples: int
    control_samples: int
    expected: int
    detected: int
    location_correct: int
    severity_matched: int
    missed: list[str]
    critical_missed: list[str]
    false_positives: list[str]
    other_findings: list[str]


def _under(locator: str, pointers: Iterable[str]) -> bool:
    return any(locator == p or locator.startswith(p.rstrip("/") + "/") for p in pointers)


# 分给某个预期问题的一条发现：发现、位置是否正确、严重度是否一致。
Hit = tuple[EvaluationFinding, bool, bool]


def _assign(candidates: dict[str, list[Hit]]) -> dict[str, Hit]:
    """一条发现只计入一个预期问题。

    先求检出最多的分配，再在其中让位置正确的发现最多，其次严重度一致的最多；
    用最小费用最大流求解，规模只有单个样本的问题与发现。
    """
    issues = list(candidates)
    found = list(dict.fromkeys(h[0].id for hits in candidates.values() for h in hits))
    offset = len(issues) + 1
    sink = offset + len(found)
    # 边：[终点, 剩余容量, 费用, 反向边下标]
    graph: list[list[list[int]]] = [[] for _ in range(sink + 1)]

    def edge(u: int, v: int, cost: int) -> None:
        graph[u].append([v, 1, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    for i, issue in enumerate(issues, start=1):
        edge(0, i, 0)
        for f, in_place, severity in candidates[issue]:
            edge(i, offset + found.index(f.id), -(2 * in_place + severity))
    for j in range(len(found)):
        edge(offset + j, sink, 0)
    while True:
        dist: list[float] = [float("inf")] * (sink + 1)
        dist[0] = 0
        via: list[tuple[int, int] | None] = [None] * (sink + 1)
        for _ in range(sink):
            changed = False
            for u, edges in enumerate(graph):
                for k, (v, capacity, cost, _) in enumerate(edges):
                    if capacity and dist[u] + cost < dist[v]:
                        dist[v], via[v], changed = dist[u] + cost, (u, k), True
            if not changed:
                break
        if via[sink] is None:
            break
        v = sink
        while (step := via[v]) is not None:
            u, k = step
            graph[u][k][1] -= 1
            graph[v][graph[u][k][3]][1] += 1
            v = u
    chosen = {}
    for i, issue in enumerate(issues, start=1):
        for v, capacity, _, _ in graph[i]:
            if offset <= v < sink and capacity == 0:
                chosen[issue] = next(h for h in candidates[issue] if h[0].id == found[v - offset])
    return chosen


def score_detection(
    samples: list[Sample],
    answers: list[SampleAnswer],
    findings: dict[str, list[EvaluationFinding]],
    evidence: dict[str, EvidenceRecord],
    origin: Origin,
    *,
    origins: set[Origin] | None = None,
    group: str | None = None,
) -> list[DetectionMetrics]:
    """检出须位置在答案范围内且对象或维度一致，或对象与维度都一致；位置正确另计。

    一条发现只计入一个预期问题；位置与严重度按分给该问题的发现统计。

    只统计答案标明 origin 应能发现的问题：程序不对语义判断负责。
    origins 指定参与统计的发现来源，默认只含 origin；组合检查可同时计入程序发现。
    group 给定时把全部样本作为一组统计，并以它为组名；否则按样本的 split 分组。
    """
    counted = origins or {origin}
    key = {a.sample_id: a for a in answers}
    metrics = []
    groups = (
        {group: samples}
        if group
        else {split: [s for s in samples if s.split == split] for split in ("debug", "holdout")}
    )
    for split, chosen in groups.items():
        if not chosen:
            continue
        values: dict[str, Any] = {
            "samples": len(chosen),
            "control_samples": sum(s.kind == "control" for s in chosen),
            "expected": 0,
            "detected": 0,
            "location_correct": 0,
            "severity_matched": 0,
            "missed": [],
            "critical_missed": [],
            "false_positives": [],
            "other_findings": [],
        }
        for s in chosen:
            answer = key[s.id]
            own = [f for f in findings.get(s.id, []) if f.origin in counted]
            located = {
                f.id: [evidence[e].locator for e in f.evidence_ids if e in evidence] for f in own
            }
            matched: set[str] = set()
            candidates: dict[str, list[Hit]] = {}
            for expected in answer.expected:
                if origin not in expected.detectable_by:
                    continue
                values["expected"] += 1
                hits = []
                for f in own:
                    in_place = any(_under(loc, expected.pointers) for loc in located[f.id])
                    same_object = f.object in expected.objects
                    same_criterion = f.criterion_id in expected.criteria
                    text = f"{f.claim}{f.requirement}{f.counterexample}{f.impact}"
                    on_topic = not expected.keywords or any(k in text for k in expected.keywords)
                    if on_topic and (
                        (in_place and (same_object or same_criterion))
                        or (same_object and same_criterion)
                    ):
                        hits.append((f, in_place, f.severity == expected.severity))
                matched |= {f.id for f, _, _ in hits}
                candidates[expected.id] = hits
            assigned = _assign(candidates)
            for expected in answer.expected:
                if expected.id not in candidates:
                    continue
                if expected.id not in assigned:
                    values["missed"].append(expected.id)
                    if expected.severity == "critical":
                        values["critical_missed"].append(expected.id)
                    continue
                _, in_place, same_severity = assigned[expected.id]
                values["detected"] += 1
                values["location_correct"] += in_place
                values["severity_matched"] += same_severity
            for f in own:
                if f.id in matched:
                    continue
                protected = f.severity != "local" and any(
                    _under(loc, answer.protected_pointers) for loc in located[f.id]
                )
                values["false_positives" if protected else "other_findings"].append(f.id)
        metrics.append(DetectionMetrics(origin=origin, split=split, **values))
    return metrics


def _hidden_texts(answers: Iterable[SampleAnswer]) -> list[str]:
    texts = []
    for answer in answers:
        texts.append(answer.rationale)
        texts.extend(e.description for e in answer.expected)
    return [t for t in texts if len(t) >= 8]


def assert_isolated(payload: Any, answers: Iterable[SampleAnswer]) -> None:
    """装配后的模型输入不得含任何答案说明；发现时拒绝调用而不是删改输入。"""
    text = json.dumps(payload, ensure_ascii=False)
    leaks = [t for t in _hidden_texts(answers) if t in text]
    if leaks:
        raise IsolationError(f"模型输入包含 {len(leaks)} 处样本答案说明，已拒绝调用")
