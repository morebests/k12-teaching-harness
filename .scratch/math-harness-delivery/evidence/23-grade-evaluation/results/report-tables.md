# 23 校准结果表（由 `evaluate_grade.py report` 生成）

## 检出、漏报与误报候选（自动匹配；人工核对见 README）

| 检查 | 样本集 | 样本 | 合法对照 | 应检出 | 检出 | 位置正确 | 严重度一致 | 漏报 | 重大漏报 | 误报候选 | 其他发现 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| program | debug | 7 | 2 | 2 | 2 | 2 | 2 | — | — | 0 | 0 |
| program | holdout | 8 | 3 | 0 | 0 | 0 | 0 | — | — | 0 | 0 |
| r1 | debug | 7 | 2 | 14 | 7 | 7 | 5 | km1-unbounded, km1-identity, km1-two-points, km2-range, km2-sampling, km2-intercept, km2-causal | km2-sampling | 0 | 17 |
| r1 | holdout | 8 | 3 | 5 | 4 | 4 | 2 | hold-revisit-roots | — | 0 | 15 |
| r2 | debug | 7 | 2 | 14 | 6 | 6 | 2 | km1-causal, km1-unbounded, km1-identity, km1-two-points, km2-range, km2-sampling, km2-intercept, km2-causal | km2-sampling | 0 | 9 |
| r2 | holdout | 8 | 3 | 5 | 4 | 4 | 2 | hold-revisit-roots | — | 0 | 11 |

## 模型逐样本

| 评阅 | 样本 | 应检出 | 检出 | 漏报 | 误报候选 | 其他发现 |
| --- | --- | --- | --- | --- | --- | --- |
| r1 | d-known-initial | 7 | 4 | km1-unbounded, km1-identity, km1-two-points | — | 0 |
| r1 | d-known-revision | 4 | 0 | km2-range, km2-sampling, km2-intercept, km2-causal | — | 1 |
| r1 | d-assess-early | 1 | 1 | — | — | 2 |
| r1 | d-time-sum | 1 | 1 | — | — | 3 |
| r1 | d-opportunity-empty | 1 | 1 | — | — | 5 |
| r1 | d-control-renumber | 0 | 0 | — | — | 2 |
| r1 | d-control-resource | 0 | 0 | — | — | 4 |
| r1 | h-opportunity-empty | 1 | 1 | — | — | 3 |
| r1 | h-assess-before-learning | 1 | 1 | — | — | 2 |
| r1 | h-reserve-double-count | 1 | 1 | — | — | 2 |
| r1 | h-revisit-dropped | 1 | 0 | hold-revisit-roots | — | 0 |
| r1 | h-order-dependency | 1 | 1 | — | — | 3 |
| r1 | h-control-swap | 0 | 0 | — | — | 2 |
| r1 | h-control-revisit | 0 | 0 | — | — | 2 |
| r1 | h-control-resource | 0 | 0 | — | — | 1 |
| r2 | d-known-initial | 7 | 3 | km1-causal, km1-unbounded, km1-identity, km1-two-points | — | 4 |
| r2 | d-known-revision | 4 | 0 | km2-range, km2-sampling, km2-intercept, km2-causal | — | 0 |
| r2 | d-assess-early | 1 | 1 | — | — | 1 |
| r2 | d-time-sum | 1 | 1 | — | — | 3 |
| r2 | d-opportunity-empty | 1 | 1 | — | — | 0 |
| r2 | d-control-renumber | 0 | 0 | — | — | 1 |
| r2 | d-control-resource | 0 | 0 | — | — | 0 |
| r2 | h-opportunity-empty | 1 | 1 | — | — | 3 |
| r2 | h-assess-before-learning | 1 | 1 | — | — | 1 |
| r2 | h-reserve-double-count | 1 | 1 | — | — | 3 |
| r2 | h-revisit-dropped | 1 | 0 | hold-revisit-roots | — | 0 |
| r2 | h-order-dependency | 1 | 1 | — | — | 2 |
| r2 | h-control-swap | 0 | 0 | — | — | 0 |
| r2 | h-control-revisit | 0 | 0 | — | — | 2 |
| r2 | h-control-resource | 0 | 0 | — | — | 0 |

## 模型作答可靠性

| 评阅 | samples | failed_calls | incomplete_usage_calls | findings | rejected_findings | rejected_citations | unverified_objects | unobservable_ratings | problems | repairs | first_attempt_rejected_citations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| r1 | 15 | 0 | 0 | 57 | 0 | 2 | 0 | 0 | 0 | 26 | 39 |
| r2 | 15 | 0 | 0 | 44 | 0 | 3 | 0 | 0 | 1 | 24 | 42 |

## r1 与 r2 的逐维评分一致性

| pairs | exact | differ_by_1 | differ_by_2_or_more | critical_disagreements |
| --- | --- | --- | --- | --- |
| 128 | 97 | 27 | 4 | 3 |

## 汇总：b-final

加权总分：95.0；等权：93.75；重大失败：False；已定维度权重 100，其加权分 95.0；未出总分原因：—

| 维度 | 状态 | 分数 | 区间下限 | 区间上限 | 重大失败 | 原始分 | 复核触发 | 问题数 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | settled | 4 | — | — | False | r1=4; r2=4 | — | 0 |
| Q2 | settled | 3 | — | — | False | r1=3; r2=3 | — | 0 |
| Q3 | settled | 4 | — | — | False | r1=4; r2=4 | — | 0 |
| Q4 | settled | 4 | — | — | False | r1=4; r2=4 | — | 0 |
| Q5 | settled | 4 | — | — | False | r1=4; r2=4 | — | 0 |
| Q6 | settled | 4 | — | — | False | r1=4; r2=4 | — | 0 |
| Q7 | settled | 4 | — | — | False | r1=4; r2=4 | — | 0 |
| Q8 | settled | 3 | — | — | False | r1=3; r2=3 | — | 0 |

## 汇总：d-known-initial

加权总分：71.25；等权：71.875；重大失败：True；已定维度权重 100，其加权分 71.25；未出总分原因：—

| 维度 | 状态 | 分数 | 区间下限 | 区间上限 | 重大失败 | 原始分 | 复核触发 | 问题数 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | settled | 4 | — | — | False | r1=4; r2=4 | — | 0 |
| Q2 | settled | 3 | — | — | False | r1=4; r2=3 | 评分不一致，须依据对象清单复核后形成共同值或独立裁定 | 0 |
| Q3 | settled | 3 | — | — | False | r1=4; r2=3 | 评分不一致，须依据对象清单复核后形成共同值或独立裁定 | 0 |
| Q4 | settled | 2 | — | — | False | r1=2; r2=2 | — | 0 |
| Q5 | settled | 4 | — | — | False | r1=4; r2=3 | 评分不一致，须依据对象清单复核后形成共同值或独立裁定 | 0 |
| Q6 | settled | 3 | — | — | False | r1=4; r2=3 | 评分不一致，须依据对象清单复核后形成共同值或独立裁定 | 0 |
| Q7 | settled | 0 | — | — | True | r1=0; r2=0 | — | 0 |
| Q8 | settled | 4 | — | — | False | r1=4; r2=3 | 评分不一致，须依据对象清单复核后形成共同值或独立裁定 | 0 |

## 比较：b-final 对 d-known-initial

裁定：对应范围不合格；加权方向 a；等权方向 a；权重浮动翻转 False；评阅方向冲突 —；说明：有已确认重大失败的一方在对应范围不合格；另一方未失败不自动证明全部更优

| 维度 | 判断 | a 状态 | b 状态 | 理由 |
| --- | --- | --- | --- | --- |
| Q1 | same_score | settled | settled | 同分；未做配对核查，不代表等效 |
| Q2 | same_score | settled | settled | 同分；未做配对核查，不代表等效 |
| Q3 | a_stronger | settled | settled | (4, 4) 高于 (3, 3) |
| Q4 | a_stronger | settled | settled | (4, 4) 高于 (2, 2) |
| Q5 | same_score | settled | settled | 同分；未做配对核查，不代表等效 |
| Q6 | a_stronger | settled | settled | (4, 4) 高于 (3, 3) |
| Q7 | a_stronger | settled | settled | (4, 4) 高于 (0, 0) |
| Q8 | b_stronger | settled | settled | (4, 4) 高于 (3, 3) |

## 模型用量

| 角色 | 调用 | 用量不完整 | 输入 | 输出 | 合计 |
| --- | --- | --- | --- | --- | --- |
| r1 | 64 | 0 | 4307663 | 1187520 | 5495183 |
| r2 | 64 | 0 | 4421831 | 1226796 | 5648627 |
| r1-round-1 | 24 | 0 | 1102229 | 347973 | 1450202 |
| r3 | 5 | 0 | 181881 | 13599 | 195480 |
| reviser | 2 | 0 | 47395 | 6185 | 53580 |
| recheck | 2 | 0 | 126265 | 16042 | 142307 |
