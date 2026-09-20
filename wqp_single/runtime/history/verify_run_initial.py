#!/usr/bin/env python3
"""Verify actual model/configuration, exact extraction, score recomputation and tools."""
import collections,json,sys
from pathlib import Path
from score import parse,score,write
run=Path(sys.argv[1]);meta=json.loads((run/'run.json').read_text())
public=json.loads((run/'public/input.json').read_text());assert set(public)=={'instruction','output_format','current_date'}
iso=json.loads((run/'isolation.json').read_text());assert not iso['bind_mounts'] and iso['read_only_rootfs'] and all(not x['readable'] for x in iso['probe'])
records=[]
for p in (run/'sessions').glob('*.jsonl'):
 for l in p.read_text().splitlines():
  try: records.append(json.loads(l))
  except json.JSONDecodeError: pass
turns=[r['payload'] for r in records if r.get('type')=='turn_context']
assert turns and all(t['model']=='gpt-6-astra' and t['effort']=='high' for t in turns)
tool_records=[r for r in records if r.get('type')=='response_item' and r.get('payload',{}).get('type') in ['custom_tool_call','custom_tool_call_output','function_call','function_call_output','web_search_call']]
(run/'tool_events.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in tool_records))
calls=collections.Counter(r['payload'].get('name','unknown') for r in tool_records if r['payload']['type'] in ['custom_tool_call','function_call'])
checks={'public_keys':True,'isolation':True,'model':'gpt-6-astra','effort':'high','raw_tool_records':len(tool_records),'tool_calls':dict(calls),'completion_event':meta.get('completed_event'),'model_status':meta.get('model_reported_status'),'end_status':meta['status'],'scored':False}
if (run/'answer.txt').exists():
 result=json.loads((run/'solver_output/result.json').read_text());answer=(run/'answer.txt').read_text();assert answer==result['final_answer'];checks['exact_extraction']=True
 if (run/'controller_scoring').exists():
  rules=json.loads((run/'controller_scoring/rules.json').read_text());g=parse((run/'controller_scoring/oracle.psv').read_text(),rules['columns']);p=parse(answer,rules['columns']);computed=score(g,p,rules)
  # JSON roundtrip converts tuple row keys to arrays.
  computed=json.loads(json.dumps(computed))
  assert json.loads((run/'scoring/scores.json').read_text())=={k:v for k,v in computed.items() if k!='field_differences'}
  assert json.loads((run/'scoring/field_differences.json').read_text())==computed['field_differences']
  checks['scored']=True;checks['parse_status']=p['status'];checks['metrics']=computed['metrics']
for f in ['score.py','verify_run.py']:
 if (run/'implementation'/f).exists(): assert (run/'implementation'/f).read_bytes()==Path(__file__).with_name(f).read_bytes()
checks['status']='passed';write(run/'verification.json',checks);print(json.dumps(checks,indent=2))
