# 首批网站构想的有界复核

复核日期：2026-09-08，约17:17—17:20（Asia/Shanghai）。本次仅新增此记录；读取[网站构想](../docs/04_sites.md)、[首批安排](../docs/06_first_batch.md)、[已有探测说明](README.md)，并核查WQP与Water Office官方文档。未生成oracle、未新增题干、未运行模型或难度实验，也未下载全站数据。下文“本次成功读取”指浏览工具取得正文，不等同于直接HTTP探测；工具可能使用缓存，已知缓存边界单列说明。

## 结论

WQP的活动/结果身份与Water Office的完整月份确有来源依据，但**更多关系连接或动态窗口并不自动证明必须反复站内检索**。若允许的官方批量接口已经能在前序结果产生前取得所有所需字段，后续依赖可在本地完成。此时仍可能有集合维护和口径判断难度，但不能把构造者写出的网页顺序视为唯一必要路径。

首批可继续探索WQP的身份与采样条件；Water Office适合先做公开下载路径挑战，确认“参考站产生窗口”究竟增加了检索必要性还是只增加离线计算。两者均未取得新候选的完整枚举、真实赢家翻转或超过旧题的模型证据。

## 本次成功读取的官方依据

| 官方页面 | 本次可支持的结论 | 不足以支持的结论 |
| --- | --- | --- |
| [WQP服务文档](https://www.waterqualitydata.us/webservices_documentation/) | 表单与服务共享过滤参数和输出；Station、Activity、Result及检测限有公开入口；可按组织、站点、日期等限定导出 | 某个新候选必须逐站点击，或summary能表达活动内全部指标的共同存在性 |
| [WQP用户指南](https://www.waterqualitydata.us/portal_userguide/) | ActivityIdentifier在组织内唯一；窄结果profile提供ResultIdentifier；一个结果可关联多个检测限 | 当前旧CSV自动具备新profile字段，或同活动同名结果必定唯一 |
| [EPA活动与结果定义](https://www.epa.gov/waterdata/concepts-and-definitions-storage-and-retrieval-and-water-quality-exchange) | 现场测量与采集水样可以分别形成Activity；结果属于活动，采样条件与分析结果分处相关对象 | 同站同日就是同次活动，或一个Activity必然代表完整站点访问 |
| [Water Office服务说明](https://wateroffice.ec.gc.ca/services/index_e.html) | 历史日均数据支持多站、flow/level及日期范围；无数据可返回只有表头的文件 | 空文件一定表示真实缺测，或请求失败可以视作站点不合格 |
| [02QC017的Flow可用性页](https://wateroffice.ec.gc.ca/report/data_availability_e.html?parameter_type=Flow&station=02QC017&type=historical) | 图例明确C为完整月、P为部分月、横线为无资料，且页面是Flow而非Level | 旧Peace River候选站本次已全部复核；此页仅用于确认标记语义 |
| [官方历史资料入口](https://www.canada.ca/en/environment-climate-change/services/water-overview/quantity/monitoring/survey/data-products-services.html)与[HYDAT说明](https://www.canada.ca/en/environment-climate-change/services/water-overview/quantity/monitoring/survey/data-products-services/national-archive-hydat.html) | 官方提供站点资料与历史日/月资料；HYDAT说明提供包含水文资料和站点信息的Access/SQLite单文件下载 | 本次已取得当前数据库，或网页与某一季度下载版本完全同步 |

WQP各文档、Water Office服务、加拿大历史资料入口与HYDAT说明均在本次返回正文，浏览工具标为当日抓取。02QC017页面虽本次读取成功，工具标注约3个月前抓取，页面修改日期为2026-03-09；只据其确认稳定图例语义。HYDAT说明正文修改日期仍为2018-07-05，当前资料入口也链接它：这支持官方下载路径存在的文档证据，不等于已核验最新下载文件或实测其更新频率。

## WQP：哪些依赖成立，哪些仍是设计假设

### 已有证据

组织内Activity身份是可靠的连接起点，连接时应保留组织上下文并核对站点一致性。若科学问题需要整次访问中多个活动的共同测量，就还需要来源明确的跨活动关系；不能用日期近似替代。

本次重新读取旧[结果响应](wqp_result_1978_probe.response)，确认290条记录且没有ResultIdentifier。温度记录有10条deg F与12条deg C；TCEQMAIN-42838的电导率有150和156 umho/cm，pH有7.1和7.5。这里只复核本地已保存响应，未重新向WQP取数。旧[共现分析](wqp_probe_analysis.json)的四指标全年存在与活动内不完整反例仍成立，但不能由此产生每活动唯一数值。介质Other、结果多值及缺少身份字段仍是解释缺口，不能通过自选平均、择首或将Other改成Water解决。

### 有价值但未定题的候选

在旧题对应的有限河段与年份范围中，核对同一组织内活动的测量完整性及必要采样条件；由合格活动集合决定后续比较窗口，再验证其他站的同口径覆盖。相对waterquality_004/005，增加的是活动粒度共同成立与后续候选集合重算，必须有真实纳排或赢家变化支撑。

若选择检测限方向，先实际检验窄结果与检测限响应的连接关系以及多个限值的类型语义，再确定研究规则。文档有连接字段不证明目标站/时期真的提供这些字段或合适的观测，不能先制定答案再补证据。

### 合法批量路径能否消除后续检索

**文档支持的能力**：WQP允许有界站点/区域与日期导出，网页不是唯一数据入口；需要的活动和结果可分别取得并连接。[服务文档](https://www.waterqualitydata.us/webservices_documentation/)

**推论，尚未运行候选验证**：如果区域、年份、指标、身份和采样条件都在预先可获得的少数导出中，那么完整活动筛选、动态窗口、站点排序都可能完全在本地计算。下载不会自动消除正确维护集合的要求，却可能消除“得到前序答案后才有必要发起后续检索”的主张。

后续攻击应让不知道gold的求解者先获得题目允许的全部官方导出能力，记录其是否无需自适应检索便稳定完成。若成功，按真实路径重新描述任务、评估难度；不能以禁止API、重复同一过滤或人为分割文件保住预想链路。若仍需额外来源解释采样关系，也要证明它确实改变纳排，不能只追加阅读步骤。

## Water Office：完整月份与数据决定窗口

### 已有证据

官方可用性页提供逐年逐月C/P/无资料状态，Flow与Level的口径应分别确认。日均服务可在一个请求中指定多个站点与时间范围；HYDAT还提供官方整体下载路径。[服务说明](https://wateroffice.ec.gc.ca/services/index_e.html)、[HYDAT说明](https://www.canada.ca/en/environment-climate-change/services/water-overview/quantity/monitoring/survey/data-products-services/national-archive-hydat.html)

不能把年度起止时间当完整月份，也不能由部分月份P直接判断某个较短窗口存在缺日：缺失日期可能在该窗口以外。反之，数值峰值窗口需要日数据，即使完整月状态能证明覆盖，也不能从C/P图例得到峰值日期。

### 有价值但未定题的候选

在旧Peace River河段的有限站点与历史年份中，用同一上游参考站指定季节的日均Flow最大值日期生成下游观察窗口，再选择共同覆盖年份和可用站点。预先写明参考季节完整性、并列取最早日期、窗口前后天数、跨月/跨年日期、有效值与标记的纳排、站点顺序以及排序并列规则。此需求只核验资料可用性，不推断洪水传播。

相对wateroffice_005，日期由前序数据产生是合理升级假设；目前还没有证明这些日期会改变最终站点，也没有查到可用性与日数据一致的真实跨月缺失见证。

### 合法批量路径的挑战更直接

**推论，尚未下载验证**：若历史年份和候选站都有限，先批量取得这些站的全季日均Flow，或使用相应HYDAT数据，就可在本地找参考站峰值、展开窗口、验证日覆盖、重算共同年份与站点。由于窗口日期已包含在预取时间全集中，“窗口未知”本身不阻止预取。

因此这个方向应优先检验批量路径。单纯将固定5—9月改成峰值前后若干天，可能仅增加计算难度。保留时必须如实说明观察到的是何种状态维护能力；不能把网络请求次数、页面局部性或源站暂时错误当成题目难度。

## 失败边界与未完成项

- 本次尝试读取[07HA001 Flow可用性页](https://wateroffice.ec.gc.ca/report/data_availability_e.html?parameter_type=Flow&station=07HA001&type=historical)与[07HD001 Flow可用性页](https://wateroffice.ec.gc.ca/report/data_availability_e.html?parameter_type=Flow&station=07HD001&type=historical)，浏览工具均返回不可重试的安全打开错误；没有换工具绕过，也没有把失败视为无资料。因而不能声称本次复核了这两站的完整月份或旧oracle。
- HYDAT链接首次点击参数未被工具接受，改用本次已返回页面引用后成功读取说明页；没有取得数据库文件。
- [此前Water Office探测](wateroffice_retry.json)曾发生Python TLS验证失败，系统curl随后在保留证书验证的条件下取得三天CSV。这是历史证据，本次没有重跑，不能用于证明新候选的全季覆盖。
- CFPB、ChemExpo和其余生态未在本次恢复后的有界复核中重新查询；此前文档与观察保留，但不据此新增当前取证结论。
- 未枚举新候选全集、未产生唯一答案、未运行合法下载求解或模型对照。WQP可继续做身份可用性探索；Water Office可继续做批量路径验证。不能将以上机制核实升级为“已构造且比旧50题更难”。
