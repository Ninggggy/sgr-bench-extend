# 31道底题有界检索复测结果

已结束：60/60次。31道中30道各测CG/GO一次；BALF因先前服务安全中断排除。所有实际运行均为gpt-5.6-sol / medium；未追加、替换或重试。

获取规则审查：34通过，26失败，0待审；3次未评分保持NA。

| 统计口径 | CG | GO |
|---|---:|---:|
| 合规且可评分：平均Item-F1 | 87.8794%（n=17） | 81.1067%（n=17） |
| 合规且可评分：整题全对率 | 76.4706%（13/17） | 64.7059%（11/17） |
| 全部原始可评分（含违规）：平均Item-F1 | 82.5283%（n=29） | 72.4702%（n=28） |
| 全部原始可评分（含违规）：整题全对率 | 62.0690%（18/29） | 50.0000%（14/28） |

合规子集经过筛选，不能代表全部31题；其来源访问、范围唯一性、格式及排序混淆仍在逐次review_notes中保留。未做参考答案的新质量认证，也不作正式收录判定。

主要限制：提示约束并未硬性拦截全部违规；出现完整候选导出、拒绝后重试、超过60请求或2目标并发的情况。原始低分也包括大小写、解释段落误入数据、列错位、排序及可能多解，不能一概归为检索能力错误。

盲测实际耗时115分55秒（19:57:58—21:53:53，北京时间2026-09-13），两个盲测槽并行。累计会话时长另列，不能当作墙钟时间。账户已用周额度观察53%→64%，共享账户差值不能全部归因本批；未使用重置。货币成本和总控token未知。

保存的旧材料/评分不变；当前summary已纠正NA误计零，旧控制器诊断快照保留用于追溯。数据源实际访问日为9月13日，沿用提示日期9月9日，部分题目要求9月12日快照，日期冲突和来源漂移未被本次修复。

更新时间：2026-09-13T13:56:42.240666+00:00

31道中30道计划执行CG/GO各一次，共60次；BALF保留此前服务安全中断，不重启。

原始分数按旧参考答案计算，不自动代表协议合规或当前来源下答案仍正确。NA/故障/缺失不补零；单次分数不是正式三次收录均值。

| 题目 | 版本 | 题面 | 状态 | 原始Item-F1 | 获取合规 |
|---|---|---|---|---:|---|
| arxiv_assumption_scope_001 | r03 | CG | completed | 100.0% | passed |
| arxiv_assumption_scope_001 | r03 | GO | completed | 100.0% | passed |
| arxiv_historical_title_001 | r02 | CG | completed | NA | failed |
| arxiv_historical_title_001 | r02 | GO | completed | 22.2222% | failed |
| arxiv_historical_title_002 | r03 | CG | completed | 25.0% | failed |
| arxiv_historical_title_002 | r03 | GO | completed | 9.0909% | failed |
| cfpb_app_issuer_version_001 | r01 | CG | completed | 100.0% | passed |
| cfpb_app_issuer_version_001 | r01 | GO | completed | 100.0% | passed |
| chembl_stereochemical_peers_001 | r02 | CG | completed | 100.0% | failed |
| chembl_stereochemical_peers_001 | r02 | GO | completed | 66.6667% | failed |
| comptox_012 | r00 | CG | completed | 100.0% | passed |
| comptox_012 | r00 | GO | completed | 100.0% | passed |
| device_recall_backlink_001 | r01 | CG | completed | 100.0% | passed |
| device_recall_backlink_001 | r01 | GO | completed | 100.0% | passed |
| diazepam_receptor_identity_001 | r01 | CG | completed | 100.0% | failed |
| diazepam_receptor_identity_001 | r01 | GO | completed | 100.0% | failed |
| economic_kegg_ddi_001 | r02 | CG | completed | 77.4327% | failed |
| economic_kegg_ddi_001 | r02 | GO | completed | 91.2621% | failed |
| economic_nvd_daily_001 | r02 | CG | completed | 11.5702% | passed |
| economic_nvd_daily_001 | r02 | GO | completed | 0.0% | failed |
| epmc_quantitative_001 | r02 | CG | completed | 100.0% | passed |
| epmc_quantitative_001 | r02 | GO | completed | 100.0% | passed |
| europemc_declared_patent_001 | r01 | CG | completed | 100.0% | passed |
| europemc_declared_patent_001 | r01 | GO | completed | 100.0% | passed |
| europemc_republication_title_001 | r01 | CG | completed | 100.0% | failed |
| europemc_republication_title_001 | r01 | GO | completed | 100.0% | passed |
| europemc_reuse_deposit_001 | r01 | CG | completed | 0.0% | failed |
| europemc_reuse_deposit_001 | r01 | GO | completed | 0.0% | passed |
| genome_002 | r00 | CG | completed | 100.0% | passed |
| genome_002 | r00 | GO | completed | 0.0% | passed |
| iana_dtls_001 | r04 | CG | completed | 100.0% | passed |
| iana_dtls_001 | r04 | GO | completed | 100.0% | failed |
| kegg_initial_cdx_001 | r02 | CG | completed | 67.7966% | passed |
| kegg_initial_cdx_001 | r02 | GO | completed | 76.0% | passed |
| kegg_module_products_001 | r01 | CG | completed | 100.0% | failed |
| kegg_module_products_001 | r01 | GO | completed | NA | failed |
| kegg_prodrug_identity_001 | r01 | CG | completed | 100.0% | passed |
| kegg_prodrug_identity_001 | r01 | GO | completed | 100.0% | passed |
| nvd_configuration_environment_001 | r01 | CG | completed | 96.4912% | failed |
| nvd_configuration_environment_001 | r01 | GO | completed | 100.0% | failed |
| nvd_initial_assessment_001 | r01 | CG | completed | 50.0% | failed |
| nvd_initial_assessment_001 | r01 | GO | completed | 66.6667% | failed |
| nvd_repository_publication_001 | r01 | CG | completed | 100.0% | passed |
| nvd_repository_publication_001 | r01 | GO | completed | 90.9091% | passed |
| optimization_guarantee_001 | r02 | CG | completed | 100.0% | passed |
| optimization_guarantee_001 | r02 | GO | completed | 100.0% | passed |
| reptile_001 | r00 | CG | completed | 71.875% | failed |
| reptile_001 | r00 | GO | completed | 66.6667% | failed |
| reptile_type_referral_001 | r01 | CG | completed | 100.0% | passed |
| reptile_type_referral_001 | r01 | GO | completed | 100.0% | passed |
| scotus_joinder_001 | r01 | CG | completed | 100.0% | passed |
| scotus_joinder_001 | r01 | GO | completed | 100.0% | passed |
| stap_replication_protocol_001 | r01 | CG | completed | 78.5714% | failed |
| stap_replication_protocol_001 | r01 | GO | completed | 78.5714% | passed |
| wateroffice_002 | r00 | CG | completed | 81.25% | passed |
| wateroffice_002 | r00 | GO | completed | 27.7778% | failed |
| waterquality_003 | r00 | CG | completed | 33.3333% | passed |
| waterquality_003 | r00 | GO | completed | 33.3333% | passed |
| wqp_censored_screening_001 | r02 | CG | completed | 100.0% | failed |
| wqp_censored_screening_001 | r02 | GO | completed | NA | failed |

按底题对照（原始Item-F1 / 获取合规审查）：

| 底题 | 版本 | CG | GO |
|---|---|---|---|
| arxiv_assumption_scope_001 | r03 | 100.0000% / passed | 100.0000% / passed |
| arxiv_historical_title_001 | r02 | NA / failed | 22.2222% / failed |
| arxiv_historical_title_002 | r03 | 25.0000% / failed | 9.0909% / failed |
| cfpb_app_issuer_version_001 | r01 | 100.0000% / passed | 100.0000% / passed |
| chembl_stereochemical_peers_001 | r02 | 100.0000% / failed | 66.6667% / failed |
| comptox_012 | r00 | 100.0000% / passed | 100.0000% / passed |
| device_recall_backlink_001 | r01 | 100.0000% / passed | 100.0000% / passed |
| diazepam_receptor_identity_001 | r01 | 100.0000% / failed | 100.0000% / failed |
| economic_kegg_ddi_001 | r02 | 77.4327% / failed | 91.2621% / failed |
| economic_nvd_daily_001 | r02 | 11.5702% / passed | 0.0000% / failed |
| epmc_quantitative_001 | r02 | 100.0000% / passed | 100.0000% / passed |
| europemc_declared_patent_001 | r01 | 100.0000% / passed | 100.0000% / passed |
| europemc_republication_title_001 | r01 | 100.0000% / failed | 100.0000% / passed |
| europemc_reuse_deposit_001 | r01 | 0.0000% / failed | 0.0000% / passed |
| genome_002 | r00 | 100.0000% / passed | 0.0000% / passed |
| iana_dtls_001 | r04 | 100.0000% / passed | 100.0000% / failed |
| kegg_initial_cdx_001 | r02 | 67.7966% / passed | 76.0000% / passed |
| kegg_module_products_001 | r01 | 100.0000% / failed | NA / failed |
| kegg_prodrug_identity_001 | r01 | 100.0000% / passed | 100.0000% / passed |
| nvd_configuration_environment_001 | r01 | 96.4912% / failed | 100.0000% / failed |
| nvd_initial_assessment_001 | r01 | 50.0000% / failed | 66.6667% / failed |
| nvd_repository_publication_001 | r01 | 100.0000% / passed | 90.9091% / passed |
| optimization_guarantee_001 | r02 | 100.0000% / passed | 100.0000% / passed |
| reptile_001 | r00 | 71.8750% / failed | 66.6667% / failed |
| reptile_type_referral_001 | r01 | 100.0000% / passed | 100.0000% / passed |
| scotus_joinder_001 | r01 | 100.0000% / passed | 100.0000% / passed |
| stap_replication_protocol_001 | r01 | 78.5714% / failed | 78.5714% / passed |
| wateroffice_002 | r00 | 81.2500% / passed | 27.7778% / failed |
| waterquality_003 | r00 | 33.3333% / passed | 33.3333% / passed |
| wqp_censored_screening_001 | r02 | 100.0000% / failed | NA / failed |

统计口径：Item-F1为逐题字段F1的宏平均；整题全对率要求Item-F1与Row-F1均为1。合规且未报告访问混淆的子集只是诊断，存在选择偏差，不能代表全部31题。

成本记录：
```json
{
  "first_start": "2026-09-13T11:57:58.665174+00:00",
  "last_completed_end": "2026-09-13T13:53:53.342453+00:00",
  "observed_start_to_last_end_seconds": 6954.677279,
  "summed_session_seconds": 13674.524,
  "usage_record_count": 60,
  "tokens": {
    "input_tokens": 82474886,
    "cached_input_tokens": 75813632,
    "cache_write_input_tokens": 0,
    "output_tokens": 328004,
    "reasoning_output_tokens": 177947
  },
  "money_cost": null,
  "controller_token_cost": null,
  "weekly_quota_attributable_to_batch": null,
  "note": "Cache input is a subset of input, reasoning output a subset of output; do not add them again. Wall interval differs from summed concurrent sessions. Missing usage is unknown."
}
```

按题面统计：

```json
{
  "CG": {
    "planned": 30,
    "raw": {
      "n": 29,
      "macro_Item_F1_exact": "16725060945/20265850528",
      "macro_Item_F1_percent": 82.52829518253911,
      "full_answers": 18,
      "full_answer_rate_percent": 62.06896551724138
    },
    "reviewed_compliant": {
      "n": 17,
      "macro_Item_F1_exact": "5119349/5825424",
      "macro_Item_F1_percent": 87.87942302568878,
      "full_answers": 13,
      "full_answer_rate_percent": 76.47058823529412
    },
    "compliant_with_access_confounds": 4,
    "compliant_without_reported_access_confounds": {
      "n": 13,
      "macro_Item_F1_exact": "907/944",
      "macro_Item_F1_percent": 96.08050847457628,
      "full_answers": 11,
      "full_answer_rate_percent": 84.61538461538461
    },
    "completed_unscored": 1,
    "unreviewed": 0,
    "noncompliant": 12
  },
  "GO": {
    "planned": 30,
    "raw": {
      "n": 28,
      "macro_Item_F1_exact": "274318/378525",
      "macro_Item_F1_percent": 72.47024635096757,
      "full_answers": 14,
      "full_answer_rate_percent": 50.0
    },
    "reviewed_compliant": {
      "n": 17,
      "macro_Item_F1_exact": "159253/196350",
      "macro_Item_F1_percent": 81.10669722434429,
      "full_answers": 11,
      "full_answer_rate_percent": 64.70588235294117
    },
    "compliant_with_access_confounds": 5,
    "compliant_without_reported_access_confounds": {
      "n": 12,
      "macro_Item_F1_exact": "208/225",
      "macro_Item_F1_percent": 92.44444444444444,
      "full_answers": 10,
      "full_answer_rate_percent": 83.33333333333333
    },
    "completed_unscored": 2,
    "unreviewed": 0,
    "noncompliant": 11
  }
}
```

逐次原始回答、来源轨迹、评分与审查在runs中；完整机器可读结果见results.json和scores.csv。
