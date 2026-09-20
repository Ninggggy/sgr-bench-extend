#!/usr/bin/env python3
"""Read-only checks of originals and completed Sol deliverables; saves local report."""
import datetime as dt,json,pathlib,tomllib
T=pathlib.Path(__file__).resolve().parent;B=T.parent;R=B/'candidates/wqp_activity_panel_001/r03';ROOT=B.parents[1]
def read(p):return json.loads(p.read_text())
def main():
 plan=read(T/'analysis_plan.json');campaign=read(T/'campaign.json');checks=[]
 for f in ['campaign.json','session_ledger.jsonl','comparisons/analysis_plan.json','README.md','report.md']:
  assert (B/f).read_bytes()==(T/'preserved_original'/f).read_bytes(),f
 checks.append('Original GPT-6 campaign, ledger, plan, README and report byte-identical')
 for task in ['new','old']:
  for v in ['cg','go']:
   src=R/'public'/f'{v}.json' if task=='new' else B/'comparisons'/f'old004_{v}_public.json'
   assert src.read_bytes()==(T/'inputs'/f'{task}_{v}.json').read_bytes()
  for kind,src in [('oracle.psv',R/'private/reference/oracle.psv' if task=='new' else B/'comparisons/old004_oracle.psv'),('rules.json',R/'private/scoring_rules.json' if task=='new' else B/'comparisons/old004_rules.json')]:assert src.read_bytes()==(T/'controller_reference'/f'{task}_{kind}').read_bytes()
 assert (T/'inputs/stage.md').read_bytes()==(ROOT/'construction_pipeline/prompts/04_blind_solver.md').read_bytes()
 assert (T/'inputs/result.schema.json').read_bytes()==(ROOT/'construction_pipeline/schemas/solver_result.schema.json').read_bytes()
 checks.append('All four public forms, two oracles/rules, stage and schema unchanged')
 ledger=[json.loads(l) for l in (T/'session_ledger.jsonl').read_text().splitlines()];assert len(ledger)<=17 and [x['session_number'] for x in ledger]==list(range(1,len(ledger)+1))
 assert all(x['model']=='gpt-5.6-sol' and x['effort']=='medium' for x in ledger)
 assert len({x['run_dir'] for x in ledger})==len(ledger)
 configs=[];threads=[];times=[];completed=[]
 for j in plan['jobs']:
  run=pathlib.Path(j['out']);m=read(run/'run.json');v=read(run/'verification.json');assert m['status']=='completed' and v['status']=='passed' and v['exact_extraction'] and v['scored']
  assert m['maximum_seconds']==6000 and m['stall_seconds']==3000 and m['actual_model']=='gpt-5.6-sol' and m['actual_effort']=='medium'
  assert any(x['run_dir']==str(run.relative_to(T)) for x in ledger)
  payload=read(run/'public/input.json');assert {k:val for k,val in payload.items() if k!='current_date'}==read(pathlib.Path(j['public']))
  for n,source in [('oracle.psv','gold'),('rules.json','rules')]:assert (run/'controller_scoring'/n).read_bytes()==pathlib.Path(j[source]).read_bytes()
  assert (run/'implementation/score.py').read_bytes()==(B/'runtime/score.py').read_bytes()
  assert (run/'implementation/data_tools.py').read_bytes()==(B/'runtime/data_tools.py').read_bytes()
  cfg=tomllib.loads((run/'solver.config.toml').read_text());assert cfg['model']=='gpt-5.6-sol' and cfg['model_reasoning_effort']=='medium';configs.append(cfg)
  iso=read(run/'isolation.json');inv=read(run/'input_inventory.json');assert not iso['bind_mounts'] and iso['read_only_rootfs'] and not inv['audit_assets'] and all(not p['readable'] for p in iso['probe'])
  recovery=read(run/'data_recovery.json');assert recovery['successful']
  assert read(run/'solver_output/result.json')['final_answer']==(run/'answer.txt').read_text()
  for line in (run/'events.jsonl').read_text().splitlines():
   e=json.loads(line)
   if e['type']=='thread.started':threads.append(e['thread_id'])
  times.append(m['elapsed_seconds']);completed.append({'label':j['label'],'run':str(run.relative_to(T)),'model':v['model'],'effort':v['effort'],'verified_turn_contexts':v['verified_turn_contexts'],'scored':v['scored'],'data_files':recovery['files'],'elapsed_seconds':m['elapsed_seconds']})
 assert len(completed)==16 and len(ledger)==16 and len(set(threads))==16
 assert all(c==configs[0] for c in configs)
 template=tomllib.loads((B/'runtime/solver.config.toml').read_text());template.update(model='gpt-5.6-sol',model_reasoning_effort='medium');assert configs[0]==template
 checks+=['16 distinct fresh model sessions match independent ledger; no repair retry used','Every run model verified in four sources; same tools/configuration, read isolation, public input, gold and rules','Per-run raw extraction and saved-score verification passed; downloaded data archived']
 end=dt.datetime.fromisoformat(campaign['ended_at']) if campaign.get('ended_at') else dt.datetime.now(dt.timezone.utc);start=dt.datetime.fromisoformat(campaign['started_at']);wall=(end-start).total_seconds();assert wall<=86400 and max(times)<=6005
 result={'checked_at':dt.datetime.now(dt.timezone.utc).isoformat(),'status':'passed','checks':checks,'completed':completed,'model_sessions':len(ledger),'repair_retries':0,'wall_seconds':wall,'sum_run_seconds':sum(times),'note':'Only artifact/configuration checks. Does not prove SGR compliance, uniqueness of old004 public selection, population difficulty or lack of prior benchmark exposure.'}
 (T/'delivery_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'passed','sessions':len(ledger),'wall_seconds':wall}))
if __name__=='__main__':main()
