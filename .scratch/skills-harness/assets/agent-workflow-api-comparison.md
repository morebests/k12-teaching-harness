# Agent、固定编排与直接模型调用：本项目的比较边界

日期：2026-09-16。性质：官方资料核查与有限比较方案。本文没有运行付费模型、修改运行代码或证明任何方案教学质量更优。当前采用路线以 [README](../../../README.md) 为准；实际调用与错误由 [全年证据](../../math-harness-delivery/evidence/15-full-year-blueprint/README.md) 及本轮实现审计另行核对。

承接 [既有职责边界核查](react-and-workflow-boundaries.md)、[Context 设计](context-and-llm-design.md)、[执行结构](execution-structure-design.md)、[控制粒度研究](harness-control-granularity-research.md) 和 [数学课时详细流程](lesson-creation-execution-design.md)。原 Skill 的设计、验算、同源材料和修订目的必须保留；它们不要求使用某个特定 Agent 构造函数。[原教案 Skill](../../../k12-teacher-skills/plugin/skills/k12-lesson-plan-creation/SKILL.md)

## 结论

**已知必须执行的读取、保存、渲染和校验，由程序安排；需要依据新内容决定的补查、验算和探索，才有理由让模型选择。生成与审阅本身不构成必须使用 Agent 的理由。** 这是结合官方机制与本项目职责得到的建议，不是已完成的质量比较。

需要分别回答三件事：

1. 下一步由程序决定，还是由模型选择工具？
2. 模型实际收到哪些内容，由什么规则装配？
3. 通过 LangChain 模型适配器还是 Google SDK 发送同一调用？

三者相互独立。把 `create_agent` 换成手写模型—工具循环，仍然是 Agent 行为；把确定的工作排进 LangGraph，也不要求放弃 LangChain 模型适配器。比较时不能同时改变三项，然后把结果统称为“直接 API 更好”。

## 官方事实

### 1. Agent 选择动作，本地应用执行工具

Google 的自定义函数调用让模型返回函数名和参数，函数代码由应用执行，再把结果交回模型。LangChain 的基本 Agent 循环也是模型选择工具、执行工具、再次调用模型，直到不再请求工具。因此所谓“把工具改为本地执行”并非核心变化：它们本来就在本地应用中执行。变化在于执行时机和参数的决定权。[Google 函数调用](https://ai.google.dev/gemini-api/docs/function-calling#how-function-calling-works)、[LangChain Agent 循环](https://docs.langchain.com/oss/python/langchain/middleware/overview#the-agent-loop)

官方将预定路径称为 workflow，将动态决定过程和工具使用称为 agent；LangGraph 同时支持这两者。节点可为普通函数、一次模型调用或完整 Agent，允许混合。[Workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents)、[Custom workflow](https://docs.langchain.com/oss/python/langchain/multi-agent/custom-workflow)

### 2. 不用 Agent 也能调用同一个 LangChain 模型

LangChain 明确支持单独使用模型，直接调用适合生成、分类和提取等任务。Google 集成提供 `with_structured_output(method="json_schema")`，通过 Gemini 原生结构化输出约束返回；另一种 `function_calling` 方法通过工具调用提取结构化数据。官方集成建议前者用于更可靠的结构化输出。[Models](https://docs.langchain.com/oss/python/langchain/models#basic-usage)、[Google 结构化输出集成](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#structured-output-methods)

因此可以先验证 `LangGraph 节点 → 同一 ChatGoogleGenerativeAI → 结构化结果 → 程序保存`，而无须同时迁移 HTTP API、SDK、服务运行与追踪机制。此项为项目实现推断；具体大型课程 Schema 仍须通过本项目锁定版本和实际请求验证，不能只凭文档示例宣布兼容。

### 3. 掌握 Context 不要求弃用 `create_agent`

官方 Context engineering 区分实际发送给模型的瞬时 Context 与持久状态；`wrap_model_call` 可按次改变消息、提示、可见工具和响应格式，而不必改写保存的全部历史。Middleware 在 `create_agent` 编译的 LangGraph 内执行，完整 Agent 可嵌入更大的工作流。[Context engineering](https://docs.langchain.com/oss/python/langchain/context-engineering)、[Middleware 与工作流](https://docs.langchain.com/oss/python/langchain/middleware/overview#use-middleware-inside-a-langgraph-workflow)

这意味着“每轮总是发送不断增长的全部历史”是当前实现可以改进的策略，不是 Agent 的不可消除属性。是否需要当前全文、问题列表、关联目标、原始知识记录或更多按需材料，应按当前工作决定；不能以减少输入为名丢失必要依据。该建议沿用本仓库 [Context 约定](context-and-llm-design.md#把参考变成实际可装配的运行资源)。

### 4. 直接 Google SDK 也可能包含自动循环

Google Python SDK 的 `generate_content` 可以直接接收 Python 函数并自动调用、回传；也可以设置 `automatic_function_calling.disable=True`，由应用处理返回的函数调用。手动声明支持 `parameters_json_schema`。因此一行 SDK 调用不一定等于一次模型请求，原生 SDK 也不自动等于固定工作流。[官方 Python SDK](https://googleapis.github.io/python-genai/#function-calling)

若目标是自己精确安排调用，应明确关掉 SDK 自动函数循环，或只提交函数声明并接管循环；不能让图、Agent 和 SDK 各自管理重试与后续调用。这里是实现建议，本文没有更改本项目配置。

### 5. Schema 能限制结构，不能替代语义检查

Gemini 的结构化输出仅支持 JSON Schema 子集，支持枚举；官方要求应用继续检查取值及语义错误。`generateContent` 的函数声明还区分 `parameters` 与 `parametersJsonSchema`，两者互斥。不能假定 Pydantic 的全部约束经过适配器后仍原样存在。[Structured outputs](https://ai.google.dev/gemini-api/docs/structured-output#json-schema-support)、[FunctionDeclaration](https://ai.google.dev/api/generate-content#FunctionDeclaration)

`generateContent` 的函数模式包含 `AUTO`、`ANY`、`NONE`、`VALIDATED`；`VALIDATED` 保留自然语言或工具选择，同时约束函数参数格式。这不能恢复在发送前已丢失的约束，也不能保证 LaTeX 可渲染、课程目标正确或数学解释成立。[FunctionCallingConfig](https://ai.google.dev/api/caching#FunctionCallingConfig)

本次查阅时 Google 指南中的许多示例已改为 Interactions API，使用 `tool_choice`、`response_format` 等参数；本项目已有调用使用 `generateContent`。两套接口应按各自 API 参考核查，不能直接复制不同端点的参数。本文不以此启动 API 迁移。

### 6. 推理延续、缓存与 Agent 是不同机制

`generateContent` 的 `thoughtSignature` 是用于后续请求的不可解释签名；函数请求与返回还需保持对应身份。Interactions 的有状态模式可由服务维护这些信息，无状态模式要求保留相应返回块。手写循环增加了正确保留这些信息的责任，并不自动提高模型效果。[Content 与 Part](https://ai.google.dev/api/generate-content#Part)、[Thinking 与签名](https://ai.google.dev/gemini-api/docs/thinking#thought-signatures)

隐式缓存默认适用于官方说明覆盖的 Gemini 模型；重复前缀有助命中，实际命中看用量。Interactions 当前只支持隐式缓存；显式缓存需使用 `generateContent`。缓存能力不以 `create_agent` 是否存在为开关，也不等于复用已经产出的课程成果。[Gemini 缓存](https://ai.google.dev/gemini-api/docs/caching)

## 对本项目的具体推断

以下是候选分工，需与本轮代码及轨迹审计合并；不表示每行必须独立创建一个图节点。

| 工作 | 建议控制方式 | 模型仍应决定什么 |
| --- | --- | --- |
| 固定 CCSS、年级范围、分页、身份与完整性 | 程序直接读取并记录证据 | 怎样利用目标组织课程；不能决定是否跳过必需范围 |
| 取本次实际父产物、当前稿、有效检查及规则 | 程序装配可核对的 Context | 发现不足时请求读取相关正文；不必反复请求已装配的同一全文 |
| 因设计需要补查 LC、进阶或邻接目标 | 模型提出有目的的请求，程序核验并执行 | 查询对象、需要解决的判断、采用理由 |
| 构造题目、选择表征、提出计算式或绘图参数 | 模型创作，有限工具执行 | 具体数学设计及修订；不预写所有参数 |
| 对已知公式、图件、目标覆盖执行必需检查 | 程序安排实际检查 | 对具体失败解释、修正或举证说明误报 |
| 保存规范内容、加入系统身份、渲染、指纹和送审 | 程序执行；模型返回候选正文或修改 | 哪些教学内容改变；不决定系统身份与检查是否跳过 |
| 独立审阅一份确定的稿件 | 优先验证一次结构化审阅调用；允许明确回报缺证据 | 教学问题、数学反例、依据与严重程度；必要补查可形成后续请求 |
| 根据检查结果决定修订、重新检查和交付 | 图控制条件和版本 | 完成实际修订；不能自报通过取代检查 |

特别是“生成”和“审阅”仅描述任务。若阶段拥有充分输入，只需返回内容或发现，一次模型调用可能足够；如果需反复试做、观察工具结果并决定下一步，动态循环可能有价值。把整个全年 LC 全库提前塞入 Context 同样可能浪费资源；应先装配确实必需的信息，保留有目的的补查。

## 如何减少同类错误

应修复产生错误的边界，而不是只加一句“以后不要犯”。以下是建议，具体已实施项由本轮代码审计确认。

1. **固定值由程序负责。** 若 `id`、`kind` 已由请求范围唯一确定，模型没有作决定的必要，可从生成负担中去除，在规范化保存时由程序加入；仍须拒绝跨层内容错误。若确需模型输出该字段，则以实际发出的 Schema 核查单值枚举、必填项及类型，不能仅检查源 Pydantic Schema。
2. **检查真实传输契约。** 用不联网的适配器回归测试核对发送给 Gemini 的工具／输出 Schema；再做最小真实兼容性验证。`const` 丢失首先是适配边界问题，不能归咎于模型没有服从它未收到的限制。
3. **数学格式给出短而明确的规则。** 区分模型生成的逻辑字符串、JSON 序列化和 Markdown／LaTeX 解析；尽量让序列化由程序负责。给模型具体字段位置、问题片段及期望形式，保留原内容进行局部修订。不要在每次提示复制整套 Schema 或堆积全部历史错误。
4. **把失败变成可复用回归样本。** 固定值、双重转义、数学标记外命令分别检测；渲染失败阻断交付并回到修订。一次修好只能证明该稿被修好，不能证明模型已永久记住。跨运行改进依赖新的有效 Schema、版本化规则、具体反馈和检查，而不是依赖旧任务中的纠错对话。

第三项与 Google 建议的字段说明、应用校验一致；SDK 文档还提醒不要在输入提示中重复完整输出 Schema／JSON 范例。这不是禁止用短局部示例说明容易混淆的数学字符串。[结构化输出建议](https://ai.google.dev/gemini-api/docs/structured-output#best-practices)、[SDK JSON Schema](https://googleapis.github.io/python-genai/#json-response-schema)

## 怎样证明，怎样不能证明

### 先做无需付费模型的核验

- 用实际发送配置证明字段约束是否到达提供方；用固定错误对象证明本地检查会拒绝它、反馈包含实际字段和原因。
- 从已有轨迹区分必要固定操作、依据内容选择的操作、重复读取和失败修复。可以统计省去某个固定工具请求的理论调用上界，但不能据此声称新方案一定节省对应 token 或保持质量。
- 用固定模型响应检查两个执行器的保存、来源校验、渲染与送审版本一致性。这证明工程路径，不证明真实模型会生成相同内容。

### 只比较当前决定，不先建两套完整系统

建议先抽出已有的一份真实稿件与有限修订任务，例如纠正一个含公式的探查并保持目标、前后联系和其他单元；再用一个必须补查依据的任务检查固定流程是否过度受限。先取得可比较的最小执行路径，不重新从零生成三份全年课程来回答局部编排问题。

| 变体 | 改变的变量 | 共同保持 |
| --- | --- | --- |
| A：修正已知契约后的 `create_agent` | 阶段内仍由模型选择工具与结束 | 同一模型／版本、参数、适配器、初稿、资料快照、规则、检查、实际允许动作 |
| B：显式 LangGraph 调用 | 固定准备与保存由程序执行，模型返回结构化内容／补查需求，程序继续相应节点 | 与 A 相同信息权限和质量目标；不删验算、独立审阅或修订 |
| 后置 C：原生 Google SDK | 仅在适配器仍有已证实能力缺失时，单独比较传输层 | 固定 B 的图、实际消息和规则；不同时迁移 API 端点、缓存策略或更换模型 |

A 必须先修复已知 Schema 缺陷，不能拿故障基线给 B 制造优势。若 B 的改动包括分阶段装配 Context，则明确称为“编排＋Context 策略”的比较；要归因于哪一项，继续逐项增减，而不是同时修改提示、模型、知识量和检查条件。

双方拥有同一份可取得的证据，不要求动态执行最终查询顺序完全相同；应比较是否取得作出判断所需的真实证据。若强制使用固定证据包进行第一轮比较，结论仅覆盖资料已充分的任务，不能推广到开放检索。

### 评价与结束条件先固定

1. **首要结果：**数学正确、层级职责正确、目标—任务—证据一致、修订保真、来源可核对、最终材料可用。已有严重问题未修或新引入问题，不能靠平均分抵消。
2. **执行结果：**完成率、首次保存成功率、修复轮数、重复查询、遗漏必需检查、错误来源声明、审阅漏报及不必要阻断。
3. **消耗：**逐调用的输入、输出、思考与缓存分项，模型及工具次数、耗时和人工介入；按实际提供方语义去重。缓存 token 不额外叠加到输入总数，也不把总 token 直接当账单费用。[Gemini 用量定义](https://ai.google.dev/api/generate-content#UsageMetadata)
4. **可比性：**任务成对、运行顺序交错、独立线程、多次重复；两方遵守相同停止政策并保留失败，不增加未经授权的累计 token 预算。缓存命中可能不同，需单列而不宣称完全受控。答案和评价标签不提前给模型。
5. **裁定：**在相同关键质量要求下，确认较少失败、冗余或维护负担，才支持采用；结果波动或样本不足则保留不确定性。小样本足以否定明显错误路径，但不能证明普遍非劣、真实教师体验或课堂学习效果。审阅模型的自评分不能独自作裁判。

## 本轮证明范围

官方资料足以确认两类实现都可行、Context 可由应用掌握、结构约束与业务校验必须分开，也足以反驳“生成／审阅必然需要 Agent”或“换成原生 API 必然更好”。它们不提供本项目的效果答案。

下一步应先依据真实轨迹剥离确定的程序职责，并保留可检查的阶段输入；再用上述有限配对验证剩余动态循环的价值。Agent 去留、Context 装配和 API 迁移分别取证，避免一次全面重写后仍然不知道哪个变化有效。
