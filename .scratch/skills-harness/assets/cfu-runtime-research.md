# LangGraph 承载 CFU 暂停、恢复与文件验证顺序

**定位：运行机制与候选结构参考。** 保留完整研究、CFU 语义及候选划分供比较；它们尚未成为本项目选定架构，也没有原型结果。教学流程的原始分析继续保留，实际采用方式由当前 Context、LLM 与执行设计确定。

查阅日期：2026-09-14。范围：LangGraph Python OSS 当前官方在线文档，以及 CFU 已知执行要求。
关联问题：[LangGraph 如何承载理解度检查的暂停恢复与文件验证顺序](../issues/08-cfu-runtime-research.md)。

本研究未安装、锁定或运行 LangGraph；在线文档不是版本快照，不能据此承诺某个已发布包版本完整具备所有所述行为。
后续已完成 [锁定版本的持久运行探针](cfu-durable-prototype-results.md)，具体证据与限制单列；不倒写本次研究为实测。
实施原型时须锁定 LangGraph、checkpointer 及模型集成包版本，再复核对应接口。本次没有代码实验、模型调用或材料生成。
CFU 来源基线为上游提交 `281eb8d41fe2837d911541c9bbb870b58add804c`；框架事实取自官方指南，未以未经核验的源码细节补足保证。
`durable-execution` 旧地址在本次查阅时重定向到 [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)；具体语义现分布在下文链接的独立页面。

结论：LangGraph 能提供持久化暂停、指定 thread 恢复及已保存工作结果的复用。
CFU 的教师决定关联、验证规范何时可读、两份文件的一致版本，以及交付是否对应已验证内容，都需要 Harness 自行实现。
checkpoint 不等于外部文件的 exactly-once 写入，也不等于文件事务、资源访问权限或教学流程版本保证。

## CFU 必须保留的边界

以下为 [CFU 主规范](../../../k12-teacher-skills/plugin/skills/k12-check-for-understanding/SKILL.md) 的要求，并非框架能力：

- Step 0–2：先读取数学参考；必要澄清最多一问；连接 KG 时按参考先取标准依据。
- Step 3：提出焦点、约束和理由后停住，等教师回答；明确改向则采用其选择并重述，不额外增加一次确认。
- Step 4–5：按确认范围造题，完整读取输出规范，然后实际写出学生版和教师版。
- Step 6：只有两份文件都存在后，才能完整读取 `references/verification.md`，随后回读两份文件并执行两道检查。
- 验证发现问题后修复、重写；通过后才交付。Step 7 邀请具体修改，但未把教师回复“满意”设为交付前条件。

本报告保留“两份材料实际写出”的前提，不用内存草稿或 `files_written=True` 自述替代。
原始规范中的无输出目录等适配歧义仍在能力契约草案中；本研究不决定这些例外，也不统一其他 Skill 的教学流程。

## 官方事实及直接工程含义

### 1. 暂停与 Web 后端恢复

**官方事实。** `interrupt(payload)` 需要 checkpointer 和 `thread_id`；payload 应可 JSON 序列化。
调用方收到中断内容后，用同一 thread 调用 `Command(resume=answer)`；`answer` 成为节点内 `interrupt()` 的返回值。
默认 `invoke()` 在 `__interrupt__` 返回中断信息。
来源：[Interrupts：Pause、Resuming](https://docs.langchain.com/oss/python/langgraph/interrupts#resuming-interrupts)。

**CFU 含义／应用推断。** 后端可返回焦点提议及待答请求，结束这次执行请求；教师回应到达后再恢复图。
等待教师不需要持续占用一个 HTTP 请求。界面展示、回应接收及调用恢复接口由 Web 后端适配。
建议保存提议编号／版本及当前待答请求；将教师回应与它们核对后才传给 `Command(resume=...)`。
`thread_id` 是定位运行状态的标识；仅知道它不构成回应者的权限证明，也不能证明回应针对当前提议。
这里的关联校验由 Harness 与调用方接口承担，不扩展到学校身份系统设计。

### 2. 恢复位置是节点入口

**官方事实。** 恢复时，中断所在节点从头运行，`interrupt()` 之前的代码再次执行。
若节点内以函数方式调用含中断的子图，父节点入口及子图内的中断节点入口都可能重跑。
同一节点多个中断的顺序必须稳定；不能用宽泛 `try/except` 吞掉中断异常。
来源：[Interrupts：恢复规则](https://docs.langchain.com/oss/python/langgraph/interrupts#rules-of-interrupts)、[子图调用](https://docs.langchain.com/oss/python/langgraph/interrupts#using-with-subgraphs-called-as-functions)。

**CFU 含义／应用推断。** 不把“调用模型选焦点”和“等教师确认”写成没有持久化边界的同一个普通节点。
先保存提议，再进入只读取提议并中断的等待节点，可避免正常确认恢复时重新选出另一个焦点。
把写文件放到中断后，只避开这次中断的前置重跑；它仍可能受后续失败、重试或时间旅行影响。

### 3. thread、checkpoint 与 pending writes

**官方事实。** thread 累积一系列运行的状态；checkpointer 以 thread 定位状态。
完整 checkpoint 对应 super-step 边界；同一 super-step 中可有多个并行节点。
同一步某节点失败时，其他成功节点已保存的 pending writes 可在恢复时复用，避免重跑成功节点。
这些节点级记录不是任意位置都可时间旅行的完整 checkpoint。
来源：[Checkpointers：Core concepts、Pending writes](https://docs.langchain.com/oss/python/langgraph/checkpointers#core-concepts)。

**官方事实。** `MemorySaver`／`InMemorySaver` 放在 RAM，进程重启后丢失。
需要跨进程恢复时，应使用持久化 checkpointer；本地示例中的内存 saver 不能证明重启恢复可用。
来源：[Persistence：MemorySaver](https://docs.langchain.com/oss/python/langgraph/persistence#memorysaver-does-not-persist-between-restarts)。

**CFU 含义／应用推断。** state 可保存确认范围、两份文件的引用、版本及检查结果。
保存文件路径只保存了一个字符串；文件内容、可用性和对应关系仍要由产物存储与应用校验保证。
pending writes 中的 “writes” 是图执行结果的持久化记录，不能据此宣称外部文件已原子写出。

### 4. 同步耐久性的准确范围

| 模式 | 官方定义 |
| --- | --- |
| `sync` | 下一步开始前，同步持久化变更／写入 checkpoint。 |
| `async` | 下一步执行期间异步写入；进程崩溃存在尚未写下 checkpoint 的风险。 |
| `exit` | 正常完成、错误退出或 HITL 中断时持久化；不保存中途状态以抵御中途进程崩溃。 |

来源：[Checkpointers：Durability modes](https://docs.langchain.com/oss/python/langgraph/checkpointers#durability-modes)。

**CFU 含义／应用推断。** 可把持久化 checkpointer 加 `durability="sync"` 作为首个原型的保守起点。
它能让“写出节点完成后的图状态”先持久化，再开始下一步；不将文件存储与 checkpoint 数据库合并为一笔事务。
“文件写成功，但图记录尚未完成就崩溃”的窗口仍须由幂等写入和恢复核对处理。
具体数据库提交、文件持久性与故障恢复效果，必须用选定后端验证，不能由 `sync` 名称外推。

### 5. 正常恢复、故障重试与时间旅行不是同一件事

| 情形 | 官方行为 | CFU 工程含义（推断） |
| --- | --- | --- |
| 中断恢复 | 中断节点从头运行，已保存的内部 task 结果可复用。 | 等待节点保持简单，模型与文件副作用放在独立边界。 |
| RetryPolicy 重试 | 根据异常类别和退避设置，重跑失败的节点 attempt。 | 节点内前面已发生的外部行为仍需幂等；只给明确可恢复的故障设置重试。 |
| 旧 checkpoint 的 replay／fork | 指定点之后的节点、模型调用、API 请求和中断重新执行，结果可能变化。 | 明确发起新修订／分支；不得覆盖已交付版本后沿用其验证结论。 |

来源：[Graph API：Re-execution](https://docs.langchain.com/oss/python/langgraph/graph-api#re-execution-and-idempotency)、[Fault tolerance：Retries](https://docs.langchain.com/oss/python/langgraph/fault-tolerance#retries)、[Use time-travel：Replay](https://docs.langchain.com/oss/python/langgraph/use-time-travel#replay)。

**补充官方事实。** `interrupt()` 会绕过 retry policy／error handler 进入暂停，它不是应自动重试的普通失败。
来源：[Fault tolerance：Behavior with interrupt](https://docs.langchain.com/oss/python/langgraph/fault-tolerance#behavior-with-interrupt)。
**应用推断。** 超时／失败后重新请求模型，可能重复请求与计费；框架 task 不能保证模型服务端仅处理一次。
供应商若提供幂等键，应按其真实保证适配；本研究未核查具体模型供应商，因此不承诺这一能力。

### 6. durable task 结果复用与幂等边界

**官方事实。** `@task` 结果在启用 checkpointer 时保存；恢复可取回已完成结果。
它既可用于 Functional API，也可在 Graph API 节点内使用，无需为了 task 改写整个 CFU 流程。
来源：[Graph API：Using tasks in nodes](https://docs.langchain.com/oss/python/langgraph/graph-api#using-tasks-in-nodes)。

**官方事实。** Functional API 从 entrypoint 开头恢复；非确定性操作及副作用应放进 task，串联的不同副作用宜分别封装。
已开始但未完成的 task 可能再次执行；官方要求使用幂等键或检查既有结果来防止重复。
来源：[Functional API：Determinism、Idempotency](https://docs.langchain.com/oss/python/langgraph/functional-api#idempotency)。

**官方事实。** 可选的 `CachePolicy` 节点缓存另有 `key_func`、TTL 和编译时的 `cache` 配置。
这是独立的缓存机制，不能与 checkpointer 恢复已完成 task 结果混为一谈。
来源：[Use Graph API：Add node caching](https://docs.langchain.com/oss/python/langgraph/use-graph-api#add-node-caching)。

**CFU 含义／应用推断。** 造题模型调用完成后先保存其结果，再尝试文件写出，避免写入失败迫使重新造题。
两份文件可各用一个幂等 task；用稳定的“本次执行＋修订＋学生／教师角色”标识写入，恢复时核对已有内容摘要。
即便 task 已保存“写入完成”，验证前也应检查引用的文件实际可读；结果缓存不会把已丢失的外部文件自动重建。
若第一次调用已产生外部效果，但完成记录未保存，第二次可能再次调用：这正是不能声称文件 exactly-once 的边界。

### 7. 流程版本与阶段资源需要应用控制

**官方事实。** LangGraph 恢复旧 state 时执行当前部署的图，不自动固定运行开始时的代码版本。
官方建议在 state 记录行为版本并按它分支；改变恢复点之前的 task／interrupt 调用位置可能错配既有结果。
来源：[Backward compatibility：Business compatibility、Non-determinism](https://docs.langchain.com/oss/python/langgraph/backward-compatibility#business-compatibility)。

**官方事实。** 官方 LangChain 示例通过应用编写的 middleware，按会话阶段筛选工具、按调用修改模型消息。
这是可用实现手段；选择什么工具和上下文，仍是应用逻辑。
来源：[Context engineering：Selecting tools](https://docs.langchain.com/oss/python/langchain/context-engineering#selecting-tools)、[Messages](https://docs.langchain.com/oss/python/langchain/context-engineering#messages)。

**CFU 含义／应用推断。** `verification.md` 的“未写出前禁止读取”应成为资源访问与上下文装配条件。
造题／写出阶段不给模型该文件内容、摘要或可绕过的通用读取能力；工具执行端也核对阶段，不能只从工具列表隐藏名称。
不要开局递归读取全部 references、把验证规范塞进共享消息历史，或预先启动验证资源读取任务。
图上的先后边只能控制节点调度，不能阻止节点内部通用文件工具提前读取规范。
进入验证阶段后装配单独的验证模型上下文：验证规范、从实际文件读取的内容及所需的已确认教学上下文；不用“计划写什么”替代实物。
Skill／参考资料版本、图行为版本和产物修订应明确记录；checkpoint 负责保存这些值，应用负责赋值与兼容策略。

## 仅针对 CFU 的最小候选拆分（推断，未验证）

主路径在必要输入已明确时可分六个节点：

| 节点 | 工作与边界 |
| --- | --- |
| `ground_and_propose` | 读取数学参考、取得标准依据、保存焦点提议及理由；不造题。 |
| `await_focus` | 用保存的提议调用一次 `interrupt()`；校验回应并保存确认范围／教师改向。 |
| `build` | 按确认范围构建题目与教师指引，保存生成结果；不能访问验证规范。 |
| `write_pair` | 完整读取输出规范，写两份材料；确认两者实际存在，返回同一修订的文件清单。 |
| `verify` | 先检查文件清单与实存，再读验证规范，回读实际两文件，执行两道检查并保存所检版本。 |
| `deliver` | 核对待交付内容与通过检查的版本一致，返回材料并询问是否满足教师需要，同时提供至多两项具体修改选项。 |

必要澄清作为主路径前的条件分支：先加载数学参考，再按 Skill 最多问一个会改变题目的问题并暂停。
它不与必须发生的焦点确认合并，也不因增加执行节点而增加教学问题。
教师明确改向后，重述其范围与理由再构建；不自动多加一轮确认。
确认原提议与明确改向两条路径，均按最终焦点筛选相关错误模式后构建。
验证失败在验证／修复循环内重写两份文件再检查；教师要求修改时形成新修订，再经过写出和验证后交付。
生成后的写出与验证连续执行，不引入 Skill 未要求的教师放行节点。

六节点只是暴露暂停、昂贵计算和文件检查边界；内部小操作可用 task，无需把每次模型／工具调用变成教学阶段。
该拆分依据上文 CFU Step 3、5、6、7，以及官方节点重跑和 task 恢复语义，不是 LangGraph 官方推荐的 CFU 模板。

## “两份文件写出后才验证”的最小应用证据（推断）

1. 为每次材料修订保存清单：修订号、两份文件的稳定引用与内容摘要；只有两份写入均成功且可读取时才完成清单。
2. `verify` 先以清单定位文件并检查存在性／版本，再开放验证规范；不要只测试任意同名旧文件是否存在。
3. 读取规范后，从产物存储回读该版本的两份材料，计算所读内容摘要，并把两道检查结果与其绑定。
4. 修复必须生成新的材料版本／摘要；旧的通过记录失效。交付前再次核对所交付版本等于检查通过版本。

若选用不可变产物版本，可以缩小检查期间被覆盖的风险；具体落盘、成对完成标识及清单提交协议仍需原型选择。
这里不假设两次文件写入原子完成：学生版成功、教师版失败时，应保持“未就绪”，幂等补齐后才进入验证。
发生时间旅行时，也不得用新图状态指向被旧分支覆盖的同一路径；产物版本必须能区分两个执行分支。

## 最小原型验证问题

1. **暂停与教师回应：** 持久化提议后暂停并杀进程，同 thread 恢复是否只重跑等待节点？提议是否不变，重复／过期回应能否被应用拒绝，明确改向是否直接成为范围？
2. **任务与写入故障窗口：** 在模型结果保存后、第一份文件写出后、第二份写出但完成记录保存前分别注入故障；重试计数、模型计数和最终成对内容是否符合预期？`sync` 与 `async` 的差异发生在哪个记录边界？
3. **验证门禁与版本：** 仅有一份文件、残留同名旧文件、摘要不匹配时能否阻止读取验证规范？两份存在后是否确实回读；修订及检查后篡改是否阻止沿用旧通过结果？
4. **恢复与 replay 的区别：** 对同一任务做正常故障恢复和旧 checkpoint replay，记录模型／文件操作次数；前者能否复用已保存任务结果，后者是否产生独立修订并重新经过必要中断和验证？

原型只需桩模型、可计数工具、持久化 checkpointer 和临时产物目录；它验证执行语义，不证明题目教学质量已达标。
