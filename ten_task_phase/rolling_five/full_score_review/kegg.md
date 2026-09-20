# KEGG 两题满分原因与改造价值复核

结论：两题均**淘汰本次改造方向**，保留 r01、原分数与来源资产；本次入选建议为 0。没有新原件支持值得投入的邻近改造，不把已用边界重新包装为新机会。此结论不是永久淘汰 KEGG，也不是声称两题严格 SGR 都不成立。

本次仅复核既有材料，没有联网、新参考执行、模型测试、攻击、正式复测或子代理。首个可观察 UTC 时钟为 2026-09-12 17:37:23（精确开始未知，首次文件读取略早）；结束时间见 kegg.json。新原件 actual_access：不适用。运行配置 2026-09-09 不充当来源截止日；两题实际题意均锚定 2026-09-12 观察记录。

## 共同判据与修订额度

[main.tex:142](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/chinese_1st_ver/latex/main.tex:142) 实际引用 sections/3_Method；writing/main.tex:140 对应引用被注释，未据其另立定义。正式 [3_Method.tex:8](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/chinese_1st_ver/latex/sections/3_Method.tex:8) 规定专门网站状态条件化的证据暴露；第42–47行六要求依次是领域性、长尾来源、唯一可核验、真值稳定、抗捷径、至少一项结果驱动后续检索/过滤/分支。第55–63行把初筛区分度和独立专家验证另列。

据两份项目复盘及全局经验，机制成立、参考完整、模型难度分开判断；不额外要求第二层、特殊回查或永久 HTTP 重放。发现的 ID 决定批量参数可以成立；普通引用遍历、后续本地 join 或排序本身不自动成立。实际完整固定材料反例应当否定相应依赖，未知 dump 不能作反例。资料入口：[economic_five_efficiency_review_2026-09-12.md](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/research/economic_five_efficiency_review_2026-09-12.md)、[construction_efficiency_review_2026-09-10.md](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/research/construction_efficiency_review_2026-09-10.md)、[benchmark-construction-efficiency.md](/Users/ning/.codex/skills/0-autoresearch-skill/references/benchmark-construction-efficiency.md)。这些作为审计资料读取，没有执行研究技能工作流。

[inventory.json](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/full_score_review/inventory.json) 确认两题均 r01、实质修订已用 0；[rolling_five_campaign.json:5](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five_campaign.json:5) 限制最多 2，故各剩 2。前药第一次 builder 的阶段输入失败不是候选内容修订。不能另起 ID 重置这一额度，也不能把满分版本的润色叫新实质机会。

## kegg_prodrug_identity_001 / r01

**1. 满分原因、机制与完整性。** [development_decision.json:7](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/candidates/kegg_prodrug_identity_001/r01/development_decision.json:7) 记录 CG/GO 均 4/4 字段，Item-F1=8/8，2行，全保留；没有 B、攻击、最终独立审计或正式均值。

CG 的路径有实际取证支持：[tool_events.jsonl:12](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/runs/kegg-prodrug-r01-cg-dev-a/tool_events.jsonl:12) 返回完整 DG00739 的四个 Member；第13–16行按四个发现的 D ID 下载并读取完整记录（调用 call_SIlRNqNXHNyI9yRXuvae5l4H、call_PPnp0FxPNGYhvHlsvRlP2E1D）；第17–18行再次完整读 DG。之后按 own COMMENT 的固定短语提取有序关系。它是**结果驱动成员检索后，简单领域身份核对**，不是纯本地 join，也没有证据说明它依赖全覆盖固定表。此基础 SGR 可成立，但对该次 Sol 很容易。

GO 要单列：[tool_events.jsonl:8](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/runs/kegg-prodrug-r01-go-dev-a/tool_events.jsonl:8) 的 D05094 搜索结果直接给盐型关系，并在 hsa:3615 搜索结果列出四个 D；第12行成功打开 D00752，页面 L24 给另一条关系，同时其他三个 D 打开返回403；第16行搜索片段给 D05095 的不同 COMMENT 和 D05096 身份。**四个输出字段确实均已暴露在公开检索结果/页面中**。[events.jsonl:27](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/runs/kegg-prodrug-r01-go-dev-a/events.jsonl:27) 最终明确以 hsa:3615 的 Drug target 展开代替 DG Member，且 limits 为空。然而必要 DG 请求始终失败（tool_events 第4、18、22行），没有完整 Member 原文；部分排除记录只有有年龄标签的搜索呈现，未核实题意要求的完整记录与观察时点。因此 GO 是**近直接公开字段路径取得正确答案，同时该次完整范围核验不足**。不能据输出满分说它完成了全部研究义务，也不能反过来推翻构造参考或 CG 已成立的依赖。

已实际读取的固定前药表 br08324 只直接覆盖普通 mofetil 对，不含 D05094/D05095 的条目注释，见 [evidence.md:8](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/runs/kegg-drug-mechanism-review-01/stage_assets/evidence.md:8)、[design_rationale.md:5](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/candidates/kegg_prodrug_identity_001/r01/design_rationale.md:5)。GO 的几个不同检索材料足以给四字段，却没有证明一份与发现结果无关的固定材料覆盖完整 Member 和所有纳排；不宣称全题固定材料反例成立。

构造侧原件是完整 [DG00739.txt:4](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/candidates/kegg_prodrug_identity_001/sources/DG00739.txt:4) 的四成员，[D_members.txt:60](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/candidates/kegg_prodrug_identity_001/sources/D_members.txt:60)、第185行两条 own COMMENT，第315行钠盐不同 COMMENT，第401–491行活性酸完整记录无该注释。[executionchecks.json:2](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/candidates/kegg_prodrug_identity_001/r01/rebuilt/executionchecks.json:2) 与 [controller_integration_check.json:2](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/candidates/kegg_prodrug_identity_001/r01/controller_integration_check.json:2) 证明原参考实际重建通过；pre/post_A 文件记录四成员与全部纳排/答案一致。早期 reference_report 的 pending 不应覆盖这些后续检查。未发现构造侧具体漏项，但独立终审和人工审核仍未执行，历史一致也不保证未来时点稳定。

**2. 自然邻近机会。** 本次 0 项。盐型独立身份、组级 Prodrugs 与自身 COMMENT 差异正是旧题已覆盖的真实边界，不能再算新增判断。GO 中出现其他药物 CPD 命名空间的搜索片段不证明当前组有新的必要证据，也不足以扩成第二方向。缺少能在同一自然目标下改变必要检索状态或领域判断的新原件，故不联网、不补完整 oracle、不拟追低分草稿。

**3. 可复用与重核。** 可复用受控访问画像、既有共享限流器、12列 flat-field/续行/终止符解析、D/DG/C 身份区分、直接成员范围、own COMMENT 归属与证据行索引。旧 oracle 仅属于当前条件和观察时点；改变日期、组、关系类型必须重核全集、条目身份、排除及目标。尤其 [reference.py:137](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/candidates/kegg_prodrug_identity_001/r01/reference.py:137) 要求加载 Drug 集合恰等于成员，第171行又要求目标在该集合；当前目标本就在组中所以可用，若未来实际发现组外 active target，不能把原解析器直接叫通用支持，需要区分成员档案和额外目标档案并补取目标原件，不能误排除。这是条件化重核提醒，不是已发现新机会。

**4. 成本。** 本次新增网络取证、参考修改、语义重构、后续验证均为0。若只复查现有范围，一轮是1个DG+1次四D batch（2请求、5记录；逐项取则5请求），首轮取得范围后才能请求成员；两个稳定性观察合计4–10请求。程序负责解析/覆盖/差异，模型只复核4个成员的归属和排除。历史 builder 用518.680秒、34,208输入/16,810输出；CG 75.425秒、326,538/1,596，GO 105.617秒、476,895/2,162。定位各 run.json 的 elapsed_seconds/usage；这些是历史观测，不是新任务预算保证。

没有定义值得做的新语义，因此新增取证量、reference改造时间、语义重核量的可靠未来范围均 unknown，不伪造数值。若以后出现真实新机会，完整新版本最低需要参考/配对改造至少1次 Astra/high，再加13个验证模型会话（A2+B2+攻击2+终审1+正式6）；取证与稳定性程序请求另计，旧A不得抵扣。仅以当前A外推12个求解/攻击会话为15.1–21.1会话分钟，是无验证的局部代理，不能作上界；终审、人工审核、费用、总wall和新题tokens均 unknown。

**5. 决定。** 淘汰本次改造方向，保留现有资产和两次满分。单一重开缺口：缺少**同一自然组内信息需求的新必要证据及其真实边界**；重开需给实际原件说明前步发现如何决定后步专门网站状态、必要信息为何不在现有固定材料内，并接受新版本完整验证。仅补GO完整性不构成新难度机会。

## kegg_module_products_001 / r01

**1. 满分原因、机制与完整性。** [development_decision.json:7](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/candidates/kegg_module_products_001/r01/development_decision.json:7) 记录两面6/6字段、Item-F1=12/12、2行。GO 的 [tool_events.jsonl:13](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/runs/kegg-module-products-r01-go-dev-a/tool_events.jsonl:13) 调用 call_R7V7QCIzmBR69NxE3LG2HYkM 下载 link/module/ec:4.1.1.39，第14行返回三个模块；第15–16行才下载这些模块及根酶，随后第17–20行取模块内容和 REACTION 尾段。**link返回身份→指定模块记录检索状态→模块特定产物证据**这一依赖实际成立。

CG 的 [tool_events.jsonl:10](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/runs/kegg-module-products-r01-cg-dev-a/tool_events.jsonl:10) 搜索已暴露模块/反应候选；第21–22行集中下载根酶、直接links与三个模块，第23–24行读三个 REACTION 区段。它没有等该次link返回才列模块URL，而利用此前搜索/页面已有的ID后校验完整links；不能倒推说CG也严格按GO顺序。无论哪条，最终区别来自各模块字段，未以 generic EQUATION 补产物。集合归组、去重与排序是简单本地计算，领域边界有题面明确规则且两面均处理正确。**基础SGR成立但容易**；不是依赖数量不足，也不是全固定包已证实覆盖。

固定材料证据见 [design_rationale.md:7](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/candidates/kegg_module_products_001/r01/design_rationale.md:7)：直接酶→模块已足够，不需强制 reaction 层；完整 reaction catalog 无M号，module catalog 无R/C号，实际没有所需配对产物，未知全库dump不作证明。[enzyme.txt:22](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/candidates/kegg_module_products_001/sources/enzyme.txt:22) 含 R00024 与 other R03140；[module_links.tsv:1](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/candidates/kegg_module_products_001/sources/module_links.tsv:1) 给完整3模块；[modules.txt:656](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/candidates/kegg_module_products_001/sources/modules.txt:656)、第852、1148行给三条相关反应。generic reaction 的 EQUATION 不是本题产品字段。

[controller_integration_check.json:2](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/candidates/kegg_module_products_001/r01/controller_integration_check.json:2) 记录重建通过，34条 REACTION 行全部纳排、3条匹配、2个root/3模块精确覆盖；pre/post_A 稳定比较通过。模型GO长输出曾截断，但随后特定尾段覆盖关键 REACTION；CG也读对应尾段。未发现现有参考的具体完整性缺口；未做最终独立审计和人工审核，不能据“程序同结果”宣布全部审核已通过。

**2. 自然邻近机会。** 本次0项。模块语义与 generic EQUATION 的差别是原构造已实证、已写入题面的核心判断；R00024 单模块普通边界和 R03140 两模块差异已全部处理。当前材料没有第二个自然研究目标所必需的新状态条件化证据。换酶、加模块数量、删去必要方向/字段提示或把省略解释成生物学缺失均不提供合法改造依据。

**3. 可复用与重核。** 可复用 EC→ALL_REAC/direct links 的范围画像、受控GET与批量经验、模块12列/续行/箭头/产品集合解析、缺失与冲突处理、REACTION逐行台账、证据索引及既有同义配对结构。新范围必须重核 ALL_REAC（含other）、全部direct links、每个完整模块的相关行与缺失配对、箭头方向和跨模块差异；不能复用旧产品答案或按旧3个ID取证。[reference.py:142](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/candidates/kegg_module_products_001/r01/reference.py:142)、第150–172行的集合覆盖可重用，但对更复杂化学表达式的处理范围仍有限，reference_report:25已说明，不得把未解析行作排除。

**4. 成本。** 本次四类新增成本均0。现有核心每轮3请求（酶、links、模块batch），116,701字节；若把已发现模块和根酶合并可估2请求，但该具体合并URL未实取，不能记成执行事实。两个稳定观察估4–6请求；可选generic reaction边界1请求/2,565字节，已有原件可复用。程序负责34行范围/集合检查，模型处理3条相关行与2个排除边界；历史builder735.249秒、73,083输入/22,140输出，CG120.763秒、492,369/2,138，GO90.434秒、352,971/1,863。详见各run.json及 [feasibility.json:20](/Users/ning/Documents/code/pcs_ra/sgr-bench/interact_sbench_formal/construction_pipeline/ten_task_phase/rolling_five/runs/kegg-annotation-boundary-feasibility-01/stage_assets/feasibility.json:20)。

新机会未定义，新增取证、参考修改、语义核验的未来量和wall均unknown；不能声称自动复用会节省固定比例。若有实质改造仍需至少1次Astra/high构造/配对+13次完整验证，程序取证另算；旧A不可抵扣。以当前A替代12个求解/攻击试次仅得18.1–24.2会话分钟的未验证代理，终审、人工审核、总wall、tokens、费用unknown，不能作可靠上界或成功保证。

**5. 决定。** 淘汰本次改造方向。单一重开缺口：没有**已实证且未被旧题规则覆盖的自然注释判断及其必需后续检索**。重开材料须给一正例、一边界与最小必要原件链；仅扩大输出或再解释已知R03140差异不足。保留两次满分，不改原件、不启动B或正式轮。

## 记录范围

历史 run.json 的 token 数是输入/输出，缓存包含于输入；会话分钟之和不等于wall。CG/GO运行身份与隔离沿用inventory内已验证记录，本次仅按结论所需读取轨迹，不重复模型测试或评分。当前审阅自身份/真实tokens由宿主记录，本审阅无法读取可靠账目，记unknown；未安装工具、未改限流、未改原题/评分/协议。本文及 kegg.json 是全部新增交付。
