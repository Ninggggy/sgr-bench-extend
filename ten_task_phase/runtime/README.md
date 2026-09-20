# 十题阶段运行器

本目录复用旧 WQP 隔离运行器，旧 campaign、运行、评分和工具文件不修改。模型调用采用现有凭据，不安装或启动付费服务。新镜像为 `sgr-ten-task-codex:local`；Dockerfile 仅在既有镜像内替换通用数据工具。

## 单次运行

必须显式给出 `--campaign`、`--ledger` 和 `--purpose`。campaign 与 ledger 必须属于 `ten_task_phase/`。公开输入只含 `instruction`、`output_format`，可含日期；运行时统一替换为 campaign.current_date。

```sh
python3 construction_pipeline/ten_task_phase/runtime/run.py \
  --campaign construction_pipeline/ten_task_phase/campaign.json \
  --ledger construction_pipeline/ten_task_phase/session_ledger.jsonl \
  --role construction --purpose construction \
  --public path/to/request.json --stage path/to/stage.md \
  --out construction_pipeline/ten_task_phase/runs/r-example --label example
```

角色 `blind` 限定 Sol/medium，用途为 `development`、`attack`、`admission`、`comparison`；角色 `construction`、`audit` 限定 Astra/medium，并分别使用同名用途。实际请求、启动 argv、复制的 TOML 和真实 turn_context 均核对。每次创建新容器，不 resume、不 fork、不挂载宿主目录；继承只读根目录、tmpfs、禁用 shell/apps/delegation 的工具配置。`--tools-config` 若指定，渲染后必须与本目录工具配置一致。

非盲阶段默认使用 `construction_result.schema.json`，除原阶段报告字段外，必须输出 `files:[{"path":"relative/path","content":"actual UTF-8 content"}]`。每个 artifacts 声明必须存在对应 files 内容；控制端落地至 `stage_assets/`，复核内容相等、JSON 可解析、Python 可编译。仅声称写好了文件不算产物。保存 Python 不会在控制端自动执行，事实和参考计算仍由后续审计检查。

`--assets` 仅允许非盲角色；使用平铺、普通、安全文件名的显式私有包。盲解禁止私有包。所有模型仍使用同一套工具。

## 收录复测

`--purpose admission --job-metadata path.json` 要求 `candidate_id,revision,protocol_version,variant,trial,run_id,plan_path`，stage 自动固定为 `admission_retest`。run_id 必须等于输出目录名。启动前从 `plan_path` 的 admission_rounds 读取唯一身份的完整六槽计划，核对 CG/GO 各三个试次、登记时刻以及本次 slot 的 run_id、variant、trial、label、run_dir；将该 round 原样保存为 `admission_registration.json`。最终是否收录由 admission.py 完成，运行器不根据低分提前结束。

## 预算与恢复

账本加锁分配会话，最多 300 次、4 个同时运行工作会话，时间窗口不超过原始 48 小时；分配检查结束标志和截止时刻。每次最大 6000 秒、无实质进展最大 3000 秒，并受 campaign 更低设定约束。`reserved_pending_sessions` 可显式保留尚未完成的收录复测调用数；若未设置，则从 reserved_sessions 目标预留中扣除已经分配的 admission/comparison 会话。控制端应在淘汰旧版本、登记新一轮后更新实际未完成预留。

批处理必须显式传 `--campaign --ledger --plan`；检查 plan 中路径的一致性。已完成结果需要重新核验产物，活跃运行不重复启动；空目录、失败目录和缺资产目录不视为完成。已结束模型调用不会被自动重跑。

控制进程意外中断时，使用 `recover_run.py RUN_DIR` 回收原容器的 sessions、公开下载与输出，不启动模型，也不把中断结果伪记为有效复测。若原模型还活跃，保留它；仅在已决定停止原基础设施故障尝试时使用 `--stop-running`。回收后保留原容器供核验，主控可在确认文件齐全后移除。正常运行器出现异常会先尝试归档，再删除容器；归档失败时保留容器并记录名称。

重试需要新目录与 `--retry-approval`，该文件声明 previous_run、classification=`infrastructure_failure` 和 evidence。保持同一题目版本、题面、用途和试次身份，最多一次修复；不能重试 completed、invalid_output 或活跃尝试，也不能对同一失败安排多个替代。收录槽的替代运行还必须受预登记计划与 admission 检查的明确规则支持；当前默认入口不会自动改动已登记槽来接纳新 run_id。

## 离线验证

```sh
python3 -m unittest discover -s construction_pipeline/ten_task_phase/runtime -p 'test_*.py'
```

验证范围包括模型四源分歧、资产内容/路径、阶段 schema、预算、预留、日期、状态恢复、有限重试，以及本目录评分和数据工具测试。测试不启动模型；实际容器与真实会话验收以保存的运行证据为准。

2026-09-13用户调整：后续非盲GPT-6工作为medium；历史high运行按原实际记录核验，正式收录审计按campaign登记的生效时间区分。盲解工具、提示、评分、日期、隔离和Sol/medium保持原协议。

当前六题修订的用户更新：`max_seconds_per_session: null` 表示取消单工作会话总时长上限；运行器跳过该项超时判断，仍执行 `stall_seconds` 和显式项目截止日期。历史批次保留各自既有数值上限。
