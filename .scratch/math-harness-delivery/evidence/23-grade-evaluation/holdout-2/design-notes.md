# holdout-2 设计说明

日期：2026-09-17。本组样本用于检验八年级年级课程检查器的检出、定位与误报，共 14 个：10 个注入样本，4 个合法对照。本文只记录设计方法、依据和校验方式；具体改动、位置和答案只在 `samples.json` 与 `answers.json` 中。

## 读过的材料

只读了任务许可的范围：

- `.scratch/math-harness-delivery/year-planning-evaluation.md`：缺陷定义、重大失败清单、关键缺口定义、第 7 节样本类型。
- `.scratch/math-harness-delivery/year-planning-rubric.json`：八维锚点、检查范围、重大失败清单。
- `.scratch/math-harness-delivery/evidence/23-grade-evaluation/candidates/b-final.json`：底稿全文。
- `.scratch/math-harness-delivery/evidence/15-full-year-blueprint/initial/request.json`：只取出 `school` 与 `instruction` 两个字段。
- `.scratch/math-harness-delivery/evidence/15-full-year-blueprint/final/knowledge.json`：只取出 `package.year_scope.nodes` 的标准编号、类型和原文，用来核对目标原意与实践范围。
- `CONTEXT.md`、`src/teaching_harness/contracts.py`、`src/teaching_harness/grade_evaluation/calibration.py`。

其他接触：列出了 `23-grade-evaluation/` 目录下的文件名，以确认 `holdout-2/` 尚不存在，没有打开其他子目录或文件。`Mutation`、`ObjectRef` 和编号字段的格式限制，是导入 `calibration.py` 后读取 pydantic 生成的 JSON Schema 得到的，没有打开 `records.py` 或 `evidence.py`。没有读取 README、工单、规格、旧样本或 git 历史，没有运行 `scripts/`，也没有调用模型或网络。

项目 `CLAUDE.md` 要求开工前阅读 README 等文件；本任务是保留样本设计，读取范围由任务明确限定，为保持样本独立于既有答案和修订 Prompt，按任务限定执行。

## 底稿与指纹

样本的 `base` 指向 `15-full-year-blueprint/final/content/curriculum.json`，但允许阅读的底稿是 `candidates/b-final.json`。两份文件解析后的 JSON 完全相同，字节上只差文件末尾的换行符，因此所有 JSON Pointer 都按 `b-final.json` 设计，`base_fingerprint` 用 `curriculum.json` 本身的字节计算。

## 按协议判断缺陷

**注入样本**必须对应协议意义上的缺陷，不能只是措辞或版式问题：

- 定为 `critical` 的，须对应协议第 3 节的四类重大失败之一：必需目标遗漏或实质误读且没有可追查的分担；关键数学结论错误或依赖矛盾导致进程不可执行；时间重复计算或已知资源约束使核心安排不可行；把不存在的数据、学生掌握或教学验证当作事实依据。
- 定为 `key_gap` 的，须符合第 4 节对关键缺口的定义：改变目标责任、必要依赖、学习机会、评价用途或核心可行性，但不至于让全年进程整体不可执行。
- 类型以协议第 3 节的重大失败和第 7 节的改动样本示例为起点，再按各维 `review_scope` 扩展到目标、实践、单元、依赖、回访、评价、探查、时间、资源和交接等不同对象，使八个维度都至少有一个样本以它为主要或可接受维度，位置分散在文档的不同部分。
- 设计遗漏类样本前，先在底稿全文里检索该目标的内容是否还出现在其他位置，只选没有可追查分担的对象，避免“遗漏”与“另有分担”并存，导致严重程度说不清。
- 每个样本只做一处改动。改动后的文字沿用底稿的术语和句式，不写“错误”“注意”等提示词，也不在 `note` 中透露意图。

**合法对照**参照协议第 7 节的合法改动示例设计。每项都先核对对照不会碰到已有依赖、学校资源清单、课内完成要求和课时合计，确保按协议不构成缺陷，同时改动足够明显，检查器能看到。

## 答案字段的取舍

- **维度：**每条只列 1–3 个。严重问题常跨维度，列入的是按锚点最可能据以判分的维度，主维度排在前面。
- **位置：**`pointers` 覆盖改动位置，以及检查器引用证据时可能落到的相邻位置，例如与改动相矛盾的原有陈述所在的条目。跨多个单元的问题使用较宽的前缀，靠对象、维度和关键词共同约束匹配。
- **对象：**按任务给定的写法填写。依赖写成“依赖方单元<-提供方单元”，回访或应用写成“目标代码@单元编号:角色”，评价写成“目标代码@单元编号”。
- **可检测性：**只有改动落在数字、编号、角色或数组顺序上，且不理解文字、只凭结构字段与标准范围就能判定时，才写 `["program","model"]`，其余只写 `["model"]`。
- **关键词：**选正确评语大概率会用到的词，兼顾数学名词和问题性质，避免只放极常见的词。
- **说明：**`rationale` 和 `description` 都是简短的中文转述，不照抄底稿或改动后的原文，以免装配时的隔离检查把样本文本误判为答案泄漏。

## 校验

在 scratchpad 中用 `uv run python` 运行一次性脚本，完成以下检查，全部通过：

1. 用 pydantic 按 `list[Sample]` 和 `list[SampleAnswer]` 校验两个文件。
2. 对每个样本在系统临时目录调用 `materialize`，确认指纹一致，改动都能执行，结果仍是合法的 `YearBlueprint`，并且与底稿不同。
3. 答案与样本按编号和 `kind` 一一对应；对照样本没有预期问题且有保护位置，注入样本各有一条预期问题；问题编号唯一。

附加检查：所有 `pointers` 和 `protected_pointers` 在对应的改动后文档中都能解析；把全部改动后文档交给 `assert_isolated`，没有发现答案泄漏；逐个样本复算与结构相关的事实（课时合计、先备顺序等），结果符合设计。

## 局限

- 严重程度和可接受维度是设计者按协议作出的判断，未经独立评阅者复核；部分问题处在关键缺口与重大失败的边界上。
- 底稿本身可能已有问题。对照样本的保护位置只覆盖改动处，如果检查器在这些位置报告的是底稿原有问题，需要人工区分，不能直接记为误报。
- 可以由程序判定的样本，只表示所需信息存在于结构字段中，不代表当前程序检查已经实现相应规则。
