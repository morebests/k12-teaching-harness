"""当前切片的教学输入、内容和查询契约；由这些类型导出 JSON Schema。"""

import hashlib
import json
import re
from typing import Annotated, Any, Literal
from uuid import NAMESPACE_URL, uuid5

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

Text = Annotated[str, Field(min_length=1, max_length=20000)]
Fingerprint = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
BLOCKED = re.compile(
    r"illustrative\s*mathematics|illustrativemathematics|im[.](?:kendallhunt|openupresources)|"
    r"accessim[.]org|im[.]k12|(?:^|\W)IM(?:\W|$)",
    re.IGNORECASE,
)


def fingerprint(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def task_id(identity: str, event_id: str) -> str:
    return str(uuid5(NAMESPACE_URL, json.dumps(["teaching-harness/v1", identity, event_id])))


def require_original(value: Any) -> None:
    if BLOCKED.search(json.dumps(value, ensure_ascii=False)):
        raise ValueError("原创运行不接受 IM 内容、引用或课程来源")


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Source(Contract):
    label: Text
    version: Text
    origin: Literal["caller", "synthetic"]


class School(Contract):
    source: Source
    lesson_count: int = Field(ge=1, le=240)
    reserve_lessons: int = Field(default=0, ge=0, le=240)
    minutes_per_lesson: int = Field(ge=15, le=120)
    class_size: int = Field(ge=1, le=100)
    resources: list[Text] = Field(min_length=1, max_length=30)
    learner_context: Text


class ExternalContent(Contract):
    id: Annotated[str, Field(pattern=r"^[a-zA-Z0-9_-]{1,80}$")]
    source: Source
    content: str | dict[str, Any]
    fingerprint: Fingerprint

    @model_validator(mode="after")
    def verify(self) -> "ExternalContent":
        if fingerprint(self.content) != self.fingerprint:
            raise ValueError("外部实际内容与指纹不符")
        if len(json.dumps(self.content, ensure_ascii=False).encode()) > 80000:
            raise ValueError("外部内容超过本次接入上限，请按任务范围提供")
        return self


class Limits(Contract):
    # 调用次数和时间由调用方显式提供；当前默认只计量累计 token。
    model_calls: int = Field(ge=1, le=100)
    tool_calls: int = Field(ge=1, le=300)
    total_tokens: int | None = Field(
        default=None,
        ge=1000,
        description="可选：按已完成调用的实际累计用量停止后续调用；不是硬费用上限",
    )
    seconds: int = Field(ge=1, le=7200)


class TaskRequest(Contract):
    schema_version: Literal[1] = 1
    event_id: Annotated[str, Field(min_length=1, max_length=100)]
    capability: Literal["curriculum_design"] = "curriculum_design"
    grade: Literal[8] = 8
    scope: Literal["section", "year"] = "section"
    instruction: Text
    target_codes: list[Annotated[str, Field(pattern=r"^8\.(?:F|EE)\.[A-C]\.[1-9]$")]] = Field(
        default_factory=list,
        max_length=6,
        description="课段的指定目标；全年必须留空，由固定 CCSS 年级投影确定完整范围",
    )
    school: School
    external_content: list[ExternalContent] = Field(default_factory=list, max_length=5)
    limits: Limits
    language: Literal["zh-CN"] = "zh-CN"

    @model_validator(mode="after")
    def original_scope(self) -> "TaskRequest":
        require_original(self.model_dump())
        if self.scope == "year" and self.target_codes:
            raise ValueError("全年目标由完整年级知识范围确定，不能用目标子集代替")
        if self.school.reserve_lessons >= self.school.lesson_count:
            raise ValueError("机动课时必须小于总课时")
        if self.scope == "section" and (
            not self.target_codes or self.school.lesson_count > 10 or self.school.reserve_lessons
        ):
            raise ValueError("课段需要 1—6 个目标、至多 10 个课时，不单列全年机动时间")
        if len(set(self.target_codes)) != len(self.target_codes):
            raise ValueError("本次目标不得重复")
        if len({x.id for x in self.external_content}) != len(self.external_content):
            raise ValueError("外部内容身份不得重复")
        return self


class Receipt(Contract):
    task_id: str
    run_id: str | None
    request_fingerprint: Fingerprint


class Block(Contract):
    type: Literal["markdown", "table", "image"]
    text: str = ""
    headers: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)
    src: str = ""
    alt: str = ""

    @model_validator(mode="after")
    def valid_block(self) -> "Block":
        if self.type == "table" and (
            not self.headers or any(len(row) != len(self.headers) for row in self.rows)
        ):
            raise ValueError("表格必须有表头且行列一致")
        if self.type == "image" and (
            not re.fullmatch(r"assets/[a-z0-9_-]+\.svg", self.src) or not self.alt
        ):
            raise ValueError("图件必须使用本任务的有效资源引用与说明")
        return self


class Goal(Contract):
    code: Text
    responsibility: Text
    task_ids: list[Text] = Field(min_length=1)
    evidence: Text
    knowledge_use: Text


class KeyTask(Contract):
    id: Annotated[str, Field(pattern=r"^[a-z0-9_-]{1,60}$")]
    purpose: Text
    prompt: Text
    solution: Text
    student_work: Text
    evidence: Text
    anticipated_response: Text
    support: Text
    blocks: list[Block] = Field(default_factory=list, max_length=20)


class LessonIntent(Contract):
    title: Text
    understanding_shift: Text
    task_ids: list[Text] = Field(min_length=1)
    student_minutes: int = Field(ge=1, le=120)
    discussion_minutes: int = Field(ge=1, le=120)
    other_minutes: int = Field(ge=0, le=120)


class Curriculum(Contract):
    schema_version: Literal[1] = 1
    id: Literal["curriculum"] = Field(
        default="curriculum", json_schema_extra={"enum": ["curriculum"]}
    )
    kind: Literal["section"] = Field(default="section", json_schema_extra={"enum": ["section"]})
    title: Text
    narrative: Text
    goals: list[Goal] = Field(min_length=1, max_length=6)
    prerequisites: Text
    successors: Text
    lessons: list[LessonIntent] = Field(min_length=1, max_length=10)
    tasks: list[KeyTask] = Field(min_length=1, max_length=20)
    practice_connections: Text
    teacher_preparation: Text
    assumptions: list[Text] = Field(min_length=1)
    limitations: list[Text] = Field(min_length=1)

    @model_validator(mode="after")
    def valid_references(self) -> "Curriculum":
        require_original(self.model_dump())
        ids = {task.id for task in self.tasks}
        if len(ids) != len(self.tasks):
            raise ValueError("关键任务身份重复")
        references = [g.task_ids for g in self.goals] + [lesson.task_ids for lesson in self.lessons]
        if any(set(refs) - ids for refs in references):
            raise ValueError("目标或课时引用了不存在的关键任务")
        return self


ObjectId = Annotated[str, Field(pattern=r"^[a-z0-9_-]{1,60}$")]


class UnitPlan(Contract):
    id: ObjectId
    title: Text
    lesson_count: int = Field(ge=1, le=240)
    narrative: Text
    prerequisite_units: list[ObjectId]
    entry: Text
    exit: Text
    assessment_plan: Text


class GoalAllocation(Contract):
    unit_id: ObjectId
    role: Literal["teach", "apply", "revisit", "assess"]
    opportunity: Text
    evidence: Text


class YearGoal(Contract):
    code: Text
    allocations: list[GoalAllocation] = Field(min_length=1)


class PracticePlan(Contract):
    code: Annotated[str, Field(pattern=r"^MP[1-8]$")]
    unit_ids: list[ObjectId] = Field(min_length=1)
    student_actions: Text
    evidence: Text


class YearProbe(KeyTask):
    unit_ids: list[ObjectId] = Field(min_length=1)
    design_consequence: Text


class KnowledgeUse(Contract):
    code: Text
    operation: Literal["components", "prerequisites", "successors"]
    record_ids: list[Text] = Field(min_length=1)
    unit_ids: list[ObjectId] = Field(min_length=1)
    decision: Text


class YearBlueprint(Contract):
    schema_version: Literal[1] = 1
    # 当前 Gemini 工具转换不保留 const；显式单值 enum 让模型看到同一约束。
    id: Literal["curriculum"] = Field(
        default="curriculum", json_schema_extra={"enum": ["curriculum"]}
    )
    kind: Literal["grade"] = Field(default="grade", json_schema_extra={"enum": ["grade"]})
    grade: Literal[8] = 8
    title: Text
    narrative: Text
    units: list[UnitPlan] = Field(min_length=1, max_length=20)
    goals: list[YearGoal] = Field(min_length=1)
    practices: list[PracticePlan] = Field(min_length=1, max_length=8)
    tasks: list[YearProbe] = Field(min_length=1, max_length=12)
    knowledge_uses: list[KnowledgeUse] = Field(min_length=1)
    design_inferences: list[Text] = Field(min_length=1)
    prerequisites: Text
    successors: Text
    reserve_lessons: int = Field(ge=0, le=240)
    reserve_plan: Text
    focus_unit_id: ObjectId
    handoff_guidance: Text
    teacher_preparation: Text
    assumptions: list[Text] = Field(min_length=1)
    limitations: list[Text] = Field(min_length=1)

    @model_validator(mode="after")
    def valid_references(self) -> "YearBlueprint":
        require_original(self.model_dump())
        ids = {u.id for u in self.units}
        if len(ids) != len(self.units) or len({t.id for t in self.tasks}) != len(self.tasks):
            raise ValueError("单元或探查任务身份重复")
        refs = [self.focus_unit_id]
        refs.extend(a.unit_id for g in self.goals for a in g.allocations)
        items: list[PracticePlan | YearProbe | KnowledgeUse] = [
            *self.practices,
            *self.tasks,
            *self.knowledge_uses,
        ]
        for item in items:
            refs.extend(item.unit_ids)
        refs.extend(p for u in self.units for p in u.prerequisite_units)
        if set(refs) - ids:
            raise ValueError("全年方案引用了不存在的单元")
        return self


TeachingContent = Annotated[Curriculum | YearBlueprint, Field(discriminator="kind")]
content_adapter: TypeAdapter[TeachingContent] = TypeAdapter(TeachingContent)


class UnitHandoff(Contract):
    parent_fingerprint: Fingerprint
    fingerprint: Fingerprint
    unit: UnitPlan
    goals: list[YearGoal]
    practices: list[PracticePlan]
    probes: list[YearProbe]
    assets: dict[str, dict[str, Any]]
    knowledge_uses: list[KnowledgeUse]
    knowledge_records: list[dict[str, Any]]
    design_inferences: list[Text]
    previous_units: list[UnitPlan]
    successor_units: list[UnitPlan]
    year_narrative: Text
    handoff_guidance: Text
    assumptions: list[Text]
    limitations: list[Text]
    school: School
    standards: list[dict[str, Any]]
    source_snapshot: dict[str, Any]
    status: Text
    checks: "CheckRecord | None"


def parse_content(value: Any) -> Curriculum | YearBlueprint:
    # 兼容早期课段调用未显式提交 kind 的情况。
    return content_adapter.validate_python({"kind": "section", **value})


class Finding(Contract):
    criterion: Literal[
        "coverage", "mathematics", "progression", "conditions", "evidence", "sources"
    ]
    target: Text
    detail: Text
    blocking: bool


class ReviewEvidence(Contract):
    coverage: Text
    mathematics: Text
    progression: Text
    conditions: Text
    evidence: Text
    sources: Text


class Review(Contract):
    findings: list[Finding]
    evidence: ReviewEvidence


class CheckRecord(Review):
    fingerprint: Fingerprint
    rules_fingerprint: str
    method: str
    applicable: bool
    passed: bool


class RenderIssue(Contract):
    location: str
    formula: str | None = None
    message: str


class TaskView(Contract):
    task_id: str
    status: Literal[
        "pending", "running", "completed", "incomplete", "stopped", "cancelled", "failed"
    ]
    native_status: str
    request: TaskRequest
    request_fingerprint: Fingerprint
    unresolved: list[str]
    usage: dict[str, Any]
    content: TeachingContent | None
    fingerprint: Fingerprint | None
    assets: dict[str, str] = Field(default_factory=dict)
    checks: CheckRecord | None
    rendered: bool = False
    render_errors: list[RenderIssue] = Field(default_factory=list)
