"""Offline retrospective over saved metadata; never launches/recomputes experiments."""
import collections
import datetime as dt
import json
from pathlib import Path
import re

BASE = Path(__file__).resolve().parents[1]
PHASE = BASE / 'ten_task_phase'
OUT = Path(__file__).with_name('efficiency_review_stats_2026-09-10.json')
TRACE = Path.home() / '.codex/sessions/2026/09/10/rollout-2026-09-10T10-28-32-01a08925-3520-7553-927d-5eeacf9e18eb.jsonl'
# Main work-order purpose, not attribution of individual tokens inside mixed sessions.
REFERENCE_ORDERS = {6, 18, 27, 30, 39, 48, 56, 95, 98, 120, 126, 129, 131, 133, 146, 147, 148, 150}
KEYS = ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens')

def read(p):
    return json.loads(p.read_text())

def time(s):
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))

def sums(rows):
    return {'sessions': len(rows), 'known_session_hours_sum': sum(r.get('elapsed_seconds') or 0 for r in rows) / 3600,
            'elapsed_unknown': sum(r.get('elapsed_seconds') is None for r in rows),
            'usage_unknown': sum(r.get('usage') is None for r in rows),
            'usage_incomplete': sum(bool(r.get('usage_incomplete')) for r in rows),
            'known_token_sums': {k: sum((r.get('usage') or {}).get(k, 0) for r in rows) for k in KEYS}}

def concurrency(rows, start, end):
    changes = collections.Counter({start: 0, end: 0})
    unknown = []
    for r in rows:
        if not r.get('started_at') or not r.get('ended_at'):
            unknown.append(r['session_number'])
            continue
        a, b = max(time(r['started_at']), start), min(time(r['ended_at']), end)
        if b > a:
            changes[a] += 1
            changes[b] -= 1
    levels = collections.Counter()
    previous, active = start, 0
    for at, delta in sorted(changes.items()):
        levels[active] += (at - previous).total_seconds()
        active += delta
        previous = at
    return {'known_max': max(k for k, v in levels.items() if v > 0),
            'known_time_seconds_by_concurrency': dict(sorted(levels.items())),
            'known_average': sum(k * v for k, v in levels.items()) / (end - start).total_seconds(),
            'missing_intervals': unknown}

def category(r):
    purpose = r.get('purpose') or 'controller'
    if purpose in ('control', 'controller'):
        return 'controller'
    if purpose == 'construction':
        return 'reference_construction_revision' if r['session_number'] in REFERENCE_ORDERS else 'source_mechanism_exploration'
    return purpose

def main():
    account = read(PHASE / 'run_accounting.json')
    campaign = read(PHASE / 'campaign.json')
    ledger = [json.loads(x) for x in (PHASE / 'session_ledger.jsonl').read_text().splitlines()]
    rows = account['runs']
    assert len(rows) == len(ledger) == 167 and account['active_work_sessions'] == 0
    for r, l in zip(rows, ledger):
        assert r['session_number'] == l['session_number'] and r.get('run_dir') == l.get('run_dir')
    start, end = time(campaign['started_at']), time(campaign['ended_at'])
    resume_start = time(next(r for r in rows if r['session_number'] == 81)['started_at'])
    result = {'sources': ['ten_task_phase/run_accounting.json', 'ten_task_phase/session_ledger.jsonl',
                          'ten_task_phase/campaign.json', 'ten_task_phase/exports/admission_report.json'],
              'read_policy': 'Saved summaries and small run metadata; only targeted root trace metadata/usage snapshots and audit event types. No source bodies emitted, no experiment reruns.',
              'classification': {'unit': 'one real model/controller work session, not one API request or one idea',
                                 'reference_order_numbers': sorted(REFERENCE_ORDERS),
                                 'note': 'Mixed sessions classified by primary declared purpose/output. Audit107 also finalized a candidate; audit132 also revised scoring. Root performs substantive source work as well as coordination; its cost cannot be split reliably.'}}
    for name, subset, beginning in [('whole_phase', rows, start), ('resume_81_to_167', [r for r in rows if r['session_number'] >= 81], resume_start)]:
        result[name] = {'started_at': beginning.isoformat(), 'ended_at': end.isoformat(),
                        'wall_hours': (end - beginning).total_seconds() / 3600, **sums(subset),
                        'raw_purpose_counts': dict(collections.Counter(r.get('purpose') or 'controller' for r in subset)),
                        'functional_categories': {k: sums([r for r in subset if category(r) == k]) for k in sorted(set(map(category, subset)))},
                        'model_effort_counts': dict(collections.Counter(str((r.get('actual_model') or r.get('model'), r.get('actual_effort') or r.get('effort'))) for r in subset)),
                        'concurrency': concurrency(subset, beginning, end)}
    candidates = []
    for d in sorted((PHASE / 'candidates').glob('*/*')):
        if not d.is_dir():
            continue
        candidates.append({'candidate_id': d.parent.name, 'revision': d.name,
                           'path': str(d.relative_to(BASE)),
                           'paired_package': all((d / x).is_file() for x in ('CG.json', 'GO.json', 'oracle.psv', 'rules.json'))})
    trials = []
    for r in rows:
        if r.get('purpose') not in ('development', 'attack', 'admission'):
            continue
        d = PHASE / r['run_dir']
        m = read(d / 'run.json')
        score = read(d / 'scoring/scores.json') if (d / 'scoring/scores.json').exists() else {}
        trials.append({'session_number': r['session_number'], 'candidate_id': m.get('candidate_id'), 'revision': m.get('revision'),
                       'variant': m.get('variant'), 'stage': m.get('stage'), 'purpose': r['purpose'],
                       'run_dir': r['run_dir'], 'status': m['status'], 'Item-F1': score.get('metrics', {}).get('Item-F1'),
                       'counts': score.get('counts'), 'verification_status': m.get('verification_status')})
    result['candidates'] = candidates
    result['trials'] = trials
    result['funnel'] = {'candidate_base_directories': len({r['candidate_id'] for r in candidates}),
                        'candidate_revision_directories': len(candidates), 'paired_revision_packages': sum(r['paired_package'] for r in candidates),
                        'paired_base_packages': len({r['candidate_id'] for r in candidates if r['paired_package']}),
                        'blind_base_tasks': len({r['candidate_id'] for r in trials}),
                        'blind_versions': len({(r['candidate_id'], r['revision']) for r in trials}),
                        'resume_new_blind_base_tasks': len({r['candidate_id'] for r in trials if r['session_number'] >= 81}),
                        'untested_ideas': None, 'untested_ideas_note': 'No uniform idea identifier; source-work-session counts are not unique candidate counts.'}
    result['case_session_costs'] = {}
    cases = {'arxiv001_direct': [20,27,39,42,44,47,51,53,55,58,60,67,69,70,72,74,76],
             'arxiv002_direct': [83,129,131,133,135,136,137,138,141,143,144,146,147,148,150,154,155,156,157,158,160,161,162,163,164,165,166,167],
             'kegg_cdx_direct': [126,132,139,140], 'patent_direct': [92,95,99,103],
             'cfpb_direct': [96,98,101,102], 'nvd_dates_direct': [104,107,110,113],
             'natcomms_repository': [124], 'anolis_identity_and_followup': [142,153], 'pancreas': [152]}
    for name, numbers in cases.items():
        selected = [r for r in rows if r['session_number'] in numbers]
        result['case_session_costs'][name] = {'session_numbers': numbers, **sums(selected),
                                            'note': 'Direct named sessions only; excludes unallocatable root/shared work and is not full marginal task cost.'}
    result['top_input_sessions'] = [{k: r.get(k) for k in ('session_number','label','purpose','elapsed_seconds','usage','usage_source')}
                                    for r in sorted(rows, key=lambda r: (r.get('usage') or {}).get('input_tokens', 0), reverse=True)[:10]]
    trace_counts = collections.Counter()
    snapshots = []
    if TRACE.exists():
        for line in TRACE.open():
            try:
                j = json.loads(line)
            except ValueError:
                continue
            if not j.get('timestamp') or not resume_start <= time(j['timestamp']) <= end:
                continue
            payload = j.get('payload', {})
            if j.get('type') == 'compacted':
                trace_counts['compactions'] += 1
            if j.get('type') == 'response_item':
                typ = payload.get('type')
                if typ in ('custom_tool_call', 'function_call'):
                    trace_counts[typ] += 1
                if typ == 'custom_tool_call_output':
                    # Nested tool text is JSON-escaped multiple times; inspect numeric
                    # metadata only, leaving the original transcript entirely unchanged.
                    s = json.dumps(payload, ensure_ascii=False).replace('\\', '')
                    match = re.search(r'"rateLimits".*?"usedPercent"\s*:\s*(\d+).*?"windowDurationMins"\s*:\s*(\d+).*?"resetsAt"\s*:\s*(\d+)', s)
                    if match:
                        snapshots.append({'at': j['timestamp'], 'bucket': 'codex', 'used_percent': int(match[1]),
                                          'window_minutes': int(match[2]), 'resets_at': int(match[3])})
    result['root_trace_metadata'] = {'source': str(TRACE), 'interval': [resume_start.isoformat(), end.isoformat()],
                                     'counts': dict(trace_counts), 'quota_snapshots': snapshots,
                                     'quota_attribution': 'Account-wide, sparse snapshots; exact task delta and credit conversion unknown.'}
    audit = PHASE / 'runs/r-resume-arxiv002-r03-audit'
    event_counts = collections.Counter()
    for line in (audit / 'events.jsonl').open():
        j = json.loads(line)
        if j.get('type') == 'item.completed':
            item = j.get('item', {})
            event_counts[item.get('type')] += 1
            if item.get('type') == 'mcp_tool_call':
                event_counts['mcp:' + str(item.get('tool'))] += 1
    result['audit161_event_metadata'] = {'counts': dict(event_counts), 'events_bytes': (audit / 'events.jsonl').stat().st_size,
                                         'recovery': read(audit / 'transcript_recovery/recovery.json')}
    wqp = read(BASE / 'wqp_single/run_accounting.json')
    sol = read(BASE / 'wqp_single/sol_medium_retest/run_accounting.json')
    result['historical_wqp_separate_ledgers'] = {
        'original': {k: v for k, v in wqp.items() if k not in ('runs', 'sessions')},
        'original_known_usage_and_elapsed': sums(wqp['runs']),
        'sol_retest': {k: v for k, v in sol.items() if k not in ('runs', 'sessions')},
        'note': 'Separate historical work, not new construction during resume81. This inventory does not purport to cover every earlier project experiment.'}
    result['limits'] = ['Missing elapsed and usage values remain unknown; known sums do not impute them as zero.',
                        'Cached input is a subset of input; reasoning output is a subset of output, never add twice.',
                        'Input minus cached input describes reported uncached input, not billed credits or weekly allowance.',
                        'Parallel session-hours sum is not wall-clock elapsed time.',
                        'Historical WQP campaigns are separate; only its user-designation control session159 is in this ledger.',
                        'This retrospective does not modify the stopped ledger, accounting snapshot, candidate states or evaluation protocol.']
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'output': str(OUT), 'funnel': result['funnel'],
                      'whole': sums(rows), 'resume': sums([r for r in rows if r['session_number'] >= 81]),
                      'concurrency_resume': result['resume_81_to_167']['concurrency'],
                      'audit_events': dict(event_counts), 'root_counts': dict(trace_counts)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
