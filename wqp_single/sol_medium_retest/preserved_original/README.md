# 单个 WQP 候选：构造、验证与难度比较

最终状态：**难题构造目标未完成，已停止本候选。** r03参考内容经独立审计和裁决核验；四次内容盲解、两次捷径、四次新旧筛选和十二次新旧确认均匹配各自原oracle。新旧确认均值均1、差值0，没有更难证据；候选保持content_validated / difficulty=inconclusive，不标auto_validated。两次实质修订已用尽，实际启动35/60个模型会话。

2026-09-09配置更新：后续普通盲解、盲捷径和新旧对照默认改为GPT-5.6 Sol/medium，构造及证据审计继续GPT-6/high。原35次运行与上述结论保留；本次没有启动Sol重测。详见[模型变更与后续协议](runtime/model_change_2026-09-09.md)。

## 主要材料

- [构造与验证报告](report.md)；[工作记录](progress.md)；[实际模型会话账本](session_ledger.jsonl)；[汇总用量](run_accounting.json)。
- [r03英文CG](candidates/wqp_activity_panel_001/r03/public/cg.md)；[r03英文GO](candidates/wqp_activity_panel_001/r03/public/go.md)。
- [r03候选摘要](candidates/wqp_activity_panel_001/r03/candidate.json)；[CG/GO语义对齐](candidates/wqp_activity_panel_001/r03/private/pair_alignment.json)；[评分规范](candidates/wqp_activity_panel_001/r03/private/scoring_rules.json)。
- [参考答案](candidates/wqp_activity_panel_001/r03/private/reference/oracle.psv)；[参考说明](candidates/wqp_activity_panel_001/r03/private/reference/reference_report.md)；[完整情景纳排](candidates/wqp_activity_panel_001/r03/private/reference/scenario_ledger.jsonl)；[逐字段证据](candidates/wqp_activity_panel_001/r03/private/field_evidence.jsonl)。
- [原始来源索引](candidates/wqp_activity_panel_001/r03/private/source_manifest.json)；[重算程序](candidates/wqp_activity_panel_001/r03/private/reference/solve_reference.py)；[独立SQL](candidates/wqp_activity_panel_001/r03/private/reference/independent_check.sql)；[实际反事实](candidates/wqp_activity_panel_001/r03/private/reference/counterfactuals.json)。
- [独立来源审计](candidates/wqp_activity_panel_001/r03/private/audit_report.md)；[独立测量前裁决](candidates/wqp_activity_panel_001/r03/private/decision.json)；[收尾裁决](candidates/wqp_activity_panel_001/r03/private/closure_decision.json)。
- [最后修订依据](candidates/wqp_activity_panel_001/r03/private/repair_report.md)；[r01来源审计](candidates/wqp_activity_panel_001/r01/private/audit_report.md)；[r02开发成绩](candidates/wqp_activity_panel_001/r02/private/content_runs_report.md)。
- [单题难度报告](comparisons/difficulty_report.md)；[预定单题比较方案](comparisons/analysis_plan.json)；[旧004参考核验与限制](comparisons/old_pair_review.md)。

## 离线重算（不启动模型）

从仓库目录运行：

```sh
python3 construction_pipeline/wqp_single/candidates/wqp_activity_panel_001/r03/private/reference/solve_reference.py
python3 construction_pipeline/scripts/prepare.py validate-candidate --candidate construction_pipeline/wqp_single/candidates/wqp_activity_panel_001/r03/candidate.json --check-files
python3 construction_pipeline/wqp_single/runtime/verify_run.py <实际运行的绝对目录>
python3 construction_pipeline/wqp_single/runtime/review_content_runs.py --revision r03
python3 construction_pipeline/wqp_single/runtime/summarize_runs.py --write
python3 construction_pipeline/wqp_single/comparisons/analyze_difficulty.py
python3 construction_pipeline/wqp_single/runtime/verify_delivery.py
```

参考程序从保存的原始CSV/ZIP重建面板、完整站年、全局窗口及全部独立撤回情景；不调用模型。原始响应已复制在各revision内，不依赖跨revision符号链接。实际评分使用每次运行保留的实现副本复算。

## 复跑独立模型尝试

使用新的、不存在的输出目录。控制端gold/rules不会复制进盲解环境；只公开题面、日期、solver提示和统一输出schema。下例显式指定新的Sol/medium；如复现原GPT-6配置，改为`--model gpt-6-astra --effort high`。新旧题比较须使用相同模型、工具和预算。

```sh
python3 construction_pipeline/wqp_single/runtime/run.py --model gpt-5.6-sol --effort medium --public construction_pipeline/wqp_single/candidates/wqp_activity_panel_001/r03/public/cg.json --stage construction_pipeline/prompts/04_blind_solver.md --gold construction_pipeline/wqp_single/candidates/wqp_activity_panel_001/r03/private/reference/oracle.psv --rules construction_pipeline/wqp_single/candidates/wqp_activity_panel_001/r03/private/scoring_rules.json --out <新的绝对输出目录> --label sol_medium_diagnostic_CG
```

GO将public/cg.json替换为public/go.json；合法捷径尝试将阶段提示替换为05_shortcut_attacker.md。本轮已停止，以上模型复跑命令仅供用户后续明确授权时使用，不在本次自动执行。不得暗中重设campaign.json的60会话/24小时预算或覆盖已有目录。

## 实际执行与停止位置

内容/捷径采用最多两次并行，新旧对照采用最多四次并行，审计与裁决按依赖顺序。四次筛选与十二次确认已全部完成，没有因分数追加试次。旧004公开选站口径不唯一，原题面与oracle原样保留；7/8旧题对照出现公开题面片段，检查的内容未见gold行，仍记录暴露限制。详见难度报告及comparisons/public_exposure_findings.md。

r01的完整独立下载文件曾因tmpfs归档方式失败而丢失，实际工具事件/SQL/答案和控制端源响应仍在；该历史缺口明确记录。r02开始的新归档方式已在实际隔离容器和真实模型运行中验证成功。无宿主目录挂载、无历史会话恢复、无任意shell读取工具。

最终交付检查：[delivery_verification.json](delivery_verification.json)。该检查只确认记录、引用、隔离/评分复核及新旧环境一致性，不证明题目更难。
