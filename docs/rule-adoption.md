# 首个有限课程切片的规则取用

运行资源为 `src/teaching_harness/resources/curriculum.md` 和 `review.md`，内容指纹写入每次任务 Context。资源只含本次实际教学要求，不把研究报告整体发给原创模型。

| 依据 | 本次采用方式 | 尚不据此声明 |
| --- | --- | --- |
| [课程能力决定](../.scratch/skills-harness/issues/12-curriculum-design.md)、[课程详细设计](../.scratch/skills-harness/assets/curriculum-design-capability.md) | 采用课段职责、Narrative、目标—机会—证据、先备／后续、关键任务试做与反馈修订；按本票只生成有限课段 | 已有权威全年／完整单元或跨层修订 |
| [共同工作规范 N1–N9](../.scratch/skills-harness/experiments/grade8-linear-functions/inputs/common.md) | 保留知识与推断区别、实际求解、学生数学工作、可观察证据、资源条件和如实结束；学校条件改为调用输入，语言按本次用户要求使用中文 | 已验证学习效果或某学生状态 |
| [知识使用约定](references/knowledge-consumption-contract.md) | 固定 CCSS、源身份与快照，明确 supports／buildsTowards 方向、分页与排除 | 图关系决定唯一课程顺序 |
| [上游输出规范](../k12-teacher-skills/plugin/skills/k12-lesson-plan-creation/references/output.md) | 保留唯一内容源、实际材料、表格与必要附件、显示一致性目的；首票采用课程 JSON 与教师阅读稿 | 已实现课时的 shared／from_shared、师生分面或上游完整教案流程 |
| [既有质量失败](../.scratch/skills-harness/experiments/grade8-linear-functions/quality-review.md) | 核对时间重叠、图件实际存在、公式渲染、无依据的效果声明；模型意见必须关联当前内容，允许核实后反驳 | 零排版错误能证明教学质量 |

新增课程能力没有同名上游 Skill。数学教案的完整 39 条 rubric、教师备课贡献、适配接受和 CFU 两道验证由各能力票落实；本票不把有限检查伪称为这些能力的完整实现或比较结论。固定上游版本仍为 `281eb8d41fe2837d911541c9bbb870b58add804c`。

数学任务、进程和修订交给模型；程序只保证当前输入、工具权限、内容引用、资源上限与必要检查。没有按每个课时、每个错误建立节点或自治 Agent。真实人类等待／回应未在首票伪造实现，超出当前授权或范围时应停止并保留未完成结果。
