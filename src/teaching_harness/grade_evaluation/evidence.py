"""把被评材料登记为带指纹的来源，并按实际位置回取原文作为证据。"""

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Literal

from teaching_harness.grade_evaluation.records import (
    EvidenceRecord,
    ObjectRef,
    Origin,
    SourceDocument,
)

Verification = Literal[
    "verified",
    "document_unknown",
    "snapshot_missing",
    "document_changed",
    "locator_invalid",
    "quote_mismatch",
]
ELLIPSIS = re.compile(r"……|…|\.\.\.")


class EvidenceError(ValueError):
    pass


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pointer_parts(pointer: str) -> list[str]:
    """RFC 6901：拆分 JSON Pointer 并还原转义。"""
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer.split("/")[1:]]


def register(
    path: Path,
    *,
    root: Path,
    id: str,
    party: str,
    role: str,
    title: str,
    locator: str | None = None,
    retrieved: str | date | None = None,
    access: str = "complete",
    access_note: str = "",
) -> SourceDocument:
    """登记实际快照；外部网页的 locator 是原始 URL，snapshot 是本地取得的正文。"""
    snapshot = path.resolve().relative_to(root.resolve()).as_posix()
    return SourceDocument.model_validate(
        {
            "id": id,
            "party": party,
            "role": role,
            "title": title,
            "locator": locator or snapshot,
            "snapshot": snapshot,
            "media": "json" if path.suffix == ".json" else "text",
            "fingerprint": file_sha256(path),
            "retrieved": retrieved,
            "access": access,
            "access_note": access_note,
        }
    )


def _pointer(value: Any, locator: str) -> Any:
    if not locator.startswith("/"):
        raise EvidenceError(f"JSON 文档需要 JSON Pointer 位置：{locator}")
    for key in pointer_parts(locator):
        if isinstance(value, list) and key.isdigit() and int(key) < len(value):
            value = value[int(key)]
        elif isinstance(value, dict) and key in value:
            value = value[key]
        else:
            raise EvidenceError(f"文档中没有这个位置：{locator}")
    return value


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _compact(text: str) -> str:
    # 模型转写 JSON 中的 LaTeX 时常多出一层反斜杠转义；只归一这一层与空白。
    return re.sub(r"\s+", "", text).replace("\\\\", "\\")


def quote_found(quote: str, text: str) -> bool:
    """片段须逐字出现；省略号分隔的多段须按顺序出现。空白与多余转义层不计。"""
    position, source = 0, _compact(text)
    for part in filter(None, (_compact(p) for p in ELLIPSIS.split(quote))):
        position = source.find(part, position)
        if position < 0:
            return False
        position += len(part)
    return position > 0


def value_at(document: SourceDocument, root: Path, locator: str) -> str:
    """回取当前快照在该位置的原文；不核对指纹。"""
    data = (root / document.snapshot).read_text()
    if document.media == "json":
        return _text(_pointer(json.loads(data), locator))
    match = re.fullmatch(r"chars:(\d+)-(\d+)", locator)
    if not match or int(match[2]) > len(data) or int(match[1]) >= int(match[2]):
        raise EvidenceError(f"文本快照中没有这个位置：{locator}")
    return data[int(match[1]) : int(match[2])]


def evidence_id(document_id: str, locator: str, quote: str, extraction: str) -> str:
    """同一位置、原文与提取得到同一身份；未能核实的引用也据此登记为失效。"""
    digest = hashlib.sha256(f"{locator}\n{quote}\n{extraction}".encode()).hexdigest()[:16]
    return f"ev:{document_id}:{digest}"


def cite(
    document: SourceDocument,
    root: Path,
    locator: str | None,
    *,
    extraction: str,
    recorded_by: Origin,
    quote: str | None = None,
    objects: list[ObjectRef] | None = None,
) -> EvidenceRecord:
    """建立证据；片段必须能在实际位置找到，文本来源可按片段定位字符区间。"""
    if not (root / document.snapshot).is_file():
        raise EvidenceError("来源快照不存在")
    if locator is None:
        if document.media == "json" or quote is None:
            raise EvidenceError("JSON 来源必须给出位置")
        start = (root / document.snapshot).read_text().find(quote)
        if start < 0:
            raise EvidenceError("文本快照中找不到该原文片段")
        locator = f"chars:{start}-{start + len(quote)}"
    source = value_at(document, root, locator)
    if quote is None:
        quote = source
    elif not quote_found(quote, source):
        raise EvidenceError(f"该位置的原文不包含所给片段：{locator}")
    return EvidenceRecord(
        id=evidence_id(document.id, locator, quote, extraction),
        document_id=document.id,
        document_fingerprint=document.fingerprint,
        locator=locator,
        quote=quote,
        extraction=extraction,
        objects=objects or [],
        recorded_by=recorded_by,
    )


def verify(
    record: EvidenceRecord, documents: dict[str, SourceDocument], root: Path
) -> Verification:
    document = documents.get(record.document_id)
    if document is None:
        return "document_unknown"
    path = root / document.snapshot
    if not path.is_file():
        return "snapshot_missing"
    if (
        file_sha256(path) != document.fingerprint
        or record.document_fingerprint != document.fingerprint
    ):
        return "document_changed"
    try:
        source = value_at(document, root, record.locator)
    except EvidenceError:
        return "locator_invalid"
    return "verified" if quote_found(record.quote, source) else "quote_mismatch"
