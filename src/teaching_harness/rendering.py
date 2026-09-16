"""由唯一 JSON 源生成可读 HTML 与有限线性函数图。"""

import json
import math
import re
import subprocess
from collections.abc import Callable
from html import escape
from pathlib import Path
from typing import Any

from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin

from teaching_harness.contracts import Curriculum, RenderIssue, YearBlueprint, YearProbe


class RenderingError(ValueError):
    def __init__(self, issues: list[RenderIssue]) -> None:
        super().__init__("阅读稿生成失败，请按具体字段修复后重新保存")
        self.issues = issues


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


def year_sections(content: YearBlueprint, text: Callable[[str, str], str]) -> list[str]:
    pieces = [
        f"<h1>{escape(content.title)}</h1>",
        '<p class="scope">全年课程蓝图 · 关键任务为可行性探查，逐课材料尚待展开</p>',
        text(content.narrative, "narrative"),
        "<h2>单元顺序与课时</h2>",
        "<table><thead><tr><th>单元</th><th>课时</th><th>承担目标</th></tr></thead><tbody>",
    ]
    for unit in content.units:
        goals = [g.code for g in content.goals if any(a.unit_id == unit.id for a in g.allocations)]
        pieces.append(
            f'<tr><td><a href="#{unit.id}">{escape(unit.title)}</a></td><td>{unit.lesson_count}</td><td>{escape("、".join(goals))}</td></tr>'
        )
    pieces.extend(
        [
            f"</tbody></table><p>教学、练习与评价合计 {sum(u.lesson_count for u in content.units)} 课时；机动 {content.reserve_lessons} 课时。</p>",
            text(content.reserve_plan, "reserve_plan"),
            "<h2>前后年级联系</h2>",
            text(content.prerequisites, "prerequisites"),
            text(content.successors, "successors"),
        ]
    )
    for i, unit in enumerate(content.units):
        path = f"units.{i}"
        pieces.append(
            f'<section id="{unit.id}"><h2>{escape(unit.title)} · {unit.lesson_count} 课时</h2>'
        )
        pieces.append(text(unit.narrative, f"{path}.narrative"))
        pieces.append(
            f"<p>本设计先备单元：{escape('、'.join(unit.prerequisite_units) or '无；依进入检查决定支持')}</p>"
        )
        for label, field in [
            ("进入条件", "entry"),
            ("完成时的数学工作", "exit"),
            ("练习与评价安排", "assessment_plan"),
        ]:
            pieces.extend([f"<h3>{label}</h3>", text(getattr(unit, field), f"{path}.{field}")])
        pieces.append("</section>")
    pieces.extend(
        [
            "<h2>目标覆盖与学习机会</h2>",
            "<p>包含父标准的整体要求和必要子项；父子不重复计数为额外目标。下列机会须由后续课时材料兑现。</p>",
        ]
    )
    roles = {"teach": "教授", "apply": "应用", "revisit": "复习", "assess": "评价"}
    for i, goal in enumerate(content.goals):
        pieces.append(f"<h3>{escape(goal.code)}</h3>")
        for j, a in enumerate(goal.allocations):
            pieces.extend(
                [
                    f'<p><a href="#{a.unit_id}">{escape(a.unit_id)}</a> · {roles[a.role]}</p>',
                    text(a.opportunity, f"goals.{i}.allocations.{j}.opportunity"),
                    text(a.evidence, f"goals.{i}.allocations.{j}.evidence"),
                ]
            )
    pieces.append("<h2>八项数学实践</h2>")
    for i, p in enumerate(content.practices):
        pieces.extend(
            [
                f"<h3>{escape(p.code)} · {escape('、'.join(p.unit_ids))}</h3>",
                text(p.student_actions, f"practices.{i}.student_actions"),
                text(p.evidence, f"practices.{i}.evidence"),
            ]
        )
    pieces.extend(
        [
            f'<h2>目标单元交接 · <a href="#{content.focus_unit_id}">{escape(content.focus_unit_id)}</a></h2>',
            text(content.handoff_guidance, "handoff_guidance"),
            "<h2>知识采用与设计推断</h2>",
        ]
    )
    for i, use in enumerate(content.knowledge_uses):
        pieces.extend(
            [
                f"<h3>{escape(use.code)} · {escape(use.operation)}</h3>",
                text(use.decision, f"knowledge_uses.{i}.decision"),
                f"<small>来源记录：{escape('、'.join(use.record_ids))}</small>",
            ]
        )
    pieces.extend(
        text(x, f"design_inferences.{i}") for i, x in enumerate(content.design_inferences)
    )
    pieces.append(
        "<h2>关键任务探查</h2><p>以下探查用于检验单元职责和数学跨度，尚非完整 Lesson。</p>"
    )
    return pieces


def render_curriculum(content: Curriculum | YearBlueprint, assets: dict[str, str]) -> str:
    md = (
        MarkdownIt("commonmark", {"html": False})
        .enable("table")
        .use(dollarmath_plugin, double_inline=True, allow_labels=False)
    )
    formulas: list[tuple[str, bool]] = []
    locations: list[str] = []
    paragraphs: list[Any] = []
    issues: list[RenderIssue] = []

    def unclosed_math(state: Any, silent: bool) -> bool:
        # 仅在正常公式规则未匹配时运行；反引号代码已由 Markdown 处理。
        remaining = state.src[state.pos :]
        # 独立的 $5 可作为金额；其它未匹配的美元定界符需修复或显式转义。
        currency = re.match(r"\$\d+(?:\.\d+)?(?=$|[\s,.;!?，。；！？：:])", remaining)
        if (remaining.startswith("$") and not currency) or re.match(
            r"\\(?:[\[\]()]|(?:frac|dfrac|tfrac|hat|sqrt|Delta|times|cdot|begin|end)\b)", remaining
        ):
            issues.append(
                RenderIssue(
                    location=state.env["location"],
                    formula=remaining[:1000],
                    message="公式分隔符未配对或 LaTeX 命令落在公式外，请使用完整的 $…$、$$…$$、\\(…\\) 或 \\[…\\]；普通美元符号写作 \\$",
                )
            )
        return False

    md.inline.ruler.after("math_inline", "unclosed_math", unclosed_math)

    def collect(tokens: Any, location: str) -> None:
        for token in tokens:
            if token.type in {"math_inline", "math_inline_double", "math_block"}:
                if re.search(
                    r"(?<!\\)\\\\(?:frac|dfrac|tfrac|times|cdot|Delta|ldots|neq|leq|geq|text|begin|end|sqrt|left|right)\b",
                    token.content,
                ):
                    issues.append(
                        RenderIssue(
                            location=location,
                            formula=token.content,
                            message="LaTeX 命令前出现重复反斜杠，会被解释为换行和普通字母；请修复源中的命令转义，例如实际字符串用一个反斜杠的 \\frac。aligned 等环境的行分隔符仍保留两个反斜杠。",
                        )
                    )
                token.meta["formula_index"] = len(formulas)
                formulas.append((token.content, token.type != "math_inline"))
                locations.append(location)
            if token.children:
                collect(token.children, location)

    def text(value: str, location: str) -> str:
        # 模型偶尔把正文换行再次转义；只展开独立的换行标记，不碰 \neq 等公式命令。
        value = re.sub(r"(?<!\\)\\n(?![A-Za-z])", "\n", value)
        # 同时接受常见的 \(...\) 与 \[...\]，渲染变换不改 JSON 源。
        value = re.sub(r"\\\((.*?)\\\)", r"$\1$", value, flags=re.DOTALL)
        value = re.sub(r"\\\[(.*?)\\\]", r"\n$$\1$$\n", value, flags=re.DOTALL)
        tokens = md.parse(value, {"location": location})
        collect(tokens, location)
        paragraphs.append(tokens)
        return f"<!--paragraph-{len(paragraphs) - 1}-->"

    if isinstance(content, YearBlueprint):
        pieces = year_sections(content, text)
    else:
        pieces = [
            f"<h1>{escape(content.title)}</h1>",
            '<p class="scope">有限课段方案与关键任务构想 · 检查状态请查看任务结果</p>',
            text(content.narrative, "narrative"),
            "<h2>目标与证据</h2>",
        ]
        for i, goal in enumerate(content.goals):
            pieces.extend(
                [
                    f"<h3>{escape(goal.code)}</h3>",
                    text(goal.responsibility, f"goals.{i}.responsibility"),
                    text(goal.knowledge_use, f"goals.{i}.knowledge_use"),
                    text(goal.evidence, f"goals.{i}.evidence"),
                ]
            )
        pieces.extend(
            [
                "<h2>先备与后续</h2>",
                text(content.prerequisites, "prerequisites"),
                text(content.successors, "successors"),
                "<h2>学习进程</h2>",
            ]
        )
        for i, lesson in enumerate(content.lessons):
            pieces.extend(
                [
                    f"<h3>{escape(lesson.title)}</h3>",
                    text(lesson.understanding_shift, f"lessons.{i}.understanding_shift"),
                    f"<p>学生工作 {lesson.student_minutes} 分钟 · 讨论 {lesson.discussion_minutes} 分钟 · 其他 {lesson.other_minutes} 分钟</p>",
                ]
            )
    for i, task in enumerate(content.tasks):
        path = f"tasks.{i}"
        pieces.extend(
            [
                f'<section id="{escape(task.id)}"><h2>关键任务 · {escape(task.id)}</h2>',
                text(task.purpose, f"{path}.purpose"),
                text(task.prompt, f"{path}.prompt"),
            ]
        )
        for j, block in enumerate(task.blocks):
            block_path = f"{path}.blocks.{j}"
            if block.type == "markdown":
                pieces.append(text(block.text, f"{block_path}.text"))
            elif block.type == "table":
                pieces.append(
                    "<table><thead><tr>"
                    + "".join(
                        f"<th>{text(h, f'{block_path}.headers.{k}')}</th>"
                        for k, h in enumerate(block.headers)
                    )
                    + "</tr></thead><tbody>"
                )
                for k, row in enumerate(block.rows):
                    pieces.append(
                        "<tr>"
                        + "".join(
                            f"<td>{text(c, f'{block_path}.rows.{k}.{n}')}</td>"
                            for n, c in enumerate(row)
                        )
                        + "</tr>"
                    )
                pieces.append("</tbody></table>")
            else:
                pieces.extend(
                    [
                        "<figure>",
                        assets[block.src],
                        f"<figcaption>{escape(block.alt)}</figcaption></figure>",
                    ]
                )
        for label, field in [
            ("解答与条件", "solution"),
            ("学生数学工作", "student_work"),
            ("观察证据", "evidence"),
            ("预判回应", "anticipated_response"),
            ("支持", "support"),
        ]:
            pieces.extend([f"<h3>{label}</h3>", text(getattr(task, field), f"{path}.{field}")])
        if isinstance(task, YearProbe):
            pieces.extend(
                [
                    "<h3>对全年安排的影响</h3>",
                    text(task.design_consequence, f"{path}.design_consequence"),
                ]
            )
        pieces.append("</section>")
    pieces.extend(
        [
            "<h2>实践与准备</h2>",
            *(
                [text(content.practice_connections, "practice_connections")]
                if isinstance(content, Curriculum)
                else []
            ),
            text(content.teacher_preparation, "teacher_preparation"),
            "<h2>假设与交付边界</h2>",
            *[text(x, f"assumptions.{i}") for i, x in enumerate(content.assumptions)],
            *[text(x, f"limitations.{i}") for i, x in enumerate(content.limitations)],
        ]
    )
    if issues:
        raise RenderingError(issues)
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
        result = json.loads(rendered.stdout)
        if result["errors"]:
            raise RenderingError(
                [
                    RenderIssue(
                        location=locations[e["index"]],
                        formula=formulas[e["index"]][0],
                        message=e["message"],
                    )
                    for e in result["errors"]
                ]
            )
        math_html = result["html"]

    def math_rule(tokens: Any, index: int, options: Any, env: Any) -> str:
        return math_html[tokens[index].meta["formula_index"]]

    def bound_math_rule(self: Any, tokens: Any, index: int, options: Any, env: Any) -> str:
        return math_rule(tokens, index, options, env)

    md.add_render_rule("math_inline", bound_math_rule)
    md.add_render_rule("math_inline_double", bound_math_rule)
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
