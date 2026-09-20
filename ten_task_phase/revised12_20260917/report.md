# 12题修订与单轮盲测

更新时间：2026-09-17T12:48:11.383113+00:00

12题均保存修订副本；2题通过本轮测前检查，CG/GO各一次，共4个登记试次。其余题的具体阻塞见下表。没有恢复旧构造总控，没有改动全局方法文档或skill。

## 每题结果

| 题目 | 本轮状态 | CG Item-F1 / Row-F1 | GO Item-F1 / Row-F1 | 获取合规 CG / GO |
|---|---|---:|---:|---|
| arxiv_historical_title_001 | 暂缓 | 未测 | 未测 | — / — |
| arxiv_historical_title_002 | 暂缓 | 未测 | 未测 | — / — |
| economic_kegg_ddi_001 | 暂缓 | 未测 | 未测 | — / — |
| economic_nvd_daily_001 | 暂缓 | 未测 | 未测 | — / — |
| europemc_reuse_deposit_001 | 已登记单轮 | 0.00% / 0.00% | 0.00% / 0.00% | failed / passed |
| genome_002 | 暂缓 | 未测 | 未测 | — / — |
| kegg_initial_cdx_001 | 暂缓 | 未测 | 未测 | — / — |
| nvd_initial_assessment_001 | 暂缓 | 未测 | 未测 | — / — |
| reptile_001 | 暂缓 | 未测 | 未测 | — / — |
| stap_replication_protocol_001 | 已登记单轮 | NA / NA | NA / NA | inconclusive / passed |
| wateroffice_002 | 暂缓 | 未测 | 未测 | — / — |
| waterquality_003 | 暂缓 | 未测 | 未测 | — / — |

## 暂缓原因

- **arxiv_historical_title_001**：有界完整路径未证实：旧证据由完整年度语料和705条评论前沿建立范围，再查历史版本。不能把旧全量构造路径直接当作v2盲测路径；未证明60请求/10页内完整替代路径。
- **arxiv_historical_title_002**：有界完整路径未证实：r03曾需25890条完整处置修复词法筛选漏项。不能直接以关键词搜索代替完整范围证明；未证明当前额度内合法完整路径。
- **economic_kegg_ddi_001**：完整已验证单条路径为20+40个端点，尚需组身份/成员发现，超过60请求。仅SSRI端点实测漏14对；完整60-ID导出禁止。历史观测期也不能冒充当前数据。未证明另一完整合法路径。
- **economic_nvd_daily_001**：需逐UUID成功零覆盖证据；参考答案的不同UUID数和必要请求将在本轮程序统计。旧全量/批量路径不能用于v2；不以额度耗尽产生低分。历史答案含143个不同UUID；仅必需成功零覆盖核对已需143次单UUID请求。
- **genome_002**：已澄清专门图范围并修正标识/输出格式；普通GENOME记录和模块可读，但联合图入口（包括源页面真实链接及旧成功路径）现为HTTP 400。最后native web访问旧合法路径收到明确non-retryable拒绝，之后不重试或换表示。联合状态证据未能确认，不测。
- **kegg_initial_cdx_001**：原题措辞和评分输出已修正，但本轮FDA关键历史文件返回HTTP 404的abuse-detection/excessive-requests拦截页；不换工具绕过。现有私有缓存不能替代盲解可达来源，因此本轮不测。
- **nvd_initial_assessment_001**：旧完整44个CVE历史包含按每页20条计算至少63页，尚未包含发现与当前状态查询。旧联合历史批量响应禁止；未证明其他60请求内完整合法路径。
- **reptile_001**：已澄清最近旧属名称和现代印度边界，但原8行答案的完整性及这些修订下的纳排尚未得到完整证据支持；保留公开答案暴露史。不得仅修改措辞后沿用未核实oracle。
- **wateroffice_002**：可按旧审查修正排序和CG/GO条件，但本轮关键08EE004 Flow可用性页面被web明确拒绝为non-retryable。未重试或换工具；当前可访问性未确认，不启动盲测绕过该阻塞。
- **waterquality_003**：已证实同HUC多个合格站点；没有公开唯一择优规则。不能为保住原三行答案事后挑选规则；当前修订明确欠定，旧oracle只保留为历史附件，不作为本轮金标准。

## 暂缓题后续修复（以上原测前记录保留）

本轮仍为部分交付。下列新核对不等于测试通过；没有新增盲测试次。完整记录见 [暂缓题处理报告](blocked_followup/report.md)。范围调整和公开择优规则尚待用户确认，已知访问拒绝未重试。

- **arxiv_historical_title_002**：完整旧目录核查显示通用词表命中168条，却遗漏r03的两个重要补项；词表搜索不能直接作为完整性证明。
- **nvd_initial_assessment_001**：已验证历史子问题可早停；但分开获取44个当前记录及45页历史至少89次，尚未包含发现。合并单条详情页的合法替代路径未验证，不能用构造端完整导出免掉当前记录获取成本。
- **reptile_001**：旧答案中的 oatesii 两个异属名同为2014；纳入范围尚未验证，不能据年份单独确定旧名。parallelus 必要页面本次明确拒绝访问。
- **wateroffice_002**：四站参考已从历史官方返回独立重建，等于修订答案；范围证据出处已纠正。实时页面拒绝仍未解除。
- **waterquality_003**：303站元数据中49个主河道名称候选已逐站核查；14个满足年限（地理筛选前）。12038不能直接当作严格下游反例；择优规则待确认，NLDI导航入口拒绝后已停止。

## 汇总口径

| 题面 | 原始宏平均 Item-F1 | 原始整题全对率 | 有效评分/登记 | 合规宏平均 Item-F1 | 合规有效评分数 |
|---|---:|---:|---:|---:|---:|
| CG | 0.00% | 0.00% | 1/2 | NA | 0 |
| GO | 0.00% | 0.00% | 1/2 | 0.00% | 1 |

| 题面 | 已运行 | 数值评分 | NA | 获取合规会话 | 合规且无已知混淆的数值评分 |
|---|---:|---:|---:|---:|---:|
| CG | 2 | 1 | 1 | 0 | 0 |
| GO | 2 | 1 | 1 | 2 | 0 |

未启动的暂缓题不计入 NA、有效评分数或上述均值分母。构造端来源核查不是新的盲测；没有新增盲测成本，总控核查 token/费用未知。

整题全对要求Item-F1和Row-F1都等于1。NA、解析失败和缺失结果不补零。原始分数只是与登记参考的确定性比较；访问失败所伴随的数字低分不能解释为能力零分。合规子集存在选择偏差，不代表全部12题。

原始双面单次分数均低于70%：europemc_reuse_deposit_001。
同时获取合规且未发现能力解释混淆的双面低于70%候选：无。

本轮不是正式收录复测，不能据此判断双面各三次均值；历史标准收录和用户指定收录均保持原状。

## 逐次诊断

- **europemc_reuse_deposit_001-polish01-cg-once**：gpt-5.6-sol/medium，模型核验 passed；原始Item-F1=0：返回PMC7934477/GSE138525而非参考行；该论文不属于已核实的10篇ACCESSION_ID索引候选。候选接口受阻且拒绝后改HTML表示重试（L3–8），不能解释为干净能力零分。
- **europemc_reuse_deposit_001-polish01-go-once**：gpt-5.6-sol/medium，模型核验 passed；原始Item-F1=0，返回同一范围外论文。获取行为合规，但完整索引查询受阻，不能将结果解释为无访问混淆的能力零分；自报31请求不准确，实际33。声称complete却未验证索引范围。
- **stap_replication_protocol_001-polish01-cg-once**：gpt-5.6-sol/medium，模型核验 passed；最终UNRESOLVED，评分器metrics=null，因此NA而非0。完整引用集合访问受阻；曾讨论4篇实验报告，但未交付答案表，不能据此计内容错误。L47–50的被拒论文定向搜索存在合规疑点，标为inconclusive。
- **stap_replication_protocol_001-polish01-go-once**：gpt-5.6-sol/medium，模型核验 passed；3次请求后因不可重试的引用接口拒绝而停止，返回UNRESOLVED。遵守访问限制；metrics=null，NA，不补零。没有可评价的答案表。

## 成本

```json
{
  "input_tokens": 4565261,
  "input_tokens_known_sessions": 4,
  "cached_input_tokens": 4120576,
  "cached_input_tokens_known_sessions": 4,
  "output_tokens": 16254,
  "output_tokens_known_sessions": 4,
  "reasoning_output_tokens": 9787,
  "reasoning_output_tokens_known_sessions": 4,
  "cache_write_input_tokens": 0,
  "cache_write_input_tokens_known_sessions": 4,
  "planned_blind_trials": 4,
  "started_blind_trials": 4,
  "completed_blind_trials": 4,
  "sum_worker_seconds": 693.381,
  "blind_wall_seconds": 263.407987,
  "controller_tokens": null,
  "controller_cost": "unknown; same host conversation, no fabricated model/session accounting",
  "currency_cost": null,
  "note": "Cached input is included in input; worker durations are not wall time. Shared account quota change is not attributed to this batch."
}
```

## 文件与复算

- `candidates/<id>/CG.json`、`GO.json`：修订题面；`*_historical.json`：原题。
- `review.json`：变更、受阻原因和证据路径；`historical_oracle.psv`与`oracle.psv`分别保留历史与本轮参考。受阻题参考不代表质量通过。
- `plan.json`、`campaign.json`、`session_ledger.jsonl`：事前登记与独立批次用量；原阶段账本未重置。
- `runs/<run>/answer.txt`、`scoring/`、`tool_events.jsonl`、`retrieval_review.json`：原始回答、评分、实际工具轨迹及审查。
- `source_checks/`：仅构造者可见的源复核；从未送入盲解容器。
- `offline_checks.json`：配对条件和机械评分检查；不冒称独立语义审核。
- `python3 report.py`：从现有运行与审查重新生成汇总，不运行模型、不重新评分。
- 逐次评分可用原 `runtime/score.py --answer runs/<run>/answer.txt --gold candidates/<id>/oracle.psv --rules candidates/<id>/rules.json --out <新目录>` 离线复算。

没有新增正式收录，没有自动继续任务。
