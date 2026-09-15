"""Reproduce narrow, local checks of the frozen 2026-09-15 experiment.

No model/network calls. These checks do not establish teaching quality.
"""
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
PARENT = RUNS / "20260915T023658Z-repair"
REVISION = RUNS / "20260915T024257Z-revision"
BLIND = RUNS / "20260915T024257Z-blind"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


index, mismatches = [], []
checked = 0
for path in sorted(RUNS.glob("*/state.json")):
    state = read(path)
    usage = state["usage"]
    index.append({
        "run": path.parent.name, "status": state["status"],
        "limits": state["limits"], "model_calls": state["model_calls"],
        "tool_calls": state["tool_calls"], "elapsed_seconds": state["elapsed_seconds"],
        "usage_summed_across_calls": {
            key: sum(item.get(key, 0) for item in usage)
            for key in ("input_tokens", "output_tokens", "total_tokens")
        },
        "cache_read_tokens": sum(item.get("input_token_details", {}).get("cache_read", 0) for item in usage),
        "actual_cost": "unknown", "artifact_count": len(state["artifacts"]),
    })
    for name, record in state["artifacts"].items():
        checked += 1
        if sha(path.parent / "artifacts" / name) != record["sha256"]:
            mismatches.append(f"{path.parent.name}/{name}")
(ROOT / "run-index.json").write_text(json.dumps(index, indent=2) + "\n")

blueprint = (REVISION / "artifacts/grade8_curriculum_blueprint.md").read_text()
skeleton = (REVISION / "artifacts/unit5_linear_functions_skeleton.md").read_text()
unit_rows = [line.split("|") for line in blueprint.splitlines() if re.match(r"\| \*\*Unit \d\*\*", line)]
periods = [int(row[4].replace("*", "").strip()) for row in unit_rows[:9]]
codes = set(re.findall(r"\b8\.(?:NS|EE|F|G|SP)\.[A-D]\.\d+(?:\.[a-d])?\b", blueprint))
original_codes = set(re.findall(r"\b8\.(?:NS|EE|F|G|SP)\.[A-D]\.\d+(?:\.[a-d])?\b", (PARENT / "artifacts/grade8_curriculum_blueprint.md").read_text()))
period_ids = lambda text: [int(n) for n in re.findall(r"^\| \*\*P(\d+)\*\*", text, re.M)]
changes = {}
for name in ["lesson6_7_8_student_materials.md", "lesson6_7_8_teacher_guides.md"]:
    old = (PARENT / "artifacts" / name).read_text().splitlines()
    new = (REVISION / "artifacts" / name).read_text().splitlines()
    changes[name] = {
        "parent_sha256": sha(PARENT / "artifacts" / name),
        "revision_sha256": sha(REVISION / "artifacts" / name),
        "changed_line_numbers": [i + 1 for i, pair in enumerate(zip(old, new)) if pair[0] != pair[1]],
        "same_line_count": len(old) == len(new),
    }

svg = ET.parse(PARENT / "artifacts/cfu8_snow_graph.svg").getroot()
ns = "{http://www.w3.org/2000/svg}"
horizontal = sorted({float(node.attrib["y1"]) for node in svg.iter(ns + "line")
                     if node.get("x1") == "80" and node.get("x2") == "600" and node.get("y1") == node.get("y2")})
points = [[(float(node.get("cx")) - 80) / 32, (420 - float(node.get("cy"))) / 9]
          for node in svg.iter(ns + "circle")]
messages = read(BLIND / "messages.json")
blocks = messages[1]["data"]["content"]
visible_text = "\n".join(block["text"] for block in blocks if block["type"] == "text")
calls = [call for message in read(REVISION / "messages.json")
         for call in message["data"].get("tool_calls", [])]

result = {
    "scope": "Frozen file integrity, code presence, pacing arithmetic, exact child differences and selected SVG geometry; not complete content acceptance",
    "artifact_records_checked": checked, "artifact_hash_mismatches": mismatches,
    "parent_status": read(PARENT / "state.json")["status"],
    "revision_status": read(REVISION / "state.json")["status"],
    "unit_periods": periods, "scheduled_regular_sum": sum(periods),
    "regular_contingency": 160 - sum(periods), "flex_periods_declared": 20,
    "target_unit": {"before": 18, "after": periods[4], "actual_percent_reduction": 100 * (18 - periods[4]) / 18},
    "blueprint_period_ids": period_ids(blueprint), "skeleton_period_ids": period_ids(skeleton),
    "numbered_and_subitem_code_presence_count": len(codes), "codes_removed": sorted(original_codes - codes),
    "expanded_material_changes": changes,
    "all_parent_svgs_unchanged": all(sha(path) == sha(REVISION / "artifacts" / path.name) for path in (PARENT / "artifacts").glob("*.svg")),
    "visual_read": {"image_blocks": sum(block["type"] == "image_url" for block in blocks),
                    "svg_source_in_initial_text": "<svg" in visible_text,
                    "teacher_file_in_initial_text": "lesson6_7_8_teacher_guides.md" in visible_text},
    "snow_graph_geometry": {"source_sha256": sha(PARENT / "artifacts/cfu8_snow_graph.svg"),
                            "horizontal_grid_pixel_steps": sorted(set(round(b - a, 6) for a, b in zip(horizontal, horizontal[1:]))),
                            "pixels_per_inch": 9, "marked_points": points,
                            "adjudication": "Grid increment is 2 inches, not 3. P1/P2 are grid intersections; top label 40 has a proportionally shorter interval after 36."},
    "revision_actual_render_tool_calls": sum(call["name"] == "check_rendering" for call in calls),
    "revision_external_render_errors": {row["source"]: row["math_errors"] for row in read(REVISION / "review/render-manifest.json")["records"]},
    "semantic_and_visual_review": "See quality-review.md; overlapping annotation and unsupported compression guarantees remain unresolved.",
}
(ROOT / "closeout-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(result, ensure_ascii=False, indent=2))
