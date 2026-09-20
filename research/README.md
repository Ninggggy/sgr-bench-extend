# 本轮研究证据与边界

当前方法及删改依据见[2026-09-13流程精简](methodology_simplification_2026-09-13.md)。以下复盘与旧规划仅在具体问题需要时查证，不是每个构造/恢复会话的必读清单；实际工作从[项目当前入口](../README.md)开始。

最新进展与经验修正见[2026-09-12五题经济轮复核](economic_five_efficiency_review_2026-09-12.md)：17项机会、2道完整候选、4次高分开发A、0/5标准收录及预算预留阻塞。仅复盘，未恢复实验。

后续构造阶段的只读效率复盘见[2026-09-10构造效率复盘](construction_efficiency_review_2026-09-10.md)，包含计数口径、成本、论文对照及可复用经验；不表示恢复已停止的构造工作。

记录日期：2026-09-07。这里保存的是方案可行性探索、旧题盘点和输入示例，不是已构造的新题数据集。

## 实际接口探测

| 请求 | 实际结果 | 能支持的判断 |
| --- | --- | --- |
| WQP Station：TCEQMAIN-10598 | HTTP 200，1228字节CSV，返回Neches River站点记录 | 站点入口、标识、类型与HUC字段可读 |
| WQP Activity：TCEQMAIN-10580，1978全年 | HTTP 200，7064字节，18条活动记录 | 当前响应提供活动身份与日期 |
| WQP Result：同站同年 | HTTP 200，86033字节，290条结果，涉及14个活动身份 | 当前响应可以按组织、站点、活动身份与活动表连接；无结果键落在活动表之外 |
| Census：2016 ACS5 B18105元数据 | HTTP 200，212908字节JSON | 可取得SEX BY AGE BY AMBULATORY DIFFICULTY变量定义；尚未做跨年可比性检查 |
| Water Office：07HA001，1966-05-01至03，flow | Python首次TLS验证失败；系统curl保持正常证书验证后HTTP 200，189字节CSV | 三天公开日流量可读：1720、1610、1540。这里只报告原始Value值，单位仍应查官方定义 |

完整请求URL、取得时间、返回类型、错误和响应路径见[live_probes.json](live_probes.json)、[WQP活动/结果探测](wqp_activity_result_probes.json)、[Water Office重试](wateroffice_retry.json)。初次错误保留，未关闭TLS校验。

WQP的一个具体观察：Temperature, sample、Specific conductance、pH、Oxygen四个名称在站点全年结果中均出现；14个有结果的活动身份中11个同时出现四者，另有3个不完整。TCEQMAIN-42848缺少pH，说明站点级存在性与活动级共同存在性确有差别。另有4个Activity响应身份没有出现在Result响应中，原因还需查明，不能直接判成源站无测量。

但这批结果的ActivityMediaName全部为Other，不能自行当作Water；名称共同出现也没有核验单位、深度、组分、限定符和科学可比性。因而这只是方向成立的一项观察，还不是合格面板或新题真值。可重算明细见[wqp_probe_analysis.json](wqp_probe_analysis.json)。尚未枚举其他站、证明来源完整性或找到最终站点赢家翻转。

## 旧题对应问题

[old_task_inventory.json](old_task_inventory.json)从正式JSONL读取50CG、50GO，覆盖14个domain、12个生态。它保留原字段并按ID后缀检查，不静默纠正数据。

发现两组内容对应跨编号：

| CG | 按内容对应GO | 主题 |
| --- | --- | --- |
| genome_003 | genome_004-g | 日本银屑病系统用药与批准顺序，8行 |
| genome_004 | genome_003-g | 灵长类维生素C模块异常和姐妹分支，2行 |

跨编号后，两组各自的domain、输出schema、oracle文本与行数一致。维生素C题的GO又省略了CG明确写出的2022截止与模块条件，因此“找到正确配对”仍不等于“两题面条件同样明确”。[对应记录](old_pairing_exceptions.json)保留此区别。原始题目没有改动；未来对照运行需显式记录内容映射和可比较范围，不直接按`task_id + '-g'`合并这两题。

## 官方机制来源

以下页面在本轮成功读取正文，仅作为其实际内容所支持的机制证据；没有把文档描述等同于具体候选已经可做。

- [Codex非交互执行](https://learn.chatgpt.com/docs/developer-commands#codex-exec)：与本机0.153.4帮助核对exec、JSON事件和输出文件参数。
- [GPT-6 Astra参数说明](https://developers.openai.com/api/docs/guides/latest-model#gpt-6-astra-update-api-and-model-parameters)：模型参数的官方来源；本地缓存列出模型不证明账户可调用。
- [WQP服务文档](https://www.waterqualitydata.us/webservices_documentation/)：网页/服务参数、不同输出粒度和数据profile差异。
- [Water Office服务说明](https://wateroffice.ec.gc.ca/services/index_e.html)：日/月/极值入口与站点、参数、时间范围。
- [CFPB投诉数据库](https://www.consumerfinance.gov/data-research/consumer-complaints/)：公开API、下载与历史分类相关说明。
- [Census API指南](https://www.census.gov/data/developers/guidance/api-user-guide.html)：数据发现、地理与vintage概念。
- [KEGG API](https://www.kegg.jp/kegg/rest/keggapi.html)：记录类型、层级与标识操作。
- [CDC WONDER常见问题](https://wonder.cdc.gov/wonder/help/faq.html)：公开/抑制值及排序行为；未尝试恢复隐去数据。
- [Reptile搜索入口](https://reptile-database.reptarium.cz/advanced_search)、[ChemExpo入口](https://comptox.epa.gov/chemexpo/)：入口可读取，具体新查询/层级行为未完成探测。

NVD开发页本轮正文读取为空，Europe PMC服务页403，NOAA/arXiv部分文档入口失败；未把搜索摘要提升为已验证机制。后续可在正式工具环境重新检查，不据此判定整个网站永久不可用。

## 完成范围

已完成真实小范围取数、普通程序分析、正式任务盘点、离线公开输入投影和prompt拼装。没有启动Codex模型构造工作进程，没有生成新CG/GO成品，没有执行新旧题难度实验，也没有人工验证记录。

example_public_cg.json和example_solver_prompt.md均来自已有arxiv_001，用于演示运行输入；它们不含私有oracle字段。该目录其他研究资产包含私有任务元数据，不应整个挂载给盲解者。
