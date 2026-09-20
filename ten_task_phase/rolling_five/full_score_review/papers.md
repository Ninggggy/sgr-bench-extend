# Papers组三题复核

结论：三题均淘汰本次改造方向，推荐继续0题。保留原件、原题与高分；未联网、未启动盲测/验证。淘汰仅针对本次改造方向，不删除来源材料。

正式入口为 `chinese_1st_ver/latex/main.tex:142` 实际引用的 `sections/3_Method.tex`：8–12行任务定义，42–47行六要求，55–63行筛选与验证。`writing/main.tex`的对应input已注释，不作为规范。效率依据见papers.json的standards。六要求分开判断：三题均有领域语义与专门原件；唯一性/稳定性只在各自既定范围与语义下获得支持；抗捷径、SGR机制和对Sol的诊断价值不由完整oracle替代。最终独立审计和人审未完成。

以下文件定位以仓库根目录为基准；sessions是物理行号，保留call ID及返回原文行号。分数为已核验Sol/medium development A，不是正式均值。

## epmc_quantitative_001/r02

累计实质修订1次，剩1次。

1. **实际满分路径。** CG和GO均7/7字段、1/1行；P.O.A.=0源于无可比较行对，不是排序失败。

CG：PubMed搜索发现两通知；点击PubMed的出版社/原文链接，一次返回同时提供更正271/491及原文730/581、baseline SCID-5和问卷返回条件；后续补PMCID。EUtils/EPMC定向访问失败，未走reference的完整年度API→XML路线。

GO：搜索发现两通知，Springer两更正正文排除作者名更正，Springer原文和PubMed补全部字段，最后打开Springer期目录核查两通知。

cause：help/admission、non-depressed/outpatient、initial/analyzed和baseline/prospective均有直接原文解释，两个实际解均处理正确。

机制：reference有年度索引返回期成员与PMCID→结果驱动fullTextXML→正文独有总体/纳入条件的依赖。24篇batch依然以前步PMCID为请求参数，不能判其自动消除依赖。但实际Sol答案承载证据主要在Springer/PubMed，已出现不依赖目标Europe PMC状态的答案路径；不能以reference路线代替实际Sol路线，亦不能因EPMC访问失败推断来源不存在。不追加第二层依赖。

完整性：pre_A_rebuild记载360年度、47期记录、24 PMCID、2通知、1输出，纳排和一致性检查通过，post_A保留完整范围比较。Sol的Springer目录只支持其列出两通知，不独立证明与EPMC47身份全等；既定7字段满分不等于独立证明索引全集。人审/独立最终审计未完成。

难度：原有自然语义边界真实，但已两面全部解决。增加分母、百分比或更正前后数值只加读表/计算，暂无新证据支持诊断性SGR。

2. **新证据机会。** 暂无值得改造依据。最近自然需求“更正数字属于哪一人群”已由现题覆盖；没有已见新原件、新版本或必需字段解除跨站易解结论。 作者名更正与help/admission为现存边界，不能重复算新证据。 没有新“证据→状态操作→必要信息”链，故没有联网探第二方向。

3. **复用与重核。** 可复用：年度/期索引原始响应、两通知/原文XML、DOI/PMCID连接和通用XML解析；reference.py的完整纳排、全范围稳定性比较和现有安全检查；7字段定义、原始高分、现有来源/边界证据。需重核：改题后必须重核纳入谓词、每条通知正文、身份范围、人群/分母语义及受影响oracle，不能移植一行旧gold；现场索引变化须重核完整答案相关范围及评估期稳定性；不要求永久公开HTTP重放。

4. **成本区间（只估不跑）。** 当前新增执行为0。下列是同规模材料未来获授权的工作量参照，不是继续建议或成功率保证。

| 阶段 | 模型累计分钟 | 程序/操作分钟 |
|---|---:|---:|
| 新增最小取证 | 10–25 | 2–8 |
| 参考调整 | 15–35 | 2–10 |
| 语义检查 | 15–30 | 2–8 |
| 完整未来验证 | 75–180 | 5–20 |

完整验证为A2+B2+攻击2+独立最终审计1+正式6，共13模型会话；取证/参考/配对改造另至少1个Astra/high。若A双满分在2次停止，旧A不抵扣新A。新取证估0–4次合法原件请求，当前实际0；tokens/账户额度未知。

5. **决定：淘汰本次改造方向。** 双满分且实际跨站答案路径成立；现有边界已解决，没有新证据值得用最后一次实质修订。保留材料和全部高分，不靠加行/条件抽低分。 本次不暂存。以后若获授权且出现不同必要状态证据的新原件，仍按原ID累计修订再判断。

关键证据：
- `construction_pipeline/ten_task_phase/rolling_five/candidates/epmc_quantitative_001/r02/development_decision.json:7–102`
- `construction_pipeline/ten_task_phase/rolling_five/candidates/epmc_quantitative_001/r02/design_rationale.md:9–23`
- `construction_pipeline/ten_task_phase/rolling_five/candidates/epmc_quantitative_001/r02/revision_notes.md:5–19`
- `construction_pipeline/ten_task_phase/rolling_five/candidates/epmc_quantitative_001/r02/reference.py:155–237`
- `construction_pipeline/ten_task_phase/rolling_five/candidates/epmc_quantitative_001/r02/pre_A_rebuild/execution_report.json:2–21`
- `construction_pipeline/ten_task_phase/rolling_five/runs/epmc-r02-cg-dev-a/sessions/rollout-2026-09-12T06-11-22-01a0943d-f22f-7fd0-b875-1801c044ef8e.jsonl:57–60, call_RG1yx8GSC5FRlZPqOYPEezee, source L57–65/L98–102`
- `construction_pipeline/ten_task_phase/rolling_five/runs/epmc-r02-cg-dev-a/sessions/rollout-2026-09-12T06-11-22-01a0943d-f22f-7fd0-b875-1801c044ef8e.jsonl:22–25 and 87–90, explicit non-retryable access failures`
- `construction_pipeline/ten_task_phase/rolling_five/runs/epmc-r02-go-dev-a/sessions/rollout-2026-09-12T06-11-23-01a0943d-f6b0-70d1-a7cd-bbe2bf0174f5.jsonl:66–76, calls call_4AXsKn8u2MjQ7JgXdF0t7fbr and call_NUCclCyHEBVNFY6BF7EXy6BP`
- `construction_pipeline/ten_task_phase/rolling_five/runs/epmc-r02-go-dev-a/sessions/rollout-2026-09-12T06-11-23-01a0943d-f6b0-70d1-a7cd-bbe2bf0174f5.jsonl:91–94, call_ijI0kHFTcTxAVdm5O34g4bU7, issue source L469–483`
- `construction_pipeline/ten_task_phase/rolling_five/runs/epmc-r02-cg-dev-a/events.jsonl:30`
- `construction_pipeline/ten_task_phase/rolling_five/runs/epmc-r02-go-dev-a/events.jsonl:25`

## arxiv_assumption_scope_001/r03

累计实质修订2次，剩0次。

1. **实际满分路径。** 两面均12/12字段、3/3行、P.O.A.=1。

CG：题名/作者搜索确定1705.08366；官方history列v1/v2/v3；批量打开三版HTML/PDF；find定义、main result、erratum，最后读取v3更正和v1定义。

GO：history→三版HTML→find→v3更正；每面5次exec。ANY_T/rank t与MATCHED_T/rank 2t直接写在定义，Definition 11包含基本条件，corrected Theorem 8明确2-very general position。

cause：版本内精确提取和勘误优先级即可作答，不要求验证证明。

机制：官方history揭示版本全集→切换版本内容→取得当前默认v3不能代替的v1定义和各版本局部勘误，是有条件成立的狭窄版本状态依赖；批量三版不消除history前步。v3内Definition 11→更正定理本身为文内阅读，不另算网站状态。机制有条件成立不等于难度合格。

完整性：history完整三版，reference.py 101–127校验版本/时间和注释全集；143–180解析矩阵、秩、主定理与同版更正。rebuilt/preblind_checks明确已执行通过。只支持作者声明的唯一转录，不验证几何定义或证明；独立最终审计/人审未完成。

难度：版本差异和强条件包含弱条件是真边界，但两面近直接全对。跨论文反例、增加量词或删提示均无当前依据，而且两次实质修订已用尽。

2. **新证据机会。** 暂无值得改造依据。r03是第二且最后实质修订。v3 Example 12的反例引用至多是普通引用线索，不授权第三次改造，也不证明新SGR。 v1与v2/v3开头reduced词语差异已在r03修复；不能推断v1允许non-reduced或几何等价。 没有新“证据→状态操作→必要信息”链，故没有联网探第二方向。

3. **复用与重核。** 可复用：官方history、三版原PDF/文本、v3HTML、版本时间与身份解析；矩阵/秩/勘误优先级证据及CG/GO语义检查；r01/r02/r03修订历史、原失败、两面满分。需重核：后来版本或新研究需求均须重核版本全集和定义/定理/勘误作用域，不移植旧三行答案；本协议禁止第三次实质修订，不得改ID重置额度。

4. **成本区间（只估不跑）。** 当前新增执行为0。下列是同规模材料未来获授权的工作量参照，不是继续建议或成功率保证。

| 阶段 | 模型累计分钟 | 程序/操作分钟 |
|---|---:|---:|
| 新增最小取证 | 10–20 | 2–8 |
| 参考调整 | 10–25 | 2–10 |
| 语义检查 | 15–30 | 2–8 |
| 完整未来验证 | 60–150 | 5–20 |

完整验证为A2+B2+攻击2+独立最终审计1+正式6，共13模型会话；取证/参考/配对改造另至少1个Astra/high。若A双满分在2次停止，旧A不抵扣新A。新取证估0–4次合法原件请求，当前实际0；tokens/账户额度未知。本题修订余量0，不能启动第三次实质修订及相应验证。

5. **决定：淘汰本次改造方向。** 两次修订额度明确耗尽，两面各5次exec满分，无新的实际错误或来源机会。 本轮不重开；用户明确改变修订政策也仅解除程序限制，不自动提供内容或难度依据。

关键证据：
- `construction_pipeline/ten_task_phase/rolling_five/candidates/arxiv_assumption_scope_001/r02/revision_notes.md:1–9`
- `construction_pipeline/ten_task_phase/rolling_five/candidates/arxiv_assumption_scope_001/r03/revision_notes.md:1–9`
- `construction_pipeline/ten_task_phase/rolling_five/candidates/arxiv_assumption_scope_001/r03/repair_review.json:4–18`
- `construction_pipeline/ten_task_phase/rolling_five/candidates/arxiv_assumption_scope_001/r03/reference.py:101–180`
- `construction_pipeline/ten_task_phase/rolling_five/candidates/arxiv_assumption_scope_001/r03/rebuilt/preblind_checks.json:475–485`
- `construction_pipeline/ten_task_phase/rolling_five/candidates/arxiv_assumption_scope_001/sources/v1.txt:162–163`
- `construction_pipeline/ten_task_phase/rolling_five/candidates/arxiv_assumption_scope_001/sources/v2.txt:186–187`
- `construction_pipeline/ten_task_phase/rolling_five/candidates/arxiv_assumption_scope_001/sources/v3.txt:428 and 486–487`
- `construction_pipeline/ten_task_phase/rolling_five/runs/arxiv-r03-cg-dev-a/sessions/rollout-2026-09-12T06-18-22-01a09444-5a46-7052-be0f-c737b3602c44.jsonl:22–32, calls call_AnonGlxGYA1lKJNp0Lx8BLlv and call_WUXGAFv4OTyxqkT0OapNsMS6, history source L28–30`
- `construction_pipeline/ten_task_phase/rolling_five/runs/arxiv-r03-cg-dev-a/sessions/rollout-2026-09-12T06-18-22-01a09444-5a46-7052-be0f-c737b3602c44.jsonl:36–46, find and original follow-up`
- `construction_pipeline/ten_task_phase/rolling_five/runs/arxiv-r03-go-dev-a/sessions/rollout-2026-09-12T06-18-33-01a09444-82fd-70b2-846d-478baec88146.jsonl:22–32, history→three HTML versions`
- `construction_pipeline/ten_task_phase/rolling_five/runs/arxiv-r03-go-dev-a/sessions/rollout-2026-09-12T06-18-33-01a09444-82fd-70b2-846d-478baec88146.jsonl:45–48, call_xF38FF1WQqqH6xeoRVdZ0sQy, source L295–297/L331–334`
- `construction_pipeline/ten_task_phase/rolling_five/runs/arxiv-r03-cg-dev-a/events.jsonl:14`
- `construction_pipeline/ten_task_phase/rolling_five/runs/arxiv-r03-go-dev-a/events.jsonl:14`

## optimization_guarantee_001/r02

累计实质修订1次，剩1次。

1. **实际满分路径。** 两面均18/18字段、3/3行、P.O.A.=1。

CG：从搜索所得UC Davis托管survey PDF读完整ZO-SCG bullet和bibliography，按题名检索三作并合并[41]/[44]；读official history和所选HTML，查询式、gap定义与Theorem 2.1(1)/4.8/3.6提供全部字段。16次exec。

GO：survey bullet/refs→题名搜索/三官方history→三版HTML，定点读gap式和定理，再以1809v1标题核对合并、survey history核对截止。12次exec。

cause：r02限定主声明并排除证明有效性，已知冲突不再改变纳排。随机方向≠sample noise、minimum/expectation、gap下标位移均两面正确。

机制：存在bullet引用标题→原作身份/history→原文query/gap的普通检索依赖，但不自动满足严格SGR。实际截止版本v2/v2/v3均等于观测时当前最新版，截止过滤未见选择非默认答案承载版本。1809v1切换用于旧标题合并身份，是真实状态证据；其存在仍不能自动把整条以当前静态正文为主的综合路径判严格SGR必要性已确立。无需新增第二层分支；这里只保守拒绝由普通citation链推出严格合格。

完整性：完整bullet有4引用，题名/作者/共同arXiv身份合为3作；reference解析版本、query和gap域并保留执行通过。source_manifest为选段及明确UNFETCHED间隙，不宣称全PDF逐行审计或会议稿与预印本等同。r01适用性不唯一仍成立；r02是主声明转录，不是数学保证认证。独立最终审计/人审未完成。

难度：定理选择、重复身份和期望/最小值边界真实但已双满分。恢复算法适用性会重现r01不唯一，而非得到合法困难。

2. **新证据机会。** 暂无值得改造依据。唯一相邻自然需求是核对声明与算法/证明的实际适用关系，但现存冲突正是r01已知停因，不是新证据。没有新作者勘误或权威原件消解它。 1810.03233v3主定理A4–A6与Lemma E.1的A3–A6冲突，A3包含convex；算法与证明参数日程亦不一致。不能自选typo修复以制造唯一oracle。 没有新“证据→状态操作→必要信息”链，故没有联网探第二方向。

3. **复用与重核。** 可复用：survey完整bullet/bibliography、三作及1809v1题名身份、official history；citation_universe/resolve/history选择、query/gap域提取器、公开主声明范围；r01 stop及冲突原件、r02选段/执行记录与原高分。需重核：若未来有勘误，需重核声明、假设、算法日程、证明范围及问题定义；旧r02转录答案不成为适用性答案；新SGR主张须指出前步证据→目标站状态操作→必要信息；不能加率/排名/行数/引用层数替代。

4. **成本区间（只估不跑）。** 当前新增执行为0。下列是同规模材料未来获授权的工作量参照，不是继续建议或成功率保证。

| 阶段 | 模型累计分钟 | 程序/操作分钟 |
|---|---:|---:|
| 新增最小取证 | 15–30 | 2–8 |
| 参考调整 | 20–45 | 2–10 |
| 语义检查 | 30–60 | 2–8 |
| 完整未来验证 | 90–240 | 5–20 |

完整验证为A2+B2+攻击2+独立最终审计1+正式6，共13模型会话；取证/参考/配对改造另至少1个Astra/high。若A双满分在2次停止，旧A不抵扣新A。新取证估0–4次合法原件请求，当前实际0；tokens/账户额度未知。

5. **决定：淘汰本次改造方向。** 主声明方向双满分；邻近适用性仍有旧不唯一性且无新原件，严格SGR也不能只凭citation链推定。并非仅缺一个可补字段的暂存情形，不值得最后一次修订。 不把未知勘误当存在；未来原件即使解开旧冲突，仍需另证自然需求与必要状态依赖，修订累计不重置。

关键证据：
- `construction_pipeline/ten_task_phase/rolling_five/candidates/optimization_guarantee_001/revision_history.json:1–13`
- `construction_pipeline/ten_task_phase/rolling_five/candidates/optimization_guarantee_001/r01/stop.json:10–16`
- `construction_pipeline/ten_task_phase/rolling_five/candidates/optimization_guarantee_001/r02/design_rationale.md:1–11`
- `construction_pipeline/ten_task_phase/rolling_five/candidates/optimization_guarantee_001/r02/reference_report.md:3–17`
- `construction_pipeline/ten_task_phase/rolling_five/candidates/optimization_guarantee_001/r02/source_manifest.json:6–16`
- `construction_pipeline/ten_task_phase/rolling_five/candidates/optimization_guarantee_001/r02/reference.py:104–152,176–245,284–304`
- `construction_pipeline/ten_task_phase/rolling_five/candidates/optimization_guarantee_001/sources/1810.03233v3.excerpt.txt:266 and 657`
- `construction_pipeline/ten_task_phase/rolling_five/candidates/optimization_guarantee_001/sources/1810.03233v3.additional.excerpt.txt:3`
- `construction_pipeline/ten_task_phase/rolling_five/runs/optimization-claim-r02-cg-dev-a/sessions/rollout-2026-09-12T15-37-22-01a09644-2252-7dd1-987d-825d3e16b37d.jsonl:24–38, survey PDF and bibliography source L1032–1048`
- `construction_pipeline/ten_task_phase/rolling_five/runs/optimization-claim-r02-cg-dev-a/sessions/rollout-2026-09-12T15-37-22-01a09644-2252-7dd1-987d-825d3e16b37d.jsonl:101–104, call_UkYOeNbuUpb9xbRu0Q5oTEu7, Theorem3.6 source L373–377`
- `construction_pipeline/ten_task_phase/rolling_five/runs/optimization-claim-r02-go-dev-a/sessions/rollout-2026-09-12T15-37-23-01a09644-23e8-7ea3-a636-58117a54d20a.jsonl:45–57, call_pkgXaEBL0H7QkwxfdXTCJvL9 histories→call_A8qxXVbWyOC3BdnEawPpQcge HTMLs`
- `construction_pipeline/ten_task_phase/rolling_five/runs/optimization-claim-r02-go-dev-a/sessions/rollout-2026-09-12T15-37-23-01a09644-23e8-7ea3-a636-58117a54d20a.jsonl:61–78, gap and theorem originals`
- `construction_pipeline/ten_task_phase/rolling_five/runs/optimization-claim-r02-go-dev-a/sessions/rollout-2026-09-12T15-37-23-01a09644-23e8-7ea3-a636-58117a54d20a.jsonl:89–99, v1 title and survey cutoff`
- `construction_pipeline/ten_task_phase/rolling_five/runs/optimization-claim-r02-cg-dev-a/events.jsonl:36`
- `construction_pipeline/ten_task_phase/rolling_five/runs/optimization-claim-r02-go-dev-a/events.jsonl:29`

## 记账和限制

开始UTC：2026-09-12 17:36:26；结束/实际wall见JSON。工具总调用、tokens、缓存、周额度未知，未推算。仅查看本组6个实际求解会话相关片段；EPMC GO中间物理行32–41不能逐行JSON解析，未改原件且未用该段支持结论；决定性后续调用/输出及最终events均可直接定位。

没有继续候选，因此不附英文改题草稿或新完整参考答案。没有换年、扩行、堆条件、删提示、改ID或新增第二层/永久HTTP重放要求的建议。
