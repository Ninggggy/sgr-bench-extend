#!/usr/bin/env python3
"""Execute explicit jobs, retaining failed attempts and rechecking completed work."""
import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from campaign_runtime import check_campaign, existing_state

BASE=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--campaign',type=Path,required=True)
    parser.add_argument('--ledger',type=Path,required=True)
    args=parser.parse_args()
    check_campaign(args.campaign,args.ledger)
    plan=json.loads(args.plan.read_text())
    for key in ['campaign','ledger']:
        if plan.get(key) and Path(plan[key]).resolve() != getattr(args,key).resolve():
            raise ValueError(f'Plan {key} differs from explicit batch argument')
    for job in plan['jobs']:
        out=Path(job['out'])
        state=existing_state(out)
        if state == 'completed':
            result=subprocess.run([sys.executable,str(BASE/'verify_run.py'),str(out)],capture_output=True,text=True)
            if result.returncode:
                raise RuntimeError('Previously completed run failed re-verification: '+str(out)+'\n'+result.stderr)
            print(json.dumps({'preserved_completed_run':str(out)}),flush=True)
            continue
        if state == 'active':
            print(json.dumps({'preserved_active_run':str(out)}),flush=True)
            continue
        if state != 'not_started':
            raise RuntimeError(f'{out}: {state}; recover evidence or explicitly schedule an allowed new attempt, never overwrite')
        command=[sys.executable,str(BASE/'run.py'),'--campaign',str(args.campaign.resolve()),
                 '--ledger',str(args.ledger.resolve()),'--public',job['public'],
                 '--stage',job['stage'],'--out',str(out),'--label',job['label']]
        for key in ['gold','rules','schema','assets','model','effort','role','purpose','tools_config','job_metadata','retry_approval']:
            value=job.get(key,plan.get(key))
            if value is not None:
                command+=['--'+key.replace('_','-'),str(value)]
        log=out.parent/(out.name+'.controller.log')
        log.parent.mkdir(parents=True,exist_ok=True)
        # Exclusive log creation catches a prior pre-directory controller failure.
        with log.open('x') as stream:
            print(json.dumps({'started':job['label'],'run':str(out),'at':dt.datetime.now(dt.timezone.utc).isoformat()}),flush=True)
            result=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT)
        metadata=json.loads((out/'run.json').read_text()) if (out/'run.json').exists() else {'status':'controller_did_not_start'}
        print(json.dumps({'finished':job['label'],'status':metadata['status'],'elapsed_seconds':metadata.get('elapsed_seconds')}),flush=True)
        if result.returncode or metadata['status'] != 'completed' or metadata.get('verification_status') != 'passed':
            raise RuntimeError('Stopped on incomplete attempt; preserve evidence and investigate under the explicit repair policy')


if __name__=='__main__':
    main()
