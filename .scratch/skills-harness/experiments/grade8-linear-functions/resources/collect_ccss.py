#!/usr/bin/env python3
"""Read the fixed CCSS Grade 8 projection; write only this task's resources.

No credentials, model calls, curriculum endpoints, global search, or external writes.
Python standard library only. The API is authoritative for returned source fields.
"""
import collections
import datetime
import hashlib
import json
import pathlib
import re
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8000/api/browse/"
FRAMEWORK = "6becf2d7-2232-5ead-983f-9f0a4de24ab7"
SNAPSHOT = "lc/v1.11.0"
OUT = pathlib.Path(__file__).resolve().parent
CONTRACT = pathlib.Path("/Users/libo/Mathematics/k12-learning/apps/studio-server/contract/openapi.json")
RECEIPTS = []
IDENTITY = None


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fetch(path, **params):
    global IDENTITY
    params = {k: v for k, v in params.items() if v is not None}
    params["sourceSnapshot"] = SNAPSHOT
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with urllib.request.urlopen(url, timeout=30) as response:
        assert response.status == 200
        raw = response.read()
    result = json.loads(raw)
    identity = result["sourceSnapshot"]
    assert identity["namespace"] + "/" + identity["version"] == SNAPSHOT
    if IDENTITY is None:
        IDENTITY = identity
    assert identity == IDENTITY, "Snapshot changed during collection"
    if "sourceSnapshotId" in result:
        assert result["sourceSnapshotId"] == SNAPSHOT
    ref = result.get("ref")
    if ref:
        assert ref["sourceSnapshotId"] == SNAPSHOT
    framework = result.get("framework")
    if framework:
        assert framework["identifier"] == FRAMEWORK
        assert framework["sourceSnapshotId"] == SNAPSHOT
    receipt = {
        "id": "Q%03d" % (len(RECEIPTS) + 1), "retrievedAt": now,
        "url": url, "httpStatus": 200, "rawResponseSha256": sha(raw),
        "nodes": [n["ref"]["identifier"] for n in result.get("nodes", [])],
        "hasMore": result.get("hasMore"), "nextCursor": result.get("nextCursor"),
    }
    RECEIPTS.append(receipt)
    return result, receipt["id"]


def fields(detail):
    return {field["name"]: field["value"] for field in detail["fields"]}


def category(source):
    code = source.get("statementCode") or ""
    if re.fullmatch(r"MP[1-8]", code):
        return "mathematical_practice"
    if re.fullmatch(r"8\.MP[1-8]", code):
        return "grade_specific_practice_statement"
    if re.fullmatch(r"8\.[A-Z]+\.[A-Z]\.\d+", code):
        return "numbered_content_standard"
    if re.fullmatch(r"8\.[A-Z]+\.[A-Z]\.\d+\.[a-z]", code):
        return "content_subitem"
    return "hierarchy_or_context"


def write_json(name, value):
    data = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()
    (OUT / name).write_bytes(data)
    return sha(data)


framework_detail, framework_query = fetch("nodes/StandardsFramework/" + FRAMEWORK)
framework_fields = fields(framework_detail)
assert framework_fields["name"] == "Common Core State Standards for Math"
assert framework_fields["academicSubject"] == "Mathematics"
assert framework_fields["jurisdiction"] == "Multi-State"
grade_levels, grade_query = fetch("frameworks/" + FRAMEWORK + "/grade-levels")
grade_projection = next(p for p in grade_levels["projections"] if p["ref"]["grade"] == "8")
expected_count = grade_projection["itemCount"]

nodes = {}
parents = collections.defaultdict(list)
children = collections.defaultdict(list)
page_queries = collections.defaultdict(list)
queue = collections.deque([None])
visited = set()
while queue:
    parent = queue.popleft()
    assert parent not in visited
    visited.add(parent)
    cursor = None
    seen_cursors = set()
    while True:
        result, query = fetch("frameworks/" + FRAMEWORK + "/grade-levels/8/items",
                              parent=parent, limit=5, cursor=cursor)
        assert result["projection"] == grade_projection["ref"]
        assert (result["parent"]["identifier"] if result["parent"] else None) == parent
        page_queries[parent].append(query)
        for node in result["nodes"]:
            ref = node["ref"]
            assert ref["sourceSnapshotId"] == SNAPSHOT
            assert ref["kind"] == "StandardsFrameworkItem"
            identifier = ref["identifier"]
            assert identifier not in children[parent], "Repeated item across pages"
            children[parent].append(identifier)
            parents[identifier].append(parent)
            if identifier not in nodes:
                nodes[identifier] = node
                if node["projectionChildCount"]:
                    queue.append(identifier)
            else:
                assert nodes[identifier] == node
        if not result["hasMore"]:
            assert result["nextCursor"] is None
            break
        cursor = result["nextCursor"]
        assert cursor and cursor not in seen_cursors
        seen_cursors.add(cursor)
    if parent is not None:
        assert len(children[parent]) == nodes[parent]["projectionChildCount"]

assert len(nodes) == expected_count
records = []
for identifier, summary in nodes.items():
    detail, query = fetch("nodes/StandardsFrameworkItem/" + identifier)
    assert detail["ref"] == summary["ref"]
    assert not detail["sourceAnomalies"], "Review source anomaly before using this input"
    source = fields(detail)
    assert source["academicSubject"] == "Mathematics"
    assert source["jurisdiction"] == "Multi-State"
    assert "8" in detail["gradeLevels"]
    assert source["statementCode"] == summary["statementCode"]["value"]
    assert source["description"] == summary["description"]["value"]
    assert source["caseIdentifierURI"].endswith(source["caseIdentifierUUID"])
    if source.get("notes") is not None and source.get("notessha256"):
        assert sha(source["notes"].encode()) == source["notessha256"]
    records.append({
        "ref": detail["ref"], "frameworkIdentifier": FRAMEWORK,
        "classification": category(source), "classificationOrigin": "collector_interpretation",
        "sourceFields": source, "gradeLevels": detail["gradeLevels"],
        "publisher": detail["publisher"]["value"], "attribution": detail["attribution"],
        "gradeProjectionParentIdentifiers": parents[identifier],
        "gradeProjectionChildIdentifiers": children[identifier],
        "sourceDetailQuery": query,
    })

assert len({r["sourceFields"]["caseIdentifierUUID"] for r in records}) == len(records)
practice_roots = [r for r in records if r["sourceFields"]["description"] in {
    "Standards for Mathematical Practice", "Standards for Mathematical Practice: Grade 8"}]
assert len(practice_roots) == 2
practice_ids = {r["ref"]["identifier"] for r in practice_roots}
practice_ids.update(child for root in practice_roots for child in root["gradeProjectionChildIdentifiers"])
practices = [r for r in records if r["ref"]["identifier"] in practice_ids]
content = [r for r in records if r["ref"]["identifier"] not in practice_ids]
assert {r["sourceFields"]["statementCode"] for r in practices if r["classification"] == "mathematical_practice"} == {"MP" + str(i) for i in range(1, 9)}
assert all(r["sourceFields"].get("notes") for r in practices if r["classification"] == "mathematical_practice")
assert {r["sourceFields"]["statementCode"] for r in practices if r["classification"] == "grade_specific_practice_statement"} == {"8.MP" + str(i) for i in range(1, 9)}
assert all(r["sourceFields"]["notes"] is None for r in practices if r["classification"] == "grade_specific_practice_statement")
practice_by_code = {r["sourceFields"]["statementCode"]: r for r in practices if r["sourceFields"]["statementCode"]}
assert all(practice_by_code[f"MP{n}"]["sourceFields"]["description"] == practice_by_code[f"8.MP{n}"]["sourceFields"]["description"] for n in range(1, 9))
# Code inventory manually checked against the five official, non-IM domain pages
# on 2026-09-15. This validates scope, not exact text equality to those pages.
official_clusters = {"EE.A": range(1, 5), "EE.B": range(5, 7), "EE.C": range(7, 9),
                     "F.A": range(1, 4), "F.B": range(4, 6), "G.A": range(1, 6),
                     "G.B": range(6, 9), "G.C": range(9, 10), "NS.A": range(1, 3), "SP.A": range(1, 5)}
expected_codes = {f"8.{cluster}.{n}" for cluster, numbers in official_clusters.items() for n in numbers}
expected_subitems = {f"8.{stem}.{letter}" for stem, letters in {
    "EE.C.7": "ab", "EE.C.8": "abc", "G.A.1": "abc"}.items() for letter in letters}
assert {r["sourceFields"]["statementCode"] for r in content if r["classification"] == "numbered_content_standard"} == expected_codes
assert {r["sourceFields"]["statementCode"] for r in content if r["classification"] == "content_subitem"} == expected_subitems

common = {
    "artifactVersion": 1,
    "purpose": "Finite CCSS standards input for the Grade 8 original-design experiment; not a curriculum sequence or a local copy of the knowledge library.",
    "sourceSnapshotId": SNAPSHOT, "sourceSnapshot": IDENTITY,
    "retrievedAt": RECEIPTS[0]["retrievedAt"],
    "framework": {"ref": framework_detail["ref"], "sourceFields": {
        k: v for k, v in framework_fields.items() if k not in {"notes", "notessha256"}
    }, "publisher": framework_detail["publisher"]["value"],
        "attribution": framework_detail["attribution"], "sourceDetailQuery": framework_query},
    "grade": "8", "sourceLanguage": "en-US",
    "contentPolicy": "Only original source field values from this CCSS framework. No translations, browser groups, curriculum metadata, IM content, LC or progression records. Preserve description and notes together.",
    "hierarchyPolicy": "Parent and child identifiers record this API's Grade 8 projection, whose roots have null parent. They are navigation evidence, not standalone source relationship records or a curriculum arrangement.",
    "orderingPolicy": "API statement_code ordering is a platform projection. Record order and standard numbering do not prescribe teaching order.",
    "fieldPolicy": "sourceFields retains the exact field names returned by node details, including normalizedstatementtype and notessha256. Absent fields are not synthesized. classification is this collector's interpretation, not a source field.",
    "companionFiles": ["ccss-grade8.json", "ccss-practices.json"],
    "auditFile": "ccss-input-audit.md",
}
content_hash = write_json("ccss-grade8.json", {**common, "scope": "Grade 8 content standards and subitems, with their source hierarchy; practice records are in the companion file", "counts": dict(collections.Counter(r["classification"] for r in content)), "records": content})
practice_hash = write_json("ccss-practices.json", {**common, "scope": "Eight general mathematical practices with full notes, eight distinct Grade 8 practice statements, and their two source grouping nodes", "practiceIdentityPolicy": "MP1-MP8 and 8.MP1-8.MP8 are distinct source nodes with distinct canonical and CASE identities. Their same-number descriptions match; no alias or equivalence source relationship has been queried or invented. Use general MP description plus notes for the detailed requirements; grade-specific nodes have notes=null. These are two source representations, not a claim of sixteen independent practices.", "counts": dict(collections.Counter(r["classification"] for r in practices)), "records": practices})

counts = collections.Counter(r["classification"] for r in records)
types = collections.Counter(str(r["sourceFields"].get("statementType")) for r in records)
audit = ["# 八年级 CCSS 有限输入：采集与完整性核查", "",
         "本文件由 `collect_ccss.py` 的只读请求生成。采集不调用模型，不读取课程端点或 IM 内容。仅本目录写入结果。", "",
         "## 来源、版本与边界", "",
         "- 本地来源：" + BASE,
         "- 固定框架：`" + FRAMEWORK + "`，名称 `" + framework_fields["name"] + "`。",
         "- 框架 CASE UUID：`" + framework_fields["caseIdentifierUUID"] + "`；与 canonical identifier 分列。",
         "- 快照：`" + SNAPSHOT + "`；采集开始：`" + RECEIPTS[0]["retrievedAt"] + "`。",
         "- 本地契约：`" + str(CONTRACT) + "`；SHA-256：`" + sha(CONTRACT.read_bytes()) + "`。",
         "- [Learning Commons 官方标准 schema](https://docs.learningcommons.org/knowledge-graph/schema-reference/standards) 区分框架、条目、CASE 身份和层级；本地实际字段以返回值为准。",
         "- 原始 attribution 保留于每份 JSON 的框架及条目，未把本地转换写成出版者原文。", "",
         "```json", json.dumps(IDENTITY, indent=2), "```", "",
         "## 实际取得与复核", "",
         f"- Q002 年级目录中 Grade 8 的 itemCount = {expected_count}；按 parent 递归并耗尽每页 hasMore/nextCursor 后取得 {len(nodes)} 个唯一条目。",
         f"- 内容文件 {len(content)} 个条目；实践文件 {len(practices)} 个条目。两文件不重叠，总和 {len(records)}。",
         "- 分类（采集器判别，原 statementType 保留）：`" + json.dumps(dict(counts), ensure_ascii=False) + "`。",
         "- 实际 statementType 分布：`" + json.dumps(dict(types), ensure_ascii=False) + "`。",
         "- 每个非叶节点取得的 child 数与 projectionChildCount 相等；同一 parent 的分页未出现重复条目；所有分页终止于 hasMore=false、nextCursor=null。",
         "- 所有条目详情均为 StandardsFrameworkItem，学科 Mathematics、辖区 Multi-State、gradeLevels 包含 8；查询始终固定同一框架和完整 sourceSnapshot。",
         "- 每个条目的 canonical identifier 与 CASE UUID 独立保存；CASE UUID 唯一且与 CASE URI 后缀相符。未调用 CASE 远程服务验证其当前内容。",
         "- 所有有 notes 哈希的条目按 UTF-8 实际内容验证 notessha256；八项 MP 的详细 notes 均非空。",
         "- MP1–MP8 在本地同一框架内齐全，description 是简短标准句，notes 是详细实践要求，两者都进入输入。另有 8.MP1–8.MP8 年级内条目，notes 均为 null。两套节点的 canonical / CASE 身份不同，逐一保留，不按标题合并或计作 16 项独立实践；未查询或编造 alias / equivalence 关系。",
         "- 19 个层级分组中，内容文件含内容总组、年级组、5 个 Domain 和 10 个 Cluster（17 个），实践文件含 2 个实践分组；分组与编号标准、字母子条目分别保存，不把标准顺序当课程顺序。",
         "- 71 个条目详情的 sourceAnomalies 全部为空；这仅表示来源没有登记异常。", "",
         "### 独立官方范围核对", "",
         "2026-09-15 通过网页读取核对以下官方、非 IM 页面所列代码集合；与本地 28 个编号标准及 8 个子条目严格相等。网页核查不替换本地来源正文，也未做全文逐字符一致性声明。", "",
         "| 官方来源 | 编号标准数 | 字母子条目数 |",
         "| --- | ---: | ---: |",
         "| [8.NS](https://www.thecorestandards.org/Math/Content/8/NS/) | 2 | 0 |",
         "| [8.EE](https://www.thecorestandards.org/Math/Content/8/EE/) | 8 | 5 |",
         "| [8.F](https://www.thecorestandards.org/Math/Content/8/F/) | 5 | 0 |",
         "| [8.G](https://www.thecorestandards.org/Math/Content/8/G/) | 9 | 3 |",
         "| [8.SP](https://www.thecorestandards.org/Math/Content/8/SP/) | 4 | 0 |", "",
         "子条目：`" + "`, `".join(sorted(expected_subitems)) + "`。",
         "8.F.A.1 的 notes 保留函数记号不作八年级要求的说明；本地用词为 in Grade 8，官方网页为 for Grade 8。保留来源实际措辞，没有静默改写。",
         "上述官方网页读取来自本次 web 工具结果；未保存网页全文或声称有网页 body 哈希。直接 urllib 请求 8.F 页返回 403，该失败未作为完整性证据。", "",
         "### 实际字段与变换", "",
         "条目 sourceFields 的实际字段为：`" + "`, `".join(sorted({k for r in records for k in r["sourceFields"]})) + "`。",
         "返回体外层的 ref、sourceSnapshot、gradeLevels、publisher.value、attribution 随内容保留；fields 数组按原 name 映射到 sourceFields，只取 value，所有 null 原样保留。node details 与目录原文一致性已验证。",
         "最新版官方 schema 的 normalizedStatementType 在本地为 normalizedstatementtype；本地节点 fields 不含 isCurrent、license、provider、dateCreated，不能把缺列解释为上游无该概念或补造字段值。许可依据是实际返回的 attribution。dateModified 只代表条目字段，本次运行版本仍以完整 sourceSnapshot 固定。",
         "框架的 notes / notessha256 未装入输入：该段混有非本次标准范围的框架参考说明；条目 notes 全部保留。所有正文保持来源英文，未将机器翻译投影当出版者原文。", "",
         "## 缺口与适用范围", "",
         "- 完整性结论针对本次固定 CCSS 框架的 Grade 8 投影及其所有节点详情，不声称完成全库质量审核。",
         "- 未把学习组件、进阶、其它年级标准、学生证据、学校条件或教学规则装入这两份标准快照；它们是否另行需要由本次任务决定。",
         "- 本地节点详情没有返回的字段不会根据最新版官方 schema 补造；本地值与 CASE 远端现值是否一致尚未请求验证。",
         "- 本地 Grade 8 年级分组的 notes=null，没有取得独立年级导言／重点领域的正文；这不影响上表的标准及子条目全集计数，也不声称输入已包含官方文档所有导言。",
         "- UI 中文 projection、display、groups、课程 metadata 不进入输入；查询收据只证明本次所取来源和分页结果。", "",
         "## 文件指纹", "",
         "| 文件 | SHA-256 |", "| --- | --- |",
         "| ccss-grade8.json | `" + content_hash + "` |",
         "| ccss-practices.json | `" + practice_hash + "` |", "",
         "## 查询收据", "",
         "所有请求均为 GET / HTTP 200，所有响应的完整 sourceSnapshot 与上文完全相同。原响应 hash 基于 HTTP body 字节；仅下列安全摘要留存，不保留 UI 响应体。", "",
         "| ID | 请求 | 时间 (UTC) | rows | hasMore | nextCursor | 原响应 SHA-256 |",
         "| --- | --- | --- | ---: | --- | --- | --- |"]
for r in RECEIPTS:
    audit.append("| " + r["id"] + " | `" + r["url"] + "` | " + r["retrievedAt"] + " | " + str(len(r["nodes"])) + " | " + str(r["hasMore"]) + " | `" + str(r["nextCursor"]) + "` | `" + r["rawResponseSha256"] + "` |")
audit.extend(["", "## 逐父节点分页闭合", "", "`null` 是年级投影根；不是新建的知识实体。", "", "| parent identifier | queries | returned child identifiers |", "| --- | --- | --- |"])
for parent, queries in page_queries.items():
    audit.append("| `" + str(parent) + "` | " + ", ".join(queries) + " | " + ", ".join("`" + x + "`" for x in children[parent]) + " |")
(OUT / "ccss-input-audit.md").write_text("\n".join(audit) + "\n")
print(json.dumps({"total": len(records), "content": len(content), "practice": len(practices),
                  "classifications": counts, "sourceTypes": types, "queryCount": len(RECEIPTS),
                  "non_numbered": [(r["sourceFields"].get("statementCode"), r["sourceFields"].get("statementType"), r["sourceFields"].get("description")) for r in content if r["classification"] == "hierarchy_or_context"],
                  "contentCodes": [r["sourceFields"].get("statementCode") for r in content if r["classification"] != "hierarchy_or_context"],
                  "sourceFields": sorted({k for r in records for k in r["sourceFields"]})}, ensure_ascii=False, indent=2))
