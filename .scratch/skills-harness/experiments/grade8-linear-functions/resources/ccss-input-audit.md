# 八年级 CCSS 有限输入：采集与完整性核查

本文件由 `collect_ccss.py` 的只读请求生成。采集不调用模型，不读取课程端点或 IM 内容。仅本目录写入结果。

## 来源、版本与边界

- 本地来源：http://127.0.0.1:8000/api/browse/
- 固定框架：`6becf2d7-2232-5ead-983f-9f0a4de24ab7`，名称 `Common Core State Standards for Math`。
- 框架 CASE UUID：`c6496676-d7cb-11e8-824f-0242ac160002`；与 canonical identifier 分列。
- 快照：`lc/v1.11.0`；采集开始：`2026-09-15T02:01:59.855668+00:00`。
- 本地契约：`/Users/libo/Mathematics/k12-learning/apps/studio-server/contract/openapi.json`；SHA-256：`94e75a78a619069bf2d604b459d2c975d464682dc3d4698a8479608c35c9d3d5`。
- [Learning Commons 官方标准 schema](https://docs.learningcommons.org/knowledge-graph/schema-reference/standards) 区分框架、条目、CASE 身份和层级；本地实际字段以返回值为准。
- 原始 attribution 保留于每份 JSON 的框架及条目，未把本地转换写成出版者原文。

```json
{
  "namespace": "lc",
  "version": "v1.11.0",
  "nodesSha256": "ffc142f72450c9692a9e547207cba3e0cd4012eb00c1d1be6aaced165c4139c5",
  "relationshipsSha256": "74389d5e438e7a7f23e1128539827533ae08acacc73c9f3e4c81cc07a8916b21",
  "schemaVersion": 2,
  "cleaningVersion": "v2"
}
```

## 实际取得与复核

- Q002 年级目录中 Grade 8 的 itemCount = 71；按 parent 递归并耗尽每页 hasMore/nextCursor 后取得 71 个唯一条目。
- 内容文件 53 个条目；实践文件 18 个条目。两文件不重叠，总和 71。
- 分类（采集器判别，原 statementType 保留）：`{"hierarchy_or_context": 19, "mathematical_practice": 8, "grade_specific_practice_statement": 8, "numbered_content_standard": 28, "content_subitem": 8}`。
- 实际 statementType 分布：`{"None": 3, "Grade Level": 1, "Standard": 36, "Domain": 5, "Cluster": 10, "Content Standard": 8, "Component": 8}`。
- 每个非叶节点取得的 child 数与 projectionChildCount 相等；同一 parent 的分页未出现重复条目；所有分页终止于 hasMore=false、nextCursor=null。
- 所有条目详情均为 StandardsFrameworkItem，学科 Mathematics、辖区 Multi-State、gradeLevels 包含 8；查询始终固定同一框架和完整 sourceSnapshot。
- 每个条目的 canonical identifier 与 CASE UUID 独立保存；CASE UUID 唯一且与 CASE URI 后缀相符。未调用 CASE 远程服务验证其当前内容。
- 所有有 notes 哈希的条目按 UTF-8 实际内容验证 notessha256；八项 MP 的详细 notes 均非空。
- MP1–MP8 在本地同一框架内齐全，description 是简短标准句，notes 是详细实践要求，两者都进入输入。另有 8.MP1–8.MP8 年级内条目，notes 均为 null。两套节点的 canonical / CASE 身份不同，逐一保留，不按标题合并或计作 16 项独立实践；未查询或编造 alias / equivalence 关系。
- 19 个层级分组中，内容文件含内容总组、年级组、5 个 Domain 和 10 个 Cluster（17 个），实践文件含 2 个实践分组；分组与编号标准、字母子条目分别保存，不把标准顺序当课程顺序。
- 71 个条目详情的 sourceAnomalies 全部为空；这仅表示来源没有登记异常。

### 独立官方范围核对

2026-09-15 通过网页读取核对以下官方、非 IM 页面所列代码集合；与本地 28 个编号标准及 8 个子条目严格相等。网页核查不替换本地来源正文，也未做全文逐字符一致性声明。

| 官方来源 | 编号标准数 | 字母子条目数 |
| --- | ---: | ---: |
| [8.NS](https://www.thecorestandards.org/Math/Content/8/NS/) | 2 | 0 |
| [8.EE](https://www.thecorestandards.org/Math/Content/8/EE/) | 8 | 5 |
| [8.F](https://www.thecorestandards.org/Math/Content/8/F/) | 5 | 0 |
| [8.G](https://www.thecorestandards.org/Math/Content/8/G/) | 9 | 3 |
| [8.SP](https://www.thecorestandards.org/Math/Content/8/SP/) | 4 | 0 |

子条目：`8.EE.C.7.a`, `8.EE.C.7.b`, `8.EE.C.8.a`, `8.EE.C.8.b`, `8.EE.C.8.c`, `8.G.A.1.a`, `8.G.A.1.b`, `8.G.A.1.c`。
8.F.A.1 的 notes 保留函数记号不作八年级要求的说明；本地用词为 in Grade 8，官方网页为 for Grade 8。保留来源实际措辞，没有静默改写。
上述官方网页读取来自本次 web 工具结果；未保存网页全文或声称有网页 body 哈希。直接 urllib 请求 8.F 页返回 403，该失败未作为完整性证据。

### 实际字段与变换

条目 sourceFields 的实际字段为：`academicSubject`, `adoptionStatus`, `alternateStatementCode`, `author`, `caseIdentifierURI`, `caseIdentifierUUID`, `dateModified`, `description`, `inLanguage`, `jurisdiction`, `normalizedstatementtype`, `notes`, `notessha256`, `statementCode`, `statementType`。
返回体外层的 ref、sourceSnapshot、gradeLevels、publisher.value、attribution 随内容保留；fields 数组按原 name 映射到 sourceFields，只取 value，所有 null 原样保留。node details 与目录原文一致性已验证。
最新版官方 schema 的 normalizedStatementType 在本地为 normalizedstatementtype；本地节点 fields 不含 isCurrent、license、provider、dateCreated，不能把缺列解释为上游无该概念或补造字段值。许可依据是实际返回的 attribution。dateModified 只代表条目字段，本次运行版本仍以完整 sourceSnapshot 固定。
框架的 notes / notessha256 未装入输入：该段混有非本次标准范围的框架参考说明；条目 notes 全部保留。所有正文保持来源英文，未将机器翻译投影当出版者原文。

## 缺口与适用范围

- 完整性结论针对本次固定 CCSS 框架的 Grade 8 投影及其所有节点详情，不声称完成全库质量审核。
- 未把学习组件、进阶、其它年级标准、学生证据、学校条件或教学规则装入这两份标准快照；它们是否另行需要由本次任务决定。
- 本地节点详情没有返回的字段不会根据最新版官方 schema 补造；本地值与 CASE 远端现值是否一致尚未请求验证。
- 本地 Grade 8 年级分组的 notes=null，没有取得独立年级导言／重点领域的正文；这不影响上表的标准及子条目全集计数，也不声称输入已包含官方文档所有导言。
- UI 中文 projection、display、groups、课程 metadata 不进入输入；查询收据只证明本次所取来源和分页结果。

## 文件指纹

| 文件 | SHA-256 |
| --- | --- |
| ccss-grade8.json | `c2d192410cb5e8535729c5aef73528bcf00798d5e160b47961ef9e185c42a3dd` |
| ccss-practices.json | `75caaa1cd1ca95739b089e30c1d8930acf80e42f944b70e91c51859e3509ff2d` |

## 查询收据

所有请求均为 GET / HTTP 200，所有响应的完整 sourceSnapshot 与上文完全相同。原响应 hash 基于 HTTP body 字节；仅下列安全摘要留存，不保留 UI 响应体。

| ID | 请求 | 时间 (UTC) | rows | hasMore | nextCursor | 原响应 SHA-256 |
| --- | --- | --- | ---: | --- | --- | --- |
| Q001 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFramework/6becf2d7-2232-5ead-983f-9f0a4de24ab7?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:01:59.855668+00:00 | 0 | None | `None` | `e94d1f386043b8675a949783033acf7d3cb59e54bae50fbd349594a272e33a69` |
| Q002 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:01:59.879138+00:00 | 0 | None | `None` | `d0ff11334753906cc52fc33e44d040307ec8a2c14a6416cfcac956e7313730ba` |
| Q003 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:01:59.923267+00:00 | 2 | False | `None` | `c239ed0c90430d975030f52bb674a710acc8655aaeac5244576a8c53fc6628dc` |
| Q004 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=957d5d34-22eb-5ec5-b50a-80d9d95a0678&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:01:59.950366+00:00 | 1 | False | `None` | `758c5d2298a9c3ce265a14243e04961a3c8218378e958caec4d15fcb2483f538` |
| Q005 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=37a2cfc1-5201-59d9-84ad-6455a88b7bc0&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:01:59.963191+00:00 | 5 | True | `eyJ2IjoxLCJiIjoiMWQ0MDIxZDRlZGU2ZjgxNyIsImsiOlswLCJNUDUiLDAsIlVzZSBhcHByb3ByaWF0ZSB0b29scyBzdHJhdGVnaWNhbGx5LiIsImFiZGQ2NzhlLWMyMjEtNWU3MC1hZTcyLTUzOTdmZDI3YzRmMiJdfQ` | `da8a31c3274b390f2aa462b69b74c917aad602c1187cd9ae64d8afe568003f45` |
| Q006 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=37a2cfc1-5201-59d9-84ad-6455a88b7bc0&limit=5&cursor=eyJ2IjoxLCJiIjoiMWQ0MDIxZDRlZGU2ZjgxNyIsImsiOlswLCJNUDUiLDAsIlVzZSBhcHByb3ByaWF0ZSB0b29scyBzdHJhdGVnaWNhbGx5LiIsImFiZGQ2NzhlLWMyMjEtNWU3MC1hZTcyLTUzOTdmZDI3YzRmMiJdfQ&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:01:59.981121+00:00 | 3 | False | `None` | `be3d2302528f5b17464469e4b19ffa220ef311d4138b8d2d0c0767fe03d90059` |
| Q007 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=7c83b999-ae43-5ee3-9bad-97660ab97ff2&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:01:59.993189+00:00 | 5 | True | `eyJ2IjoxLCJiIjoiY2JlYzkwNDQxNGM0MTMyOSIsImsiOlsxLCIiLDAsIlN0YXRpc3RpY3MgJiBQcm9iYWJpbGl0eSIsIjM0ZjJmZWFkLWEzODAtNWY2ZS1iNWJmLTczMzgyMDY2ZTQyZiJdfQ` | `9c2cf54209390ec99c342fc2b7074793c5a218af38f889f353574f1df69cd8f8` |
| Q008 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=7c83b999-ae43-5ee3-9bad-97660ab97ff2&limit=5&cursor=eyJ2IjoxLCJiIjoiY2JlYzkwNDQxNGM0MTMyOSIsImsiOlsxLCIiLDAsIlN0YXRpc3RpY3MgJiBQcm9iYWJpbGl0eSIsIjM0ZjJmZWFkLWEzODAtNWY2ZS1iNWJmLTczMzgyMDY2ZTQyZiJdfQ&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.007172+00:00 | 1 | False | `None` | `ad1d210ee9d6aa9ad08ef97c8e24204c72e0cd7aab21ad045f8eb0981a1a8c42` |
| Q009 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=e0d847f6-991b-5dc0-a66b-0deb99ce53dc&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.015540+00:00 | 3 | False | `None` | `9ad6fe0cfdc3936bd457b84eb2faad07333aca69ad2e5210eb756ed1fa516c36` |
| Q010 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=ff2b2fbc-89b4-55d1-a47b-7f9c096b4c3a&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.025560+00:00 | 2 | False | `None` | `9ad58330a99439dabef1db1196fc48b146325d63cc79f4aba8467a84b32c5d63` |
| Q011 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=d9e48f2b-8a24-52ae-b418-79c6172fd473&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.036150+00:00 | 3 | False | `None` | `f206b84f65febb366663fb45a63ae7c0cadb3d4f4387276217aa5d282bcdd5f6` |
| Q012 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=e1203a0b-ace1-5f1a-b540-8ad4fc404824&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.046078+00:00 | 5 | True | `eyJ2IjoxLCJiIjoiMTFlMWM2YTg5Y2NjNjg4MCIsImsiOlswLCI4Lk1QNSIsMCwiVXNlIGFwcHJvcHJpYXRlIHRvb2xzIHN0cmF0ZWdpY2FsbHkuIiwiZDNhZTdlNmUtYTEyZi01MTNkLWI4MjktZjgzYzQzODgyNTExIl19` | `999bc2bf83fea0a4902182fd287f4aef36976a193f8f865e761cd6e2456a7906` |
| Q013 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=e1203a0b-ace1-5f1a-b540-8ad4fc404824&limit=5&cursor=eyJ2IjoxLCJiIjoiMTFlMWM2YTg5Y2NjNjg4MCIsImsiOlswLCI4Lk1QNSIsMCwiVXNlIGFwcHJvcHJpYXRlIHRvb2xzIHN0cmF0ZWdpY2FsbHkuIiwiZDNhZTdlNmUtYTEyZi01MTNkLWI4MjktZjgzYzQzODgyNTExIl19&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.056937+00:00 | 3 | False | `None` | `8d2dfea632c106b95952e57e22e3ec12e33900c5aa89d7894c236f7c8701b4f7` |
| Q014 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=34f2fead-a380-5f6e-b5bf-73382066e42f&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.068471+00:00 | 1 | False | `None` | `b734b7ad9ac2b7810818ed3e173820448e9bb87deb7e0b49708ff8a9cb359943` |
| Q015 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=8c6472f2-dbaf-572d-a5f6-5f4db1523ce7&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.078101+00:00 | 1 | False | `None` | `d2575450627fe5dce0a714dca5d725c37b2bec7bac084ee7d76a45802bca6fd9` |
| Q016 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=995dd00c-c6f3-56b7-9870-5392bc1cffa0&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.086144+00:00 | 4 | False | `None` | `82e88dc9323f4e20fae90927f4b5e7d1a7a9d30f2bb8fcf1a0eac53fed45fa54` |
| Q017 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=7102e92a-5e93-5103-b719-d6e6946b7741&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.096641+00:00 | 2 | False | `None` | `0f49cbfc8e32ecf6e1775282635412fbf16f8673a3b7cda02b3992999f7bbcd4` |
| Q018 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=aca5ec40-e19f-51bc-9b2a-8eaf9b29b0a4&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.105840+00:00 | 2 | False | `None` | `706a984bc28ba055b2ca7b6a3db73d31c99148230fcb9562c4fa7517b0da570b` |
| Q019 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=51403b34-cc8d-5ba7-b9cf-9f02a5e636d4&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.116527+00:00 | 3 | False | `None` | `2be5fb3545ee0338b633fe7fad5429e2b058378e6873aba896b41a5cb262b3cf` |
| Q020 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=185e9d9f-ac74-5621-aced-81909baa4077&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.128231+00:00 | 2 | False | `None` | `7c91b45e1109ae4a64d3dee7e48aa3a334bf6900106133716671fb6a22c95c89` |
| Q021 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=4ad73579-5cf8-50bc-a385-33085176f7df&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.140708+00:00 | 5 | False | `None` | `288b34c27627fff0d5fa582b0be3d91f1f45e450db551fc569621f2d3bf27237` |
| Q022 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=a5cb12bf-64a7-5154-b546-2f40b149168a&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.153208+00:00 | 3 | False | `None` | `30e5a31d19a9a9dae8cd09631f505f2dffe9f48d64354bd8e175d6e40ecd4d2c` |
| Q023 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=a8d71370-4be0-5801-9d5f-042508c0a2bf&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.162532+00:00 | 1 | False | `None` | `c6f673661e7fea5fa5bf97d094f3c71a35a5defbe4b1e3340d9cf6ab89d06127` |
| Q024 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=1ae7700c-15cc-5f51-8fee-f7240611ac5d&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.171365+00:00 | 4 | False | `None` | `a04a2271cc2daac7fd8ee28237d58cab1715e6e1db269c3bef9e75ed8f2d4df3` |
| Q025 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=a81d1c5d-4b13-58e1-ab79-b95a72cd6792&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.181301+00:00 | 2 | False | `None` | `241929c8daf9798f1ebb7fc6b44947a485125cb7dd2a44a654aefdcbd8be0eec` |
| Q026 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=b686895b-8c12-52ff-84c5-1acd55ee9e34&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.190662+00:00 | 2 | False | `None` | `43b17d32d383b54d3b871b91f9303ffca6116d2336f2f7964139da8bfe04ac30` |
| Q027 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=15f1b8b4-b836-5750-866a-f7d5f377a296&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.202320+00:00 | 3 | False | `None` | `33a34815d7db286d5d4294dfd6c77a9e330ec5c30248d631dfcac54a0c6da164` |
| Q028 | `http://127.0.0.1:8000/api/browse/frameworks/6becf2d7-2232-5ead-983f-9f0a4de24ab7/grade-levels/8/items?parent=785dbfaa-3ede-5681-91dc-23574d49a09e&limit=5&sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.213343+00:00 | 3 | False | `None` | `8692c1da5dde86d4c9796b27f0fae9e64aadb262e97fdc38759ab3c33db347ba` |
| Q029 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/957d5d34-22eb-5ec5-b50a-80d9d95a0678?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.223437+00:00 | 0 | None | `None` | `429c9ee971f177cd35aab9963d42d1b0be884e20059f5c20772ea3c2ed747f7d` |
| Q030 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/37a2cfc1-5201-59d9-84ad-6455a88b7bc0?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.229590+00:00 | 0 | None | `None` | `81275f81669c5fbe15a899a9de25ac2cc7f2c234b58661ab69fc7cecd38382db` |
| Q031 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/7c83b999-ae43-5ee3-9bad-97660ab97ff2?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.236621+00:00 | 0 | None | `None` | `dd6021b9f0f4f545600e0f183c95e1db94e17d6188594b7a3af85fa6df44d090` |
| Q032 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/3b1f7006-2d44-5097-86b6-7ac05d0de3ac?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.241134+00:00 | 0 | None | `None` | `9011d5c7310f89893e55c31b98a743393e9bb996b9e6533f333007f0d5cc5be9` |
| Q033 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/6a0b0b39-d910-5b38-8d8d-6c1b1e22a351?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.245280+00:00 | 0 | None | `None` | `9f3f57df65b87f5170c951c51a6d96f7fe7013b48471bbca839b36b907b60be7` |
| Q034 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/f0dc8000-e9bd-5e45-8268-684ccf49c304?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.249510+00:00 | 0 | None | `None` | `bc2d414c7b9e931a7b503fa5d09547dad0e83cc52791168f9aabfb9a0dab8b4b` |
| Q035 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/4493563c-595c-53a2-a21a-5c027c6d4dc4?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.254385+00:00 | 0 | None | `None` | `6a25dac481d1e8df8d2d3b6f305740d8e8deb8b9317803e0572db760a941301c` |
| Q036 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/abdd678e-c221-5e70-ae72-5397fd27c4f2?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.258642+00:00 | 0 | None | `None` | `a38319e187fc2b88ad6637969b136cb7cfa474413ec5f3ff7f788ef68424263b` |
| Q037 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/e87ba523-1aec-5c4d-a894-b21036323a93?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.264704+00:00 | 0 | None | `None` | `03877f537c5f1c2d63edc6d950503e1d02eeb00ee8d68a2c3d81af204dd23549` |
| Q038 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/4d9707ed-235e-543a-b90f-87c54d740e46?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.269514+00:00 | 0 | None | `None` | `b72b57557718069a928002d8baf00bc7819a6c9b45ec32c4f774ecee226eabdf` |
| Q039 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/da2c7ffe-57fa-5b44-85ef-342e76a5820e?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.273759+00:00 | 0 | None | `None` | `b1333ee25a5ad432e08816cb8b20b1c71d9efc1eea5db12443c825d06f29595b` |
| Q040 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/e0d847f6-991b-5dc0-a66b-0deb99ce53dc?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.277871+00:00 | 0 | None | `None` | `a0939fa6264ce52b927ab6359c13b3b8204ad8b224f59c7fb954a4d08d6a907c` |
| Q041 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/ff2b2fbc-89b4-55d1-a47b-7f9c096b4c3a?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.282563+00:00 | 0 | None | `None` | `dd6cd23b0c437786023296695863bf13c84bd25fc5ce6a61270edcbb7b7ab197` |
| Q042 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/d9e48f2b-8a24-52ae-b418-79c6172fd473?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.287845+00:00 | 0 | None | `None` | `372b0435b6be682b5a2df901f42687f88445073b5ab8b9ad138a996697739395` |
| Q043 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/e1203a0b-ace1-5f1a-b540-8ad4fc404824?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.291630+00:00 | 0 | None | `None` | `c0187d6443d2336f38beeef8ee15965b8bd071cc31b5f4e37f3964738ad86e57` |
| Q044 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/34f2fead-a380-5f6e-b5bf-73382066e42f?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.296572+00:00 | 0 | None | `None` | `c0619a25434804c1b659e64d18efc131ace3ef55a54f65dc4649896c1f303f01` |
| Q045 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/8c6472f2-dbaf-572d-a5f6-5f4db1523ce7?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.300265+00:00 | 0 | None | `None` | `e2cb040e329dab71000a313c658ab0357795df4d74b85fcb5e077a690fb4bd47` |
| Q046 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/995dd00c-c6f3-56b7-9870-5392bc1cffa0?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.304598+00:00 | 0 | None | `None` | `0bc6aea5ea6ad34c139d0ecbc7a6d5da112c0aec2517efeb3ee5531b3bd767e5` |
| Q047 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/7102e92a-5e93-5103-b719-d6e6946b7741?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.308565+00:00 | 0 | None | `None` | `bb8d30f203cf14b7bde9431c6a7b76f0c8f92e4baa358861d8e2b40111b85329` |
| Q048 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/aca5ec40-e19f-51bc-9b2a-8eaf9b29b0a4?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.312742+00:00 | 0 | None | `None` | `53f8ec6e93b873f35d6058ae3dfefccb1e81726820adc482ec230f7d9c55e2cc` |
| Q049 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/51403b34-cc8d-5ba7-b9cf-9f02a5e636d4?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.317208+00:00 | 0 | None | `None` | `035e6e4ef776e4c8a2ba03e3fcad45fbbc399ba1f10b430866c845ad72c8c0e1` |
| Q050 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/185e9d9f-ac74-5621-aced-81909baa4077?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.322165+00:00 | 0 | None | `None` | `16d9dc482574202b6f416ceb45bb49e4778296adb539c0bb23a652af3e1379ef` |
| Q051 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/4ad73579-5cf8-50bc-a385-33085176f7df?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.328148+00:00 | 0 | None | `None` | `47762c8944d9151d30d03fabe4eb9c305d629ee6e8a1ba6a2e0d745619df449d` |
| Q052 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/a5cb12bf-64a7-5154-b546-2f40b149168a?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.333731+00:00 | 0 | None | `None` | `83d74d74ab9a95136115d265d9219fc1365518bebe6d7c0d96e25fb239184c21` |
| Q053 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/a8d71370-4be0-5801-9d5f-042508c0a2bf?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.338277+00:00 | 0 | None | `None` | `9da8bfa28fe76801055e153d35f76fdcfe3d63cd45d63b32e20619e0779a6c4d` |
| Q054 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/3d45bc79-6517-51e1-aef8-435cedc7bd42?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.342064+00:00 | 0 | None | `None` | `3ed5d109f9f6db80f4b8549d147090afe98a833bec103299cde01666894c51ba` |
| Q055 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/30d5f421-351b-5d45-b251-1bd15b2e6e0f?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.345873+00:00 | 0 | None | `None` | `1411eb785fe9b186cd07661715dcb590225d163aef6f9a7a351b1e436295f1dd` |
| Q056 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/c3575094-d44c-54b4-9dd8-d675dd76c738?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.350060+00:00 | 0 | None | `None` | `2542ba80ea82af5895c3277f55ba8a373e8411ec674ccb12411f8abc195cd7e7` |
| Q057 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/9cacbba9-1d93-5069-8302-4437624c056f?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.353714+00:00 | 0 | None | `None` | `69d2362185ac6b3b0d7b9ff4709272030660dc06216f798468ef0490dc19a1af` |
| Q058 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/d3ae7e6e-a12f-513d-b829-f83c43882511?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.357470+00:00 | 0 | None | `None` | `ae3217ac25f8438bb4baf97b85966e3fa63d1634d6bd2888f0d183fab072b1af` |
| Q059 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/15cb90d9-4e84-5a7d-b673-754766ca7e9e?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.360762+00:00 | 0 | None | `None` | `9c18a6deb85120e6525e46e64ce50bd93b7b8a01b6da78b059eecafa03f90021` |
| Q060 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/e3e3ccb9-148f-5bc4-bb0a-608e462cba5c?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.364914+00:00 | 0 | None | `None` | `6bf0e5e372d749cfe75688977389e65ce0a61cf4caf541647b4db34c95b0e70d` |
| Q061 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/4a9f78a4-d08a-5584-aff3-0b62d582e84c?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.369318+00:00 | 0 | None | `None` | `4bf0462585a912cb86f04b2371f67553425fcdfbfdd6db595b5dfb1277d6f596` |
| Q062 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/1ae7700c-15cc-5f51-8fee-f7240611ac5d?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.373307+00:00 | 0 | None | `None` | `73169f8909f3f9f0d0115fb5944274bef4b04a017d0720c1acb3b3855249fbf0` |
| Q063 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/a81d1c5d-4b13-58e1-ab79-b95a72cd6792?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.376813+00:00 | 0 | None | `None` | `5ee6426e017c3a0ebdbe3aad8b73c118f4b63ee8898e0853b284cd32ee066609` |
| Q064 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/549d72b8-68e2-527f-a3fa-c8fb033fe4a2?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.380906+00:00 | 0 | None | `None` | `fa706a3bbcdcbad6bd644182a33b0b370cbc4d9f9a14e7c15060338ab8644eb3` |
| Q065 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/3bebaa64-eeef-5329-b3cc-dddc8e68f0a1?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.385027+00:00 | 0 | None | `None` | `199fd2dea680353881374cf992b1945d1906104543b92dbee3734eb94369160d` |
| Q066 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/85e37e84-850b-55bb-8e2c-db84016e7e56?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.389694+00:00 | 0 | None | `None` | `9f3fb9290e9588810552f8c4110f4318000d3c5e03f51cb285aa2fb3f274cd4a` |
| Q067 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/11610aaf-64f0-518d-b9c1-95070a8a7001?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.393841+00:00 | 0 | None | `None` | `510756a6d262995a161aceae9eada4a88d0969fc1db922bfb3e7f1811c2a5458` |
| Q068 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/0b02d60f-6a4e-5cf6-9a46-91ba5bfe5b7d?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.397672+00:00 | 0 | None | `None` | `9fed85be298d649185568f25a9b6af4db7b0112750089db927c649be837401fa` |
| Q069 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/f42ff582-c718-5196-917c-9178b1fb2c91?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.401817+00:00 | 0 | None | `None` | `44d02e5041832c3101d5097e6f419a01526afee92d19ad1a7a048bb7d2342699` |
| Q070 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/b686895b-8c12-52ff-84c5-1acd55ee9e34?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.405822+00:00 | 0 | None | `None` | `623a4818840565326f2e90353b12711d0f281b34f1a10f7bbd0c4daf67fe9097` |
| Q071 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/15f1b8b4-b836-5750-866a-f7d5f377a296?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.409202+00:00 | 0 | None | `None` | `7f3d321b7ef418d3d00048015ec46bf6af7616cf618d36f88798c6b8fa828fcb` |
| Q072 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/e4de5a68-0b5a-5a21-bfe2-2924f3a7e70e?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.412861+00:00 | 0 | None | `None` | `ee3641331eb0fea0706d79849e5434b70fc1ee4723765a82e9984bfcf383d39a` |
| Q073 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/9f8337d3-e4d7-51cc-a27c-f8403bca7ad1?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.417714+00:00 | 0 | None | `None` | `70c35ea4dffc9b51a7e6b7695db9531830917ddf935d68840d8cb7f9c42d57ad` |
| Q074 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/534ca674-79cd-5a7e-b7e0-b9258b338e8c?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.422482+00:00 | 0 | None | `None` | `b83150d93593647da1aee3693512b870348405b318d0b7794b10ee77226d519e` |
| Q075 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/0ff0d447-960a-5116-9fde-5989f4fc88fc?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.427418+00:00 | 0 | None | `None` | `ac4a19b27c4d030eb1321fce5dce99dfd2a0d1f361c7bd324938b37a5ec15a08` |
| Q076 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/9d3c6a12-46a7-5285-a425-df2570bc7764?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.431637+00:00 | 0 | None | `None` | `97611b71d4b4432cff64dc29d034a4e670355e8f1f150b795285a89d36a36d23` |
| Q077 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/785dbfaa-3ede-5681-91dc-23574d49a09e?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.436784+00:00 | 0 | None | `None` | `7c8fc5035d1fa1431262832816b21379f45faa227559f6c483fbe07cfde18cab` |
| Q078 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/01283b43-9bb8-5430-aff3-c10cf3d29937?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.440933+00:00 | 0 | None | `None` | `9c4a2f114a29f0890a28ce5cd778a5b15ad727e9052277c67c131f1b558c823b` |
| Q079 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/cf8f294e-a741-5295-8441-39a8caeeb802?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.444728+00:00 | 0 | None | `None` | `f0683954220ccb75622f7ba29f8ca035ca922dfa84b1ec5dec5eb5a4295cfcd2` |
| Q080 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/1f9fc8f9-d21d-51be-8078-d50b4365fc87?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.449129+00:00 | 0 | None | `None` | `25f9b8b8116d5e3cf2bc97162dc9abc1daee2a04005ffd53f920aadd0df3e6b7` |
| Q081 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/29523042-4921-5e17-85a7-caadeab205ce?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.453795+00:00 | 0 | None | `None` | `1c7cd664361da1571acf9e296fc167575e5738f0d8bab0f12d1ac939745489ac` |
| Q082 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/52aff65f-f9bf-51bb-99c0-0a53063975ae?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.457858+00:00 | 0 | None | `None` | `1a63d534ed9285294d8d475acbec31e4079df5bc9278d881ceb0f3e1cb0ddebc` |
| Q083 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/baa2ebfe-b4ae-5424-b435-0978cbda8219?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.461456+00:00 | 0 | None | `None` | `0cc5aade319cab856709a9ade5c52060b1d692487ac2b40feee962e17aff3057` |
| Q084 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/74df37a8-5572-588b-a649-6045601c2aab?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.466315+00:00 | 0 | None | `None` | `7af6f6e231858d3387259c18a6f2f2cd653a8b68ec2b646acffe1adf12ffab40` |
| Q085 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/75acceb6-cebe-5b1b-be1c-a9d7dc230f94?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.470978+00:00 | 0 | None | `None` | `2a4f5e53b5f27d2e0f7c7aed8c2751671375b7379d5dfe8c52be3dd387d05ead` |
| Q086 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/56b722c3-4a4c-50c9-bc55-a152ee3b276d?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.475131+00:00 | 0 | None | `None` | `d2c3457a9c71741211b50868bbd578f0ddfa1577b7516b90b4d3fa200ca944c1` |
| Q087 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/2ef2cd57-bb44-5bc3-a5e3-081de809894f?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.479141+00:00 | 0 | None | `None` | `8115cad190b6e37500b575fdd0a7d3398a4d3ef613297993b46c8aebcc7e41de` |
| Q088 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/98da3d52-b694-59f6-be1f-912861048cdc?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.483681+00:00 | 0 | None | `None` | `ebe0581b68def27fc26df3dc9890eaba7792c7dc8df74ccd59625dc2fecc12d0` |
| Q089 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/13130cb1-c8cf-5460-a77e-04115ef91419?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.488103+00:00 | 0 | None | `None` | `efb089005ba865702c07bd1b5ae5534b747d2a99fd19ae37f40610cadc05df91` |
| Q090 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/ab19383d-8a81-5766-909c-92569f412a7a?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.492037+00:00 | 0 | None | `None` | `147e38efebf0fc36575e56814279a985b7a76c8ce63d13fac8544a18200e1547` |
| Q091 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/10204309-7113-5913-aa66-6d95f9338f05?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.496672+00:00 | 0 | None | `None` | `e5bd4497eef97f26d87caeeb28280be7c9d22deec31aff289aae1df6b267d0bb` |
| Q092 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/e4fb1b8a-aa7d-559f-a28b-47500a5c1a61?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.501263+00:00 | 0 | None | `None` | `ee728c1638082c240ebe29819eaa9e44f6e8d134d21d388ccaf28255edfdf065` |
| Q093 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/8d03e081-fa8a-554a-ab0f-ce2b978d9da4?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.505879+00:00 | 0 | None | `None` | `e1a74a07a74e3d9d80f1e4981d27310eb53cfc0b58d7af762a4c042511eee37a` |
| Q094 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/45845725-c424-5979-935e-799020ffdbdb?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.510625+00:00 | 0 | None | `None` | `4a8fa6d1674d1a775ce6b644b7a0bae6c430532d01fb082222ae72cc91c1b88a` |
| Q095 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/edc37a90-fbc4-5141-a96c-743419e57327?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.514901+00:00 | 0 | None | `None` | `e7b5b4b0babddd20967f85ad31a4d81eb7eac94b2d9a6d1fd0af85291fd7cd32` |
| Q096 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/c7c0e167-bb2b-525b-89f7-0bea1608513c?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.519760+00:00 | 0 | None | `None` | `96c1ccccd9aa09e01a0f7868ce1c24f056ca670c578ed01f26e495a733a30817` |
| Q097 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/ab3f9261-b89d-58c9-aae6-ab8312d688c7?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.523832+00:00 | 0 | None | `None` | `b4445b7aeeb29100d58d7c636b48b145d5a636b1c6267e76a374f8e9527a4a4b` |
| Q098 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/19bac67b-648d-5cb8-8dd5-ecbba72a895c?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.527928+00:00 | 0 | None | `None` | `49f2d8d17049909bae9ca8a4fa94bc763b60ca29ca38ac8098ae8c49730bc27d` |
| Q099 | `http://127.0.0.1:8000/api/browse/nodes/StandardsFrameworkItem/f2a92de7-8237-5af3-aa9c-cb854c54a493?sourceSnapshot=lc%2Fv1.11.0` | 2026-09-15T02:02:00.531889+00:00 | 0 | None | `None` | `261a9a156b51d788e96e51413216a632a15bfe75157a0ba0c1d0b1c25c3e2c41` |

## 逐父节点分页闭合

`null` 是年级投影根；不是新建的知识实体。

| parent identifier | queries | returned child identifiers |
| --- | --- | --- |
| `None` | Q003 | `957d5d34-22eb-5ec5-b50a-80d9d95a0678`, `37a2cfc1-5201-59d9-84ad-6455a88b7bc0` |
| `957d5d34-22eb-5ec5-b50a-80d9d95a0678` | Q004 | `7c83b999-ae43-5ee3-9bad-97660ab97ff2` |
| `37a2cfc1-5201-59d9-84ad-6455a88b7bc0` | Q005, Q006 | `3b1f7006-2d44-5097-86b6-7ac05d0de3ac`, `6a0b0b39-d910-5b38-8d8d-6c1b1e22a351`, `f0dc8000-e9bd-5e45-8268-684ccf49c304`, `4493563c-595c-53a2-a21a-5c027c6d4dc4`, `abdd678e-c221-5e70-ae72-5397fd27c4f2`, `e87ba523-1aec-5c4d-a894-b21036323a93`, `4d9707ed-235e-543a-b90f-87c54d740e46`, `da2c7ffe-57fa-5b44-85ef-342e76a5820e` |
| `7c83b999-ae43-5ee3-9bad-97660ab97ff2` | Q007, Q008 | `e0d847f6-991b-5dc0-a66b-0deb99ce53dc`, `ff2b2fbc-89b4-55d1-a47b-7f9c096b4c3a`, `d9e48f2b-8a24-52ae-b418-79c6172fd473`, `e1203a0b-ace1-5f1a-b540-8ad4fc404824`, `34f2fead-a380-5f6e-b5bf-73382066e42f`, `8c6472f2-dbaf-572d-a5f6-5f4db1523ce7` |
| `e0d847f6-991b-5dc0-a66b-0deb99ce53dc` | Q009 | `995dd00c-c6f3-56b7-9870-5392bc1cffa0`, `7102e92a-5e93-5103-b719-d6e6946b7741`, `aca5ec40-e19f-51bc-9b2a-8eaf9b29b0a4` |
| `ff2b2fbc-89b4-55d1-a47b-7f9c096b4c3a` | Q010 | `51403b34-cc8d-5ba7-b9cf-9f02a5e636d4`, `185e9d9f-ac74-5621-aced-81909baa4077` |
| `d9e48f2b-8a24-52ae-b418-79c6172fd473` | Q011 | `4ad73579-5cf8-50bc-a385-33085176f7df`, `a5cb12bf-64a7-5154-b546-2f40b149168a`, `a8d71370-4be0-5801-9d5f-042508c0a2bf` |
| `e1203a0b-ace1-5f1a-b540-8ad4fc404824` | Q012, Q013 | `3d45bc79-6517-51e1-aef8-435cedc7bd42`, `30d5f421-351b-5d45-b251-1bd15b2e6e0f`, `c3575094-d44c-54b4-9dd8-d675dd76c738`, `9cacbba9-1d93-5069-8302-4437624c056f`, `d3ae7e6e-a12f-513d-b829-f83c43882511`, `15cb90d9-4e84-5a7d-b673-754766ca7e9e`, `e3e3ccb9-148f-5bc4-bb0a-608e462cba5c`, `4a9f78a4-d08a-5584-aff3-0b62d582e84c` |
| `34f2fead-a380-5f6e-b5bf-73382066e42f` | Q014 | `1ae7700c-15cc-5f51-8fee-f7240611ac5d` |
| `8c6472f2-dbaf-572d-a5f6-5f4db1523ce7` | Q015 | `a81d1c5d-4b13-58e1-ab79-b95a72cd6792` |
| `995dd00c-c6f3-56b7-9870-5392bc1cffa0` | Q016 | `549d72b8-68e2-527f-a3fa-c8fb033fe4a2`, `3bebaa64-eeef-5329-b3cc-dddc8e68f0a1`, `85e37e84-850b-55bb-8e2c-db84016e7e56`, `11610aaf-64f0-518d-b9c1-95070a8a7001` |
| `7102e92a-5e93-5103-b719-d6e6946b7741` | Q017 | `0b02d60f-6a4e-5cf6-9a46-91ba5bfe5b7d`, `f42ff582-c718-5196-917c-9178b1fb2c91` |
| `aca5ec40-e19f-51bc-9b2a-8eaf9b29b0a4` | Q018 | `b686895b-8c12-52ff-84c5-1acd55ee9e34`, `15f1b8b4-b836-5750-866a-f7d5f377a296` |
| `51403b34-cc8d-5ba7-b9cf-9f02a5e636d4` | Q019 | `e4de5a68-0b5a-5a21-bfe2-2924f3a7e70e`, `9f8337d3-e4d7-51cc-a27c-f8403bca7ad1`, `534ca674-79cd-5a7e-b7e0-b9258b338e8c` |
| `185e9d9f-ac74-5621-aced-81909baa4077` | Q020 | `0ff0d447-960a-5116-9fde-5989f4fc88fc`, `9d3c6a12-46a7-5285-a425-df2570bc7764` |
| `4ad73579-5cf8-50bc-a385-33085176f7df` | Q021 | `785dbfaa-3ede-5681-91dc-23574d49a09e`, `01283b43-9bb8-5430-aff3-c10cf3d29937`, `cf8f294e-a741-5295-8441-39a8caeeb802`, `1f9fc8f9-d21d-51be-8078-d50b4365fc87`, `29523042-4921-5e17-85a7-caadeab205ce` |
| `a5cb12bf-64a7-5154-b546-2f40b149168a` | Q022 | `52aff65f-f9bf-51bb-99c0-0a53063975ae`, `baa2ebfe-b4ae-5424-b435-0978cbda8219`, `74df37a8-5572-588b-a649-6045601c2aab` |
| `a8d71370-4be0-5801-9d5f-042508c0a2bf` | Q023 | `75acceb6-cebe-5b1b-be1c-a9d7dc230f94` |
| `1ae7700c-15cc-5f51-8fee-f7240611ac5d` | Q024 | `56b722c3-4a4c-50c9-bc55-a152ee3b276d`, `2ef2cd57-bb44-5bc3-a5e3-081de809894f`, `98da3d52-b694-59f6-be1f-912861048cdc`, `13130cb1-c8cf-5460-a77e-04115ef91419` |
| `a81d1c5d-4b13-58e1-ab79-b95a72cd6792` | Q025 | `ab19383d-8a81-5766-909c-92569f412a7a`, `10204309-7113-5913-aa66-6d95f9338f05` |
| `b686895b-8c12-52ff-84c5-1acd55ee9e34` | Q026 | `e4fb1b8a-aa7d-559f-a28b-47500a5c1a61`, `8d03e081-fa8a-554a-ab0f-ce2b978d9da4` |
| `15f1b8b4-b836-5750-866a-f7d5f377a296` | Q027 | `45845725-c424-5979-935e-799020ffdbdb`, `edc37a90-fbc4-5141-a96c-743419e57327`, `c7c0e167-bb2b-525b-89f7-0bea1608513c` |
| `785dbfaa-3ede-5681-91dc-23574d49a09e` | Q028 | `ab3f9261-b89d-58c9-aae6-ab8312d688c7`, `19bac67b-648d-5cb8-8dd5-ecbba72a895c`, `f2a92de7-8237-5af3-aa9c-cb854c54a493` |

## 官方八年级导言补充（2026-09-15）

在本轮标准快照完成后，按任务 A 的全年联系需要，直接核查并新增 [ccss-grade8-introduction.md](ccss-grade8-introduction.md)。它是 **官方网页补充**，不是本地 LC 年级节点的 `notes`，也不声明属于 `lc/v1.11.0`；既有本地字段仍然为 null，既有 JSON 字节和指纹保持不变。

- 来源：[CCSS 官方 Grade 8 » Introduction](https://www.thecorestandards.org/Math/Content/8/introduction/)。
- 实际核查日期：2026-09-15；核查记录时间：2026-09-15T02:03:25Z（Asia/Shanghai 2026-09-15 10:03:25）。
- 本次取得：开篇三个重点领域、编号 1–3 的完整导言，以及同页 Grade 8 Overview（五个内容领域下的 10 条概览和八项数学实践）。网页范围到 Mathematical Practices 第 8 项结束；未保留导航、视频或其他页面内容。
- 读取方式：直接 web open 指定官方页面并核对返回正文；没有沿教材或任务示例链接读取内容，没有读取 IM。Markdown 只转换排版，不添加课程排序、课时分配或模型推断。
- [官方 Public License](https://www.thecorestandards.org/public-license/) 于同日直接核查；新文件保留 NGA Center/CCSSO 归属及所要求的版权声明。
- 新文件 UTF-8 字节 SHA-256：`4f0cf331cc7c8d0a3842a4ce0cb306b230b72dae940dc6069dc44c41014f648f`。
- 此指纹是所保存 Markdown 文件的指纹，不是未保存的 HTTP 原响应 body 哈希。原页面没有提供本次可引用的独立版本号，因此以来源 URL、实际核查时间和文件指纹定位。
- 前文“未取得年级导言”的缺口现由此独立来源补齐；该补充不改变 71 个本地节点的计数和来源结论。
