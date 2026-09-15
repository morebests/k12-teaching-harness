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
