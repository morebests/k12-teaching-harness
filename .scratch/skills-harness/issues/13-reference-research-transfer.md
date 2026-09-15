# IM 方法论与本地知识研究有哪些应进入 Harness 设计

Type: research
Labels: wayfinder:research
Mode: AFK
Status: resolved
Assignee: li3p
Blocked by:

## Question

核查用户指定的 IM 方法论长文和内容导入研究，识别能够补强本项目独立数学课程、教学执行、Context 与质量验证的依据。关键事实沿原始来源复核；外部项目自己的产品约束不自动成为本项目要求。

同时检查既有 Learning Commons 研究：哪些关系语义、标识与版本、覆盖和数据使用结论应固化为本仓库的消费约定，哪些只需保留来源与可复核样本？固化结果要进入项目任务必读入口及相应决策，不承担外部数据下载、导入或 Learner Model 建设。

## Context

- [IM 方法论长文](/Users/libo/Mathematics/k12-learning/docs/research/illustrative-mathematics-design-methodology-humanized.md)
- [IM 来源范围、权利与完整性研究](/Users/libo/Mathematics/k12-learning/.scratch/im-v360-content-import/research/01-source-scope-rights-and-completeness.md)
- [LC 与 AccessIM 结构及格式漂移研究](/Users/libo/Mathematics/k12-learning/.scratch/im-v360-content-import/research/02-lc-structure-and-accessim-schema-drift-audit.md)
- [Learning Commons 既有研究](/Users/libo/Mathematics/k12-learning/research/learning-commons/README.md)
- [本仓库本地知识用法](../assets/learning-commons-integration.md)
- [当前课程能力决定](12-curriculum-design.md)

## Comments

### 研究分工

IM 方法论由 research 子代理核对原始来源并写入本仓库专题材料；主代理核查两份导入研究、本地知识事实和现有项目约定，整合采用范围及读取入口。只读取外部仓库，所有本轮文档变更留在本仓库；不调用课程生成模型或启动导入工程。

### Resolution：保留来源，固化消费语义，补强教学执行（2026-09-14）

用户指定资料对本项目有直接参考价值，已完成转用研究。它们没有给出可取代原 Skills 的完整执行机制或更优效果证据；当前独立数学课程与四项教学能力主线保持。

**IM 方法论：**完整阅读长文，复核十个官方页面，形成 [IM 方法论补强](../assets/im-design-methodology-transfer.md)。新增价值集中在活动目的与教学动作、表征语义和使用史、讨论预案与真实学生作品、不同支持类型、跨时间练习、形成性响应范围、互动方式各自的信息与作品延续、教师准备的实际工作。K／Grade 1 观察清单、centers 和小学响应分类提供了数学内部不宜统一的反例。这些已接入课程与 Context 分析及执行／HITL／质量票，作为需要落实和验证的设计依据，不直接锁定每项候选流程。

**两份导入研究：**采纳对目录、关系、正文与版本分别检查，以及跨来源身份、受众／语言、非树引用和变化影响的区分。本地只读复核了 18 个英文 Course、59 个树外活动中 58 个通过引用连接等样本。原报告的完整跨站映射与来源格式测试没有在本项目重跑；爬虫、导入、原子发布、特定首批课题及其 Generation 限制均不迁移为本仓库职责。

**Learning Commons 固化：**[知识使用约定](../../../docs/references/knowledge-consumption-contract.md) 承载框架选择、图内／CASE／出版者身份、关系方向及对齐角色、来源与设计推断、版本延续和对象使用范围。共同研究模型、个体实例及 LC 定义进入 [CONTEXT](../../../CONTEXT.md)；[证据基线](../../../docs/references/reference-baseline.json) 固定八份外部文件的 SHA-256、已用数据快照元数据及七项查询观察。具体计数、SQLite 物理列、文档类型全集和网页格式仍是版本化证据，不是永久接口。清单仅定位与检测变化，不冒充已归档完整外部资料。

**进入执行的位置：**README 与材料索引已增加读取入口；[执行结构](03-execution-structure.md) 落实教学目的、Context 和真实状态，[知识与模型工具](04-runtime-adapters.md) 落实查询与来源语义，[HITL](07-hitl-protocol.md) 区分预案、教师亲做与课堂事件，[质量验证](05-capability-validation.md) 纳入适用性和知识使用反例。

本轮只读外部资料和本地数据库，保留原详细流程。实际完成的是来源研究、有限数据复核和文档固化；未进行生成、接口实现、运行原型或课堂效果测试。研究完成后继续 [课程与教学设计的执行流程和状态如何设计](03-execution-structure.md)。

### 用户澄清：共同结构与个体实例（2026-09-14）

用户指出，LC／LVN 的共同模型可以关联具体学生，不同学生拥有不同掌握情况。此前将其概括为“两种 Learner Model”容易错误暗示需要两套互不相干的模型，已修正领域词汇、知识使用约定及 Context／本地图研究：共同结构可以复用，个体状态由外部系统依据证据形成；关联身份本身不等于已有观测。LC／LVN 还包含认知、社会情感与背景因素，其个人状态不能全部压成知识技能掌握度。本仓库继续消费相关状态与证据，不扩大到模型估计或更新工程。
