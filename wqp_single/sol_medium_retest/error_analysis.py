#!/usr/bin/env python3
"""Controller classifications linked to raw outcomes and saved offline diagnoses."""
import json,pathlib
T=pathlib.Path(__file__).resolve().parent
summary=json.loads((T/'summary.json').read_text());ex={r['label']:r for r in json.loads((T/'public_exposure_findings.json').read_text())['findings']};health={r['label']:r for r in json.loads((T/'tool_health.json').read_text())['runs']}
known={
 'screening_new_CG_1':(['cohort_completeness_reasoning'], 'diagnostics/first_cg_error.json','区间层统一覆盖判断错误，误排除真实共同区间，48行中仅3行正确。'),
 'screening_new_GO_1':(['numeric_text_sort'], 'diagnostics/screening_go_error.json','状态、身份和计数正确；溶解氧按TEXT排序，12行选错活动。'),
 'confirmation_new_CG_2':(['numeric_text_sort','output_transcription'], 'diagnostics/confirmation_cg2_error.json','保存的状态计算正确；数值排序错误，且最终抄录损坏3个行身份键。消除抄录错误仍不能整行答对。'),
 'confirmation_new_GO_1':(['numeric_text_sort'], 'diagnostics/ranking_evidence.json','输出与筛选GO逐字一致；SQL使用ORDER BY c.do，导入列为TEXT。'),
 'confirmation_new_GO_2':(['numeric_text_sort'], 'diagnostics/ranking_evidence.json','输出与筛选GO逐字一致；SQL直接排序导入的溶解氧TEXT列。'),
 'confirmation_new_GO_3':(['output_completeness','parse_failure'], 'diagnostics/confirmation_go3_error.json','计算表216字段全部正确，最终CSV仅12列，丢弃6个必需字段。原评分为NA，不能作为状态推理失败或补零。')}
rows=[]
for r in summary['runs']:
 label=r['label'];categories,evidence,explanation=known.get(label,([],None,'原始最终答案完整匹配原oracle。'))
 assert r['status']=='completed'
 if not categories:assert r['metrics'] and r['metrics']['whole_task_exact']==1
 h=health[label]
 rows.append({'label':label,'run':r['run'],'phase':r['phase'],'task':r['comparison_task'],'runtime_failure':False,'parse_failure':r.get('parse_status')=='parse_failure','parse_issues':json.loads((T/r['run']/'scoring/parsed.json').read_text())['issues'],'source_change':'No observed change in checked decisive source projections; full eligible panel checks separately reported' if r['comparison_task']=='new' else 'No contrary selected-station field evidence observed; original official verification and this run native web evidence retained','question_ambiguity':'Known nonunique public station selection in original004 remains' if r['comparison_task']=='old' else 'No new answer-determining ambiguity identified in fixedr03','public_answer_exposure':ex[label]['classification'],'error_categories':categories,'explanation':explanation,'diagnostic_evidence':evidence,'data_tool_failure_count':len(h['data_tool_failures']),'client_tool_failure_count':len(h['client_tool_failures']),'transient_access_handling':'Within-session retries/alternative official requests; no replacement model attempt. Data read/completeness verified separately.','raw_metrics':r['metrics'],'field_differences':r.get('differences_path')})
(T/'error_analysis.json').write_text(json.dumps({'classification_role':'Controller offline diagnosis, not an extra blind solve, model audit or scorer change','runs':rows,'policy':'Raw scores retained; all fixed attempts reported. A parsing/output failure or exposed answer is not automatically cognitive/state difficulty. Diagnostic reconstructed tables never replace submitted answers.'},ensure_ascii=False,indent=2)+'\n')
lines=['# 错误、运行与来源分项审查','','|尝试|归类|具体问题|','|---|---|---|']
for r in rows:lines.append(f"|[{r['label']}]({r['run']}/run.json)|{', '.join(r['error_categories']) or '匹配原oracle'}|{r['explanation']}|")
lines+=['','数值排序错误来自模型没有按现有工具说明显式转换TEXT列，不是新增工具限制或改评分制造的错误。CG2另有抄录问题；GO3有实际字段遗漏，原指标为NA，诊断不替换正式成绩。四次旧题完整答案暴露另见[暴露检查](public_exposure_findings.md)。','', '完整分类、暂时访问失败计数、解析细节、逐字段链接见[error_analysis.json](error_analysis.json)；原始工具失败原文见[tool_health.json](tool_health.json)。']
(T/'error_analysis.md').write_text('\n'.join(lines)+'\n');print('16 attempts classified')
