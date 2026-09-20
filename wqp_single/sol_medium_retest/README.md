# GPT-5.6 Sol / medium 独立诊断

本轮已完成4次筛选和12次确认，16次模型会话，未重试。新题确认完整交付匹配2/6，旧题6/6；新题另1次解析失败不补零，旧题确认3/6次实际gold暴露。详见[最终报告](report.md)。

本目录属于2026-09-09新授权的固定重测，目标只覆盖现有wqp_activity_panel_001/r03和waterquality_004的CG/GO。原GPT-6实验及难题目标未完成结论保持原样。

- 预定计划：[analysis_plan.json](analysis_plan.json)；独立预算：[campaign.json](campaign.json)；实际会话：[session_ledger.jsonl](session_ledger.jsonl)。
- 原样公开输入：[inputs/](inputs/)；仅控制端参考：[controller_reference/](controller_reference/)。每次盲解仅得到公开题面、实际日期、相同阶段提示与统一schema。
- 逐次原始输入、输出、工具、下载、评分和隔离证据均在[runs/](runs/)各独立目录。
- [工作记录](progress.md)；[逐次与等权汇总](summary.md)；[机器可读成绩](summary.json)；[模型核验](model_verification.json)。[最终解读](report.md)；[错误分类](error_analysis.md)；[暴露检查](public_exposure_findings.md)。

离线复算（不启动模型），从项目根目录运行：

```sh
python3 construction_pipeline/wqp_single/sol_medium_retest/recompute.py
```

逐次评分复核使用该次保存的实现：

```sh
python3 <运行绝对目录>/implementation/verify_run.py <运行绝对目录>
python3 <运行绝对目录>/implementation/score.py --answer <运行绝对目录>/answer.txt --gold <运行绝对目录>/controller_scoring/oracle.psv --rules <运行绝对目录>/controller_scoring/rules.json --out <新的评分目录>
```

实际模型运行命令为execute.py first、screening_rest、confirmation（按依赖顺序）；已有目录不会重跑，不创建追加试次。结束的campaign拒绝调用。交付后不自动开启新campaign。

已知限制继续适用：r03可合法批量取数后本地求解，严格SGR结构未成立；旧004公开选站不唯一；需区分本轮公开基准题面暴露与真正gold泄露。每题面确认3次是小规模诊断，不能外推GPT-6、其他底题或旧50题。
