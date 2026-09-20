"""Summarize existing session records; does not allocate or run any session."""
from pathlib import Path
import json,datetime
B=Path(__file__).parent
ledger=[json.loads(x) for x in (B/'session_ledger.jsonl').read_text().splitlines()]
active=[x for x in ledger if x['session_number']>18]
rows=[]
for x in active:
 p=B/x['run_dir']/'run.json';r=json.loads(p.read_text()) if p.exists() else {}
 rows.append({'session_number':x['session_number'],**{k:r.get(k,x.get(k)) for k in ['run_id','candidate_id','revision','role','model','actual_model','effort','actual_effort','status','started_at','ended_at','elapsed_seconds','usage','errors']}})
totals={k:sum((r.get('usage') or {}).get(k,0) or 0 for r in rows) for k in ['input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens']}
now=datetime.datetime.now(datetime.timezone.utc)
obj={'as_of':now.isoformat(),'budget_epoch':2,'blind_allocated':sum(x['role']=='blind' for x in active),'review_allocated':sum(x['role']=='audit' for x in active),'worker_token_totals_available':totals,'sum_worker_elapsed_seconds':sum(r.get('elapsed_seconds') or 0 for r in rows),'cost_note':'No price assumptions. Cached input subset of input; reasoning subset of output. Worker elapsed overlaps; sum is not wall time. Running sessions have unavailable final usage. Controller cost separate.','runs':rows}
(B/'epoch2_costs.json').write_text(json.dumps(obj,indent=2)+'\n')
s=json.loads((B/'state.json').read_text());s.update(blind_used=obj['blind_allocated'],review_used=obj['review_allocated'],remaining_blind=12-obj['blind_allocated'],remaining_reviews=15-obj['review_allocated'],costs='epoch2_costs.json')
plan=json.loads((B/'plan.json').read_text());allocated={x['run_id'] for x in ledger};s['unexecuted_registered_slots']=sum(x['run_id'] not in allocated for r in plan['development_rounds'] for x in r['slots'])
s['current_epoch_running']=[r['run_id'] for r in rows if r['status']=='running'];s['work_session_elapsed_seconds']=(now-datetime.datetime.fromisoformat(s['work_session_started_at'])).total_seconds()
for id in ['C','D','E']:
 if id in s['slots']:
  s['slots'][id]['blind_used']=sum(x['candidate_id']==id and x['role']=='blind' for x in active);s['slots'][id]['review_used']=sum(x['candidate_id']==id and x['role']=='audit' for x in active)
(B/'state.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:obj[k] for k in ['as_of','blind_allocated','review_allocated','worker_token_totals_available']}))
