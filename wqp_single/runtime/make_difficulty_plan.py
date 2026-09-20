#!/usr/bin/env python3
"""Create a fixed comparison plan after factual review; never replace existing attempts."""
import argparse,datetime as dt,json,pathlib,uuid
B=pathlib.Path(__file__).resolve().parent.parent;ROOT=B.parents[1];REV=B/'candidates/wqp_activity_panel_001'/('r'+str(json.loads((B/'comparisons/analysis_plan.json').read_text())['revision']).zfill(2));P=REV/'private';C=B/'comparisons'
p=argparse.ArgumentParser();p.add_argument('--phase',choices=['screening','confirmation'],required=True);a=p.parse_args()
decision=json.loads((P/'decision.json').read_text());assert decision['content_verdict']=='ready_for_difficulty_test','Content adjudication does not support proceeding to difficulty tests'
out=C/(a.phase+'_run_plan.json');assert not out.exists(),'Never overwrite an existing run plan'
if a.phase=='confirmation':
 screen=json.loads((C/'screening_run_plan.json').read_text())
 assert all((pathlib.Path(j['out'])/'run.json').exists() and json.loads((pathlib.Path(j['out'])/'run.json').read_text()).get('completed_event') for j in screen['jobs']), 'Screening attempts must finish before a fresh confirmation plan is created'
 n=3
else:n=1
jobs=[]
for rep in range(1,n+1):
 for task,variant in [('new','cg'),('old','cg'),('new','go'),('old','go')]:
  jobs.append({'phase':a.phase,'comparison_task':task,'replicate':rep,'variant':variant,'label':f'{a.phase}_{task}_{variant.upper()}_{rep}','public':str(REV/'public'/f'{variant}.json') if task=='new' else str(C/f'old004_{variant}_public.json'),'stage':str(ROOT/'construction_pipeline/prompts/04_blind_solver.md'),'out':str(REV/'runs'/('r-'+uuid.uuid4().hex[:12])),'gold':str(P/'reference/oracle.psv') if task=='new' else str(C/'old004_oracle.psv'),'rules':str(P/'scoring_rules.json') if task=='new' else str(C/'old004_rules.json')})
out.write_text(json.dumps({'created_at':dt.datetime.now(dt.timezone.utc).isoformat(),'phase':a.phase,'candidate':'wqp_activity_panel_001/'+REV.name,'old_comparison':'waterquality_004','jobs':jobs,'retries':'No score-dependent repeats; all predetermined jobs remain in report','independence':'Fresh clean containers, no resume/fork, interleaved order; replicate numbers do not imply statistical pairing'},indent=2)+'\n')
print(str(out))
