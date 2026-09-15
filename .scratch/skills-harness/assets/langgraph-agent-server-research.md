# LangChain、LangGraph 与 Agent Server：教学执行的运行承载

查阅日期：2026-09-15。关联：[运行栈专项](../issues/11-agent-server-stack-research.md)、[执行结构决定](../issues/03-execution-structure.md)、[HITL 决定](../issues/07-hitl-protocol.md)。本文为官方资料研究与本项目推论，未部署服务器、运行恢复实验或验证生产容量；不替代后续锁定版本的检查。LangSmith 观察与评测由同一专项另行整合。

**结论：可以复用现成的模型循环、持久化执行和任务服务，主要自建工作应集中在教学 Context、真实人类决定、版本化产物和检查条件。** 长程运行没有理由继续以实验脚本的单进程循环为生产承载，也没有依据为每个教学场景另造队列或状态机。教学上的等待位置已有决定；本研究核对如何可靠承载它们，而不是重新规定何时必须找教师。

后续证据：[锁定版本的持久运行实测](cfu-durable-prototype-results.md) 已验证有限 SQLite 恢复、真实原型回应及 Agent Server dev 正常重启。下文保留本次官方研究的事实／推论，实际保证只以该实测范围为限。

## 官方事实

### 组件与职责

LangChain 的 `create_agent` 提供模型调用工具的循环，并可用 middleware 装配提示、工具和运行行为；LangChain agents 建立在 LangGraph 上。LangGraph 提供更底层的有状态执行，允许确定性步骤与模型行动共存，不要求将所有推理拆成节点。[LangChain agents](https://docs.langchain.com/oss/python/langchain/agents)、[产品关系](https://docs.langchain.com/oss/python/langgraph/overview)。

当前产品名称是 **LangSmith Deployment**，其中 **Agent Server** 提供部署应用的 API、持久化和后台任务队列。服务器注入 checkpointer 与 store，应用导出的图不应自行配置另一套。`assistant` 是图的可版本化配置；`thread` 跨多次运行保存状态；`run` 是一次执行。配置版本不等于图代码版本，thread 也不是学校、学生或课程实体本身。[Agent Server](https://docs.langchain.com/langsmith/agent-server)、[Assistants](https://docs.langchain.com/langsmith/assistants)、[Threads](https://docs.langchain.com/langsmith/use-threads)、[Runs](https://docs.langchain.com/langsmith/runs)。

### HITL 与恢复

`interrupt(payload)` 以可序列化内容发出等待，依赖持久化 checkpointer 和稳定 `thread_id`。随后以同一 thread 的 `Command(resume=...)` 恢复；回应成为 `interrupt()` 的返回值。它能承载选择、编辑、教师贡献等不同内容，并非只能返回批准布尔值；Server SDK 也有相应恢复入口。[Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)、[Server HITL](https://docs.langchain.com/langsmith/add-human-in-the-loop)。

恢复会**从中断节点入口重新执行**，不是恢复 Python 调用栈到暂停的那一行。中断前模型调用或外部写入可能重做；同一节点内中断的调用顺序需稳定。已完成 task 的结果可由 checkpoint 复用，但开始后未完成的 task 仍可能重跑，需幂等键或核对已有结果。[恢复规则](https://docs.langchain.com/oss/python/langgraph/interrupts#rules-of-interrupts)、[task 幂等性](https://docs.langchain.com/oss/python/langgraph/functional-api#idempotency)。

`sync` 在下一步前完成 checkpoint；`async` 与下一步并行写，崩溃有未写下的窗口；`exit` 只在正常、错误或 HITL 退出时保存，中途崩溃不能恢复中间进度。这些控制图状态的耐久性，**没有把图数据库与产物存储合成事务，也没有认定教师已接受材料**。[Durability modes](https://docs.langchain.com/oss/python/langgraph/checkpointers#durability-modes)。

### 后台运行、断连与取消

Agent Server 已提供后台执行和流式输出。`POST /threads/{thread_id}/runs/stream` 当前默认 `on_disconnect="continue"`、`durability="async"`、`multitask_strategy="enqueue"`、`stream_resumable=false`；这些应显式配置，不靠默认值表达产品决定，也不推广为所有 SDK 方法或端点的默认值。`run` 的终止与浏览器连接结束不同。[创建及流式 API](https://docs.langchain.com/langsmith/agent-server-api/thread-runs/create-run-stream-output)。

普通 `join_stream` 不补发加入前的输出。可恢复 run stream 需显式启用，相关输出暂存 Redis，当前默认 TTL 为 120 秒；超过窗口不能假定每个 token 都可补齐。thread stream 另提供 `Last-Event-ID`，不要混用其接口和保证。[Streaming API](https://docs.langchain.com/langsmith/streaming#join-and-stream)、[流缓存配置](https://docs.langchain.com/langsmith/env-var-self-hosted#resumable-stream-ttl-seconds)。

取消默认动作 `interrupt` 保留 run 和 checkpoint；`rollback` 删除该 run 及其 checkpoint、恢复此前 thread 状态。后者不适合作为需要保留历史的默认取消，文档也不能证明外部写入随之撤销。运行中的工具仍须处理结果是否已发生的不确定性。[Cancel a run](https://docs.langchain.com/langsmith/cancel-run)、[Double texting](https://docs.langchain.com/langsmith/double-texting)。

### 并发、部署与版本

同一 thread 同时最多执行一个 run；新输入可排队、拒绝、打断或回滚。此机制避免同线程并行执行，**不判断多人谁有权决定，也不解决不同 thread 同改课程版本**。worker 的运行并发与 API 请求并发分别扩展；渲染、知识访问等阻塞操作不应堵住异步事件循环。[执行生命周期](https://docs.langchain.com/langsmith/agent-server#run-execution-lifecycle)、[扩容](https://docs.langchain.com/langsmith/agent-server-scale)。

生产 Agent Server 与 OSS LangGraph 的部署前提不同。Standalone 无控制平面，但需 PostgreSQL、Redis 及 LangSmith license；当前官方推荐 Kubernetes／维护中的 Helm chart 为生产路径，Docker／Compose 示例用于开发测试，禁止依赖 scale-to-zero 承载该长期任务服务。Cloud、Hybrid、完整自托管另有不同计划和基础设施条件，未核实本项目拥有哪种许可。[部署选择](https://docs.langchain.com/langsmith/deployment)、[Standalone](https://docs.langchain.com/langsmith/deploy-standalone-server)。

`langgraph dev` 使用内存与本地保存，`langgraph up` 用 PostgreSQL／Redis 验证接近生产的运行。跑通 dev 不能证明多进程生产恢复。[本地开发与测试](https://docs.langchain.com/langsmith/local-dev-testing)。身份系统仍由外部产品负责；服务器提供 `@auth.authenticate` 与 `@auth.on` 对接验证及资源过滤，自托管没有默认认证，不能只靠 thread ID 隔离学校。[Auth](https://docs.langchain.com/langsmith/auth)。

旧 thread 恢复时运行**当前部署的图**，并不自动锁住开始时代码。删除暂停节点、收紧 state 字段、改变 task／interrupt 顺序会影响恢复；教学行为版本需要显式保留，新增字段兼容旧 state，破坏性更新前检查待恢复任务。[Backward compatibility](https://docs.langchain.com/oss/python/langgraph/backward-compatibility)。

## 对本项目的推论与建议

沿用[已定的阶段内模型行动循环](execution-structure-design.md#阶段内模型怎样行动)：LangChain 承担模型与工具接口，LangGraph 保存有价值的工作及必要等待边界，Agent Server 承担 threads／runs、队列、流式和取消。每种能力的教学规则、上下文可见范围和完成条件仍由本仓库实现；无需按 Grade／Unit／Lesson 建自治 Agent，也不以“已有 middleware”替代教学设计。

一个教学任务可跨多个 run，等待教师时释放计算。先保存可审阅对象，再发出等待；真实回应由外部身份进入，应用核对请求、对象版本、有效范围和去重，保存采用动作后恢复。对已有有效授权直接使用。`request_human`、超时及服务器 `interrupted` 状态本身都不证明有人实际回应；取消和教学等待也不能只凭该状态字区分。

产物、检查和人类决定以稳定引用及版本相互关联，内容存储保持可回读；checkpoint 保存其引用及工作状态。工具写入使用稳定操作身份并能检查先前结果。不要把 Server 队列的调度语义扩展为模型计费、文件写入、内容提升或教师决定的端到端 exactly-once 保证。

为保留审计，普通取消优先采用保留记录的动作，并阻止旧在途结果成为当前交付。恢复界面以持久状态、待答请求和产物为准，SSE 只承担进度投影。针对同一课程版本的不同任务，在产物采用处核对预期版本；不另造覆盖 Server 的通用会话队列。

首次运行原型可显式采用 `sync` 检验昂贵工作和真实等待的保存；保留一个简单的同线程并发策略，并用具体修改需求核对是否应排队或打断。预算按教学任务累计，Server 的超时、重试、run 次数不能自动重置它。以上是候选起点，不是所有生产场景的已定配置。

## 最有价值的三个故障窗口

| 验证对象 | 有界注入 | 必须取得的证据 |
| --- | --- | --- |
| 真实回应已接收，恢复尚未可靠启动 | 显示同一草稿，接收真实用户回应；在记录动作／创建 resume run 两侧中止服务，再重送同一事件，并发送旧版事件 | 不丢决定、不重复解释成另一个动作、不伪造贡献；已有工作被复用，旧回应不能放行新内容。先用显式测试事件检验程序语义；真实参与另记 |
| 产物已写，checkpoint 或取消尚未落定 | 写入一份版本化材料后终止 worker；恢复时核对文件，再让旧调用在取消后迟到 | 内容可回读、重复操作可识别、检查仍对应该版本；取消的结果不提升为当前交付，调用消耗不清零 |
| 教师等待跨部署更新并伴随断连 | 停在真实待答状态；部署兼容新增字段／节点别名，再用旧版本对象恢复；对破坏性更新另测显式拒绝；断连超过流缓存窗口 | 恢复原展示对象和行为约定，兼容失败明确可见；无需完整 token 重放也能重建任务与待答状态。不能用 assistant 配置版本代替代码兼容证明 |

这三个窗口决定主执行结构能否兑现，比继续精修例题或遍历所有服务器功能更有价值。框架版本、SDK、模型适配器、数据库和镜像需在原型开始前固定；当前未声称任何窗口已通过。

## 补充证据与应谨慎的假设

| 主题 | 当前一手依据与具体限制 |
| --- | --- |
| Redis 与流缓存 | [Data plane](https://docs.langchain.com/langsmith/data-plane#redis) 概览写不保存事件；[环境变量](https://docs.langchain.com/langsmith/env-var-self-hosted#resumable-stream-ttl-seconds) 明确可恢复流暂存输出。按配置的具体描述设计，不能保证 Redis 永远不含内容或流能永久回放；待选定版本复验 |
| 观察服务与执行部署 | [Deployment](https://docs.langchain.com/langsmith/deployment) 将 Agent 运行位置与 LangSmith 观察／评测位置分开；[Data plane](https://docs.langchain.com/langsmith/data-plane#langsmith-tracing) 列出 Cloud tracing 必需、Hybrid／自托管可关闭。不能把关闭 tracing 等同于关闭许可校验和用量遥测；本次没有启用或上传 |
| 恢复与回放 | [Checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers#replay) 说明旧 checkpoint 之后的模型、API 和 interrupt 会重执行。回放是一项新的工作，不直接沿用后继内容的旧批准或检查 |
| 版本与业务兼容 | [兼容指南](https://docs.langchain.com/oss/python/langgraph/backward-compatibility#business-compatibility) 的行为版本只在应用实际分支时有效；记录版本号本身不能固定逻辑。必须保留对应旧规则和恢复路径 |
| 可行性范围 | 官方资料支持该运行架构方向；本仓库真实实验仍是本地循环，没有 Server HITL、生产部署或并发结果。本研究不证明教学质量、学校使用效果、容量、价格或本项目许可资格 |
