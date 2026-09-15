# 四项教学 Skills：执行能力源码盘点

盘点日期：2026-09-14。上游子模块提交：`281eb8d41fe2837d911541c9bbb870b58add804c`（2026-08-28，`New skills release for Claude for Teachers (#9)`）；读取时子模块工作区干净。
本稿范围仅为固定上游四项 Skills 的源码事实，不限制本项目能力或规定必须复刻的行为。当前新增独立课程体系设计、本地知识前提及质量基线以 [README](../../../README.md) 为准。
本次只读源码、参考文件、评分 CSV，并比较渲染源码；未联网、调用模型或 KG、安装依赖、运行上游脚本、生成教学材料或执行评测。以下是源码事实，非协议设计或能力验证结论。`L` 为所链接源文件的行号。

## 教案创建：`k12-lesson-plan-creation`

- **输入与路由**：从请求及历史确定 math／ELA／science／social studies，先加载对应学科参考；新教案中的分层材料仍由本技能一次生成，不联用 differentiation；未覆盖的课程走无指定课程分支。[PC] L3–14、38–71。
- **默认值**：math／ELA 默认 45–60 分钟、通用可及性设计、CCSS；science 默认 45–60 分钟、NGSS；识别州信号后改用州框架。ELA 还区分 K–2 解码／朗读理解，单音型课 30–40 分钟、完整识字时段 60–80 分钟；未指定文本标记为建议。社会研究必须知道州、年级段与主题，可代拟探究问题。[PC-M] L5–12；[PC-E] L5–27、55–104；[PC-S] L5–21；[PC-H] L15–25。
- **顺序与首次暂停**：静默路由 → 最多两个按学科优先级选择的澄清问题，和独立的“整套材料／先看草稿”问题合为一轮 → 等教师回复 → 标准依据 → 构建。无缺失信息仍必须给草稿选择；只有回复后仍不知道教什么才再澄清。[PC] L75–106、125–144。
- **草稿分支与修订**：默认整套；只有选择草稿才在完成同等标准检索与构建后展示聊天草稿（年级／主题／标准、流程分钟数、实际任务、先备知识、exit ticket）。此后暂停等待修改或明确继续；修改后重呈草稿，获准当轮才生成文件。[PC] L137–165。
- **工具与资源**：KG 可用时必须在起草前调用；math 取标准、后向 progression、最多 5 个 learning components、3 个 misconceptions、IM lesson＋activity；ELA 取标准及 components；science 取标准及 OSE activity；社会研究取州标准。标准检索最多 3 次，无可用结果转已有知识并加覆盖说明；KG 不可用须加规定页脚，不编造出处。[PC-KG] L8–100；[PC] L88–98。
- **学科内容分支**：math 枚举并覆盖标准全部结构情形、退出题检测最难情形、讨论至少 10 分钟；ELA 保留年级文本难度，按年级／任务类型组织读写；science 分年级组织现象→调查→解释／模型，并分别表达三维目标；社会研究采用州标准＋C3 探究、两份有访问出处的材料与证据论证。[PC-M] L34–93；[PC-E] L49–176；[PC-S] L55–149；[PC-H] L68–139。
- **输出与修改**：单一 `lesson.json` 的 `shared`＋`documents[]` 经 `render_all.sh` 生成每文档 `.docx` 和 `.html`，保留 JSON 工作文件。至少教案、观察模板；学生确实持纸页时生成学生材料，纯口语课可省但须说明；可有来源材料包及特殊尺寸补充材料。修改只改源 JSON、同步重渲染并清除旧叙述；每次交付都问全部产出是否满意，给 3–4 个具体修改选项。[PC] L169–263；[PC-O] L117–159、215–222。
- **强制检查／失败**：输出前读完整 output 参考；检查材料清单与任务双向对应、师生题面一致、时间总和、阅读水平、计算／答案、书写空间、无障碍与文档完整性；生成后确认每文档两个格式均存在且非微小文件，错误修 JSON 重跑，彻底失败须明说，不能静默改为聊天交付。[PC-O] L6–115；[PC] L203–224。
- **评分证据**：`shared.csv` 33 项＋适用学科 6／7 项，需全套产出、实际题面／答案、最终聊天与课程／年级信号；结构覆盖、最难退出题、师生双向一致性等必须从材料核对，不能靠自述。条件项按年级、理解／phonics、论证写作、定量数据分流。[EV] L13、33–37、52–67；[PC-R] L2–34；[PC-RM] L2–7；[PC-RE] L2–8；[PC-RS] L2–8；[PC-RH] L2–8。

## 已有课时的差异化教学适配：`k12-lesson-differentiation`

- **输入与来源分支**：四学科既有教案；历史中的教案直接用，上传先读，URL 先取回；不可读／抓取失败须说明并暂停请求重分享／粘贴。math／science 可按课程位置或标题进 KG 找原课，无须先索要上传；大于一课的材料改用请求中信息并向教师确认。无来源先问年级＋主题／strand＋标准。[DF] L31–97；[DF-E] L5–22。
- **澄清与默认值**：先检测州；社会研究未知州必须问，其余默认 CCSS／NGSS 并给可重锚页脚。未指定层级时问一个合并问题（below／at／above 是否合适＋学习需求）；已有层级则不重问。每次扫描 ELL／WIDA／IEP／504 等输入并使用；缺失时明确 UDL 默认，三层均有句式与词汇支持，默认整课含退出题。[DF] L62–109、248–255；[DF-M] L182–195。
- **顺序与暂停**：路由／取得来源／必要澄清＋草稿选择 → 等回复 → 标准依据 → R1–R8 分层设计 → 整套交付或聊天草稿。草稿呈现来源、标准、年级、各层改动理由、实际任务、共同任务及重分组规则；等修改／明确继续后才生成。命名课程检索出现多个候选时，另需教师确认具体课再取材料。[DF] L114–191；[DF-KG] L43–49、100–106。
- **KG 差异**：math 必须取前后向 progression，misconceptions 无结果可从已有知识补；components 在并行批次说明中列为调用项，具体步骤又标为可选，须保留这一差异。IM 材料仅“已确认 IM 且按名称定位”才取。ELA components 只查 K–2，3+ 从标准拆解且禁止 progression API；science 禁止 components／progression API，改取 OSE 材料并识别前后衔接；社会研究只查州标准、衔接来自州框架知识。断连允许运行并加技能规定页脚。[DF-KG] L19–125。
- **不可省略的教学约束**：三层保留原标准及最难要求、共同情境／核心任务；支架不泄露答案。数学 Below 的嵌入支架按第 1 题≤2、第 2 题≤1、第 3 题起 0、退出题 0–1 渐退；其他学科按自身规则，不能套数学题号模式。Above 必须增加思考而非同类加量；都有形成性检查、提前完成任务、反思，教师计划注明本课证据对应的分组依据及可重新分组。[DF] L127–134；[DF-M] L44–180；[DF-O] L25–68、194–210。
- **学科差异／数据默认**：math 按具体→表征→抽象建立先备衔接；ELA 三层同一年级文本，K–5 区分解码／流利度和理解障碍，无数据按年级设默认；science 按观察→表征→解释设计并保留认知冲突，无数据以能观察但解释不足为默认；社会研究默认词汇＋来源分析常规。形成性数据在交付后追问以修订，不要求先有诊断数据才能生成。[DF-M] L52–88；[DF-E] L56–89、212–234；[DF-S] L57–91、194–210；[DF-H] L63–84、191–205。
- **输出／完成**：`differentiation.json` → `teacher_plan.docx`、`worksheet_group_a/b/c.docx`，同时保留各 HTML 与 JSON；全部同一输出轮交付。学生仅见 Group A／B／C。math／ELA／社会研究教师计划上限 3 页，science 按原课阶段组织、上限 5 页。所有修订读 output、定点改 JSON、全套重渲染；每轮问四文件是否满意，**教师确认全部满意才完成**。[DF] L195–267；[DF-M] L201–211；[DF-E] L240–250；[DF-H] L209–219；[DF-S] L214–227。
- **检查／失败／特殊输出**：生成前执行全部双向任务与支架核对、三张学生页标准代码核对、分组依据、两段设计理由、学生语言／无障碍检查；修改扫除旧上下文。生成错误修源重跑，不能静默聊天降级；仅用户明确请求渲染器无法表达的产出／布局才可另写生成代码，仍取同一源内容。[DF-O] L25–108、212–235；[DF] L225–239。
- **评分证据**：`differentiation.csv` 27 项，需要源教案／已知课程和州、学习需求与层级的对话、四文档、首次交付与后续回复；核对各层最难要求、双向对齐、支架渐退、分组依据及修改选项。另有 `M-CLARIFY-STATE`，仅社会研究且州未知时检查交付前的州问题，不能因此要求数学也必问州。[DF-R] L2–28；[DF-RQ] L1–2。

## 备课：`k12-lesson-prep`

- **输入／边界**：实际的既有教案（也可接前一技能产出）；先取得教案并亲自尝试关键任务，不能猜测。该目录只有 SKILL、LICENSE，无附带 references／scripts；技能正文没有固定年级、时长、框架默认。[PP] L3–17。
- **流程／教师实际参与**：取得真实教案 → 先尝试关键任务 → 把关键任务原样交给教师，请其亲做并指出“几乎正确”的回答错在哪里 → **教师先给自己的尝试／判断后**，才给模型的近似错误答案和观察 → 围绕任务设计讨论并纠正教师的事实错误 → 留便签 → 问是否修改。[PP] L17。
- **节奏／停止**：每轮几行、只问可用一句话或一道短题作答的问题；首次交流后明确教师随时可停，若追加只提供一个具体方向。技能正文要求写 `$OUTPUT_DIR/prep_note.md`，200–300 词，按原课教学顺序用原阶段名作粗体标题；未定义“必须确认满意才完成”的终态。[PP] L17。
- **评分所需证据**：16 项 rubric 明确区分 `artifacts/chat/both`，需原教案、完整师生与工具调用对话、便签；观察须具体到原题细节与原方法、障碍类型及原因，关键术语／符号、课程已有支持也要能追溯；至少一个教师实质贡献进入便签，不能只收集形式回复。[PP-R] L2–17。
- **评分带来的额外分支**：M1 要按已有教案／上传／链接／可检索课程位置取实际课，取不到给粘贴或链接退路；P1b 在 math＋KG connected 时要工具转录证明适用 misconception 的使用或确无适用结果。M2 接受明确拒答、三分钟单轮和先回答内容问题的例外；M6 接受教师明确要求模型先给近似错误答案。[PP-R] L3、12–17。
- **例外中的评分冲突**：M2／M6 允许拒答，M5 却无条件要求至少一项教师实质贡献进入便签；三分钟无便签路径也未在 M5／M6 完整列明。单事实查询被 SKILL 描述排除，rubric 却作为合法无便签情境引用。不能将这些差异一概称为可同时满足。[PP] L9–11；[PP-R] L10–17。
- **检查与事实边界**：正文强制实际尝试、教师先作答、事实纠错、任务而非学生标签、便签长度／顺序；没有专用验证脚本、格式转换器或失败重试规定。Rubric 仍提及 subject references 和“合法不产便签”等路径，当前极简 SKILL 未完整定义它们，不能据此声称相应执行实现已存在。[PP] L17；[PP-R] L2、5、7、10–17。

## 理解度检查：`k12-check-for-understanding`

- **输入／默认／边界**：数学主题或标准＋可推断或确认的年级；其他学科退出本技能。最多一个影响题目的澄清问题（年级或二选一标准），题量／格式／rigor 不问，按标准动词选 conceptual／procedural／application／mixed，产 1–3 题。[CF] L3–23、43–64；[CF-M] L7–12、31–39。
- **顺序／硬暂停**：加载 math → 必要澄清 → KG 或已有知识的标准依据 → 审阅所有返回的 learning components，选可检测焦点，说明所做事情、约束及理由 → **停下来等教师确认／改向，不能同轮继续造题** → 按教师选择重述范围 → 构建 → 先写两文件 → 后验检查 → 交付／修订。[CF] L43–137。
- **KG／退路**：按代码查标准（州框架传 jurisdiction），无结果改关键词；取 components、前后向 progression／coherence map、misconceptions。components 为空时说明并从标准子部分提议，仍须确认；相关错误不足 3 个可从已有知识补，但不得伪称已记录。无连接加教师指南规定页脚，不制造引文。[CF-KG] L10–68；[CF] L68–75。
- **构建约束**：先建立错误→先备／本年级→题干条件映射，再造题；conceptual 可 MC／多选／CR，procedural 以 CR 为主且 MC≤1，application 用 CR。响应需显示思考；干扰项至少覆盖先备缺口及本年级混淆，后续动作要不同，先备路径指向具体标准；遵循数字范围、表示形式、年级阅读长度与不贴负面标签的语言。[CF-M] L16–119；[CF] L25–28。
- **输出**：`$OUTPUT_DIR/cfu_[topic-slug]_student.html` 与 `_teacher.html` 两个独立、内联样式且无外部脚本文件；学生页仅题目／选项或空间＋姓名日期，教师页有标准等六项元信息、焦点／衔接说明、完整同序题面、答案与响应→解释→下一步表。无 `$OUTPUT_DIR` 时参考允许把两文档分开内联交付。[CF-O] L7–31、108–119、166–246；[CF-M] L108–119。
- **后验检查／重试**：只有两文件写出后才加载 verification、回读实际文件；Gate A 对 MC 每个选项写最强可辩理由到 `/tmp/verify_notes.md`，须只有一个可辩答案；Gate B 用实际数量检验每个错误是否真能得到该选项（CR 检查预期响应）。有子代理时可只给学生页做盲答；修复后重写两文件并重查改动，仍失败则换题。[CF] L119–128；[CF-V] L3–85。
- **附加检查／修改**：图形必须有 `<title>/<desc>`、`role="img"`、`aria-labelledby`，文字不泄露所问答案；逐句检查阅读长度、两文件题文／顺序一致。交付不透露检索来源、验证过程或第三方名字；收尾最多两个具体修改方向，若接受则改写两文件再问。[CF] L132–159；[CF-O] L35–73。
- **评分证据**：35 项 math rubric，需两文件＋完整焦点提议／暂停／教师改向对话、已确认焦点的约束及标准／progression 输入；按 `Source` 判断材料或对话。条件包括 grade-unknown、lc-redirect、conceptual-K-8、procedural。仅看最终指南不能判断 M2 是否真实等待。[CF-R] L2–36。

## 共同能力与不可抹平的差异

- **共同事实**：读取教学上下文和已有对话、按受众生成产出、保留必要教师交互和修订；creation／differentiation／CFU 明确要求 KG 可用即调用、不可用走规定退路，prep 的 KG 要求主要出现在条件 rubric。源码没有四项通用固定阶段表。[PC] L38–98；[DF] L31–123；[PP] L17；[CF] L43–95。
- **交互类型有不同语义**：缺信息的澄清（可推断／默认）≠ 草稿选择和放行（creation／differentiation）≠ 造题焦点确认（CFU 必停）≠ 教师亲做与判断（prep 核心）≠ 输出后修改邀请；只有 differentiation 明确以全部满意作为完成条件。不能仅以“一次提问／一次生成”计等价。
- **文件执行能力可部分共用**：两项 Word 技能的 `render_documents.py`、`lesson_common.py`、两个具体 renderer、`theme.css` 静态比较相同；shell 分别保存 lesson／differentiation JSON。依赖 bash、python3、`python-docx==1.1.2`，缺包尝试安装，失败时写 HTML 后非零退出；调用方还须核对 Word 完整性。[PC-SH] L13–44；[DF-SH] L12–44；[RENDER] L48–104。
- **渲染成功不等于要求通过**：渲染入口只检查有 documents 数组；缺失 shared 引用会返回空块而非报错，且有格式修复逻辑。教学覆盖、四文件数量、支架渐退、对应关系和后验题目验证仍是单独的技能要求。[RENDER] L69–102；[COMMON] L312–333、438–465。
- **评测资料的范围**：evals 提供 rubric 和人工接入 judge 的使用说明，未提供现成运行器、完整案例集或已跑分数；每条独立评分，不适用条件跳过；KG 专有条目需要相应数据才能准确评分。必要执行证据包括输入／源材料、对话和工具结果、实际产出以及技能规定的检查结果，不能仅保存最终回复。[EV] L20–72、112–114。
- **上游不一致须留证据**：creation math 允许 2–3 个误解而 shared P4a 要≥3；differentiation P5 允许任务改写／减量而 output 要 shared 原文一致；prep rubric 保留未在极简 SKILL 详述的路径；CFU 支持多选，但 Gate A 与 R6 用“唯一可辩答案”描述 MC，未明写多选校验方式；CFU 无输出目录可内联，但 Step 6 要已有文件。这里只标出，未决定如何统一。[PC-M] L78；[PC-R] L5；[DF-R] L6；[DF-O] L194–206；[PP-R] L12–17；[CF-M] L35–39；[CF-V] L18–34；[CF-R] L19；[CF-O] L26–31；[CF] L121–128。
- **数学进一步核查**：creation 的 K–2 未知量要求未完整限定到加减主题，Design notes 的 2–3 与 shared O7 的 1–2 可取交集；differentiation 数学 R6 也明确允许 Below 保结构改数字，与共同题面原文一致存在分支冲突。数学 R3 允许已知州缺进阶时回退，KG 指导又限制为州未知；数学参考与主规范识别 IM 的证据条件也不同。具体流程及候选解释继续保留，见 [数学教案分析](lesson-creation-execution-design.md#源码差异与候选解释) 和 [数学适配分析](execution-contract-draft.md#数学适配的-kg-与明确解释)；本项目采用决定及效果验证另行记录。[PC-M] L44、80–83；[PC-R] L23；[DF-M] L7、61–78、154；[DF] L48–49；[DF-KG] L34–41。

[PC]: ../../../k12-teacher-skills/plugin/skills/k12-lesson-plan-creation/SKILL.md
[PC-M]: ../../../k12-teacher-skills/plugin/skills/k12-lesson-plan-creation/references/math.md
[PC-E]: ../../../k12-teacher-skills/plugin/skills/k12-lesson-plan-creation/references/ela.md
[PC-S]: ../../../k12-teacher-skills/plugin/skills/k12-lesson-plan-creation/references/science.md
[PC-H]: ../../../k12-teacher-skills/plugin/skills/k12-lesson-plan-creation/references/social_studies.md
[PC-KG]: ../../../k12-teacher-skills/plugin/skills/k12-lesson-plan-creation/references/learning-commons-kg.md
[PC-O]: ../../../k12-teacher-skills/plugin/skills/k12-lesson-plan-creation/references/output.md
[DF]: ../../../k12-teacher-skills/plugin/skills/k12-lesson-differentiation/SKILL.md
[DF-M]: ../../../k12-teacher-skills/plugin/skills/k12-lesson-differentiation/references/math.md
[DF-E]: ../../../k12-teacher-skills/plugin/skills/k12-lesson-differentiation/references/ela.md
[DF-S]: ../../../k12-teacher-skills/plugin/skills/k12-lesson-differentiation/references/science.md
[DF-H]: ../../../k12-teacher-skills/plugin/skills/k12-lesson-differentiation/references/social_studies.md
[DF-KG]: ../../../k12-teacher-skills/plugin/skills/k12-lesson-differentiation/references/learning-commons-kg.md
[DF-O]: ../../../k12-teacher-skills/plugin/skills/k12-lesson-differentiation/references/output.md
[PP]: ../../../k12-teacher-skills/plugin/skills/k12-lesson-prep/SKILL.md
[CF]: ../../../k12-teacher-skills/plugin/skills/k12-check-for-understanding/SKILL.md
[CF-M]: ../../../k12-teacher-skills/plugin/skills/k12-check-for-understanding/references/math.md
[CF-KG]: ../../../k12-teacher-skills/plugin/skills/k12-check-for-understanding/references/learning-commons-kg.md
[CF-O]: ../../../k12-teacher-skills/plugin/skills/k12-check-for-understanding/references/output.md
[CF-V]: ../../../k12-teacher-skills/plugin/skills/k12-check-for-understanding/references/verification.md
[EV]: ../../../k12-teacher-skills/evals/README.md
[PC-R]: ../../../k12-teacher-skills/evals/k12-lesson-plan-creation/rubrics/shared.csv
[PC-RM]: ../../../k12-teacher-skills/evals/k12-lesson-plan-creation/rubrics/math.csv
[PC-RE]: ../../../k12-teacher-skills/evals/k12-lesson-plan-creation/rubrics/ela.csv
[PC-RS]: ../../../k12-teacher-skills/evals/k12-lesson-plan-creation/rubrics/science.csv
[PC-RH]: ../../../k12-teacher-skills/evals/k12-lesson-plan-creation/rubrics/social_studies.csv
[DF-R]: ../../../k12-teacher-skills/evals/k12-lesson-differentiation/rubrics/differentiation.csv
[DF-RQ]: ../../../k12-teacher-skills/evals/k12-lesson-differentiation/rubrics/clarifying_question.csv
[PP-R]: ../../../k12-teacher-skills/evals/k12-lesson-prep/rubrics/internalization.csv
[CF-R]: ../../../k12-teacher-skills/evals/k12-check-for-understanding/rubrics/math.csv
[PC-SH]: ../../../k12-teacher-skills/plugin/skills/k12-lesson-plan-creation/scripts/render_all.sh
[DF-SH]: ../../../k12-teacher-skills/plugin/skills/k12-lesson-differentiation/scripts/render_all.sh
[RENDER]: ../../../k12-teacher-skills/plugin/skills/k12-lesson-plan-creation/scripts/render_documents.py
[COMMON]: ../../../k12-teacher-skills/plugin/skills/k12-lesson-plan-creation/scripts/lesson_common.py
