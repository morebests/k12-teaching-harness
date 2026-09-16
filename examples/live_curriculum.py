"""服务外消费者：提交、原生进度流、重送与结果查询。"""

import argparse
import asyncio
import json
import os
from contextlib import nullcontext
from pathlib import Path

from dotenv import load_dotenv

from teaching_harness.client import HarnessClient
from teaching_harness.contracts import TaskRequest, fingerprint


async def main() -> None:
    parser = argparse.ArgumentParser(description="通过原生服务生成课程方案")
    parser.add_argument("--url", default="http://127.0.0.1:2024")
    parser.add_argument("--event", required=True)
    parser.add_argument("--query", help="仅查询已有 task_id，不发起生成")
    parser.add_argument("--output", default="work/last-result.json")
    parser.add_argument("--source", help="调用方已规范化的实际 JSON 内容文件")
    parser.add_argument("--instruction", help="本次课程设计的具体要求")
    parser.add_argument("--identity", help="使用本地凭据配置中的指定身份")
    parser.add_argument("--request", help="完整任务 JSON；可用于全年蓝图，event 由 --event 指定")
    parser.add_argument(
        "--diagnostics", help="维护者：为新运行订阅详细原生流并保存到新的 JSONL 文件"
    )
    args = parser.parse_args()
    if args.query and args.diagnostics:
        parser.error("--diagnostics 用于新运行；已有运行请用原生 runs.join_stream 读取已保留的流")
    if args.diagnostics and Path(args.diagnostics).resolve() == Path(args.output).resolve():
        parser.error("诊断流与最终结果需要不同的输出文件")
    load_dotenv(".env.local")
    credentials = json.loads(os.environ["HARNESS_AUTH_TOKENS"])
    identity = args.identity or next(iter(credentials))
    token = credentials[identity]
    request = TaskRequest.model_validate(
        {
            "event_id": args.event,
            "target_codes": ["8.F.B.4"],
            "instruction": "设计一个八年级线性函数课段。完整承担 8.F.B.4：从文字、两组数值、表格和真实函数图构建线性模型并解释变化率及初始值；关键任务须有实际题目和解答。课段位置为临时设计，不是全年权威上层。",
            "school": {
                "source": {
                    "label": "已有离线实验的合成学校条件",
                    "version": "2026-09-15",
                    "origin": "synthetic",
                },
                "lesson_count": 3,
                "minutes_per_lesson": 50,
                "class_size": 28,
                "resources": ["纸笔", "直尺", "方格纸", "黑白打印", "教师投影", "普通计算器"],
                "learner_context": "假设有前序年级课程经历，无班级诊断或个人掌握证据。必需任务课内完成。",
            },
            "limits": {
                "model_calls": 40,
                "tool_calls": 100,
                "seconds": 1200,
            },
        }
    )
    if args.request:
        request = TaskRequest.model_validate(
            {**json.loads(Path(args.request).read_text()), "event_id": args.event}
        )
    if args.source:
        source = json.loads(Path(args.source).read_text())
        request = TaskRequest.model_validate(
            {
                **request.model_dump(),
                "external_content": [
                    {
                        "id": "caller-source",
                        "content": source,
                        "fingerprint": fingerprint(source),
                        "source": {
                            "label": Path(args.source).name,
                            "version": fingerprint(source),
                            "origin": "caller",
                        },
                    }
                ],
            }
        )
    if args.instruction:
        request = TaskRequest.model_validate(
            {**request.model_dump(), "instruction": args.instruction}
        )
    async with HarnessClient(args.url, identity, token) as client:
        if args.query:
            result = await client.query(args.query)
        else:
            trace_path = Path(args.diagnostics) if args.diagnostics else None
            if trace_path:
                trace_path.parent.mkdir(parents=True, exist_ok=True)
            # 诊断含实际模型／工具内容，文件仅当前用户可读写且不覆盖旧记录。
            with (
                os.fdopen(os.open(trace_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w")
                if trace_path
                else nullcontext()
            ) as trace:
                receipt = await client.submit(request, diagnostics=bool(trace_path))
                assert receipt.run_id is not None
                print(receipt.model_dump_json(), flush=True)
                assert await client.submit(request, diagnostics=bool(trace_path)) == receipt
                if trace:
                    trace.write(json.dumps({"receipt": receipt.model_dump()}) + "\n")
                async for chunk in client.native.runs.join_stream(
                    receipt.task_id,
                    receipt.run_id,
                    stream_mode=None if trace else "custom",
                    last_event_id="0-0" if trace else None,
                ):
                    if trace:
                        trace.write(
                            json.dumps(
                                {
                                    "event": chunk.event,
                                    "id": chunk.id,
                                    "data": chunk.data,
                                },
                                ensure_ascii=False,
                            )
                            + "\n"
                        )
                        trace.flush()
                    if chunk.event.split("|")[0] == "custom":
                        event = chunk.data
                        if event.get("type") == "draft":
                            print(
                                json.dumps(
                                    {
                                        "type": "draft",
                                        "checked": False,
                                        "title": event["content"]["title"],
                                    },
                                    ensure_ascii=False,
                                ),
                                flush=True,
                            )
                        else:
                            print(json.dumps(event, ensure_ascii=False), flush=True)
            result = await client.query(receipt.task_id)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(
            json.dumps(
                {"status": result["status"], "task_id": result["task_id"], "output": str(output)},
                ensure_ascii=False,
            ),
            flush=True,
        )


if __name__ == "__main__":
    asyncio.run(main())
