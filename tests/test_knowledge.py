"""知识消费边界：实际 HTTP 形状的分页、身份、方向与故障。"""

import httpx
import pytest

from teaching_harness.knowledge import Knowledge, KnowledgeError

SNAPSHOT = {
    "namespace": "test",
    "version": "1",
    "nodesSha256": "nodes",
    "relationshipsSha256": "edges",
}


def ref(identifier, kind="StandardsFrameworkItem"):
    return {"sourceSnapshotId": "test/1", "kind": kind, "identifier": identifier}


def transport(repeated_cursor=False, changed_version=False):
    def handle(request):
        path = request.url.path.removeprefix("/api/browse/")
        params = request.url.params
        body = {"sourceSnapshot": SNAPSHOT}
        if request.url.path == "/api/health":
            pass
        elif path == "frameworks/directory":
            body["nodes"] = [
                {
                    "display": {"value": "Common Core State Standards for Math"},
                    "academicSubject": {"value": "Mathematics"},
                    "ref": ref("ccss", "StandardsFramework"),
                }
            ]
        elif path == "search":
            body.update(nodes=[{"ref": ref("target")}], hasMore=False, nextCursor=None)
        elif path.endswith("root-paths"):
            body.update(
                isComplete=True,
                structureRelation="hasChild",
                paths=[{"steps": [{"ref": ref("ccss", "StandardsFramework")}]}],
            )
        elif path.endswith("relationships"):
            direction = params["direction"]
            kind = params["endpointKind"]
            last = bool(params.get("cursor"))
            body.update(
                appliedType=params["type"],
                appliedDirection=direction,
                appliedEndpointKind=kind,
                hasMore=not last or repeated_cursor,
                nextCursor="page2" if not last or repeated_cursor else None,
                edges=[
                    {
                        "identifier": "edge2" if last else "edge1",
                        "direction": direction,
                        "relationshipType": params["type"],
                        "provenance": "source_fact",
                        "endpoint": {"ref": ref("neighbor2" if last else "neighbor1", kind)},
                        "publisher": {"value": "测试来源"},
                        "attribution": "合成来源",
                        "qualifiers": [],
                        "upstreamIdentifier": None,
                    }
                ],
            )
        else:
            _, kind, identifier = path.split("/")
            body.update(
                ref=ref(identifier, kind),
                fields=[
                    {"name": "statementCode", "value": "8.F.B.4"},
                    {"name": "description", "value": "合成标准或组件正文"},
                    {"name": "caseIdentifierUUID", "value": "case-distinct-id"},
                ],
                publisher={"value": "测试来源"},
                attribution="合成来源",
            )
        if changed_version and path == "search":
            body["sourceSnapshot"] = {**SNAPSHOT, "version": "2"}
        return httpx.Response(200, json=body)

    return httpx.MockTransport(handle)


@pytest.mark.parametrize(
    "operation,source_kind",
    [
        ("components", "LearningComponent"),
        ("prerequisites", "StandardsFrameworkItem"),
        ("successors", "StandardsFrameworkItem"),
    ],
)
async def test_遍历所有分页并保留来源方向与两类身份(operation, source_kind):
    async with httpx.AsyncClient(base_url="http://knowledge", transport=transport()) as client:
        knowledge = Knowledge(client, page_size=1)
        await knowledge.initialize()
        result = await knowledge.lookup("8.F.B.4", operation)
        assert len(result["records"]) == 2
        assert result["standard"]["ref"]["identifier"] == "target"
        assert result["standard"]["source_fields"]["caseIdentifierUUID"] == "case-distinct-id"
        first = result["records"][0]
        if operation == "successors":
            assert first["source"] == ref("target") and first["target"] == ref("neighbor1")
        else:
            assert first["source"] == ref("neighbor1", source_kind) and first["target"] == ref(
                "target"
            )


@pytest.mark.parametrize("option", ["repeated_cursor", "changed_version"])
async def test_分页或版本异常不能冒充完整结果(option):
    async with httpx.AsyncClient(
        base_url="http://knowledge", transport=transport(**{option: True})
    ) as client:
        knowledge = Knowledge(client)
        await knowledge.initialize()
        with pytest.raises(KnowledgeError):
            await knowledge.lookup("8.F.B.4", "components")


def grade_transport(fault=None):
    base = transport()
    codes = {"root": "8.EE.C", "parent": "8.EE.C.7", "a": "8.EE.C.7.a", "b": "8.EE.C.7.b"}
    children = {None: ["root"], "root": ["parent"], "parent": ["a", "b"], "a": [], "b": []}

    def handle(request):
        path = request.url.path
        params = request.url.params
        body = {"sourceSnapshot": SNAPSHOT, "framework": ref("ccss", "StandardsFramework")}
        projection = {
            "sourceSnapshotId": "test/1",
            "projectionKind": "gradeLevelMetadata",
            "sourceField": "gradeLevel",
            "frameworkIdentifier": "ccss",
            "grade": "8",
        }
        if path.endswith("grade-levels"):
            body["projections"] = [{"ref": projection, "itemCount": 5 if fault == "missing" else 4}]
        elif path.endswith("/items"):
            parent = params.get("parent")
            ids = children[parent]
            second = params.get("cursor") == "second"
            if fault == "error" and parent == "parent":
                return httpx.Response(503)
            if fault == "empty" and parent is None:
                ids = []
            page = ids[1:] if second else ids[:1]
            body.update(
                projection=projection,
                parent=None if parent is None else ref(parent),
                nodes=[
                    {
                        "ref": ref(i),
                        "projectionChildCount": len(children[i]),
                        "outsideChildCount": 0,
                    }
                    for i in page
                ],
                hasMore=len(ids) > 1 and not second,
                nextCursor="second" if len(ids) > 1 and not second else None,
            )
            if fault == "cursor" and body["hasMore"]:
                body["nextCursor"] = None
        elif path.rsplit("/", 1)[-1] in codes:
            ident = path.rsplit("/", 1)[-1]
            body.update(
                ref=ref(ident),
                fields=[
                    {"name": "statementCode", "value": codes[ident]},
                    {"name": "description", "value": "合成层级正文"},
                ],
                publisher={"value": "测试来源"},
                attribution="合成来源",
            )
        else:
            return base.handle_request(request)
        return httpx.Response(200, json=body)

    return httpx.MockTransport(handle)


async def test_全年遍历含父标准与全部子项并以动态范围核对完整性():
    async with httpx.AsyncClient(base_url="http://knowledge", transport=grade_transport()) as c:
        k = Knowledge(c, page_size=1)
        await k.initialize()
        result = await k.grade_scope(8)
    assert result["complete"] is True
    assert result["target_codes"] == ["8.EE.C.7.a", "8.EE.C.7.b"]
    assert result["parent_codes"] == ["8.EE.C.7"]
    assert len(result["nodes"]) == 4
    assert result["nodes"][-1]["parent_ids"] == ["parent"]


@pytest.mark.parametrize("fault", ["missing", "cursor", "empty", "error"])
async def test_全年缺页空根与查询错误均不能声称完整(fault):
    async with httpx.AsyncClient(
        base_url="http://knowledge", transport=grade_transport(fault)
    ) as c:
        k = Knowledge(c, page_size=1)
        await k.initialize()
        with pytest.raises((KnowledgeError, httpx.HTTPStatusError)):
            await k.grade_scope(8)
