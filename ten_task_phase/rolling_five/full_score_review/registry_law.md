# IANA / SCOTUS 满分题有界复核

结论：本次不推荐任何一道直接进入改造。IANA 暂存一个历史原件缺口；SCOTUS 淘汰本次改造方向。保留两题原版本、满分与停止决定。本次只读既存材料，未联网、未运行参考程序或评分器、未启动测试/攻击/正式复测。暂无新增原件支持值得改造的结论。

## 依据与口径

正式论文入口为 `chinese_1st_ver/latex/main.tex:142` 实际引用的 `sections/3_Method.tex`，不是 writing 旧稿。Method:8–12 要求专门网站的状态暴露答案证据，42–47 六要求分别为领域性、长尾来源、唯一可验证、时间/版本稳定、抗捷径、前步条件化后续检索。62–63 要核实非平凡依赖和实际捷径。发现参数驱动的一次批量访问可以保留依赖，不额外要求第二层、特殊回查或永久 HTTP 重放；任意引用遍历则不自动证明严格 SGR。

共同经验：`construction_pipeline/research/construction_efficiency_review_2026-09-10.md:52–74`、`construction_pipeline/research/economic_five_efficiency_review_2026-09-12.md:34–52`、`/Users/ning/.codex/skills/0-autoresearch-skill/references/benchmark-construction-efficiency.md`（“先明确合格的依据”“先查便宜的反证”“失败信号与停止规则”）。此技能参考作为审计资料读取，没有执行研究工作流。下文 `C/` 与 `R/` 分别指本目录上一级的 `candidates/` 与 `runs/`；机器报告给出绝对路径。

`full_score_review/inventory.json` 已验证模型为 Sol/medium、隔离和原运行评分；IANA 48/48 是 Item-F1 分子/分母口径，实际为 24/24 个字段、4 行；SCOTUS 18/18 对应 9/9 字段、3 行。不是正式三次均值，也不是独立质量终审。

## iana_dtls_001 / r03

### 1. 实际满分原因、机制、完整性

主要原因是**注册表直接给四个注册字段，发现的标识符驱动一批文档检索，再直接读取 RFC header 与 draft family 状态**。不是大量本地 join，也不是工具故障导致偶然得分。

- GO 原轨迹 `R/iana-r03-go-dev-a/tool_events.jsonl:5–9`：ordinal 28 请求 TXT，ordinal 31 的 L164–172 给出全部四个 Y 条目及引用；ordinal 35/42 用这些 RFC/draft 身份搜索并打开，ordinal 45 的 family 页面 L89–108 给出最新 revision 和 Expired，RFC 头给 Category。最后 ordinal 49 回看两个 RFC 页首。XML 失败在第3–4行，TXT成功后不影响答案。
- CG 原轨迹 `R/iana-r03-cg-dev-a/tool_events.jsonl:7–14`：ordinal 36/39 得到注册表，L157–165 暴露四条；ordinal 43 批量点击四个发现的引用，ordinal 50 查看页首，ordinal 57/60 从旧 revision 页面到最新 revision。CG额外旧→新跳转是实际走法，不是任务必要第二层；GO直接 family 页即足够。
- 原运行 `run.json`：CG 75.438秒，GO 60.396秒。两面均24/24，见 `C/iana_dtls_001/r03/development_decision.json:7–91`。注册名、53与54身份、N/D及过期草稿的必要语义都已明确界定，Sol正确执行，不应删提示求低分。

**机制分层判断：**注册表→发现的 draft family/版本状态至少支持真实逻辑依赖；把 IETF document family/revision 作为专门站点记录视图，可以解释为一层 SGR，且实际很容易。单独的 RFC 引用跳转不能承担全部 SGR 论证。现有 state_graph:18–30 自承五源短路径、无必需版本深跳；跨 IANA/IETF 生态如何落实 Method 的目标 W 及状态仍未经独立终审，故不声称严格 SGR 已获最终认证。不存在已证“固定全材料覆盖一切”反例：IANA XML/TXT只覆盖注册字段，不能给全部文档生命周期；Datatracker dumps/API覆盖未知，不从访问失败推断不存在。

**完整性：**参考实现 `reference.py:94–157` 枚举103条和完整0–65535区间，99排除、4身份纳入；`controller_pre_A_check.json` 记录实际执行及24字段对齐；`development_decision.json:98–102` 记录测后全集及字段一致。现有集合/答案完整性有强证据，无已发现漏项。constructor报告里“未执行”是较早状态，不覆盖后续 controller 已执行记录；独立终审和人工审核仍未做。另有不影响当前四行答案的元数据残留：`candidate.json:59` private empty clause仍写header+NONE，而r03公共格式及reference已经修复；若复用应同步纠正，不能改写历史满分或称当前非空答案不完整。

### 2. 唯一邻近机会与缺口

仅暂存“过时 connection_id 分配的具体历史规范与最终分配的兼容边界”，不启动新方向或完整oracle。自然需求是确定旧设备的53分配对应哪份协议规范，避免把54最终规范误用于53；它不同于抄成熟度，也不是换年或加行数。

既存见证：`C/iana_dtls_001/sources/rfc9146.txt:573–580` 明确说53属于本文件先前版本、与最终文档不兼容，故改用54；`r03/annotations.json:7,12` 也明确当前原件不足以把最终行为归给过时分配。

拟议但**未验证**的依赖是：注册表发现过时数值身份 → RFC明确其来源是早期分配 → IETF该文档的历史revision/分配记录视图 → 取得53实际使用的规范版本及必要兼容边界。**唯一最小缺口**是一份官方历史 Internet-Draft 原件（或明确指向该原件的官方分配事件），其revision可核定，正文明确使用53并能定位兼容性相关定义。当前材料没有这个对应关系；“previous version”不能推定任意一个旧revision。原件URL/revision未知，不猜测。

重开只接受上述最小原件；仅拿到“53被deprecated”、新状态页或更多现行RFC不解除缺口。若原件一页已直接给完整所需对照且无需结果条件化网站状态，或者原件不足定义唯一版本边界，即停止，不扩全集/第二方向。已有文本已经直接回答“是否兼容=否”，因此不能仅把“兼容否”作为新难字段。暂无新增证据支持现在值得改造。

### 3. 可复用与必须重核

可复用：IANA namespace/table画像、TXT/XML读取经验、singleton/range覆盖检查、数值主键与xref类型解析、来源索引、普通N及53/54/60边界、RFC header解析、既有序列化修复。103条及四个身份可作该次观察的研究证据。

需重核：历史53→文档revision对应、旧版本定义及与最终文档的真实区别、自然问题完整范围、CG/GO全部条件和新reference；任何新观察日期的注册全集/生命周期也必须重核。旧成熟度字段正确不自动迁移为历史兼容性答案。不能沿用旧A替代修订后验证。

修订余量：协议上限2（`R/iana-r03-go-dev-a/campaign_context.json:9`），inventory记used=1、remaining=1。实际r01→r02是措辞编辑，r02→r03是实发empty serialization问题修复，见 `editorial_patch.json`、`serialization_patch.json`、`serialization_repair_review.json:4–26` 和 `progress.md:27`。不把r03机械当已用两次领域修订，也不擅自退还账上已计的一次；新历史语义条件需占剩余实质修订，换ID不能重置。

### 4. 成本（条件估计，不是已执行计划）

新增取证只值得有界原件定位：程序/浏览1–3次针对性原件请求，Astra审读约5–15分钟上限；是否在上限内取得原件未知，停止不保证成功。若缺口解除，参考修改预计程序/人工20–45分钟（复用约300行参考的注册解析，新增历史关系/证据字段）；语义核对另需模型/领域判断20–45分钟，涵盖身份、revision和兼容定义，程序无法代替。依据是旧builder实际1515.936秒（25.27分钟）及本次所见复用范围；估计无实测节省比例，token和金额未知。

完整后续验证仍须新A2；仅通过才B2、攻击2、独立终审1、正式6，共完整路径13模型会话，另至少1次Astra/high取证、参考与配对改造会话，加人工审核时间未知。旧A每次约1–1.3分钟只说明旧题易解，不可靠预测新题；完整后续墙钟、token、费用unknown，不用13乘旧时长冒充预算。当前不授权或启动这些阶段。

### 5. 决定

**暂存，不入选继续。** 一个重开证据缺口如上。当前满分有具体短路径支持，现有 incompatibility 事实已是旧构造已知材料，本次没有新增原件。无可审查的新条件答案，因此不提供伪成型英文题面，也不消耗剩余修订。

## scotus_joinder_001 / r01

### 1. 实际满分原因、机制、完整性

主要原因是**发布批次表发现三案，随后取得三份PDF，syllabus attribution集中给出全部named groups，按已明确的formal joinder规则做小规模集合计数**。有领域判断（lead与separate ownership、部分加入与结论同意），但当前材料将它们写得很明白。

- GO `R/scotus-r01-go-dev-a/tool_events.jsonl:1–6`：ordinal14查询选定term/date，输出ordinal17提供三案与官方PDF文件名；ordinal23一次打开三份发现的PDF。ordinal26的Moore L177–180、ordinal33的Counterman L89–94及Mallory L78–84就给全部组，随后ordinal39/46做声明和版本核对。第10行ordinal49回看完整term表L34–36，确认三案和R顺序。并非从最终答案反推过程。
- CG `R/scotus-r01-cg-dev-a/tool_events.jsonl:3–5`：ordinal23/26取得term表并点击三案；其初次批量结果未显示，后续试了原release文件和错误目录，最后通过站内搜索结果到正确preliminary prints（第19–28行，ordinal77/89/101及返回80/92/104）。第29–30行查Alito等声明。这个额外定位成本不是更复杂的joinder推理。
- 原 `run.json` CG 130.921秒、GO 80.618秒；两面9/9，`development_decision.json:7–83`。Moore 6/6、Counterman 5/5、Mallory 4/5均可由集中attribution和作者计数得到；没有必要读完每页法律论证。

**机制分层判断：**日期过滤后的结果决定下一批PDF身份，真实逻辑依赖成立，batch并不取消它。现有证据具体支持的是“term/release scope → 文档记录视图”；按Method:8–12的严格SGR要求，仍需独立说明这种网站层级/记录选择对答案证据暴露的作用，而不是仅称跨页即SGR。材料没有证明它不成立；PDF静态不是固定全覆盖反例，也不要求另造第二层。就本次改造决定而言，无需把旧题机制判死：短路径满分和无新证据已足以不继续。

固定材料检查见 `state_graph.json:14–19`：Jnl22只确认批次、不供完整joinder；被检查的Orders PDF为901–970页，不是本题三案全集；GovInfo完整bulk覆盖unknown。这些不能升级为“全部固定材料均不可能”或“有固定材料故机制已失败”。

**完整性：**`reference.py:93–115,279–297` 先枚举58条term记录再选日期/类别，所选3案与annotation集合严格对齐；`pre_A_rebuild/execution_checks.json`为58/3、4named groups、unresolved=[]；`controller_pre_A_stability.json`、`controller_post_A_stability.json`支持全列表及9字段跨A不变。`annotations.json:14–21,33–41,56–64`定位普通、separate ownership和部分joinder边界；reference:197–257核对完整part partition与计数。现有参考完整性有支持，未发现漏案/错计；未完成独立终审及人工审核，不把满分当两者替代。

### 2. 邻近机会

**没有已取证值得改造的新机会。** 原件中的自然ownership/part范围边界（Counterman separate joinder、Mallory divided lead）已经在旧题必要规则及答案中处理，并被两面成功解决。把范围改为所有separate opinions只增加同三份PDF上的本地计数；把问题改成哪种理由具有拘束力需要另一个不确定的法律评价目标，当前没有支持唯一参考与必需后续检索的新原件。本次不把任何一个包装为第二候选，不联网枚举新年份/新案件。

仅保留重开门槛：一份官方、具体的后续原件，证明当前批次某个formal attribution的身份/版本范围需要根据前文结果选择另一官方记录才能确定，而且该事实不是现有三份PDF的直接归纳。当前没有这样的原件、对应网站状态或自然新条件，故机会字段为null。此门槛是未来证据要求，不是声称已存在。

### 3. 可复用与必须重核

可复用：term表画像与58条观察全集、日期/类别/发布序号解析、法院docket/print身份检查、PDF-text配对说明、named justice集合、普通/分part解析、scope ownership证据和现有三案annotation索引。尤其 `reference.py:135–148` 的parser只处理当前两种已见attribution形式，不能外推为通用法院解析器。

需重核：任何新增写作主体/类别/日期完整范围、新的attribution语法、形式加入与结论同意边界、版本对应和反证、配对规则、reference真值。原三案非空答案和稳定记录只覆盖旧题，不能通过复制答案或换ID抵扣验证。

修订余量：上限2；r01暂无实质修订，used=0、remaining=2。余量可用不构成继续理由。

### 4. 成本

本次建议新增取证/参考改造/语义工作投入均为0，因为没有具名新原件或新必要条件。若今后提供上述一份原件，首次有界检查可设1–3次针对请求、模型5–15分钟上限；目前连请求目标都unknown，不能当可执行预算。reference改动规模及独立语义核对总量unknown，不能将全部separate-opinion重标的时间说成既有parser自动完成。

成本参照：旧feasibility282.356秒，builder740.483秒（12.34分钟）；旧A时长如上，是这些旧材料的实际成本，不是新题估计。若实质修订真的值得进入完整验证，仍有A2+B2+攻击2+独审1+正式6共13模型会话，另至少1次Astra/high取证、参考与配对改造会话，加人工审核未知。后续时长/token/金额unknown；历史满分不能抵扣。

### 5. 决定

**淘汰本次改造方向，保留旧题和全部证据。** 依据是现有三个PDF的集中formal attribution已被两面正确处理，且无新原件说明新的自然、必要检索判断。并非认定一切法院题不可能，也非宣告旧题严格SGR已被固定材料推翻。现在没有值得交付的英文改造草稿。

## 复核成本与边界

起始UTC：2026-09-12T17:36:53Z；结束UTC：2026-09-12T17:43:45.199075+00:00；wall上限1200秒，不要求耗满。模型按父任务授权为GPT-6 Astra/high；实际宿主token计数不在本子代理可见接口内，输入/缓存/输出均unknown。未兑换额度。

截至写本报告前，手工可数只读exec_command调用17次（包括路径纠正和截断后的定向读取），时钟2次；加本报告创建及JSON/路径检查共20次exec_command、15次functions.exec；不把本地程序请求等同模型会话。全部网络请求0，新盲测/攻击/正式复测0，新子代理0。涉及原轨迹的外部工具记录仅作历史资料，没有重放。
