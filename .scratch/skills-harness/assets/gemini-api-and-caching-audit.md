# Gemini API、会话延续与缓存核查

日期：2026-09-16。代码基线：`ccdf3c8`。这是对官方资料及锁定依赖的只读研究，不是 API 迁移决定。未调用付费模型、创建缓存或读取 `.env`；实际运行的缓存命中和草稿复用链由同轮原生 trace 审计另行核对。

## 结论

当前 Harness 使用 Gemini `generateContent`／`streamGenerateContent`，没有使用 Google 的 **Interactions API**，也没有主动建立显式缓存。现有适配器已经支持 `cached_content`，应用尚未使用；同一适配器会保留供应商返回的缓存命中数，但应用的累计摘要只收集输入、输出和总 token，漏掉了缓存分项。源码依据见下表。

Google 提供自动隐式缓存，因此“没有创建显式缓存”不等于“没有享受缓存”。是否命中须看每次供应商返回的用量；本报告不根据默认配置推定某次运行已命中。服务端会话延续、提示缓存和 LangGraph 检查点分别解决不同问题，不能互相替代。

## 一、当前调用到底走哪条路径

锁定依赖为 `langchain-google-genai 4.4.0` 和 `google-genai 2.23.0`，见 [uv.lock](/Users/libo/Mathematics/k12-teaching-harness/uv.lock:291) 与 [适配器锁定项](/Users/libo/Mathematics/k12-teaching-harness/uv.lock:646)。以下是实际安装源码的定位，不以最新版文档代替已运行版本。

| 核查对象 | 已核实事实 | 本地依据 |
| --- | --- | --- |
| 模型构造 | `ChatGoogleGenerativeAI` 默认 `gemini-3.8-flash`，配置 key、重试、单次输出长度和超时；没有 `cached_content` 或 interaction ID | [graph.py](/Users/libo/Mathematics/k12-teaching-harness/src/teaching_harness/graph.py:193) |
| 作者与审阅者 | 两个 `create_agent` 共用模型接口，审阅使用 `ToolStrategy(Review)`；这里的 response format 不是供应商的 Responses／Interactions API | [graph.py](/Users/libo/Mathematics/k12-teaching-harness/src/teaching_harness/graph.py:208) |
| 异步生成 | `_agenerate` 调 `async_client.models.generate_content` | [chat_models.py](/Users/libo/Mathematics/k12-teaching-harness/.venv/lib/python3.13/site-packages/langchain_google_genai/chat_models.py:4187) |
| 异步流式 | `_astream` 调 `async_client.models.generate_content_stream` | [chat_models.py](/Users/libo/Mathematics/k12-teaching-harness/.venv/lib/python3.13/site-packages/langchain_google_genai/chat_models.py:4291) |
| 显式缓存接口 | 适配器定义 `cached_content: str \| None`，默认空；构造 `GenerateContentConfig` 时向 Google 透传 | [参数定义](/Users/libo/Mathematics/k12-teaching-harness/.venv/lib/python3.13/site-packages/langchain_google_genai/chat_models.py:3278)、[请求构造](/Users/libo/Mathematics/k12-teaching-harness/.venv/lib/python3.13/site-packages/langchain_google_genai/chat_models.py:4132) |
| 缓存用量 | `cached_content_token_count` 被映射为 `AIMessage.usage_metadata.input_token_details.cache_read`；输出 token 包含思考 token，另保留 reasoning 分项 | [用量映射](/Users/libo/Mathematics/k12-teaching-harness/.venv/lib/python3.13/site-packages/langchain_google_genai/chat_models.py:2040) |
| 应用汇总 | middleware 只累计 `input_tokens`、`output_tokens`、`total_tokens`，所以简报总数不能显示普通输入与缓存输入的费用差异 | [execution.py](/Users/libo/Mathematics/k12-teaching-harness/src/teaching_harness/execution.py:189) |

只读搜索范围 `src/teaching_harness` 未发现 `cached_content`、`previous_interaction_id` 或缓存创建调用；安装的 `langchain_google_genai` 包没有 `interactions` 路径。底层 Google SDK 已有 [interactions.py](/Users/libo/Mathematics/k12-teaching-harness/.venv/lib/python3.13/site-packages/google/genai/interactions.py)，但 SDK 具备功能不表示上层适配器已经调用。

LangChain 官方集成给出的显式缓存方式也是先调用 `client.caches.create`，再将返回的 `cache.name` 交给 `ChatGoogleGenerativeAI(cached_content=...)`；没有承诺该参数会替应用自动建立或维护缓存。[LangChain 官方 Context caching 示例](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai#context-caching)

## 二、用户说的“response API”应对应什么

本次核查的 Gemini 原生接口叫 **Interactions API**。Google 当前概览明确：2026 年 6 月起已正式可用，建议新项目使用；`generateContent` 虽标记为 legacy，仍受支持。这是截至核查日的事实，不能沿用此前“Interactions 仍在 beta”的旧判断。[Google Interactions 概览](https://ai.google.dev/gemini-api/docs/interactions-overview)

`previous_interaction_id` 让服务端回取既有输入与输出，客户端无需重传完整对话。它不继承每轮的 `tools`、`system_instruction`、`generation_config`，这些仍须重新指定。默认 `store=true`；付费档默认保存 55 天、免费档 1 天，关闭存储会影响后续 ID 延续。官方建议利用此机制改善隐式缓存命中，但尚不支持显式缓存。[状态管理、保存与限制](https://ai.google.dev/gemini-api/docs/interactions-overview#server-side-state-management)

减少传输不等于历史 token 免费。官方多轮计数示例对第二轮使用 `previous_interaction_id`，并明确用量包含两轮内容；接口仍返回总输入、缓存输入、输出及思考用量。因此费用判断应使用具体用量和相应价格，不能把 interaction ID 当成只付新增一句话的钱。[官方多轮 token 计数](https://ai.google.dev/gemini-api/docs/tokens#count-multi-turn-tokens)、[Interactions 用量字段](https://ai.google.dev/api/interactions-api-v1)

迁移涉及消息与工具结果格式、流事件、状态 ID 和数据保存语义，不是把现有 `response_format` 改名。官方迁移文档有生成、流式、工具及多轮的分别改法。[官方迁移指南](https://ai.google.dev/gemini-api/docs/migrate-to-interactions)

## 三、自动缓存与显式缓存

| 机制 | 需要应用做什么 | 怎样确认 |
| --- | --- | --- |
| 隐式缓存 | Gemini 2.5 及以上默认启用；将稳定、较大的共同内容放在前面，短时间内保持相似前缀可增加命中机会；不保证每次命中 | `generateContent` 的 `usage_metadata.cached_content_token_count`；Interactions 的 `usage.total_cached_tokens` |
| 显式缓存 | 主动创建缓存对象并引用其名称，管理适用模型、内容版本、TTL 和过期；当前用于 `generateContent`，Interactions 不支持 | 缓存对象存在及实际生成响应的缓存用量 |

官方当前表明确列出 `Gemini 3.8 Flash` 的最低缓存输入长度为 **4,096 tokens**；2.5 Flash／Pro 为 2,048。大于阈值只说明满足长度条件，不保证隐式命中。[Interactions 缓存文档](https://ai.google.dev/gemini-api/docs/caching)

显式缓存目前为 beta（`v1beta`），默认 TTL 为 1 小时，可自行设置。缓存作为输入前缀参与模型上下文，仍计入 token 限制；缓存读取、非缓存输入、输出及保存时长分别影响费用。短暂或不再复用的内容不应未经测算就长期保存。[generateContent 缓存说明](https://ai.google.dev/gemini-api/docs/generate-content/caching?hl=en)

截至 2026-09-16，官方 `gemini-3.8-flash` Standard 付费档每百万 token 为：普通输入 **$0.75**、缓存输入 **$0.075**、输出（含思考）**$3.75**；显式缓存保存费为每百万 token 每小时 **$0.50**。页面注明这些价格适用至 2026-12-31。这里是公开标价，不是账户实际账单；本次没有核对账户档位或折扣。[Google 价格页](https://ai.google.dev/gemini-api/docs/pricing#gemini-3.8-flash)

按上述 Standard 档、纯文本、无其他收费工具推算，生成费用可估为：`(输入 − cache_read) × 普通输入价 + cache_read × 缓存输入价 + 输出 × 输出价`；显式缓存另加保存费。**这是条件性估算公式。** `total_tokens` 本身不扣去命中部分；直接用总 token 乘普通输入价会错误估计费用。

## 四、对本项目的建议与验证边界

以下是研究建议，尚未实施，也未改变既定技术路线：

1. **先补齐用量展示。** 现有 adapter 已有缓存分项，先将原生 trace 中的 `cache_read` 与实际输入、输出、reasoning 分开核对；避免用一个总 token 数声称费用或节省。未知值保持未知。
2. **保持已验证的上下文与草稿延续。** API 缓存是重复输入的计算／计费优化，不会替代已保存课程、图件、检查结果和 LangGraph 阶段状态。更换 API 不会自动找回当前 `generateContent` 请求对应的 Interaction ID。
3. **按稳定前缀做小范围实测。** 固定规则、允许共享的知识包和内容版本可作为缓存候选；作者、审阅和隔离读题的可见范围继续分别控制。不能为命中缓存把答案或无关历史送给不该看到它的检查者。
4. **迁移先验证适配，不先改全图。** 如选择 Interactions，应先对现有一组工具往返验证消息延续、工具结果、结构化审阅、流事件、取消、用量和检查点恢复。官方的新项目推荐值得采用评估，但不能直接声称现有 LangChain 4.4 adapter 已支持，也不能把 Interactions 的服务端历史当成 LangGraph 业务恢复。
5. **显式缓存与 Interactions 分别比较。** 当前 generateContent 已能使用显式缓存，Interactions 侧则通过会话 ID 改善隐式缓存；并非必须先迁移才能获得任何缓存收益。是否需要主动缓存应以当前真实命中率、内容复用频率及 TTL 成本决定，不能仅凭长 prompt 就断定收益。

本报告证明的是官方能力与当前接入缺口。没有执行 API 对照实验，不宣称迁移后一定更省、不宣称所有旧 token 都白费，也不据后续较小修订任务的消耗推断从零生成的消耗。
