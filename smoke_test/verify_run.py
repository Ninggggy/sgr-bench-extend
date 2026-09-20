#!/usr/bin/env python3
"""Offline verification and tool-log extraction; never calls the solver."""
import argparse, collections, json, pathlib
from score import task, parse, score, write

def main():
    p=argparse.ArgumentParser();p.add_argument('run',type=pathlib.Path);a=p.parse_args();run=a.run
    t=task();public=json.loads((run/'public/input.json').read_text())
    assert set(public)=={'instruction','output_format','current_date'}
    assert all(public[k]==t[k] for k in ['instruction','output_format'])
    assert 'arxiv_001' not in (run/'public/prompt.md').read_text()
    result=json.loads((run/'solver_output/result.json').read_text());answer=(run/'answer.txt').read_text()
    assert answer==result['final_answer']
    schema=t['rubric']['normalization']['schema']
    computed=score(parse(t['oracle_answer'],schema),parse(answer,schema),schema)
    stored=json.loads((run/'scoring/scores.json').read_text())
    assert stored=={k:v for k,v in computed.items() if k!='field_differences'}
    assert json.loads((run/'scoring/field_differences.json').read_text())==computed['field_differences']
    assert (run/'implementation/score.py').read_bytes()==pathlib.Path(__file__).with_name('score.py').read_bytes()
    records=[]
    for path in (run/'sessions').glob('*.jsonl'):
        records.extend(json.loads(line) for line in path.read_text().splitlines())
    tool_records=[r for r in records if r.get('type')=='response_item' and r.get('payload',{}).get('type') in ['custom_tool_call','custom_tool_call_output','function_call','function_call_output','web_search_call']]
    (run/'tool_events.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in tool_records))
    calls=collections.Counter(r['payload'].get('name','unknown') for r in tool_records if r['payload']['type'] in ['custom_tool_call','function_call'])
    turns=[r['payload'] for r in records if r.get('type')=='turn_context']
    assert turns and all(r['model']=='gpt-6-astra' and r['effort']=='high' for r in turns)
    write(run/'verification.json',{'status':'passed','public_projection':'exact formal instruction/output_format, only three public keys','extraction':'byte-equivalent final_answer text, no additions','scoring':'same pre-solve scorer; all stored counts and differences independently recomputed','actual_model':turns[0]['model'],'effort':turns[0]['effort'],'tool_call_counts':dict(calls),'tool_records':len(tool_records),'isolated_session_files':len(list((run/'sessions').glob('*.jsonl'))),'trace_tool_payloads':'tool_events.jsonl contains raw calls and responses with timestamps'})
    print(json.dumps(json.loads((run/'verification.json').read_text()),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
