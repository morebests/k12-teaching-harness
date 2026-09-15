# 生成覆盖完整八年级 CCSS 的全年蓝图

Status: ready-for-agent
Blocked by: [从任务接口完成有明确范围的真实课程设计](01-live-curriculum-task.md)
Size: M/L — 已有真实执行循环上扩大知识与设计范围，主要未知是覆盖和课程组织质量。

## What to build

调用方请求完整全年方案，Harness 取得完整八年级 CCSS 内容及实践范围，设计自有单元组织、Narrative 与学习进程，并交付有覆盖检查的真实全年蓝图。承接首票移出的全年工作。

## Acceptance criteria

- [ ] 经同一任务 API 使用实际本地数据遍历全部必要层级和分页；缺页、空集、排除和错误有不同结果，不能硬编码旧快照节点数来证明完整。
- [ ] 目标、学习进程、各单元职责与 Narrative、先备／后续和学校时间条件齐备；Learning Components 和图关系实际用于设计，模型推断与图事实分开。
- [ ] 全年内容标准和实践标准分别有覆盖依据；单元位置由本设计决定，线性函数不预设为 IM Unit 4。
- [ ] 用关键任务构想试查单元职责是否可实施；不要求本票生成全年逐课材料，也不把构想视为已展开课时。
- [ ] 检查遗漏、重复、目标与时间矛盾等问题，反馈修订实际方案；严重问题保留并阻止相应通过声明。
- [ ] 提供相关线性函数单元的具体版本、目标分配、时间、Narrative 和前后联系，可被课时设计直接读取；不得从临时首票课段暗中补出全年事实。
- [ ] 真实运行保存输入、规则、知识、消耗、实际方案与检查；目标 IM 持续隔离，外部调用示例和 OpenAPI 同步实际支持范围。

## Reading and boundaries

读 [规格](../spec.md)、[课程能力](../../skills-harness/assets/curriculum-design-capability.md)、[Context 设计](../../skills-harness/assets/context-and-llm-design.md) 和 [知识使用约定](../../../docs/references/knowledge-consumption-contract.md)。不依赖新增 HITL，因为此例使用已明确的全年设计授权；确需交互的任务必须等待相应能力可用。

## Comments

### 2026-09-15：从原首票分离

首次运行贯通与全年覆盖分别验收，完整全年仍在首条课程到课时主线中，未转为后置功能。
