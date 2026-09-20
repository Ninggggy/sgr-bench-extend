#!/usr/bin/env python3
"""Summarize archived real tool outcomes without treating error counts as difficulty."""
import collections,json,pathlib
T=pathlib.Path(__file__).resolve().parent
out=[]
for j in json.loads((T/'analysis_plan.json').read_text())['jobs']:
 r=pathlib.Path(j['out']);mf=r/'run.json'
 if not mf.exists():continue
 m=json.loads(mf.read_text());tf=r/'downloaded_data/tool_calls.jsonl';calls=[json.loads(l) for l in tf.read_text().splitlines()] if tf.exists() else []
 failures=[]
 for n,c in enumerate(calls,1):
  res=c.get('result',{});status=res.get('status')
  if c.get('is_error') or isinstance(status,int) and status>=400:
   failures.append({'line':n,'tool':c['name'],'arguments':c['arguments'],'result':res,'started_at':c['started_at'],'ended_at':c['ended_at']})
 client_failures=[]
 ef=r/'events.jsonl'
 if ef.exists():
  for number,line in enumerate(ef.read_text().splitlines(),1):
   event=json.loads(line);item=event.get('item',{})
   if event.get('type')=='item.completed' and item.get('type')=='mcp_tool_call' and (item.get('error') or item.get('status')=='failed'):
    client_failures.append({'event_line':number,'id':item.get('id'),'tool':item.get('tool'),'arguments':item.get('arguments'),'error':item.get('error'),'status':item.get('status')})
 out.append({'label':j['label'],'run':str(r.relative_to(T)),'status':m['status'],'ending_reason':m.get('ending_reason'),'runner_error':m.get('error'),'cli_errors':m.get('errors'),'data_tool_calls':dict(collections.Counter(c['name'] for c in calls)),'data_tool_failures':failures,'client_tool_failures':client_failures,'note':'HTTP/SQL/query failures may be recovered within the same attempt; no model-session repair retry is implied. Native web responses remain in tool_events and sessions for detailed inspection.'})
(T/'tool_health.json').write_text(json.dumps({'runs':out,'classification_policy':'A tool error is not automatically an environment failure or a reasoning failure; inspect request, response and effect on final answer. Completed outcomes and parse status are separate.'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps([{'label':r['label'],'status':r['status'],'tool_failure_count':len(r['data_tool_failures'])} for r in out]))
