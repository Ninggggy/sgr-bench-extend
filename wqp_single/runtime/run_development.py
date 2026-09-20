#!/usr/bin/env python3
"""Run declared development attempts; two full successes trigger repair, never extra attempts."""
import argparse,datetime,json,pathlib,subprocess,sys
B=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--plan',type=pathlib.Path,required=True);p.add_argument('--remaining-revisions',type=int,required=True);a=p.parse_args();plan=json.loads(a.plan.read_text());done=[]
for j in plan['jobs']:
 out=pathlib.Path(j['out'])
 if not (out/'run.json').exists():
  one=a.plan.parent/'runtime_current_job.json';one.write_text(json.dumps({'jobs':[j]},indent=2)+'\n')
  r=subprocess.run([sys.executable,str(B/'run_batch.py'),'--plan',str(one)])
  if r.returncode:raise SystemExit(r.returncode)
 meta=json.loads((out/'run.json').read_text());done.append(j)
 if meta['status']!='completed':raise SystemExit('Development attempt did not complete; inspect actual failure, no automatic retry')
 if a.remaining_revisions>0:
  for variant in ['cg','go']:
   candidates=[x for x in done if x['variant']==variant and 'content_' in x['label']]
   if len(candidates)==2:
    exact=[]
    for x in candidates:
     s=json.loads((pathlib.Path(x['out'])/'scoring/scores.json').read_text());exact.append(s.get('metrics') is not None and s['metrics']['Item-F1']==1 and s['metrics']['Row-F1']==1 and s['metrics']['P.O.A.']==1)
    if all(exact):
     disposition={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'trigger':f'Two {variant.upper()} development solves fully correct','action':'return_to_construction','completed_jobs':[x['label'] for x in done],'not_run_jobs':[x['label'] for x in plan['jobs'] if x not in done],'new_model_sessions_added_due_to_score':0,'remaining_substantive_revisions':a.remaining_revisions,'claim':'This form exposed no substantial difficulty in this development round. Not a precise success probability estimate.','rule_provenance':'User correction received after r01; recorded before r02 development.'}
     (a.plan.parent/'development_disposition.json').write_text(json.dumps(disposition,indent=2)+'\n');print(json.dumps(disposition),flush=True);raise SystemExit(0)
print('Declared development attempts complete. Inspect evidence before next stage.',flush=True)
