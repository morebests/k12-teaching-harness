# 将真实任务关联到 LangSmith 并隔离观察故障

Status: ready-for-agent
Blocked by: [从任务接口完成有明确范围的真实课程设计](01-live-curriculum-task.md)

Size: M — 一条实际任务的外部观察路径；评价执行器另行交付。

## What to build

对可运行的教学任务接入真实 LangSmith 服务，让维护者从任务看到模型／工具、Context 清单、材料、检查、修订和消耗。观察服务故障不能破坏任务结果。离线回归与对照执行器从 [创建能力对照](11-skills-comparison.md) 开始，不能把 LangSmith 在线可用设为质量评价的硬前置。

## Acceptance criteria

- [ ] 先用独立合成输入验证真实服务发送、关联与读取；已有 Key 仅由配置使用，不打印或写入材料。历史真实回应不为连通测试批量上传。
- [ ] 对一条实际教学任务验证 thread／run 与业务任务、事件、产物版本关联；业务数据库仍是权威状态，trace 不承担授权或人类决定。
- [ ] 发送前执行配置的数据范围和受众策略，不泄露答案至学生流或把跨租户 Context 混入追踪。
- [ ] 记录当前已实现路径中成功、失败和停止任务的实际消耗；缺失费用或 token 如实记未知。后续回应／续作票扩展等待与跨恢复累计的实际用例，不让本票等待尚未实现的所有状态，也不新增预算优化门槛。
- [ ] 网络错误、限流和不可用情况下任务仍能完成或保持自己的停止原因，材料与检查可从业务接口取得；发送异常可诊断而不无限重试。
- [ ] 追踪能关联本地不可变案例／结果身份，后续评价执行器上线时无需重定义业务身份；本票不建设评价器或要求一次性提供全部能力数据集。
- [ ] 确定性、模型与人工判断在观察中保留来源；人工标注不自动转为教师回应或发布。
- [ ] 交付真实服务证据与本地故障结果，不能以旧的本地 HTTP 接收探针声称平台已接通。

## Reading and boundaries

读 [规格](../spec.md)、[LangSmith 研究](../../skills-harness/assets/langsmith-observability-evaluation-research.md)、[验证路线](../../skills-harness/assets/validation-and-release-route.md) 与 [既有质量裁定](../../skills-harness/experiments/grade8-linear-functions/quality-review.md)。

本票依赖已有真实任务，不依赖完整单元或五项能力齐备。第一票已经保留基础执行记录；本票增加平台关联。云端追踪、离线可重跑评价和内容质量达标分别验收。

## Comments

### 2026-09-15：开发期详细诊断前置到首票

按用户要求，首票补入可信维护者的原生消息／工具流、JSONL 保存和环境开关，并移除模型与启动脚本对 LangSmith 的硬编码关闭。生产默认关闭详细诊断，保留按配置开启的路径。外层状态可读，动态嵌套 Agent 的 checkpoint 独立回取尚未实现。详见 [实施证据](../evidence/01-live-curriculum/maintainer-diagnostics.md)。本票仍负责真实 LangSmith 发送／读取、业务身份关联、内容发送范围和观察故障验证；不能将配置开关与本地原生流通过当作平台验收。

### 2026-09-15：解除观察平台与评价的绑定

将质量回归／对照交给评价票；仍保留真实服务连通和故障解耦。本票不再阻塞 Skills 或 IM 评价工作。
