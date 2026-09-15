"""从正式类型导出教学契约；原生运行 API 由 Agent Server 自身提供。"""

import json
from pathlib import Path

from teaching_harness.api import app
from teaching_harness.contracts import Curriculum, Review, TaskRequest, TaskView

target = Path(__file__).resolve().parents[1] / "docs/contracts"
target.mkdir(parents=True, exist_ok=True)
for name, model in [
    ("task-request", TaskRequest),
    ("curriculum", Curriculum),
    ("review", Review),
    ("task-view", TaskView),
]:
    (target / f"{name}.schema.json").write_text(
        json.dumps(model.model_json_schema(), ensure_ascii=False, indent=2) + "\n"
    )
(target / "content.openapi.json").write_text(
    json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n"
)
