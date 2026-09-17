"""年级课程评价与检查校准的本地入口；说明见 23 证据目录的 README。"""

import sys

from teaching_harness.grade_evaluation.cli import main

# 长时间运行时进度逐行写出，重定向到文件也能及时看到。
sys.stdout.reconfigure(line_buffering=True)  # type: ignore[union-attr]
main()
