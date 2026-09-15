"""当前切片的教学输入、内容和查询契约；由这些类型导出 JSON Schema。"""

import hashlib
import json
import re
from typing import Annotated, Any, Literal
from uuid import NAMESPACE_URL, uuid5

from pydantic import BaseModel, ConfigDict, Field, model_validator

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
    lesson_count: int = Field(ge=1, le=10)
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
        if len(json.dumps(self.content)) > 80000:
            raise ValueError("外部内容超过本次接入上限，请按任务范围提供")
        return self


class Limits(Contract):
    # 必须显式提供；当前没有经质量校准的生产默认预算。
    model_calls: int = Field(ge=1, le=100)
    tool_calls: int = Field(ge=1, le=300)
    total_tokens: int = Field(ge=1000, le=2000000)
    seconds: int = Field(ge=1, le=7200)


class TaskRequest(Contract):
    schema_version: Literal[1] = 1
    event_id: Annotated[str, Field(min_length=1, max_length=100)]
    capability: Literal["curriculum_design"] = "curriculum_design"
    grade: Literal[8] = 8
    scope: Literal["section"] = "section"
    instruction: Text
    target_codes: list[Annotated[str, Field(pattern=r"^8\.(?:F|EE)\.[A-C]\.[1-9]$")]] = Field(
        min_length=1, max_length=6
    )
    school: School
    external_content: list[ExternalContent] = Field(default_factory=list, max_length=5)
    limits: Limits
    language: Literal["zh-CN"] = "zh-CN"

    @model_validator(mode="after")
    def original_scope(self) -> "TaskRequest":
        require_original(self.model_dump())
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
    id: Literal["curriculum"] = "curriculum"
    kind: Literal["section"] = "section"
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
    content: Curriculum | None
    fingerprint: Fingerprint | None
    assets: dict[str, str] = Field(default_factory=dict)
    checks: CheckRecord | None
    rendered: bool = False
