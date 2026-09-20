# 七道开发A满分候选：有界复核报告

本次选择 **0题** 进入改造方案：**6题淘汰本次改造方向，1题暂存**。没有新盲测、攻击、正式复测、完整答案扩展或公开取证。淘汰的是当前改造方向，不是整个网站。原七题两面满分版本继续停止重复抽样。

## 核对与总表

依据正式论文 `main.tex:142` 实际引用的 `sections/3_Method.tex` 和两份最新效率复盘。清单、当前版本与14份实际评分/模型核验均已逐项核对；两面均为gpt-5.6-sol/medium。表内分数是“正确字段/参考字段”，不是正式收录均值。详见 [inventory.json](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/full_score_review/inventory.json:1) 和 [preservation_check.json](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/full_score_review/preservation_check.json:1)。

按“已有新证据与缺口是否具体→自然研究意义→范围/身份可核实程度→剩余修订及成本”作机会优先序；这不是难度或成功率排名，未达继续条件者不会因排名靠前获选。

|序|候选/版本|CG；GO开发A|满分原因|唯一新机会或无依据结论|可复用材料|预计改造成本|实质修订已用/剩余|决定及逐题证据|
|---|---|---|---|---|---|---|---|---|---|
|1|IANA DTLS / r03|24/24；24/24|注册表给4项身份，发现RFC/draft后读取状态；短路径直接字段|暂存：RFC9146明确53早期分配与54不兼容，但未指明对应历史revision|103条范围、数值/区间/xref解析、RFC字段、空结果修复|取证1–3请求、模型5–15分钟；参考20–45分钟，语义20–45分钟，均为未实测粗估；再加V|1 / 1|暂存；[registry_law.md](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/full_score_review/registry_law.md:13)|
|2|KEGG模块产物 / r01|6/6；6/6|links返回模块ID→取3模块→读REACTION并做小集合比较；依赖成立但容易|无新证据；generic EQUATION与模块产品边界已经纳入并解对|限流、flat-field、模块完整范围、反应/产品解析及稳定性记录|无具体新条件，取证/改参考/语义成本未知；同范围重取约2–3请求，非改造估价；再加V|0 / 2|淘汰本次方向；[kegg.md](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/full_score_review/kegg.md:37)|
|3|KEGG前药身份 / r01|4/4；4/4|CG取DG全成员及4个D；GO从搜索和D页面取得4字段，但未完成完整DG核验|无新证据；盐型、自身COMMENT与组关系边界已在旧题|限流、续行解析、成员/目标身份、纳排及pre/post范围比较|新条件未定义，新增取证/参考/语义未知；同范围重取2–5请求，非改造估价；再加V|0 / 2|淘汰本次方向；[kegg.md](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/full_score_review/kegg.md:15)|
|4|最高法院加入关系 / r01|9/9；9/9|term/date发现3案→PDF署名组→含作者的小集合计数，领域判断正确|无新自然状态条件；不因发现后材料是静态PDF就否定依赖|58条term范围、docket身份、PDF锚点、已见署名语法|没有具体新原件，新增取证/参考/语义未知；旧构造740.5秒仅供规模参考；再加V|0 / 2|淘汰本次方向；[registry_law.md](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/full_score_review/registry_law.md:55)|
|5|EPMC定量结论 / r02|7/7；7/7|实际Sol主要走PubMed/Springer通知和原文，所有人群语义均解对；非reference的EPMC API路线|无新证据；人群、分母和更正边界已经覆盖|年度/期索引、DOI/PMCID、XML、完整纳排/稳定性及字段定义|无可执行新方向，成本未知；组报告同规模粗估取证10–25、参考15–35、语义15–30模型分钟，不是预留或承诺；再加V|1 / 1|淘汰本次方向；[papers.md](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/full_score_review/papers.md:9)|
|6|优化保证范围 / r02|18/18；18/18|survey引用→三作身份/history→正文定理；两个解均正确处理随机量和下标|回到适用性会重现r01声明/证明不一致；无新勘误消解，引用链不自动证明严格SGR|完整bullet、引用去重、history、query/gap提取、冲突和旧版本记录|新勘误/唯一性未闭合，成本未知；同规模粗估取证15–30、参考20–45、语义30–60模型分钟；再加V|1 / 1|淘汰本次方向；[papers.md](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/full_score_review/papers.md:108)|
|7|arXiv假设范围 / r03|12/12；12/12|官方history→三版本→定义/勘误，每面5次exec即可完成；版本依赖可保留|暂无依据；同版反例/引用不是新机会，且两次修订已用尽|history、三版原件、版本/时间解析、矩阵秩和勘误优先级|本协议下第三次实质改造不可启动，当前新增执行0；不能换ID再预留|2 / 0|淘汰本次方向；[papers.md](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/full_score_review/papers.md:57)|

**V：完整新版本后续验证**，若各前置阶段允许继续，须重新做开发A2、开发B2、攻击2、独立最终审计1、正式复测6，共13个模型会话；取证、参考及配对改造另至少1个Astra/high会话，必要的人类审核另计。旧满分A不能抵扣。累计模型时长与并行经过时间不同；正式/攻击成本尚未实测，完整时长、token和费用未知。本次V全部未执行，不能据此承诺节省或双70%结果。表中粗估仅保留复核者同规模工作参照，不构成未经估算的总预算，也不授权重开。

## 机制、完整性和难度分别判断

- KEGG模块题有结果驱动的模块请求；前药CG也有成员发现后的请求。两面满分表明已测版本容易，不能把这种batch本身当作SGR反例。
- 前药GO正确拿到4个输出字段，但未充分核实完整DG范围；EPMC实际主要靠出版社/PubMed作答，不能把构造侧完整API路线当成Sol已完成的路线。两者均不据此推翻原构造参考，也不将未取得完整范围伪称已验证的全覆盖固定材料。
- arXiv假设题确有旧版本证据不可由最新版本简单替代。优化题和法院题虽有发现身份后的检索，但严格网站状态必要性不能仅由引用/PDF遍历推出；本次保留待证范围，不以静态文件本身判死。
- 原参考的已有重算/范围检查有支持，但本次不是最终独立收录审计或人审。未发现新错误不等于已证明最终合格。

## 为什么不提交改造方案

没有候选同时具备可用新原件、必要状态变化、完整且唯一的范围及可控改造成本。因此本次入选0题，不写缺乏依据的题面草稿，也不生成新答案。

唯一暂存项是IANA：RFC9146第10.2节确实说明早期53与最终54不兼容，但仅称“previous version”，不能猜定具体历史revision。最小重开证据是一份官方历史Internet-Draft或官方分配事件，明确把53对应到具体版本及定义。拿到后仍须核对其状态依赖是否必要、版本关系是否唯一、最终固定文档是否已直接覆盖新问题。当前未联网补此原件，不将这项假设当成已成立方案。其研究意义是避免实现者把最终分配语义套到旧分配；现有“53已废弃”的简单字段不够支持实质改造。

需重核的内容不能直接复用：任何改变后的纳排、身份/版本范围、关系归属及答案；现场数据还需实际评估期稳定性。构造缓存与旧答案只留构造侧。IANA private `candidate.json`空结果文字尚残留header+NONE，而公共r03及reference已修复；不影响当前四行满分，未来复用须同步。本次按要求保留原件，未静默修补。

## 关键证据与轨迹

各行链接进入相应逐题报告，含CG/GO原始tool_events/events行号、关键原件及参考程序定位。所有引用均来自实际材料，来源未知仍标未知。程序汇总的完整逐题字段与排序见 [report.json](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/full_score_review/report.json:1)。IANA历史缺口的直接原文已由总控抽查：`candidates/iana_dtls_001/sources/rfc9146.txt:573–580`。

## 实际成本与其他工作

截至2026-09-12T17:51:06.361969+00:00，本次3个Astra/high复核工作会话已结束，实际分别耗时review_registry_law 434.2秒、review_papers 599.0秒、review_kegg 406.9秒，均低于1200秒。自用户提出复核起实际经过974.9秒；三工作会话时长之和1440.0秒，不能当作实际经过时间。并发峰值为总控+3=4。

已知token（3复核会话加总控自本次请求后的已记录增量）：输入10,007,149，其中缓存输入9,570,816；输出59,832。缓存是输入的子集。总控最后保存/校验的未回传尾部仍未知，费用未知；不能从输入token换算周额度。实际工具调用分项、起止时刻和原始trace见[costs.json](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/full_score_review/costs.json:1)，模型/effort原始turn_context核验见[model_verification.json](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/full_score_review/model_verification.json:1)。论文组一次报告写入语法失败也保留并计入。新增公开请求0、新测试0、额度重置0。

其他工作：奎宁结构的初步完整范围和格式检查已保存，但完整构造第一次因两次websocket超时而结束（2122.114秒、无完整产物、usage未回传），不是完成底题。唯一替代尝试尚未启动，现暂缓。没有其他本项目构造/测试进程；环境中可见的sleep/编译容器不是本轮模型会话。原五题目标仍为0/5，不能标记完成。

本次复核完成后停止。后续重开、改造或测试不自动执行。
