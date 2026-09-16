# 数学 Harness 的交付路线与实现票

更新：2026-09-16。项目目的见 [仓库 README](../../README.md)，行为与质量门槛见 [规格](spec.md)。当前共 26 张票；01、15 保留原有限工程交付，其余工作待实现。`Status` 表示 triage 角色，实施进度另列；票号是稳定身份，不表示执行顺序。

## 为什么先集中全年规划

当前缺口是年度目标、学习经历、表征、练习和评价尚未组成足够可信的课程进程。若直接展开 Lesson，后续材料会继承尚未解决的上层问题。因此先在全年层验证阶段成果、集中 Context、定向检查和回修，再把有效方法迁移到其他能力。当前暂停向 03／17／06 推进，五项能力与完整课程目标保留。

工作包按能消除的教学风险和可独立验收的成果拆分，不按 Graph 节点、Agent 角色或组件名拆分。每票先说明为什么做，再给输入、成果、失败回修与证据。完整理由链见 [规格 Y1–Y6](spec.md#问题价值与验证依据)，本次承接变更见 [重整记录](year-planning-replan.md)。

## 当前主线：23 → 24 → 25 → 26

| 工作项 | 为什么排在这里 | 可检查的交付 | 就绪程度 |
| --- | --- | --- | --- |
| [检查校准与全年证据评价（23）](issues/23-year-evaluation-and-check-calibration.md) | 先知道怎样判断和检查会漏什么，避免事后选择有利标准 | 证据索引、对象级发现、评分／裁定记录、旧错和新变体及合法对照的实际校准 | ready-for-agent；待实现 |
| [目标依据与全年布局（24）](issues/24-year-foundation-and-layout.md) | 先夯实年度责任和组织理由，防止错误扩散 | 真实 A／B、集中 Context、检查回修和有效交接 | ready-for-agent；工程前置为 15、23 |
| [所有单元进程与全年核查（25）](issues/25-year-progressions-and-global-checks.md) | 布局还不能证明学习机会与全年组合成立 | 全部 C、D、真实全年从头生成、阅读稿及单元交接 | needs-triage；据 24 实际成果收口 |
| [全年 IM 比较与修订复评（26）](issues/26-year-im-comparison-and-revision.md) | 让质量差距和方法效果有证据可判 | 逐维强弱／重大问题、实际修订复评、方法结论与局限 | needs-triage；据 23、25 收口 |

25／26 保留明确完成目标，但不假装已经知道实际单元工作量、评分分歧或专业评阅条件。输入具备后按既有授权收口，必要时继续拆票；不重开一次产品访谈，也不因缺少专业评阅而停止独立的实现和证据准备。

评价规则在生成前固定，适用检查贯穿 A–D，26 才对固定候选作完整同尺度比较。**四张票结束不自动表示全年质量达到 IM。** 按 [规格门槛](spec.md#验收与质量声明)分别记录工程完成、全年质量和方法证据；有未解决关键差距时继续年度回修，不用更高总分抵消，也不以向下展开替代。

## 保持的边界与后续里程碑

当前仍是 [文件化教学内容闭环](spec.md#当前阶段文件化教学内容闭环)，运行使用 LangGraph＋Agent Server dev。复用现有模型 Adapter 和原生状态、流式、取消／中断；不前置业务数据库、内容历史、生产部署或新的累计 token 预算。必要格式修复、数学检查、访问边界和维护者诊断随真实工作落实。

| 后续里程碑 | 为什么需要 | 验收范围 |
| --- | --- | --- |
| 03／17：课时材料与正式课段 | 检验全年意图在学生实际任务中兑现，并清偿旧 Section 混放 Lesson 内容 | 独立 Lesson、师生材料、连续三课、表征练习连续性和上层反馈 |
| 06／07：完整单元与跨层修改 | 局部三课不能代表完整进程，调整还会改变后续机会 | 全部课段／课时／练习／评价、容量及跨层修订 |
| 08／09／10／16：其余教学工作 | 适配、备课、CFU 和草稿协作有各自教学目的 | 各自规则、实际材料、真实参与和完成条件，迁移机制重新验证 |
| 11／19 与 12／20：后续对照 | 全年证据不能替代各能力流程或完整单元内容质量 | Skills 自身尺度、完整单元同尺度参考与修订，记录参考影响 |
| 运行与消费者交付 | 真实决定与成果还需在故障、权限变化和部署下可信 | 02／04／05／18／13／21／22／14 的明确范围及实际证据 |

独立单课仍可从明确目标开始，备课可读外部真实原课，CFU 不要求先有教案；这些工程入口保留。当前执行优先级与全年质量门槛不会被伪造成每张票的新硬依赖。17 的上层提供方从 15 换为 25，是实际交接契约的变化。

## 保留的工作项与硬依赖

下表保留原 22 票身份与范围，新四票见上表。完整工程图及 triage 角色见 [依赖关系](dependencies.md)。原 [拆票分析](ticket-sizing-review.md)及 [旧快照](ticket-baseline-20260915.json)保留历史证据，当前变更由本版正文说明。

| 工作项 | 规模与就绪程度 | 硬依赖 | 独立结果 |
| --- | --- | --- | --- |
| [从任务接口完成有明确范围的真实课程设计](issues/01-live-curriculum-task.md) | L；有限范围已实现并验证 | 无 | 一个真实有限课段方案；任务、知识、内容及最小访问契约 |
| [生成覆盖完整八年级 CCSS 的全年蓝图](issues/15-full-year-blueprint.md) | M/L；原有限工程范围已交付 | [从任务接口完成有明确范围的真实课程设计](issues/01-live-curriculum-task.md) | 完整年级获取、年度样本和历史交接；新方法与质量由 23–26 承接 |
| [直接生成一课的真实师生材料并检查修订](issues/03-continuous-lessons-and-materials.md) | L；边界已明确 | [从任务接口完成有明确范围的真实课程设计](issues/01-live-curriculum-task.md) | 一课已授权直接生成；真实师生材料与检查修订 |
| [让真实教学决定跨进程等待并恢复执行](issues/02-human-decision-and-resume.md) | L；边界已明确 | [从任务接口完成有明确范围的真实课程设计](issues/01-live-curriculum-task.md) | 真实展示、回应、采纳事务和受控重启 |
| [按真实草稿回应生成课时材料](issues/16-lesson-draft-review.md) | M；边界已明确 | [让真实教学决定跨进程等待并恢复执行](issues/02-human-decision-and-resume.md)、[直接生成一课的真实师生材料并检查修订](issues/03-continuous-lessons-and-materials.md) | 草稿修改与授权生成，实际任务延续 |
| [从全年蓝图交接到连续三课](issues/17-curriculum-lesson-handoff.md) | M/L；边界已明确 | [补足所有单元的规划进程并核查全年连贯性](issues/25-year-progressions-and-global-checks.md)、[直接生成一课的真实师生材料并检查修订](issues/03-continuous-lessons-and-materials.md) | 真实全年版本到连续三课，跨课连续性 |
| [将真实任务关联到 LangSmith 并隔离观察故障](issues/04-tracing-and-quality-regressions.md) | M；边界已明确 | [从任务接口完成有明确范围的真实课程设计](issues/01-live-curriculum-task.md) | 真实 trace 关联与观察失败解耦 |
| [取消教学任务并续作明确停止的工作](issues/05-stop-cancel-and-recovery.md) | M；边界已明确 | [让真实教学决定跨进程等待并恢复执行](issues/02-human-decision-and-resume.md) | 主动取消、停止保存与明确条件下续作 |
| [在崩溃和调度结果不明后自动恢复任务](issues/18-crash-reconciliation.md) | L；边界已明确 | [取消教学任务并续作明确停止的工作](issues/05-stop-cancel-and-recovery.md) | 跨故障窗口自动核对，避免重复有效提交 |
| [按自然语言修改课程并重查受影响内容](issues/07-scoped-curriculum-revision.md) | L；边界已明确 | [从全年蓝图交接到连续三课](issues/17-curriculum-lesson-handoff.md)、[取消教学任务并续作明确停止的工作](issues/05-stop-cancel-and-recovery.md) | 连续课时范围的结构修订、局部支持对照 |
| [完成线性函数整个单元的教学内容与检查](issues/06-complete-linear-functions-unit.md) | XL；待实际输入收口 | [从全年蓝图交接到连续三课](issues/17-curriculum-lesson-handoff.md)、[取消教学任务并续作明确停止的工作](issues/05-stop-cancel-and-recovery.md) | 完整单元内容与全范围检查，按实际三课结果收口 |
| [根据学习证据适配真实数学课时](issues/08-lesson-adaptation.md) | L；边界已明确 | [直接生成一课的真实师生材料并检查修订](issues/03-continuous-lessons-and-materials.md)、[让真实教学决定跨进程等待并恢复执行](issues/02-human-decision-and-resume.md) | 一节真实原课的支持／拓展与自身接受流程 |
| [围绕真实任务完成教师参与的备课](issues/09-teacher-preparation.md) | M/L；边界已明确 | [让真实教学决定跨进程等待并恢复执行](issues/02-human-decision-and-resume.md) | 真实原课上的教师贡献与备课便签 |
| [生成并双重验证数学理解度检查](issues/10-check-for-understanding.md) | L；边界已明确 | [直接生成一课的真实师生材料并检查修订](issues/03-continuous-lessons-and-materials.md)、[让真实教学决定跨进程等待并恢复执行](issues/02-human-decision-and-resume.md) | 一个焦点的学生页、教师指南及两道验证 |
| [从课时创建开始建立可离线复现的 Skills 对照](issues/11-skills-comparison.md) | L；边界已明确 | [直接生成一课的真实师生材料并检查修订](issues/03-continuous-lessons-and-materials.md) | 直接创建与原 Skill 的早期离线对照 |
| [扩展并汇总四项 Skills 的实际对照证据](issues/19-four-capability-comparison.md) | L/XL；待实际输入收口 | [从课时创建开始建立可离线复现的 Skills 对照](issues/11-skills-comparison.md)、[根据学习证据适配真实数学课时](issues/08-lesson-adaptation.md)、[围绕真实任务完成教师参与的备课](issues/09-teacher-preparation.md)、[生成并双重验证数学理解度检查](issues/10-check-for-understanding.md)、[按真实草稿回应生成课时材料](issues/16-lesson-draft-review.md) | 四项能力与草稿交互的实际对照汇总 |
| [固定完整单元并完成同尺度的首轮评阅](issues/12-frozen-unit-comparison.md) | L；待实际输入收口 | [完成线性函数整个单元的教学内容与检查](issues/06-complete-linear-functions-unit.md)、[从课时创建开始建立可离线复现的 Skills 对照](issues/11-skills-comparison.md) | 完整候选 A 固定、参考影响、同尺度 R 与实际首轮意见 |
| [根据匿名评阅意见修订并复核完整课程](issues/20-comparison-driven-revision.md) | 待评阅结果确定；待实际输入收口 | [固定完整单元并完成同尺度的首轮评阅](issues/12-frozen-unit-comparison.md)、[按自然语言修改课程并重查受影响内容](issues/07-scoped-curriculum-revision.md) | 有来源意见驱动的 B 及实际重查 |
| [在持久部署中重启和恢复实际教学任务](issues/13-production-runtime-package.md) | L；待实际输入收口 | [在崩溃和调度结果不明后自动恢复任务](issues/18-crash-reconciliation.md) | 一个冻结版本的实际持久部署、备份与恢复 |
| [在权限撤销后隔离任务、材料和后台续作](issues/21-access-revocation.md) | M/L；边界已明确 | [直接生成一课的真实师生材料并检查修订](issues/03-continuous-lessons-and-materials.md)、[在崩溃和调度结果不明后自动恢复任务](issues/18-crash-reconciliation.md) | 动态撤权、受众边界和后台续作访问一致性 |
| [在部署升级后正确恢复旧版本待答任务](issues/22-waiting-task-upgrade.md) | L；待实际输入收口 | [在持久部署中重启和恢复实际教学任务](issues/13-production-runtime-package.md) | 真实旧待答任务跨一次部署升级 |
| [从外部后端调用五项能力并核对交付边界](issues/14-backend-integration.md) | M；边界已明确 | [按自然语言修改课程并重查受影响内容](issues/07-scoped-curriculum-revision.md)、[根据学习证据适配真实数学课时](issues/08-lesson-adaptation.md)、[围绕真实任务完成教师参与的备课](issues/09-teacher-preparation.md)、[生成并双重验证数学理解度检查](issues/10-check-for-understanding.md)、[按真实草稿回应生成课时材料](issues/16-lesson-draft-review.md) | 已有五能力的服务外消费者契约汇总 |

## 共享成果与消费责任

| 成果 | 提供方 | 消费要求 |
| --- | --- | --- |
| 任务承载、知识身份、当前内容和基本可信访问 | 01／15 | 23–25 复用，不另建任务服务 |
| 全年证据记录、检查反馈与校准 | 23 | 24／25 使用适用判据；26 独立比较；后续能力只复用机制，另用自己的规则 |
| 目标、布局、Context 与有效阶段交接 | 24 | 25 按实际成果展开，全局约束不因局部输入丢失 |
| 全部单元规划、全年核查和精确单元交接 | 25 | 26 固定候选，17 在全年质量门槛后取得有效上层 |
| 真实回应与原文／采纳／续作 | 02 | 16 及各能力保留自己的教学语义，不能用模型或定时器代替人类 |
| Lesson 与同源师生材料 | 03 | 17、08、10、16 等复用实际内容和检查，不沿用旧混合 Section |
| 主动取消续作、自动故障恢复、持久部署 | 05／18／13 | 逐项扩大验证面，21 动态权限、22 跨部署兼容分别验收 |

共享模块从实际工作中提炼，提供方的可运行契约和证据齐备后再接入；准备输入不等于前置行为已完成。每张能力票维护自己的外部调用示例，14 汇总契约及漂移检查。

## 执行与证据约定

- 每票先读 README、规格、对应决定、详细流程和适用上游原文；产品模型取得的运行资源另以装配记录验证。
- 每项重要选择说明目的、已有不足、替代、代价和验证方式。发现假设不成立时修正方法，不为保住图结构改写质量目标。
- 使用 [同一交互基准](prototype-baseline.md)，依据已授权 [工作区方案](teaching-workspace.shape.md)按实际能力落实；不重索定稿确认，也不把静态演示当真实能力。
- 保留来源事实、设计推断、合成条件与真实学习证据的区别。当前已读取 IM，后续比较记录参考影响；保留评测答案和独立评语不泄给被测生成。
- 各票报告可运行行为、当次质量和证据局限。真实专业评阅、教师参与和生产条件缺失时，相应门槛保持未通过，不能伪造。
- 先质量、记录真实消耗、再优化；修复可继续时不以自设 token 额度停止。失败和未完成结果同样留存。

## Comments

### 2026-09-16：从教学目的重写当前路线

将全年优先从补充评论落实到正文和 23–26。原 22 票身份保留，17 改用 25 的实际上层；旧单元冻结前禁读 IM 条款按用户已授权的参考研究修订。完整能力及生产职责未删除。以下记录说明历史拆分，不作为当前排程。


### 2026-09-15：从整体路线拆成实现工作

按用户确认的整体交付路线创建本规格与 14 张实现票。分票是执行粒度选择，不是新增 14 个用户场景或固定模型阶段；没有减少任何一项能力，也没有将人工质量判定伪装成 agent 已可独立完成的工作。

### 2026-09-15：逐票规模与依赖复核

原 14 票保留身份，新增 8 项明确承接被拆出的行为。移除备课对生成器、评价对云端观察、消费者验证对完整内容／生产宿主的非必要依赖；补齐完整单元的续作条件。六个未来工作包不再预标全部就绪。详细原因、原票对应及边界见逐票复核。

### 2026-09-15：实现前保存与用户交互复核

按用户新要求补充全量依赖图，并把旧开发状态原型与现行教学交互候选分别定位。新增单页样本只验证外部消费者怎样表达教学工作，不提前建设 Web 产品，也不修改五项能力的参与条件。保存并推送后，待项目负责人确认具体交互基准再开始产品实现。
