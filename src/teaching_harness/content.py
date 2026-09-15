"""当前 JSON 内容与指纹检查；同目录串行、写完整再替换。"""

import fcntl
import hashlib
import json
import os
import re
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import UUID

from teaching_harness.contracts import Curriculum, Review, fingerprint
from teaching_harness.rendering import linear_svg, render_curriculum


class ContentError(ValueError):
    pass


class ContentStore:
    def __init__(self, root: Path, thread_id: str) -> None:
        self.root = root.resolve() / str(UUID(thread_id))

    @contextmanager
    def locked(self) -> Iterator[None]:
        self.root.mkdir(parents=True, exist_ok=True)
        with (self.root / ".write.lock").open("a") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def _write(self, name: str, data: bytes) -> None:
        target = self.root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=target.parent)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp, target)
        finally:
            Path(tmp).unlink(missing_ok=True)

    def _json(self, name: str) -> Any:
        path = self.root / name
        return json.loads(path.read_text()) if path.exists() else None

    def record(self, name: str, value: Any) -> None:
        if name not in {"knowledge.json", "execution.json", "context.json"}:
            raise ContentError("记录类型不受支持")
        with self.locked():
            self._write(name, json.dumps(value, ensure_ascii=False, indent=2).encode())

    def _snapshot(self) -> dict[str, Any]:
        content = self._json("content/curriculum.json")
        if content is None:
            return {"content": None, "fingerprint": None, "checks": None}
        curriculum = Curriculum.model_validate(content)
        assets: dict[str, str] = {}
        for task in curriculum.tasks:
            for block in task.blocks:
                if block.type == "image":
                    path = self.root / block.src
                    if not path.is_file() or path.is_symlink():
                        raise ContentError("当前内容包含缺失或无效的图件引用")
                    assets[block.src] = hashlib.sha256(path.read_bytes()).hexdigest()
        source_digest = fingerprint({"content": content, "assets": assets})
        rendering = self._json("output/render.json")
        output = self.root / "output/curriculum.html"
        output_digest = (
            hashlib.sha256(output.read_bytes()).hexdigest() if output.is_file() else None
        )
        rendered = bool(
            rendering
            and rendering.get("source_fingerprint") == source_digest
            and rendering.get("output_fingerprint") == output_digest
        )
        digest = fingerprint({"content": content, "assets": assets, "output": output_digest})
        checks = self._json("checks.json")
        if checks:
            checks["applicable"] = checks["fingerprint"] == digest
            checks["passed"] = (
                checks["applicable"]
                and rendered
                and not any(x["blocking"] for x in checks["findings"])
            )
        return {
            "content": content,
            "fingerprint": digest,
            "assets": assets,
            "checks": checks,
            "rendered": rendered,
        }

    def snapshot(self) -> dict[str, Any]:
        with self.locked():
            return self._snapshot()

    def save(self, content: Curriculum, expected: str | None) -> dict[str, Any]:
        with self.locked():
            previous = self._snapshot()
            if previous["fingerprint"] != expected:
                raise ContentError("当前稿已改变；请重新读取后再保存")
            for task in content.tasks:
                for block in task.blocks:
                    if block.type == "image" and not (self.root / block.src).is_file():
                        raise ContentError("必须先创建图件再引用")
            self._write("content/curriculum.json", content.model_dump_json(indent=2).encode())
            asset_text = {
                b.src: (self.root / b.src).read_text()
                for t in content.tasks
                for b in t.blocks
                if b.type == "image"
            }
            try:
                html = render_curriculum(content, asset_text).encode()
            except (ValueError, TimeoutError, OSError):
                # 源稿保留；旧渲染清单与新源不匹配，不会被提升为当前通过。
                return self._snapshot()
            self._write("output/curriculum.html", html)
            source_digest = fingerprint(
                {
                    "content": content.model_dump(),
                    "assets": {
                        k: hashlib.sha256(v.encode()).hexdigest() for k, v in asset_text.items()
                    },
                }
            )
            self._write(
                "output/render.json",
                json.dumps(
                    {
                        "source_fingerprint": source_digest,
                        "output_fingerprint": hashlib.sha256(html).hexdigest(),
                        "renderer_version": 1,
                    }
                ).encode(),
            )
            return self._snapshot()

    def plot_linear(
        self,
        name: str,
        *,
        slope: float,
        intercept: float,
        x_max: float,
        y_max: float,
        x_label: str,
        y_label: str,
        expected_fingerprint: str | None = None,
    ) -> dict[str, Any]:
        if not re.fullmatch(r"[a-z0-9_-]{1,60}", name):
            raise ContentError("图件身份无效")
        parameters = {
            "slope": slope,
            "intercept": intercept,
            "x_max": x_max,
            "y_max": y_max,
            "x_label": x_label,
            "y_label": y_label,
        }
        svg = linear_svg(**parameters)  # type: ignore[arg-type]
        with self.locked():
            if (self.root / f"assets/{name}.svg").exists() and self._snapshot()[
                "fingerprint"
            ] != expected_fingerprint:
                raise ContentError("修改图件需要当前内容指纹")
            self._write(f"assets/{name}.json", json.dumps(parameters, ensure_ascii=False).encode())
            self._write(f"assets/{name}.svg", svg.encode())
        return {
            "src": f"assets/{name}.svg",
            "fingerprint": hashlib.sha256(svg.encode()).hexdigest(),
            "parameters": parameters,
        }

    def rendered(self, expected: str | None = None) -> str:
        with self.locked():
            current = self._snapshot()
            if expected and current["fingerprint"] != expected:
                raise ContentError("阅读稿对应的内容已改变")
            if not current.get("rendered"):
                raise ContentError("当前稿尚无有效阅读稿")
            return (self.root / "output/curriculum.html").read_text()

    def review_assets(self) -> dict[str, Any]:
        with self.locked():
            current = self._snapshot()
            result = {}
            for name in current.get("assets", {}):
                result[name] = {
                    "svg": (self.root / name).read_text(),
                    "parameters": self._json(name.removesuffix(".svg") + ".json"),
                }
            return result

    def evidence(self) -> dict[str, Any]:
        with self.locked():
            return {
                name: self._json(name + ".json") for name in ["context", "knowledge", "execution"]
            }

    def check(self, expected: str, review: Review, rules: str) -> dict[str, Any]:
        with self.locked():
            if self._snapshot()["fingerprint"] != expected:
                raise ContentError("检查对象已改变，旧检查不能应用于当前稿")
            self._write(
                "checks.json",
                json.dumps(
                    {
                        "fingerprint": expected,
                        "rules_fingerprint": rules,
                        "method": "程序核对与隔离模型审阅；未经过教师校准",
                        **review.model_dump(),
                    },
                    ensure_ascii=False,
                    indent=2,
                ).encode(),
            )
            return self._snapshot()
