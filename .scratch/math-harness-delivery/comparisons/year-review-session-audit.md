# 首次全年蓝图：作者与审阅会话证据核查

日期：2026-09-16。范围仅限 `15-full-year-blueprint/initial` 对应的真实运行。未重新调用模型，未读取或复制凭据，也不输出模型私有思考或签名。当前工作范围按用户最新要求限于全年规划；本记录不推进 Lesson 或连续课时。

## 结论

**首次作者与审阅者属于同一 Agent Server thread，但模型消息历史隔离。** 审阅并非接在作者几十条对话后继续；它重新接收一条包含待审稿与依据的用户消息。两者共享模型类型和教学材料，这不等于共享作者的模型对话，也不保证审阅能够摆脱同模型或作者表述带来的偏差。

本结论来自实际原生流与调用签名核对，不仅来自当前代码。初次审阅确实漏检；没有证据把漏检归因为“同一 conversation 沿用作者思考”。

## 原始记录与可复核位置

本地原始流：[work/year-live/trace.jsonl](../../../work/year-live/trace.jsonl)，557 行。其 SHA-256 为 `44458655914a0062702f6cca24e70c8065587f95bcb1f505c00ecb6797f466ac`，本次重新计算与[初稿用量审计](../evidence/15-full-year-blueprint/initial/usage-audit.json)记录一致。原始流被 Git 忽略，仅维护者本地保存；下文只记录结构、计数和证据位置。

| 要核查的事实 | 实际证据 |
| --- | --- |
| 服务端任务是否相同 | 第 12、524 行 checkpoint 的 `thread_id` 都是 `bd2963bc-6183-58c2-b2b3-90a14f60a398`。 |
| 子图状态是否分开 | 第 12 行命名空间为 `author:dcd8fec1-056b-fda5-4061-d50c3f63b1c3`；第 524 行为 `reviewer:0760a46f-cebd-bfd4-84bd-0d73428de153`。 |
| 作者末次模型输入 | 第 282 行 `payload.input.messages` 有 39 条：1 human、19 ai、19 tool。 |
| 审阅首次模型输入 | 第 526 行只有 1 human、0 ai、0 tool；该 human 的 `additional_kwargs` 与 `response_metadata` 均为空。没有传入作者 AI 消息或作者工具对话序列。 |
| 审阅后续模型输入 | 第 540 行为 1 human、1 ai、1 tool；新增的 AI／Tool 来自审阅者自己的 `calculate_math`，并非作者历史。 |
| 实际模型与次数 | 第 528、542 行消息元数据均为 `google_genai`／`gemini-3.8-flash`。初稿合计 22 次模型调用：作者 20 次、审阅 2 次；工具合计 20 次：作者 19 次、审阅 1 次。 |

进一步将第 526 行的实际 `work.rules` 与 `messages` 按历史 middleware 的序列化方式重算指纹，得到 `230b292d3d85cdf122f420d4dfcb8517da54caf58203a7f8f116e72f1d25525e`，与[执行记录](../evidence/15-full-year-blueprint/initial/execution-summary.json)首次 `reviewer/0/model/…` 完全一致。因此，原生图输入与该实际模型调用的规则／消息签名可以对应起来。

这里的调用指纹是本地请求摘要，不是 Gemini 的私有 thought signature。

## 审阅首次实际收到什么

第 526 行唯一 human 消息的 JSON 顶层只有以下五项，总长 255,384 个 Python 字符；字符数不是 token 数：

| 字段 | 实际内容及计数 |
| --- | --- |
| `request` | 原始全年请求、180 节课、20 节机动、每课 50 分钟、28 人、资源和合成条件等；`external_content` 为空。 |
| `knowledge` | `year_scope`、36 条 `scope` 条目及 9 条 `additional` 查询结果。追加结果含 code、operation、records、来源等，是作者已查到的知识依据。 |
| `content` | 当前完整全年蓝图：Narrative、8 个单元、目标、数学实践、4 个探查的题面与解法、来源采用及交接等。 |
| `assets` | `assets/rainwater_tank.svg` 的审阅资源。 |
| `render_identity` | 本次渲染对象及身份信息。 |

输入没有 `review_feedback`、先前 `review_result` 或作者消息列表；也没有作者 AI 消息携带的内部思考／thought signature。**但审阅不是不接触作者结论的盲审**：完整稿件中的设计理由、解答、预判回应和效果表述都可见，知识包还包含作者选查的资料。这是内容层面的共享，不能称为完全独立证据。

审阅唯一一次实际工具调用是 `calculate_math("22+22+22+18+26+16+14+20")`。它核算课时合计，并没有用工具分别核算全部探查。模型最终写了四项探查的计算依据，但这些文字不能证明额外工具执行，也不能仅凭此证明每项任务已得到充分独立验证。[实际工具记录](../evidence/15-full-year-blueprint/initial/tool-execution.json)、[初稿检查](../evidence/15-full-year-blueprint/initial/checks.json)

## 当时的规则与历史代码

实际规则保存在[初稿 context.json](../evidence/15-full-year-blueprint/initial/context.json)第 31 行 `prepared_context.rules.review`，与原生流第 526 行 `work.rules` 逐字一致，长度 1,064 个字符。它要求独立审阅、仅报告当前稿实际证据，并按覆盖、数学、进程、条件、评价证据、来源六类检查；包含独立求解探查、条件／单位／反例、资源时间、预测回应不确定性及不得声称课堂验证等要求。

**不能用当前更长规则代替当时规则。** 对照提交 `2e29ec2` 中的 `resources/year-review.md`，该提交比初次运行规则多了“此前审阅漏查过以下问题”的资源、数据、数学范围及效果声明清单。它是后续强化，不是第一次审阅已经收到的内容。初次规则并非完全没有相关要求，但这些要求仍未阻止实际漏检。

历史提交 `2e29ec2` 的 `src/teaching_harness/graph.py` 第 225–239 行显示一次 `model_factory()` 的结果传给两个 `create_agent`；第 148 行各自用新 `HumanMessage` 初始化；第 421–445 行审阅只装配上述五项内容。其 `execution.py` 第 178–179 行将本阶段规则设置为 system message，并对规则和消息计算调用指纹。这与真实轨迹吻合。

该提交晚于初次运行，且规则确有后续变化，因此这里只把它作为可复核的历史实现对照，**不把它冒充初次运行的完整构建快照**。原始流没有记录 Python 对象身份，无法单靠流证明当时两个 Agent 使用同一个对象实例；可以确认二者同模型名称、同服务端任务、不同子图命名空间，以及上述实际消息分离。

## 不能由本次核查推出什么

- 没有逐字节网络抓包，不能宣称已审计 Gemini HTTP 请求中的全部传输字段或提供方内部状态；结论限于原生模型节点输入、实际调用摘要及响应元数据。
- 没有跨模型或盲审对照，不能证明同模型盲点、共享作者表述、规则具体程度或检查流程各造成多少漏检。
- 同一服务端 thread 用于管理本次任务，不等于模型自动看见其全部状态；同一模型对象也不是对话历史的替代物。真正需要审计的是每次调用实际装配的消息、规则和工具结果。
- 消息隔离只能回答“是否携带作者对话”，不能回答全年规划方法是否充分、课程是否达到 IM 水平或审阅是否可靠；这些仍需实际全年产物与独立评价机制验证。
