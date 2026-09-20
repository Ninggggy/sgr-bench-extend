from pathlib import Path
import datetime as dt,json,subprocess,sys
R=Path(__file__).resolve().parent;now=dt.datetime.now(dt.timezone.utc).isoformat()
summary=json.loads((R/'summary.json').read_text());state=json.loads((R/'state.json').read_text());cost=json.loads((R/'final_costs.json').read_text())
faces={}
for face in ('CG','GO'):
 p=R/'runs'/f'new-two-A-v3-{face}';x=json.loads((p/'exact_report.json').read_text());run=json.loads((p/'run.json').read_text());x.update(usage=run['usage'],elapsed_seconds=run['elapsed_seconds'],run_dir=str(p.relative_to(R)));faces[face]=x
summary['versions']=[x for x in summary['versions'] if not(x['candidate_id']=='A' and x['revision']=='v3')]
summary['versions'].append({'candidate_id':'A','revision':'v3','quality':'passed_preblind_audit_and_postblind_trajectory_review','faces':faces,'qualified':False})
stop='A used all three substantive versions; A v3 CG and GO each valid 80/80. The conjunction of two qualified tasks is impossible within the authorized version limit. All registered pairs completed. B v3 remains unallocated; no claim of exhaustive infeasibility across every possible direction.'
for x in (summary,state):
 x.update(status='uncompleted_A_version_budget_exhausted',goal_completed=False,stopped_at=now,blind_used=8,blind_limit=12,review_used=10,review_limit=15,remaining_blind=4,remaining_reviews=5,unexecuted_registered_slots=0,stop_reason=stop,final_costs='final_costs.json')
 x.pop('resumption_stop_reason',None)
summary['versions_used']={'A':3,'B':2}
state['slots']['A'].update(versions=['v1','v2','v3'],quality='v3_passed',CG='80/80',GO='80/80',passed=False,blind_used=6,review_used=6)
state['current_opportunity']='No active construction; version-limited campaign ended unsuccessfully.'
for name,x in [('summary.json',summary),('state.json',state)]: (R/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
for f in ['REPORT.md','README.md']:
 old=R/f.replace('.md','_before_A3.md')
 if not old.exists():old.write_text((R/f).read_text())
report=f'''# 两题计划：目标未完成

截至 {now}，**0/2 道达标**。A 第三版已通过质量审查，但 CG、GO 均为 80/80；A 的三个实质版本已用完。本计划按版本额度规则停止。不是审查总额度耗尽，也不是单工作会话超时。没有追加题号、重置位置或重复测试。

## 位置总表

|位置及最新版本|质量状态|有效 CG Item-F1|有效 GO Item-F1|双面严格低于 70%|版本|盲测 / 审查|
|---|---|---|---|---|---|---|
|A v3：葡萄牙历史日志的时区库升级影响|参考、配对、公开路径、评分和轨迹通过|80/80|80/80|否|3/3|6 / 6|
|B v2：HTTP 勘误回移|测试后确认共享题意歧义|无（原始 22/24）|无（原始 24/24）|否|2/3|2 / 4|

A v3 两面 Row-F1 均为 16/16，整题全对均为 true；两套偏移字段也均为 8/8。精确验收为 `10×80 < 7×80`，即 `800 < 560`，结果为假。没有四舍五入或对两面取平均。

总用量：**盲测 8/12，审查 10/15**。B 的第三版没有分配；剩余 4 次盲测、5 次审查不能突破 A 的版本上限，也没有为了耗尽额度而继续构造。B 的后续机会尚未达到入选要求，不表示已证明所有其他方向不可行。

## 全部版本

|版本|题材及处置|CG Item-F1 / Row-F1 / 全对|GO Item-F1 / Row-F1 / 全对|
|---|---|---|---|
|A v1|世界遗产边界批准例外；质量通过，难度未达标|14/14；2/2；true|14/14；2/2；true|
|A v2|返场演员身份及角色信用；质量通过，难度未达标|40/40；8/8；true|40/40；8/8；true|
|A v3|时区源文件语义与本地时间逆映射；质量通过，难度未达标|80/80；16/16；true|80/80；16/16；true|
|B v1|DNS 缓存诊断；必要检索依赖不足，未登记盲测|未测，不计零|未测，不计零|
|B v2|HTTP 新旧标准语义；共享歧义使两面验收失效|原始 22/24；4/6；false|原始 24/24；6/6；true|

旧版资产、得分与处置均保留，没有把 B 的无效结果改成低分。所有结果是**经过开发筛选的单次评估**，不是无偏最终评估、三次均值或正式收录。

## 本次新增的实质工作

A v3 的自然问题是迁移没有 UTC 偏移和 fold 标记的葡萄牙历史日志。范围由 2024b 官方国家索引闭合，比较 2024a、2024b 在 1992—1993 年的全部本地时间逆映射差异。三个候选时区完整核对，两个排除，一个产生八个最大区间。

关键判断包括标准时间与 UTC 后缀的换算、基本偏移和夏令时抵消、零/一/两个 UTC 原像、版本中有效记录及最大区间合并。这是新的原始证据和新的判断任务，不是改名、扩表或换措辞。完整原件、逐字段定位、候选纳排和从源文件重算的程序在 [A/v3](A/v3/reference.md)。程序不读取手写参考答案。

四次新增 Astra/medium 审查均计数。前三次发现的具体问题和修复保留；第四次通过。盲测前补足了评分器依赖、明确别名政策、修复空回答/纯分隔符资格判断和整题格式检查，并执行 23 个确定性评分样例（包括恰好 70%）。162 个已保存的边界往返核对通过；它们共享编译后的源语义，只校验逆映射实现，不冒称独立验证历史事实。完整性由有限区间划分和原始规则审查支持。

构造端浏览器实际读取了两版葡萄牙片段、EU/W-Eur 规则和完整国家索引；普通网页工具也读取了 IANA 原件。IANA 原始文本在浏览器中被当作下载阻止，使用公开 GitHub 原文件页面验证浏览器路径，未把浏览器成功等同于盲测成功。独立审查为静态证据审查，不声称审查模型自己重新运行了浏览器或重算程序。

## 模型实际成功路径与经验

CG 使用 6 次 web 调用、23 项搜索/打开/页内查找，定位三个原始文件后完成全部判断。GO 使用 9 次调用、27 项操作，先读公开 GitHub 标签原件，再用 IANA 原件交叉核对。均没有使用直接数据接口、批量下载、编译器、私有资料、预合并答案或另一面的回答；没有决定性访问失败或格式混淆。

实测说明：真实反例和必要判断只是质量条件，不能作为模型会错的证据。A v3 的源材料仍能收敛到一小组明确规则，Sol/medium 正确完成了逆映射；增加概念复杂度并未达到低分验收。不能据此临时删除容易字段、更改权重、再测同版，或用更大材料量补救。

B 的继续探索保留在 [机会记录](exploration/resumed_screening.md) 及 [补充记录](exploration/final_screening_notes.md)。化学证书方向没有完成原件可视核验和完整身份参考；结构生物学方向存在单页汇总及重复关系的捷径，未进入完整构造。

## 交付与最终检查

- [成对登记](plan.json)：四个版本的 CG/GO 各一次，登记资产和 A v3 权威评分程序完整保留；共八面全部执行。
- [原始运行](runs/)：18 次计数模型会话，逐次模型/effort、隔离、原始回答和工具轨迹。A v3 两面各有 authoritative_scoring、exact_report、retrieval_review 和 trajectory_review。
- [全部版本机器汇总](summary.json)、[独立账本](session_ledger.jsonl)、[检查结果](final_checks.json)。
- [A v3 参考](A/v3/reference.md)、[重算程序](A/v3/recompute.py)、[审查通过记录](A/v3/review-4.md)、[修改与审查处置](A/v3/quality_resolution.md)。
- [实际成本](final_costs.json)、[先前会话成本](costs.json)、[构造端继续会话网页/浏览器原始记录](evidence/resumed_web_browser_calls.jsonl)。

A v3 一次 CLI 预检因缺少 output_format 在模型分配前失败，单独保存诊断；没有占用模型调用，也未当作一次盲测重抽。与六题计划的额度及内容保持分离，复用现有 public_web 运行器；没有新增浏览器盲测工程。

## 成本快照

继续工作会话从 {cost['resumed_started_at']} 开始，当前快照墙钟 {cost['resumed_wall_seconds']:.1f} 秒；此前独立工作会话 4331.1 秒，两段均低于单会话 6000 秒。停止原因是 A 版本用尽。

18 次工作模型会话耗时合计 {cost['worker_elapsed_seconds_sum']:.3f} 秒；累计 input_tokens={cost['worker_usage_totals']['input_tokens']:,}，cached_input_tokens={cost['worker_usage_totals']['cached_input_tokens']:,}，output_tokens={cost['worker_usage_totals']['output_tokens']:,}，其中 reasoning_output_tokens={cost['worker_usage_totals']['reasoning_output_tokens']:,}。本次新增 4 次审查、2 次盲测，共新增 input_tokens={cost['resumed_worker_usage']['input_tokens']:,}、output_tokens={cost['resumed_worker_usage']['output_tokens']:,}。

继续会话构造端记录 {cost['constructor_resumed_native_web_calls']} 次原生 web 调用、{cost['constructor_resumed_logical_operations_literal_count']} 项字面请求操作、{cost['constructor_resumed_browser_node_calls']} 次浏览器 Node 调用。网页工具内部 HTTP、浏览器内部请求及构造端 shell 下载没有完整计量，不冒称为零。主控可取得的本次 token 增量为 input_tokens={cost['controller_resumed_token_delta']['input_tokens']:,}、output_tokens={cost['controller_resumed_token_delta']['output_tokens']:,}，详细快照口径另存。缓存/推理都是子集，不重复相加；没有可取得的货币账单。
'''
(R/'REPORT.md').write_text(report)
(R/'README.md').write_text('''# 两题独立计划交付索引

**目标未完成，0/2 达标。** A 用完 3/3 实质版本；最后一版 CG、GO 均有效 80/80。B 最新版因共享歧义没有有效成绩。总用量：盲测 8/12，审查 10/15。所有已登记两面均完成。

详见 [最终报告](REPORT.md)、[全版本结果](summary.json)、[独立账本](session_ledger.jsonl)、[实际成本](final_costs.json)。

- [A v1](A/v1/reference.md)：世界遗产边界批准例外。
- [A v2](A/v2/reference.md)：Cabaret 返场人员身份及信用。
- [A v3](A/v3/reference.md)：葡萄牙历史日志在 tzdb 2024a→2024b 的逆映射差异；[重算](A/v3/recompute.py)、[评分](A/v3/score_answer.py)、[审查](A/v3/review-4.md)。
- [B v1](B/v1/reference.md)：DNS 诊断，未通过检索依赖要求。
- [B v2](B/v2/reference.md)：HTTP 勘误回移；[歧义复核](B/v2/post_test_arbitration.md)。
- [全部原始运行](runs/)、[事前登记](plan.json)、[公开材料证据](evidence/)、[探索记录](exploration/)。

独立计数与六题计划分离。全部成绩为经过开发筛选的单次评估，不是无偏最终评估或正式收录。旧快照文件 *_before_A3.md、costs.json、resumed_costs.json 保留历史时间点，不代表当前状态。
''')
print('Updated final report, summary, state and index.')
