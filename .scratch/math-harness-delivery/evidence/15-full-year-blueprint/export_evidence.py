"""从本轮原生记录导出可复核证据；不复制原始消息、签名或凭据。"""

import hashlib
import json
import shutil
from pathlib import Path

from teaching_harness.contracts import fingerprint

TARGET = Path(__file__).resolve().parent
ROOT = TARGET.parents[3]
WORK = ROOT / "work/year-live"


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def export(label, result_name, trace_name):
    result_path = WORK / result_name
    if not result_path.exists():
        return None
    result = json.loads(result_path.read_text())
    source = WORK / "tasks" / result["task_id"]
    target = TARGET / label
    target.mkdir(exist_ok=True)
    for name in (
        "content/curriculum.json",
        "output/curriculum.html",
        "output/render.json",
        "checks.json",
        "knowledge.json",
    ):
        dest = target / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, dest)
    for name in result.get("assets", {}):
        for asset in (name, name.removesuffix(".svg") + ".json"):
            dest = target / asset
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / asset, dest)
    write(target / "request.json", result["request"])
    context = json.loads((source / "context.json").read_text())
    context.pop("identity", None)
    write(target / "context.json", context)
    execution = json.loads((source / "execution.json").read_text())
    write(
        target / "execution-summary.json", {k: v for k, v in execution.items() if k != "operations"}
    )
    messages, calls = {}, {}

    def visit(value, phase):
        if isinstance(value, dict):
            usage = value.get("usage_metadata")
            if usage and value.get("id"):
                prior = messages.get(value["id"], {}).get("usage", {}).get("total_tokens", 0)
                # 同一完整消息会出现在多种原生事件中；不能对事件或增量块直接求和。
                if usage.get("total_tokens", 0) > prior:
                    messages[value["id"]] = {"phase": phase, "usage": usage}
            tool_calls = value.get("tool_calls", [])
            for call in tool_calls if isinstance(tool_calls, list) else []:
                if (
                    isinstance(call, dict)
                    and isinstance(call.get("args"), dict)
                    and call.get("name")
                ):
                    calls[fingerprint([call["name"], call["args"]])] = call
            for child in value.values():
                visit(child, phase)
        elif isinstance(value, list):
            for child in value:
                visit(child, phase)

    trace = WORK / trace_name
    for line in trace.open():
        event = json.loads(line)
        namespace = event.get("event", "")
        phase = (
            "reviewer"
            if "reviewer:" in namespace
            else "author"
            if "author:" in namespace
            else "outer"
        )
        visit(event, phase)
    model_calls = []
    for message in messages.values():
        u = message["usage"]
        model_calls.append(
            {
                "phase": message["phase"],
                **{k: u[k] for k in ("input_tokens", "output_tokens", "total_tokens")},
                "cache_read_tokens": u.get("input_token_details", {}).get("cache_read", 0),
                "reasoning_tokens": u.get("output_token_details", {}).get("reasoning", 0),
            }
        )
    usage = execution["usage"]
    for key in ("input_tokens", "output_tokens", "total_tokens"):
        assert sum(c[key] for c in model_calls) == usage[key], (label, key)
    assert len(model_calls) == usage["model_calls"]
    transcript = []
    for event in execution["events"]:
        if event["kind"] != "tool_started":
            continue
        op = execution["operations"][event["operation_id"]]
        call = calls.get(op["signature"])
        assert call is not None, event["operation_id"]
        args = call["args"]
        if call["name"].startswith("save_") and "content" in args:
            name = f"drafts/{len(transcript) + 1:03d}-request.json"
            write(target / name, args["content"])
            args = {
                **args,
                "content": {"saved_request": name, "fingerprint": fingerprint(args["content"])},
            }
        transcript.append(
            {
                "order": len(transcript) + 1,
                "stage": event["stage"],
                "round": event["round"],
                "operation_id": event["operation_id"],
                "name": call["name"],
                "arguments": args,
                "result": op.get("result"),
                "status": op["status"],
            }
        )
    assert len(transcript) == usage["tool_calls"]
    write(target / "tool-execution.json", transcript)
    record = {
        "label": label,
        "task_id": result["task_id"],
        "fingerprint": result["fingerprint"],
        **usage,
        "cache_read_tokens": sum(c["cache_read_tokens"] for c in model_calls),
        "reasoning_tokens": sum(c["reasoning_tokens"] for c in model_calls),
        "trace": str(trace.relative_to(ROOT)),
        "trace_sha256": hashlib.sha256(trace.read_bytes()).hexdigest(),
        "calls": model_calls,
    }
    write(target / "usage-audit.json", record)
    return record


records = [
    r
    for args in [
        ("initial", "result.json", "trace.jsonl"),
        ("revision", "revision-result.json", "revision-trace.jsonl"),
        ("final", "final-result.json", "final-trace.jsonl"),
    ]
    if (r := export(*args)) is not None
]
write(
    TARGET / "usage-audit.json",
    {
        "说明": "完整 AIMessage 去重后的供应商实际用量，与执行计量逐项一致。cache_read 已包含在 input，reasoning 已包含在 output；费用未对账。修订是携带旧稿的新任务，不是检查点续作。",
        "runs": records,
        "totals": {
            key: sum(r[key] for r in records)
            for key in (
                "model_calls",
                "tool_calls",
                "input_tokens",
                "output_tokens",
                "total_tokens",
                "cache_read_tokens",
                "reasoning_tokens",
            )
        },
    },
)
print(
    json.dumps(
        {
            r["label"]: {
                k: r[k] for k in ("model_calls", "tool_calls", "total_tokens", "cache_read_tokens")
            }
            for r in records
        },
        ensure_ascii=False,
    )
)
