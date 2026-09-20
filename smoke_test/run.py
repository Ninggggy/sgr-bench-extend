#!/usr/bin/env python3
"""One fresh Docker-isolated Codex solve; never automatically retry."""
import argparse, datetime as dt, json, os, shutil, subprocess as sp, sys, time, uuid
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
IMAGE='sgr-smoke-codex:local'

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def dump(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def cmd(args,**kw):
    r=sp.run(args,text=True,capture_output=True,**kw)
    if r.returncode: raise RuntimeError(f'Command failed ({r.returncode}): {args[:3]}: {r.stderr}')
    return r

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--auth',type=Path,default=Path.home()/'.codex/auth.json');args=ap.parse_args()
    ids=[int(p.name) for p in (BASE/'runs').glob('[0-9][0-9][0-9]')] if (BASE/'runs').exists() else []
    run=BASE/'runs'/f'{max(ids,default=0)+1:03d}';run.mkdir(parents=True)
    public=run/'public';public.mkdir()
    date=dt.datetime.now().astimezone().date().isoformat()
    prep=ROOT/'construction_pipeline/scripts/prepare.py'
    cmd([sys.executable,str(prep),'public','--task',str(ROOT/'runs/open-source/sgr-bench/constraint.jsonl'),'--task-id','arxiv_001','--date',date,'--out',str(public/'input.json')])
    cmd([sys.executable,str(prep),'render','--stage','04_blind_solver','--input',str(public/'input.json'),'--out',str(public/'prompt.md')])
    shutil.copyfile(ROOT/'construction_pipeline/schemas/solver_result.schema.json',public/'result.schema.json')
    config='''model = "gpt-6-astra"
model_provider = "openai"
model_reasoning_effort = "high"
web_search = "live"
approval_policy = "never"
sandbox_mode = "read-only"
[features]
shell_tool = false
unified_exec = false
shell_snapshot = false
apps = false
multi_agent = false
multi_agent_v2 = false
'''
    (run/'solver.config.toml').write_text(config)
    # Run and retain the independent scoring checks before any model invocation.
    tests=sp.run([sys.executable,'-m','unittest','discover','-s',str(BASE),'-p','test_score.py','-v'],capture_output=True,text=True)
    (run/'scoring_tests.txt').write_text('Artificial fixtures only; completed '+now()+'\n'+tests.stdout+tests.stderr)
    if tests.returncode: raise RuntimeError('Scoring checks failed')
    for f in ['score.py','test_score.py','run.py','Dockerfile','SCORING.md']:
        if (BASE/f).exists():
            (run/'implementation').mkdir(exist_ok=True);shutil.copyfile(BASE/f,run/'implementation'/f)
    name='sgr-solve-'+uuid.uuid4().hex[:12]
    metadata={'task_id':'arxiv_001','variant':'CG','model':'gpt-6-astra','provider':'openai','effort':'high','current_date':date,'controller_timezone':str(dt.datetime.now().astimezone().tzinfo),'started_at':None,'ended_at':None,'elapsed_seconds':None,'status':'preparing','attempt_policy':'one invocation, no automatic retries','maximum_seconds':6000,'stall_seconds':3000,'tools_config':'solver.config.toml','actual_model':'unknown','usage':None,'exit_code':None}
    dump(run/'run.json',metadata)
    process=None;created=False
    try:
        cmd(['docker','create','--name',name,'--read-only','--cap-drop=ALL','--security-opt','no-new-privileges','--pids-limit','128','--memory','2g','--tmpfs','/root:rw,nosuid,nodev,size=256m','--tmpfs','/work:rw,nosuid,nodev,size=256m','--tmpfs','/tmp:rw,nosuid,nodev,size=128m','--workdir','/work','--entrypoint','/bin/sleep',IMAGE,'infinity']);created=True
        cmd(['docker','start',name])
        cmd(['docker','exec',name,'mkdir','-p','/root/.codex','/work/out'])
        for source,destination in [(p,'/work/'+p.name) for p in public.iterdir()]+[(args.auth,'/root/.codex/auth.json'),(run/'solver.config.toml','/root/.codex/config.toml')]:
            # Stream through exec: Docker archive copy cannot populate a read-only rootfs.
            r=sp.run(['docker','exec','-i',name,'sh','-c','umask 077; cat > '+destination],input=source.read_bytes(),stdout=sp.DEVNULL,stderr=sp.PIPE)
            if r.returncode: raise RuntimeError('Container input copy failed: '+r.stderr.decode())
        marker=run/'private_probe.txt';marker.write_text('NON-SENSITIVE ISOLATION PROBE\n')
        probe_script='''const fs=require('fs'); const paths=JSON.parse(process.argv[1]); let out=[]; for(const p of paths){try{fs.readFileSync(p);out.push({path:p,readable:true})}catch(e){out.push({path:p,readable:false,error:e.code})}}; console.log(JSON.stringify(out)); if(out.some(x=>x.readable))process.exit(2);'''
        paths=[str(marker),str(ROOT/'runs/open-source/sgr-bench/constraint.jsonl'),str(Path.home()/'.codex/sessions'),'/var/run/docker.sock','/host','/mnt/host']
        probe=cmd(['docker','exec',name,'node','-e',probe_script,json.dumps(paths)])
        inspect=json.loads(cmd(['docker','inspect',name]).stdout)[0]
        isolation={'checked_at':now(),'method':'Docker mount namespace, clean image, no bind mounts or Docker socket, empty tmpfs home/work, only public input/schema and auth/config copied','probe':json.loads(probe.stdout),'bind_mounts':inspect['Mounts'],'read_only_rootfs':inspect['HostConfig']['ReadonlyRootfs'],'cap_drop':inspect['HostConfig']['CapDrop'],'security_opt':inspect['HostConfig']['SecurityOpt'],'image_id':inspect['Image'],'network':'Docker bridge; no host network; solver has native remote web tool only, shell and apps/MCP/delegation disabled','auth':'Existing auth copied to container tmpfs; never delivered as prompt or retained in results','history':'No resume/fork; clean home; only this run sessions persisted inside container and copied out after completion'}
        dump(run/'isolation.json',isolation)
        if inspect['Mounts']: raise RuntimeError('Unexpected mounted host data')
        version=cmd(['docker','exec',name,'codex','--version']).stdout.strip();metadata['cli_version']=version
        (run/'cli_help.txt').write_text(cmd(['docker','exec',name,'codex','exec','--help']).stdout)
        (run/'features.txt').write_text(cmd(['docker','exec',name,'codex','features','list']).stdout)
        invocation=['docker','exec','-i',name,'codex','exec','--strict-config','--model','gpt-6-astra','-c','model_reasoning_effort="high"','--cd','/work','--skip-git-repo-check','--sandbox','read-only','--json','--output-schema','/work/result.schema.json','--output-last-message','/work/out/result.json','-']
        dump(run/'invocation.json',invocation)
        metadata['started_at']=now();metadata['status']='running';dump(run/'run.json',metadata)
        started=time.monotonic();last_progress=started;last_size=0
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
                            if event.get('type')=='turn.completed' or (event.get('type') in ['item.started','item.completed'] and event.get('item',{}).get('type')!='error'):
                                last_progress=time.monotonic()
                        except json.JSONDecodeError: pass
                    last_size=size
                elapsed=time.monotonic()-started
                if elapsed>6000 or time.monotonic()-last_progress>3000:
                    reason='timeout' if elapsed>6000 else 'stalled'
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
                assert set(result)=={'status','final_answer','evidence','limitations'}
                assert result['status'] in ['complete','partial','abstain'] and isinstance(result['final_answer'],str)
                assert isinstance(result['evidence'],list) and all(isinstance(e,dict) and set(e)=={'url','locator'} and all(isinstance(x,str) for x in e.values()) for e in result['evidence'])
                assert isinstance(result['limitations'],list) and all(isinstance(x,str) for x in result['limitations'])
                (run/'answer.txt').write_text(result['final_answer'])
                dump(run/'extraction.json',{'status':'valid','source':'solver_output/result.json','field':'final_answer','transformations':[],'characters':len(result['final_answer'])})
                scored=cmd([sys.executable,str(BASE/'score.py'),'--answer',str(run/'answer.txt'),'--out',str(run/'scoring')]);(run/'scoring_stdout.txt').write_text(scored.stdout)
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
    print(json.dumps({'directory':str(run),**metadata},ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()
