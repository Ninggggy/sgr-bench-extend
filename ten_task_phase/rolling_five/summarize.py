"""Summarize this round's existing ledger and run metadata; no model calls."""
import datetime as dt
import json
import fcntl
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(BASE / 'runtime'))
from account import usage_from_trace

def reconcile_controller_turns(campaign):
    """Reconcile actual host turns, including aborted/user-clarification work."""
    ledger = BASE / campaign['session_ledger']
    with ledger.open('r+') as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        rows = [json.loads(line) for line in stream if line.strip()]
        origins = {r['trace_path']: r for r in rows if r.get('trace_path')}
        cutoff = dt.datetime.fromisoformat(campaign['started_at'])
        for trace_path, origin in origins.items():
            turns = {}
            with Path(trace_path).open() as trace:
                for line in trace:
                    try:
                        event = json.loads(line)
                    except ValueError:
                        continue
                    payload = event.get('payload', {})
                    turn_id = payload.get('turn_id')
                    if event.get('type') == 'event_msg' and payload.get('type') == 'task_started':
                        if dt.datetime.fromisoformat(event['timestamp']) >= cutoff:
                            turns.setdefault(turn_id, dict(started_at=event['timestamp'], status='running'))
                    elif event.get('type') == 'turn_context' and turn_id in turns:
                        turns[turn_id].update(model=payload.get('model'), effort=payload.get('effort'))
                    elif (event.get('type') == 'event_msg' and turn_id in turns
                          and payload.get('type') in ('task_complete', 'turn_aborted')):
                        turns[turn_id].update(ended_at=event['timestamp'], status='completed' if payload['type'] == 'task_complete' else 'aborted')
            existing = {r.get('turn_id'): r for r in rows if r.get('trace_path') == trace_path}
            for turn_id, state in turns.items():
                if turn_id not in existing:
                    row = dict(session_number=len(rows)+1, run_id='controller-turn-'+turn_id,
                               run_dir=None, label='actual controller continuation or clarification',
                               purpose='coordination', role='controller', thread_id=origin.get('thread_id'),
                               turn_id=turn_id, trace_path=trace_path, usage_incomplete=True, **state)
                    rows.append(row)
                    existing[turn_id] = row
                else:
                    existing[turn_id].update(state)
                if state.get('ended_at'):
                    existing[turn_id]['elapsed_seconds'] = (dt.datetime.fromisoformat(state['ended_at'])-dt.datetime.fromisoformat(state['started_at'])).total_seconds()
        stream.seek(0)
        stream.write(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows))
        stream.truncate()

def summarize():
    campaign = json.loads((BASE / 'rolling_five_campaign.json').read_text())
    reconcile_controller_turns(campaign)
    rows = [json.loads(x) for x in (BASE / campaign['session_ledger']).read_text().splitlines() if x.strip()]
    totals = dict(input_tokens=0, cached_input_tokens=0, output_tokens=0)
    for row in rows:
        if row.get('run_dir'):
            run = BASE / row['run_dir']
            meta = json.loads((run / 'run.json').read_text())
            row.update({k: meta.get(k) for k in ('status', 'elapsed_seconds', 'usage', 'actual_model', 'actual_effort', 'verification_status', 'error')})
            if row.get('usage') is None:
                traces = list((run / 'sessions').glob('*.jsonl'))
                if len(traces) == 1:
                    row['usage'] = usage_from_trace(traces[0])
                    row['usage_incomplete'] = True
        elif row.get('trace_path'):
            row['usage'] = usage_from_trace(Path(row['trace_path']), row.get('turn_id'))
            row['usage_incomplete'] = True
        for key in totals:
            totals[key] += (row.get('usage') or {}).get(key, 0)
    now = dt.datetime.now(dt.timezone.utc)
    result = dict(at=now.isoformat(), model_work_sessions=len(rows),
                  inherited_ceiling=campaign['max_sessions'], remaining_sessions=None if campaign['max_sessions'] is None else campaign['max_sessions']-len(rows),
                  reserved_pending_sessions=campaign['reserved_pending_sessions'],
                  wall_clock_seconds=(now-dt.datetime.fromisoformat(campaign['started_at'])).total_seconds(),
                  model_elapsed_seconds_sum=sum(r.get('elapsed_seconds') or 0 for r in rows),
                  known_tokens=totals, currency_cost=None,
                  limitations='Active/unreported usage is partial or unknown. Cached input is part of input. Session durations are not wall time. Account quota is shared and cannot be inferred from tokens.', runs=rows)
    (HERE / 'run_accounting.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'runs'}, ensure_ascii=False))

if __name__ == '__main__':
    summarize()
