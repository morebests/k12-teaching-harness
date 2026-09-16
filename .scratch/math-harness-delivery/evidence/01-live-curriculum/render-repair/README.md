# token 计量纠偏与真实材料修复

日期：2026-09-16。对应[首票](../../../issues/01-live-curriculum-task.md)、[五阶段图](../../../ticket-01-graph-refactor-design.md)。旧失败记录[保持原样](../graph-refactor/README.md)。

## 结果

最终任务 `474e1282-96b7-5b94-88b3-cc3fe0aa6a12` 已完成：`completed`、`rendered=true`、`checks.passed=true`、无未解决项。交付仍为八年级 8.F.B.4 的三课时方案与三项关键任务，不是全年或完整课时材料包。

- [实际 HTML 阅读稿](final/output/curriculum.html)、[唯一 JSON 源](final/content/curriculum.json)、[SVG 与生成参数](final/assets/rainwater_tank.json)。
- [API 结果及当前指纹检查](final/api-result.json)、[检查文件](final/checks.json)。
- [完整工具请求、返回、关联和顺序](final/tool-calls.json)、[执行阶段及实际用量](final/execution-summary.json)、[Context](final/context.json)、[LC 查询审计](final/knowledge-audit.json)。
- [两轮文件指纹与浏览器检查结果](verification.json)、[代码审查](review.md)、[自动化验证](pytest.txt)。

最终源／图／输出整体指纹为 `3fb1c9789e4434372ca89ecd3a61b954e22b662c06de6cf9b039ba05c58e5787`；HTML SHA-256 为 `204e734e99c0f4769bf548a95103909dfc7fefc21fcb70c352a5ddb967a4d631`。补充格式校验后，使用最终代码重新渲染两个真实样本，输出逐字节等于原生任务保存的 HTML。

## 原因与修复

**180 万 token 阈值由开发者写进调用示例，非用户指定，也非 Gemini 或 Agent Server 的限制。** 另用消息字节数加常数估算下一次调用预留空间，使上轮在实际累计 1,655,352 tokens 时提前停止。这偏离了先做质量、再观察消耗的约定。现在默认 `limits.total_tokens=null`，示例不设置累计阈值，删除字节估算和动态压缩输出。仍记录供应商实际用量；只有明确传入阈值才在新增调用前核对，已经完成的审阅可继续进行纯程序提交。

Gemini adapter 已提供 `get_num_tokens(text)`，锁定版本 `langchain-google-genai==4.4.0` 的实现调用供应商 `count_tokens`。实测文本 `Explain the slope of y = 3x + 5.` 为 13 tokens。这个文本包装并不覆盖完整请求的 system instruction 与工具声明；调用后以 `usage_metadata` 记录实际输入、输出及总用量。输出计数包含思考用量，无法事前精确预测。依据：[Google token API](https://ai.google.dev/api/tokens)、[Google 计数说明](https://ai.google.dev/gemini-api/docs/tokens)。本次不建设精确预算分配框架。

**“排版失败”实际是公式解析失败。** 最小反例为同一段落的 `$x$\n$$y$$\n解得 $b$`：原解析器未启用段落内双美元支持，把后续中文“解得”错配为公式，KaTeX 因中文处于数学模式报错。增加段落空行能消除症状；单独移除缩进或换成简单公式不能消除，因此不是某个数学解答错误。修复使用解析器已有的 `double_inline`，没有关闭 KaTeX 严格校验。

原保存路径吞掉具体错误，只返回 `rendered=false`。现在 `render_errors` 包含源字段、实际公式和原因，绑定当前源／图件指纹；工具返回与送审反馈均可读取，修源重新保存成功后清除。未配对公式、常见命令重复转义也有回归反例。独立金额 `$5` 的语法歧义按金额处理，普通美元字符可显式转义。JSON 日志中显示的双反斜杠不等于实际字符串重复转义；逐字节核对后，真实样本没有证明存在此类错误，不能把它列为本次事故根因。

参考的是上游[教案 Skill §5](../../../../../k12-teacher-skills/plugin/skills/k12-lesson-plan-creation/SKILL.md) 与[输出规范](../../../../../k12-teacher-skills/plugin/skills/k12-lesson-plan-creation/references/output.md)的执行机制：同一内容源、修源、重新生成、检查实际输出后交付。当前有限切片采用 JSON／HTML／SVG，未移植完整 Word 包；保存草稿不能替代修复和验收。

## 两轮真实工作与消耗

均经独立的原生 Agent Server dev、正式五阶段图、Gemini `gemini-3.8-flash` 和 LC `lc/v1.11.0` 执行；`limits.total_tokens=null`。它们是通过外部内容入口提交的新任务，**不是旧 run 恢复**。原开发服务 2024 未热替换。

| 任务 | 实际工作 | 模型调用 | 工具调用 | 输入 token | 输出 token | 总 token | 活动秒数 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| [格式修复](format-pass/api-result.json) | 采用上轮草稿，生成实际图件、保存阅读稿并独立审阅 | 8 | 11 | 388,801 | 21,654 | 410,455 | 66.33 |
| [最终修订](final/api-result.json) | 走查发现后修订假设、外推条件、问题编号和读图题面，再渲染与独立审阅 | 11 | 13 | 510,181 | 23,642 | 533,823 | 82.99 |
| 本轮合计 | 两次接续修订 | 19 | 24 | 898,982 | 45,296 | 944,278 | 149.32 |

若合计旧图重构失败任务的 1,655,352 tokens，这份草稿从那次生成到当前稿，三个 run 共 2,599,630 tokens、49 次模型调用、50 次工具调用。不同 run 的 Context 会重复，不将本轮修复用量冒充从零生成成本，更不由一个样本推定生产额度。费用未知，保留 null。

### 补充核查：缓存分项与内容接续

2026-09-16 从三个 run 的原生完整 AIMessage 用量抽取并按消息 ID 去重，保存 [逐调用缓存审计](cache-usage-audit.json)。原失败任务的缓存输入为 1,275,512／1,569,550（81.3%）；格式修复为 216,664／388,801（55.7%）；最终修订为 330,708／510,181（64.8%）。**隐式缓存实际生效；此前汇总遗漏了缓存分项。** adapter 已保留 `input_token_details.cache_read` 与 `output_token_details.reasoning`，当前应用 Ledger 尚未累计展示这两项。

缓存输入包含在总输入中，思考包含在总输出中，不另加也不从总用量删除；账单须按实际档位和各分项判断。后两次 run 通过 `--source` 复用上一稿 JSON，未复用旧 Agent 消息或旧 run 的 checkpoint。410,455 tokens 对应已有草稿的较窄修复和更少调用，不能解释为缓存提高或从零生成效率提高。旧成果被复用，但错误停止及后续重复工作确有额外消耗，不能把所有费用都合理化。接口事实见 [Gemini 核查](../../../../skills-harness/assets/gemini-api-and-caching-audit.md)。

首次修复中出现一次模型发出的无效工具名，模型收到真实错误后改正；最终修订中两次把路径或扩展名传入图件 name，第三次改为 `rainwater_tank` 后成功。错误均保留，没有从计量或工具记录中抹掉。依据这次事实补充了工具 name 的说明和错误示例；该提示改进未重新消耗模型做专项优化测试。

最终作者 Agent 请求顺序：读取空稿 → 两次错误图件名 → 创建图件 → 六次数值核算（15、40、25、25、350、6）→ 保存 → 回读成功阅读稿。审阅 Agent 单独计算 `12*6+20=92`，随后提交无阻断的结构化 `Review`。同批独立工具可能并行，记录分别保留请求和返回顺序；`Review` 是结构化输出，不混入实际工具次数。

## 实际材料与视觉检查

首次阅读稿已经显示正常公式，但走查发现模型漏检的内容：把未诊断先备说成已经掌握、未说明数据外推假设、预判回应编号与实际题目不一致、读图题面直接给出了应由学生读取的坐标。最终稿针对这些反馈修源，并重新接受隔离审阅：

- 先备与常见困难在 Narrative 中明确为待核对假设。
- 表格数据与线性模型的一致性，和实际过程持续线性的假设分别表述；题面提供 0—12 小时恒定充电、容量至少 350 Wh 的条件。
- 读图题面保留格点提示，坐标留给学生读取；答案与教师支持保留真实坐标。
- 图像横轴 0—5、步长 1；纵轴 0—100、步长 20；直线通过 (0,20)、(5,80)。求装满时间为 (92−20)/12=6 分钟，与题解一致。

使用本机只读 HTTP 服务和 Codex 浏览器实际打开最终 HTML。1280 像素视口检查：120 个 MathML 公式、20 个分式、1 张表、1 个 SVG；公式／表／图无横向溢出，未显示原始 LaTeX 命令。实际截图观察了连续公式、分式、乘号、表格与函数图，检查正文不再被误吸入公式。这是桌面阅读稿走查，未证明打印分页、不同浏览器兼容、教师校准或课堂学习效果。

## 回归与观察范围

最终自动化验证为 65 项测试通过（32.56 秒），Ruff、mypy 与差异空白检查通过。

回归覆盖同段连续块公式、错误定位、修复后错误清除、未闭合／重复转义反例、金额和代码、合法 aligned 换行；累计 token 默认只计量、显式阈值、最终审阅跨阈值后仍提交。保留原阶段接续、取消、并行工具计量及诊断权限测试。

原生详细流保存在本机 `work/render-repair-live/trace.jsonl` 与 `work/render-repair-final/trace.jsonl`（0600、忽略跟踪）；归档只提取工具参数／返回、模型用量及阶段证据，不保存供应商内部签名。此次验证的 LangSmith 发送在独立进程中关闭，未修改用户 `.env`，不声称已验证平台 trace 页面。
