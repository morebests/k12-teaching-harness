# 按真实草稿回应生成课时材料

Status: ready-for-agent
Blocked by: [让真实教学决定跨进程等待并恢复执行](02-human-decision-and-resume.md)、[直接生成一课的真实师生材料并检查修订](03-continuous-lessons-and-materials.md)
Size: M — 在实际课时内容与待答机制上增加创建自身的草稿协作。

## What to build

教师先看包含实际任务的课时草稿，提出修改或授权成套生成；Harness 按真实意图继续，最终材料保留已采用任务。不会把只有修改理解为生成批准，也不会重复询问“改好直接生成”。

## Acceptance criteria

- [ ] 草稿完成适用知识准备和实际数学任务设计，展示版本可回读；不能只有模板或主题清单。
- [ ] 仅修改后更新草稿并等待；“改好直接生成”直接修改、生成和检查；已有完整生成决定不重复提问。
- [ ] 否定、附带条件、新意图和简短回答按实际展示对象解释，原始回应和采纳范围持久关联；下游重试不重解释已采纳决定。
- [ ] 最终材料源延续已采用题目、数据、条件和目标；若确需改变，记录理由、影响与适用授权，重查实际内容。
- [ ] 经 API 验证真实草稿交接和等待恢复，生成后沿用完整数学／渲染检查；调用例随接口更新。
- [ ] 材料已完成后的一般满意邀请不变成必须等待；不能借本票将创建改成适配的整套接受流程。

## Reading and boundaries

读 [规格](../spec.md)、[创建流程](../../skills-harness/assets/lesson-creation-execution-design.md)、[创建原 Skill](../../../k12-teacher-skills/plugin/skills/k12-lesson-plan-creation/SKILL.md) 及其适用参考、[HITL](../../skills-harness/assets/hitl-design.md)。保持一课闭合，不在本票建设连续课时进程。

## Comments
