#!/usr/bin/env python3
"""One fresh Docker-isolated Codex solve; never automatically retry."""
import argparse, datetime as dt, json, os, shutil, subprocess as sp, sys, time, uuid
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
IMAGE='sgr-wqp-codex:local'

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def dump(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def cmd(args,**kw):
    r=sp.run(args,text=True,capture_output=True,**kw)
    if r.returncode: raise RuntimeError(f'Command failed ({r.returncode}): {args[:3]}: {r.stderr}')
    return r

def meaningful_output(value):
    """Only real non-error response content advances the stall clock."""
    def failed(x):
        if isinstance(x,str):
            try:return failed(json.loads(x))
            except (ValueError,TypeError):return any(t in x.lower() for t in ['unknownissuer','tool execution failed','error fetching','mcp tool call requires approval'])
        if isinstance(x,list):return any(failed(y) for y in x)
        if isinstance(x,dict):
            if x.get('isError') or x.get('is_error') or x.get('error'):return True
            status=x.get('status')
            if isinstance(status,int) and status>=400:return True
            return any(failed(y) for y in x.values() if isinstance(y,(dict,list,str)))
        return False
    body=json.dumps(value,sort_keys=True)
    return len(body)>120 and not failed(value)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--auth',type=Path,default=Path.home()/'.codex/auth.json')
    ap.add_argument('--public',type=Path,required=True)
    ap.add_argument('--stage',type=Path,required=True)
    ap.add_argument('--schema',type=Path,default=ROOT/'construction_pipeline/schemas/solver_result.schema.json')
    ap.add_argument('--gold',type=Path)
    ap.add_argument('--rules',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--label',default='solve')
    ap.add_argument('--assets',type=Path,help='Explicit audit-only bundle, never use for blind runs')
    args=ap.parse_args()
    campaign_path=BASE.parent/'campaign.json';campaign=json.loads(campaign_path.read_text())
    if dt.datetime.now(dt.timezone.utc)>=dt.datetime.fromisoformat(campaign['deadline']): raise RuntimeError('Campaign wall-clock budget exhausted')
    ledger=BASE.parent/'session_ledger.jsonl'
    count=len(ledger.read_text().splitlines()) if ledger.exists() else 0
    if count>=campaign['max_sessions']: raise RuntimeError('Campaign session budget exhausted')
    run=args.out.resolve();run.mkdir(parents=True,exist_ok=False)
    public=run/'public';public.mkdir()
    payload=json.loads(args.public.read_text())
    assert set(payload) in ({'instruction','output_format'},{'instruction','output_format','current_date'})
    date=dt.datetime.now().astimezone().date().isoformat()
    payload['current_date']=date
    dump(public/'input.json',payload)
    stage=args.stage.read_text()
    (public/'prompt.md').write_text(stage+'\n\nInput JSON:\n'+json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    shutil.copyfile(args.schema,public/'result.schema.json')
    shutil.copyfile(BASE/'solver.config.toml',run/'solver.config.toml')
    for f in ['score.py','test_score.py','run.py','audit_run.py','verify_run.py','Dockerfile','SCORING.md','data_tools.py']:
        if (BASE/f).exists():
            (run/'implementation').mkdir(exist_ok=True);shutil.copyfile(BASE/f,run/'implementation'/f)
    if args.gold:
        assert args.rules and args.rules.exists()
        (run/'controller_scoring').mkdir()
        shutil.copyfile(args.gold,run/'controller_scoring/oracle.psv')
        shutil.copyfile(args.rules,run/'controller_scoring/rules.json')
    name='sgr-solve-'+uuid.uuid4().hex[:12]
    metadata={'controller_label':args.label,'audit_assets':bool(args.assets),'model':'gpt-6-astra','provider':'openai','effort':'high','current_date':date,'controller_timezone':str(dt.datetime.now().astimezone().tzinfo),'started_at':None,'ended_at':None,'elapsed_seconds':None,'status':'preparing','attempt_policy':'one invocation, no automatic retries','maximum_seconds':6000,'stall_seconds':3000,'tools_config':'solver.config.toml','actual_model':'unknown','usage':None,'exit_code':None}
    dump(run/'run.json',metadata)
    process=None;created=False
    try:
        cmd(['docker','create','--name',name,'--read-only','--cap-drop=ALL','--security-opt','no-new-privileges','--pids-limit','128','--memory','2g','--tmpfs','/root:rw,nosuid,nodev,size=256m','--tmpfs','/work:rw,nosuid,nodev,size=768m','--tmpfs','/tmp:rw,nosuid,nodev,size=128m','--workdir','/work','--entrypoint','/bin/sleep',IMAGE,'infinity']);created=True
        cmd(['docker','start',name])
        cmd(['docker','exec',name,'mkdir','-p','/root/.codex','/work/out','/work/data'])
        for source,destination in [(p,'/work/'+p.name) for p in public.iterdir()]+[(args.auth,'/root/.codex/auth.json'),(run/'solver.config.toml','/root/.codex/config.toml')]:
            # Stream through exec: Docker archive copy cannot populate a read-only rootfs.
            r=sp.run(['docker','exec','-i',name,'sh','-c','umask 077; cat > '+destination],input=source.read_bytes(),stdout=sp.DEVNULL,stderr=sp.PIPE)
            if r.returncode: raise RuntimeError('Container input copy failed: '+r.stderr.decode())
        if args.assets:
            if 'audit' not in args.label: raise RuntimeError('Assets are audit only')
            for source in args.assets.iterdir():
                if not source.is_file() or '/' in source.name: raise RuntimeError('Audit bundle must contain regular files')
                dest='/work/data/'+source.name
                r=sp.run(['docker','exec','-i',name,'sh','-c','umask 077; cat > '+dest],input=source.read_bytes(),stdout=sp.DEVNULL,stderr=sp.PIPE)
                if r.returncode: raise RuntimeError('Audit copy failed')
        marker=run/'private_probe.txt';marker.write_text('NON-SENSITIVE ISOLATION PROBE\n')
        probe_script='''const fs=require('fs'); const paths=JSON.parse(process.argv[1]); let out=[]; for(const p of paths){try{fs.readFileSync(p);out.push({path:p,readable:true})}catch(e){out.push({path:p,readable:false,error:e.code})}}; console.log(JSON.stringify(out)); if(out.some(x=>x.readable))process.exit(2);'''
        paths=[str(marker),str(ROOT/'runs/open-source/sgr-bench/constraint.jsonl'),str(Path.home()/'.codex/sessions'),'/var/run/docker.sock','/host','/mnt/host']
        probe=cmd(['docker','exec',name,'node','-e',probe_script,json.dumps(paths)])
        inspect=json.loads(cmd(['docker','inspect',name]).stdout)[0]
        isolation={'checked_at':now(),'method':'Docker mount namespace, clean image, no bind mounts or Docker socket, empty tmpfs home/work, only public input/schema and auth/config copied','probe':json.loads(probe.stdout),'bind_mounts':inspect['Mounts'],'read_only_rootfs':inspect['HostConfig']['ReadonlyRootfs'],'cap_drop':inspect['HostConfig']['CapDrop'],'security_opt':inspect['HostConfig']['SecurityOpt'],'image_id':inspect['Image'],'network':'Docker bridge; no host network; native live web plus bounded official HTTPS/CSV MCP; shell, apps and delegation disabled','auth':'Existing auth copied to container tmpfs; never delivered as prompt or retained in results','history':'No resume/fork; clean home; only this run sessions persisted inside container and copied out after completion'}
        inventory_script="import pathlib,json; print(json.dumps([{'path':str(x),'bytes':x.stat().st_size} for d in ['/work','/opt/wqp'] for x in pathlib.Path(d).rglob('*') if x.is_file()]))"
        invfiles=json.loads(cmd(['docker','exec',name,'python3','-c',inventory_script]).stdout)
        dump(run/'input_inventory.json',{'recorded_at':now(),'stage':'before_codex_invocation','copied_public_files':[p.name for p in public.iterdir()],'auth':'one existing auth.json in tmpfs home; filename disclosed, contents never archived','data_and_tool_files':invfiles,'audit_assets':bool(args.assets),'host_mounts':inspect['Mounts']})
        dump(run/'isolation.json',isolation)
        if inspect['Mounts']: raise RuntimeError('Unexpected mounted host data')
        version=cmd(['docker','exec',name,'codex','--version']).stdout.strip();metadata['cli_version']=version
        (run/'cli_help.txt').write_text(cmd(['docker','exec',name,'codex','exec','--help']).stdout)
        (run/'features.txt').write_text(cmd(['docker','exec',name,'codex','features','list']).stdout)
        invocation=['docker','exec','-i',name,'codex','exec','--strict-config','--model','gpt-6-astra','-c','model_reasoning_effort="high"','--cd','/work','--skip-git-repo-check','--sandbox','read-only','--json','--output-schema','/work/result.schema.json','--output-last-message','/work/out/result.json','-']
        dump(run/'invocation.json',invocation)
        metadata['started_at']=now();metadata['status']='running';dump(run/'run.json',metadata)
        import fcntl
        with ledger.open('a+') as f:
            fcntl.flock(f.fileno(),fcntl.LOCK_EX);f.seek(0)
            allocated=len(f.read().splitlines())
            if allocated>=campaign['max_sessions']:raise RuntimeError('Campaign session budget exhausted at invocation')
            f.write(json.dumps({'session_number':allocated+1,'run_dir':str(run.relative_to(BASE.parent)),'label':args.label,'started_at':metadata['started_at'],'model':'gpt-6-astra','effort':'high'})+'\n');f.flush()
            fcntl.flock(f.fileno(),fcntl.LOCK_UN)

        started=time.monotonic();last_progress=started;last_size=0;seen_progress=set();session_offsets={};last_trace_check=started
        with (run/'events.jsonl').open('w') as events,(run/'runner.stderr').open('w') as err,(public/'prompt.md').open() as prompt:
            process=sp.Popen(invocation,stdin=prompt,stdout=events,stderr=err,start_new_session=True)
            reason='exited'
            while process.poll() is None:
                time.sleep(5)
                size=(run/'events.jsonl').stat().st_size
                if size!=last_size:
                    # Do not treat repeated retry/error messages as substantive progress.
                    with (run/'events.jsonl').open() as f: f.seek(last_size);new=f.read()
                    for line in new.splitlines():
                        try:
                            event=json.loads(line)
                            item=event.get('item',{})
                            meaningful=event.get('type')=='turn.completed'
                            if event.get('type')=='item.completed' and item.get('type') not in ['error','reasoning','agent_message']:
                                body=json.dumps(item.get('result',item.get('aggregated_output',item.get('text',''))),sort_keys=True)
                                failed=item.get('error') or item.get('status')=='failed' or (isinstance(item.get('result'),dict) and item['result'].get('isError'))
                                if not failed and meaningful_output(item.get('result',item.get('aggregated_output',''))) and body not in seen_progress:
                                    meaningful=True;seen_progress.add(body)
                            if meaningful: last_progress=time.monotonic()
                        except json.JSONDecodeError: pass
                    last_size=size
                if time.monotonic()-last_trace_check>=20:
                    # CLI web summaries have no response bodies. Inspect actual local rollout responses.
                    trace_script="const fs=require('fs');const offsets=JSON.parse(process.argv[1]);const base='/root/.codex/sessions';let out=[];function walk(d){for(const e of fs.readdirSync(d,{withFileTypes:true})){let p=d+'/'+e.name;if(e.isDirectory())walk(p);else{let b=fs.readFileSync(p);let from=offsets[p]||0;let tail=b.subarray(from).toString();let end=tail.lastIndexOf('\\n');if(end>=0){out.push({path:p,offset:from+Buffer.byteLength(tail.slice(0,end+1)),records:tail.slice(0,end).split('\\n').flatMap(l=>{try{let r=JSON.parse(l);return r.type==='response_item'&&['custom_tool_call_output','function_call_output'].includes(r.payload?.type)?[r]:[]}catch{return[]}})})}}}}if(fs.existsSync(base))walk(base);console.log(JSON.stringify(out));"
                    traces=sp.run(['docker','exec',name,'node','-e',trace_script,json.dumps(session_offsets)],capture_output=True,text=True)
                    if traces.returncode==0:
                        for f in json.loads(traces.stdout):
                            session_offsets[f['path']]=f['offset']
                            for record in f['records']:
                                body=json.dumps(record['payload'].get('output',''),sort_keys=True)
                                # Explicit errors, empty wrappers and repeated identical outputs do not reset stall.
                                failed=any(x in body.lower() for x in ['iserror\\":true','iserror\\": true','unknownissuer','tool execution failed','error fetching'])
                                if meaningful_output(record['payload'].get('output','')) and body not in seen_progress:
                                    seen_progress.add(body);last_progress=time.monotonic()
                    last_trace_check=time.monotonic()
                elapsed=time.monotonic()-started
                if elapsed>6000 or time.monotonic()-last_progress>3000 or dt.datetime.now(dt.timezone.utc)>=dt.datetime.fromisoformat(campaign['deadline']):
                    reason='timeout' if elapsed>6000 else 'campaign_deadline' if dt.datetime.now(dt.timezone.utc)>=dt.datetime.fromisoformat(campaign['deadline']) else 'stalled'
                    stop_script="const fs=require('fs');for(const p of fs.readdirSync('/proc').filter(x=>/^\\d+$/.test(x))){try{if(fs.readlinkSync('/proc/'+p+'/exe').endsWith('/codex'))process.kill(Number(p),'SIGTERM')}catch(e){}}"
                    cmd(['docker','exec',name,'node','-e',stop_script]);break
            try: process.wait(timeout=30)
            except sp.TimeoutExpired:
                reason='forced_stop_after_timeout'
                cmd(['docker','stop','-t','10',name])
                process.wait(timeout=30)
        metadata.update(ended_at=now(),elapsed_seconds=round(time.monotonic()-started,3),exit_code=process.returncode,ending_reason=reason)
        # Copy this session's data only, without the auth/config home directory.
        (run/'solver_output').mkdir(exist_ok=True)
        copied=sp.run(['docker','exec',name,'cat','/work/out/result.json'],capture_output=True)
        if copied.returncode==0: (run/'solver_output/result.json').write_bytes(copied.stdout)
        else: (run/'copy_errors.txt').write_bytes(copied.stderr)
        session_script="const fs=require('fs'),p='/root/.codex/sessions'; function walk(d){return fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(d+'/'+e.name):[{name:e.name,text:fs.readFileSync(d+'/'+e.name,'utf8')}])};console.log(JSON.stringify(fs.existsSync(p)?walk(p):[]));"
        copied=sp.run(['docker','exec',name,'node','-e',session_script],capture_output=True,text=True)
        if copied.returncode==0:
            (run/'sessions').mkdir(exist_ok=True)
            for f in json.loads(copied.stdout): (run/'sessions'/Path(f['name']).name).write_text(f['text'])
        # Recover only this session's public downloads/computations, never auth.
        recovery_script="import pathlib,base64,json; p=pathlib.Path('/work/data'); print(json.dumps([{'name':x.name,'data':base64.b64encode(x.read_bytes()).decode()} for x in p.iterdir() if x.is_file()]))"
        recovered=sp.run(['docker','exec',name,'python3','-c',recovery_script],capture_output=True,text=True)
        if recovered.returncode: (run/'data_copy_error.txt').write_text(recovered.stderr)
        else:
            import base64
            (run/'downloaded_data').mkdir(exist_ok=True)
            for saved in json.loads(recovered.stdout):
                assert Path(saved['name']).name==saved['name']
                (run/'downloaded_data'/saved['name']).write_bytes(base64.b64decode(saved['data']))
            dump(run/'data_recovery.json',{'method':'explicit regular files through docker exec; Docker archive API does not see this tmpfs','files':len(json.loads(recovered.stdout)),'successful':True})
        raw=run/'solver_output/result.json' 
        metadata['answer_ready']=raw.is_file()
        events=[]
        for line in (run/'events.jsonl').read_text().splitlines():
            try: events.append(json.loads(line))
            except json.JSONDecodeError: pass
        metadata['completed_event']=any(e.get('type')=='turn.completed' for e in events)
        metadata['usage']=next((e.get('usage') for e in reversed(events) if e.get('type')=='turn.completed'),None)
        metadata['errors']=[e for e in events if e.get('type') in ['error','turn.failed']]
        metadata['status']='completed' if process.returncode==0 and metadata['completed_event'] else reason if reason!='exited' else 'runtime_error'
        if raw.is_file():
            try:
                result=json.loads(raw.read_text())
                schema=json.loads((public/'result.schema.json').read_text())
                assert set(result)==set(schema['properties'])
                assert set(schema['required'])<=set(result)
                for field,definition in schema['properties'].items():
                    typ=definition.get('type')
                    if typ=='string': assert isinstance(result[field],str)
                    if typ=='array': assert isinstance(result[field],list)
                    if typ=='object': assert isinstance(result[field],dict)
                    if typ=='integer': assert isinstance(result[field],int)
                    if 'enum' in definition: assert result[field] in definition['enum']
                metadata['model_reported_status']=result.get('status')
                metadata['model_content_verdict']=result.get('content_verdict')
                dump(run/'extraction.json',{'status':'valid','source':'solver_output/result.json','kind':'nonblind_stage_structured_output','transformations':[],'schema':'public/result.schema.json','validation_scope':'Top-level exact keys/types/enums; CLI output-schema constrains generation; independent adjudication still required.'})
            except Exception as e:
                metadata['status']='invalid_output';dump(run/'extraction.json',{'status':'error','error':str(e)})
        for path in (run/'sessions').rglob('*.jsonl'):
            for line in path.read_text().splitlines():
                try:
                    ev=json.loads(line)
                    if ev.get('type')=='turn_context': metadata['actual_model']=ev.get('payload',{}).get('model','unknown')
                except json.JSONDecodeError: pass
    except Exception as e:
        metadata.update(status='environment_error',error=f'{type(e).__name__}: {e}',ended_at=now())
        (run/'controller_error.txt').write_text(metadata['error']+'\n')
    finally:
        if created: sp.run(['docker','rm','-f',name],capture_output=True)
        if process and process.poll() is None: process.terminate()
        dump(run/'run.json',metadata)
    if (run/'sessions').exists():
        checked=sp.run([sys.executable,str(BASE/'verify_run.py'),str(run)],capture_output=True,text=True)
        (run/'verification_stdout.txt').write_text(checked.stdout+checked.stderr)
    print(json.dumps({'directory':str(run),**metadata},ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()
