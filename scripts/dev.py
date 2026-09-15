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
# 当前切片记录本地执行证据；云端内容发送由观察接入票单独验收。
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGGRAPH_CLI_NO_ANALYTICS"] = "1"
os.chdir(root)
os.execv(str(root / ".venv/bin/langgraph"), ["langgraph", "dev", "--no-browser", *sys.argv[1:]])
