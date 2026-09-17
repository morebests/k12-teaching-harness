# 23 校准结果表（由 `evaluate_grade.py report` 生成；自动匹配，人工核对见 README）

## 样本集 debug

| 检查 | 样本 | 合法对照 | 应检出 | 检出 | 位置正确 | 严重度一致 | 漏报 | 重大漏报 | 误报候选 | 其他发现 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 程序 | 7 | 2 | 2 | 2 | 2 | 2 | — | — | 0 | 0 |
| 专项：promises | 7 | 2 | 14 | 1 | 1 | 1 | km1-resources, km1-stats-data, km1-causal, km1-unbounded, km1-identity, km1-two-points, km1-overclaim, km2-range, km2-sampling, km2-intercept, km2-causal, inj-time-sum, inj-opportunity-f-a-3 | km1-resources, km1-stats-data, km2-sampling, inj-time-sum, inj-opportunity-f-a-3 | 0 | 7 |
| 专项：probes | 7 | 2 | 14 | 3 | 3 | 3 | km1-resources, km1-causal, km1-unbounded, km1-identity, km1-two-points, km2-sampling, km2-intercept, km2-causal, inj-assess-structural, inj-time-sum, inj-opportunity-f-a-3 | km1-resources, km2-sampling, inj-time-sum, inj-opportunity-f-a-3 | 0 | 0 |
| 专项：statements | 7 | 2 | 14 | 2 | 2 | 2 | km1-resources, km1-stats-data, km1-causal, km1-unbounded, km1-overclaim, km2-range, km2-sampling, km2-intercept, km2-causal, inj-assess-structural, inj-time-sum, inj-opportunity-f-a-3 | km1-resources, km1-stats-data, km2-sampling, inj-time-sum, inj-opportunity-f-a-3 | 0 | 12 |
| 整体评阅 r1 | 7 | 2 | 14 | 5 | 5 | 4 | km1-stats-data, km1-unbounded, km1-identity, km1-two-points, km1-overclaim, km2-range, km2-sampling, km2-intercept, km2-causal | km1-stats-data, km2-sampling | 0 | 17 |
| 整体评阅 r2 | 7 | 2 | 14 | 6 | 6 | 2 | km1-causal, km1-unbounded, km1-identity, km1-two-points, km2-range, km2-sampling, km2-intercept, km2-causal | km2-sampling | 0 | 9 |
| r1＋程序＋专项 | 7 | 2 | 14 | 10 | 10 | 9 | km1-unbounded, km2-sampling, km2-intercept, km2-causal | km2-sampling | 0 | 36 |
| r2＋程序＋专项 | 7 | 2 | 14 | 10 | 10 | 7 | km1-unbounded, km2-sampling, km2-intercept, km2-causal | km2-sampling | 0 | 28 |

### debug 逐样本

| 检查 | 样本 | 应检出 | 检出 | 漏报 | 误报候选 | 其他发现 |
| --- | --- | --- | --- | --- | --- | --- |
| r1 | d-known-initial | 7 | 2 | km1-stats-data, km1-unbounded, km1-identity, km1-two-points, km1-overclaim | — | 0 |
| r1 | d-known-revision | 4 | 0 | km2-range, km2-sampling, km2-intercept, km2-causal | — | 1 |
| r1 | d-assess-early | 1 | 1 | — | — | 2 |
| r1 | d-time-sum | 1 | 1 | — | — | 3 |
| r1 | d-opportunity-empty | 1 | 1 | — | — | 5 |
| r1 | d-control-renumber | 0 | 0 | — | — | 2 |
| r1 | d-control-resource | 0 | 0 | — | — | 4 |
| r1+checks | d-known-initial | 7 | 6 | km1-unbounded | — | 4 |
| r1+checks | d-known-revision | 4 | 1 | km2-sampling, km2-intercept, km2-causal | — | 4 |
| r1+checks | d-assess-early | 1 | 1 | — | — | 4 |
| r1+checks | d-time-sum | 1 | 1 | — | — | 5 |
| r1+checks | d-opportunity-empty | 1 | 1 | — | — | 7 |
| r1+checks | d-control-renumber | 0 | 0 | — | — | 5 |
| r1+checks | d-control-resource | 0 | 0 | — | — | 7 |
| r2 | d-known-initial | 7 | 3 | km1-causal, km1-unbounded, km1-identity, km1-two-points | — | 4 |
| r2 | d-known-revision | 4 | 0 | km2-range, km2-sampling, km2-intercept, km2-causal | — | 0 |
| r2 | d-assess-early | 1 | 1 | — | — | 1 |
| r2 | d-time-sum | 1 | 1 | — | — | 3 |
| r2 | d-opportunity-empty | 1 | 1 | — | — | 0 |
| r2 | d-control-renumber | 0 | 0 | — | — | 1 |
| r2 | d-control-resource | 0 | 0 | — | — | 0 |
| r2+checks | d-known-initial | 7 | 6 | km1-unbounded | — | 8 |
| r2+checks | d-known-revision | 4 | 1 | km2-sampling, km2-intercept, km2-causal | — | 3 |
| r2+checks | d-assess-early | 1 | 1 | — | — | 3 |
| r2+checks | d-time-sum | 1 | 1 | — | — | 5 |
| r2+checks | d-opportunity-empty | 1 | 1 | — | — | 2 |
| r2+checks | d-control-renumber | 0 | 0 | — | — | 4 |
| r2+checks | d-control-resource | 0 | 0 | — | — | 3 |

## 样本集 holdout-v1

| 检查 | 样本 | 合法对照 | 应检出 | 检出 | 位置正确 | 严重度一致 | 漏报 | 重大漏报 | 误报候选 | 其他发现 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 程序 | 8 | 3 | 0 | 0 | 0 | 0 | — | — | 0 | 0 |
| 专项：promises | 8 | 3 | 5 | 3 | 3 | 3 | hold-opportunity-sp-a-4, hold-revisit-roots | hold-opportunity-sp-a-4 | 0 | 7 |
| 专项：probes | 8 | 3 | 5 | 0 | 0 | 0 | hold-opportunity-sp-a-4, hold-assess-systems-early, hold-reserve-double, hold-revisit-roots, hold-order-systems-functions | hold-opportunity-sp-a-4, hold-reserve-double, hold-order-systems-functions | 0 | 0 |
| 专项：statements | 8 | 3 | 5 | 0 | 0 | 0 | hold-opportunity-sp-a-4, hold-assess-systems-early, hold-reserve-double, hold-revisit-roots, hold-order-systems-functions | hold-opportunity-sp-a-4, hold-reserve-double, hold-order-systems-functions | 1 | 13 |
| 整体评阅 r1 | 8 | 3 | 5 | 4 | 4 | 2 | hold-revisit-roots | — | 0 | 15 |
| 整体评阅 r2 | 8 | 3 | 5 | 4 | 4 | 2 | hold-revisit-roots | — | 0 | 11 |
| r1＋程序＋专项 | 8 | 3 | 5 | 4 | 4 | 3 | hold-revisit-roots | — | 1 | 35 |
| r2＋程序＋专项 | 8 | 3 | 5 | 4 | 4 | 3 | hold-revisit-roots | — | 1 | 31 |

### holdout-v1 逐样本

| 检查 | 样本 | 应检出 | 检出 | 漏报 | 误报候选 | 其他发现 |
| --- | --- | --- | --- | --- | --- | --- |
| r1 | h-opportunity-empty | 1 | 1 | — | — | 3 |
| r1 | h-assess-before-learning | 1 | 1 | — | — | 2 |
| r1 | h-reserve-double-count | 1 | 1 | — | — | 2 |
| r1 | h-revisit-dropped | 1 | 0 | hold-revisit-roots | — | 0 |
| r1 | h-order-dependency | 1 | 1 | — | — | 3 |
| r1 | h-control-swap | 0 | 0 | — | — | 2 |
| r1 | h-control-revisit | 0 | 0 | — | — | 2 |
| r1 | h-control-resource | 0 | 0 | — | — | 1 |
| r1+checks | h-opportunity-empty | 1 | 1 | — | — | 6 |
| r1+checks | h-assess-before-learning | 1 | 1 | — | — | 4 |
| r1+checks | h-reserve-double-count | 1 | 1 | — | — | 6 |
| r1+checks | h-revisit-dropped | 1 | 0 | hold-revisit-roots | — | 3 |
| r1+checks | h-order-dependency | 1 | 1 | — | — | 4 |
| r1+checks | h-control-swap | 0 | 0 | — | statements:h-control-swap:1 | 4 |
| r1+checks | h-control-revisit | 0 | 0 | — | — | 4 |
| r1+checks | h-control-resource | 0 | 0 | — | — | 4 |
| r2 | h-opportunity-empty | 1 | 1 | — | — | 3 |
| r2 | h-assess-before-learning | 1 | 1 | — | — | 1 |
| r2 | h-reserve-double-count | 1 | 1 | — | — | 3 |
| r2 | h-revisit-dropped | 1 | 0 | hold-revisit-roots | — | 0 |
| r2 | h-order-dependency | 1 | 1 | — | — | 2 |
| r2 | h-control-swap | 0 | 0 | — | — | 0 |
| r2 | h-control-revisit | 0 | 0 | — | — | 2 |
| r2 | h-control-resource | 0 | 0 | — | — | 0 |
| r2+checks | h-opportunity-empty | 1 | 1 | — | — | 6 |
| r2+checks | h-assess-before-learning | 1 | 1 | — | — | 3 |
| r2+checks | h-reserve-double-count | 1 | 1 | — | — | 7 |
| r2+checks | h-revisit-dropped | 1 | 0 | hold-revisit-roots | — | 3 |
| r2+checks | h-order-dependency | 1 | 1 | — | — | 3 |
| r2+checks | h-control-swap | 0 | 0 | — | statements:h-control-swap:1 | 2 |
| r2+checks | h-control-revisit | 0 | 0 | — | — | 4 |
| r2+checks | h-control-resource | 0 | 0 | — | — | 3 |

## 样本集 holdout-v2

| 检查 | 样本 | 合法对照 | 应检出 | 检出 | 位置正确 | 严重度一致 | 漏报 | 重大漏报 | 误报候选 | 其他发现 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 程序 | 14 | 4 | 5 | 4 | 4 | 3 | h2i-10 | — | 0 | 1 |
| 专项：promises | 14 | 4 | 10 | 3 | 3 | 3 | h2i-01, h2i-02, h2i-03, h2i-06, h2i-07, h2i-09, h2i-10 | h2i-01, h2i-02, h2i-03, h2i-06, h2i-07, h2i-09 | 0 | 14 |
| 专项：probes | 14 | 4 | 10 | 1 | 1 | 1 | h2i-01, h2i-02, h2i-03, h2i-04, h2i-05, h2i-06, h2i-07, h2i-08, h2i-10 | h2i-01, h2i-02, h2i-03, h2i-04, h2i-06, h2i-07 | 0 | 0 |
| 专项：statements | 14 | 4 | 10 | 1 | 1 | 1 | h2i-01, h2i-02, h2i-04, h2i-05, h2i-06, h2i-07, h2i-08, h2i-09, h2i-10 | h2i-01, h2i-02, h2i-04, h2i-06, h2i-07, h2i-09 | 0 | 24 |
| 整体评阅 r1 | 14 | 4 | 10 | 7 | 6 | 5 | h2i-03, h2i-08, h2i-10 | h2i-03 | 0 | 31 |
| 整体评阅 r2 | 14 | 4 | 10 | 8 | 7 | 6 | h2i-08, h2i-10 | — | 0 | 28 |
| r1＋程序＋专项 | 14 | 4 | 10 | 9 | 9 | 7 | h2i-10 | — | 0 | 70 |
| r2＋程序＋专项 | 14 | 4 | 10 | 9 | 9 | 7 | h2i-10 | — | 0 | 67 |

### holdout-v2 逐样本

| 检查 | 样本 | 应检出 | 检出 | 漏报 | 误报候选 | 其他发现 |
| --- | --- | --- | --- | --- | --- | --- |
| r1 | h2-01 | 1 | 1 | — | — | 2 |
| r1 | h2-02 | 0 | 0 | — | — | 2 |
| r1 | h2-03 | 1 | 1 | — | — | 0 |
| r1 | h2-04 | 1 | 0 | h2i-03 | — | 3 |
| r1 | h2-05 | 1 | 1 | — | — | 4 |
| r1 | h2-06 | 1 | 1 | — | — | 5 |
| r1 | h2-07 | 1 | 1 | — | — | 1 |
| r1 | h2-08 | 0 | 0 | — | — | 0 |
| r1 | h2-09 | 1 | 1 | — | — | 6 |
| r1 | h2-10 | 1 | 0 | h2i-08 | — | 1 |
| r1 | h2-11 | 0 | 0 | — | — | 0 |
| r1 | h2-12 | 1 | 1 | — | — | 3 |
| r1 | h2-13 | 0 | 0 | — | — | 0 |
| r1 | h2-14 | 1 | 0 | h2i-10 | — | 4 |
| r1+checks | h2-01 | 1 | 1 | — | — | 5 |
| r1+checks | h2-02 | 0 | 0 | — | — | 5 |
| r1+checks | h2-03 | 1 | 1 | — | — | 3 |
| r1+checks | h2-04 | 1 | 1 | — | — | 6 |
| r1+checks | h2-05 | 1 | 1 | — | — | 10 |
| r1+checks | h2-06 | 1 | 1 | — | — | 7 |
| r1+checks | h2-07 | 1 | 1 | — | — | 3 |
| r1+checks | h2-08 | 0 | 0 | — | — | 2 |
| r1+checks | h2-09 | 1 | 1 | — | — | 9 |
| r1+checks | h2-10 | 1 | 1 | — | — | 4 |
| r1+checks | h2-11 | 0 | 0 | — | — | 1 |
| r1+checks | h2-12 | 1 | 1 | — | — | 5 |
| r1+checks | h2-13 | 0 | 0 | — | — | 3 |
| r1+checks | h2-14 | 1 | 0 | h2i-10 | — | 7 |
| r2 | h2-01 | 1 | 1 | — | — | 2 |
| r2 | h2-02 | 0 | 0 | — | — | 2 |
| r2 | h2-03 | 1 | 1 | — | — | 0 |
| r2 | h2-04 | 1 | 1 | — | — | 0 |
| r2 | h2-05 | 1 | 1 | — | — | 3 |
| r2 | h2-06 | 1 | 1 | — | — | 4 |
| r2 | h2-07 | 1 | 1 | — | — | 4 |
| r2 | h2-08 | 0 | 0 | — | — | 2 |
| r2 | h2-09 | 1 | 1 | — | — | 4 |
| r2 | h2-10 | 1 | 0 | h2i-08 | — | 0 |
| r2 | h2-11 | 0 | 0 | — | — | 3 |
| r2 | h2-12 | 1 | 1 | — | — | 3 |
| r2 | h2-13 | 0 | 0 | — | — | 1 |
| r2 | h2-14 | 1 | 0 | h2i-10 | — | 0 |
| r2+checks | h2-01 | 1 | 1 | — | — | 5 |
| r2+checks | h2-02 | 0 | 0 | — | — | 5 |
| r2+checks | h2-03 | 1 | 1 | — | — | 3 |
| r2+checks | h2-04 | 1 | 1 | — | — | 3 |
| r2+checks | h2-05 | 1 | 1 | — | — | 9 |
| r2+checks | h2-06 | 1 | 1 | — | — | 6 |
| r2+checks | h2-07 | 1 | 1 | — | — | 6 |
| r2+checks | h2-08 | 0 | 0 | — | — | 4 |
| r2+checks | h2-09 | 1 | 1 | — | — | 7 |
| r2+checks | h2-10 | 1 | 1 | — | — | 3 |
| r2+checks | h2-11 | 0 | 0 | — | — | 4 |
| r2+checks | h2-12 | 1 | 1 | — | — | 5 |
| r2+checks | h2-13 | 0 | 0 | — | — | 4 |
| r2+checks | h2-14 | 1 | 0 | h2i-10 | — | 3 |

## 整体评阅的作答可靠性

| 评阅 | samples | failed_calls | incomplete_usage_calls | findings | rejected_findings | rejected_citations | unverified_objects | unobservable_ratings | problems | repairs | first_attempt_rejected_citations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| r1 | 29 | 0 | 0 | 100 | 0 | 5 | 0 | 0 | 0 | 50 | 81 |
| r2 | 29 | 0 | 0 | 88 | 0 | 5 | 0 | 0 | 1 | 46 | 76 |

## 专项检查的作答可靠性

| 专项 | samples | errors | findings | rejected_findings | rejected_citations | problems | repairs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| promises | 30 | 0 | 37 | 0 | 0 | 2 | 5 |
| probes | 30 | 0 | 5 | 0 | 0 | 0 | 0 |
| statements | 30 | 0 | 54 | 0 | 0 | 0 | 3 |

## r1 与 r2 的逐维评分一致性

| pairs | exact | differ_by_1 | differ_by_2_or_more | critical_disagreements |
| --- | --- | --- | --- | --- |
| 240 | 179 | 50 | 11 | 10 |

## 汇总：b-final

加权总分：82.5；等权：81.25；重大失败：False；已定维度权重 100，其加权分 82.5；未出总分原因：—

| 维度 | 状态 | 分数 | 区间下限 | 区间上限 | 重大失败 | 原始分 | 复核触发 | 问题 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | settled | 4 | — | — | False | r1=4; r2=4 | — | — |
| Q2 | settled | 3 | — | — | False | r1=3; r2=3 | — | — |
| Q3 | settled | 4 | — | — | False | r1=4; r2=4 | — | — |
| Q4 | settled | 2 | — | — | False | r1=4; r2=4 | — | — |
| Q5 | settled | 2 | — | — | False | r1=4; r2=4 | — | — |
| Q6 | settled | 4 | — | — | False | r1=4; r2=4 | — | — |
| Q7 | settled | 4 | — | — | False | r1=4; r2=4 | — | — |
| Q8 | settled | 3 | — | — | False | r1=3; r2=3 | — | — |

## 汇总：d-known-initial

加权总分：None；等权：None；重大失败：True；已定维度权重 85，其加权分 55.0；未出总分原因：Q6：invalid

| 维度 | 状态 | 分数 | 区间下限 | 区间上限 | 重大失败 | 原始分 | 复核触发 | 问题 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | settled | 4 | — | — | False | r1=4; r2=4 | — | — |
| Q2 | settled | 3 | — | — | False | r1=4; r2=3 | 评分不一致，须依据对象清单复核后形成共同值或独立裁定 | — |
| Q3 | settled | 3 | — | — | False | r1=4; r2=3 | 评分不一致，须依据对象清单复核后形成共同值或独立裁定 | — |
| Q4 | settled | 2 | — | — | False | r1=2; r2=2 | — | — |
| Q5 | settled | 2 | — | — | False | r1=4; r2=3 | 评分不一致，须依据对象清单复核后形成共同值或独立裁定 | — |
| Q6 | invalid | None | — | — | False | r1=4; r2=3 | 评分不一致，须依据对象清单复核后形成共同值或独立裁定 | 裁定引用失效 ['ev:d-known-initial:04775ba665ac46d5'] |
| Q7 | settled | 0 | — | — | True | r1=0; r2=0 | — | — |
| Q8 | settled | 4 | — | — | False | r1=4; r2=3 | 评分不一致，须依据对象清单复核后形成共同值或独立裁定 | — |

## 比较：b-final 对 d-known-initial

裁定：对应范围不合格；加权方向 None；等权方向 None；权重浮动翻转 None；评阅方向冲突 —；说明：有已确认重大失败的一方在对应范围不合格；另一方未失败不自动证明全部更优

| 维度 | 判断 | a 状态 | b 状态 | 理由 |
| --- | --- | --- | --- | --- |
| Q1 | same_score | settled | settled | 同分；未做配对核查，不代表等效 |
| Q2 | same_score | settled | settled | 同分；未做配对核查，不代表等效 |
| Q3 | a_stronger | settled | settled | (4, 4) 高于 (3, 3) |
| Q4 | same_score | settled | settled | 同分；未做配对核查，不代表等效 |
| Q5 | same_score | settled | settled | 同分；未做配对核查，不代表等效 |
| Q6 | undetermined | settled | invalid | 缺少可用分数 |
| Q7 | a_stronger | settled | settled | (4, 4) 高于 (0, 0) |
| Q8 | b_stronger | settled | settled | (4, 4) 高于 (3, 3) |

## 模型用量

| 角色 | 调用 | 用量不完整 | 输入 | 输出 | 合计 |
| --- | --- | --- | --- | --- | --- |
| r1 | 120 | 0 | 8197305 | 2289065 | 10486370 |
| r2 | 120 | 0 | 8088093 | 2331308 | 10419401 |
| r1-round-1 | 24 | 0 | 1102229 | 347973 | 1450202 |
| promises | 30 | 0 | 990219 | 764158 | 1754377 |
| statements | 30 | 0 | 446520 | 319632 | 766152 |
| probes | 16 | 0 | 149783 | 91672 | 241455 |
| r3 | 8 | 0 | 395255 | 34442 | 429697 |
| reviser | 2 | 0 | 47395 | 6185 | 53580 |
| recheck | 2 | 0 | 126265 | 16042 | 142307 |
