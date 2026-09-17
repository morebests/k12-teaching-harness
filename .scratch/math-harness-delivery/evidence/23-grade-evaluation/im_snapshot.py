"""取得 IM 八年级公开规划页面的正文快照，供同尺度证据索引使用。

全文只写入被 Git 忽略的 work/grade-evaluation/im/；仓库只保存来源、日期与指纹。
IM 6–8 Math v.360 按 CC BY-NC 4.0 授权，引用时保留出处。不登录，不读取受保护内容。
用法：uv run python .scratch/math-harness-delivery/evidence/23-grade-evaluation/im_snapshot.py
"""

import hashlib
import json
import re
import time
from datetime import UTC, datetime
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "work/grade-evaluation/im"
SOURCES = Path(__file__).with_name("im-sources.json")
BASE = "https://accessim.org/6-8/grade-8"
PAGES = {
    "im-g8-scope-sequence": ("全年范围与顺序", f"{BASE}/course-guide/scope-and-sequence?a=teacher"),
    "im-g8-assessment-guidance": ("评价指导", f"{BASE}/course-guide/assessment-guidance?a=teacher"),
    **{f"im-g8-unit-{n}": (f"第 {n} 单元总页", f"{BASE}/unit-{n}?a=teacher") for n in range(1, 10)},
}
BLOCKS = {"p", "div", "li", "br", "tr", "section", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol"}
SKIP = {"script", "style", "noscript", "svg", "template"}


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in SKIP:
            self.skip += 1
        elif tag in BLOCKS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
        elif tag in BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.parts.append(data)


def page_text(html: str) -> str:
    parser = TextExtractor()
    parser.feed(html)
    text = unescape("".join(parser.parts)).replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    today = datetime.now(UTC).astimezone().date().isoformat()
    sources = []
    with httpx.Client(
        headers={"User-Agent": "Mozilla/5.0"}, timeout=60, follow_redirects=True
    ) as http:
        for page_id, (title, url) in PAGES.items():
            response = http.get(url)
            response.raise_for_status()
            text = page_text(response.text)
            path = OUT / f"{page_id}.txt"
            path.write_text(text)
            sources.append(
                {
                    "id": page_id,
                    "title": title,
                    "url": url,
                    "retrieved": today,
                    "snapshot": path.relative_to(ROOT).as_posix(),
                    "sha256": hashlib.sha256(text.encode()).hexdigest(),
                    "characters": len(text),
                    "html_sha256": hashlib.sha256(response.content).hexdigest(),
                    "sign_in_prompt": "Sign in to access protected content" in text,
                }
            )
            time.sleep(1)
    SOURCES.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
