#!/usr/bin/env python3
"""Account only the new campaign and its actual invocation ledger."""
import collections,datetime as dt,json,pathlib
T=pathlib.Path(__file__).resolve().parent
campaign=json.loads((T/'campaign.json').read_text());ledger=[json.loads(l) for l in (T/'session_ledger.jsonl').read_text().splitlines()];rows=[]
for e in ledger:
 r=T/e['run_dir'];m=json.loads((r/'run.json').read_text());rows.append({**e,'status':m['status'],'ended_at':m.get('ended_at'),'elapsed_seconds':m.get('elapsed_seconds'),'usage':m.get('usage'),'actual_model':m.get('actual_model'),'actual_effort':m.get('actual_effort')})
end=dt.datetime.fromisoformat(campaign['ended_at']) if campaign.get('ended_at') else dt.datetime.now(dt.timezone.utc);wall=(end-dt.datetime.fromisoformat(campaign['started_at'])).total_seconds()
usage=collections.Counter()
for r in rows:usage.update({k:v for k,v in (r.get('usage') or {}).items() if isinstance(v,(int,float))})
result={'campaign':'campaign.json','model':'gpt-5.6-sol','effort':'medium','actual_sessions':len(rows),'maximum_sessions':17,'scheduled_regular_slots':16,'repair_retries_used':max(0,len(rows)-16),'status_counts':dict(collections.Counter(r['status'] for r in rows)),'wall_seconds':wall,'sum_model_run_seconds':sum(r['elapsed_seconds'] or 0 for r in rows),'remaining_wall_seconds':max(0,(dt.datetime.fromisoformat(campaign['deadline'])-end).total_seconds()),'reported_cli_usage_sum':dict(usage),'sessions':rows,'note':'CLI reported token totals include repeatedly supplied and cached context; not a count of distinct source text. Concurrent run seconds are not campaign wall time. All recorded model attempts count, including faults. No GPT-6 sessions included.'}
(T/'run_accounting.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['actual_sessions','status_counts','wall_seconds']}))
