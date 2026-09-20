#!/usr/bin/env python3
"""Recover an interrupted controller's own container without launching a model.

Recovery never certifies an interrupted solve as a valid trial. Completed,
verified runs are left alone; infrastructure retry requires a separate explicit
classification and new attempt directory.
"""
import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from campaign_runtime import existing_state
from archive_io import copy_session_assets


def recover(run, stop_running=False):
    run=Path(run)
    state=existing_state(run)
    if state in ['active','completed']:
        return {'status':'left_unchanged','reason':state}
    metadata=json.loads((run/'run.json').read_text())
    name=metadata['container_name']
    inspected=subprocess.run(['docker','inspect',name],capture_output=True,text=True)
    if inspected.returncode:
        report={'status':'container_unavailable','evidence_already_saved':True,'error':inspected.stderr}
    else:
        inspect=json.loads(inspected.stdout)[0]
        if inspect['HostConfig']['Binds'] or not inspect['HostConfig']['ReadonlyRootfs']:
            raise RuntimeError('Recovery container does not preserve required isolation')
        probe="import os,json; print(json.dumps([int(x) for x in os.listdir('/proc') if x.isdigit() and os.path.exists('/proc/'+x+'/exe') and os.path.realpath('/proc/'+x+'/exe').endswith('/codex')]))"
        checked=subprocess.run(['docker','exec',name,'python3','-c',probe],capture_output=True,text=True)
        processes=json.loads(checked.stdout) if checked.returncode == 0 else []
        if processes and not stop_running:
            return {'status':'model_still_running','container':name,'action':'Leave active execution intact, or explicitly stop it before recovering an interrupted attempt'}
        if processes:
            stop="import os,signal,json; [os.kill(x,signal.SIGTERM) for x in json.loads(os.environ['STOP_PIDS'])]"
            subprocess.run(['docker','exec','-e','STOP_PIDS='+json.dumps(processes),name,'python3','-c',stop],check=True)
        saved=copy_session_assets(name,run,[('/root/.codex/sessions','sessions'),('/work/data','downloaded_data'),('/work/out','solver_output')])
        report={'status':'recovered_interrupted_attempt','files':saved,'container_retained':name,
                'scorable_trial':False,'reason':'Controller interruption requires explicit infrastructure classification; no automatic replay'}
    report['at']=dt.datetime.now(dt.timezone.utc).isoformat()
    (run/'recovery.json').write_text(json.dumps(report,indent=2)+'\n')
    if metadata.get('status') in ['preparing','running']:
        metadata.update(status='controller_interrupted',ended_at=report['at'],recovery_status=report['status'])
        (run/'run.json').write_text(json.dumps(metadata,indent=2)+'\n')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('run',type=Path)
    parser.add_argument('--stop-running',action='store_true')
    args=parser.parse_args()
    print(json.dumps(recover(args.run,args.stop_running),indent=2))
