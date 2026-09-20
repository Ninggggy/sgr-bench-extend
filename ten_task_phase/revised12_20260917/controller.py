"""Run exactly the preregistered fresh trials, at most three workers plus controller."""
import concurrent.futures, datetime as dt, json, subprocess, sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
PLAN=json.loads((BASE/'plan.json').read_text())
RUNTIME=BASE.parent/'runtime'
def save(records):
    (BASE/'execution.json').write_text(json.dumps({'updated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'results':records},ensure_ascii=False,indent=2)+'\n')
def run(job):
    out=Path(job['out'])
    if out.exists():return {'run_id':job['label'],'status':'existing_preserved_no_retry'}
    command=[sys.executable,str(RUNTIME/'run.py'),'--campaign',PLAN['campaign'],'--ledger',PLAN['ledger']]
    for key in ['public','stage','out','label','gold','rules','job_metadata']:
        command.extend(['--'+key.replace('_','-'),job[key]])
    for key in ['model','effort','role','purpose']:command.extend(['--'+key,PLAN[key]])
    (BASE/'logs').mkdir(exist_ok=True)
    with (BASE/'logs'/(job['label']+'.log')).open('x') as f:
        proc=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT)
    meta=json.loads((out/'run.json').read_text()) if (out/'run.json').exists() else {'status':'not_started_runtime_rejection'}
    result={k:meta.get(k) for k in ['status','actual_model','actual_effort','verification_status','elapsed_seconds','errors']}
    result.update(run_id=job['label'],exit_code=proc.returncode)
    if proc.returncode:
        result['log_tail']=(BASE/'logs'/(job['label']+'.log')).read_text()[-2400:]
    return result
def main():
    records={};save(records);jobs=iter(PLAN['jobs']);pending={};exhausted=False
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        while pending or not exhausted:
            while len(pending)<3 and not exhausted:
                try:job=next(jobs)
                except StopIteration:exhausted=True;break
                pending[pool.submit(run,job)]=job
            if not pending:break
            done,_=concurrent.futures.wait(pending,timeout=10,return_when=concurrent.futures.FIRST_COMPLETED)
            for future in done:
                job=pending.pop(future)
                try:r=future.result()
                except Exception as e:r={'run_id':job['label'],'status':'controller_exception','error':repr(e)}
                records[job['label']]=r;save(records);print(json.dumps(r,ensure_ascii=False),flush=True)
                text=json.dumps(r).lower()
                if any(x in text for x in ['usage limit','rate_limit_exceeded','insufficient_quota','model_not_found','authentication_error','not_started_runtime_rejection']):
                    for rest in jobs:records[rest['label']]={'run_id':rest['label'],'status':'not_started_batch_blocked'}
                    exhausted=True;save(records)
    print('BATCH_TERMINAL',flush=True)
if __name__=='__main__':main()
