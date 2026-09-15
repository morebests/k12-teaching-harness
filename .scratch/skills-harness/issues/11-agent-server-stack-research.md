# LangChain、LangGraph、Agent Server 与 LangSmith 如何共同承载教学 Harness

Type: research
Labels: wayfinder:research
Mode: AFK
Status: resolved
Assignee: li3p
Blocked by: 01, 03, 07

## Question

根据当前官方文档核对 LangChain、LangGraph、Agent Server 与 LangSmith 的职责边界与完整后端方案。覆盖模型与工具循环、上下文、技能资源、执行图、HITL、assistants／threads／runs、后台执行与流式输出、并发与取消、持久化、认证授权对接、部署与运行依赖、版本更新。LangSmith 同时核查 tracing、数据集、离线／在线评测、人工标注、版本比较，以及与产品端人类决定、产物记录的关系。

执行时点：课程体系及各项教学能力的流程分析形成后、开始实现之前。已有流程与 HITL 语义已形成，并取得有限真实模型实验；用户于 2026-09-15 明确将 LangSmith 一并纳入并要求继续，现启动专项，与主执行方案的接口收敛相互校核。

明确框架或服务已经提供什么、Harness 仍要实现什么，避免把 Agent Server 等同于教学执行器，或重新自建它已有的会话与运行机制。核对官方产品名称及生产部署条件，不把开发服务器当作完整生产方案。

形成与长程课程设计、跨层修订及教学任务相关的技术验证场景；原有 Web 产品、Learner Model、身份权限体系、已本地化知识数据和全系统治理仍是外部前提，本仓库只负责必要接入及运行边界。

## Context

- [Skills Harness 实现架构地图](../map.md)
- [完整实现需求与首项建议](../assets/harness-scope-and-priority.md)
- [仓库目标](../../../README.md)

## Comments

### LangSmith 接入配置已提供（2026-09-15）

用户告知 `.env` 已提供 LangSmith Key；已仅核对 `LANGSMITH_API_KEY`、`LANGSMITH_PROJECT`、`LANGSMITH_TRACING` 配置项存在且非空，未读取输出或记录其值。本次未请求 LangSmith 服务，因此凭据有效性、服务权限和真实平台接入仍未验证。后续需要平台验证时使用独立合成样本；已有本地 SDK 实测的证据范围保持不变。当前继续收敛调用接口，不因配置到位扩大实验范围。

### 有限运行验证回填（2026-09-15）

[CFU 持久运行实测](../assets/cfu-durable-prototype-results.md) 已验证 SQLite 的进程退出恢复、一次真实原型回应和 13 项固定事件控制；Agent Server dev 的实际接口和正常重启恢复走通；LangSmith SDK 向本地记录器的发送、字段过滤及 503 解耦走通。生产数据库恢复、部署容量、破坏性升级与 LangSmith 后端／评测尚未实测。研究结论沿用，有限证据进入调用设计，不将其外推到所有能力或生产保证。

### Resolution：复用运行与评测平台，教学语义和内容提交由 Harness 保证（2026-09-15）

已完成 [LangChain／LangGraph／Agent Server 官方研究](../assets/langgraph-agent-server-research.md) 与 [LangSmith 观察和评测研究](../assets/langsmith-observability-evaluation-research.md)，并整合到 [主执行与调用候选](../assets/main-execution-design.md)。按当日官方文档回答本票的框架责任与可行性问题；未锁定生产版本、部署服务或取得真实恢复验证。

1. **可复用的执行能力。** LangChain 的模型／工具循环及 middleware 可作为起点，LangGraph 承载有状态执行与真实中断；当前 Agent Server 属于 LangSmith Deployment，已有 assistants／threads／runs、后台队列、流式、并发与取消入口。无需另造相同会话和队列服务，也不将每条教学规则拆成图节点。
2. **本仓库的实质工作。** 五项能力各自的教学流程、Context 装配与可见范围、规则版本、知识语义、真实人类决定、产物与检查及交付条件仍由 Harness 实现。外部 Web 身份／权限接入框架认证和资源过滤；可信身份、有效授权和课程对象范围不能由模型文本决定。
3. **HITL 与数据一致性。** 中断恢复从节点入口重跑，应用须先保存可复用的展示对象、请求与采纳动作。checkpoint 与 Server 调度不提供跨产物、决定和外部副作用的端到端恰好一次保证。取消优先保留历史，并阻止在途旧结果成为当前交付；同线程并发策略不解决不同任务修改同一课程的冲突。
4. **部署和升级的真实条件。** Standalone 生产需要 PostgreSQL、Redis 与许可等条件，开发服务器不代表生产验证。旧 thread 默认用当前部署代码恢复，必须维护兼容 state、等待节点及行为版本。页面恢复依赖持久任务与产物；流式缓存的窗口不能当作永久运行历史。具体端点默认值及官方文档差异见报告，规格应显式配置。
5. **LangSmith 的位置。** 将模型、工具、Context、产物版本和检查关联到 traces；用冻结数据集和 evaluator 比较质量、修订、消耗与误报，专家标注帮助校准。LangSmith thread 只是观察关联，annotation queue 完成不构成产品 HITL；在线空闲触发也不代表教师已回应或教学完成。实际生成中的检查反馈仍进入模型修订链。
6. **本地运行与数据去向分别决定。** Agent Server 本地运行不意味着 LangSmith traces 留在本地；离线评测指数据集型评测，并非断网。依据外部产品数据政策配置发送范围和保存位置，不因本研究启用 tracing 或上传已有内容。许可、拓扑与用量连接按所选服务核实，不从 OSS 许可推导整个平台部署条件。

**研究结束后的验证交接：**现有 [HITL 审计](../experiments/grade8-linear-functions/hitl-coverage-audit.json) 确认 9 次真实 Gemini 执行均未发请求，且没有回应／恢复入口。因此本票解决“框架怎样承载及本项目还要承担什么”，不解决“实现是否已经兑现”。优先验证三个窗口：回应保存到恢复启动、产物写入到 checkpoint／取消、等待跨代码升级及断连。对应 [运行原型](09-cfu-runtime-prototype.md) 和 [主执行候选](../assets/main-execution-design.md#下一项高价值验证及结束条件) 在开始时锁定版本与结束判据，保留各能力专属差异。观察关联与失败行为随同一切片验证；不新增一轮样例精修或泛化平台功能探索。

本票为 AFK 研究结论，按 Wayfinder 研究例外记录 resolved；[调用接口](02-execution-interface.md)、[质量验证](05-capability-validation.md) 与 [总体架构](06-architecture-conclusion.md) 继续按其证据要求推进，不因本票关闭而自动通过。

### 启动专项并补入 LangSmith（2026-09-15）

按用户本次指令启动。先以官方资料核查可复用能力与应用责任，重点回答长程任务、真实中断恢复、版本化产物、可观察检查及评测如何衔接。当前 Gemini 实验只保存本地记录，没有实际人类请求／恢复，没有接入 LangSmith；研究和设计不冒充这些路径已运行，也不自动启用云端 tracing 或上传现有数据。

### 排期调整

用户明确现阶段重点仍是 Skill 流程分析，完整运行时与 Agent Server 专项留到实现前强化。本票退回未认领；尚未启动该专项研究，没有运行或部署结论。

### 执行结构提供的具体核查对象（2026-09-14）

[执行结构决定](03-execution-structure.md) 提供阶段边界、版本化内容、真实请求、预算停止及产物检查要求。启动专项时核对这些职责如何映射到框架已有的持久化和 Agent Server 的会话／运行，尤其是等待不占用模型循环、结果已产生但记录未提交、取消中的在途调用、旧行为版本恢复与并发修订。checkpoint 不代替产物一致性或教学状态校验；本注记没有提前启动专项或锁定节点 API。

### HITL 对恢复与并发的补充（2026-09-14）

[HITL 语义](../assets/hitl-design.md#回应关联与实际处理) 要求将“接收真实事件、采纳决定、启动后续工作”之间的失败窗口具体化；同一事件去重不能承诺模型调用或工具副作用恰好一次，也不能代替外部多人决定规则。恢复已保存动作不重新解释为另一方案；取消后在途结果不得再成为当前交付。启动本票时核查框架已提供部分及应用责任，不自行先造一套会话或队列服务。
