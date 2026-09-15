# 首票工具调用顺序与记录缺口复核

复核日期：2026-09-15。本次只分析已有代码和冻结证据，没有重跑 Gemini、改写原始记录或上传 LangSmith。框架取舍另见 [ReAct 与工作流边界复核](../../../skills-harness/assets/react-and-workflow-boundaries.md)。

## 可以回答到什么程度

可以从 E 的记录还原 23 次业务工具的事件顺序、16 次计算的输入输出、一次成功绘图的参数及结果、一次成功保存的内容指纹。**不能完整还原一次 `author.ainvoke` 或 `reviewer.ainvoke` 的所有模型消息、工具调用参数与返回内容。** 原记录没有 Agent 调用边界和 `tool_call_id`，读取结果与错误细节也有缺失。此前“完整执行事件”的表述仅能理解为已记录事件的完整文件，不能理解为完整调用 trace。

`create_agent(...)` 创建执行图；`agent.ainvoke(...)` 才是一次执行。一次执行可包含多次 Gemini 调用，不能把工厂调用、Agent 执行和模型调用混为同一个计数。

## 原始证据与方法

- 任务：`e0d8ee31-4157-560f-be9a-17c72eab31ab`。
- Agent Server run：`01a0a496-2876-7dd3-8d9d-3005dd245ea0`。
- 来源：[execution.json](e-completed/execution.json)、[acceptance.json](e-completed/acceptance.json)、[checks.json](e-completed/checks.json)。
- `execution.json` 的 SHA-256：`0499820a1550668ddb71f6ac8f3e069e75b9588fec3fdf5b4a0a1be958de3f66`。
- 原记录包含 96 条事件；累计 25 次模型调用、23 次业务工具调用、1,240,648 token、181.915 秒，费用未知。
- 实际运行版本：LangChain 1.4.0、LangGraph 1.2.11、Agent Server API 0.14.1、Gemini 适配器 4.4.0，见 [Context 清单](e-completed/context.json)。

下表按 `events` 数组的记录顺序列出 `tool_started`，匹配紧随的同名结束／错误事件；本样本没有工具事件交错。模型序号只表示工具开始前最近一条 `model_finished.call`，**不是通过 `tool_call_id` 证明的父子关联**。此种重建方法不能推广到并发工具调用。

## E 的实际顺序

日志中的 `calculate` 对应提供给模型的 `calculate_math`；不同命名也是后续追踪需要统一的事项。

| 工具次序 | 前置模型序号 | 工具 | 已记录的输入或结果 |
| --- | --- | --- | --- |
| 1 | 1 | `read_curriculum` | 仅记录开始，没有返回快照／指纹的事件；无法从此文件恢复当时返回值 |
| 2 | 2 | `plot_linear` | `ContentError`；未记录失败参数和具体错误文本 |
| 3 | 3 | `plot_linear` | 再次 `ContentError`；未记录失败参数和具体错误文本 |
| 4 | 4 | `plot_linear` | 成功保存 `assets/water_tank_fill.svg`；斜率 20、截距 40，横轴上界 10、纵轴上界 200 |
| 5 | 5 | `calculate_math` | `15 + 6 * 4` → `39` |
| 6 | 6 | `calculate_math` | `(145 - 85) / (7 - 3)` → `15` |
| 7 | 7 | `calculate_math` | `(220 - 145) / (12 - 7)` → `15` |
| 8 | 8 | `calculate_math` | `85 - 15 * 3` → `40` |
| 9 | 9 | `calculate_math` | `15 * 15 + 40` → `265` |
| 10 | 10 | `calculate_math` | `(180 - 40) / 20` → `7` |
| 11 | 11 | `calculate_math` | `(770 - 420) / (9 - 4)` → `70` |
| 12 | 12 | `calculate_math` | `420 - 70 * 4` → `140` |
| 13 | 13 | `calculate_math` | `70 * 12 + 140` → `980` |
| 14 | 14 | `calculate_math` | `(120 - 195) / (8 - 3)` → `-15` |
| 15 | 15 | `calculate_math` | `240 / 15` → `16` |
| 16 | 16 | `calculate_math` | `(30 - 18) / (60 - 20)` → `3/10` |
| 17 | 17 | `calculate_math` | `18 - (3/10)*20` → `12` |
| 18 | 18 | `calculate_math` | `(4/10)*100 + 12` → `52` |
| 19 | 19 | `calculate_math` | `52 - 42` → `10` |
| 20 | 20 | `save_curriculum` | `ContentError`；未保存失败入参及具体原因 |
| 21 | 21 | `read_curriculum` | 仅记录开始，没有返回快照／指纹的事件 |
| 22 | 22 | `save_curriculum` | 成功，内容指纹为 `3aafa7cd0b26f057ececc0c240363a4defc59cadadecb2a2dc5e047f4789844c` |
| 23 | 24 | `calculate_math` | `(145-85)/(7-3)` → `15` |

第 23 和第 25 次模型调用后没有记录业务工具；随后出现 `review_finished`，发现列表为空，并以 `work_finished` 结束。结构化检查回复所用的 `ToolStrategy(Review)` 不计入这 23 次业务工具，不能用该表枚举所有供应商层面的 function call。

成功图件的 SHA-256 为 `65b53e83aea76fb7248d6188f98aecfb4cf80ad362fa4208ffe56cd20feaa09f`，横轴标签为“注水时间 t (小时)”，纵轴标签为“水箱储水量 W (加仑)”。图件、参数和最终课程可从 [实际产物目录](e-completed/) 回查。最终检查对应上表保存的内容指纹，没有发现项；这只说明该有限任务的既有程序与模型检查结果。

## 哪些是推断，哪些不能补写

结合 [执行代码](../../../../src/teaching_harness/graph.py)，最自然的解释是：生成 Agent 经第 1–22 次模型调用完成读稿、绘图、验算和保存，第 23 次模型调用结束生成；审阅 Agent 在第 24 次调用验算，第 25 次形成结构化审阅。**由于缺少调用边界与消息记录，这个分段是控制流推断，不是日志直接给出的事实。** 尤其不能排除没有进入业务工具函数的结构化回复／参数校验步骤。

两次绘图失败不能直接解释为同一种错误；代码既可能拒绝图件名称，也可能拒绝旧内容指纹等条件。保存失败后重新读取再保存，符合修复旧指纹的行为模式，但原记录只保留 `ContentError`，不足以认定其具体原因。不能用代码中的可能错误文本冒充本次真实返回。

本次没有模型主动调用 `browse`。知识由执行端在调用 Agent 之前通过 `knowledge.prepare` 装配，具体 HTTP 记录位于 [knowledge.json](e-completed/knowledge.json)，不属于上表的模型工具序列。

## 为什么这是实现缺口

当前 `Budget.record` 只写事件类型和少量字段。`awrap_model_call` 没有逐调用保留用量、调用标识和可公开的工具请求；`awrap_tool_call` 没有统一记录成功输入输出；`read_curriculum` 没有结束记录；生成 `ainvoke` 的返回对象被丢弃，审阅只提取结构化结果。两个 Agent 共用一份累计日志，没有阶段或调用实例身份。

这不是 `create_agent` 无法观察：其返回对象包含消息，工具请求与响应可按原生标识关联，也有框架 callback／tracing 路径。前端不开放原始消息流，不妨碍在维护者可见的执行记录中保留所需工具入参、结果、错误和关联。关闭云端 tracing 也不能成为本地关联缺失的理由。

后续修正应复用框架标识和调用钩子，至少能关联任务／run、阶段、Agent 调用、模型调用、`tool_call_id`、选定参数、返回值或可回读引用、起止／错误和实际用量；模型内隐推理不作为记录要求。依赖旧内容引用时，只有指纹而没有可回读对象的情况必须如实标为不可重建。云端接入另外由 [LangSmith 观察票](../../issues/04-tracing-and-quality-regressions.md) 验证。

## 对执行图的判断

现有外层图只有 `START → curriculum_work → END`。知识装配、生成、独立审阅、确定性检查、反馈路由都放在节点内部，图没有表达这些业务阶段。已有 [执行结构设计](../../../skills-harness/assets/execution-structure-design.md) 原本就区分“各能力流程”和“阶段内行动循环”；本次实现尚未充分落实这个分工。

后续宜先把这些已有的粗阶段及反馈条件映射为明确的图状态和转移，再验证恢复与文件副作用的行为。模型按内容选择哪些算式、需要补查什么依据、如何设计任务，仍可在 `create_agent` 内完成。**计算函数是确定性的，不代表调用它的时机和表达式也是预先确定的。** 不能把本次事后观察到的 23 次工具序列固化成所有课程必须照走的流程，也不能为每条教学规则增加一个节点。

这份复核补记实现和观察缺口，不改写既有真实运行结果，不宣称阶段编排或完整追踪已经修好。
