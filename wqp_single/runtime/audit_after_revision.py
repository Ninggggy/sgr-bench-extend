#!/usr/bin/env python3
"""Serial continuation within the authorized active campaign, not a scheduled automation."""
import argparse,datetime,json,pathlib,subprocess,sys,time
B=pathlib.Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--revision',required=True);a=ap.parse_args();P=B.parent/'candidates/wqp_activity_panel_001'/a.revision/'private'
plan=json.loads((P/'content_run_plan.json').read_text());campaign=json.loads((B.parent/'campaign.json').read_text())
while True:
 if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(campaign['deadline']):raise SystemExit('Campaign deadline reached')
 states=[]
 for j in plan['jobs']:
  f=pathlib.Path(j['out'])/'run.json';states.append(json.loads(f.read_text())['status'] if f.exists() else 'not_started')
 if all(s=='completed' for s in states):break
 if any(s in ['environment_error','runtime_error','invalid_output','timeout','stalled','campaign_deadline'] for s in states):raise SystemExit('An actual attempt needs controller investigation; no automatic retry')
 time.sleep(10)
for adjudication in [False,True]:
 args=[sys.executable,str(B/'audit_revision.py'),'--revision',a.revision]
 if adjudication:args.append('--adjudication')
 print('Starting '+a.revision+(' adjudication' if adjudication else ' independent source audit'),flush=True);subprocess.run(args,check=True)
print('Audit decisions saved. Controller must inspect before any separate difficulty experiment.',flush=True)
