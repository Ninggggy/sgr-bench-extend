#!/usr/bin/env python3
"""Compact status/actual-score accounting; no solver calls."""
import argparse,datetime as dt,json,pathlib
B=pathlib.Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
rows=[]
ledger=B/'session_ledger.jsonl'
for line in ledger.read_text().splitlines() if ledger.exists() else []:
 x=json.loads(line);r=B/x['run_dir'];m=json.loads((r/'run.json').read_text());o={'session_number':x['session_number'],'label':x['label'],'run_dir':x['run_dir'],'status':m['status'],'started_at':m.get('started_at'),'ended_at':m.get('ended_at'),'elapsed_seconds':m.get('elapsed_seconds'),'actual_model':m.get('actual_model'),'ending_reason':m.get('ending_reason'),'completed_event':m.get('completed_event'),'model_reported_status':m.get('model_reported_status'),'exit_code':m.get('exit_code'),'usage':m.get('usage'),'metrics':None,'parse_status':None}
 if (r/'scoring/scores.json').exists():s=json.loads((r/'scoring/scores.json').read_text());o['metrics']=s['metrics'];o['score_status']=s['status'];o['counts']=s['counts']
 if (r/'scoring/parsed.json').exists():o['parse_status']=json.loads((r/'scoring/parsed.json').read_text())['status']
 if o['started_at'] and o['ended_at']:
  o['utc_timestamp_duration_seconds']=round((dt.datetime.fromisoformat(o['ended_at'])-dt.datetime.fromisoformat(o['started_at'])).total_seconds(),3)
  o['timestamp_minus_monotonic_seconds']=round(o['utc_timestamp_duration_seconds']-(o['elapsed_seconds'] or 0),3)
 rows.append(o)
report={'updated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'sessions_started':len(rows),'budget_sessions':60,'session_seconds_sum':sum(r['elapsed_seconds'] or 0 for r in rows),'campaign':json.loads((B/'campaign.json').read_text()),'runs':rows}
report['timing_note']='elapsed_seconds is the runner monotonic-clock duration. UTC timestamp duration is retained separately; large discrepancies may reflect host suspension/clock behavior and are not attributed to reasoning. Parallel session sums are not campaign wall time.'
end=dt.datetime.fromisoformat(report['campaign']['ended_at']) if report['campaign'].get('ended_at') else dt.datetime.now(dt.timezone.utc)
report['campaign_wall_seconds_so_far']=round((end-dt.datetime.fromisoformat(report['campaign']['started_at'])).total_seconds(),3)
report['campaign_closed']=bool(report['campaign'].get('ended_at'))
if a.write:(B/'run_accounting.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'sessions_started':len(rows),'sessions':[{'n':r['session_number'],'label':r['label'],'status':r['status'],'seconds':r['elapsed_seconds'],'scores':r['metrics']} for r in rows]},ensure_ascii=False,indent=2))
