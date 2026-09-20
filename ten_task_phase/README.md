# 新增10底题阶段

当前为部分交付，目标10个底题/20条任务记录；已收录1个底题（arXiv r02），两份JSONL各1条，尚缺9个底题。最新清单、精确均值和成本见 DELIVERY.md 与 exports/admission_report.json。

计划/规则：campaign.json、progress.md、comparisons/analysis_plan.json。全部模型会话记session_ledger.jsonl，恢复不重置预算。原WQP及旧Sol目录不改。主控、工程子任务也计费；本地纯计算不计模型会话。

## 恢复与复算

2026-09-10 用户明确更新总控计时口径：总控持续到原300次/48小时阶段边界，不受单个6000秒工作会话限制；构造、审计、盲解等工作会话仍执行6000秒及无实质进展3000秒限制。原截止为2026-09-11T09:30:08Z（北京时间9月11日17:30:08），历史超时记录保留。当前原生持续目标为active，不建立定时自动化，不因一个工作单结束要求用户再次“继续”。

当前恢复总控为账本第81次真实持续会话；上下文压缩不另记新会话。复测预留按未收录题数维护，目前尚缺9题，至少54次；失败轮不能抵扣剩余题所需复测。最新接续证据见research/resume_2026-09-10_review.md。

先读 progress.md、run_accounting.json 和 comparisons/analysis_plan.json，再检查实际运行的容器与 run.json。预算起点为 2026-09-09T09:30:08Z，恢复不重置。盲解统一日期为 2026-09-09。当前使用已经登记的 ten-task-v1 协议；恢复时不要重建或替换盲解镜像、工具、提示和评分程序。以下建设命令是历史入口，不是要求恢复时重复执行。

收录与导出按实际六次独立普通复测、真实模型证据、审计报告和精确 Item-F1 分数重新计算：

```sh
python3 construction_pipeline/ten_task_phase/runtime/admission.py export --manifest construction_pipeline/ten_task_phase/admission_manifest.json --out construction_pipeline/ten_task_phase/exports
python3 construction_pipeline/ten_task_phase/runtime/account.py --out construction_pipeline/ten_task_phase/run_accounting.json
```

exports/constraint.jsonl 和 exports/goal.jsonl 只含符合两组分别严格低于 70% 及质量要求的底题。少于 10 题为部分交付，零行不是完成。金额无法从服务方取得，保持 null，实际会话和返回 token 用量按运行记录报告，不能记作零成本。

## 历史建设入口（已完成，不重复）

从项目根目录执行：

```sh
python3 -m unittest discover -s construction_pipeline/ten_task_phase/runtime -p 'test_*.py'
```

共享KEGG限速服务只返回时间许可，不提供文件、证据或认证信息。旧镜像作为基础，保留证书及隔离措施。正在运行的limiter无需重复启动；本次本地端口18763。

构造入口已实际启动：

```sh
python3 construction_pipeline/ten_task_phase/runtime/run.py --campaign construction_pipeline/ten_task_phase/campaign.json --ledger construction_pipeline/ten_task_phase/session_ledger.jsonl --role construction --purpose construction --model gpt-6-astra --effort high --public construction_pipeline/ten_task_phase/inputs/chemexpo.json --stage construction_pipeline/ten_task_phase/inputs/construct.md --out construction_pipeline/ten_task_phase/runs/r-chemexpo-explore-01 --label chemexpo-explore-01
```

上条已执行，不要重新运行或覆盖输出目录。恢复先查run.json/真实容器/账本，再按运行器恢复入口处理。候选定稿且内容审计成立后才预登记收录复测六次；开发和攻击分数不能作为收录分数。具体接口见 runtime/README_admission.md。已有注册轮不能重复注册或挑选低分替换；arXiv r02 轮明确不自动补替换试次。

本地导出不等于发布。收录成绩参与了筛选，不代表无偏评估。没有实际专家审查时human_validation=not_performed。
