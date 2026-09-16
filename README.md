# K-12 Teaching Harness

本仓库的目标是：**建设一个数学优先、能够设计独立课程体系并可靠执行教学任务的 Harness，交付可由 Web 产品后端调用的教学设计能力。**

它使用本地 Learning Commons、课程目标和学习者上下文，完成课程体系、课时与材料、教学适配、教师备课和理解度检查。对上游 Skills 已有的四项能力，目标是达到并争取超过其教学执行水平；新增课程体系设计能力将各层目标、学习进程、实际任务和评测贯通起来。

本 README 是本项目**目标、实施路线、设计与协作原则、职责范围**的权威入口。项目任务先读本页，再按 [文档读取路径](#文档读取路径) 进入当前决定、规格和详细参考。本轮 wayfinder 已形成 [架构与可行性结论](.scratch/skills-harness/assets/architecture-conclusion.md)，并已交接为 [五项能力的交付规格](.scratch/math-harness-delivery/spec.md) 和 [实现路线与任务](.scratch/math-harness-delivery/README.md)。首个有限课程任务已实现并完成真实模型检查闭环；其余实现票、生产和广泛教学质量门槛仍待完成。实际结果、失败与局限见 [首票验证报告](.scratch/math-harness-delivery/evidence/01-live-curriculum/README.md)。

当前方案于 2026-09-15 按用户“定稿提交 push”的指令定稿，包含 [面向课程负责人／教师的交互参考](.scratch/math-harness-delivery/prototype-baseline.md) 与下文的文件化／框架复用范围。全年课程体系及跨层交接已补入同一原型；全部 ticket 的工程依赖见 [依赖关系图](.scratch/math-harness-delivery/dependencies.md)。实现期间共用同一交互参考，按当前阶段落实功能，内容历史等后置能力不因原型已有演示而提前建设。不再重复索取本轮定稿确认；静态原型不是生产或教学质量验收。

当前 [全年课程到实际教学的交互方案](.scratch/math-harness-delivery/teaching-workspace.shape.md) 已获准构建，并落实为 [可点击页面](.scratch/math-harness-delivery/prototypes/teaching-workspace.prototype.html)：全年、单元／课段、实际材料、局部修订、条件与版本，以及各能力自己的 HITL。静态样本的行为和视口检查见 [本轮走查](.scratch/math-harness-delivery/prototype-build-walkthrough.md)，不代表生产能力或教学质量验收。

**当前先完成文件化的教学内容闭环。** 按用户最新范围，自行确定中间格式，不再评估或借鉴另一项目的 authoring；暂不上业务数据库，不建设内容版本历史。采用 JSON 保存当前课程／教学工作源和检查，正文允许 Markdown／LaTeX，图件另存文件；运行状态与真实待答由框架管理，保留内容指纹以核对检查和回应的适用性。具体见 [文件化内容格式](.scratch/math-harness-delivery/content-system-design.md)。先落实最小格式与读写渲染，不将全功能内容平台、编辑器或生产部署作为此前置；完整追溯、内容历史及生产可靠性保留在后续交付范围。

当前运行时继续使用 **LangGraph＋Agent Server，以 `langgraph dev` 本地开发模式运行**。会话、run、状态保存、流式、取消及 HITL 恢复直接复用框架，前端使用原生 API／SDK；不另造后台任务、队列、SSE 或文件运行状态机。教学内容仍用 JSON／图件保存，不建业务数据库或内容历史；框架内部 checkpoint 保留。具体见 [简化运行时](.scratch/math-harness-delivery/content-system-design.md#运行时也从简)。当前无需独立 PostgreSQL／Redis 服务，生产部署与完整故障验收后置。

## 当前可运行切片：工程验证范围

已支持八年级 CCSS 的有限课段设计：真实 Gemini＋本地 LC、原生任务 API／进度流、JSON／图件／教师阅读稿、独立检查与反馈修订。运行 `uv sync --frozen`、`npm ci --ignore-scripts` 后，按 [配置与调用说明](docs/runtime.md) 启动 `uv run python scripts/dev.py --port 2024`。正式类型和导出契约位于 `src/teaching_harness/contracts.py` 与 `docs/contracts/`。

**当前产物是工程验证样本，尚未交付正式课程体系或可直接授课的 Lesson 材料包。** 当前实现把多课任务和解答集中保存在独立 Section 中，缺少正式全年／单元定位、独立 Lesson 及师生材料交接。课段应承担单元内部的理解进程、表征变化和检查位置，具体题面、解答、教师组织与学生材料应落在 Lesson；上层可保留代表任务及引用。修复阅读稿和程序检查通过不能替代这些职责。后续回到全年蓝图、单课材料和跨层交接主线，不继续把孤立课段报告打磨成独立产品。详见 [首票范围与对照复核](.scratch/math-harness-delivery/ticket-01-scope-and-comparison-review.md)。

**当前下一项内容主线是 [全年蓝图（15）](.scratch/math-harness-delivery/issues/15-full-year-blueprint.md)**，随后推进 [一课材料（03）](.scratch/math-harness-delivery/issues/03-continuous-lessons-and-materials.md) 和 [全年到连续三课（17）](.scratch/math-harness-delivery/issues/17-curriculum-lesson-handoff.md)。01 的有限工程范围已完成；当前不继续扩大孤立课段，也不以 Skills 对照准备替代尚未交付的课程内容。必要交互、检查和运行保障随教学链接入。完整规格、22 张票及拆分依据的核对见 [整体推进路径复核](.scratch/math-harness-delivery/delivery-path-audit.md)。

维护者可通过原生流查看模型／工具请求、返回与错误，并保存本地诊断记录。开发脚本默认开启诊断能力，读取仍须服务配置的维护者身份及任务访问权；生产直接启动默认关闭，可由管理员显式开启。普通教学订阅继续只提供教学进度、草稿与结果。LangSmith 追踪尊重服务端显式配置，平台关联和观察故障仍由后续票验收；配置与回放方法见 [维护者诊断](docs/runtime.md#维护者诊断)。

首票此前真实结果为 3 课时、6 项关键任务，检查通过；不代表完整全年、正式三课上层、课堂成效或生产保证。当前已采用[五阶段执行图](.scratch/math-harness-delivery/ticket-01-graph-refactor-design.md)：作者与审阅用静态 Agent，其余阶段用普通 Python。已保存阶段可按框架检查点接续，未确认的外部调用仍保守停止；取消后公开续作与生产恢复后置。重构后的三课时样本曾因自设 token 拦截及公式解析问题未完成，[失败证据](.scratch/math-harness-delivery/evidence/01-live-curriculum/graph-refactor/README.md)保留。现已撤销默认累计 token 预算、修复公式解析与具体错误反馈，并完成真实修订、独立审阅及桌面浏览器走查；[最终阅读稿](.scratch/math-harness-delivery/evidence/01-live-curriculum/render-repair/final/output/curriculum.html)与[实际消耗和验证范围](.scratch/math-harness-delivery/evidence/01-live-curriculum/render-repair/README.md)可直接核对。此次通过不代表教师校准、打印成套课时材料或课堂成效。

## 本仓库要交付的能力

| 能力 | 必须完成的教学工作 |
| --- | --- |
| 课程体系设计 | 设计 Grade／Unit／Section／Lesson 的目标分配、学习进程、表征、任务和评测；形成各层 Narrative，解释组织理由与前后衔接，并能检查和修订跨层关系 |
| 课时与材料设计 | 将本课目标和课程位置落实为真实数学任务、解法、教师引导、学生材料及学习检查 |
| 教学适配 | 根据相关学习证据调整任务入口、支持、支架与拓展，保持明确的数学目标，说明改动及依据 |
| 教师备课 | 围绕真实课时亲做和分析关键任务，与教师讨论难点、学生可能的思考及教学应对，形成可使用的备课结果 |
| 理解度检查 | 设计能够区分目标理解及相关困难的任务，验证题目、答案和回应解释，给出具体后续教学指引 |

课程体系设计是上游四项 Skills 未提供的新增核心能力。其完成条件包含目标、学习进程、任务和证据之间可检验的联系；生成目录或拼接若干独立教案不足以完成它。

**数学是首个实现学科。** 其他学科分别保留自己的教学特点；差异过大时分别设计流程、资源和检查。学科差异集中记录、按需引用，其他学科的专属问题不进入数学首阶段的验收门槛。当前沿用上游美国 K–12 教学语境。

**标准框架自始至终固定使用 CCSS（Common Core State Standards）。** 数学采用 CCSS Mathematics 的内容标准与数学实践标准，贯穿课程设计、教学任务、知识查询和质量验证。州标准选择、州版替换及跨框架适配不在项目范围内；学校差异通过教学条件、资源和学习者支持处理。Harness 固定 CCSS 框架身份并记录所用数据版本，不让教师或模型重新选择框架。

## Harness 的执行职责

- **Context 体系**：从具体教学工作反推模型需要的规则、各层课程与 Narrative、知识关系、实际材料、学习证据、学校约束和真实人类决定；设计按阶段装配、信息可见范围、来源与版本、跨调用延续及更新失效。
- **LLM 与工具的使用方法**：组织理解目标、查图、设计任务、试做、生成、检查和修订的行动循环；明确每项判断由什么输入支撑、需要什么工具结果、怎样验证。保留简明设计依据与可检查结果。
- **HITL**：按具体教学目的设计课程取舍、教师亲做、内容审阅等交互；记录真实回应及其对象、版本，处理修改、取消和恢复。外部已提供的本次有效决定直接使用。
- **完整运行能力**：承载会话与任务、模型和工具调用、持久化、流式进度、并发与取消、故障恢复、版本兼容和运行观察，并与外部 Web 产品对接。
- **质量与修订**：核对数学正确性、任务认知要求、学习机会、证据与目标对应、产物可用性和跨层一致性；修改后定位受影响内容，重新检查相应版本。
- **执行证据**：返回产物、待答请求、检查结论、使用依据及生成和修订记录，使外部系统能够完成审核、发布和追溯。

生产执行在 Web 后端承载，不依赖 Claude、Codex 等交互式 Agent 客户端。按用户当前偏好，已用 Gemini `gemini-3.8-flash` 完成全年蓝图与连续三课生成、两轮问题反馈修订、复查和一次跨层课时调整的有限实验；材料有所改善，仍有图形可读性、时间安排和效果声明问题，尚未证明教学质量达标。证据见 [实测记录](.scratch/skills-harness/experiments/grade8-linear-functions/runtime-notes.md)、[质量裁定](.scratch/skills-harness/experiments/grade8-linear-functions/quality-review.md) 和 [质量验证票](.scratch/skills-harness/issues/05-capability-validation.md)。Claude、OpenAI 和开源模型三类接入仍纳入评估，具体调用组合根据实际能力验证确定。

## 三类参考依据的不同作用

| 依据 | 在本项目中的作用 | 使用原则 |
| --- | --- | --- |
| [k12-teacher-skills](https://github.com/anthropics/k12-teacher-skills) | 教学执行流程、Context、LLM 使用、HITL、检查与修订的首选参考，以及既有四项能力的比较基线 | 完整保留详细流程分析。原规则不自动成为项目约束；重要改动必须说明原目的、替代机制和验证证据。在尚未证明更优效果前，继续以它们为设计起点 |
| IM | 成熟课程设计思路与教学内容的参考、对照对象 | 形成自己的课程结构，借鉴有教学理由的原则；固定原创内容后，再做条件可比的 IM 对照与修正。具体单元顺序、课堂阶段、MLR 和数量不自动成为产品要求 |
| 本地 Learning Commons | 标准、Learning Components、学习进阶、课程层级、依赖及对齐的知识依据 | 使用真实实体、关系方向与来源，说明本次采用的用途；分别记录图中事实和设计推断。学习支持、课程依赖与关联各按自己的语义使用 |

原 Skills 与 IM 的用途需要分别判断：独立课程结构不意味着舍弃已有教学执行经验；参考原 Skill 流程也不意味着必须复制 IM 的课程体系。

Learning Commons 的本地化已由另一项目完成；[已有数据研究](../k12-learning/research/learning-commons/README.md) 和本仓库的 [实际用法核查](.scratch/skills-harness/assets/learning-commons-integration.md) 是使用入口。图提供设计依据，教学设计仍需判断任务、学习者条件和课堂可实施性。

知识身份、框架版本、关系语义、来源与推断及内容使用范围，执行时遵守 [知识使用约定](docs/references/knowledge-consumption-contract.md)；具体查阅版本与只读样本记录在 [证据基线](docs/references/reference-baseline.json)，不把快照计数或物理字段写死为接口。IM 方法论的新增教学依据及数学内部差异见 [转用研究](.scratch/skills-harness/assets/im-design-methodology-transfer.md)，原 Skills 的流程参考继续保留。

## 实施路线

本节描述完整交付路线；当前文件化阶段的约定优先于旧文档中“首版即持久数据库／不可变历史”的时点。LangChain／LangGraph／Agent Server／LangSmith 的技术方向保留，数据库支持的生产部署和完整恢复随后验证；文件保存不能被声称为已通过这些运行保证。各能力的教学流程、必要质量检查和真实 HITL 按适用切片继续落实。

以下是已确定的推进方向；架构依据见 [架构地图](.scratch/skills-harness/map.md)，当前实施要求与进度见 [交付规格](.scratch/math-harness-delivery/spec.md) 和 [实现路线](.scratch/math-harness-delivery/README.md)。框架版本和模型能力以实施时的实际验证为据。

1. **分析教学工作与执行机制。** 从原 Skills 的详细流程出发，理解每一步保障什么；同步补充课程体系设计。将 Context、LLM 使用、工具、HITL、产物和完成条件一起展开，随流程定义验收标准。
2. **用数学单元贯通设计与必要验证。** 当前沿八年级线性函数方向，包含全年蓝图、前后联系、课段、实际课时、材料和评测，并检验一次跨层修订；具体研究条件与取样深度见 [输入与评价准备](.scratch/skills-harness/experiments/grade8-linear-functions/README.md)，仍为待验证候选。验证从具备充分教学资源和必要运行保障的简洁模型循环开始，按实际缺口逐项增加机制，不先建设两套完整架构再比较。无需先完成整套 K–12，也不能仅用孤立单课代表课程体系能力。
3. **实现前补齐运行、服务与评测架构。** 以 LangChain／LangGraph／Agent Server／LangSmith 为技术方向，核查可复用的框架能力及本项目责任，完成会话、任务、持久化、恢复、模型与工具接入、部署运维、运行追踪与评测等专项及必要原型。当前已有 [主执行与调用设计](.scratch/skills-harness/assets/main-execution-design.md)、[完整运行专项研究](.scratch/skills-harness/issues/11-agent-server-stack-research.md) 和 [有限持久运行实测](.scratch/skills-harness/assets/cfu-durable-prototype-results.md)，据此已收敛 [调用约定](.scratch/skills-harness/issues/02-execution-interface.md)与[模型／知识／产物选择](.scratch/skills-harness/issues/04-runtime-adapters.md)；生产部署、完整版本迁移和平台评测仍按[验证路线](.scratch/skills-harness/assets/validation-and-release-route.md)实施。LangSmith 的观察、评测和人工标注需要与产品的真实人类参与及内容记录正确衔接。研究和局部探针不代替生产运行保证。
4. **形成可实施规格并交付。** wayfinder 后已完成 `/to-spec` 与 `/to-tickets` 的本地交接。经 [规模与依赖复核](.scratch/math-harness-delivery/ticket-sizing-review.md)，工程首步用有明确范围的真实课程任务贯通运行，再分别完成全年蓝图、单课材料与连续课时交接；首个教学交付里程碑仍是全年到实际课时，随后扩展完整单元及跨层修订。适配、教师备课和理解度检查在各自所需基础具备后推进，不必等整个单元；备课可使用外部提供的真实原课。五项能力都保留在交付范围中，质量检查、HITL、恢复、观察和后端调用随真实切片建设。硬依赖、价值优先顺序与发布门槛分别记录，远端工作包按实际产出收口，不全部预标为可执行；具体见 [完整功能交付路线](.scratch/math-harness-delivery/README.md)。
5. **持续比较并改进。** 四项既有能力与固定上游执行基线比较；原创课程与 IM 做条件可比的内容对照。分别验证执行可靠性、内容质量、交互和产物，并据证据改进。评价标准从第一步开始定义，不留到实现结束才补。

完整运行时研究的既定时点不妨碍及早研究会改变教学流程可行性的技术问题；其余服务与部署细节在实现前集中强化。当前没有已验证的更优完整替代机制，也尚未证明生成质量达到原 Skills。

## 设计与协作原则

1. **从教学目的出发。** 用第一性原理理解、检验和改进已有机制：学生或教师要完成什么，需要什么信息、行动与证据。简洁或统一的架构本身不能证明教学效果更好。
2. **克制设计，按证据扩展。** 从交互、Context 到接口和实现机制，先采用能完成真实教学工作的最小充分方案。默认在已明确目标与授权内自主推进；新增提问、选项、阶段、专用分支或通用抽象，须说明具体需要、简单替代及收益。按缺口逐项扩展，避免先铺开再回收；场景分析不自动成为产品功能或生产流程。保留必要质量、真实参与和运行保障，不为预想的未来变化先建机制。**工作优先级由主线价值和依赖决定，不能跟随最新话题漂移。** 用户的提问或补充建议先判断是否改变目标、阻塞当前架构决定或会造成重大返工；有价值但可后置的内容记录后继续主线。每个实验须说明它要解决哪项当前决定、已有证据为何不足，以及何时结束；局部完善不自动成为下一个任务。
3. **充分利用 LLM 的推理与内置知识。** 让模型承担需求理解、数学推理、任务创作、教学方案比较和修订；提供充分适用规则、当前任务与按需工具，不以穷举分支替代推理，也不要求每个常识或推理步骤都检索。具体标准与图关系以实际来源为据，学校条件、学习者状态和人类决定由真实输入提供；模型知识与设计推断可参与创作，实际产出接受相应检查。使用方式见 [Context 设计](.scratch/skills-harness/assets/context-and-llm-design.md#模型内置知识与任务证据怎样协作)。
4. **保留参考，审慎替换。** 原 Skills 的源码与详细流程分析持续作为设计和比较依据。区分来源要求、候选解释、本项目已定约束和验证结果；提出替代时保留原基线及其价值，取得效果证据后再判断。
5. **用真实工作验收。** 检查实际题目、解法、表征、推理要求、学习证据与可用材料。文件存在、模型自评和教师满意各只能证明相应事实，不能独自证明全部质量。
6. **尊重能力、学科与课程层级的差异。** 各 Skill 和学科按自身特点设计。覆盖在约定的年级／单元范围检查，单课承担其实际目标；个体支持变化与课程基线变化分别处理。
7. **让人类参与有目的、决定有对象。** 教师亲做、课程取舍与内容审阅分别设计；回应、产物和检查关联具体版本。修改后分析影响，沿已有授权推进，避免重复索取同一决定。
8. **明确证据的适用范围。** 来源事实、模型推断和真实学习证据分别记录。静态设计、程序检查、模型评测和课堂反馈各有证明范围；离线内容评分不能冒充学习效果。
9. **主动检查路线偏离。** 对偏离既定目标或路线的建议，指出冲突、提出不同意见并说明证据与代价；不能顺着局部表述默默改变主线。明确调整后同步权威文档和关联决定；常规已授权工作持续推进。
10. **研究和决定随工作文档化。** 详细研究、流程与验证证据通过索引和决策票可到达；保留可复核依据，不用新摘要替代重要原分析。路线变化更新本页，具体架构决定记在对应决策票或适用 ADR。
11. **质量先行，摸清消耗后再优化预算。** 当前先实现并验证高质量的教学能力，随正常任务记录不同范围与复杂度的实际消耗；取得质量与消耗基线后，再逐项优化并验证质量保持。当前默认不设累计 token 预算，真实示例只记录供应商实际用量；不得以自设 token 额度或字节估算截断必要修订。预算优化不作为规格或首版交付的前置专项，不为节省调用而削减必要 Context、检查或有进展的修订。保留可配置的防失控上限、取消、累计消耗和停止续作；遵守明确的资源限制，触限保存未完成工作，不降低质量标准或冒称完成。12／24 次探索上限不成为生产默认。具体落实见 [质量与消耗的推进顺序](.scratch/skills-harness/assets/validation-and-release-route.md#质量与消耗的推进顺序)。

## 外部系统与本仓库的边界

完整 Web 学习系统面向学校、教师、学生和家长，负责采集学习过程证据并形成 Learner Model。这是 Harness 的使用环境和对接背景；本仓库的交付目标是上文的课程与教学设计能力。

| 外部负责提供或建设 | 本仓库负责的对接 |
| --- | --- |
| Web 界面、身份权限及学校工作流 | 接收任务与有权限的上下文，发出真实待答请求，返回进度与结果 |
| 学习证据采集、管理及 Learner Model 构建更新 | 使用与当前教学任务相关的证据，落实个性化改变并记录依据 |
| 已完成本地化的 Learning Commons 数据 | 查询并正确使用知识实体、关系和版本；不承担下载与入库 |
| 全系统归因、审核发布与质量治理 | 提供产物、来源、检查、生成、修订及人类决定的执行证据 |

学校环境进入设计的实际约束包括教学日历、资源、教师准备负担、学生工作量及所需支持。外部系统负责这些能力的建设，不免除 Harness 的接口、质量和证据职责。

## 文档读取路径

| 文档 | 负责说明什么 | 何时读取 |
| --- | --- | --- |
| [AGENTS.md](AGENTS.md) | 项目 Agent 的读取和工作约定 | 项目任务入口；[CLAUDE.md](CLAUDE.md) 指向同一文件 |
| 本 README | 仓库目标、路线、原则和职责边界 | 开始项目任务及本文更新后 |
| [PRODUCT.md](PRODUCT.md) | 供 Impeccable 使用的已确认产品事实摘要：用户、工作情境、能力、证据及交互原则；不另立需求或视觉权威 | 产品交互与界面设计任务开始时，与本 README 及相关详细流程一起读取 |
| [架构结论](.scratch/skills-harness/assets/architecture-conclusion.md)、[架构地图](.scratch/skills-harness/map.md) 与子决策票 | 采用结构、规划状态、具体决定及依据 | 进入规格、核对架构决定或发现反证时 |
| [规划材料索引](.scratch/skills-harness/assets/index.md) | 按任务类型选择研究、详细流程和候选设计 | 分析、实现或评审相关教学与运行能力前 |
| [知识使用约定](docs/references/knowledge-consumption-contract.md) 与 [证据基线](docs/references/reference-baseline.json) | 知识消费责任，以及可核对的来源文件与数据样本 | 设计或实现知识查询、Context、来源追溯及其评测时 |
| [CONTEXT.md](CONTEXT.md) 与 `docs/adr/` | 领域词汇与适用架构决定；ADR 按需建立 | 使用或调整领域概念、核对相关架构决定时 |
| [交付规格](.scratch/math-harness-delivery/spec.md)、[实现路线与任务](.scratch/math-harness-delivery/README.md) | 五项能力的行为、接口、范围、依赖及验收要求；[逐票复核](.scratch/math-harness-delivery/ticket-sizing-review.md) 说明拆分理由 | 实现或评审任务前；当前由已完成的有限任务接续全年蓝图 |

**开发 Agent 的文档读取与产品 LLM 的运行时 Context 都要落实。** AGENTS.md 负责引导项目工作读取上述资料；产品运行时则需要在执行规格中明确各阶段加载的教学规则、数据、产物和验证资源及其版本，并由 Harness 实际装配和检查。写入 README 不代表运行时模型已经取得这些信息。

## 获取源码

```bash
git clone --recursive git@github.com:morebests/k12-teaching-harness.git
```

已有克隆可初始化子模块：

```bash
git submodule update --init --recursive
```

上游参考保存在 `k12-teacher-skills/` 子模块中。依赖资料见 [上游评测说明](k12-teacher-skills/evals/README.md)、[LangGraph 文档](https://langchain-ai.github.io/langgraph/) 和 [LangChain 文档](https://python.langchain.com/)。
