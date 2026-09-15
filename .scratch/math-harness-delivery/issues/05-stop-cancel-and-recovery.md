# 取消教学任务并续作明确停止的工作

Status: ready-for-agent
Blocked by: [让真实教学决定跨进程等待并恢复执行](02-human-decision-and-resume.md)

Size: M — 验收主动取消与可续作停止；系统性崩溃恢复单列。

## What to build

调用方可以取消实际教学任务，或在资源限制／依赖问题解决后继续保存的工作。请求重送和在途模型的迟到结果不能让已取消工作重新生效。任意故障窗口的自动核对与恢复由 [故障恢复](18-crash-reconciliation.md) 承接。

## Acceptance criteria

- [ ] 取消和续作接口符合规格；先持久禁止提交，再取消 Server run。模型在取消后返回的内容只能保留为无效候选，不能成为有效交付。
- [ ] 触限保存已有内容、未解决问题、停止原因与累计消耗；明确限制改变后才续作。待答不能由续作跳过，已取消任务不能原地重开。
- [ ] 取消与续作使用已保存的动作身份，重送不重复提交；检验在途生成和取消交错的实际结果，不能只检查取消函数被调用。
- [ ] 并发操作使用预期版本条件；同任务串行，冲突可解释；发起去重仍在尚无 task ID 时成立。
- [ ] 停止时保留可读成果和有效引用；跨存储故障的系统性注入转入故障恢复票，本票不得声称已验证任意硬退出。
- [ ] 查询能准确区分取消已接受、在途运行正在停止与已停止；订阅断流协议的验收由故障恢复票完成。
- [ ] 真实任务内容与原始人类回应在恢复后保持版本和来源；通过记录清楚区分 dev／本地进程保证与后续生产存储验收。

## Reading and boundaries

读 [规格](../spec.md)、[主执行设计](../../skills-harness/assets/main-execution-design.md)、[执行结构](../../skills-harness/assets/execution-structure-design.md)、[Agent Server 研究](../../skills-harness/assets/langgraph-agent-server-research.md) 与 [有限探针](../../skills-harness/assets/cfu-durable-prototype-results.md)。

本票扩展已有真实课程任务，不造独立队列平台。完整生产 PostgreSQL／Redis、备份及跨部署兼容由生产候选票验证，不能用本票本地成功替代。

## Comments

### 2026-09-15：分开主动停止与异常恢复

取消／续作是调用方可用的完整行为，自动故障恢复是另一项完整行为。后者移交独立票，既避免大票，也避免与真实回应票重复负责同一组崩溃测试。
