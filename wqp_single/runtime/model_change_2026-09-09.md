# 后续盲测切换 GPT-5.6 Sol / medium

日期：2026-09-09。用户在查看GPT-6难度结果后要求调整盲测模型。本次更新运行默认值、请求/实际模型核对和后续执行提示；没有启动新模型测试，不改变r03参考答案、历史作答、已结束campaign或已使用的修订额度。

## 已有结果

r03的4次内容盲解、2次捷径均完整正确；4次新旧筛选及12次确认也全部匹配各自原oracle。确认阶段新旧CG/GO各3次全对，Item-F1、Row-F1、P.O.A.均为1，新减旧差值为0。已记录35次GPT-6/high工作会话，34次正常完成、1次早期环境错误。详见[原报告](../report.md)、[难度报告](../comparisons/difficulty_report.md)。

这不是只有模型分数的问题。[r03来源审计](../candidates/wqp_activity_panel_001/r03/private/audit_report.md)已观察到合法官方批量下载及本地SQL/JavaScript解法：公开题面足以预先确定下载参数，后续所谓检索依赖可本地计算。原833次撤回还可依据支持变化缩减为51次，再筛至5次关键变化。事实答案可复算，但严格SGR结构未成立。

旧waterquality_004的参考字段可以核对，公开分段/选站规则却不唯一，有具体合格替代站。7/8次旧题运行遇到公开基准题面/格式片段，已检查内容未见gold答案行，不能说已证实答案泄露。详见[旧题复核](../comparisons/old_pair_review.md)与[暴露检查](../comparisons/public_exposure_findings.md)。这些限制在换模型后仍然存在。

## 后续角色配置

| 角色 | 模型 | effort |
| --- | --- | --- |
| 构造、参考解、证据审计与裁决 | gpt-6-astra | high |
| CG/GO内容盲解、盲捷径测试 | gpt-5.6-sol | medium |
| 新题及旧WQP对照的筛选、确认 | gpt-5.6-sol | medium |

运行入口[run.py](run.py)对普通盲解采用新的默认值；可用`--model`、`--effort`显式指定。审计入口[audit_run.py](audit_run.py)保留GPT-6/high；带私有审计资产的调用使用审计角色规则。模型选择不放进公开题面，也不向盲解者透露当前是在做难度筛选。

每次生成的solver.config.toml、CLI参数、run.json和会话账本记录一致的请求模型/effort；[verify_run.py](verify_run.py)再与实际turn_context交叉核对。工具模板中的历史GPT-6默认值供审计使用，普通盲解会生成替换模型两项后的本次配置。保留原生网页、JavaScript、WQP数据工具、只读沙箱和读取隔离，不随模型变更缩短时间或删减工具。

新批次计划应显式写入`model: gpt-5.6-sol`和`effort: medium`；[run_batch.py](run_batch.py)将其传给运行器。旧配置复现应显式指定`--model gpt-6-astra --effort high`。使用新输出目录，不能重用已完成计划的结果路径或覆盖历史成绩。

## 结论边界与接续

- 原GPT-6比较方案和成绩不改写。模型变更是在看过成绩后的研究选择，不能称为旧实验的预定配置。
- 要比较“新题比旧题难”，双方都须在Sol/medium及相同工具、预算下重新测量，不能拿Sol新题分数减GPT-6旧题分数。
- 如继续测r03，先在独立比较目录记录本轮题目版本、试次数与失败规则；现有检索结构及旧对照问题未解决时，只作受限诊断。Sol失败不能证明SGR结构合格，也不能改写“未证明对GPT-6更难”。
- 本次没有重启结束的campaign、延长原预算、追加构造修订或生成Sol分数。真实账户访问、Sol下工具行为与最终结构化作答仍需实际运行核验；离线配置检查不替代这一步。

官方OpenAI Docs已核验模型ID为`gpt-5.6-sol`、支持medium及结构化输出和工具调用；本机模型缓存也列出medium，但缓存不证明账户调用成功。[官方模型页](https://developers.openai.com/api/docs/models/gpt-5.6-sol)。沿用Codex CLI，显式指定模型与推理档位，不改认证或请求端点。[官方配置说明](https://learn.chatgpt.com/docs/config-file/config-reference)、[模型迁移说明](https://developers.openai.com/api/docs/guides/upgrading-to-gpt-5p6-sol)。

## 本次离线验证

- `test_model_config.py`的11项测试通过：Sol/medium盲解默认、GPT-6/high审计保留、显式旧配置、TOML其他项不变、四类模型证据不一致拒绝、沿用每次历史评分器。
- 只读核对历史r03/r-615ba2d60939的metadata、invocation、TOML和turn_context，新验证逻辑接受实际GPT-6/high证据；没有重写该运行的verification或得分。
- 两个使用模拟工作进程的批处理检查通过：新旧任务均收到Sol/medium；第一项发生verification_failed时退出2且不启动后项。没有调用真实工作进程。
- 改动Python语法、CLI帮助及61处相关Markdown本地链接检查通过。真实Sol运行及其工具输出尚未验证。

复查模型配置测试，不调用模型：

```sh
python3 -m unittest discover -s construction_pipeline/wqp_single/runtime -p test_model_config.py -v
```
