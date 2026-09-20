from pathlib import Path
import datetime as dt,json,re
R=Path(__file__).resolve().parent
old=json.loads((R/'resumed_costs.json').read_text());start=old['started_at'];now=dt.datetime.now(dt.timezone.utc).isoformat()
log=Path('/Users/ning/.codex/sessions/2026/09/19/rollout-2026-09-19T16-32-25-01a0b8cb-98a1-7de1-8440-a4498e91b287.jsonl')
selected=[];ids=set();web=browser=ops=0;latest=old['latest_controller_tokens'];latest_at=old['latest_controller_usage_at']
for line in log.open():
 x=json.loads(line);t=x.get('timestamp','')
 if t<start:continue
 p=x.get('payload',{});kind=p.get('type')
 if x.get('type')=='event_msg' and kind=='token_count' and p.get('info'):
  info=p['info'];usage=info.get('total_token_usage')
  if usage:latest=usage;latest_at=t
 if x.get('type')!='response_item':continue
 if kind in ('custom_tool_call','function_call'):
  code=p.get('input',p.get('arguments',''));name=p.get('name','')
  wc=len(re.findall(r'tools\.web__run\s*\(',code))+(name in ('web.run','web__run'))
  bc=len(re.findall(r'tools\.mcp__node_repl__js\s*\(',code))+(name=='mcp__node_repl__js')
  if wc or bc:
   web+=wc;browser+=bc
   if wc:ops+=len(re.findall(r'[\"\']?(?:q|ref_id)[\"\']?\s*:',code))
   ids.add(p.get('call_id'));selected.append(x)
 elif kind in ('custom_tool_call_output','function_call_output') and p.get('call_id') in ids:selected.append(x)
(R/'evidence/resumed_web_browser_calls.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in selected)+'\n')
workers=[]
for p in sorted((R/'runs').glob('*/run.json')):
 x=json.loads(p.read_text())
 if x.get('role') not in ('audit','blind'):continue
 workers.append({k:x.get(k) for k in ['run_id','candidate_id','revision','role','model','effort','actual_model','actual_effort','started_at','ended_at','elapsed_seconds','status','usage']})
ledger=[json.loads(x) for x in (R/'session_ledger.jsonl').read_text().splitlines()]
usagekeys=['input_tokens','cached_input_tokens','cache_write_input_tokens','output_tokens','reasoning_output_tokens']
new=[x for x in workers if x['started_at']>=start]
result={'snapshot_at':now,'resumed_started_at':start,'resumed_wall_seconds':(dt.datetime.fromisoformat(now)-dt.datetime.fromisoformat(start)).total_seconds(),'first_work_session_wall_seconds':4331.06284,'first_session_costs':'costs.json','workers':workers,'worker_session_count':len(workers),'ledger_allocations':len(ledger),'blind_used':sum(x.get('role')=='blind' for x in ledger),'review_used':sum(x.get('role')=='audit' for x in ledger),'worker_elapsed_seconds_sum':sum(x.get('elapsed_seconds') or 0 for x in workers),'worker_usage_totals':{k:sum((x.get('usage') or {}).get(k,0) or 0 for x in workers) for k in usagekeys},'resumed_worker_count':len(new),'resumed_worker_elapsed_sum':sum(x.get('elapsed_seconds') or 0 for x in new),'resumed_worker_usage':{k:sum((x.get('usage') or {}).get(k,0) or 0 for x in new) for k in usagekeys},'constructor_resumed_native_web_calls':web,'constructor_resumed_logical_operations_literal_count':ops,'constructor_resumed_browser_node_calls':browser,'controller_resumed_initial_tokens':old['baseline_controller_tokens'],'controller_latest_tokens':latest,'controller_latest_usage_at':latest_at,'controller_resumed_token_delta':{k:latest.get(k,0)-old['baseline_controller_tokens'].get(k,0) for k in latest},'notes':['Cached tokens are a subset of input; reasoning tokens are a subset of output. Do not double-count.','Controller token counters are local rollout usage snapshots, not a monetary bill; snapshots exclude subsequent final reporting.','Logical web operations count literal q/ref_id entries in logged JavaScript; internal tool/browser HTTP and constructor shell requests are not fully metered. Raw calls and responses are preserved.','One A3 audit CLI preflight failed before model/session allocation; it is diagnosed separately and is not an additional review.','No prices or dollar costs are inferred.']}
(R/'final_costs.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['worker_session_count','ledger_allocations','blind_used','review_used','resumed_wall_seconds','worker_elapsed_seconds_sum','worker_usage_totals','resumed_worker_usage','constructor_resumed_native_web_calls','constructor_resumed_logical_operations_literal_count','constructor_resumed_browser_node_calls','controller_resumed_token_delta']},indent=2))
