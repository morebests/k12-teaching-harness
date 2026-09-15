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

启动脚本最终执行原生 `langgraph dev`，没有新增 HTTP 服务、队列或 SSE 转发层。框架自动注入 checkpointer，保存到 `.langgraph_api/`；不要删除该目录后期待找回原 thread。本阶段无需独立 PostgreSQL／Redis。本机内容默认写入 `work/`，可用 `HARNESS_WORK_DIR` 改为另一目录。

`HARNESS_AUTH_TOKENS` 是由服务管理员配置的身份到随机长凭据映射，适合本地开发；不是学校身份平台。调用方用 `Authorization: Bearer …`。正文中的身份、角色与租户声明不能覆盖认证上下文。已关闭开发工具的替代认证路径；生产认证、动态撤权与部署仍未验收。不要把这些后端凭据交给学生或公开浏览器。

当前启动脚本关闭内容 trace 上报，保留本地执行记录；原生服务自身的运行遥测与教学内容记录不同。LangSmith 平台 trace 关联由后续票验证。

## 教学请求与原生 API

正式类型在 `src/teaching_harness/contracts.py`。运行中读取 `/v1/contracts`，静态版本见 [请求 Schema](contracts/task-request.schema.json)、[查询 Schema](contracts/task-view.schema.json) 和 [内容 OpenAPI](contracts/content.openapi.json)。`uv run python scripts/export_contract.py` 可重新导出。

| 行为 | 使用入口 | 当前语义 |
| --- | --- | --- |
| 接收任务 | SDK `threads.create` | `thread_id` 由可信身份与 `event_id` 确定；metadata.request 放入正式 TaskRequest，服务重新校验并记录身份与正文指纹 |
| 启动生成 | SDK `runs.create` 或 `runs.stream` | 已创建 thread，assistant 为 `curriculum`；input 为 `{"request": 原请求}`，`multitask_strategy="reject"` |
| 重送 | `HarnessClient.submit` | 同一事件返回相同 thread／run；同事件不同正文冲突。已有 run 不重新生成 |
| 状态／断流恢复 | 原生 `threads.get`、`runs.get/list`、`runs.join_stream` | 刷新或断流先查询原任务；不要自动发起新生成。流式显式采用 `on_disconnect="continue"` |
| 教学进度 | 原生 `custom` 流 | 实际步骤、未检查草稿、检查与修订、结果；不开放 messages／debug 或内部子图 |
| 当前内容 | `GET /v1/threads/{id}/content` | 读取实际 JSON 和当前检查；不调用模型。可传 `expected_fingerprint`，过期则 409 |
| 阅读稿 | `GET /v1/threads/{id}/reading?expected_fingerprint=…` | 受同一身份约束的 HTML／MathML／SVG；只提供与当前指纹相符的阅读稿 |
| 执行依据 | `GET /v1/threads/{id}/evidence` | 当前 Context、知识查询及调用／工具／检查记录；无凭据或模型私有消息 |
| 取消 | 原生 `runs.cancel(action="interrupt")` | 保留已保存内容，查询显示取消；不提供 rollback。重送不会重开取消的任务 |

原生 API 的完整文档由运行服务的 `/docs`／`/openapi.json` 提供。教学请求不支持外部改写 checkpoint、任意 config、webhook、队列策略或状态预填。未实现 capability／scope 用 422 明确拒绝，不能自动变成另一能力。

接收与启动使用两个原生操作。若网络中断导致启动结果不明，先查询已有 thread 的 runs；确认没有 run 后才调用启动。并行重送通过原生并发拒绝与已有 run 查询收敛。本阶段不宣称跨机器故障恰好执行一次，也不自建接收／调度事务。

## 实际消费者

```bash
uv run python examples/live_curriculum.py --event 自己选择的唯一事件标识
# 仅查询已有任务，不重发生成：
uv run python examples/live_curriculum.py --event 原事件标识 --query 已返回的任务UUID
```

示例使用已有合成条件：28 人、3×50 分钟、纸笔与黑白打印，无真实学生诊断。它不是学校实际情况；正式调用方应提供自己的来源与版本。相同标识不可用于修改正文。新的事件代表新任务；未实现同一任务的预算续作或人类回应。

资源上限必须显式提供，包含模型调用、工具调用、累计 token 和活动秒数。示例额度用于本次有限验证，未经生产工作量校准。每次调用前预留输入与输出空间，并记录供应商实际用量；若消耗未知、剩余额度不足或超时，则停止续作，保留已保存草稿。费用未知时保持 null，失败调用可能已产生供应商费用。

实测发现原生 `cancel(wait=true)` 可先返回终态，关闭服务时后台节点仍可能被框架重新排队。当前执行入口若看到已有调用证据，保留累计消耗并返回 `stopped`，不会从零预算再次生成。这只是当前切片的重入保护；取消持久性、自动恢复和受控续作仍由后续票验收。操作后应查询原任务，不能将 `wait=true` 当作故障恢复保证。

## 当前内容与检查

工作目录保存 `content/curriculum.json`、`assets/*.json`／`*.svg`、`output/curriculum.html`、`checks.json`、`context.json`、`knowledge.json` 和 `execution.json`。后三者是执行证据，不是运行状态权威；thread／run 仍由框架管理。

当前源只维护一份；保存时比较预期指纹，同目录加锁、单文件先写完整再替换。检查关联源、图件和实际阅读稿；图件参数必须能重新生成完全相同的 SVG，否则查询拒绝交付。改写内容、换图、破坏引用或改变检查规则都不能继续显示原稿通过；没有跨文件事务、历史读取或回滚承诺。后续正式内容修订入口尚未开放。

正文支持 Markdown 与 LaTeX，表格为显式行列。公式用固定 KaTeX 转为 MathML；原始 HTML 不执行。图件工具当前只绘制第一象限内的线性函数，保存数学参数与 SVG，未提供任意绘图代码、上传解析或图片平台。HTML 是课程负责人／教师的完整阅读稿，含解答；学生材料受众投影由单课材料票实现，不能直接把这一阅读稿发给学生。

生成模型只能保存候选。程序核对目标集合、课时预算、引用、渲染与指纹；隔离审阅调用读取当前实际课程、知识和图件，逐项检查覆盖、数学、进程、条件、证据及来源。阻断问题返回生成模型修订并重查。`completed` 仅表示本次有限切片的程序与模型检查通过，不表示教师批准、课堂成效、全年课程完备或广泛教学质量达标。

外部原课通过 `external_content` 传入实际文本／结构内容、来源、版本和内容指纹。接受的源会进入当前任务 Context；不会按链接下载文件，也不要求原课来自本仓库生成器。

示例可用 `--source 已规范化内容.json --instruction 本次设计要求` 传入真实来源。新的发起事件会产生新任务；这不代表恢复旧 run 或读取内容历史。阅读排版会展开模型偶发的独立字面换行标记，保留原 JSON 文本与 LaTeX 命令。

## 知识与原创隔离

每次运行从本地健康信息固定数据快照，从框架目录解析 CCSS 数学身份。代码解析核对精确代码、框架路径和节点正文，CASE 身份与图内身份分别保留。组件经 `LC → supports → Standard` 取得；前驱查询 `buildsTowards` 入边，后继查询出边。分页、源版本和排除结果随查询记录；空集不伪造关系。

模型没有任意文件、URL、SQL、shell 或课程读取工具。browse 只投影标准、组件、实际进阶边及来源，移除混合课程导航／对齐信息；输入和投影对已标识的对应参考来源作排除检查。实际运行不装配开发研究目录或目标课程。该边界不能消除模型预训练记忆，也不能证明未标明来源的复制文本没有参考污染。

框架依据：[Agent Server 认证](https://docs.langchain.com/langsmith/auth)、[自定义只读路由](https://docs.langchain.com/langsmith/custom-routes)、[LangChain 原生模型循环](https://docs.langchain.com/oss/python/langchain/agents)。实际适用范围以本仓库锁定版本和运行证据为准。
