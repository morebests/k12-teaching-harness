"""从正式类型导出教学契约；原生运行 API 由 Agent Server 自身提供。"""

import json
from pathlib import Path

from teaching_harness.api import app
from teaching_harness.contracts import (
    Review,
    TaskRequest,
    TaskView,
    UnitHandoff,
    YearBlueprint,
    content_adapter,
)

target = Path(__file__).resolve().parents[1] / "docs/contracts"
target.mkdir(parents=True, exist_ok=True)
for name, model in [
    ("task-request", TaskRequest),
    ("year-blueprint", YearBlueprint),
    ("unit-handoff", UnitHandoff),
    ("review", Review),
    ("task-view", TaskView),
]:
    (target / f"{name}.schema.json").write_text(
        json.dumps(model.model_json_schema(), ensure_ascii=False, indent=2) + "\n"
    )
(target / "curriculum.schema.json").write_text(
    json.dumps(content_adapter.json_schema(), ensure_ascii=False, indent=2) + "\n"
)
(target / "content.openapi.json").write_text(
    json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n"
)
