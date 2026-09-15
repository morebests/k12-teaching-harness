"""内容接口负责文件、引用和检查的实际往返。"""

import hashlib
import json
from uuid import uuid4

import pytest
from fake_graph import sample_content

from teaching_harness.content import ContentError, ContentStore
from teaching_harness.contracts import Curriculum, Review


def test_公式表格和图件可以渲染且修改后检查失效(tmp_path):
    store = ContentStore(tmp_path, str(uuid4()))
    graph = store.plot_linear(
        "tank",
        slope=3,
        intercept=5,
        x_max=8,
        y_max=30,
        x_label="时间（分钟）",
        y_label="水量（升）",
    )
    source = sample_content()
    source["tasks"][0]["blocks"] = [
        {
            "type": "markdown",
            "text": r"核对 $y=3x+5$。\n\n说明 $x\neq 0$。$\begin{aligned}y&=3x+5\\n&=x+1\end{aligned}$",
        },
        {"type": "table", "headers": ["$x$", "$y$"], "rows": [["2", "11"], ["6", "23"]]},
        {"type": "image", "src": graph["src"], "alt": "水量随时间变化图"},
    ]
    saved = store.save(Curriculum.model_validate(source), None)
    review = Review(
        findings=[],
        evidence={
            k: "固定样本"
            for k in ["coverage", "mathematics", "progression", "conditions", "evidence", "sources"]
        },
    )
    checked = store.check(saved["fingerprint"], review, "规则版本")
    assert checked["checks"]["passed"]
    html = store.rendered()
    submitted = store.review_input()
    assert (
        submitted["render_identity"]["output_fingerprint"]
        == hashlib.sha256(html.encode()).hexdigest()
    )
    assert submitted["review_assets"][graph["src"]]["parameters"]["slope"] == 3
    assert "<math" in html and "<table>" in html and "<svg" in html
    assert r"。\n" not in html and "≠" in html
    assert "<mi>n</mi>" in html
    source["narrative"] += "增加单位比较。"
    changed = store.save(Curriculum.model_validate(source), saved["fingerprint"])
    assert not changed["checks"]["applicable"]
    assert not changed["checks"]["passed"]
    parameters = store.root / "assets/tank.json"
    changed_parameters = json.loads(parameters.read_text())
    changed_parameters["slope"] = 999
    parameters.write_text(json.dumps(changed_parameters))
    with pytest.raises(ContentError, match="参数"):
        store.snapshot()
