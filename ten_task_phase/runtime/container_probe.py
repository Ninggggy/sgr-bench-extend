#!/usr/bin/env python3
"""Probe official sources with the same image/CA/data tool, without any model call."""
import argparse,base64,json,pathlib,subprocess,datetime
B=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('url');p.add_argument('--name',required=True);a=p.parse_args()
out=B/'research'/a.name;out.mkdir(exist_ok=False)
code="""import sys,pathlib,json,base64
sys.path.insert(0,'/opt/wqp');import data_tools as d
d.DATA=pathlib.Path('/tmp/data');d.DATA.mkdir()
try:
 r=d.fetch({'url':sys.argv[1]})
except Exception as e:r={'error':str(e)}
print(json.dumps({'result':r,'files':[{'name':p.name,'base64':base64.b64encode(p.read_bytes()).decode()} for p in d.DATA.iterdir() if p.is_file()]}))
"""
r=subprocess.run(['docker','run','--rm','--read-only','--cap-drop=ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,nosuid,nodev,size=128m','--entrypoint','python3','sgr-ten-task-codex:local','-c',code,a.url],capture_output=True,text=True,timeout=180)
(out/'stderr.txt').write_text(r.stderr)
if r.returncode==0:
 x=json.loads(r.stdout)
 for f in x['files']:
  if pathlib.Path(f['name']).name!=f['name']:raise ValueError('invalid path')
  (out/f['name']).write_bytes(base64.b64decode(f['base64']))
 x['result']['probe_completed_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();(out/'result.json').write_text(json.dumps(x['result'],indent=2)+'\n')
 print(json.dumps({k:v for k,v in x['result'].items() if k not in ['preview','headers','query']},indent=2))
else:print('probe failed',r.returncode,r.stderr[:1000])
