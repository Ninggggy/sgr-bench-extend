#!/usr/bin/env python3
"""Scan delivered files for current known auth values; never print/store those values."""
import json,pathlib
T=pathlib.Path(__file__).resolve().parent
obj=json.loads((pathlib.Path.home()/'.codex/auth.json').read_text());values=[]
def collect(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if isinstance(v,str) and len(v)>20 and (k.endswith('_token') or k.upper()=='OPENAI_API_KEY'):values.append(v.encode())
   elif isinstance(v,(dict,list)):collect(v)
 elif isinstance(x,list):
  for v in x:collect(v)
collect(obj);matches=[];scanned=0
for p in T.rglob('*'):
 if not p.is_file() or '__pycache__' in p.parts:continue
 b=p.read_bytes();scanned+=1
 if any(v in b for v in values):matches.append(str(p.relative_to(T)))
result={'status':'passed' if not matches else 'failed','files_scanned':scanned,'known_secret_value_count':len(values),'matching_files':matches,'scope':'Exact current known authentication values only; no secret values retained in this report. Not proof against unknown credentials or future auth rotation.'}
(T/'privacy_check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));assert not matches
