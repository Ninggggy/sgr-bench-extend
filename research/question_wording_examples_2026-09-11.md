# 题面语言改写示例

按用户要求补充：让题目更清楚、通俗，像真实的信息请求。以下以现有三题为例；英文是题面示例，中文说明写法。它们是编辑草稿，不替换已测试题面，不承接旧成绩，也未进行新的实验或独立语义审计。

## 1. arxiv_historical_title_001/r02：先交代要找的关系

原开头的“audit historical title changes across direct replacement records”把抽象概念挤在一起。可以先说明要找什么，再给出精确的范围和版本规则：

> Find withdrawn preprints that direct readers to another record for the same work. Among these replacements, identify those whose title at the specified historical cutoff differs from their current title.

这是开头示例，不是完整题面。后文仍须保留2021年首次提交、当前cs.LG类别及交叉分类、2026年9月9日观察日期、直接替代的纳排，以及“源记录最后一个标记撤回的版本的提交时间”这一精确截止定义。不能为了通俗把它简称为“撤回日期”。标题比较和输出规则也须保留。

## 2. arxiv_historical_title_002/r03：拆开范围、关系和时间规则

下面是CG正文的分段改写草稿。主要变化是移除全大写强调和长句嵌套，把查找对象、关系纳排和历史版本选择分别说明。

> Build a historical bibliography of the successor records named by withdrawn preprints. For each qualifying relationship, report the successor version and title that meet the cutoff rule below.
>
> Use public catalogue metadata current through 9 September 2026. Start with all records first submitted in 2020, using UTC dates. Keep records that are currently withdrawn and whose current categories include cs.LG, including cross-listed records.
>
> Include every direct successor named in the source record’s current notice as a replacement, an updated or corrected version, or the result of a merger. Also include mistaken separate submissions that redirect readers to another record. Exclude merely related work, independently developed equivalent results, and forthcoming work that the notice does not name. Successors can be from any year or category.
>
> For each source record, use its last listed submission timestamp as the cutoff. This is a rule for reconstructing the bibliography; it does not claim when the withdrawal happened. If that timestamp is after 9 September 2026 UTC, stop and report version drift.
>
> For each direct successor, select the version with the latest submission timestamp at or before the cutoff. Keep all versions tied at that timestamp. If no version meets the cutoff, omit that relationship. Report the title of each selected version, whether or not it differs from the successor’s current title.
>
> To carry out the search, first establish the complete annual category inventory. Check each source’s withdrawal status and current notice, follow its named successor, and compare the two submission histories. Then retrieve the title for the selected successor version. For mergers, follow the named successor rather than another contributing record.

输出要求单独放置，保留现有定义：

> Return only a pipe-separated table with header source_id|source_last_submission_utc|target_id|target_version|target_submission_utc|target_title. Use unversioned record identifiers, an integer version number, UTC timestamps as YYYY-MM-DDTHH:MM:SSZ, and the selected version's title, preserving its wording. Use one row per source, direct successor and selected version; sort by those three fields.

GO也应先写目标，再写全部资格与时间规则；操作指导的取舍须按原配对定义逐项核对。不能为读起来简短而删掉并列版本、无合格版本、来源漂移等会影响答案的条件。

## 3. wqp_activity_panel_001/r03：先解释比较的含义

“globally non-dominated continuous-period/station-cohort designs”适合技术定义，不适合直接作为读者的第一句话。开头可改为：

> I want to check whether removing one sampling activity changes which time periods and station groups we would use to compare seasonal low oxygen in the Trinity River. Test each eligible activity separately, restoring the original data before the next test.
>
> Compare designs by the number of consecutive years and the number of stations they include. Keep a design unless another covers at least as many years and stations, and more of at least one. For each removal that changes the set of retained designs, report the resulting designs and their lowest-oxygen observations in the removed activity’s calendar quarter.

这只是开头示例。后文仍需定义完整站点组、可行区间、活动资格和季度参照的跨年范围，并保留原有地理范围、结果质量、单位换算、独立移除、并列处理及18列输出。把这些条件按用途分段，比删掉条件更可靠。“最低氧观测”最后须落实到同一个活动及其伴随测量，不能把不同活动的字段拼起来。

## 使用方式

今后的题面先检查三件事：读完开头能否说出要查什么；每个条件是否放在容易找到的位置；普通表达是否仍精确保留原含义。遵循[配对题面提示词](../prompts/07_pair_writer.md)，不要将上述草稿直接覆盖正式导出。当前收录状态、评分和停止状态保持原记录。
