#!/usr/bin/env python3
"""Report recorded content attempts and legal data paths; no fabricated answers."""
import argparse,collections,datetime as dt,json,pathlib
ap=argparse.ArgumentParser();ap.add_argument('--revision',default='r01');args=ap.parse_args()
B=pathlib.Path(__file__).resolve().parent.parent;REV=B/'candidates/wqp_activity_panel_001'/args.revision;P=REV/'private';plan=json.loads((P/'content_run_plan.json').read_text());rows=[]
for job in plan['jobs']:
 r=pathlib.Path(job['out']);o={'label':job['label'],'variant':job['variant'],'run':str(r.relative_to(REV)),'status':'not_started','metrics':None,'downloads':[],'tool_counts':{}}
 if (r/'run.json').exists():
  m=json.loads((r/'run.json').read_text());o.update({k:m.get(k) for k in ['status','actual_model','effort','current_date','completed_event','model_reported_status','elapsed_seconds','ending_reason','exit_code','usage']})
 if (r/'scoring/scores.json').exists():
  s=json.loads((r/'scoring/scores.json').read_text());o.update(metrics=s['metrics'],score_status=s['status'],counts=s['counts'],parse_status=json.loads((r/'scoring/parsed.json').read_text())['status'])
 if (r/'solver_output/result.json').exists():
  res=json.loads((r/'solver_output/result.json').read_text());o.update(evidence=res.get('evidence'),limitations=res.get('limitations'),raw_final_answer_path=str((r/'answer.txt').relative_to(REV)))
 if (r/'downloaded_data/tool_calls.jsonl').exists():
  calls=[json.loads(l) for l in (r/'downloaded_data/tool_calls.jsonl').read_text().splitlines()];o['tool_counts']=dict(collections.Counter(c['name'] for c in calls));o['downloads']=[{'requested_at':c['started_at'],'url':c['arguments']['url'],'status':c['result'].get('status'),'error':c['result'].get('error'),'file_id':c['result'].get('file_id'),'bytes':c['result'].get('bytes'),'archive_members':c['result'].get('members'),'full_csv_rows':c['result'].get('data_rows')} for c in calls if c['name']=='download'];o['sql_calls']=[{'started_at':c['started_at'],'arguments':c['arguments'],'result_file_id':c['result'].get('file_id'),'rows_returned_by_query':c['result'].get('total_rows'),'error':c['result'].get('error')} for c in calls if c['name']=='query_csv']
 if not o['tool_counts'] and (r/'events.jsonl').exists():
  recorded=[]
  for line in (r/'events.jsonl').read_text().splitlines():
   event=json.loads(line);item=event.get('item',{})
   if event.get('type')=='item.completed' and item.get('type')=='mcp_tool_call':recorded.append(item)
  o['tool_counts']=dict(collections.Counter(x['tool'] for x in recorded))
  o['downloads']=[{'url':x['arguments']['url'],'status':x.get('status'),'error':x.get('error'),'retention':'actual full tool return in events.jsonl; original downloaded file not retained'} for x in recorded if x['tool']=='download']
  o['data_retention_limitation']='Docker archive API did not recover tmpfs full download files; actual tool calls/results and controller original sources remain. Never relabel subsequent fetches as original solver data.'
 if (r/'verification.json').exists():o['verification']=json.loads((r/'verification.json').read_text())
 if (r/'scoring_rule_recheck/scores.json').exists():o['rule_recheck_metrics']=json.loads((r/'scoring_rule_recheck/scores.json').read_text())['metrics']
 rows.append(o)
report={'updated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'purpose':'Four content blind solves and two separate blind shortcut attempts; no result here is a difficulty screening or confirmation run','prespecified_plan':'content_run_plan.json','actual_runs':rows,'independence':'Each received only the public task/date/output format plus the appropriate stage prompt and solver result schema in a new isolated Docker/Codex context. Probe/config/history details remain per-run. No fork/resume or host bind mounts.','correctness_scope':'Scores measure exact declared output semantics against independently recomputed source gold; same-model agreement alone does not establish source truth.','status_fields':'Runtime completion event, exit status, self-reported status, answer parsing and metrics are separate. HTTP errors remain recorded; complete transport with HTTP500 is not valid source data.'}
(P/'content_runs_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
lines=['# 四次内容盲解与两次合法捷径尝试','',report['purpose'],'','|运行|运行状态|模型自报|解析|Item-F1|Row-F1|P.O.A.|秒|','|---|---|---|---|---:|---:|---:|---:|']
for r in rows:
 m=r['metrics'] or {};lines.append('|'+ '|'.join(str(x) for x in [r['label'],r['status'],r.get('model_reported_status','NA'),r.get('parse_status','NA'),m.get('Item-F1','NA'),m.get('Row-F1','NA'),m.get('P.O.A.','NA'),r.get('elapsed_seconds','NA')])+'|')
for r in rows:
 lines+=['','## '+r['label'],'',f"原始记录：{r['run']}。下载/计算工具计数：{json.dumps(r['tool_counts'],ensure_ascii=False)}。"]
 if r.get('limitations'):lines+=['','模型实际报告的限制：',*['- '+str(x) for x in r['limitations']]]
 lines+=['','实际官方下载请求：']
 for d in r['downloads']:lines+=['- '+str(d['status'])+' '+d['url']+('；'+d['error'] if d.get('error') else '')]
lines+=['','完整工具请求/返回与SQL在events.jsonl、tool_events.jsonl与sessions/；r01六次运行的完整下载文件因tmpfs归档失败未保留，控制端参考源数据独立保存；没有用空答案代替非空解析失败。是否合法消除核心SGR依赖由独立审计/裁决决定，而不是由分数或网络请求次数自行决定。']
(P/'content_runs_report.md').write_text('\n'.join(lines)+'\n');print(json.dumps({'recorded_attempts':len(rows),'completed':sum(r['status']=='completed' for r in rows)}))
