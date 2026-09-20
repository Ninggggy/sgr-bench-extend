#!/usr/bin/env python3
"""Read-only campaign accounting; no model calls or result rewriting."""
import argparse,datetime as dt,json,pathlib
B=pathlib.Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text())
def usage_from_trace(p, turn_id=None):
 last=None
 active=None
 baseline=None
 selected=None
 for line in p.open():
  try:
   x=json.loads(line)
   if x.get('type')=='event_msg' and x.get('payload',{}).get('type')=='task_started':
    active=x['payload'].get('turn_id')
    if active==turn_id:baseline=dict(last or {})
   if x.get('type')=='event_msg' and x.get('payload',{}).get('type')=='token_count':
    info=x['payload'].get('info') or {}
    if info.get('total_token_usage'):
     last=info['total_token_usage']
     if active==turn_id:selected=dict(last)
  except (ValueError,TypeError):pass
 if turn_id is None:return last
 if selected is None:return None
 return {k:v-(baseline or {}).get(k,0) for k,v in selected.items()}

def account():
 c=load(B/'campaign.json');rows=[json.loads(x) for x in (B/'session_ledger.jsonl').read_text().splitlines() if x.strip()];out=[]
 for row in rows:
  r=dict(row)
  if row.get('run_dir'):
   p=B/row['run_dir'];m=load(p/'run.json') if (p/'run.json').exists() else {}
   r.update({k:m.get(k) for k in ['status','started_at','ended_at','elapsed_seconds','usage','actual_model','actual_effort','verification_status','error']})
   r['usage_source']='completed event' if r.get('usage') is not None else 'unavailable'
   if r.get('usage') is None:
    traces=list((p/'sessions').glob('*.jsonl'))
    if len(traces)==1:
     partial=usage_from_trace(traces[0])
     if partial is not None:
      r['usage']=partial
      r['usage_source']='last recorded cumulative session token_count'
      r['usage_incomplete']=m.get('status')!='completed'
      r['usage_note']='Observed cumulative usage, not zero; a failed session may have consumed unreported tokens after this event.'
  else:
   paths=[]
   if row.get('thread_id'):paths=list((pathlib.Path.home()/'.codex/sessions').rglob('*'+row['thread_id']+'*.jsonl'))
   if paths:
    r['usage']=usage_from_trace(paths[0],row.get('turn_id'))
    r['usage_source']='actual turn cumulative-token delta' if row.get('turn_id') else 'last session cumulative token_count'
  out.append(r)
 now=dt.datetime.now(dt.timezone.utc);end=dt.datetime.fromisoformat(c['ended_at']) if c.get('ended_at') else now
 elapsed=(end-dt.datetime.fromisoformat(c['started_at'])).total_seconds()
 return {'at':now.isoformat(),'campaign_id':c['campaign_id'],'model_work_sessions':len(rows),'remaining_sessions':c['max_sessions']-len(rows),'active_work_sessions':sum(r.get('status') in ['running','preparing'] for r in out),'wall_clock_seconds':elapsed,'remaining_wall_clock_seconds':max(0,(dt.datetime.fromisoformat(c['deadline'])-end).total_seconds()),'model_elapsed_seconds_sum':sum(r.get('elapsed_seconds') or 0 for r in out),'currency_cost':None,'cost_note':'Uses existing account credentials; no purchased services. Currency cost unavailable from provider; report actual returned token usage, including failures and engineering/controller sessions. Root cumulative usage includes forked context; do not infer monetary cost or sum cached/input/output as independent billing buckets.','runs':out}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path);a=p.parse_args();x=account()
 if a.out:a.out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
 else:print(json.dumps(x,ensure_ascii=False,indent=2))
