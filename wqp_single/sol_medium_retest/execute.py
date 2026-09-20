#!/usr/bin/env python3
"""Execute only the fixed Sol slots; never create attempts or retry automatically."""
import argparse,concurrent.futures,datetime as dt,json,pathlib,subprocess,sys
T=pathlib.Path(__file__).resolve().parent

def execute(job):
 out=pathlib.Path(job['out'])
 if out.exists():
  meta=json.loads((out/'run.json').read_text())
  if meta['status'] in ['preparing','running']:raise RuntimeError('Existing active attempt: '+job['label'])
  print(json.dumps({'existing_no_rerun':job['label'],'status':meta['status']}),flush=True)
  return meta
 args=[sys.executable,str(T.parent/'runtime/run.py')]
 for k in ['public','stage','schema','gold','rules','out','label','model','effort','campaign','ledger']:args+=['--'+k,job[k]]
 out.parent.mkdir(parents=True,exist_ok=True)
 print(json.dumps({'start':job['label'],'at':dt.datetime.now(dt.timezone.utc).isoformat()}),flush=True)
 with (out.parent/(out.name+'.controller.log')).open('x') as f:r=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT)
 meta=json.loads((out/'run.json').read_text()) if (out/'run.json').exists() else {'status':'controller_did_not_start'}
 print(json.dumps({'finish':job['label'],'status':meta['status'],'seconds':meta.get('elapsed_seconds')}),flush=True)
 if r.returncode or meta['status'] in ['environment_error','runtime_error','verification_failed','controller_did_not_start']:raise RuntimeError('Fault: '+job['label']+'; preserve attempt, no automatic retry')
 return meta

def main():
 p=argparse.ArgumentParser();p.add_argument('phase',choices=['first','screening_rest','confirmation']);a=p.parse_args()
 jobs=json.loads((T/'analysis_plan.json').read_text())['jobs']
 if a.phase=='first':execute(jobs[0]);return
 review=json.loads((T/'first_run_review.json').read_text());assert review['proceed']
 if a.phase=='confirmation':assert json.loads((T/'screening_review.json').read_text())['proceed']
 jobs=[j for j in jobs if j['phase']==('screening' if a.phase=='screening_rest' else 'confirmation')]
 if a.phase=='screening_rest':jobs=jobs[1:]
 # Do not enqueue beyond four until a worker succeeds; a fault prevents new starts.
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  pending={};it=iter(jobs)
  for j in [next(it,None) for _ in range(min(4,len(jobs)))]:pending[pool.submit(execute,j)]=j
  try:
   while pending:
    done,_=concurrent.futures.wait(pending,return_when=concurrent.futures.FIRST_COMPLETED)
    for f in done:f.result();del pending[f]
    for _ in done:
     j=next(it,None)
     if j:pending[pool.submit(execute,j)]=j
  except Exception:
   for f in pending:f.cancel()
   raise
if __name__=='__main__':main()
