"""Finite, read-only knowledge adapter for the original-design experiment only."""
import hashlib
import json
import re
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8000/api/browse/"
FRAMEWORK = "6becf2d7-2232-5ead-983f-9f0a4de24ab7"
SNAPSHOT = "lc/v1.11.0"
BLOCKED_REFERENCE = re.compile(r"illustrative\s*mathematics|illustrativemathematics|im\.kendallhunt|im\.openupresources", re.I)


def fields(detail):
    return {f["name"]: f["value"] for f in detail["fields"]}


class Knowledge:
    def __init__(self, root, event):
        self.event = event
        self.records, self.codes, self.cache = {}, {}, {}
        for name in ("ccss-grade8.json", "ccss-practices.json"):
            data = json.loads((root / "resources" / name).read_text())
            self.identity = data["sourceSnapshot"]
            for record in data["records"]:
                assert record["frameworkIdentifier"] == FRAMEWORK
                ref = record["ref"]
                assert ref["sourceSnapshotId"] == SNAPSHOT
                self.records[ref["identifier"]] = record
                for key in ("statementCode", "alternateStatementCode"):
                    code = record["sourceFields"].get(key)
                    if code:
                        self.codes.setdefault(code, set()).add(ref["identifier"])
        self.ccss_ids = set(self.records)

    def fetch(self, path, **params):
        params = {k: v for k, v in params.items() if v is not None}
        url = BASE + path + "?" + urllib.parse.urlencode({**params, "sourceSnapshot": SNAPSHOT})
        if url in self.cache:
            self.event("knowledge_cache_hit", url=url)
            return self.cache[url]
        with urllib.request.urlopen(url, timeout=20) as response:
            raw = response.read()
        data = json.loads(raw)
        if data.get("sourceSnapshot") != self.identity:
            raise ValueError("Knowledge snapshot identity mismatch")
        self.event("knowledge_http", url=url, status=200,
                   response_sha256=hashlib.sha256(raw).hexdigest())
        self.cache[url] = data
        return data

    def pages(self, path, collection, **params):
        cursor, seen, results = None, set(), []
        for _ in range(20):
            page = self.fetch(path, limit=100, cursor=cursor, **params)
            if collection == "edges":
                if (page["appliedType"] != params["type"] or page["appliedDirection"] != params["direction"]
                        or page["appliedEndpointKind"] != params["endpointKind"]):
                    raise ValueError("Relationship query scope mismatch")
            results.extend(page[collection])
            if not page["hasMore"]:
                if page.get("nextCursor") is not None:
                    raise ValueError("Inconsistent terminal pagination")
                return results
            cursor = page.get("nextCursor")
            if not cursor or cursor in seen:
                raise ValueError("Incomplete or repeated pagination cursor")
            seen.add(cursor)
        raise ValueError("Query exceeds prototype page bound; result not complete")

    def root_matches(self, paths):
        expected = {"sourceSnapshotId": SNAPSHOT, "kind": "StandardsFramework", "identifier": FRAMEWORK}
        return paths.get("structureRelation") == "hasChild" and any(
            p["steps"] and p["steps"][0]["ref"] == expected for p in paths.get("paths", []))

    def verify_ccss(self, ref):
        if ref["kind"] != "StandardsFrameworkItem" or ref["sourceSnapshotId"] != SNAPSHOT:
            return False
        if ref["identifier"] in self.ccss_ids:
            return True
        paths = self.fetch(f"nodes/StandardsFrameworkItem/{ref['identifier']}/root-paths")
        if not paths["isComplete"]:
            raise ValueError("CCSS root-path verification incomplete")
        if not self.root_matches(paths):
            return False
        self.ccss_ids.add(ref["identifier"])
        return True

    def detail(self, ref):
        if ref["kind"] not in {"StandardsFrameworkItem", "LearningComponent"} or ref["sourceSnapshotId"] != SNAPSHOT:
            raise ValueError("Node outside approved knowledge kinds/snapshot")
        if ref["identifier"] in self.records:
            record = self.records[ref["identifier"]]
            result = {"ref": ref, "source_fields": record["sourceFields"], "publisher": record["publisher"],
                      "attribution": record["attribution"], "source_snapshot": self.identity}
        else:
            data = self.fetch(f"nodes/{ref['kind']}/{ref['identifier']}")
            if data["ref"] != ref:
                raise ValueError("Node identity mismatch")
            result = {"ref": ref, "source_fields": fields(data), "publisher": data["publisher"]["value"],
                      "attribution": data["attribution"], "source_snapshot": self.identity}
        expected = "Common Good Learning Tools" if ref["kind"] == "StandardsFrameworkItem" else "Achievement Network"
        if result["publisher"] != expected or result["source_fields"].get("author") != expected:
            raise ValueError("Node source not in this experiment's reviewed source allowlist")
        if BLOCKED_REFERENCE.search(json.dumps(result)):
            raise ValueError("Node contains a reference excluded from original input")
        return result

    def resolve(self, code):
        code = code.strip().removeprefix("CCSS.Math.Content.")
        if not re.fullmatch(r"[A-Za-z0-9.-]{2,40}", code):
            raise ValueError("Provide a standard code, not a free-text search")
        known = self.codes.get(code, set())
        if len(known) == 1:
            return self.detail({"sourceSnapshotId": SNAPSHOT, "kind": "StandardsFrameworkItem", "identifier": next(iter(known))})
        matches = {}
        for node in self.pages("search", "nodes", q=code, kind="StandardsFrameworkItem"):
            paths = node.get("sourcePaths") or {}
            if not self.root_matches(paths):
                continue
            ref = node["ref"]
            if not self.verify_ccss(ref):
                continue
            detail = self.detail(ref)
            f = detail["source_fields"]
            if code in (f.get("statementCode"), f.get("alternateStatementCode")):
                matches[ref["identifier"]] = detail
        if len(matches) != 1:
            raise ValueError(f"Expected one exact CCSS code match; found {len(matches)}")
        identifier, detail = next(iter(matches.items()))
        self.codes[code] = {identifier}
        return detail

    def lookup(self, code, kind):
        standard = self.resolve(code)
        if kind == "standard":
            return {"standard": standard}
        if kind not in {"components", "prerequisites", "successors"}:
            raise ValueError("Unknown knowledge request")
        direction = "outgoing" if kind == "successors" else "incoming"
        relation = "supports" if kind == "components" else "buildsTowards"
        endpoint_kind = "LearningComponent" if kind == "components" else "StandardsFrameworkItem"
        publisher = "Achievement Network" if kind == "components" else "Student Achievement Partners"
        ref = standard["ref"]
        edges = self.pages(f"nodes/StandardsFrameworkItem/{ref['identifier']}/relationships", "edges",
                           type=relation, direction=direction, endpointKind=endpoint_kind)
        if len({e["identifier"] for e in edges}) != len(edges):
            raise ValueError("Repeated relationship identity across pages")
        accepted, excluded = [], []
        for edge in edges:
            authors = [q["value"] for q in edge["qualifiers"] if q["name"] == "author"]
            other = edge["endpoint"]["ref"]
            if (edge["publisher"]["value"] != publisher or authors != [publisher]
                    or edge["provenance"] != "source_fact"):
                excluded.append({"edge": edge["identifier"], "reason": "unreviewed source"})
                continue
            if edge["direction"] != direction or edge["relationshipType"] != relation or other["kind"] != endpoint_kind:
                raise ValueError("Relationship shape mismatch")
            if endpoint_kind == "StandardsFrameworkItem" and not self.verify_ccss(other):
                excluded.append({"edge": edge["identifier"], "reason": "outside CCSS framework"})
                continue
            try:
                node = self.detail(other)
            except ValueError as exc:
                excluded.append({"edge": edge["identifier"], "reason": str(exc)})
                continue
            source, target = (other, ref) if direction == "incoming" else (ref, other)
            accepted.append({"edge_identifier": edge["identifier"], "relationship_type": relation,
                             "direction": direction, "source": source, "target": target,
                             "provenance": edge["provenance"], "publisher": publisher,
                             "attribution": edge["attribution"], "qualifiers": edge["qualifiers"],
                             "upstream_identifier": edge["upstreamIdentifier"],
                             "identifier_repaired": edge["identifierRepaired"], "endpoint": node})
        result = {"standard": standard, "request": kind, "complete_for_query": True,
                  "source_snapshot": self.identity, "source_filter": publisher,
                  "total_edges": len(edges), "records": accepted, "excluded": excluded,
                  "interpretation": "Source support links are not fixed curriculum order or learner mastery evidence."}
        self.event("knowledge_delivered", code=code, operation=kind, accepted=len(accepted), excluded=len(excluded),
                   payload_sha256=hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest())
        return result
