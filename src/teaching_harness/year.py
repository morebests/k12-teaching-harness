"""全年蓝图的范围核对与单元交接；来源完整性由知识适配器保证。"""

from typing import Any

from teaching_harness.contracts import Finding, TaskRequest, YearBlueprint, fingerprint


def check_year(
    content: YearBlueprint, request: TaskRequest, knowledge: dict[str, Any]
) -> list[Finding]:
    findings: list[Finding] = []

    def reject(criterion: Any, target: str, detail: str) -> None:
        findings.append(Finding(criterion=criterion, target=target, detail=detail, blocking=True))

    scope = knowledge.get("year_scope", {})
    if not scope.get("complete"):
        reject("sources", "year_scope", "未取得完整年级来源，不能核对全年覆盖")
    expected = set(scope.get("target_codes", [])) | set(scope.get("parent_codes", []))
    codes = [g.code for g in content.goals]
    if set(codes) != expected or len(codes) != len(set(codes)):
        reject(
            "coverage",
            "goals",
            f"全年覆盖与来源不符；遗漏 {sorted(expected - set(codes))}，"
            f"多余 {sorted(set(codes) - expected)}；同一目标不得重复建档，父标准不重复计数",
        )
    positions = {u.id: i for i, u in enumerate(content.units)}
    for unit in content.units:
        if any(positions[p] >= positions[unit.id] for p in unit.prerequisite_units):
            reject("progression", unit.id, "本设计的先备单元必须位于当前单元之前")
        if not any(a.unit_id == unit.id for g in content.goals for a in g.allocations):
            reject("coverage", unit.id, "单元没有承担任何内容目标")
    for goal in content.goals:
        roles = [(a.unit_id, a.role) for a in goal.allocations]
        if not any(a.role == "teach" for a in goal.allocations) or len(roles) != len(set(roles)):
            reject("coverage", goal.code, "目标需要明确教学承担位置；同单元同角色不得重复计入")
    if {p.code for p in content.practices} != {f"MP{i}" for i in range(1, 9)}:
        reject("coverage", "practices", "八项数学实践需要分别说明数学工作和观察证据")
    if (
        content.reserve_lessons != request.school.reserve_lessons
        or sum(u.lesson_count for u in content.units) + content.reserve_lessons
        != request.school.lesson_count
    ):
        reject("conditions", "units", "单元教学课时与机动课时必须分别符合请求且合计等于全年课时")
    focus = next((g for g in content.goals if g.code == "8.F.B.4"), None)
    if not focus or not any(
        a.unit_id == content.focus_unit_id and a.role == "teach" for a in focus.allocations
    ):
        reject("coverage", "focus_unit_id", "交接单元必须实际承担 8.F.B.4 的教学职责")
    records = {
        (r["code"], r["operation"], item["id"])
        for r in knowledge.get("additional", [])
        for item in r.get("records", [])
    }
    operations = set()
    for use in content.knowledge_uses:
        operations.add(use.operation)
        if any((use.code, use.operation, rid) not in records for rid in use.record_ids):
            reject("sources", use.code, "采用的组件或关系身份不在本次实际查询结果内")
    if "components" not in operations or not operations.intersection(
        {"prerequisites", "successors"}
    ):
        reject("sources", "knowledge_uses", "全年组织须实际使用学习组件与前后支持联系并解释选择")
    return findings


def unit_handoff(
    content: YearBlueprint,
    unit_id: str,
    parent_fingerprint: str,
    request: TaskRequest,
    knowledge: dict[str, Any],
    assets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    unit = next((u for u in content.units if u.id == unit_id), None)
    if unit is None:
        raise ValueError("全年方案中没有该单元")
    codes = {g.code for g in content.goals if any(a.unit_id == unit_id for a in g.allocations)}
    scope = knowledge.get("package", {}).get("year_scope", {})
    codes.update(p.code for p in content.practices if unit_id in p.unit_ids)
    codes.update(f"{content.grade}.{p.code}" for p in content.practices if unit_id in p.unit_ids)
    nodes = {n["detail"]["ref"]["identifier"]: n for n in scope.get("nodes", [])}
    selected_nodes = {
        key
        for key, n in nodes.items()
        if n["detail"]["source_fields"].get("statementCode") in codes
    }
    pending = list(selected_nodes)
    for key in pending:
        for parent in nodes[key]["parent_ids"]:
            if parent not in selected_nodes:
                selected_nodes.add(parent)
                pending.append(parent)
    selected = {
        (k.code, k.operation, rid)
        for k in content.knowledge_uses
        if unit_id in k.unit_ids
        for rid in k.record_ids
    }
    used_assets = {
        b.src for p in content.tasks if unit_id in p.unit_ids for b in p.blocks if b.type == "image"
    }
    result = {
        "parent_fingerprint": parent_fingerprint,
        "unit": unit.model_dump(),
        "goals": [
            g.model_dump()
            for g in content.goals
            if any(a.unit_id == unit_id for a in g.allocations)
        ],
        "practices": [p.model_dump() for p in content.practices if unit_id in p.unit_ids],
        "probes": [p.model_dump() for p in content.tasks if unit_id in p.unit_ids],
        "assets": {src: assets[src] for src in sorted(used_assets)},
        "knowledge_uses": [k.model_dump() for k in content.knowledge_uses if unit_id in k.unit_ids],
        "knowledge_records": [
            {
                **r,
                "records": [
                    item
                    for item in r.get("records", [])
                    if (r["code"], r["operation"], item["id"]) in selected
                ],
            }
            for r in knowledge.get("additional", [])
            if any(
                (r["code"], r["operation"], item["id"]) in selected for item in r.get("records", [])
            )
        ],
        "design_inferences": content.design_inferences,
        "previous_units": [
            u.model_dump() for u in content.units if u.id in unit.prerequisite_units
        ],
        "successor_units": [
            u.model_dump() for u in content.units if unit_id in u.prerequisite_units
        ],
        "year_narrative": content.narrative,
        "handoff_guidance": content.handoff_guidance,
        "assumptions": content.assumptions,
        "limitations": content.limitations,
        "school": request.school.model_dump(),
        "standards": [n for key, n in nodes.items() if key in selected_nodes],
        "source_snapshot": scope.get("source_snapshot", {}),
    }
    return {**result, "fingerprint": fingerprint(result)}
