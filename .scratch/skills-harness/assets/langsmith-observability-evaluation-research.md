# LangSmith：教学执行观察、评测与人类参与的边界

查阅日期：2026-09-15。以下链接均为本日访问的 LangChain 官方在线文档，可能继续更新；未锁定或实测 LangSmith SDK／服务版本。关联[运行架构研究票](../issues/11-agent-server-stack-research.md)、[既有人类参与设计](hitl-design.md)及[质量验证](../issues/05-capability-validation.md)。本次仅研究并提出候选，不启用 tracing、创建云资源或上传现有实验记录。

**项目判断：LangSmith 应纳入架构，用于解释运行、比较改动和组织质量评阅；真实人类决定、当前产物版本及运行恢复仍由业务执行链承载。** 它能帮助定位 Gemini 为什么反复修改、哪些检查有误，不能仅凭一个成功 trace 或较高评分证明数学教学包可用。

后续证据：[SDK 本地发送实测](cfu-durable-prototype-results.md#agent-server-与-langsmith-分别测到了哪一层) 已核对固定运行的关联、选定字段过滤和目标返回 503 时的业务完成。接收方为本机记录器，不是 LangSmith 云端／自托管后端；下文的数据集、评测及平台行为仍属官方研究，未取得服务实测。

## 官方事实

### 运行与观察是不同职责

LangSmith Observability 可观察 LangChain／LangGraph，也支持其他框架；Deployment 是另外的 agent 托管能力，可选择仅使用观察与评测而不托管 agent。Deployment 各拓扑使用 Agent Server 运行时；本地部署 Agent Server 与自托管整个 LangSmith 平台是两件事。[平台选项](https://docs.langchain.com/langsmith/platform-setup)、[Deployment](https://docs.langchain.com/langsmith/deployment)

| 对象 | 文档含义 | 本项目不能据此推定的事 |
| --- | --- | --- |
| LangSmith run | 一次模型、工具或其他工作单元，相当于 span | 不等于一次完整课程任务或 Agent Server run |
| trace | 一次操作中有父子关系的 runs | trace 成功不等于教学检查通过 |
| LangSmith thread | 用 `thread_id`／`session_id` metadata 关联多轮 traces | 不提供业务状态或恢复点；官方示例另外存储对话历史 |
| Agent Server 持久数据 | checkpoint、thread metadata、assistant 等 | 不因记录了产物引用便自动保存实际文件 |

来源：[观察概念](https://docs.langchain.com/langsmith/observability-concepts)、[关联 threads](https://docs.langchain.com/langsmith/threads)、[Agent Server 运行与持久化](https://docs.langchain.com/langsmith/agent-server)。最后一列为依据这些职责作出的项目边界判断。关联 metadata 需传到子 runs，官方特别提醒漏传会影响 thread 筛选和用量汇总。

现有 `ChatGoogleGenerativeAI` 适配器有 LangSmith 自动 tracing 入口。通用 LLM trace 的模型识别、token／成本展示依赖 provider、model name 和 usage metadata；接入文档不保证本项目 Gemini 具体版本的统计已完整，也不代表展示金额就是供应商账单。[Gemini 集成](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai)、[LLM trace 字段](https://docs.langchain.com/langsmith/log-llm-trace)

### 评测、版本比较与人工标注

Dataset 保存 examples：输入、可选参考输出和 metadata。参考输出供 evaluator 使用，不传给被测应用。Experiment 记录某一应用版本在数据集上的输出、评分及轨迹；同一数据集可比较不同配置。数据集内容变化会形成版本。[评测概念](https://docs.langchain.com/langsmith/evaluation-concepts)、[实验比较](https://docs.langchain.com/langsmith/compare-experiment-results)

Offline 指对准备好的案例评价，**不意味着数据留在本机或不联网**；online 对生产 runs／threads 评价，可筛选、采样，通常没有参考答案。Thread 级评测会在满足空闲条件后观察历史；空闲不是业务完成，教师尚未回答也可能暂时无活动。[在线评测](https://docs.langchain.com/langsmith/online-evaluations-llm-as-judge)。后一判断来自本项目长期等待语义。

Annotation queues 收集 run 的人工评分，支持单项和成对比较、多评阅者、预约与完成状态；评阅者不能看到别人评分，但可看到评论。因此多评阅者设置本身不保证本项目所说的匿名评阅／输入隔离，更不保证教师作出了课程决定。[人工标注队列](https://docs.langchain.com/langsmith/annotation-queues)

LLM judge 按评分提示评价；官方要求复核评分、调校提示，可加入已判分示例。平台模板是起点，需自行提供数学正确性、任务认知要求、时间可行性等判据。[评测方法](https://docs.langchain.com/langsmith/evaluation-concepts#llm-as-judge)、[配置 judge](https://docs.langchain.com/langsmith/llm-as-judge)。上游同样要求按实际文件逐条评分、跳过不适用条款，并与教育实践者校准，不能把最终聊天中的自述当成材料证据。[上游评测说明](../../../k12-teacher-skills/evals/README.md)

Prompt 管理支持 commits、差异及环境标签；标签可重新指向别的 commit。因此长程任务应记录实际使用的 commit／内容指纹，恢复时不能仅凭可变的 `production` 标签推定规则未变。[Prompt 版本管理](https://docs.langchain.com/langsmith/manage-prompts)

### 数据去向与部署前提

Cloud 将观察和评测数据放在 LangChain 云端。Hybrid 可以只将 Agent Server 放在自己的环境，而 traces 仍发往 SaaS；Self-hosted 和 BYOC LangSmith 当前为 Enterprise，不能因 LangGraph 开源就推定整个平台免费自托管。[平台拓扑及套餐条件](https://docs.langchain.com/langsmith/platform-setup)、[Self-hosted 条件](https://docs.langchain.com/langsmith/self-hosted)

本地 `langgraph dev/up` 可设置 `LANGSMITH_TRACING=false` 关闭 tracing，CLI analytics 另有开关；许可／用量校验又是另一条连接。自托管 LangSmith 非离线模式要求发出许可和计费用量遥测，完全离线另需许可；Engine 有额外内容外发路径，本项目无需因接入观察就启用它。[本地数据行为](https://docs.langchain.com/langsmith/data-storage-and-privacy)、[自托管 egress 条件](https://docs.langchain.com/langsmith/self-host-egress)

SDK 能按请求关闭 tracing，或在发送前隐藏／转换 inputs、outputs、metadata；这些是独立选项，隐藏正文不会自动隐藏 metadata。界面筛选是事后查看，不能替代发送前的数据选择。[条件 tracing](https://docs.langchain.com/langsmith/trace-without-env-vars)、[发送前脱敏](https://docs.langchain.com/langsmith/mask-inputs-outputs)。Trace 有保留期；加入 dataset 的内容另行持久保存，不能把 trace 删除理解为相关数据集副本也已删除。[保留语义](https://docs.langchain.com/langsmith/observability-concepts#data-retention)

## 项目建议：首版只接入会帮助当前决定的部分

1. **保留一条可解释的执行轨迹。** 关联产品任务、Agent Server thread／run、产物版本、实际 Context 清单、CCSS／图数据版本及检查器版本。按一次执行记录模型、知识查询、产物写入、检查和修订；真实待答请求与回应只记录必要关联，不把等待时间算成模型处理耗时。完整产物、人类事件与决定保留在业务存储，LangSmith 保存允许的观察副本或引用。
2. **把“正在生成的检查”与“评价执行器”分开。** 当前材料的数学／排版检查应及时回到模型修订循环；LangSmith 保存检查证据并离线比较循环效果。Online judge 先用于发现问题和评测回流，不直接恢复人类等待、改写当前课程或自动发布。需要自动触发回修时，仍须经版本、权限和预算校验。
3. **先形成少量可核对的回归案例。** 使用现有实验中的实际失败、修复及检查误报，分别记录检查结果和裁定；不能把模型意见自动升级为参考答案。区分课程蓝图、课时材料、跨层修订和真实参与，各看相关指标。冻结案例版本、模型配置、规则和 evaluator；比较质量、资源耗用、修订后退化及未解决项，不汇成一个“教学总分”。
4. **人类参与回到产品流程。** 教师确认焦点、亲做任务、接受材料都是有对象和版本的真实事件，由外部 Web 输入，经 Harness 核验后恢复。Annotation queue 适合专家抽查和 judge 校准；队列 Done 不代替教师同意。将专家评分作为另一类证据关联产物，保持[五项能力自己的完成语义](hitl-design.md)。
5. **观察接入不扩大原创输入。** 初期沿用本地版本化规则，暂不迁移到远程 Prompt Hub。后续即使使用实验比较，原创生成仍只得到允许的输入；参考材料与评阅意见的可见范围由实验设计控制，平台不会自动提供严格双盲。

## 尚未实测及下一次最小验证

已完成的是官方资料核查，现有 Gemini 实验仍未接入 LangSmith。下一次运行原型只需围绕主链验证：一次真实等待／恢复后，跨轮 traces、版本和人类事件能否准确关联；一次检查反馈能否定位被改文件；关闭或失去 tracing 时，业务执行与必要证据是否仍完整；选择性发送是否真的排除不允许的 Context、图片、工具结果和 metadata；固定数据集重跑是否能区分有效修复与误报。

锁定 SDK、适配器和服务版本后再核对这些行为。实际学校数据的发送范围、存储区域及保留约定属于外部产品数据政策，本仓库负责兑现可配置的数据选择和关联边界；本轮不以此暂停其他架构工作，也不上传历史记录来证明集成。
