"""Read-only aggregation of archived answers/scores; writes this batch's report only."""
from pathlib import Path
from fractions import Fraction
import json,csv,datetime
p=Path(__file__).resolve().parent;plan=json.loads((p/'plan.json').read_text());rows=[]
for job in plan['jobs']:
 d=Path(job['out']);m=json.loads((d/'run.json').read_text()) if (d/'run.json').exists() else {}
 identity=json.loads(Path(job['job_metadata']).read_text());score={};ratio=None
 if (d/'scoring/scores.json').exists():
  score=json.loads((d/'scoring/scores.json').read_text());c=score.get('counts') or {};n=c.get('correct_fields');den=c.get('item_denominator')
  if isinstance(n,int) and isinstance(den,int) and den>0 and isinstance((score.get('metrics') or {}).get('Item-F1'),(int,float)):ratio=Fraction(2*n,den)
 answer=json.loads((d/'solver_output/result.json').read_text()) if (d/'solver_output/result.json').exists() else {}
 audit=json.loads((d/'retrieval_review.json').read_text()) if (d/'retrieval_review.json').exists() else {}
 rows.append({'candidate_id':identity['candidate_id'],'revision':identity['revision'],'variant':identity['variant'],'run_id':job['label'],'run_status':m.get('status','not_started'),'model':m.get('actual_model'),'effort':m.get('actual_effort'),'verification':m.get('verification_status'),'answer_status':answer.get('status','unknown'),'item_f1_exact':str(ratio) if ratio is not None else '', 'item_f1_percent':float(ratio*100) if ratio is not None else '', 'score_status':score.get('status','not_scored'), 'row_f1':(score.get('metrics') or {}).get('Row-F1',''),'retrieval_compliance':audit.get('verdict','pending'),'access_confounded':audit.get('access_confounded',False),'format_confounded':audit.get('format_confounded',False),'capability_score_eligible':audit.get('capability_score_eligible',None),'review_notes':audit.get('reason',audit.get('limitations','')),'started_at':m.get('started_at'),'ended_at':m.get('ended_at'),'seconds':m.get('elapsed_seconds'),'limitations':answer.get('limitations',[]),'usage':m.get('usage'),'run_dir':str(d)})
with (p/'scores.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=[k for k in rows[0] if k not in ['usage']]);w.writeheader();w.writerows({k:v for k,v in r.items() if k!='usage'} for r in rows)
summary={}
for v in ['CG','GO']:
 rr=[r for r in rows if r['variant']==v];sc=[r for r in rr if r['item_f1_exact']!=''];ok=[r for r in sc if r['retrieval_compliance']=='passed' and r['model']=='gpt-5.6-sol' and r['effort']=='medium' and r['verification']=='passed']
 def stats(group):
  return {'n':len(group),'macro_Item_F1_exact':str(sum((Fraction(r['item_f1_exact']) for r in group),Fraction())/len(group)) if group else None,'macro_Item_F1_percent':float(sum((Fraction(r['item_f1_exact']) for r in group),Fraction())/len(group)*100) if group else None,'full_answers':sum(Fraction(r['item_f1_exact'])==1 and r['row_f1']==1 for r in group),'full_answer_rate_percent':100*sum(Fraction(r['item_f1_exact'])==1 and r['row_f1']==1 for r in group)/len(group) if group else None}
 summary[v]={'planned':30,'raw':stats(sc),'reviewed_compliant':stats(ok),'compliant_with_access_confounds':sum(r['access_confounded'] for r in ok),'compliant_without_reported_access_confounds':stats([r for r in ok if not r['access_confounded']]),'completed_unscored':sum(r['run_status']=='completed' and r['item_f1_exact']=='' for r in rr),'unreviewed':sum(r['retrieval_compliance']=='pending' for r in sc),'noncompliant':sum(r['retrieval_compliance']=='failed' for r in sc)}
started=[datetime.datetime.fromisoformat(r['started_at']) for r in rows if r['started_at']]
ended=[datetime.datetime.fromisoformat(r['ended_at']) for r in rows if r['ended_at']]
usage_keys=['input_tokens','cached_input_tokens','cache_write_input_tokens','output_tokens','reasoning_output_tokens']
cost={'first_start':min(started).isoformat() if started else None,'last_completed_end':max(ended).isoformat() if ended else None,'observed_start_to_last_end_seconds':(max(ended)-min(started)).total_seconds() if started and ended else None,'summed_session_seconds':sum(r['seconds'] or 0 for r in rows),'usage_record_count':sum(bool(r['usage']) for r in rows),'tokens':{k:sum((r['usage'] or {}).get(k,0) or 0 for r in rows) for k in usage_keys},'money_cost':None,'controller_token_cost':None,'weekly_quota_attributable_to_batch':None,'note':'Cache input is a subset of input, reasoning output a subset of output; do not add them again. Wall interval differs from summed concurrent sessions. Missing usage is unknown.'}
disposition={k:sum(r['run_status']=='completed' and r['retrieval_compliance']==k for r in rows) for k in ['passed','failed','pending']}
report={'completed':sum(r['run_status']=='completed' for r in rows),'total_planned':len(rows),'review_disposition_all_completed':disposition,'cost':cost,'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':plan['protocol_version'],'excluded':['europemc_balf_provenance_001'],'summary':summary,'results':rows,'limitations':['Single trial per variant, not formal admission or statistical certification.','Scores compare archived references; source drift not independently revalidated.','Pending or failed retrieval reviews are not compliant scores.','No zero imputation for missing results; raw computed empty-answer scores are distinguished by status and limitations.','Token totals are not account quota consumption.']}
(p/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
lines=['# 31道底题有界检索复测','',f"更新时间：{report['updated_at']}",'','31道中30道计划执行CG/GO各一次，共60次；BALF保留此前服务安全中断，不重启。','', '原始分数按旧参考答案计算，不自动代表协议合规或当前来源下答案仍正确。NA/故障/缺失不补零；单次分数不是正式三次收录均值。','', '| 题目 | 版本 | 题面 | 状态 | 原始Item-F1 | 获取合规 |','|---|---|---|---|---:|---|']
headline=['# 31道底题有界检索复测结果','',f"已结束：{report['completed']}/{report['total_planned']}次。31道中30道各测CG/GO一次；BALF因先前服务安全中断排除。所有实际运行均为gpt-5.6-sol / medium；未追加、替换或重试。",'',f"获取规则审查：{disposition['passed']}通过，{disposition['failed']}失败，{disposition['pending']}待审；3次未评分保持NA。",'', '| 统计口径 | CG | GO |','|---|---:|---:|']
for group,label in [('reviewed_compliant','合规且可评分'),('raw','全部原始可评分（含违规）')]:
 a,c=summary['CG'][group],summary['GO'][group]
 headline.append(f"| {label}：平均Item-F1 | {a['macro_Item_F1_percent']:.4f}%（n={a['n']}） | {c['macro_Item_F1_percent']:.4f}%（n={c['n']}） |")
 headline.append(f"| {label}：整题全对率 | {a['full_answer_rate_percent']:.4f}%（{a['full_answers']}/{a['n']}） | {c['full_answer_rate_percent']:.4f}%（{c['full_answers']}/{c['n']}） |")
headline+=['','合规子集经过筛选，不能代表全部31题；其来源访问、范围唯一性、格式及排序混淆仍在逐次review_notes中保留。未做参考答案的新质量认证，也不作正式收录判定。','', '主要限制：提示约束并未硬性拦截全部违规；出现完整候选导出、拒绝后重试、超过60请求或2目标并发的情况。原始低分也包括大小写、解释段落误入数据、列错位、排序及可能多解，不能一概归为检索能力错误。','', '盲测实际耗时115分55秒（19:57:58—21:53:53，北京时间2026-09-13），两个盲测槽并行。累计会话时长另列，不能当作墙钟时间。账户已用周额度观察53%→64%，共享账户差值不能全部归因本批；未使用重置。货币成本和总控token未知。','', '保存的旧材料/评分不变；当前summary已纠正NA误计零，旧控制器诊断快照保留用于追溯。数据源实际访问日为9月13日，沿用提示日期9月9日，部分题目要求9月12日快照，日期冲突和来源漂移未被本次修复。','']
lines=headline+lines[2:]
for r in rows:lines.append(f"| {r['candidate_id']} | r{r['revision']:02d} | {r['variant']} | {r['run_status']} | {str(round(r['item_f1_percent'],4))+'%' if r['item_f1_exact'] else 'NA'} | {r['retrieval_compliance']} |")
paired=[]
for cid in dict.fromkeys(r['candidate_id'] for r in rows):
 rr=[r for r in rows if r['candidate_id']==cid];by={r['variant']:r for r in rr}
 def display(v):
  r=by[v]
  return (f"{r['item_f1_percent']:.4f}%" if r['item_f1_exact'] else 'NA')+' / '+r['retrieval_compliance']
 paired.append(f"| {cid} | r{rr[0]['revision']:02d} | {display('CG')} | {display('GO')} |")
lines+=['','按底题对照（原始Item-F1 / 获取合规审查）：','','| 底题 | 版本 | CG | GO |','|---|---|---|---|']+paired
lines+=['','统计口径：Item-F1为逐题字段F1的宏平均；整题全对率要求Item-F1与Row-F1均为1。合规且未报告访问混淆的子集只是诊断，存在选择偏差，不能代表全部31题。','', '成本记录：','```json',json.dumps(cost,ensure_ascii=False,indent=2),'```','','按题面统计：','', '```json',json.dumps(summary,ensure_ascii=False,indent=2),'```','', '逐次原始回答、来源轨迹、评分与审查在runs中；完整机器可读结果见results.json和scores.csv。']
(p/'report.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(summary))
