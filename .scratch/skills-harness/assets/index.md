# 规划材料索引

整理日期：2026-09-15。所属地图：[课程与教学设计 Harness 架构地图](../map.md)。

本页是 `assets/` 的统一入口及任务读取路由。项目目标、实施路线与原则统一以 [README](../../../README.md) 为准；下文区分候选设计、上游详细参考和框架研究。研究完成不表示生成能力或教学效果已验证。

## 按任务读取

先读 [README](../../../README.md) 的目标、实施路线、设计与协作原则及职责边界。本轮架构已收敛，先读 [架构与可行性结论](architecture-conclusion.md)，具体状态与采用范围从 [架构地图](../map.md) 和对应决策票取得；本页负责选择材料，不另行定义项目目标。

分析、实现或评审时，按下表读取全部适用分支。读取详细分析后，沿其来源链接核对相关上游原文；概览不能替代流程、案例、适用条件和验证依据。

| 当前任务 | 必读材料 | 应带回当前工作的内容 |
| --- | --- | --- |
| 实现前用户交互与原型复核 | [交互基准与维护约定](../../math-harness-delivery/prototype-baseline.md)、[全年到教学的交互方案](../../math-harness-delivery/teaching-workspace.shape.md)、[教学工作区样本](../../math-harness-delivery/prototypes/teaching-workspace.prototype.html)、[完整依赖图](../../math-harness-delivery/dependencies.md)，以及本表对应能力的详细流程 | 课程层级导航与内容旁的教学任务、各能力自己的参与条件、旧开发原型的证据定位；现行 HTML 随用户指令定稿保存，按文件化阶段实施，内容历史后置，不把模拟当作真实运行 |
| 整体能力与执行架构 | [架构结论](architecture-conclusion.md)、[能力范围与推进路线分析](harness-scope-and-priority.md)、[四项源码盘点](skill-capabilities.md)、[执行与 HITL 参考](execution-contract-draft.md)、[执行结构分析](execution-structure-design.md)、[采用决定](../issues/03-execution-structure.md) 及 [主执行与调用设计](main-execution-design.md) | 各项能力的实际工作、输入产物、完成条件、现有机制、阶段边界、实际版本交接和改变需要的证据 |
| 课程体系与跨层修订 | [课程能力决定](../issues/12-curriculum-design.md#resolution课程设计的能力约定与双向交接2026-09-14)、[课程体系设计](curriculum-design-capability.md)、[IM 方法论补强](im-design-methodology-transfer.md)、[本地图用法](learning-commons-integration.md)、[Context 设计](context-and-llm-design.md) | 四层职责、双向交接、活动目的、表征与练习进程、证据及变更影响 |
| 数学课时与材料设计 | [数学教案详细流程](lesson-creation-execution-design.md)、[教案创建原 Skill](../../../k12-teacher-skills/plugin/skills/k12-lesson-plan-creation/SKILL.md) 及其中适用参考 | 知识依据、实际任务、教师交互、草稿延续、材料生成、检查与修订 |
| 数学图形与可视材料 | [数学可视材料候选](math-visual-materials-design.md)、[材料生成详细流程](lesson-creation-execution-design.md#材料源检查与成套交付)、[上游数学参考](../../../k12-teacher-skills/plugin/skills/k12-lesson-plan-creation/references/math.md)、[上游输出规范](../../../k12-teacher-skills/plugin/skills/k12-lesson-plan-creation/references/output.md) 及 [实际图形质量证据](../experiments/grade8-linear-functions/quality-review.md) | 教学用途、关键图及早试做、可编辑生成源、多轮精修、师生可见信息、实际渲染与版本检查；模块划分仍为候选 |
| 教学适配 | [适配详细分析](execution-contract-draft.md#已有课时的差异化教学适配)、[适配原 Skill](../../../k12-teacher-skills/plugin/skills/k12-lesson-differentiation/SKILL.md) 及适用学科参考 | 原课与目标、学习需要、支架与拓展、共同任务、产物及自身交互和完成条件 |
| 教师备课 | [备课详细分析](execution-contract-draft.md#备课)、[备课原 Skill](../../../k12-teacher-skills/plugin/skills/k12-lesson-prep/SKILL.md) 及其 rubric | 实际任务、模型试做、教师贡献、信息呈现顺序、讨论与便签、停止和例外 |
| 理解度检查 | [CFU 详细流程](cfu-execution-design.md)、[CFU 原 Skill](../../../k12-teacher-skills/plugin/skills/k12-check-for-understanding/SKILL.md) 及其构建和验证参考 | 焦点、错误映射、题目构建、独立读题、实际产物检查、回应解释和修复 |
| Context、LLM 或工具编排 | [Context 与 LLM 设计](context-and-llm-design.md)，特别是 [整体与单元两类任务输入](context-and-llm-design.md#整体课程方案与单元内课程设计的输入)、[执行结构的装配与状态](execution-structure-design.md)、[知识使用约定](../../../docs/references/knowledge-consumption-contract.md)，以及本表中所涉及能力的详细流程 | 每阶段的实际内容、初始必备／按需读取／生成内容、上层交接、资源路径、可见范围、来源和版本延续、模型调用与检查 |
| 场景细分、控制粒度与简化 | [强模型下的控制粒度研究](harness-control-granularity-research.md)、[执行结构比较](execution-structure-design.md#先比较执行方式)、[质量验证](../issues/05-capability-validation.md) 及所涉能力的原流程 | 区分评测样本、教学规则与生产分支；比较有充分 Context 和必要运行承载的简洁循环，说明新增控制的依据、代价及去留条件 |
| 修订、HITL 与停止行为 | [执行结构决定](../issues/03-execution-structure.md)、[状态、修订与停止分析](execution-structure-design.md)、[人类参与决定](../issues/07-hitl-protocol.md)、[HITL 详细设计](hitl-design.md)、[主执行中的介入位置](main-execution-design.md#hitl-究竟介入哪里) 及对应能力的详细流程 | 已采用的结构与交互边界、能力特有的回应与结束、已有授权、对象版本、多人规则、检查复用和预算停止；区分设计基线与真实验证 |
| 课程修订状态原型与接口表达 | [自然语言到执行链的逐步讲解](curriculum-revision-execution-walkthrough.md)、[原型及运行记录](curriculum-state-prototype-notes.md)、[交互演示](../prototypes/curriculum-state.prototype.html)、[原型票](../issues/14-curriculum-state-prototype.md) | 入口、Prompt／Context、模型与程序职责、按钮对应的真实／模拟动作；补查依据与决定适用性，模拟不当作 LLM 或服务器恢复证据 |
| 模型与产物工具实现 | [模型、知识与产物实现选择](model-knowledge-artifact-design.md)、[采用决定](../issues/04-runtime-adapters.md)及本表对应能力、Context、知识与运行分支 | 原生模型循环、实际资源装配、工具校验、最终材料检查和源码复用边界；不将原型硬编码搬进生产 |
| 知识关系与本地查询 | [知识使用约定](../../../docs/references/knowledge-consumption-contract.md)、[本地 Learning Commons 图的教学设计用法](learning-commons-integration.md)、[证据基线](../../../docs/references/reference-baseline.json) 及其来源 | 框架与身份、节点和边、非树引用、方向及角色、来源与推断、版本适用范围 |
| 其他学科或学科规则变化 | [完整学科差异分析](lesson-creation-subject-flows.md) 及对应上游学科参考 | 各学科自己的任务、材料、证据、交互和检查，避免跨学科规则串用 |
| 暂停恢复与服务运行 | [完整运行时专项](../issues/11-agent-server-stack-research.md)、[LangGraph／Agent Server 研究](langgraph-agent-server-research.md)、[LangSmith 研究](langsmith-observability-evaluation-research.md)、[持久运行实测](cfu-durable-prototype-results.md)、[主执行与调用设计](main-execution-design.md)；CFU 专属顺序另读 [局部研究](cfu-runtime-research.md) | 框架事实、应用责任、部署与许可条件、实际验证范围；持久状态、产物、人类事件与观察分别落实 |
| 能力质量与比较评测 | [交付验证路线](validation-and-release-route.md)、[质量验证决策票](../issues/05-capability-validation.md)、[上游评测说明](../../../k12-teacher-skills/evals/README.md)、[LangSmith 评测与人工标注](langsmith-observability-evaluation-research.md) 及所评能力的流程与 rubric | 可比条件、真实内容和交互证据、规则适用性，以及替代机制的效果验证；人工标注不替代产品 HITL |
| 八年级线性函数的隔离原创实验 | [实验讨论方案](grade8-linear-functions-validation-design.md)、[独立官方标准](grade8-linear-functions-standards.md)、[具体输入与评价准备](../experiments/grade8-linear-functions/README.md) 及 [质量验证票](../issues/05-capability-validation.md) | 组织者核对两层范围、允许资源、冻结与匿名评阅；原创只加载允许的任务／知识文件和实际交接，不能沿开发路由加载 IM 及其派生内容 |

进入实现或评审时，还需读取 [五项能力的交付规格](../../math-harness-delivery/spec.md)、[实现路线与任务](../../math-harness-delivery/README.md) 中对应实现票和关联决定；[逐票规模与依赖复核](../../math-harness-delivery/ticket-sizing-review.md) 解释当前拆分与待收口工作包。候选研究提供依据，不能自动替代已确定的验收要求。规格和实现票已经形成，实际实施与质量验收尚未开始。

## 当前设计与研究

当前采用 [文件化内容格式](../../math-harness-delivery/content-system-design.md)。涉及内容保存、公式／表格／图片、修改、检查、渲染或制作前后端接合时，须与本表相关分支一起读取。按用户最新范围，JSON 保存当前工作源，正文允许 Markdown／LaTeX，图件另存；暂不上数据库，不建设内容版本历史，也不再以外部 authoring 为参考。该阶段约定覆盖旧设计中首版存储的时点，完整运行方向与教学质量要求保留；最小字段及实际往返仍待实现验证。

运行继续采用 **LangGraph＋Agent Server dev**，直接复用 thread／run、本地 checkpoint、流式、取消和真实中断恢复；不自建后台协程调度、文件运行状态机或 SSE 服务。不上业务数据库及不做内容历史，不表示停用框架状态保存；此前停用 Agent Server 的候选已撤回，生产部署专项仍后置。

| 材料 | 已完成的工作 | 使用边界 |
| --- | --- | --- |
| [数学课程与教学设计 Harness：架构与可行性结论](architecture-conclusion.md) | 汇总采用结构、职责、首个实现顺序及规格交接 | 本轮 Wayfinder 已收敛；生产、完整单元及 Skills 质量尚未通过，不代表已证明最优 |
| [模型、知识与产物工具的实现选择](model-knowledge-artifact-design.md) | 原生循环、实际运行资源、browse 映射、工具职责与上游渲染源码复用 | 技术选择及源码／官方依据；真实模型与原生服务合并、全部模型与生产恢复仍待验收 |
| [从架构可行到教学交付的验证路线](validation-and-release-route.md) | 完整单元、五项能力、Skills／IM 分开比较、运行和教师使用门槛；先质量、随任务记录消耗、后优化预算 | 方法与交接已定；预算优化不作首版前置，不重写原始失败或宣称模型／教师质量已通过 |
| [CFU 持久执行：真实回应、故障恢复与服务接口实测](cfu-durable-prototype-results.md) | 13 项固定事件故障探针、一次真实原型焦点回应及跨进程恢复、Agent Server dev 重启、LangSmith SDK 本地发送与 503 解耦 | 固定模型／材料，完整教学检查未实现；不是生产恢复、LangSmith 云端集成、任意自然语言理解或学校试用证据 |
| [教学 Harness 的主执行链、调用与运行承载](main-execution-design.md) | 将自然语言任务、实际版本与 Context、模型／工具、检查修订、五项 HITL 位置和框架责任连成主链 | 调用语义已由关联决定收敛，含六项操作、回执／采纳／续作、范围化结果及静态示例；正式 Schema、生产实现和任意自然语言质量尚未验证 |
| [八年级实验的输入、运行与验证](../experiments/grade8-linear-functions/README.md) | 完整年级 CCSS／实践输入、共同规范、两类任务书、39 条 rubric 取用；真实蓝图与三课、两轮材料修订、像素读题及一次跨层压缩 | 有限取样链已走完；材料可读性和压缩可行性仍有未通过项。尚未达到 Skills；三课不代替完整单元，原创全单元冻结前不看对应 IM |
| [真实 Gemini 运行与修订记录](../experiments/grade8-linear-functions/runtime-notes.md) | LangChain 适配器、本地 browse 语义工具、有界循环、实际版本交接、预算失败、独立读题、图形／渲染及问题反馈 | 记录失败与改动；12／24 次是探索预算，非生产结论；未验证完整服务、真实人类恢复或课堂效果 |
| [实际材料质量裁定](../experiments/grade8-linear-functions/quality-review.md) | 按 E1–E10 核对原稿、修订稿、视觉模型误报与真实缺陷、18→14 跨层修订及后续验证对象 | 模型自报与检查轨迹分别处理；零解析错误、课时算术和文件同步不代表教学质量通过 |
| [数学图形与可视材料：从教学用途到可修订产物](math-visual-materials-design.md) | 评估单列专业模块；用途说明、关键图早期试做、数学描述与绘制、局部精修、受众版本和教学包集成 | 已后置，非当前下一项任务；未新增生产模块或运行对照。按主线依赖重新进入时先针对函数图 |
| [八年级线性函数：独立课程设计与后置比较的讨论方案](grade8-linear-functions-validation-design.md) | 展开用户候选：全年蓝图与完整单元、实际模型循环、参考隔离、版本冻结、匿名评阅和后续改进；识别 LC 与原 Skill 的间接 IM 入口 | 早期实验讨论，非原创生成提示包；当前范围与门槛读交付验证路线，实际运行另有记录；未读取对应 IM 或声称严格双盲 |
| [八年级线性函数：官方标准与候选验证边界](grade8-linear-functions-standards.md) | 只用独立官方标准核查 8.F、相关 8.EE 及此前目标；区分标准事实、先备假设和候选范围 | 未查 IM；标准不规定课程顺序，不证明实际学生掌握，也未固定 Unit 4 编号或课时数 |
| [独立课程与教学设计 Harness：能力范围与推进路线](harness-scope-and-priority.md) | 五类能力、外部前提、独立设计与 IM 对照策略、课程到课时的主线、可靠性和贯通验证建议 | 保留早期范围与路线分析；当前采用结论读总体架构决定，生成器尚未实现 |
| [本地 Learning Commons 图的教学设计用法](learning-commons-integration.md) | 阅读已有研究并只读查询 v1.11.0；补充会话插件及 [本地 Studio API 实测](learning-commons-integration.md#本地-studio-http-api-实测2026-09-15)，确认文档来源、标准／LC／进阶查询与来源身份 | 不建设数据本地化；HTTP 样本与后续有限工具接入各有记录，不证明生产接入、图自动生成课程或全部目标有同样丰富的关系 |
| [Context 与 LLM 使用方法：设计起点](context-and-llm-design.md) | 从原 Skill 流程展开课程到课时的阶段输入、模型／工具工作、真实资源装配、可见范围及版本延续 | 具体结构采用见执行决定；完整接口、模型配置与替代效果仍未验证 |
| [课程与教学设计的执行结构、状态与修订](execution-structure-design.md) | 比较三类结构，明确阶段内行动、实际资源、版本与检查、人类等待、跨层回修和停止；含删课轨迹及十三项反例 | 采用范围见执行决定；本文为源码与静态分析，后续状态原型证据单列；不固定全部能力的完成条件 |
| [五项教学能力的人类参与、回应与恢复](hitl-design.md) | 逐项定义请求内容、有效回应及结束，区分授权／接受／贡献；明确复合指令、版本适用、重复与多人冲突，补齐 prep 内容解释分支及二十项场景 | 采用范围见人类参与决定；CFU 有限恢复已有独立实测，任意自然语言理解、其余能力和学校教师使用仍待验证 |
| [课程修订状态原型：运行记录与接口启示](curriculum-state-prototype-notes.md) | 单文件演示；Node 与浏览器均走完 11 个场景、65 次动作；补充自由操作、截图与用户反馈，明确场景的现实情况及参与者 | 检查和回应为模拟，页面走查已完成；开发者走查台不等于教师界面，不能据此声称教学质量或服务器可靠性已验证 |
| [从一句修改需求到课程修订：原型所代表的执行链](curriculum-revision-execution-walkthrough.md) | 解释原型所在环节、自然语言入口、Prompt 与实际 Context、模型／工具循环、程序控制及九个按钮的代码对应 | 真实运行链为设计展开，只有 HTML 控制逻辑已运行；不把一个按钮规定为一个模型调用或图节点，不将示例 Prompt 当完整资源 |
| [强模型下的 Harness 控制粒度](harness-control-granularity-research.md) | 核对六项一手资料和本地模拟逻辑；补入公平的简洁 Agent 基线，区分必要职责与可延后细化，提出有限对照与逐项增减方法 | 尚无真实模型对照；案例数量不能证明分支必要，不以简化之名删除原 Skills 教学目的，不把外部开发实验当教学证据 |
| [数学课程体系设计：IM 参考研究与 Harness 能力候选](curriculum-design-capability.md) | 核对官方 Narrative、任务与评测；展开四层责任、双向交接、关键任务试做循环和八项静态反例 | 能力层采用范围见决策票，具体编排仍为候选；研究案例不是首个实施主题，未运行生成或内容评测 |
| [IM 方法论研究对教学 Harness 的补强](im-design-methodology-transfer.md) | 完整阅读指定长文并核对十个官方页面；补充活动目的、表征语义、讨论预案、支持、练习、互动机制及数学内部差异 | 官方事实、长文推论和本项目建议分开；不迁移外部项目对象及 Generation 约束，未证明更优执行效果 |

稳定的知识消费责任另见 [知识使用约定](../../../docs/references/knowledge-consumption-contract.md)；[证据基线](../../../docs/references/reference-baseline.json) 保存八份外部研究文件指纹、数据投影元数据和七项查询观察。资料转用与固化范围记录在 [IM 方法论与本地知识研究有哪些应进入 Harness 设计](../issues/13-reference-research-transfer.md)。

这些材料分别支撑已收敛的 [课程能力](../issues/12-curriculum-design.md)、[执行流程](../issues/03-execution-structure.md)、[人类参与](../issues/07-hitl-protocol.md)、[调用接口](../issues/02-execution-interface.md)、[模型与工具](../issues/04-runtime-adapters.md)和[验证路线](../issues/05-capability-validation.md)。两类原型保留各自实际证明范围；[总体架构决定](../issues/06-architecture-conclusion.md)已交接到规格阶段。决策解决不表示产品能力、运行机制或教学效果已通过验收。

## 上游能力、详细流程与学科参考

以下以固定上游 `281eb8d41fe2837d911541c9bbb870b58add804c` 为依据。**详细流程是重要设计起点，完整保留；本项目约束另行确定。** 其中的“必须”、固定数量与完成条件描述原 Skill 或早期候选。改变流程须说明教学目的如何保留，并用可比较的效果证据验证。

| 材料 | 适合查阅的问题 | 使用边界 |
| --- | --- | --- |
| [四项教学 Skills：执行能力源码盘点](skill-capabilities.md) | 原有四项能力具体做什么，依赖哪些参考、工具与评分要求 | 静态源码事实；不限制新增能力，也不证明执行质量 |
| [上游四项 Skills 的执行与 HITL 参考](execution-contract-draft.md) | 各项能力不同的教学动作、交互、材料、检查和修订 | 不统一各项完成条件；保留原流程及候选分析，不自动视为项目契约 |
| [上游数学教案创建的执行参考](lesson-creation-execution-design.md) | 数学课时设计中的任务、表征、解法、材料与交互案例 | 固定 IM 形式和逐条 rubric 移植不再是产品约束 |
| [上游教案创建的学科差异参考](lesson-creation-subject-flows.md) | ELA、科学、社会研究为何需要分别处理，以及各自的教学依据 | 集中记录、按需引用；不把数学流程推广到其他学科，不将其他学科问题设为数学门槛 |
| [上游理解度检查的执行参考](cfu-execution-design.md) | 焦点选择、实际题目、验证与修订有哪些值得保留的教学工作 | 单项参考；固定题量、HTML 和交互形式可按本项目需要取舍 |

## 框架事实与历史结论

| 材料 | 已完成的工作 | 使用边界 |
| --- | --- | --- |
| [LangChain、LangGraph 与 Agent Server 运行架构研究](langgraph-agent-server-research.md) | 按官方资料核对模型循环、持久中断、会话／运行、流式与取消、并发、认证、部署及版本兼容 | 提供完整运行候选；后续局部实测单列，生产版本与部署保证仍未验证 |
| [LangSmith：教学执行观察、评测与人类参与的边界](langsmith-observability-evaluation-research.md) | 核对 traces、版本化数据集与比较、在线评测、人工标注、数据去向及平台条件 | SDK 本地发送证据单列，平台后端仍未接入。观察 thread 不代替执行状态，人工标注不代替教师决定 |
| [LangGraph 承载 CFU 暂停、恢复与文件验证顺序](cfu-runtime-research.md) | 官方文档中的中断、持久化、重试与外部副作用研究 | 保留局部研究事实；后续锁定版本的原型结果单列，不替代完整运行研究 |

[完整运行架构专项](../issues/11-agent-server-stack-research.md) 已按用户要求在流程分析与有限实验后完成官方研究，并纳入 LangSmith；结论已记录在该票。随后 [持久运行探针](cfu-durable-prototype-results.md) 补入有限控制、开发服务和 SDK 发送证据；生产持久化、部署容量与版本迁移仍待相应验证。

原 [Learning Commons 后端接入研究票](../issues/10-learning-commons-integration-research.md) 保留历史记录；远程权限与材料获取不再是当前架构的前置问题，其旧报告已由本地图使用报告替换。此前由逐条移植及远程材料缺口引出的确认请求已撤回。详细执行分析在一次过度清理后已完整恢复；参考分析的保留与项目约束的采用分别处理。范围变更的正式记录见 [课程体系与教学能力的范围和质量基线是什么](../issues/01-capability-contract.md)。

## 验证边界与后续记录

已经完成源码盘点、官方资料研究与本地只读查询，并运行内存状态原型、有限 Gemini 教学设计循环、实际版本交接、学生单独读题和材料渲染／浏览器走查。两轮实际材料修订、像素读题与一次跨层压缩的结果已记录，包含有效修复、检查误报及未通过项。后续持久探针另取得 SQLite 跨进程恢复、一次真实原型回应、Agent Server dev 正常重启和 LangSmith SDK 本地发送证据。尚未验证完整单元质量、稳定修订效果、生产服务器故障恢复、跨模型基线或课堂效果。没有合作学校／教师试用证据；离线内容比较不能证明学习效果。

本轮 Wayfinder 已基于既有产品交流、源码／官方研究和有限运行证据形成架构结论，并交接为 [规格和实现票](../../math-harness-delivery/README.md)。后续实现继续兑现完整运行专项及验证路线；原质量失败、生产恢复和真实使用未测项不得随地图关闭或规格形成改为通过。

新增研究优先更新已有专题，同时维护本索引和关联决策票。每份材料标明来源、事实与推断、当前适用范围及实际验证程度；地图只索引已解决的决定，未决设计留在子票中。
