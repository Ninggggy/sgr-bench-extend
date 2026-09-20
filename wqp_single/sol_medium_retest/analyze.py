#!/usr/bin/env python3
"""Offline Sol-only recomputation and summaries; never invokes a model."""
import argparse,collections,datetime as dt,importlib.util,json,pathlib,statistics,subprocess,sys,tomllib
T=pathlib.Path(__file__).resolve().parent
METRICS=['Item-F1','Row-F1','P.O.A.','whole_task_exact']
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def aggregate(rows):
 cells={}
 for task in ['new','old']:
  for form in ['cg','go']:
   rs=[r for r in rows if r['comparison_task']==task and r['variant']==form];sc=[r for r in rs if r.get('metrics') is not None]
   vals={m:[r['metrics'][m] for r in sc] for m in METRICS}
   cells[task+'_'+form]={'scheduled':len(rs),'started':sum(r['status']!='not_started' for r in rs),'completed':sum(r['status']=='completed' for r in rs),'evaluable':len(sc),'exact_count':sum(r['metrics']['whole_task_exact'] for r in sc),'end_to_end_exact_rate':sum(r['metrics']['whole_task_exact'] for r in sc)/len(rs) if rs else None,'means':{m:statistics.mean(v) if v else None for m,v in vals.items()},'ranges':{m:[min(v),max(v)] if v else None for m,v in vals.items()},'values':vals}
 means={task:{m:(cells[task+'_cg']['means'][m]+cells[task+'_go']['means'][m])/2 if all(cells[task+'_'+v]['means'][m] is not None for v in ['cg','go']) else None for m in METRICS} for task in ['new','old']}
 delta={m:means['new'][m]-means['old'][m] if all(means[t][m] is not None for t in ['new','old']) else None for m in METRICS}
 full={t:all(cells[t+'_'+v]['evaluable']==cells[t+'_'+v]['scheduled'] and cells[t+'_'+v]['scheduled']>0 for v in ['cg','go']) for t in ['new','old']}
 complete_means={t:means[t] if full[t] else {m:None for m in METRICS} for t in ['new','old']}
 end_exact={t:(cells[t+'_cg']['end_to_end_exact_rate']+cells[t+'_go']['end_to_end_exact_rate'])/2 if cells[t+'_cg']['scheduled'] and cells[t+'_go']['scheduled'] else None for t in ['new','old']}
 return {'cells':cells,'equal_weight_means':means,'new_minus_old':delta,'mean_scope':'Evaluable-only within each form, then equal CG/GO; conditional descriptive estimates when a planned answer is unscorable. Never impute zero.','all_slots_evaluable':full,'complete_plan_equal_weight_means':complete_means,'complete_plan_delta':delta if all(full.values()) else {m:None for m in METRICS},'end_to_end_equal_weight_exact_rate':end_exact}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--verify',action='store_true');a=ap.parse_args()
 plan=read(T/'analysis_plan.json');rows=[];checks=[]
 for j in plan['jobs']:
  run=pathlib.Path(j['out']);r={k:j[k] for k in ['label','phase','comparison_task','variant','replicate']};r.update(run=str(run.relative_to(T)),status='not_started',metrics=None)
  if (run/'run.json').exists():
   m=read(run/'run.json');r.update({k:m.get(k) for k in ['status','completed_event','model_reported_status','elapsed_seconds','started_at','ended_at','actual_model','actual_effort','ending_reason','error']})
   if a.verify and (run/'verification.json').exists():
    result=subprocess.run([sys.executable,str(run/'implementation/verify_run.py'),str(run)],capture_output=True,text=True)
    if result.returncode:raise RuntimeError(j['label']+': '+result.stderr)
   if (run/'verification.json').exists():
    v=read(run/'verification.json');assert v['model']=='gpt-5.6-sol' and v['effort']=='medium';checks.append({'label':j['label'],'run':r['run'],**v})
   if (run/'scoring/scores.json').exists():
    s=read(run/'scoring/scores.json');r.update(metrics=s['metrics'],score_status=s['status'],counts=s['counts'],omitted_ids=s['omitted_ids'],extra_ids=s['extra_ids'],duplicate_ids=s['duplicate_ids'],parse_status=read(run/'scoring/parsed.json')['status'])
    if r['metrics'] is not None:r['metrics']['whole_task_exact']=int(all(r['metrics'][k]==1 for k in METRICS[:3]))
    bad=[d for d in read(run/'scoring/field_differences.json') if not d['correct']];r['incorrect_field_count']=len(bad);r['difference_reasons']=dict(collections.Counter(d['reason'] for d in bad));r['incorrect_fields']=dict(collections.Counter(d['field'] for d in bad));r['differences_path']=r['run']+'/scoring/field_differences.json'
   if (run/'solver_output/result.json').exists():
    raw=read(run/'solver_output/result.json');r['reported_limitations']=raw.get('limitations');r['reported_evidence']=raw.get('evidence')
  rows.append(r)
 phases={p:aggregate([r for r in rows if r['phase']==p]) for p in ['screening','confirmation']}
 summary={'updated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'model':'gpt-5.6-sol','effort':'medium','plan':'analysis_plan.json','scope':'Only Sol attempts; screening separate from confirmation. No population/significance inference.','runs':rows,'summaries':phases}
 write(T/'summary.json',summary);write(T/'model_verification.json',{'runs':checks,'all_recorded_checks_passed':all(c['status']=='passed' for c in checks),'expected_completed_slots':16,'verified':len(checks),'note':'Four sources checked in each run: metadata, CLI argv, TOML and actual turn_context; no claim for not-yet-completed runs.'})
 lines=['# Sol/medium 逐次成绩','', '此表只包含本轮固定计划；NA不是零分。计数是原解析器识别的条目，不等于未识别CSV中实际包含的数据行；confirmation_new_GO_3的原CSV有12行12列，但缺6个必需字段，原解析计数为0、指标为NA。完整匹配以原评分器的三个指标均1判定；旧004的参考集合不代表公开条件唯一。','']
 for p in ['screening','confirmation']:
  lines += ['## '+p,'','|尝试|状态|Item-F1|Row-F1|P.O.A.|整题匹配|正确字段/参考/预测|正确行/参考/预测|正确顺序对/共有对|','|---|---|---:|---:|---:|---:|---|---|---|']
  for r in [x for x in rows if x['phase']==p]:
   ms=r['metrics'] or {};c=r.get('counts') or {};fmt=lambda k:str(ms.get(k,'NA'))
   count=lambda ks:'/'.join(str(c.get(k,'NA')) for k in ks)
   lines.append('|'+ '|'.join([f"[{r['label']}]({r['run']}/run.json)",r['status'],*[fmt(k) for k in METRICS],count(['correct_fields','gold_fields','pred_fields']),count(['correct_rows','gold_rows','pred_rows']),count(['correct_pairs','pair_denominator'])])+'|')
  lines+=['','|题目/题面|可评分/预定|整题匹配数|Item-F1均值|Row-F1均值|P.O.A.均值|整题正确率|','|---|---:|---:|---:|---:|---:|---:|']
  for key,c in phases[p]['cells'].items():lines.append('|'+ '|'.join([key,f"{c['evaluable']}/{c['scheduled']}",str(c['exact_count']),*[f'{c["means"][m]:.6f}' if c['means'][m] is not None else 'NA' for m in METRICS]])+'|')
  lines+=['','可评分尝试内先平均、CG/GO等权（新、旧、差值）；存在NA时仅为条件描述均值：','']
  for m in METRICS:lines.append(f"- {m}: {phases[p]['equal_weight_means']['new'][m]} / {phases[p]['equal_weight_means']['old'][m]} / {phases[p]['new_minus_old'][m]}")
  lines += ['',f"完整预定分母的指标差值：{phases[p]['complete_plan_delta']}；端到端完整匹配率（解析失败记未交付成功，不作能力零分）：{phases[p]['end_to_end_equal_weight_exact_rate']}",'']
 lines+=['## 逐字段差异与原始作答','']
 for r in rows:
  if r.get('differences_path'):lines.append(f"- {r['label']}: [字段明细]({r['differences_path']})；[原始答案]({r['run']}/answer.txt)；[原始工具记录]({r['run']}/tool_events.jsonl)。差异记录数 {r['incorrect_field_count']}；类型 {r['difference_reasons']}。")
 (T/'summary.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps({'completed':sum(r['status']=='completed' for r in rows),'scorable':sum(r['metrics'] is not None for r in rows),'confirmation':phases['confirmation']['equal_weight_means']},ensure_ascii=False))
if __name__=='__main__':main()
