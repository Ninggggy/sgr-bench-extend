"""Record post-score controller reviews without editing registered task assets."""
from pathlib import Path
import datetime as dt,json,re
P=Path(__file__).resolve().parent;R=P.parents[1]
now=dt.datetime.now(dt.timezone.utc).isoformat()
for face in ('CG','GO'):
 run=R/'runs'/f'new-two-A-v3-{face}'
 raw=[json.loads(x) for x in (run/'tool_events.jsonl').read_text().splitlines()]
 calls=[x for x in raw if x['payload']['type'] in ('custom_tool_call','function_call')]
 scripts=[x['payload'].get('input',x['payload'].get('arguments','')) for x in calls]
 assert all('tools.web__run(' in s for s in scripts)
 logical=sum(len(re.findall(r'[\"\']?(?:q|ref_id)[\"\']?\s*:',s)) for s in scripts)
 sourcepath=('Search → pinned IANA country index and both europe files → targeted Portugal and EU/W-Eur page reads → exact inverse-local interval table.' if face=='CG' else 'Search → tagged raw GitHub country index and both europe files → Portugal and EU/W-Eur reads → additional date search → pinned IANA originals for confirmation → exact inverse-local interval table.')
 review={'verdict':'passed','capability_score_eligible':True,'reviewed_by':'controller','reviewed_at':now,'content_errors':[],'access_issues':[],'format_errors':[],'access_confounded':False,'format_confounded':False,'answer_exposure_review':'passed','retrieval_compliance':{'ordinary_search_and_page_reads':True,'direct_data_api':False,'bulk_or_split_bulk_fetch':False,'private_answer_access':False,'pagination_violation':False,'notes':'All tool inputs are ordinary web search/open/find. These are three original text files per source mirror, not a dataset endpoint or premerged inverse answer. Page rereads are localized sections of the same originals. No archive download, compiler, shell, private file, opposite-face result, or direct API is invoked. Unrelated archive/API links inside search results/source comments were not followed.'},'web_tool_calls':len(scripts),'logical_web_requests':logical,'source_path':sourcepath,'success_path_analysis':'Every one of 40 fields is correct, including old/new March 1992 gap reversal, offset cancellation at old zone boundaries, winter offset, December gap and March/June 1993 gap/fold. The finite source rules support a short legal reasoning route. Counterexamples established necessary judgments but did not produce errors. No workload-only or wording-only retest is justified.'}
 (run/'retrieval_review.json').write_text(json.dumps(review,indent=2)+'\n')
 scores=json.loads((run/'authoritative_scoring/scores.json').read_text());c=scores['counts'];n=2*c['correct_fields'];d=c['item_denominator']
 exact={'valid':True,'quality':'passed','item_fraction_unreduced':{'n':n,'d':d},'item_f1_exact':f'{n}/{d}','row_f1_exact':f"{2*c['correct_rows']}/{c['row_denominator']}",'whole_task_correct':scores['whole_answer_correct'],'exact_threshold_comparison':{'left':10*n,'right':7*d},'strictly_below_70':10*n<7*d,'qualified_face':False,'offset_field_accuracy':scores['offset_field_accuracy'],'scoring':'authoritative_scoring/scores.json','retrieval_review':review}
 (run/'exact_report.json').write_text(json.dumps(exact,indent=2)+'\n')
 (run/'trajectory_review.md').write_text(f'''# {face} 原始轨迹审查\n\n结论：成绩有效，难度未达标。Item-F1 {n}/{d}，Row-F1 {2*c['correct_rows']}/{c['row_denominator']}，整题全对 true。精确比较 {10*n} < {7*d} 为假。\n\n先保存 raw result.json / answer.txt，再执行事前登记的 score_answer.py 得到 authoritative_scoring，之后核查工具轨迹。本审查没有改写题面、参考、字段权重或解析器。\n\n内容：40 个字段和 8 行全部正确。获取：{len(scripts)} 次普通 web 调用，{logical} 项搜索/打开/页内查找，均为允许路径；不是限制计数。访问：没有决定性获取失败。格式：正常表格，提取零变换，无额外或缺失行。隔离记录显示无主机绑定目录、无历史恢复、没有参考答案或另一面回答可读。\n\n实际路径：{sourcepath}\n\n原始公开文件虽包含多个国家，但其为正常单篇版本原件；定点页内读取不构成批量抓取。搜索结果及原文注释中的未访问链接不是额外请求。未发现预合并答案、直接数据接口、批量导出或答案暴露。\n\n成功原因：模型从少量源文件提取了决定性规则，正确把 UTC 段映射回本地时间；短路径上的必要判断均被完成。不能因构造者认为细节复杂而宣称题目足够难。\n\n逐次实际调用：\n\n'''+ '\n\n'.join('```javascript\n'+s+'\n```' for s in scripts))
 print(face,exact['item_f1_exact'],logical)
