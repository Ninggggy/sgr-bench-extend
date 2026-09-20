# 严格收录与本地导出

`admission.py` 从真实模型运行目录重算分数。只导出内容审计成立、CG 和 GO 各三个预定 Item-F1 均值严格低于 7/10 的底题；使用 `Fraction(2 * correct_fields, item_denominator)`，阈值比较不使用浮点数。未满十题输出 `partial_delivery: true`。所有成绩均为用于收录的筛选成绩。

```sh
python3 construction_pipeline/ten_task_phase/runtime/admission.py check --manifest construction_pipeline/ten_task_phase/admission_manifest.json
python3 construction_pipeline/ten_task_phase/runtime/admission.py export --manifest construction_pipeline/ten_task_phase/admission_manifest.json --out construction_pipeline/ten_task_phase/exports
python3 -m unittest discover -s construction_pipeline/ten_task_phase/runtime -p test_admission.py -v
```

上述 manifest 需由控制端在产生真实候选后建立。测试仅使用临时合成夹具，不构成真实候选或研究成绩。

## Manifest

所有路径相对包含该路径字段的计划/manifest 文件目录；candidate.private 路径相对 candidate.json 目录。顶层示例：

```json
{
  "campaign_path": "campaign.json",
  "plan_path": "comparisons/analysis_plan.json",
  "ledger_path": "session_ledger.jsonl",
  "candidates": [
    {"candidate_path": "candidates/new_candidate/r01/candidate.json", "family": "identity_dependent_expansion"}
  ]
}
```

候选使用 `construction_pipeline/schemas/candidate.schema.json` 已有字段；收录须 `status=content_validated`、`validation.content=passed`。CG/GO 公开输出规则必须相等。证据清单、oracle、参考程序和状态图须实际存在且非空。程序允许原12生态的规范名称；当前完整集合见 `ECOSYSTEMS`。原50 task_id、`wqp_activity_panel_001` revision 3 不计入。

## 批次统一协议

开始本批次任何盲解前，在campaign.json登记实际协议文件与镜像：

```json
{
  "protocol_assets": {
    "registered_at": "2026-09-09T11:00:00+00:00",
    "solver_config_path": "protocol/solver.config.toml",
    "scorer_path": "protocol/score.py",
    "data_tools_path": "protocol/data_tools.py",
    "image_id": "填写本批实际 Docker 镜像 ID"
  }
}
```

路径相对campaign.json；配置必须是实际 Sol/medium 配置。工具/评分文件为本批普通协议资产，不新增hash。程序逐字对照每个run保存的配置、评分代码和数据工具代码，核对实际镜像及注册时间。它会检查整个账本中已经启动的所有Sol盲解，包括开发、攻击、旧对照和失败模型尝试；跨题或新旧工具不一致时拒绝导出。启动前基础设施失败且无invocation记录的项保留账本，不冒称已执行盲解。

## 普通测试计划

复用 `comparisons/analysis_plan.json` 的 `admission_rounds` 数组。每个 candidate_id/revision/protocol_version 只能有一个 round。六个 slot 必须在第一个复测会话前全部登记，trial 严格为 CG 1/2/3 和 GO 1/2/3。示例仅展示一个 slot，实际必须六个：

```json
{
  "protocol_version": "ten-task-v1",
  "admission_rounds": [
    {
      "candidate_id": "new_candidate",
      "revision": 1,
      "protocol_version": "ten-task-v1",
      "registered_at": "2026-09-09T12:00:00+00:00",
      "rules_path": "../candidates/new_candidate/r01/rules.json",
      "audit_paths": ["../candidates/new_candidate/r01/audit_run"],
      "slots": [
        {"variant": "CG", "trial": 1, "run_id": "r-cg1", "run_dir": "../candidates/new_candidate/r01/runs/r-cg1", "label": "admission_new_candidate_r01_CG_1"}
      ]
    }
  ]
}
```

运行器用 `--job-metadata` 接收 candidate_id/revision/protocol_version/stage/variant/trial/run_id/plan_path；stage 必须 `admission_retest`，plan_path 是上述完整计划路径。启动时读取 round，保存普通 `admission_registration.json` 运行记录。导出核对各运行保存的完整 round 与当前 round 相等、登记时间早于实际启动。后改 run_id、label、版本或删掉高分替换低分都会被拒绝。不得改写已执行 round；追加其他候选的 round 不影响已有记录。

当前程序保守地不接受替换试次：基础设施故障会使该版本保持不可判定。即使campaign允许一次基础设施修复，也不能通过修改原slot或增加未预定run绕过；若实际需要替换，须先实现并测试预先指定的 primary/retry slot 与真实故障裁决协议，原失败运行及成本必须保留。模型错误、空答案和可评分部分答案不能作为重试原因。

## 审计输出

`audit_paths` 是实际 Astra/medium 运行目录。优先使用默认非盲输出 `files[]`，包含唯一文件 `audit.json`；程序逐字核对其 `content` 与已回收 `stage_assets/audit.json`。也兼容独立 schema 直接输出下面的顶层结构：

```json
{
  "candidate_id": "new_candidate",
  "revision": 1,
  "protocol_version": "ten-task-v1",
  "checks": {
    "content": {"verdict": "pass", "evidence_paths": ["stage_assets/content_review.md"]},
    "sgr": {"verdict": "pass", "evidence_paths": ["stage_assets/sgr_review.md"]},
    "semantic_alignment": {"verdict": "pass", "evidence_paths": ["stage_assets/alignment.md"]},
    "substantive_errors_cg": {
      "verdict": "pass", "error_category": "scope", "substantive_progress": true,
      "explanation": "填写该版本CG运行中真实且可复查的实质错误与进展。",
      "evidence_paths": ["stage_assets/cg_error_review.md"]
    },
    "substantive_errors_go": {
      "verdict": "pass", "error_category": "identity", "substantive_progress": true,
      "explanation": "填写该版本GO运行中真实且可复查的实质错误与进展。",
      "evidence_paths": ["stage_assets/go_error_review.md"]
    }
  }
}
```

每个 check 恰由一份审计负责，可将五项分散在多份独立审计中，不接受重叠或相互矛盾的同名check。审计全部完成后才登记复测。evidence_paths 相对审计 run 目录，必须引用实际非空文件；正文需记录领域/身份/范围/检索决策错误、实质进展，并复查两次普通开发盲解和一次攻击是否齐全、独立参考核对、全集/纳排依据、真实检索依赖反例、批量合法路径、逐字段来源和语义对齐。`error_category` 只允许 `domain/identity/scope/retrieval_decision`。程序核验实际 Astra/medium 四源及输出证据关联，无法代替审计者判断科学内容是否正确。不得把自动审计写成人类专家验证。

## 核验与产物

每个有效复测必须有真实 completed 事件、completed 状态、退出码0、无运行错误，及 request / invocation / TOML / 实际 turn_context 四源匹配的 Sol/medium。实际会话ID和Docker容器不得重复；读取隔离探针、只读根文件系统、无bind mount、移除权限、no-new-privileges 均须成立。六次同日期、同预算、同配置、同实际镜像与保存评分实现。公开输入须逐字段等于同版本单个题面加统一日期，原始答案须逐字对应 result.final_answer。

每个run的 `implementation/score.py` 按该run保存的 rules/oracle/answer 重新计算，核对完整 scores.json 和 field_differences.json；有声明的 `record_separator` 按保存规则传给解析器。NA、非数值、解析失败、缺文件、分数与计数不一致、版本/计划不一致均不可判定，不补零。可合法评分的 `NONE` 空输出仍按原评分规则处理。

导出 `constraint.jsonl`、`goal.jsonl` 和 `admission_report.json`。GO 的 task_id 为 CG 底题 ID 加 `-g` 后缀。JSONL保留原发布格式的 task_id/domain/autonomy_type/oracle_output_cardinality/instruction/start_url/output_format/oracle_answer/metadata/rubric 字段。报告保留每个底题六run、完整计数、Item-F1、Row-F1、P.O.A.、完整正确指标、精确分数、两组精确均值、模型证据与审计结论。符合数超过10、重复底题版本或同家族超过2时拒绝整个导出，避免静默截取。未达标候选保留在报告中，不进入JSONL。

2026-09-13用户调整：后续非盲GPT-6工作为medium；历史high运行按原实际记录核验，正式收录审计按campaign登记的生效时间区分。盲解工具、提示、评分、日期、隔离和Sol/medium保持原协议。
