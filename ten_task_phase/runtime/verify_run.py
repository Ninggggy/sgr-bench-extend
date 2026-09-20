#!/usr/bin/env python3
"""Verify actual model/configuration, exact extraction, score recomputation and tools."""
import collections
import importlib.util
import json
import sys
import tomllib
from pathlib import Path
from stage_results import validate, materialize_files

def invocation_model(invocation):
    """Read the actual saved argv, rejecting ambiguous repeated overrides."""
    if not isinstance(invocation, list) or not all(isinstance(x, str) for x in invocation):
        raise ValueError('Invocation must be an argv list')
    models, efforts = [], []
    i = 0
    while i < len(invocation):
        arg = invocation[i]
        value = None
        if arg in ('--model', '-m', '-c', '--config'):
            i += 1
            if i >= len(invocation):
                raise ValueError('Missing invocation option value')
            value = invocation[i]
        elif arg.startswith(('--model=', '--config=')):
            arg, value = arg.split('=', 1)
        if arg in ('--model', '-m'):
            models.append(value)
        elif arg in ('-c', '--config'):
            assignment = tomllib.loads(value)
            if 'model' in assignment:
                models.append(assignment['model'])
            if 'model_reasoning_effort' in assignment:
                efforts.append(assignment['model_reasoning_effort'])
        i += 1
    if len(models) != 1 or len(efforts) != 1:
        raise ValueError('Invocation must explicitly request model and effort exactly once')
    return models[0], efforts[0]


def verify_model_evidence(metadata, invocation, config_text, turns):
    """Cross-check controller request, executed argv, copied config and CLI trace."""
    expected = metadata.get('model'), metadata.get('effort')
    if not all(isinstance(x, str) and x for x in expected):
        raise ValueError('Run metadata lacks requested model/effort')
    config = tomllib.loads(config_text)
    if metadata.get('tool_profile') in ('web_only', 'public_web'):
        if config.get('mcp_servers'):
            raise ValueError('Web-only run exposes an MCP server')
        if config.get('sandbox_mode') != 'read-only' or config.get('web_search') != 'live':
            raise ValueError('Web-only run changed sandbox or web configuration')
        if any(config.get('features', {}).get(k) is not False for k in ('shell_tool', 'unified_exec', 'apps', 'multi_agent')):
            raise ValueError('Web-only run exposes shell, apps or delegation')
    if (config.get('model'), config.get('model_reasoning_effort')) != expected:
        raise ValueError('Saved TOML does not match requested model/effort')
    if metadata.get('provider') != config.get('model_provider'):
        raise ValueError('Saved TOML provider does not match request')
    if invocation_model(invocation) != expected:
        raise ValueError('Saved invocation does not match requested model/effort')
    if not turns or any((t.get('model'), t.get('effort')) != expected for t in turns):
        raise ValueError('Actual turn_context model/effort missing or mismatched')
    # Historical high runs retain their actual evidence; new launches are
    # restricted to medium by run.py, and admission checks the policy date.
    allowed = {('gpt-5.6-sol','medium')} if metadata.get('role','blind') == 'blind' else {('gpt-6-astra','high'), ('gpt-6-astra','medium')}
    if expected not in allowed:
        raise ValueError('Model does not match authorized role')
    if metadata.get('actual_model', 'unknown') not in ('unknown', expected[0]):
        raise ValueError('Recorded actual_model contradicts turn_context')
    if metadata.get('actual_effort', 'unknown') not in ('unknown', expected[1]):
        raise ValueError('Recorded actual_effort contradicts turn_context')
    return {'model': expected[0], 'effort': expected[1],
            'model_evidence_sources': ['run.json request', 'invocation.json argv',
                                       'solver.config.toml', 'sessions turn_context'],
            'verified_turn_contexts': len(turns)}


def verify(run):
    run=Path(run)
    spec=importlib.util.spec_from_file_location('run_scorer',run/'implementation/score.py')
    scorer=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scorer)
    parse,score,write=scorer.parse,scorer.score,scorer.write
    meta=json.loads((run/'run.json').read_text())
    public=json.loads((run/'public/input.json').read_text())
    assert set(public)=={'instruction','output_format','current_date'}
    iso=json.loads((run/'isolation.json').read_text())
    assert not iso['bind_mounts'] and iso['read_only_rootfs'] and all(not x['readable'] for x in iso['probe'])
    records=[]
    for p in (run/'sessions').glob('*.jsonl'):
        for line in p.read_text().splitlines():
            try: records.append(json.loads(line))
            except json.JSONDecodeError: pass
    turns=[r['payload'] for r in records if r.get('type')=='turn_context']
    evidence=verify_model_evidence(meta,json.loads((run/'invocation.json').read_text()),(run/'solver.config.toml').read_text(),turns)
    tool_records=[r for r in records if r.get('type')=='response_item' and r.get('payload',{}).get('type') in ['custom_tool_call','custom_tool_call_output','function_call','function_call_output','web_search_call']]
    (run/'tool_events.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in tool_records))
    calls=collections.Counter(r['payload'].get('name','unknown') for r in tool_records if r['payload']['type'] in ['custom_tool_call','function_call'])
    checks={'public_keys':True,'isolation':True,**evidence,'raw_tool_records':len(tool_records),'tool_calls':dict(calls),'completion_event':meta.get('completed_event'),'model_status':meta.get('model_reported_status'),'end_status':meta['status'],'scored':False}
    if meta.get('status') == 'completed' and not (run/'solver_output/result.json').is_file():
        raise ValueError('Completed run lacks result')
    if (run/'solver_output/result.json').is_file() and meta.get('status') != 'invalid_output':
        result=json.loads((run/'solver_output/result.json').read_text())
        validate(result,json.loads((run/'public/result.schema.json').read_text()))
        checks['stage_schema']=True
        if meta.get('role','blind') != 'blind':
            checks['stage_assets']=materialize_files(result,run/'stage_assets',write=False,registered_data=run/'downloaded_data')
    if meta.get('role','blind') == 'blind' and meta.get('audit_assets'):
        raise ValueError('Blind run received private assets')
    if (run/'answer.txt').exists():
        result=json.loads((run/'solver_output/result.json').read_text())
        answer=(run/'answer.txt').read_text()
        assert answer==result['final_answer']
        checks['exact_extraction']=True
        if (run/'controller_scoring').exists():
            rules=json.loads((run/'controller_scoring/rules.json').read_text())
            g=parse((run/'controller_scoring/oracle.psv').read_text(),rules['columns'],rules.get('record_separator'))
            p=parse(answer,rules['columns'],rules.get('record_separator'))
            computed=score(g,p,rules)
            # JSON roundtrip converts tuple row keys to arrays.
            computed=json.loads(json.dumps(computed))
            assert json.loads((run/'scoring/scores.json').read_text())=={k:v for k,v in computed.items() if k!='field_differences'}
            assert json.loads((run/'scoring/field_differences.json').read_text())==computed['field_differences']
            checks['scored']=True
            checks['parse_status']=p['status']
            checks['metrics']=computed['metrics']
    checks['historical_scorer']='Recomputed with this run implementation/score.py; later global scorer edits do not replace recorded scoring semantics.'
    if meta.get('tool_profile') == 'public_web':
        # Tool availability is verifiable here; semantic bulk/API use requires trace review.
        checks['retrieval_compliance'] = {
            'status': 'pending_trace_review',
            'policy': 'public/retrieval_policy.md',
            'checks': ['ordinary_page_fetch_vs_direct_data_api', 'bulk_or_split_bulk_acquisition',
                       'pagination', 'answer_exposure', 'access_and_format_confounders'],
            'request_count_is_cap': False,
            'note': 'Configuration verification is not a retrieval-compliance pass.'}
    checks['status']='passed'
    write(run/'verification.json',checks)
    return checks


if __name__=='__main__':
    print(json.dumps(verify(Path(sys.argv[1])),indent=2))
