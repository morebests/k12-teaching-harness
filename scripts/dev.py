"""加载本机配置后启动原生 Agent Server dev。"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

root = Path(__file__).resolve().parents[1]
load_dotenv(root / ".env.local")
load_dotenv(root / ".env")
if not os.environ.get("HARNESS_AUTH_TOKENS"):
    raise SystemExit("请按 .env.example 在 .env.local 配置可信调用凭据")
# 开发默认提供诊断能力；实际读取仍需配置维护者身份和原有任务权限。
os.environ.setdefault("HARNESS_DIAGNOSTICS", "true")
# SDK 与 Agent Server 对别名的优先级不同；以新版开关为准统一，保证显式关闭生效。
tracing_keys = (
    "LANGSMITH_TRACING",
    "LANGSMITH_TRACING_V2",
    "LANGCHAIN_TRACING_V2",
    "LANGCHAIN_TRACING",
)
tracing = next((os.environ[key] for key in tracing_keys if key in os.environ), "false")
for key in tracing_keys:
    os.environ[key] = tracing
os.environ["LANGGRAPH_CLI_NO_ANALYTICS"] = "1"
os.chdir(root)
os.execv(str(root / ".venv/bin/langgraph"), ["langgraph", "dev", "--no-browser", *sys.argv[1:]])
