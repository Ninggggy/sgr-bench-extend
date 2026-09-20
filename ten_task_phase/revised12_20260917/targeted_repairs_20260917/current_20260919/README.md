# 当前配置入口

[协议](protocol.md) · [配置](campaign.json) · [状态](state.json) · [盲测提示](blind.md) · [获取规则](retrieval_policy.md)

历史目录不再作为新试次的配置来源，不修改历史成绩或按新规则重判。此目录继承同一轮用量，不是追加额度。当前六题来源核查中，无新试次。旧五题配置见 *.before_six_tasks；本轮完整目标见 goal-objective.md。

执行用runtime/run.py，指定本目录campaign.json、session_ledger.jsonl和blind.md，使用public_web配置。输入/参考/评分/CG/GO试次必须先按项目登记；不能直接使用旧题重跑。审查提示为audit.md，模型固定Astra/medium。执行前使用runtime/check_current_repairs.py检查当前配置；该检查不调用模型或外部资源。

后续已登记试次的命令格式（占位参数须替换成已登记的新版本文件；这不是启动指令）：

```sh
python3 construction_pipeline/ten_task_phase/runtime/run.py \
  --campaign construction_pipeline/ten_task_phase/revised12_20260917/targeted_repairs_20260917/current_20260919/campaign.json \
  --ledger construction_pipeline/ten_task_phase/revised12_20260917/targeted_repairs_20260917/current_20260919/session_ledger.jsonl \
  --stage construction_pipeline/ten_task_phase/revised12_20260917/targeted_repairs_20260917/current_20260919/blind.md \
  --public <registered-public.json> --gold <registered-oracle.psv> \
  --rules <registered-rules.json> --job-metadata <registered-job.json> \
  --out <new-run-directory> --role blind --purpose development
```

运行器自动按campaign选择public_web，无须从旧webonly目录复制配置；显式配置若不一致会报错。上述接口配置已离线检查，尚未进行在线试跑。盲测不需要浏览器插件，不将缺少插件作为待办或阻塞。

六题进度见 [work_notes.md](work_notes.md)，当前汇总见 [results.json](results.json)。离线检查：62 项通过（包含 70% 精确边界、无效/缺测、历史预算、防重抽、两面登记、首对预留）。这些检查不证明来源完整或题目达标。

六题开发盲测必须提供 plan_path，指向 development_rounds 登记。每轮包含 candidate_id/revision/protocol_version/registered_at、model/effort/tool_profile、CG/GO/reference/recompute/rules 相对文件路径，以及两个独立 slots（run_id/run_dir/variant/trial=1）。原始轨迹审查需明确 verdict、capability_score_eligible、access_confounded、format_confounded 和 answer_exposure_review；本轮 answer_exposure_review 用 passed/pending/failed，详细依据另写 diagnosis。未审查值不能计为成功。

登记时还须保存 `registered_contents`，包含 CG、GO、reference、recompute、rules 五份 UTF-8 原文；可调用 runtime/campaign_runtime.py 的 `development_contents(plan_dir, pair)` 生成。启动任一面时逐项作普通文本比对，并与已准备另一面保存的登记记录比对；执行题面、参考及规则来自已检查副本。这些私有登记内容不得放入盲测 public 目录。没有新增 hash 或冻结 contract。
