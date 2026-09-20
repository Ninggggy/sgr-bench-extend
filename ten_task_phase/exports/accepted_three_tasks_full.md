# 已收录三道底题：完整题面与参考答案

[完整中文阅读版](accepted_three_tasks_zh.md)

来源：同目录 constraint.jsonl、goal.jsonl。本文件逐字保留导出的 instruction、output_format 与 oracle_answer；中文导读只帮助阅读，不替代正式题面。每题 CG/GO 的参考答案相同，因此答案只展示一次。

## 1. 2021年 arXiv 撤回论文的替代文献历史标题变化

**底题：** `arxiv_historical_title_001/r02`  
**答案数据行数：** 8  
**起始网站：** https://arxiv.org/search/advanced

**中文导读：** 从2021年首次提交、属于 cs.LG 的论文中，找出撤回且明确指向直接替代文献的记录。按撤回版本的提交时刻选定替代文献当时的最新版本，仅保留该版本标题与当前标题措辞不同的关系。答案列出前驱编号、替代编号和版本。

### CG 题面（完整原文）

Using catalogue records as observed on 9 September 2026, audit historical title changes across direct replacement records for preprints first submitted during calendar year 2021 in UTC and classified as cs.LG, including cross-listed records. Find every predecessor whose latest recorded version is marked withdrawn and whose current comment explicitly identifies a distinct archive record as its direct replacement or continuation of the same work. Include notices of supersession, subsumption, merger into another record, revised resubmission, or correction of an accidentally duplicated record when they designate that other record. Exclude ordinary references, administrative text-overlap notices, incoming mergers, and active companion records unless the stated withdrawal and direct-replacement conditions are satisfied. Follow only the directly designated replacement, not a chain of later replacements. For each relationship, use the predecessor's latest version marked withdrawn as the withdrawal version. Select the replacement version whose recorded submission timestamp is the latest not later than that withdrawal version's recorded submission timestamp, comparing exact UTC timestamps. These are submission-record times, not public announcement or availability times. Include only relationships for which such a replacement version exists AND the title attached to that selected version differs in wording from the replacement record's current title. Ignore layout whitespace and equivalent mathematical rendering when comparing titles. Return the predecessor identifier, distinct replacement identifier and selected replacement version. To investigate, establish the complete year/category cohort, interpret replacement direction and actual withdrawal status, compare the two records' submission histories, then retrieve the selected version's metadata and compare its historical title with the current title before deciding whether to include the relationship.

### GO 题面（完整原文）

Using catalogue records as observed on 9 September 2026, audit historical title changes across direct replacement records for preprints first submitted during calendar year 2021 in UTC and classified as cs.LG, including cross-listed records. Find every predecessor whose latest recorded version is marked withdrawn and whose current comment explicitly identifies a distinct archive record as its direct replacement or continuation of the same work. Include notices of supersession, subsumption, merger into another record, revised resubmission, or correction of an accidentally duplicated record when they designate that other record. Exclude ordinary references, administrative text-overlap notices, incoming mergers, and active companion records unless the stated withdrawal and direct-replacement conditions are satisfied. Follow only the directly designated replacement, not a chain of later replacements. For each relationship, use the predecessor's latest version marked withdrawn as the withdrawal version. Select the replacement version whose recorded submission timestamp is the latest not later than that withdrawal version's recorded submission timestamp, comparing exact UTC timestamps. These are submission-record times, not public announcement or availability times. Include only relationships for which such a replacement version exists AND the title attached to that selected version differs in wording from the replacement record's current title. Ignore layout whitespace and equivalent mathematical rendering when comparing titles. Return the predecessor identifier, distinct replacement identifier and selected replacement version.

### 两版本共同的输出要求（完整原文）

Return only a pipe-separated table with header predecessor_id|replacement_id|selected_version. Use unversioned archive identifiers in the first two columns and v followed by the version number in the third. Use one row per qualifying direct relationship, sorted by predecessor_id then replacement_id.

### 参考答案（两版本共用，完整原文）

```text
predecessor_id|replacement_id|selected_version
2102.13653|1809.04564|v1
2103.00222|2011.10443|v1
2103.06490|1911.00234|v3
2104.13818|1908.06077|v1
2106.14997|2101.12365|v6
2107.01273|2011.09052|v1
2108.08647|2005.01026|v2
2111.03536|2103.07364|v1
```

## 2. Trinity River 水质观测的单活动撤除敏感性

**底题：** `wqp_activity_panel_001/r03`  
**答案数据行数：** 12  
**起始网站：** https://www.waterqualitydata.us/

**中文导读：** 使用2000—2019年指定范围的水质记录，建立同一采样活动的完整四指标观测、季度完整性、连续年份与站点集合的全局Pareto前沿。逐个独立撤除采样活动，找出前沿发生变化的情景，并为各情景的每个新前沿区间选出对应季度的最低溶解氧活动及其指标。

**收录说明：** 用户指定收录；原始审计与分数保留。

### CG 题面（完整原文）

I am auditing whether a common-observation-period comparison of seasonal low-oxygen events on the Trinity River depends on a single sampled activity. I need every individual activity withdrawal that changes the globally non-dominated continuous-period/station-cohort designs, and the surviving designs' lowest-oxygen reference events in the season of the withdrawn observation. These are independent hypothetical data-quality sensitivity trials; they do not assert that any official observation is wrong or has actually been withdrawn, and they are not causal or flow-adjusted trend estimates.

1. Enumerate the complete mainstem universe. Use the Water Quality Portal legacy WQX 2.2 records for organization USGS-TX, with ActivityStartDate from 2000-01-01 through 2019-12-31 inclusive. The finite station universe is all monitoring locations with any recorded data in this period in HUC8 12030101, 12030102, 12030103, 12030104, 12030105, 12030106, 12030107, 12030108, 12030109, 12030201, 12030202, 12030203. Retain locations whose MonitoringLocationName starts with "Trinity Rv " and whose MonitoringLocationTypeName is exactly "Stream" or "Stream: Tidal stream". The tidal mainstem is included; other named rivers, tributaries, reservoirs and wells are outside this study.

2. Resolve source activity identities and sampling conditions. An eligible activity must have ActivityMediaName exactly "Water" and ActivityTypeCode exactly "Sample-Routine". Exclude quality-control field replicates and all other activity types, including "Unknown". Identify activities by the combination of OrganizationIdentifier and ActivityIdentifier, and verify the MonitoringLocationIdentifier and ActivityStartDate agree when linking result and activity records. An activity is the recorded sampling unit, not an entire station visit: do not merge different activities merely because they share a station, date, time or depth. Preserve reported depth as metadata; blank depth is unknown and does not imply surface water. Use ActivityStartDate, not digits in ActivityIdentifier, to determine the calendar quarter.

3. Construct usable same-activity parameter panels. A complete activity must contain all four USGS parameter codes: 00010 (water temperature), 00095 (specific conductance at 25 degrees C), 00300 (dissolved-oxygen concentration), and 00400 (pH). Oxygen percent saturation, including code 00301, is not a substitute for code 00300. Use only finite numeric results marked Accepted or Final, with ResultValueTypeName "Actual", and with both ResultDetectionConditionText and MeasureQualifierCode blank. Discard results with missing or incompatible units. Normalize temperature to degrees C (degrees F: (F-32)*5/9), conductance to microSiemens/cm at 25 degrees C (microSiemens/cm and micromhos/cm are equivalent; milliSiemens/cm multiply by 1000), dissolved oxygen to mg/L (micrograms/L divide by 1000), and pH to standard units. Within each activity and parameter code, the usable results must yield exactly one distinct normalized numeric value; repeated identical values count once, but conflicting values make that activity incomplete. Do not choose an arbitrary first value or average conflicts.

4. Determine complete station-years. A station supports a calendar year only when it has at least one complete eligible activity in each of that year's four calendar quarters: January-March, April-June, July-September, October-December. Indicator presence somewhere in a year, four samples in one season, and period-of-record envelopes do not establish this condition. Years with a missing quarter remain gaps; do not fill them or bridge them.

5. Enumerate original common windows and full cohorts. Consider every inclusive contiguous calendar-year interval [start_year, end_year] within 2000–2019, including one-year intervals. For each interval its cohort is exactly ALL retained stations that support EVERY year in that interval. This is a fixed membership set over the whole interval, not a union of annually changing stations and not a chosen subset. An interval is feasible only if its cohort contains at least two stations, so there is a between-station comparison. Its duration is end_year-start_year+1 and its coverage is the number of stations in its cohort.

6. Compute the original global frontier. For any dataset state, define its duration-versus-station-coverage Pareto frontier as follows. Interval X dominates interval Y if X has at least as many years AND at least as many cohort stations as Y, with at least one of these two quantities strictly larger. Compare against ALL feasible intervals, including intervals at different dates or with different or overlapping cohorts. Retain an interval only if no feasible interval dominates it. Equal duration and coverage do not dominate one another: retain all such tied intervals when undominated. Do not choose one longest interval, apply a weighted score, require containment, or treat equal station counts as equal membership.

7. Withdraw each eligible activity independently and recompute the full design state. The unmodified data define the original eligible activities and the original frontier. Consider EVERY original complete eligible activity at EVERY retained mainstem station as a separate hypothetical withdrawal, including activities at stations outside the original frontier cohorts. A withdrawal removes that one OrganizationIdentifier/ActivityIdentifier and all its results. Keep the original station universe, geographic limits, date limits and all other records. Each trial starts again from the full original data; withdrawals are never cumulative. Recompute quarterly support, supported years, all interval cohorts and the GLOBAL frontier after the withdrawal. A trial is frontier-changing if its entire set of frontier designs differs from the original set. A design identity consists of start_year, end_year and the complete set of organization/station identities in its cohort. A mere change in a sample count or selected oxygen minimum without a frontier-design change does not qualify. Test activities whether or not they were an original selected minimum. Reconsider all intervals and retained stations: previously dominated designs may become frontier designs, and equal duration/coverage designs at different dates remain separate.

8. For each changing trial, return to its surviving intervals and select the correct seasonal event. For EACH frontier-changing withdrawal and EACH interval on that trial's recomputed frontier, define quarter as the QUARTER-OF-YEAR of the withdrawn activity's ActivityStartDate. Form the set of REMAINING complete eligible activities at ANY station in that post-withdrawal interval's own cohort, with dates inside that interval and in that quarter-of-year across its years. Count distinct organization/activity keys in that set. Select ONE activity across the entire cohort with the lowest unrounded dissolved-oxygen concentration. Break ties by earliest ActivityStartDate, then ActivityStartTime/Time in ascending local clock order (missing after known times), then MonitoringLocationIdentifier, then ActivityIdentifier, with identifiers ordered case-sensitively and lexicographically. Report that selected activity's own organization, station, activity ID, date, temperature, conductance and pH. Never reuse an event/count from another withdrawal, interval or the full original record. Round the four measurements only in final output, using decimal round-half-up to two decimal places.

9. Write all changing-trial/interval entities. Return one row per frontier-changing withdrawal and post-withdrawal frontier interval. The cohort_station_ids field lists that interval's entire post-withdrawal set of MonitoringLocationIdentifier values, sorted lexicographically and joined with semicolons; organization is USGS-TX throughout this bounded study. Sort rows by withdrawn_ActivityIdentifier lexicographically, then start_year ascending and end_year ascending. Preserve identifiers; report years and counts as integers, quarter as Q1/Q2/Q3/Q4, dates as YYYY-MM-DD, and measurements to two decimal places. If a changing withdrawal leaves no feasible interval, output one sentinel row for it: start_year=end_year=cohort_station_count=eligible_activity_count=0, cohort_station_ids=NONE, the withdrawn activity's quarter, selected identifiers/date=NONE and all four measurements=NA. If no withdrawal changes the frontier, output NONE. Failed or incomplete retrieval remains an unresolved limitation, not evidence of zero records.

### GO 题面（完整原文）

I am auditing whether a common-observation-period comparison of seasonal low-oxygen events on the Trinity River depends on a single sampled activity. I need every individual activity withdrawal that changes the globally non-dominated continuous-period/station-cohort designs, and the surviving designs' lowest-oxygen reference events in the season of the withdrawn observation. These are independent hypothetical data-quality sensitivity trials; they do not assert that any official observation is wrong or has actually been withdrawn, and they are not causal or flow-adjusted trend estimates.

The sensitivity audit must satisfy the following definitions and reporting requirements.

Use the Water Quality Portal legacy WQX 2.2 records for organization USGS-TX, with ActivityStartDate from 2000-01-01 through 2019-12-31 inclusive. The finite station universe is all monitoring locations with any recorded data in this period in HUC8 12030101, 12030102, 12030103, 12030104, 12030105, 12030106, 12030107, 12030108, 12030109, 12030201, 12030202, 12030203. Retain locations whose MonitoringLocationName starts with "Trinity Rv " and whose MonitoringLocationTypeName is exactly "Stream" or "Stream: Tidal stream". The tidal mainstem is included; other named rivers, tributaries, reservoirs and wells are outside this study.

An eligible activity must have ActivityMediaName exactly "Water" and ActivityTypeCode exactly "Sample-Routine". Exclude quality-control field replicates and all other activity types, including "Unknown". Identify activities by the combination of OrganizationIdentifier and ActivityIdentifier, and verify the MonitoringLocationIdentifier and ActivityStartDate agree when linking result and activity records. An activity is the recorded sampling unit, not an entire station visit: do not merge different activities merely because they share a station, date, time or depth. Preserve reported depth as metadata; blank depth is unknown and does not imply surface water. Use ActivityStartDate, not digits in ActivityIdentifier, to determine the calendar quarter.

A complete activity must contain all four USGS parameter codes: 00010 (water temperature), 00095 (specific conductance at 25 degrees C), 00300 (dissolved-oxygen concentration), and 00400 (pH). Oxygen percent saturation, including code 00301, is not a substitute for code 00300. Use only finite numeric results marked Accepted or Final, with ResultValueTypeName "Actual", and with both ResultDetectionConditionText and MeasureQualifierCode blank. Discard results with missing or incompatible units. Normalize temperature to degrees C (degrees F: (F-32)*5/9), conductance to microSiemens/cm at 25 degrees C (microSiemens/cm and micromhos/cm are equivalent; milliSiemens/cm multiply by 1000), dissolved oxygen to mg/L (micrograms/L divide by 1000), and pH to standard units. Within each activity and parameter code, the usable results must yield exactly one distinct normalized numeric value; repeated identical values count once, but conflicting values make that activity incomplete. Do not choose an arbitrary first value or average conflicts.

A station supports a calendar year only when it has at least one complete eligible activity in each of that year's four calendar quarters: January-March, April-June, July-September, October-December. Indicator presence somewhere in a year, four samples in one season, and period-of-record envelopes do not establish this condition. Years with a missing quarter remain gaps; do not fill them or bridge them.

Consider every inclusive contiguous calendar-year interval [start_year, end_year] within 2000–2019, including one-year intervals. For each interval its cohort is exactly ALL retained stations that support EVERY year in that interval. This is a fixed membership set over the whole interval, not a union of annually changing stations and not a chosen subset. An interval is feasible only if its cohort contains at least two stations, so there is a between-station comparison. Its duration is end_year-start_year+1 and its coverage is the number of stations in its cohort.

For any dataset state, define its duration-versus-station-coverage Pareto frontier as follows. Interval X dominates interval Y if X has at least as many years AND at least as many cohort stations as Y, with at least one of these two quantities strictly larger. Compare against ALL feasible intervals, including intervals at different dates or with different or overlapping cohorts. Retain an interval only if no feasible interval dominates it. Equal duration and coverage do not dominate one another: retain all such tied intervals when undominated. Do not choose one longest interval, apply a weighted score, require containment, or treat equal station counts as equal membership.

The unmodified data define the original eligible activities and the original frontier. Consider EVERY original complete eligible activity at EVERY retained mainstem station as a separate hypothetical withdrawal, including activities at stations outside the original frontier cohorts. A withdrawal removes that one OrganizationIdentifier/ActivityIdentifier and all its results. Keep the original station universe, geographic limits, date limits and all other records. Each trial starts again from the full original data; withdrawals are never cumulative. Recompute quarterly support, supported years, all interval cohorts and the GLOBAL frontier after the withdrawal. A trial is frontier-changing if its entire set of frontier designs differs from the original set. A design identity consists of start_year, end_year and the complete set of organization/station identities in its cohort. A mere change in a sample count or selected oxygen minimum without a frontier-design change does not qualify. Test activities whether or not they were an original selected minimum. Reconsider all intervals and retained stations: previously dominated designs may become frontier designs, and equal duration/coverage designs at different dates remain separate.

For EACH frontier-changing withdrawal and EACH interval on that trial's recomputed frontier, define quarter as the QUARTER-OF-YEAR of the withdrawn activity's ActivityStartDate. Form the set of REMAINING complete eligible activities at ANY station in that post-withdrawal interval's own cohort, with dates inside that interval and in that quarter-of-year across its years. Count distinct organization/activity keys in that set. Select ONE activity across the entire cohort with the lowest unrounded dissolved-oxygen concentration. Break ties by earliest ActivityStartDate, then ActivityStartTime/Time in ascending local clock order (missing after known times), then MonitoringLocationIdentifier, then ActivityIdentifier, with identifiers ordered case-sensitively and lexicographically. Report that selected activity's own organization, station, activity ID, date, temperature, conductance and pH. Never reuse an event/count from another withdrawal, interval or the full original record. Round the four measurements only in final output, using decimal round-half-up to two decimal places.

Return one row per frontier-changing withdrawal and post-withdrawal frontier interval. The cohort_station_ids field lists that interval's entire post-withdrawal set of MonitoringLocationIdentifier values, sorted lexicographically and joined with semicolons; organization is USGS-TX throughout this bounded study. Sort rows by withdrawn_ActivityIdentifier lexicographically, then start_year ascending and end_year ascending. Preserve identifiers; report years and counts as integers, quarter as Q1/Q2/Q3/Q4, dates as YYYY-MM-DD, and measurements to two decimal places. If a changing withdrawal leaves no feasible interval, output one sentinel row for it: start_year=end_year=cohort_station_count=eligible_activity_count=0, cohort_station_ids=NONE, the withdrawn activity's quarter, selected identifiers/date=NONE and all four measurements=NA. If no withdrawal changes the frontier, output NONE. Failed or incomplete retrieval remains an unresolved limitation, not evidence of zero records.

### 两版本共同的输出要求（完整原文）

Return data rows only, newline-separated and pipe-separated, in this exact column order: withdrawn_OrganizationIdentifier|withdrawn_ActivityIdentifier|withdrawn_MonitoringLocationIdentifier|withdrawn_ActivityStartDate|start_year|end_year|cohort_station_count|cohort_station_ids|quarter|eligible_activity_count|selected_OrganizationIdentifier|selected_MonitoringLocationIdentifier|selected_ActivityIdentifier|selected_ActivityStartDate|dissolved_oxygen_mg_L|temperature_deg_C|specific_conductance_uS_cm|pH. Apply all stated scenario identity, cohort membership, date/quarter, units, precision, sentinel and sorting rules. Output NONE only when there is no frontier-changing withdrawal.

### 参考答案（两版本共用，完整原文）

```text
USGS-TX|nwistx.01.01401065|USGS-08065350|2014-03-11|2013|2019|2|USGS-08057410;USGS-08067000|Q1|37|USGS-TX|USGS-08057410|nwistx.01.01601917|2016-03-09|8.40|16.30|400.00|7.70
USGS-TX|nwistx.01.01401065|USGS-08065350|2014-03-11|2014|2015|3|USGS-08057410;USGS-08067000;USGS-08067252|Q1|27|USGS-TX|USGS-08067252|nwistx.01.01501624|2015-03-20|8.90|15.80|359.00|7.40
USGS-TX|nwistx.01.01401515|USGS-08065350|2014-05-20|2013|2019|2|USGS-08057410;USGS-08067000|Q2|61|USGS-TX|USGS-08057410|nwistx.01.01503036|2015-06-10|5.00|27.40|346.00|7.40
USGS-TX|nwistx.01.01401515|USGS-08065350|2014-05-20|2014|2015|3|USGS-08057410;USGS-08067000;USGS-08067252|Q2|31|USGS-TX|USGS-08067252|nwistx.01.01502581|2015-05-30|4.30|25.30|276.00|7.10
USGS-TX|nwistx.01.01500574|USGS-08065350|2014-10-30|2013|2019|2|USGS-08057410;USGS-08067000|Q4|39|USGS-TX|USGS-08057410|nwistx.01.01900010|2018-10-10|5.70|22.30|295.00|7.70
USGS-TX|nwistx.01.01500574|USGS-08065350|2014-10-30|2014|2015|3|USGS-08057410;USGS-08067000;USGS-08067252|Q4|17|USGS-TX|USGS-08067252|nwistx.01.01500130|2014-10-15|5.50|26.20|387.00|7.60
USGS-TX|nwistx.01.01601150|USGS-08067000|2015-12-02|2002|2007|2|USGS-08057410;USGS-08065350|Q4|21|USGS-TX|USGS-08057410|nwistx.01.00300032|2002-10-08|6.50|24.20|535.00|7.40
USGS-TX|nwistx.01.01601150|USGS-08067000|2015-12-02|2014|2014|4|USGS-08057410;USGS-08065350;USGS-08067000;USGS-08067252|Q4|12|USGS-TX|USGS-08067252|nwistx.01.01500130|2014-10-15|5.50|26.20|387.00|7.60
USGS-TX|nwistx.01.01900498|USGS-08067000|2019-02-13|2002|2007|2|USGS-08057410;USGS-08065350|Q1|24|USGS-TX|USGS-08065350|nwistx.01.00200965|2002-03-27|8.10|15.00|328.00|7.80
USGS-TX|nwistx.01.01900498|USGS-08067000|2019-02-13|2013|2018|2|USGS-08057410;USGS-08067000|Q1|34|USGS-TX|USGS-08057410|nwistx.01.01601917|2016-03-09|8.40|16.30|400.00|7.70
USGS-TX|nwistx.01.01900498|USGS-08067000|2019-02-13|2014|2014|4|USGS-08057410;USGS-08065350;USGS-08067000;USGS-08067252|Q1|11|USGS-TX|USGS-08057410|nwistx.01.01401056|2014-03-06|9.50|14.40|838.00|7.30
USGS-TX|nwistx.01.01900498|USGS-08067000|2019-02-13|2014|2015|3|USGS-08057410;USGS-08067000;USGS-08067252|Q1|27|USGS-TX|USGS-08067252|nwistx.01.01501624|2015-03-20|8.90|15.80|359.00|7.40
```

## 3. 2020年 arXiv 撤回论文的历史替代文献目录

**底题：** `arxiv_historical_title_002/r03`  
**答案数据行数：** 21  
**起始网站：** https://arxiv.org/search/advanced

**中文导读：** 从2020年首次提交、当前属于 cs.LG 且已撤回的记录中，找出通知明确指定的直接后继文献。以源记录最后列出的提交时刻为截止，选定后继文献当时最新的版本，返回时间、版本和历史标题；本题不要求标题发生变化。

**收录说明：** 用户指定收录；原始审计与分数保留。

### CG 题面（完整原文）

Reconstruct a historical bibliography from catalogue records, using public metadata current through 9 September 2026. Consider every record first submitted during calendar 2020 (UTC) whose current categories include cs.LG, including crosslists, and whose current record is withdrawn. Include each direct successor that its current notice names as a replacement, updated or corrected version, or merger result; this includes mistaken separate submissions redirected to another record. A merely related work, an independently developed equivalent result, or an unnamed forthcoming work is not a direct named successor. For each source-to-successor relation, use the SOURCE RECORD'S LAST LISTED SUBMISSION TIMESTAMP as the cutoff, and select the successor version with the latest submission timestamp at or before it. This cutoff is a bibliographic convention, not an asserted withdrawal-event date. Use the title belonging to the selected successor version. Successors may be from any year or category. Include all qualifying relations and all versions tied at the latest eligible timestamp, without filtering for title changes. Omit a relation if no successor version was submitted by its cutoff. If a source's last listed submission is after 9 September 2026 UTC, stop and report version drift. The purpose is to identify the successor citations supported by this explicit historical cutoff. Start with the complete annual category inventory, inspect the current notices and withdrawal status, follow the named successor rather than any other merger contributor, and use source and successor submission histories to determine which version-specific title to retrieve.

### GO 题面（完整原文）

Reconstruct a historical bibliography from catalogue records, using public metadata current through 9 September 2026. Consider every record first submitted during calendar 2020 (UTC) whose current categories include cs.LG, including crosslists, and whose current record is withdrawn. Include each direct successor that its current notice names as a replacement, updated or corrected version, or merger result; this includes mistaken separate submissions redirected to another record. A merely related work, an independently developed equivalent result, or an unnamed forthcoming work is not a direct named successor. For each source-to-successor relation, use the SOURCE RECORD'S LAST LISTED SUBMISSION TIMESTAMP as the cutoff, and select the successor version with the latest submission timestamp at or before it. This cutoff is a bibliographic convention, not an asserted withdrawal-event date. Use the title belonging to the selected successor version. Successors may be from any year or category. Include all qualifying relations and all versions tied at the latest eligible timestamp, without filtering for title changes. Omit a relation if no successor version was submitted by its cutoff. If a source's last listed submission is after 9 September 2026 UTC, stop and report version drift. The purpose is to identify the successor citations supported by this explicit historical cutoff.

### 两版本共同的输出要求（完整原文）

Return only a pipe-separated table with header source_id|source_last_submission_utc|target_id|target_version|target_submission_utc|target_title. Use unversioned record identifiers, an integer version number, UTC timestamps as YYYY-MM-DDTHH:MM:SSZ, and the selected version's title, preserving its wording. Use one row per source, direct successor and selected version; sort by those three fields.

### 参考答案（两版本共用，完整原文）

```text
source_id|source_last_submission_utc|target_id|target_version|target_submission_utc|target_title
2001.01717|2022-09-21T21:23:23Z|1907.03532|3|2022-07-23T05:34:24Z|Classification of Macromolecule Type Based on Sequences of Amino Acids Using Deep Learning
2001.09328|2021-10-04T02:39:01Z|2009.02623|2|2020-10-17T13:54:54Z|Information Theoretic Counterfactual Learning from Missing-Not-At-Random Feedback
2001.09532|2021-09-10T12:33:44Z|2109.03866|1|2021-09-08T18:28:56Z|Learning the hypotheses space from data through a U-curve algorithm: a statistically consistent complexity regularizer for Model Selection
2001.11578|2021-09-10T12:34:05Z|2109.03866|1|2021-09-08T18:28:56Z|Learning the hypotheses space from data through a U-curve algorithm: a statistically consistent complexity regularizer for Model Selection
2003.03601|2021-05-31T15:30:41Z|2005.08948|2|2021-05-31T15:22:57Z|Achieving Online Regression Performance of LSTMs with Simple RNNs
2003.03657|2020-07-05T06:15:37Z|2006.14426|1|2020-06-25T14:04:55Z|Spatio-temporal Sequence Prediction with Point Processes and Self-organizing Decision Trees
2005.12741|2020-05-28T19:49:41Z|1807.11926|1|2018-07-31T17:15:11Z|What am I searching for?
2006.00784|2020-12-15T04:45:58Z|2012.07346|1|2020-12-14T08:56:04Z|Better scalability under potentially heavy-tailed feedback
2006.01364|2020-12-15T04:46:42Z|2012.07346|1|2020-12-14T08:56:04Z|Better scalability under potentially heavy-tailed feedback
2006.06799|2020-11-19T18:30:01Z|2011.09128|2|2020-11-19T08:29:31Z|Multigrid-in-Channels Neural Network Architectures
2006.13025|2020-07-01T20:44:03Z|2001.01796|4|2020-06-30T12:06:48Z|Fair Active Learning
2008.13265|2022-02-04T02:01:30Z|2010.11327|14|2022-01-13T06:27:17Z|Meta-Learning Guarantees for Online Receding Horizon Learning Control
2009.01395|2020-09-04T02:51:03Z|1912.05078|2|2020-01-07T06:44:41Z|An Improving Framework of regularization for Network Compression
2009.13051|2021-05-01T14:24:22Z|2009.14471|5|2021-02-25T22:08:03Z|PettingZoo: Gym for Multi-Agent Reinforcement Learning
2010.07532|2023-01-25T07:50:08Z|2010.01171|2|2023-01-25T07:46:34Z|Data-Driven Certification of Neural Networks with Random Input Noise
2010.11327|2022-11-01T02:20:14Z|2111.15041|3|2022-10-31T05:33:07Z|Online Learning for Predictive Control with Provable Regret Guarantees
2010.11869|2022-10-19T21:37:40Z|2104.08453|3|2022-10-19T21:31:34Z|R&R: Metric-guided Adversarial Sentence Generation
2011.03426|2022-08-09T18:24:58Z|2104.02017|2|2022-07-27T04:48:32Z|Efficient Personalized Speech Enhancement through Self-Supervised Learning
2011.08470|2022-05-04T10:06:15Z|2102.10955|1|2021-02-22T12:50:49Z|Learning Purified Feature Representations from Task-irrelevant Labels
2012.01380|2022-03-23T05:52:16Z|2201.07858|1|2022-01-19T20:52:42Z|Decoupling the Depth and Scope of Graph Neural Networks
2012.03115|2021-09-29T10:58:20Z|2108.09423|1|2021-08-21T02:47:59Z|Adaptive unsupervised learning with enhanced feature representation for intra-tumor partitioning and survival prediction for glioblastoma
```
