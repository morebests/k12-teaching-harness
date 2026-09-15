"""Throwaway, two-call Gemini tool-round-trip probe. No curriculum generation."""
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from dotenv import dotenv_values
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, messages_to_dict
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

ROOT = Path(__file__).resolve().parent
MODEL = "gemini-3.8-flash"


@tool
def read_standard(code: str) -> dict:
    """Read an exact CCSS Grade 8 standard code from the fixed local input snapshot."""
    requested_code = code
    code = code.removeprefix("CCSS.Math.Content.")
    data = json.loads((ROOT / "resources/ccss-grade8.json").read_text())
    for record in data["records"]:
        fields = record["sourceFields"]
        if fields["statementCode"] == code:
            return {"ref": record["ref"], "code": code, "requested_code": requested_code,
                    "text": fields["description"], "notes": fields["notes"]}
    return {"error": "Exact code not present"}


def main():
    key = dotenv_values(ROOT.parents[3] / ".env").get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY is missing; no key value printed.")
    run = ROOT / "runs" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-connectivity")
    run.mkdir(parents=True, exist_ok=False)
    result = {"model_requested": MODEL, "started_at": datetime.now(timezone.utc).isoformat(),
              "purpose": "forced tool call and tool result continuation; not a teaching quality test",
              "tracing": "local only", "model_calls": 0, "usage": []}
    start = time.monotonic()
    messages = [SystemMessage(content="Test the provided data tool. Do not design curriculum."),
                HumanMessage(content="Read CCSS 8.F.B.4 using read_standard, then state its code and first sentence exactly.")]
    try:
        model = ChatGoogleGenerativeAI(model=MODEL, api_key=key, vertexai=False,
                                      temperature=1.0, thinking_level="low",
                                      max_tokens=1024, max_retries=0, timeout=90)
        result["model_calls"] += 1
        response = model.bind_tools([read_standard], tool_choice="read_standard").invoke(messages)
        messages.append(response)
        result["usage"].append(response.usage_metadata)
        result["first_metadata"] = response.response_metadata
        if len(response.tool_calls) != 1:
            raise ValueError("Expected one tool call")
        call = response.tool_calls[0]
        if (call["name"] != "read_standard" or set(call["args"]) != {"code"}
                or call["args"]["code"].removeprefix("CCSS.Math.Content.") != "8.F.B.4"):
            raise ValueError("Unexpected tool request")
        output = read_standard.invoke(call["args"])
        messages.append(ToolMessage(content=json.dumps(output), tool_call_id=call["id"], name=call["name"]))
        result["model_calls"] += 1
        answer = model.bind_tools([read_standard]).invoke(messages)
        messages.append(answer)
        result["usage"].append(answer.usage_metadata)
        result["final_metadata"] = answer.response_metadata
        result["answer"] = answer.content
        result["status"] = "tool_round_trip_received" if not answer.tool_calls else "unexpected_followup_tool"
    except Exception as exc:
        result["status"] = "failed"
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc).replace(key, "[REDACTED]")[:2000]
    result["elapsed_seconds"] = round(time.monotonic() - start, 3)
    (run / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    (run / "messages.json").write_text(json.dumps(messages_to_dict(messages), ensure_ascii=False, indent=2))
    print(json.dumps({"run": str(run), **result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
