# Learning Commons KG 如何作为后端运行依赖接入

Type: research
Labels: wayfinder:research
Mode: AFK
Status: resolved
Assignee: li3p
Blocked by:

适用状态：历史远程接口研究，已退出当前架构前置条件。用户明确本地数据由其他项目提供；当前设计依据为 [本地 Learning Commons 图的教学设计用法](../assets/learning-commons-integration.md)。以下保留原问题与当时结论，不要求重新开通服务或验证下载路径。

## Question

核对上游插件配置与各 Skill 的 KG 指导，并根据 Learning Commons 官方资料确认 Web 后端可用的连接方式、认证与访问前提、工具协议及接口兼容问题。

重点教案创建：标准与课程检索在何时发生、返回数据如何支撑教学设计、未连接／无结果／请求失败如何区分。梳理其他三项的不同使用要求，不形成统一 KG 调用链。

区分可由公开资料确认的接入方式、需配置外部账户或凭据的前提，以及必须真实连接才能验证的未知。没有授权或凭据时不尝试私有访问，不虚构已连通或可匿名使用的结论。

## Context

- [Skills Harness 实现架构地图](../map.md)
- [四项 Skills 的完整实现需求与首项建议](../assets/harness-scope-and-priority.md)
- [上游 KG 配置与引用](../../../k12-teacher-skills/README.md)

## Comments

### Resolution

当时完成公开官方资料与本地上游规范核查。原报告由下述临时研究 worktree 保留，assets 中同名报告现已重写为本地图使用研究。

官方提供带 API key 的 MCP 与 REST。公开 MCP 文档列出标准、组件、进阶三类工具，不能据此证明上游数学教案所需的误解、课时与完整材料查询均已可用；REST 参数语义、层级结构和材料覆盖也需适配验证。课程元数据与教学材料的访问范围不同。

本次未读取凭据或调用 KG 数据接口，实际权限、完整工具集及材料覆盖仍待验证。原始报告位于临时研究 worktree `/private/tmp/k12-kg-runtime-20260914` 的 `codex/research-kg-runtime` 分支，已复制到本地图 assets。

用户提出“AI 辅助生成后人工确认”作为材料来源候选。该路径进入教案创建流程分析；它可以满足原创教学材料需求，但不据此声称取得了原课程材料或 KG 研究记录。

### 当前前提取代历史接入问题（2026-09-14）

用户提供另一项目已完成的本地数据与研究。已以只读模式核验实际数据库中的几何目标、LC、学习进阶和 IM 课程层级；当前问题是怎样用图支撑独立课程设计，远程权限、连接与材料缺口不再作为该设计的假设障碍。原有“因获取不到而增加审阅”的待确认方案撤回。
