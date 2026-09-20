# 收录与导出接口

运行入口为 `admission.py check --manifest <manifest.json>` 和 `admission.py export --manifest <manifest.json> --out <directory>`。程序只读原始题面、参考答案、评分规则、账本、普通测试计划、运行轨迹和审计证据；导出命令写两份 JSONL 及 admission_report.json。

manifest 指向 campaign、ledger、analysis_plan 和候选 candidate.json。每个底题及协议版本在 analysis_plan.admission_rounds 中只能有一轮，恰好含 CG/GO 各三个预定槽；六个 run_id、trial、label、路径不可互换。必须在任何槽启动前登记，并在内容及实质错误审计完成后登记。运行器同时保存当时的登记记录。真实基础设施故障遵循该轮事前修复规则，禁止追加未预定试次；arXiv r02 轮规定零自动替换，故障即不可判定。

程序逐项核对请求参数、实际命令、配置和真实 turn_context 中 Sol/medium 或 Astra/medium，独立 Docker 会话和实际镜像、统一工具、日期和预算、题面及 oracle/rules 版本，以及每个运行的实际完成和可解析答案。全阶段已启动的 Sol 运行均须符合登记协议，不能只对收录运行检查工具。

分数从原始回答和现有确定性评分程序复算，以整数 correct_fields 与 item_denominator 构造 Fraction。每组均值为三次精确 Item-F1 的和除以三；CG 和 GO 都必须严格小于 Fraction(7, 10)。等于 70%、任一组达到阈值、缺少试次或解析失败、混版本、非普通复测、重复会话、审计未通过均不可导出。边界与异常行为的普通测试见 test_admission.py。

当前报告遇到未完成槽时保持 inconclusive，已验证的部分试次仍保留；完整六次原始记录始终以 analysis_plan、session_ledger 和 runs 为准，不补零。最多收录十个底题，同一构造方法最多两个，原五十题不计入；2026-09-10用户明确指定 WQP r03 与 arxiv_historical_title_002/r03 例外计入，依据记录在 admission_manifest.json 与 campaign.json。该例外仅适用上述两个明确版本，报告保留 standard_assessment，导出标记 user_designated_exception，不伪造标准六次复测或SGR通过。少于十个时 partial_delivery=true。

所有收录复测都是参与挑题的筛选成绩，不是无偏独立评估或统计认证。导出标记 content_validated、difficulty=screened，并据实保留 human_validation；不自动宣称 auto_validated。

2026-09-13用户调整：后续非盲GPT-6工作为medium；历史high运行按原实际记录核验，正式收录审计按campaign登记的生效时间区分。盲解工具、提示、评分、日期、隔离和Sol/medium保持原协议。
