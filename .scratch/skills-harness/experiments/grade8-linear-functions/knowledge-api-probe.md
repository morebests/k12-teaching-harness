# 八年级原创实验：知识 API 有界事实核查

日期：2026-09-15。**组织者文档，不装入原创模型 Context。** 本次为 wayfinder 的两个目标做只读 HTTP 核查；没有实现完整 adapter、调用模型、读取 `.env`、改写输入资源、创建分支或解决决策票。结果说明当前接口怎样返回事实，不证明教学设计或学习效果。

直接来源为 [本地 OpenAPI 契约](/Users/libo/Mathematics/k12-learning/apps/studio-server/contract/openapi.json) 和下述 `/api/browse/` GET 返回。清洗采证保存在 [knowledge-api-probe.samples.json](knowledge-api-probe.samples.json)：包含请求状态、两个目标的标准／LC 详情样本、边身份及来源、分页和 14 个进阶端点的框架验证。没有保存或输出原响应的 UI `groups`、`endpointRelationshipGroups`，没有调用课程端点。

执行边界来自 [实验 README](README.md)、[知识使用约定](../../../../docs/references/knowledge-consumption-contract.md)、[Context 设计](../../assets/context-and-llm-design.md#整体课程方案与单元内课程设计的输入) 和 [运行装配分析](../../assets/execution-structure-design.md#运行时-context-怎样真实进入调用)。先前 [本地接口记录](../../assets/learning-commons-integration.md#本地-studio-http-api-实测2026-09-15) 用于定位问题；本报告中的接口观察重新调用取得。外部文件读取仅限所授权的 OpenAPI，不沿研究索引读取外部 IM 及其派生课程文件。

## 固定身份及本次覆盖

| 项目 | 实际值 |
| --- | --- |
| CCSS Mathematics 框架 canonical identifier | `6becf2d7-2232-5ead-983f-9f0a4de24ab7` |
| 框架 CASE UUID | `c6496676-d7cb-11e8-824f-0242ac160002` |
| 每次 GET 的 `sourceSnapshot` | `lc/v1.11.0` |
| OpenAPI SHA-256 | `94e75a78a619069bf2d604b459d2c975d464682dc3d4698a8479608c35c9d3d5` |
| 返回物化版本 | `schemaVersion=2`、`cleaningVersion=v2` |
| nodesSha256 | `ffc142f72450c9692a9e547207cba3e0cd4012eb00c1d1be6aaced165c4139c5` |
| relationshipsSha256 | `74389d5e438e7a7f23e1128539827533ae08acacc73c9f3e4c81cc07a8916b21` |

两个哈希是 API 返回的来源元数据，本次未重新读取或计算源 JSONL。采证批次记录 84 个 GET：81 个 HTTP 200，另有三次主动错误探针，见后文。此前用于确认结构的探索请求不计入该批次计数。[采证：`sourceSnapshot`、`requestStatusCounts`、`requests`](knowledge-api-probe.samples.json)

| 目标 | canonical identifier（用于 API 路径） | CASE UUID（单独保留） |
| --- | --- | --- |
| `8.F.B.4` | `0ff0d447-960a-5116-9fde-5989f4fc88fc` | `6b9ef36a-d7cc-11e8-824f-0242ac160002` |
| `8.G.B.7`（非 F 样本） | `baa2ebfe-b4ae-5424-b435-0978cbda8219` | `6ba063cb-d7cc-11e8-824f-0242ac160002` |

两条详情的 `jurisdiction=Multi-State`、`academicSubject=Mathematics`、`statementType=Standard`，`publisher.value` 和 `fields` 中 `author` 均为 `Common Good Learning Tools`。这些属性补充来源核对；框架身份由真实 `hasChild` 根路径确定，不能仅用作者或管辖范围替代。[采证：`targets[].standardDetail`、`rootPaths`、`membership`](knowledge-api-probe.samples.json)

## 按代码精确定位 CCSS

以下路径共同前缀为 `http://127.0.0.1:8000/api/browse`；所有请求都附 `sourceSnapshot=lc/v1.11.0`。模型只需要提交代码；框架 ID、快照和 HTTP 路由由执行端固定。

1. 对已经冻结并审计的八年级输入，可用其中的 `statementCode → ref` 索引；键必须精确匹配，且 ref 的快照／类型与固定输入一致。这是本轮的可用实现选择，不代表 API 提供了按框架过滤的搜索参数。
2. 需要在线解析代码时，调用 `GET /search?q={code}&kind=StandardsFrameworkItem&limit=100`。契约没有 `framework` 查询参数；必须完成分页，不能取首条搜索命中。
3. 在 `nodes[].sourcePaths` 中核验 `structureRelation == "hasChild"`，并寻找某条 `paths[].steps[0].ref` 精确等于固定框架 ref。ref 含 `sourceSnapshotId`、`kind`、`identifier` 三项。不要用字符串包含、框架名称或显示标题代替此比较。
4. 对通过框架核验的候选调用 `GET /nodes/StandardsFrameworkItem/{identifier}`。将 `fields` 按 `name` 建索引，要求 `statementCode.value` 精确等于所请求的代码。`alternateStatementCode` 单独保留；不能把模糊搜索命中或别名默认为精确标准身份。
5. 接受恰好一个精确候选；零个或多个候选都返回明确的解析问题。缓存必须绑定快照与框架身份。成功详情保留 ref、CASE UUID／URI、代码、正文、notes、来源及快照元数据；读取英文时使用原 `value`，不要把机器翻译 `projection.text` 写成来源原文。

实际分页以 `limit=10` 走完：`8.F.B.4` 返回 `10+10+10+1=31` 条，`8.G.B.7` 返回 `10+10+6=26` 条。两者都有州版同代码命中，按固定框架后各 1 条，再读详情核对代码后仍各 1 条。最后页均 `hasMore=false, nextCursor=null`。[契约：`searchSourceNodes`、`SearchPage`、`SourceNodeDetail`；采证：`targets[].search`](knowledge-api-probe.samples.json)

## 标准端点的框架核验

关系返回的 `endpoint.frameworkName` 在本次全部进阶端点中为 `null`，端点也没有完整框架 ref。因此不能只看端点代码或 `frameworkName` 接受它。八年级端点可以在已审计的固定框架 ref 集合中验证；其他年级／高中端点使用：

```text
GET /api/browse/nodes/StandardsFrameworkItem/{canonicalIdentifier}/root-paths
    ?sourceSnapshot=lc%2Fv1.11.0
```

返回结构中的关键字段如下，均为原 API 字段：

```json
{
  "node": {
    "sourceSnapshotId": "lc/v1.11.0",
    "kind": "StandardsFrameworkItem",
    "identifier": "0ff0d447-960a-5116-9fde-5989f4fc88fc"
  },
  "sourceSnapshotId": "lc/v1.11.0",
  "structureRelation": "hasChild",
  "paths": [{"steps": [{"ref": {
    "sourceSnapshotId": "lc/v1.11.0",
    "kind": "StandardsFramework",
    "identifier": "6becf2d7-2232-5ead-983f-9f0a4de24ab7"
  }}]}],
  "isComplete": true,
  "truncatedBy": null
}
```

上例省略中间 steps、显示投影和 `sourceSnapshot` 元数据，仅示意需要核验的字段；完整两个目标根路径在清洗采证中。本次 14 个不同进阶端点均重新读取完整根路径和节点详情，全部从固定 CCSS 数学框架可达，所有 `isComplete=true`。源码契约允许根路径不完整，运行中不能把截断或失败当成“不属于 CCSS”；可返回无法核验并排除该端点。该 root-paths 端点没有 cursor；不完整状态由 `isComplete/truncatedBy` 明示。[契约：`listNodeRootPaths`、`RootPaths`；采证：`progressionEndpoints`](knowledge-api-probe.samples.json)

对于本次八年级目标，另实测了 `GET /frameworks/{fixedFramework}/grade-levels/8/items/{itemIdentifier}/membership`，两者 `inProjection=true`。此端点同时要求该年级元数据及框架可达性；不能把它用于排除合法的七年级／高中进阶端点。[采证：`targets[].membership`](knowledge-api-probe.samples.json)

## LC 与 supports 的真实返回

便捷列表：

```text
GET /standards/items/{standardIdentifier}/learning-components
    ?sourceSnapshot=lc%2Fv1.11.0&lcVersion=lc%2Fv1.11.0
```

顶层是 `standard, sourceSnapshot, sourceSnapshotId, lcVersionId, ordering, nodes`。契约明确一次返回该标准的全部直接 LC，不提供 cursor；超过该接口安全上界应报 504，不能擅自视为完整小集合。每个 `nodes[]` 是 `LearningComponentSummary`，包含：

```json
{
  "ref": {
    "sourceSnapshotId": "lc/v1.11.0",
    "kind": "LearningComponent",
    "identifier": "5f3a9252-5252-54ed-9c00-f4c910b3b9a4"
  },
  "description": {"value": "Determine the initial value of a function from a mathematical context presented in a table or graph"},
  "academicSubject": {"value": "Mathematics"},
  "author": {"value": "Achievement Network"}
}
```

上例省略投影及 `standard` anchor。LC summary 的 author 可直接用于初筛，但没有完整 attribution，也没有 `supports` edge identity。若需要来源边证据，就查询：

```text
GET /nodes/StandardsFrameworkItem/{standardIdentifier}/relationships
    ?type=supports&direction=incoming&endpointKind=LearningComponent
    &limit=100&sourceSnapshot=lc%2Fv1.11.0
GET /nodes/LearningComponent/{componentIdentifier}
    ?sourceSnapshot=lc%2Fv1.11.0
```

因此 `get_components(code)` 的最小完整实现可以直接用 **supports 入边分页 → 允许来源的 LC 详情**；便捷 LC 列表并非必调。本次同时调用两种路线，验证两个目标的 LC identifier 集合与 supports endpoint identifier 集合完全一致。[契约：`StandardsItemLearningComponents`、`LearningComponentSummary`；采证：`targets[].components`、`relationships.supports_incoming`](knowledge-api-probe.samples.json)

LC 详情使用通用 `SourceNodeDetail`：`ref`、`publisher.value`、`attribution`、`fields[]` 等。这里 `fields[]` 的值直接是 `{"name":"author","value":"Achievement Network","projection":null}`，不是再包一层 SourceValue。字段实际包括 `academicSubject, author, dateCreated, dateModified, description, examples, inLanguage, examplessha256`；样本 `examples` 的原值是字符串 `"[]"`，不要把它混为 null。代码不得因为这一投影没有某个字段，就宣称上游所有版本不含该字段。

本次 13 个 LC 全部逐个读详情：summary 的 `author.value`、详情的 `publisher.value`、`fields[name=author].value` 一致，均为 **Achievement Network**。13 条 supports 边的 `publisher.value` 与 `qualifiers[name=author].value` 也一致为该作者。attribution 明确写 Learning Commons 从 Achievement Network 获得 LC，许可 CC BY-4.0。**可据当前快照的显式来源字段设置 Achievement Network 白名单**；本次没有发现未知作者或混合作者，也未核查该作者全部历史派生链，不能把白名单声称为全库的历史原创性证明。[采证：`components.details` 与 supports 边来源](knowledge-api-probe.samples.json)

## buildsTowards 的边结构和方向

```text
GET /nodes/StandardsFrameworkItem/{standardIdentifier}/relationships
    ?type=buildsTowards&direction=incoming&endpointKind=StandardsFrameworkItem
    &limit=100&sourceSnapshot=lc%2Fv1.11.0
```

查后续时仅将 `direction=outgoing`。顶层保留 `node, sourceSnapshot, sourceSnapshotId, appliedType, appliedDirection, appliedEndpointKind, ordering, edges, hasMore, nextCursor`；下面是 `8.F.B.4` 的一条实际出边，省略翻译和非来源限定字段：

```json
{
  "identifier": "1333480b-6231-5094-b193-ed1d74f51802",
  "relationshipType": "buildsTowards",
  "direction": "outgoing",
  "provenance": "source_fact",
  "endpoint": {
    "ref": {
      "sourceSnapshotId": "lc/v1.11.0",
      "kind": "StandardsFrameworkItem",
      "identifier": "9a0fdd78-5f2d-573b-a3b0-965a37b79252"
    },
    "display": {"value": "HSF-BF.A.2"},
    "displayField": "statementCode",
    "frameworkName": null
  },
  "publisher": {"value": "Student Achievement Partners", "projection": null},
  "attribution": "Knowledge Graph is provided by Learning Commons under the CC BY-4.0 license. Learning Commons received learning progressions under CC0 from Student Achievement Partners.",
  "upstreamIdentifier": null,
  "identifierRepaired": false,
  "qualifiers": [{"name":"author","value":"Student Achievement Partners","projection":null}]
}
```

API 的 edge 不直接给 `sourceIdentifier/targetIdentifier`；它返回查询的顶层 `node`、相对该节点的 `direction` 和另一端 `endpoint.ref`。执行端若规范化两端，必须按下表转换，同时保留原 direction：

| API direction | source（来源边的起点） | target（来源边的终点） | 教学解释 |
| --- | --- | --- | --- |
| `incoming` | `endpoint.ref` | 顶层 `node` | `supports` 的 LC 支持本标准；`buildsTowards` 的基础支持本目标 |
| `outgoing` | 顶层 `node` | `endpoint.ref` | 本标准支持后续标准 |

同端点平行边保留各自 identifier，不能压成一个布尔值。`identifierRepaired/upstreamIdentifier` 分别保留 canonical identity 与来源身份记录。本次所有边 `identifierRepaired=false, upstreamIdentifier=null`。14 条进阶边的 `publisher.value`、`qualifiers` 中 `author` 都为 **Student Achievement Partners**，且 `provenance=source_fact`。进阶的英文关系定义明确是不要求严格先修顺序的方向性支持；不能将这些边直接转成必须全部通过的先修链。[契约：`SourceRelationship`；采证：`relationships.buildsTowards_*`](knowledge-api-probe.samples.json)

| 查询目标 | LC／supports 入边 | buildsTowards 入边（基础） | buildsTowards 出边（后续） |
| --- | --- | --- | --- |
| `8.F.B.4` | 11／11 | 2：`7.RP.A.2`、`8.F.A.3` | 8：`HSF-BF.A.2`、`HSS-ID.C.7`、`HSF-BF.A.1.a`、`HSF-LE.B.5`、`HSF-LE.A.2`、`HSF-IF.B.6`、`HSA-CED.A.2`、`HSF-LE.A.1` |
| `8.G.B.7` | 2／2 | **0，HTTP 200 完整空集** | 4：`HSF-TF.A.3`、`HSG-SRT.C.8`、`HSF-TF.C.8`、`8.G.B.8` |

`8.G.B.7` 的空入边只说明本次固定快照中这个查询为空，不能证明无需先备或学生已经准备好。[采证：全部两目标记录](knowledge-api-probe.samples.json)

## 分页、来源过滤和错误必须怎样表达

关系列表契约的 `limit` 默认 25、上限 100；搜索默认 50、上限 100。每页验证固定快照、查询节点与 `appliedType/appliedDirection/appliedEndpointKind`，按 `hasMore` 继续并原样回传 opaque `nextCursor`。cursor 绑定快照与筛选条件，不解析其内部结构、不跨查询复用。发现 `hasMore=true` 却缺 cursor、cursor 循环或读取失败时返回不完整／错误，不宣称已取全。

本次所有六种关系查询用 `limit=2` 读到底，再与 `limit=100` 的完整返回比较：有序 edge identifier 列表一致，无分页重复；`8.F.B.4 supports` 为 6 页（2、2、2、2、2、1），其出向进阶为 4 页；`8.G.B.7` 出向进阶为 2 页。最后页均 `nextCursor=null`。这些观察验证了两个样本的分页，不是全库覆盖证明。[采证：`relationships.*.pages`、`limit100Equivalent`](knowledge-api-probe.samples.json)

建议这轮运行采用以下具体过滤规则；它是依本次证据提出的执行端选择，不是新增全项目永久来源政策：

1. 仅开放 `get_standard(code)`、`get_components(code)`、`get_progression(code,direction)` 这类语义工具，不接收模型提供的任意 URL、类型或框架。代码解析按上文固定身份实施。
2. `get_components` 只取 `supports/incoming/LearningComponent`；每条边要求 `provenance=source_fact`，边 publisher 与 qualifier author 都精确在 `{"Achievement Network"}`，LC 详情 publisher 与字段 author 也精确在该集合。缺失、不一致或其他作者均暂排除，报告排除数量与原因。返回 author、attribution、ref、定义及实际 supports 边身份。
3. `get_progression` 只取 `buildsTowards/incoming|outgoing/StandardsFrameworkItem`；要求边 provenance、publisher、author 一致为允许的来源（本轮 `Student Achievement Partners`），两端都验证固定 CCSS 框架。返回端点的完整标准内容和来源、边身份、原 direction 及必要的规范化两端。中间关系或多跳由后续显式查询产生，不补造直接边。
4. 不根据 `endpoint.frameworkName=null`、代码看起来像 CCSS 或 author 名字单独接受框架身份。首轮遇到非白名单、空来源或来源冲突，保留组织者侧原因／数量，不把未批准内容带入模型 Context。当前样本排除数为 0，不据此忽略未来排除情况。
5. 分页先完成该查询的来源集合，再过滤；某页过滤后为 0 仍需沿 cursor 继续。返回 `retrievedCount/returnedCount/excludedCount` 及是否完整，可另报按原因计数。为预算中止的查询明确标为 partial；成功但全部被过滤、来源真实空集和 HTTP 失败分别表达。
6. API 返回的 `groups` 是**不随当前筛选改变**的全部一跳关系统计，另外还有 `endpointRelationshipGroups`、平台图投影状态等 UI 内容。采用字段白名单构造模型结果；不将原 JSON 原样转发，也不把整个 browse tag 放行。仅需标准、LC、允许边及其来源／版本；根路径用于框架校验，不给模型整套浏览导航。

源码契约明示的常见失败为 400（参数／cursor）、404（节点不存在）、409（快照／版本不匹配）、504（特定完整集合超安全上界）。本次三次主动探针的真实返回是：

| 有意发送的请求 | 实际 HTTP 与错误码 | 解释 |
| --- | --- | --- |
| 将 supports 入边页 cursor 用到 buildsTowards 入边查询 | `400 INVALID_CURSOR` | cursor 绑定筛选条件；重开正确查询，不静默用空结果 |
| 标准详情要求 `sourceSnapshot=lc/v0.0.0` | `409 SNAPSHOT_MISMATCH` | 当前服务固定为 `lc/v1.11.0`；不能自动换版本继续沿用旧验证 |
| 将 `8.G.B.7` CASE UUID 放进 canonical identifier 的节点路径 | `404 NODE_NOT_FOUND` | CASE 身份与图内 canonical 身份不互换；不表示此标准不存在 |

采证批次的正常请求均成功，未观察到自然发生的超时或 5xx；因此本轮没有验证 504、服务中断或恢复行为。错误 body 原样保存在清洗采证的 `negativeProbes`，cursor 只留哈希，不当作持久身份。[实际错误记录](knowledge-api-probe.samples.json)

这份记录足以支撑本轮有限查询包装及其身份／来源检查。它没有验证全年所有目标的关系覆盖、全部作者来源链、真实模型隔离行为或教学质量；后续运行必须审计实际装配和工具返回。
