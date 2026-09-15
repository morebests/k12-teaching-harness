"""由唯一 JSON 源生成可读 HTML 与有限线性函数图。"""

import json
import math
import re
import subprocess
from html import escape
from pathlib import Path
from typing import Any

from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin

from teaching_harness.contracts import Curriculum


def linear_svg(
    slope: float, intercept: float, x_max: float, y_max: float, x_label: str, y_label: str
) -> str:
    if (
        not all(math.isfinite(v) and abs(v) <= 1000000 for v in (slope, intercept, x_max, y_max))
        or x_max <= 0
        or y_max <= 0
    ):
        raise ValueError("坐标范围或函数参数无效")
    if max(len(x_label), len(y_label)) > 30:
        raise ValueError("坐标标签过长，请缩短并在正文解释单位")
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 480" role="img">',
        f"<title>{escape(y_label)}随{escape(x_label)}变化</title>",
        '<rect width="680" height="480" fill="white"/>',
        '<defs><clipPath id="plot"><rect x="100" y="55" width="500" height="340"/></clipPath></defs>',
    ]
    for i in range(6):
        x, y = 100 + i * 100, 395 - i * 68
        parts.extend(
            [
                f'<path d="M{x} 55V395 M100 {y}H600" stroke="#ccc" fill="none"/>',
                f'<text x="{x}" y="420" text-anchor="middle" font-size="16">{x_max * i / 5:g}</text>',
                f'<text x="88" y="{y + 5}" text-anchor="end" font-size="16">{y_max * i / 5:g}</text>',
            ]
        )
    parts.extend(
        [
            '<path d="M100 55V395H600" stroke="#222" fill="none" stroke-width="2"/>',
            f'<path d="M100 {395 - intercept / y_max * 340} L600 {395 - (slope * x_max + intercept) / y_max * 340}" stroke="#174c70" fill="none" stroke-width="3" clip-path="url(#plot)"/>',
            f'<text x="350" y="458" text-anchor="middle" font-size="18">{escape(x_label)}</text>',
            f'<text x="100" y="28" font-size="18">{escape(y_label)}</text>',
            "</svg>",
        ]
    )
    return "".join(parts)


def render_curriculum(content: Curriculum, assets: dict[str, str]) -> str:
    md = MarkdownIt("commonmark", {"html": False}).enable("table").use(dollarmath_plugin)
    formulas: list[tuple[str, bool]] = []
    paragraphs: list[Any] = []

    def collect(tokens: Any) -> None:
        for token in tokens:
            if token.type in {"math_inline", "math_block"}:
                token.meta["formula_index"] = len(formulas)
                formulas.append((token.content, token.type == "math_block"))
            if token.children:
                collect(token.children)

    def text(value: str) -> str:
        # 同时接受常见的 \(...\) 与 \[...\]，渲染变换不改 JSON 源。
        value = re.sub(r"\\\((.*?)\\\)", r"$\1$", value, flags=re.DOTALL)
        value = re.sub(r"\\\[(.*?)\\\]", r"\n$$\1$$\n", value, flags=re.DOTALL)
        tokens = md.parse(value)
        collect(tokens)
        paragraphs.append(tokens)
        return f"<!--paragraph-{len(paragraphs) - 1}-->"

    pieces = [
        f"<h1>{escape(content.title)}</h1>",
        '<p class="scope">有限课段方案与关键任务构想 · 检查状态请查看任务结果</p>',
        text(content.narrative),
        "<h2>目标与证据</h2>",
    ]
    for goal in content.goals:
        pieces.extend(
            [
                f"<h3>{escape(goal.code)}</h3>",
                text(goal.responsibility),
                text(goal.knowledge_use),
                text(goal.evidence),
            ]
        )
    pieces.extend(
        [
            "<h2>先备与后续</h2>",
            text(content.prerequisites),
            text(content.successors),
            "<h2>学习进程</h2>",
        ]
    )
    for lesson in content.lessons:
        pieces.extend(
            [
                f"<h3>{escape(lesson.title)}</h3>",
                text(lesson.understanding_shift),
                f"<p>学生工作 {lesson.student_minutes} 分钟 · 讨论 {lesson.discussion_minutes} 分钟 · 其他 {lesson.other_minutes} 分钟</p>",
            ]
        )
    for task in content.tasks:
        pieces.extend(
            [
                f'<section id="{escape(task.id)}"><h2>关键任务 · {escape(task.id)}</h2>',
                text(task.purpose),
                text(task.prompt),
            ]
        )
        for block in task.blocks:
            if block.type == "markdown":
                pieces.append(text(block.text))
            elif block.type == "table":
                pieces.append(
                    "<table><thead><tr>"
                    + "".join(f"<th>{text(h)}</th>" for h in block.headers)
                    + "</tr></thead><tbody>"
                )
                for row in block.rows:
                    pieces.append("<tr>" + "".join(f"<td>{text(c)}</td>" for c in row) + "</tr>")
                pieces.append("</tbody></table>")
            else:
                pieces.extend(
                    [
                        "<figure>",
                        assets[block.src],
                        f"<figcaption>{escape(block.alt)}</figcaption></figure>",
                    ]
                )
        for label, value in [
            ("解答与条件", task.solution),
            ("学生数学工作", task.student_work),
            ("观察证据", task.evidence),
            ("预判回应", task.anticipated_response),
            ("支持", task.support),
        ]:
            pieces.extend([f"<h3>{label}</h3>", text(value)])
        pieces.append("</section>")
    pieces.extend(
        [
            "<h2>实践与准备</h2>",
            text(content.practice_connections),
            text(content.teacher_preparation),
            "<h2>假设与交付边界</h2>",
            *[text(x) for x in content.assumptions + content.limitations],
        ]
    )
    if sum(len(f[0]) for f in formulas) > 100000 or len(formulas) > 500:
        raise ValueError("公式排版超过本切片范围")
    math_html = []
    if formulas:
        rendered = subprocess.run(
            ["node", str(Path(__file__).with_name("resources") / "render-math.cjs")],
            input=json.dumps(formulas),
            text=True,
            capture_output=True,
            timeout=20,
            check=False,
        )
        if rendered.returncode:
            raise ValueError("公式排版失败，当前稿保留供修订")
        math_html = json.loads(rendered.stdout)

    def math_rule(tokens: Any, index: int, options: Any, env: Any) -> str:
        return math_html[tokens[index].meta["formula_index"]]

    def bound_math_rule(self: Any, tokens: Any, index: int, options: Any, env: Any) -> str:
        return math_rule(tokens, index, options, env)

    md.add_render_rule("math_inline", bound_math_rule)
    md.add_render_rule("math_block", bound_math_rule)
    body = "".join(pieces)
    for i, tokens in enumerate(paragraphs):
        body = body.replace(f"<!--paragraph-{i}-->", md.renderer.render(tokens, md.options, {}))
    return (
        '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'
        + escape(content.title)
        + "</title><style>body{max-width:900px;margin:36px auto;padding:0 24px;font:17px/1.7 system-ui;color:#17212a}h1{font-size:30px}h2{margin-top:36px}h3{font-size:18px}.scope{color:#586472}table{border-collapse:collapse;width:100%}td,th{border:1px solid #abb5bf;padding:8px}figure{margin:20px 0}svg{max-width:680px;width:100%;height:auto}section{border-top:1px solid #bbb;margin-top:32px}math{font-size:1.12em}@media print{body{margin:0;font-size:11pt}h2,h3{break-after:avoid}table,figure{break-inside:avoid}}</style><body>"
        + body
        + "</body></html>"
    )
