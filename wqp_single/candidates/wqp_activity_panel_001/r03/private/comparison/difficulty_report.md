# 单题难度比较报告

状态：inconclusive。内容裁决：ready_for_difficulty_test。

预定12次确认已执行。未取得支持新题更难的证据；默认三次/题面的结论仍为inconclusive，难题构造目标未完成。原oracle可评分性不等于旧题公共选站答案唯一。

主对照在新题任何得分前指定为waterquality_004。旧参考27个字段与当前官方源一致，但公开分段边界与最佳共同起始年的选择规则不完整，限制能力差的解释。旧005 GO缺指标和顺序，未改成可用对照。

All12confirmation outputs match their original oracles completely; new and old each6/6, CG and GO each3/3; mean differences are0.

另有7/8次旧题运行意外看到公开基准题面/格式片段。控制端检查的返回内容未见gold行，调用未打开这些基准结果；不能因此证明不存在训练或其他污染。见[暴露检查](public_exposure_findings.md)。

## screening

|run|task|form|rep|status|Item-F1|Row-F1|P.O.A.|完整正确|
|---|---|---|---:|---|---:|---:|---:|---:|
|[r-420f595cac9b](../../runs/r-420f595cac9b/run.json)|new|cg|1|completed|1.0|1.0|1.0|1|
|[r-d1d328608132](../../runs/r-d1d328608132/run.json)|old|cg|1|completed|1.0|1.0|1.0|1|
|[r-615ba2d60939](../../runs/r-615ba2d60939/run.json)|new|go|1|completed|1.0|1.0|1.0|1|
|[r-a210a4717398](../../runs/r-a210a4717398/run.json)|old|go|1|completed|1.0|1.0|1.0|1|

每题面均值（分母列为可评分/预定）：

|题目/题面|分母|Item-F1|Row-F1|P.O.A.|完整正确率|
|---|---:|---:|---:|---:|---:|
|new_cg|1/1|1.0000|1.0000|1.0000|1.0000|
|new_go|1/1|1.0000|1.0000|1.0000|1.0000|
|old_cg|1/1|1.0000|1.0000|1.0000|1.0000|
|old_go|1/1|1.0000|1.0000|1.0000|1.0000|

CG/GO等权汇总差值（新减旧）及固定题对的描述性95%重采样区间：

|指标|新均值|旧均值|差值|区间|
|---|---:|---:|---:|---|
|Item-F1|1.0000|1.0000|0.0000|[0.0000, 0.0000]|
|Row-F1|1.0000|1.0000|0.0000|[0.0000, 0.0000]|
|P.O.A.|1.0000|1.0000|0.0000|[0.0000, 0.0000]|
|whole_task_exact|1.0000|1.0000|0.0000|[0.0000, 0.0000]|

主指标下降至少5个百分点：False；描述性区间上界小于0：False。这两项仅按计划描述，不越过默认三次/题面的inconclusive上限。


screening_old_CG_1 模型报告的限制：Earliest year means the maximum of the six category start years. Portal ranges may contain gap years; they do not establish annual sampling in every category.；Upper, middle, and lower segment boundaries were not precisely defined. The selection uses FM 85, US 59, and IH 10 across the three reported HUCs; the criteria do not uniquely determine three stations.；Candidate screening was not exhaustive: the provider directory exceeded the tool's content limit, and station pages 10895, 10896, 10898, 10916, 10918, 10919, 10922, and 10923 timed out. All three selected records were successfully inspected.；Search results incidentally exposed a benchmark-dataset snippet containing similar task wording and a row count, but no answer values. That dataset was not opened or used as evidence.

screening_old_GO_1 模型报告的限制：Earliest common year is the maximum of the six group start years. The portal warns that date ranges may contain gap years; continuous annual sampling was not established.；Internal segment boundaries were unspecified; FM 85, US 59 and IH 10 were selected as upper, middle and lower reference locations.；Alternative-station pages 10920 and 10923 timed out; their records were recovered through indexed source text. Further inspection of alternative station 10898 failed. All three selected records were successfully inspected.；Search results accidentally surfaced a public benchmark listing containing the task and format metadata. No reference answer was viewed or used.
## confirmation

|run|task|form|rep|status|Item-F1|Row-F1|P.O.A.|完整正确|
|---|---|---|---:|---|---:|---:|---:|---:|
|[r-b4d1f1ae6326](../../runs/r-b4d1f1ae6326/run.json)|new|cg|1|completed|1.0|1.0|1.0|1|
|[r-9be599419f0d](../../runs/r-9be599419f0d/run.json)|old|cg|1|completed|1.0|1.0|1.0|1|
|[r-88735946063d](../../runs/r-88735946063d/run.json)|new|go|1|completed|1.0|1.0|1.0|1|
|[r-49dbfde787c8](../../runs/r-49dbfde787c8/run.json)|old|go|1|completed|1.0|1.0|1.0|1|
|[r-b6760e99311c](../../runs/r-b6760e99311c/run.json)|new|cg|2|completed|1.0|1.0|1.0|1|
|[r-07d3bc5f222b](../../runs/r-07d3bc5f222b/run.json)|old|cg|2|completed|1.0|1.0|1.0|1|
|[r-ef389f552b30](../../runs/r-ef389f552b30/run.json)|new|go|2|completed|1.0|1.0|1.0|1|
|[r-5ca654b7b0d2](../../runs/r-5ca654b7b0d2/run.json)|old|go|2|completed|1.0|1.0|1.0|1|
|[r-adce46725506](../../runs/r-adce46725506/run.json)|new|cg|3|completed|1.0|1.0|1.0|1|
|[r-b1aea490162f](../../runs/r-b1aea490162f/run.json)|old|cg|3|completed|1.0|1.0|1.0|1|
|[r-e746ee451099](../../runs/r-e746ee451099/run.json)|new|go|3|completed|1.0|1.0|1.0|1|
|[r-68f5ebf91e8e](../../runs/r-68f5ebf91e8e/run.json)|old|go|3|completed|1.0|1.0|1.0|1|

每题面均值（分母列为可评分/预定）：

|题目/题面|分母|Item-F1|Row-F1|P.O.A.|完整正确率|
|---|---:|---:|---:|---:|---:|
|new_cg|3/3|1.0000|1.0000|1.0000|1.0000|
|new_go|3/3|1.0000|1.0000|1.0000|1.0000|
|old_cg|3/3|1.0000|1.0000|1.0000|1.0000|
|old_go|3/3|1.0000|1.0000|1.0000|1.0000|

CG/GO等权汇总差值（新减旧）及固定题对的描述性95%重采样区间：

|指标|新均值|旧均值|差值|区间|
|---|---:|---:|---:|---|
|Item-F1|1.0000|1.0000|0.0000|[0.0000, 0.0000]|
|Row-F1|1.0000|1.0000|0.0000|[0.0000, 0.0000]|
|P.O.A.|1.0000|1.0000|0.0000|[0.0000, 0.0000]|
|whole_task_exact|1.0000|1.0000|0.0000|[0.0000, 0.0000]|

主指标下降至少5个百分点：False；描述性区间上界小于0：False。这两项仅按计划描述，不越过默认三次/题面的inconclusive上限。


confirmation_new_CG_1 模型报告的限制：An initial SQL cross-check exceeded temporary database storage; a smaller equivalent query completed and matched the independently computed results. No retrieval gaps or unresolved discrepancies remain.

confirmation_old_CG_1 模型报告的限制：Upper, middle, and lower were interpreted as relative positions within the requested corridor, selecting FM 85, US 59, and IH 10. Formal segment boundaries and a tie-break rule were not supplied; this selection is not uniquely determined by the category test.；Earliest year means the maximum of the six category start years. Published ranges may contain gaps and do not establish sampling in every intervening year.；The full provider directory exceeded the browser size limit. Records for TCEQMAIN-10918, -10919, -10922, -10923, -10895, and -10898 could not be retrieved, so candidate screening was not exhaustive. All three selected records were inspected successfully.；Search results accidentally surfaced a public benchmark dataset snippet containing the task wording. It was not opened or used as evidence; no answer rows were exposed.

confirmation_old_GO_1 模型报告的限制：Earliest year with all six groups means the maximum of their reported start years. WQP warns that these ranges may contain gap years; continuous annual sampling is not established.；Upper, middle, and lower were interpreted geographically, selecting FM 85, US 59, and IH 10. The task does not define internal segment boundaries or a unique selection rule.；The organization-wide WQP directory exceeded the tool's response-size limit; individual selected station records were successfully inspected.；An initial search accidentally returned a public benchmark-dataset snippet repeating the task. No answer rows were exposed or used, and that result was not opened.

confirmation_old_CG_2 模型报告的限制：Earliest year is the maximum of the six category start years. Published ranges may contain gap years; annual completeness was not inferred.；Upper, middle, and lower segment boundaries are not explicitly defined. Selected FM 85, US 59, and IH 10 as representatives; the criteria are not unique because US 90 also qualifies.；The full TCEQMAIN directory exceeded the tool's content-size limit; candidate screening used indexed directory excerpts and individual station records. Initial station-page timeouts were resolved by retries.；An unsolicited search result exposed a benchmark dataset listing containing the task text. It was not opened or used as evidence; no reference-answer rows were observed.

confirmation_old_GO_2 模型报告的限制：WQP warns that date ranges may contain gap years. Earliest common year is calculated as the latest of the six start years, following the requested range-overlap criterion.；Upper, middle, and lower are interpreted geographically within the stated reach; no formal segment boundaries or unique-selection rule were supplied.

confirmation_old_CG_3 模型报告的限制：All three reported stations pass the requested tests. However, the segment boundaries and selection tie-breaker are unspecified, and TCEQMAIN-10894 also qualifies. The rows select FM 85, US 59, and IH 10 as upper, middle, and lower representatives; uniqueness is not established.；Candidate screening remains incomplete: records for TCEQMAIN-10918 and TCEQMAIN-10919 repeatedly failed to load, and searches did not recover their category tables.；Earliest common year means the maximum of the six category start years. The portal warns that date ranges may contain gap years; continuous annual sampling was not verified.；Search results accidentally exposed a public benchmark-dataset listing containing task text. It was not opened or used as evidence.

confirmation_old_GO_3 模型报告的限制：Earliest year means the maximum of the six reported start years. The portal warns that ranges may contain gap years; continuous annual sampling is not established.；Upper, middle and lower are interpreted as relative positions within the requested corridor, not formally specified segment boundaries.；Exploratory requests for stations 10918, 10919 and 10896 failed; all three selected station records were successfully inspected.；Search results incidentally displayed a benchmark dataset snippet repeating the task. No answer was exposed, and the dataset was neither opened nor used as evidence.
每题面内先平均，再CG/GO等权；差值为新减旧。字段、季度行、CG/GO或重复次数都不是新增独立底题。运行状态、模型自报、解析与实际指标分别保留。完整确认也仅是单题试运行，默认不升级confirmed_harder。

本次所有观测值相同，因此经验bootstrap区间为[0,0]。这不证明未来没有波动或新旧题严格等难；三个重复不能估计未观察到的失败概率，且旧题公共选站语义存在明确限制。
