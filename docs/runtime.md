# 有限课程任务的运行与调用

当前交付范围是八年级数学的有限课段方案、Narrative、关键任务构想、实际检查与阅读稿。标准固定使用 CCSS Mathematics。全年方案、完整单元材料、其余四项能力、真实待答恢复、内容历史和生产运行分别由后续票交付。

## 安装与启动

需要 Python 3.12／3.13、uv、Node.js 与 npm，以及已运行的本地 Learning Commons browse 服务。本次验证版本由 `uv.lock` 和 `package-lock.json` 固定。

```bash
uv sync --frozen
npm ci --ignore-scripts
# 参考 .env.example，把可信调用凭据配置到不入库的 .env.local。
# Gemini 密钥可沿用已有 .env。
uv run python scripts/dev.py --port 2024
```

启动脚本先加载 `.env.local` 和 `.env`，再执行原生 `langgraph dev`，没有新增 HTTP 服务、队列或 SSE 转发层。`langgraph.json` 的 env 只固定协议开关；直接启动原生服务时凭据由部署环境提供。框架自动注入 checkpointer，保存到 `.langgraph_api/`；不要删除该目录后期待找回原 thread。本阶段无需独立 PostgreSQL／Redis。本机内容默认写入 `work/`，可用 `HARNESS_WORK_DIR` 改为另一目录。

`HARNESS_AUTH_TOKENS` 是由服务管理员配置的身份到随机长凭据映射，适合本地开发；不是学校身份平台。调用方用 `Authorization: Bearer …`。正文中的身份、角色与租户声明不能覆盖认证上下文。已关闭开发工具的替代认证路径；生产认证、动态撤权与部署仍未验收。不要把这些后端凭据交给学生或公开浏览器。

开发脚本默认开启维护者诊断能力；详细读取需要另配可信维护者名单。LangSmith 云端发送默认关闭，显式设置 `LANGSMITH_TRACING=true` 后启动脚本和模型调用均尊重配置。原生服务自身的运行遥测与教学内容记录不同。平台 trace 关联由后续票验证。

## 教学请求与原生 API

正式类型在 `src/teaching_harness/contracts.py`。运行中读取 `/v1/contracts`，静态版本见 [请求 Schema](contracts/task-request.schema.json)、[查询 Schema](contracts/task-view.schema.json) 和 [内容 OpenAPI](contracts/content.openapi.json)。`uv run python scripts/export_contract.py` 可重新导出。

| 行为 | 使用入口 | 当前语义 |
| --- | --- | --- |
| 接收任务 | SDK `threads.create` | `thread_id` 由可信身份与 `event_id` 确定；metadata.request 放入正式 TaskRequest，服务重新校验并记录身份与正文指纹 |
| 启动生成 | SDK `runs.create` 或 `runs.stream` | 已创建 thread，assistant 为 `curriculum`；input 为 `{"request": 原请求}`，`multitask_strategy="reject"` |
| 重送 | `HarnessClient.submit` | 同一事件返回相同 thread／run；同事件不同正文冲突。已有 run 不重新生成 |
| 状态／断流恢复 | 原生 `threads.get`、`runs.get/list`、`runs.join_stream` | 刷新或断流先查询原任务；不要自动发起新生成。流式显式采用 `on_disconnect="continue"` |
| 教学进度 | 原生 `custom` 流 | 普通调用方取得实际步骤、未检查草稿、检查与修订、结果；重连省略过滤条件时也只返回 custom |
| 维护者诊断 | 原生 messages／updates／debug 及子图事件流 | 服务开关、维护者资格与原有任务归属同时生效；原生请求／响应含工具调用关联和实际内容 |
| 当前内容 | `GET /v1/threads/{id}/content` | 读取实际 JSON 和当前检查；不调用模型。可传 `expected_fingerprint`，过期则 409 |
| 阅读稿 | `GET /v1/threads/{id}/reading?expected_fingerprint=…` | 受同一身份约束的 HTML／MathML／SVG；只提供与当前指纹相符的阅读稿 |
| 执行依据 | `GET /v1/threads/{id}/evidence` | 当前 Context、知识查询及调用／工具／检查记录；无凭据或模型私有消息 |
| 取消 | 原生 `runs.cancel(action="interrupt")` | 保留已保存内容，查询显示取消；不提供 rollback。重送不会重开取消的任务 |

原生 API 的完整文档由运行服务的 `/docs`／`/openapi.json` 提供。教学请求不支持外部改写 checkpoint、任意 config、webhook、队列策略或状态预填。未实现 capability／scope 用 422 明确拒绝，不能自动变成另一能力。

`langgraph.json` 用框架原生 `FF_V2_EVENT_STREAMING=false` 关闭本票未接入的 v2 事件／命令协议，包括 `/threads/{id}/stream/events` 的 SSE／WebSocket 与 `/threads/{id}/commands`。这些入口会提供另一套运行配置和订阅方式，未经同等权限验证不能开放；本票使用的 `/runs` 原生 API 与流继续可用。锁定 API 版本的 `http.disable_event_streaming` 未在配置 Schema 中声明，实测会被忽略，因此采用功能开关。

接收与启动使用两个原生操作。若网络中断导致启动结果不明，先查询已有 thread 的 runs；确认没有 run 后才调用启动。并行重送通过原生并发拒绝与已有 run 查询收敛。本阶段不宣称跨机器故障恰好执行一次，也不自建接收／调度事务。

## 实际消费者

```bash
uv run python examples/live_curriculum.py --event 自己选择的唯一事件标识
# 仅查询已有任务，不重发生成：
uv run python examples/live_curriculum.py --event 原事件标识 --query 已返回的任务UUID
```

示例使用已有合成条件：28 人、3×50 分钟、纸笔与黑白打印，无真实学生诊断。它不是学校实际情况；正式调用方应提供自己的来源与版本。相同标识不可用于修改正文。新的事件代表新任务；未实现同一任务的预算续作或人类回应。

调用方显式提供模型调用、工具调用和活动秒数的防失控上限，仍可取消任务。当前阶段**默认不设置累计 token 预算**，示例也不设置；先完成必要生成、检查和修订，记录供应商实际 `usage_metadata`。已删除按消息字节数估算 token 并预留预算的做法。费用未知时保持 null，失败调用可能已产生供应商费用。

兼容字段 `limits.total_tokens` 可省略或为 null。仅调用方明确填写时，按已完成调用返回的实际累计用量判断是否继续；单次调用可能跨过阈值，所以它不是硬费用上限。明确设限但用量未知时不能继续核对额度；没有累计阈值时，已确认完成、仅缺计量的调用标记 `unknown_usage`，不因此中止教学工作。无论是否设限，结果未确认的外部调用仍禁止盲目重放。

当前 Gemini adapter 的 `get_num_tokens(text)` 调用 Google `count_tokens`，可计数文本输入；若要精确计数完整请求，还需包含 system instruction、工具声明等请求内容。响应 `usage_metadata` 提供实际输入、输出及总用量，输出包含模型思考 token；不能事前精确预测输出消耗。本阶段不前置建设累计预算分配器。参见 [Google token 计数接口](https://ai.google.dev/api/tokens)。

实测发现原生 `cancel(wait=true)` 可先返回终态，关闭服务时后台节点仍可能被框架重新排队。当前执行入口若看到已有调用证据，保留累计消耗并返回 `stopped`，不会从零预算再次生成。这只是当前切片的重入保护；取消持久性、自动恢复和受控续作仍由后续票验收。操作后应查询原任务，不能将 `wait=true` 当作故障恢复保证。

## 当前内容与检查

工作目录保存 `content/curriculum.json`、`assets/*.json`／`*.svg`、`output/curriculum.html`、`checks.json`、`context.json`、`knowledge.json` 和 `execution.json`。后三者是执行证据，不是运行状态权威；thread／run 仍由框架管理。

当前源只维护一份；保存时比较预期指纹，同目录加锁、单文件先写完整再替换。检查关联源、图件和实际阅读稿；图件参数必须能重新生成完全相同的 SVG，否则查询拒绝交付。改写内容、换图、破坏引用或改变检查规则都不能继续显示原稿通过；没有跨文件事务、历史读取或回滚承诺。后续正式内容修订入口尚未开放。

正文支持 Markdown 与 LaTeX，表格为显式行列。公式用固定 KaTeX 转为 MathML；原始 HTML 不执行。图件工具当前只绘制第一象限内的线性函数，保存数学参数与 SVG，未提供任意绘图代码、上传解析或图片平台。HTML 是课程负责人／教师的完整阅读稿，含解答；学生材料受众投影由单课材料票实现，不能直接把这一阅读稿发给学生。

生成模型只能保存候选。程序核对目标集合、课时预算、引用、渲染与指纹；隔离审阅调用读取当前实际课程、知识和图件，逐项检查覆盖、数学、进程、条件、证据及来源。阻断问题返回生成模型修订并重查。`completed` 仅表示本次有限切片的程序与模型检查通过，不表示教师批准、课堂成效、全年课程完备或广泛教学质量达标。

外部原课通过 `external_content` 传入实际文本／结构内容、来源、版本和内容指纹。接受的源会进入当前任务 Context；不会按链接下载文件，也不要求原课来自本仓库生成器。

示例可用 `--source 已规范化内容.json --instruction 本次设计要求` 传入真实来源。新的发起事件会产生新任务；这不代表恢复旧 run 或读取内容历史。阅读排版会展开模型偶发的独立字面换行标记，保留原 JSON 文本与 LaTeX 命令。

保存后必须核对 `rendered`。失败时 `render_errors` 给出当前源字段、出错公式和具体原因，作者修改同一 JSON 源并重新保存；错误记录绑定源与图件指纹，成功后清除。当前源未成功生成阅读稿不能通过检查。正文支持同段的 `$…$` 与 `$$…$$`，不要求调用方靠手工补空行规避解析器缺陷；LaTeX 命令由 JSON 序列化转义，不手工重复转义。实现和验收遵循上游“修源→重新渲染→检查实际输出”的闭环，保存草稿不是格式修复的完成条件。

无法匹配的公式定界符和常见 LaTeX 命令的重复转义也会返回字段级错误。普通美元符号使用 `\$`，代码示例放在反引号内；独立的 `$5` 金额与缺结束符的纯数字公式存在语法歧义，按金额处理。语法检查不等于数学语义正确，最终文件仍要核对。

## 维护者诊断

在服务端 `.env.local` 配置 `HARNESS_DEBUG_IDENTITIES=["本地开发调用方"]`，身份须已存在于 `HARNESS_AUTH_TOKENS`。正文／metadata 不能赋予维护者角色。维护者仍只能读取原本有权访问的任务，当前开发认证按任务 owner 隔离；跨学校运维授权由后续认证票扩展。

| 配置 | 开发脚本 | 生产直接启动 |
| --- | --- | --- |
| `HARNESS_DIAGNOSTICS` | 未设置时为 `true`，显式 `false` 关闭 | 未设置时关闭，显式 `true` 开启 |
| `HARNESS_DEBUG_IDENTITIES` | 默认空名单，需要明确指定 | 同样需要明确指定 |
| `LANGSMITH_TRACING` | 默认 `false`；尊重显式设置并统一旧别名 | 生产直接启动须显式设置 `false` 关闭发送；原生服务可能按 API Key 自动开启 |

生产关闭详细诊断时仍保存基础执行事件、任务结果与用量。开关控制新详细订阅、重连和内部子图状态读取；已经发送的流无法收回。当前配置由服务进程读取，更改 `.env.local` 后需受控重启；不宣称已经实现在线动态撤权。LangSmith 发送与本地诊断是独立开关，关闭云端发送须设置 `LANGSMITH_TRACING=false`。

开发脚本按 `LANGSMITH_TRACING`、`LANGSMITH_TRACING_V2`、`LANGCHAIN_TRACING_V2`、`LANGCHAIN_TRACING` 的顺序取首个已设置值，并同步别名，避免 SDK 与 Agent Server 优先级不同导致关闭失效。生产直接启动不会经过这个脚本，应清除旧别名或统一设为相同值。

用新事件发起带诊断的开发运行：

```bash
uv run python examples/live_curriculum.py \
  --event 维护者诊断-001 \
  --identity 本地开发调用方 \
  --diagnostics work/diagnostics/维护者诊断-001.jsonl
```

示例通过 `HarnessClient.submit(..., diagnostics=True)` 为新 run 选择 `custom`、`messages-tuple`、`updates`、`debug`、子图流及原生 `stream_resumable`。保存 task／run 回执、事件 ID、命名空间与原始事件数据；终端仍显示教学进度。诊断文件含实际模型／工具内容，权限为 `0600`，已有文件拒绝覆盖。作者与检查 Agent 分别命名为 `curriculum_author`、`curriculum_reviewer`；工具请求的 `id` 与返回的 `tool_call_id` 用于配对，保留工具名、参数、返回或错误。重复消息可能来自不同流模式，应按调用标识及子图执行路径归并，不能用事件条数当作工具次数。

已有诊断运行通过官方 SDK 回放：

```python
# client 是具有维护者凭据的 HarnessClient；只读取已有 run。
async for part in client.native.runs.join_stream(
    task_id, run_id, last_event_id="0-0"
):
    print(part.event, part.id, part.data)
```

`0-0` 从已保留的首条事件开始；断线续接用最后收到的事件 ID。当前 dev 的可重连流缓存在进程内，结束后可回放，服务重启后不保证保留；长期复核使用已导出的 JSONL。checkpoint 不是这份流缓存。对未启用详细保留的旧事件重送不会补录，也不会重新调用模型；既有 E 的缺失参数／返回不能追溯恢复。

作者／审阅已改为静态子图；具有任务访问权的维护者可以通过历史父检查点回取实际子图状态。只读取最新外层 completed 不代表读到了内部历史，具体方法见[有限课段的阶段图](#有限课段的阶段图)。实际服务验证见[重构记录](../.scratch/math-harness-delivery/evidence/01-live-curriculum/graph-refactor/README.md)。

如需 LangSmith，可在服务端显式设置 `LANGSMITH_TRACING=true`、`LANGSMITH_API_KEY`、`LANGSMITH_PROJECT`。本次验证使用真实 dev 服务和可控模型／知识边界，没有上传历史内容，也没有验收云端关联、故障解耦或生产数据范围策略；这些仍见 [观察平台票](../.scratch/math-harness-delivery/issues/04-tracing-and-quality-regressions.md)。

## 知识与原创隔离

每次运行从本地健康信息固定数据快照，从框架目录解析 CCSS 数学身份。代码解析核对精确代码、框架路径和节点正文，CASE 身份与图内身份分别保留。组件经 `LC → supports → Standard` 取得；前驱查询 `buildsTowards` 入边，后继查询出边。分页、源版本和排除结果随查询记录；空集不伪造关系。

模型没有任意文件、URL、SQL、shell 或课程读取工具。browse 只投影标准、组件、实际进阶边及来源，移除混合课程导航／对齐信息；输入和投影对已标识的对应参考来源作排除检查。实际运行不装配开发研究目录或目标课程。该边界不能消除模型预训练记忆，也不能证明未标明来源的复制文本没有参考污染。

框架依据：[Agent Server 认证](https://docs.langchain.com/langsmith/auth)、[自定义只读路由](https://docs.langchain.com/langsmith/custom-routes)、[LangChain 原生模型循环](https://docs.langchain.com/oss/python/langchain/agents)。实际适用范围以本仓库锁定版本和运行证据为准。

## 有限课段的阶段图

2026-09-16 的重构采用 `prepare_task → author → prepare_review → reviewer → record_review`。作者和审阅是静态 `create_agent` 子图；准备、固定送审对象、提交检查和停止收尾用普通 Python。阻断检查由条件边返回作者，不额外调用一个“路由 LLM”。[目标图与边界](../.scratch/math-harness-delivery/ticket-01-graph-refactor-design.md)记录状态和恢复位置。

维护者可用 `threads.get_history()` 取得父检查点，再用 `threads.get_state(task_id, checkpoint=..., subgraphs=True)` 展开当时的作者或审阅子图。已结束任务的最新父状态未必带子图任务，应从历史检查点读取；原生消息流仍可按诊断示例回放。父状态不含 `messages`，普通证据接口也不返回工具重放缓存。

已持久化的准备、作者和审阅输出分别支持框架阶段接续。当前 API 继续拒绝调用方任意改写状态、配置或发起续作；完整教师回应及取消后续作留在后续票。未知外部调用停止自动重放，消耗不归零。

**升级前先处理旧图的活动 run。** 本次拓扑版本是 `curriculum-stages-v1`；旧图的 `curriculum_work` 检查点不能直接交给新图继续。等待旧活动运行结束，或保留旧版本服务处理它们；旧成果仍可按文件读取。真实重构验收使用独立端口和工作目录，未热替换原开发服务。
