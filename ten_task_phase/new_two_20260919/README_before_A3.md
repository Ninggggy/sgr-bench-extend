> 2026-09-19 继续执行结果：目标未完成，仍为 0/2 达标。本轮追加机会筛查没有形成满足入选条件的第三版，没有新增盲测或独立审查。审查额度现为 15 次，已用 6 次；盲测额度 12 次，已用 6 次；A、B 各已用 2/3 版。见 [本轮筛查](exploration/resumed_screening.md) 与 [本轮成本](resumed_costs.json)。下文保留先前版本和先前停止时的历史记录；历史“审查 6 次用尽”不代表当前额度。

> 预算更新（2026-09-19T09:49:48.081053+00:00）：用户将审查总上限由6次提高到15次；已用6次，剩余9次。盲测仍为6/12，A、B各已用2/3个版本，历史计数与成绩不变。此前因审查额度耗尽停止的记录为历史状态；本次预算修改未新增试次，尚未恢复运行。

# 两题独立计划交付索引

**目标未完成；已按内容审查额度用尽规则停止。** 最新汇总见 [REPORT.md](REPORT.md)；精确结果见各运行目录的 exact_report.json，原始确定性分数见 scoring/scores.json。

- [A v1：世界遗产边界批准例外](A/v1/reference.md)：完整参考、13项纳排、原件定位、重算程序、CG/GO及审查修复；两面均100%。
- [A v2：Cabaret返场成员档案](A/v2/reference.md)：完整27人候选、信用分区与角色判断、原始DOM提取重算、CG/GO及审查修复。
- [B v1：DNS缓存诊断](B/v1/reference.md)：未进入盲测；[不采用原因](B/v1/disposition.md)。两次审查均保留、计数。
- [B v2：HTTP技术勘误回移](B/v2/reference.md)：完整14项勘误纳排、三项语义核对、重算与CG/GO；[测试后歧义复核](B/v2/post_test_arbitration.md)。
- [原件探索机会与弃选证据](exploration/opportunities.md)、[公开网页及浏览器证据](evidence/)。
- [独立会话账本](session_ledger.jsonl)、[成对事前登记及原样文本](plan.json)、[成本记录](costs.json)、[最终状态](state.json)。
- [全部原始运行](runs/)：每次包含模型/effort记录、隔离验证、原始工具轨迹、回答、确定性评分或内容审查；盲测另有 trajectory_review.md 与 retrieval_review.json。

独立额度：Sol/medium盲测最多12次，Astra/medium内容审查最多6次；A/B各最多3个实质版本。与六题计划未混用额度或内容。协议标识中的six-repairs仅选择现有public_web兼容实现，不继承其用量、题目或成绩。

复用现有 ../runtime/run.py、score.py。没有新增浏览器盲测工程；浏览器只用于构造端复现核验。每个已登记版本CG/GO各一次，不重抽。所有成绩均为经过开发筛选的单次评估，不能当作无偏最终评估或三次均值正式收录。

重算示例：在仓库工作目录执行 python3 construction_pipeline/ten_task_phase/new_two_20260919/A/v2/recompute.py。四个版本各有recompute.py；都从原始字段或保留原件观察生成答案，不读取oracle.psv。A v2原始DOM路径依赖本目录的evidence，交付时须一起保留。
