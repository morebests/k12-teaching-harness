"""服务外消费者：提交、原生进度流、重送与结果查询。"""

import argparse
import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from teaching_harness.client import HarnessClient
from teaching_harness.contracts import TaskRequest


async def main() -> None:
    parser = argparse.ArgumentParser(description="通过原生服务生成有限课段")
    parser.add_argument("--url", default="http://127.0.0.1:2024")
    parser.add_argument("--event", required=True)
    parser.add_argument("--query", help="仅查询已有 task_id，不发起生成")
    parser.add_argument("--output", default="work/last-result.json")
    args = parser.parse_args()
    load_dotenv(".env.local")
    identity, token = next(iter(json.loads(os.environ["HARNESS_AUTH_TOKENS"]).items()))
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
                "total_tokens": 1800000,
                "seconds": 1200,
            },
        }
    )
    async with HarnessClient(args.url, identity, token) as client:
        if args.query:
            result = await client.query(args.query)
        else:
            receipt = await client.submit(request)
            print(receipt.model_dump_json(), flush=True)
            assert await client.submit(request) == receipt
            async for chunk in client.native.runs.join_stream(
                receipt.task_id, receipt.run_id, stream_mode="custom"
            ):
                if chunk.event == "custom":
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
