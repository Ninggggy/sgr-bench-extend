import concurrent.futures,datetime,json,pathlib,subprocess,sys,time
base=pathlib.Path(sys.argv[1]).resolve();plan=json.loads((base/'plan.json').read_text());runtime=base.parents[1]/'runtime'
# The run directory is nested under rolling_five; runtime is at ten_task_phase/runtime.
runtime=base.parent.parent/'runtime'
records={}
def save():
 result={'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'planned':len(plan['jobs']),'results':records,'excluded':['europemc_balf_provenance_001'],'access_audit':'pending; raw scores are not compliant scores'}
 from fractions import Fraction
 for variant in ['CG','GO']:
  vals=[Fraction(r['item_f1_exact']) for r in records.values() if r.get('variant')==variant and r.get('item_f1_exact') is not None]
  result[variant]={'scored':len(vals),'planned':30,'raw_macro_mean_exact':str(sum(vals,Fraction())/len(vals)) if vals else None}
 (base/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
def run(job):
 out=pathlib.Path(job['out']);meta=json.loads(pathlib.Path(job['job_metadata']).read_text());res={'variant':meta['variant'],'candidate_id':meta['candidate_id'],'run_id':job['label']}
 if out.exists():return {**res,'status':'existing_run_preserved'}
 if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(plan['deadline']):return {**res,'status':'not_started_deadline'}
 command=[sys.executable,str(runtime/'run.py'),'--campaign',plan['campaign'],'--ledger',plan['ledger']]
 for k in ['public','stage','out','label','gold','rules','job_metadata']:command+=['--'+k.replace('_','-'),job[k]]
 for k in ['model','effort','role','purpose']:command+=['--'+k,plan[k]]
 (base/'logs').mkdir(exist_ok=True)
 with (base/'logs'/(job['label']+'.log')).open('x') as log:
  proc=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 res['exit_code']=proc.returncode
 if (out/'run.json').exists():
  m=json.loads((out/'run.json').read_text());res.update({k:m.get(k) for k in ['status','actual_model','actual_effort','elapsed_seconds','started_at','ended_at']});res['errors']=m.get('errors',[])
 else:res['status']='not_started_runtime_rejection'
 f=out/'scoring/scores.json'
 if f.exists():
  s=json.loads(f.read_text());c=s.get('counts',{});n=c.get('correct_fields');d=c.get('item_denominator')
  if isinstance(n,int) and isinstance(d,int) and d>0 and isinstance((s.get('metrics') or {}).get('Item-F1'),(int,float)):
   from fractions import Fraction
   res['item_f1_exact']=str(Fraction(2*n,d));res['counts']=c
 return res
save()
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 pending={}; jobs=iter(plan['jobs']);exhausted=False
 while pending or not exhausted:
  while len(pending)<2 and not exhausted:
   try:job=next(jobs)
   except StopIteration:exhausted=True;break
   pending[pool.submit(run,job)]=job
  done,_=concurrent.futures.wait(pending,timeout=10,return_when=concurrent.futures.FIRST_COMPLETED)
  for future in done:
   job=pending.pop(future)
   try:record=future.result()
   except Exception as e:record={'status':'controller_exception','error':str(e),'run_id':job['label']}
   records[job['label']]=record;save();print(json.dumps(record),flush=True)
   if any(t in json.dumps(record.get('errors',[])).lower() for t in ['usage limit','rate_limit_exceeded','insufficient_quota']):
    for rest in jobs: records[rest['label']]={'status':'not_started_quota','run_id':rest['label']}
    exhausted=True;save()
print('BATCH_TERMINAL',flush=True)
