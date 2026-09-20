#!/usr/bin/env python3
"""Continue this turn's already authorized serial audit after all six prescribed solves."""
import json,pathlib,subprocess,sys,time,datetime
B=pathlib.Path(__file__).resolve().parent;P=B.parent/'candidates/wqp_activity_panel_001/r01/private'
campaign=json.loads((B.parent/'campaign.json').read_text());plan=json.loads((P/'content_run_plan.json').read_text())
while True:
 if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(campaign['deadline']):raise SystemExit('Campaign deadline reached')
 states=[]
 for j in plan['jobs']:
  p=pathlib.Path(j['out'])/'run.json';states.append(json.loads(p.read_text())['status'] if p.exists() else 'not_started')
 if all(s=='completed' for s in states):break
 if any(s in ['environment_error','runtime_error'] for s in states):raise SystemExit('Content environment failure requires controller investigation, no auto retry')
 time.sleep(10)
for adjudicate in [False,True]:
 args=[sys.executable,str(B/'start_audit.py')]
 if adjudicate:args+=['--adjudication']
 print('Starting '+('independent adjudication' if adjudicate else 'independent source audit'),flush=True)
 subprocess.run(args,check=True)
print('Content audit and adjudication complete. Controller must inspect the decision before difficulty runs.',flush=True)
