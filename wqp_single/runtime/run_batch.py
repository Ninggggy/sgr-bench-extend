#!/usr/bin/env python3
"""Execute a prespecified list serially, no automatic retries or score-dependent additions."""
import argparse,datetime as dt,json,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,required=True);a=p.parse_args();plan=json.loads(a.plan.read_text())
for job in plan['jobs']:
 out=Path(job['out'])
 if out.exists():
  print(json.dumps({'skipped_existing_run_no_overwrite':str(out)}),flush=True)
  continue
 args=[sys.executable,str(B/'run.py'),'--public',job['public'],'--stage',job['stage'],'--out',str(out),'--label',job['label']]
 for k in ['gold','rules','schema','assets']:
  if job.get(k):args+=['--'+k,job[k]]
 for k in ['model','effort']:
  value=job.get(k,plan.get(k))
  if value is not None:args+=['--'+k,value]
 log=out.parent/(out.name+'.controller.log');log.parent.mkdir(parents=True,exist_ok=True)
 print(json.dumps({'started':job['label'],'run':str(out),'at':dt.datetime.now(dt.timezone.utc).isoformat()}),flush=True)
 with log.open('w') as f:r=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT)
 meta=json.loads((out/'run.json').read_text()) if (out/'run.json').exists() else {'status':'controller_did_not_start'}
 print(json.dumps({'finished':job['label'],'status':meta['status'],'elapsed_seconds':meta.get('elapsed_seconds'),'at':dt.datetime.now(dt.timezone.utc).isoformat()}),flush=True)
 if r.returncode or meta['status'] in ['environment_error','runtime_error','verification_failed','controller_did_not_start']:
  print('Stopped on environment/controller/verification error; preserve attempt and investigate without automatic retry.',flush=True);sys.exit(2)
