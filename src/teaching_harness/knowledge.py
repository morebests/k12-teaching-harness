"""只读 browse 适配：动态解析 CCSS，保留分页、源身份及关系方向。"""

import os
import re
from graphlib import CycleError, TopologicalSorter
from typing import Any, Literal
from urllib.parse import quote

import httpx

from teaching_harness.contracts import fingerprint, require_original

Operation = Literal["standard", "components", "prerequisites", "successors"]


class KnowledgeError(ValueError):
    def __init__(self, message: str, result_status: str = "error") -> None:
        super().__init__(message)
        self.result_status = result_status


class Knowledge:
    def __init__(self, client: httpx.AsyncClient, page_size: int = 100) -> None:
        self.client = client
        self.page_size = page_size
        self.identity: dict[str, Any] = {}
        self.snapshot_id = ""
        self.framework: dict[str, Any] = {}
        self.records: list[dict[str, Any]] = []
        self.audit: list[dict[str, Any]] = []
        self.cache: dict[str, Any] = {}
        self.preparation: dict[str, Any] = {}

    async def initialize(self) -> None:
        response = await self.client.get("/api/health")
        response.raise_for_status()
        self.identity = response.json()["sourceSnapshot"]
        self.snapshot_id = self.identity["namespace"] + "/" + self.identity["version"]
        expected = os.environ.get("HARNESS_LC_SNAPSHOT")
        if expected and expected != self.snapshot_id:
            raise KnowledgeError("本地知识版本与服务固定配置不符")
        directory = await self.fetch("frameworks/directory")
        matches = [
            n
            for n in directory["nodes"]
            if n["display"]["value"] == "Common Core State Standards for Math"
            and n["academicSubject"]["value"] == "Mathematics"
        ]
        if len(matches) != 1:
            raise KnowledgeError("无法唯一解析 CCSS Mathematics 框架")
        self.framework = matches[0]["ref"]

    async def fetch(self, path: str, **params: Any) -> dict[str, Any]:
        params = {k: v for k, v in params.items() if v is not None}
        key = fingerprint([path, params])
        if key in self.cache:
            return self.cache[key]
        response = await self.client.get(
            "/api/browse/" + path, params={**params, "sourceSnapshot": self.snapshot_id}
        )
        response.raise_for_status()
        data = response.json()
        if data.get("sourceSnapshot") != self.identity:
            raise KnowledgeError("知识查询期间源版本改变")
        self.audit.append(
            {
                "path": path,
                "params": params,
                "response_fingerprint": fingerprint(data),
                "has_more": data.get("hasMore"),
                "next_cursor": data.get("nextCursor"),
            }
        )
        self.cache[key] = data
        return data

    async def pages(
        self, path: str, collection: str, *, expected: dict[str, Any] | None = None, **params: Any
    ) -> list[dict[str, Any]]:
        cursor = None
        seen: set[str] = set()
        results: list[dict[str, Any]] = []
        # 本次查询的防失控边界；越界显式失败，不把截断当完整结果。
        for _ in range(100):
            page = await self.fetch(path, limit=self.page_size, cursor=cursor, **params)
            if expected and any(page.get(key) != value for key, value in expected.items()):
                raise KnowledgeError("知识分页的框架、年级或父项不符")
            if collection == "edges" and any(
                page.get("applied" + key[0].upper() + key[1:]) != value
                for key, value in params.items()
            ):
                raise KnowledgeError("知识服务未执行指定关系过滤")
            results.extend(page[collection])
            if not page["hasMore"]:
                if page.get("nextCursor"):
                    raise KnowledgeError("终页仍有游标", "partial")
                return results
            cursor = page.get("nextCursor")
            if not cursor or cursor in seen:
                raise KnowledgeError("知识查询分页不完整或重复", "partial")
            seen.add(cursor)
        raise KnowledgeError("知识分页超过上限，未取得完整结果", "partial")

    async def grade_scope(self, grade: int) -> dict[str, Any]:
        """遍历固定框架的年级投影；动态核对页、子项数与总数，保留原层级。"""
        base = f"frameworks/{quote(self.framework['identifier'], safe='')}/grade-levels"
        directory = await self.fetch(base)
        choices = [p for p in directory["projections"] if p["ref"]["grade"] == str(grade)]
        if directory["framework"] != self.framework or len(choices) != 1:
            raise KnowledgeError("无法取得唯一完整的 CCSS 年级投影")
        projection = choices[0]
        if projection["itemCount"] <= 0:
            raise KnowledgeError("年级投影为空，不能生成全年覆盖声明", "empty")
        nodes: dict[str, dict[str, Any]] = {}
        queue: list[str | None] = [None]
        roots = []
        for parent in queue:
            page = await self.pages(
                f"{base}/{grade}/items",
                "nodes",
                parent=parent,
                expected={
                    "framework": self.framework,
                    "projection": projection["ref"],
                    "parent": nodes[parent]["detail"]["ref"] if parent else None,
                },
            )
            ids = [n["ref"]["identifier"] for n in page]
            if len(set(ids)) != len(ids):
                raise KnowledgeError("年级层级分页存在重复身份")
            if parent is None:
                roots = ids
                if not roots:
                    raise KnowledgeError("年级投影根为空，未取得全年范围", "empty")
            elif len(ids) != nodes[parent]["projection_child_count"]:
                raise KnowledgeError("年级投影缺少子项，不能把部分页当完整目标", "partial")
            for n in page:
                identifier = n["ref"]["identifier"]
                if identifier not in nodes:
                    if not await self.in_framework(n["ref"]):
                        raise KnowledgeError("年级投影包含非 CCSS 条目")
                    nodes[identifier] = {
                        "detail": await self.detail(n["ref"]),
                        "parent_ids": [],
                        "projection_child_count": n["projectionChildCount"],
                        "outside_child_count": n["outsideChildCount"],
                    }
                    queue.append(identifier)
                if parent is not None:
                    nodes[identifier]["parent_ids"].append(parent)
            if len(nodes) > projection["itemCount"]:
                raise KnowledgeError("年级投影遍历超出源声明范围")
        if len(nodes) != projection["itemCount"]:
            raise KnowledgeError("年级投影总范围与实际遍历不符，可能缺页或缺分支", "partial")
        try:
            TopologicalSorter({key: n["parent_ids"] for key, n in nodes.items()}).prepare()
        except CycleError:
            raise KnowledgeError("标准层级存在循环") from None
        targets: list[str] = []
        parents: list[str] = []
        practices: list[dict[str, Any]] = []
        for n in nodes.values():
            code = n["detail"]["source_fields"].get("statementCode") or ""
            if re.fullmatch(rf"{grade}\.[A-Z]+\.[A-Z]\.\d+(?:\.[a-z])?", code):
                (parents if n["projection_child_count"] else targets).append(code)
            elif re.fullmatch(rf"(?:{grade}\.)?MP[1-8]", code):
                practices.append(n["detail"])
        if not targets or len(targets + parents) != len(set(targets + parents)):
            raise KnowledgeError("全年内容目标为空或标准代码身份重复")
        return {
            "complete": True,
            "result_status": "complete",
            "projection": projection,
            "framework": self.framework,
            "source_snapshot": self.identity,
            "root_ids": roots,
            "nodes": list(nodes.values()),
            "target_codes": sorted(targets),
            "parent_codes": sorted(parents),
            "practices": practices,
            "scope_note": "按年级元数据投影保留全部层级；非本年级子项以 outside_child_count 记录排除。父标准与子项不重复计数；数学实践另行承担。",
        }

    async def prepare_year(self, grade: int) -> dict[str, Any]:
        self.preparation = {"grade": grade, "complete": False}
        try:
            await self.initialize()
            scope = await self.grade_scope(grade)
            practice_codes = {p["source_fields"]["statementCode"] for p in scope["practices"]}
            if not {f"MP{i}" for i in range(1, 9)} <= practice_codes:
                raise KnowledgeError("数学实践范围不完整", "partial")
        except (KnowledgeError, httpx.HTTPError) as exc:
            self.preparation.update(
                result_status=exc.result_status if isinstance(exc, KnowledgeError) else "error",
                source_snapshot=self.identity,
                framework=self.framework,
                error={
                    "type": type(exc).__name__,
                    "message": str(exc)
                    if isinstance(exc, KnowledgeError)
                    else "知识 HTTP 请求失败",
                    "http_status": exc.response.status_code
                    if isinstance(exc, httpx.HTTPStatusError)
                    else None,
                },
            )
            raise
        self.preparation.update(
            result_status="complete",
            complete=True,
            source_snapshot=self.identity,
            framework=self.framework,
        )
        return {
            "year_scope": scope,
            "scope": "完整年级内容及实践原文；组件与前后联系由设计 Agent 按问题继续查询",
        }

    async def in_framework(self, ref: dict[str, Any]) -> bool:
        if (
            ref.get("sourceSnapshotId") != self.snapshot_id
            or ref.get("kind") != "StandardsFrameworkItem"
        ):
            return False
        paths = await self.fetch(
            f"nodes/StandardsFrameworkItem/{quote(ref['identifier'], safe='')}/root-paths"
        )
        if not paths["isComplete"]:
            raise KnowledgeError("框架归属路径不完整")
        return paths.get("structureRelation") == "hasChild" and any(
            path["steps"] and path["steps"][0]["ref"] == self.framework for path in paths["paths"]
        )

    async def detail(self, ref: dict[str, Any]) -> dict[str, Any]:
        if ref["sourceSnapshotId"] != self.snapshot_id or ref["kind"] not in {
            "LearningComponent",
            "StandardsFrameworkItem",
        }:
            raise KnowledgeError("节点不在本次知识范围内")
        data = await self.fetch(f"nodes/{ref['kind']}/{quote(ref['identifier'], safe='')}")
        if data["ref"] != ref:
            raise KnowledgeError("知识节点身份不符")
        # 只投影源字段；不把目录、课程对齐、UI groups 等混合来源交给模型。
        allowed_fields = {
            "academicSubject",
            "author",
            "caseIdentifierURI",
            "caseIdentifierUUID",
            "dateModified",
            "dateCreated",
            "description",
            "inLanguage",
            "notes",
            "statementCode",
            "alternateStatementCode",
            "statementType",
            "identifier",
            "name",
        }
        result = {
            "ref": ref,
            "source_fields": {
                f["name"]: f["value"] for f in data["fields"] if f["name"] in allowed_fields
            },
            "publisher": data["publisher"]["value"],
            "attribution": data["attribution"],
            "source_snapshot": self.identity,
        }
        require_original(result)
        if not result["source_fields"].get("description"):
            raise KnowledgeError("知识节点缺少实际正文")
        return result

    async def resolve(self, code: str) -> dict[str, Any]:
        if not re.fullmatch(r"[A-Za-z0-9.-]{2,40}", code):
            raise KnowledgeError("请使用标准代码")
        matches = {}
        for node in await self.pages("search", "nodes", q=code, kind="StandardsFrameworkItem"):
            hint = node.get("sourcePaths") or {}
            if hint.get("isComplete") and not any(
                p["steps"] and p["steps"][0]["ref"] == self.framework for p in hint.get("paths", [])
            ):
                continue
            if not await self.in_framework(node["ref"]):
                continue
            detail = await self.detail(node["ref"])
            fields = detail["source_fields"]
            if code in (fields.get("statementCode"), fields.get("alternateStatementCode")):
                matches[node["ref"]["identifier"]] = detail
        if len(matches) != 1:
            raise KnowledgeError(f"CCSS 目标 {code} 未取得唯一完整正文")
        return next(iter(matches.values()))

    async def lookup(self, code: str, operation: Operation) -> dict[str, Any]:
        standard = await self.resolve(code)
        result: dict[str, Any] = {
            "code": code,
            "operation": operation,
            "standard": standard,
            "framework": self.framework,
            "source_snapshot": self.identity,
            "complete_for_query": True,
            "records": [],
            "excluded": [],
        }
        if operation != "standard":
            relation = "supports" if operation == "components" else "buildsTowards"
            direction = "outgoing" if operation == "successors" else "incoming"
            kind = "LearningComponent" if operation == "components" else "StandardsFrameworkItem"
            ref = standard["ref"]
            edges = await self.pages(
                f"nodes/StandardsFrameworkItem/{quote(ref['identifier'], safe='')}/relationships",
                "edges",
                type=relation,
                direction=direction,
                endpointKind=kind,
            )
            if len({e["identifier"] for e in edges}) != len(edges):
                raise KnowledgeError("关系分页存在重复身份")
            for edge in edges:
                other = edge["endpoint"]["ref"]
                if (
                    edge["direction"] != direction
                    or edge["relationshipType"] != relation
                    or other["kind"] != kind
                ):
                    raise KnowledgeError("来源关系的方向或类型不符")
                if edge["provenance"] != "source_fact" or (
                    kind == "StandardsFrameworkItem" and not await self.in_framework(other)
                ):
                    result["excluded"].append(
                        {"id": edge["identifier"], "reason": "非源事实或非 CCSS 端点"}
                    )
                    continue
                record = {
                    "id": edge["identifier"],
                    "type": relation,
                    "source": other if direction == "incoming" else ref,
                    "target": ref if direction == "incoming" else other,
                    "direction": direction,
                    "provenance": edge["provenance"],
                    "publisher": edge["publisher"]["value"],
                    "attribution": edge["attribution"],
                    "qualifiers": edge["qualifiers"],
                    "upstream_identifier": edge["upstreamIdentifier"],
                    "endpoint": await self.detail(other),
                }
                try:
                    require_original(record)
                except ValueError:
                    result["excluded"].append({"id": edge["identifier"], "reason": "原创范围排除"})
                    continue
                result["records"].append(record)
        result["result_status"] = (
            "complete" if operation == "standard" or result["records"] else "empty"
        )
        if result["excluded"]:
            result["result_status"] = "filtered"
        self.records.append(result)
        return result

    async def prepare(self, targets: list[str]) -> dict[str, Any]:
        await self.initialize()
        goals = []
        operations: tuple[Operation, ...] = ("components", "prerequisites", "successors")
        for code in targets:
            goals.append({op: await self.lookup(code, op) for op in operations})
        practices = [await self.lookup(f"MP{i}", "standard") for i in range(1, 9)]
        return {
            "targets": goals,
            "practices": practices,
            "scope": "仅本次目标及其直接联系；不是全年覆盖",
        }
