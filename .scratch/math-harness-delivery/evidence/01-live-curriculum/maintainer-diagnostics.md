# 维护者诊断的实施与验证

日期：2026-09-15。用户要求开发阶段能够跟踪模型／工具执行，生产可关闭，维护者不能被普通教学流的限制永久挡住。范围补入 [首票](../../issues/01-live-curriculum-task.md)，采用条款见 [规格](../../spec.md#4-任务级调用约定)。

## 实施结果

- 原生 Agent Server 接受经服务端配置授权的详细消息、工具、debug 与子图事件流。需同时满足 `HARNESS_DIAGNOSTICS=true`、身份在 `HARNESS_DEBUG_IDENTITIES` 中，以及原有任务 owner 权限。
- `scripts/dev.py` 默认开启本地诊断能力；直接启动的服务未设置开关时关闭。普通重连固定过滤 custom，线程详细流拒绝，不能借重连绕过创建时的限制。
- `langgraph.json` 通过原生 `FF_V2_EVENT_STREAMING=false` 关闭未纳入本票的 v2 SSE／命令／WebSocket，避免另一套入口绕过诊断和运行配置限制；保留已验证的原生 runs 流。
- `HarnessClient.submit(..., diagnostics=True)` 为新 run 开启原生详细且可重连的流。示例 `--diagnostics` 保存 JSONL，含 thread／run 回执、事件 ID、命名空间与原始数据；新文件权限 `0600`，拒绝覆盖。
- 作者和检查 Agent 有独立名称，原生流保留工具请求的 `id` 和返回的 `tool_call_id`。不同流模式会重复展示同一消息，需按调用标识和子图路径配对，不能直接计数事件。
- 移除两个 `tracing_context(enabled=False)` 及开发脚本强制关闭逻辑，尊重服务端 `LANGSMITH_TRACING`；未配置时开发脚本默认不发送云端内容。基础执行事件、任务结果和用量继续记录。

使用步骤见 [运行说明](../../../../docs/runtime.md#维护者诊断)。本机维护者配置写在忽略的 `.env.local`，不保存真实 token。配置变化需受控重启，不是在线动态撤权。

## 验证方法与结果

使用锁定依赖的真实 `langgraph dev`，仅把正式图的外部模型与知识服务替换为测试边界；测试配置始终关闭 LangSmith。本轮不调用真实 Gemini，不上传历史教学内容。没有把测试固定内容当作教学质量或平台接通证据。

`tests/test_diagnostics.py` 验证：

1. 维护者读取原生模型、工具及外层任务状态：调用 `calculate_math`，ID 为 `math`，参数 `(23-11)/(6-2)`，对应 `tool_call_id=math` 的返回为 `3`。状态断言只证明外层完成，不证明内部 checkpoint 可独立回取。
2. 运行结束后从 `last_event_id="0-0"` 回放到首个工具往返，同时可识别 `curriculum_author` 与 `curriculum_reviewer`。
3. 普通身份请求消息流和线程详细流被拒绝；跨任务 owner 的维护者读取状态／流也被拒绝。原生 SSE 可能先发 HTTP 200，随后只发 `error` 事件报告 404，测试检查实际事件而非只检查 HTTP 头。
4. 普通重连即使不传过滤器，也只取得教学 custom 事件，不继承其他已发布模式。
5. 生产默认未设置、显式 `false` 两种配置均拒绝详细创建、重连和内部状态读取；普通任务仍完成，用量非零。
6. 独立命令行消费者实际保存错误调用：`calculate_math(1/0)` 的 ID 与对应错误消息可配对；结果与作者／审阅路径均可读取，文件权限为 `0600`，未包含测试认证 token，终端无原始工具消息。
7. 普通身份与维护者均不能从未开放的 v2 事件／命令入口绕过限制：HTTP 入口为 404，WebSocket 握手拒绝，带任意 config／metadata 的命令未创建 run。测试复用正式 `langgraph.json` 的 HTTP 与 env 配置，避免只在测试夹具里关闭。首次采用 `http.disable_event_streaming` 后测试仍失败：锁定 API 的配置 Schema 未包含该字段，会静默丢弃；改用原生功能开关。

`tests/test_dev_config.py` 在进程启动边界验证诊断默认值、显式关闭、LangSmith 显式开启及旧别名兼容，并检查 SDK 实际 `tracing_is_enabled()`。测试避免读取本机密钥或启动真实云端发送。

最终全量 [40 项通过，24.37 秒](diagnostics-pytest.txt)，Ruff 与 mypy（12 个源文件）通过。原有教学 API、内容、知识与模型 Schema 测试继续通过。本轮早期全量 35 项通过后，审查发现缺口，新增反例并再次全量验证；不把早期通过当作最终收口。

## 规范审查

按 `code-review` 技能，以 `9d1cb71e13cd5a5aed33f1c2001a7bcc75c6145f` 为固定基点审查本轮工作区与新增文件。规范轴发现 2 项：v2 备用事件／命令协议能绕过既有配置和订阅限制；新旧 LangSmith 开关优先级不同，显式关闭可能仍被 SDK 解释为开启。两项均已用真实失败用例复现，再通过原生功能开关与追踪别名归一修复。规范轴复核剩余 0 项，没有单列 Fowler 启发式问题。

## 规格审查

规格轴发现 2 项能力声明超出证据：内部子图 checkpoint 独立回取尚未实现，以及开发脚本的云端默认关闭不能代表生产直接启动的默认值。已收窄说明：当前提供详细事件流与外层状态，内部 checkpoint 回取后置；生产直接启动须显式配置追踪关闭。规格轴复核剩余 0 项，云端验收与阶段图／恢复范围保持后置。

## 限制与后续

当前 dev 原生流缓存位于进程内，运行结束可回放，重启后不保证保留。需要长期复核时保存 JSONL；checkpoint 不能替代详细流记录。已有普通 run 不因重送而补录，既有 E 的缺失参数／返回也无法追溯恢复。原始 E 文件保持不变。

LangSmith 是独立发送开关；本地诊断关闭不自动关闭云端。真实云端发送／读取、业务关联、发送范围和观察故障解耦仍由 [观察平台票](../../issues/04-tracing-and-quality-regressions.md) 验收。生产认证、跨任务运维授权和动态撤权也未提前声明完成。

作者／审阅 Agent 动态创建，原生外层图不能发现其子图供 checkpoint 独立回取；当前详细消息通过事件流观察，不能宣称已经支持内部状态历史。开发脚本默认关闭云端发送，生产直接启动需显式关闭；原生平台可能在只配置 API Key 时自动启用追踪。开发脚本已统一新旧开关，防止旧版 `true` 覆盖新版 `false`。

本次没有重构外层阶段图；[ReAct 与工作流职责复核](../../../skills-harness/assets/react-and-workflow-boundaries.md) 中的编排缺口仍保留，不能用工具追踪通过替代阶段恢复验证。
