"""Ordinary ledger allocation and status-based recovery for this campaign."""
import datetime as dt
import fcntl
import json
import os
from pathlib import Path

ACTIVE = {'preparing', 'running'}
CURRENT_PROTOCOLS = {'five-repairs-public-web-20260919', 'six-repairs-public-web-20260919'}
PAIR_ASSETS = ('reference', 'recompute', 'rules', 'CG', 'GO')


def read_json(path):
    return json.loads(Path(path).read_text())


def read_ledger(text):
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def check_campaign(campaign_path, ledger):
    campaign_path, ledger = Path(campaign_path).resolve(), Path(ledger).resolve()
    campaign = read_json(campaign_path)
    authorized_root = Path(__file__).resolve().parent.parent
    if not campaign_path.is_relative_to(authorized_root):
        raise ValueError('This runner requires the authorized ten_task_phase campaign')
    if ledger.parent != campaign_path.parent:
        raise ValueError('Ledger must belong to this campaign directory')
    configured = campaign.get('session_ledger')
    if configured and (campaign_path.parent / configured).resolve() != ledger:
        raise ValueError('Ledger contradicts campaign.session_ledger')
    if campaign.get('ended_at'):
        raise RuntimeError('Campaign already ended')
    if campaign.get('protocol_version') in CURRENT_PROTOCOLS and campaign.get('deadline') is None:
        # This authorized continuation has session limits, not a project deadline.
        # Historical campaigns retain their original wall-clock checks.
        pass
    else:
        start, deadline = (dt.datetime.fromisoformat(campaign[k]) for k in ['started_at','deadline'])
        if start.tzinfo is None or deadline.tzinfo is None or deadline-start > dt.timedelta(hours=48):
            raise ValueError('Campaign must retain an explicit maximum 48-hour window')
        if dt.datetime.now(dt.timezone.utc) >= deadline:
            raise RuntimeError('Campaign wall-clock budget exhausted')
    limit = campaign['max_sessions']
    if limit is not None and (type(limit) is not int or not 1 <= limit <= 300):
        raise ValueError('Invalid session limit')
    dt.date.fromisoformat(campaign['current_date'])
    return campaign


def row_active(row, campaign_dir):
    if row.get('run_dir'):
        path = Path(campaign_dir) / row['run_dir'] / 'run.json'
        return not path.exists() or read_json(path).get('status') in ACTIVE
    return row.get('status') in ACTIVE


def allocate(campaign_path, ledger, run, metadata):
    """Serialize concurrent budget checks and append exactly one charged attempt."""
    ledger = Path(ledger)
    with ledger.open('a+') as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        campaign = check_campaign(campaign_path, ledger)
        stream.seek(0)
        rows = read_ledger(stream.read())
        previous_run=metadata.get('previous_run')
        if previous_run and any(r.get('previous_run') == previous_run for r in rows):
            raise RuntimeError('This failed attempt already has a replacement; further sampling is forbidden')
        inherited = campaign.get('inherited_blind_sessions', 0) + campaign.get('inherited_review_sessions', 0)
        role = metadata['role']
        for budget_role, key, inherited_key in [('blind', 'max_blind_sessions', 'inherited_blind_sessions'), ('audit', 'max_review_sessions', 'inherited_review_sessions')]:
            used = campaign.get(inherited_key, 0) + sum(r.get('role') == budget_role for r in rows)
            if role == budget_role and key in campaign and used >= campaign[key]:
                raise RuntimeError(f'{budget_role} session budget exhausted')
        if campaign.get('protocol_version') in CURRENT_PROTOCOLS:
            if role not in ('blind', 'audit'):
                raise ValueError('This continuation allocates only blind and review sessions')
            if role == 'audit' and (metadata['model'], metadata['effort']) != ('gpt-6-astra', 'medium'):
                raise ValueError('Current reviews require gpt-6-astra/medium')
            if campaign.get('reserve_first_review_and_pair'):
                if metadata.get('candidate_id') not in campaign['candidate_ids']:
                    raise ValueError('Candidate is outside the authorized task scope')
                if not metadata.get('revision'):
                    raise ValueError('A substantive revision is required')
            if role == 'blind':
                identity = tuple(metadata.get(k) for k in ('candidate_id','revision','variant','trial'))
                if any(v is None for v in identity) or identity[2] not in ('CG','GO') or identity[3] != 1:
                    raise ValueError('Current blind runs require candidate/revision and one CG or GO trial')
                if identity[0] not in campaign['candidate_ids']:
                    raise ValueError('Candidate is outside the authorized task scope')
                prior = rows + campaign.get('inherited_blind_trials', [])
                if any(tuple(r.get(k) for k in ('candidate_id','revision','variant','trial')) == identity for r in prior):
                    raise RuntimeError('Same-version resampling is forbidden')
                revisions = {r.get('revision') for r in prior if r.get('candidate_id') == identity[0]}
                if identity[1] not in revisions and len(revisions) >= campaign['max_versions_per_task']:
                    raise RuntimeError('Task version budget exhausted')
            if campaign.get('reserve_first_review_and_pair'):
                # Reviews consume a substantive version too, before blind allocation.
                cid, rev = metadata['candidate_id'], metadata['revision']
                revisions = set(campaign.get('inherited_versions', {}).get(cid, []))
                revisions.update(r['revision'] for r in rows if r.get('candidate_id') == cid and r.get('revision'))
                if rev not in revisions and len(revisions) >= campaign['max_versions_per_task']:
                    raise RuntimeError('Task version budget exhausted')
                after = rows + [metadata]
                pending = first_attempt_reservations(campaign, after)
                for budget_role, key, inherited_key in [('blind', 'max_blind_sessions', 'inherited_blind_sessions'), ('audit', 'max_review_sessions', 'inherited_review_sessions')]:
                    remaining = campaign[key] - campaign.get(inherited_key, 0) - sum(r.get('role') == budget_role for r in after)
                    if remaining < pending[budget_role]:
                        raise RuntimeError(f'This attempt would consume reserved first review/pair {budget_role} sessions')
        limit = campaign['max_sessions']
        if limit is not None and len(rows) + inherited >= limit:
            raise RuntimeError('Campaign session budget exhausted')
        active = sum(row_active(row, Path(campaign_path).parent) for row in rows)
        if active + campaign.get('controller_concurrency_slots', 0) >= min(4, campaign['maximum_concurrent_model_sessions']):
            raise RuntimeError('Maximum concurrent model sessions reached')
        purpose = metadata['purpose']
        if 'reserved_pending_sessions' in campaign:
            reserved = campaign['reserved_pending_sessions'] if purpose != 'admission' else 0
        else:
            configured = campaign.get('reserved_sessions', {})
            categories = [('admission','accepted_target_retests'), ('comparison','old_comparisons_max')]
            reserved = sum(max(0, configured.get(key,0)-sum(r.get('purpose') == cat for r in rows))
                           for cat,key in categories if cat != purpose)
        if limit is not None and limit - inherited - len(rows) - 1 < reserved:
            raise RuntimeError('This attempt would consume reserved testing sessions')
        row = {'session_number':len(rows)+1, 'run_id':metadata['run_id'],
               'run_dir':os.path.relpath(run,Path(campaign_path).parent),
               'label':metadata['controller_label'], 'started_at':metadata['allocated_at'],
               'model':metadata['model'], 'effort':metadata['effort'], 'purpose':purpose,
               'role':metadata['role'], 'attempt':metadata['attempt'], 'controller_pid':os.getpid(),
               'previous_run':previous_run}
        for key in ('candidate_id', 'revision', 'variant', 'trial', 'protocol_version'):
            if key in metadata:
                row[key] = metadata[key]
        stream.write(json.dumps(row)+'\n')
        stream.flush()
        os.fsync(stream.fileno())
        return row


def first_attempt_reservations(campaign, rows):
    """Reserve untouched tasks and the missing face of every started pair."""
    pending = {'audit': 0, 'blind': 0}
    stopped = set(campaign.get('stopped_candidate_ids', []))
    for cid in campaign['candidate_ids']:
        task_rows = [r for r in rows if r.get('candidate_id') == cid]
        blinds = [r for r in task_rows if r.get('role') == 'blind']
        if cid not in stopped:
            pending['audit'] += not any(r.get('role') == 'audit' for r in task_rows)
            if not blinds:
                pending['blind'] += 2
        for rev in {r.get('revision') for r in blinds}:
            faces = {r.get('variant') for r in blinds if r.get('revision') == rev}
            pending['blind'] += len({'CG', 'GO'} - faces)
    return pending


def development_contents(plan_dir, pair):
    """Read the ordinary text copies to include when recording a development pair."""
    return {key: (Path(plan_dir) / pair[key]).read_text(encoding='utf-8')
            for key in PAIR_ASSETS}


def check_development_pair(campaign, job, public, gold, rules, out):
    """Match an invocation to its previously recorded paired development plan."""
    plan_path = Path(job['plan_path']).resolve()
    plan = read_json(plan_path)
    rounds = [r for r in plan['development_rounds'] if all(r.get(k) == job.get(k)
              for k in ('candidate_id', 'revision', 'protocol_version'))]
    if len(rounds) != 1:
        raise ValueError('Development job requires exactly one registered pair')
    pair = rounds[0]
    stamp = dt.datetime.fromisoformat(pair['registered_at'])
    if stamp.tzinfo is None or stamp >= dt.datetime.now(dt.timezone.utc):
        raise ValueError('Pair must be registered before invocation')
    slots = pair['slots']
    if len(slots) != 2 or {(s['variant'], s['trial']) for s in slots} != {('CG', 1), ('GO', 1)}:
        raise ValueError('Development pair must register CG and GO exactly once')
    if len({s['run_id'] for s in slots}) != 2 or len({s['run_dir'] for s in slots}) != 2:
        raise ValueError('Paired runs must be distinct')
    for slot in slots:
        prior = plan_path.parent / slot['run_dir'] / 'development_registration.json'
        if prior.exists() and read_json(prior) != pair:
            raise ValueError('Pair registration differs from an already prepared face')
    for key in ('model', 'effort', 'tool_profile'):
        if pair[key] != campaign['blind_' + key]:
            raise ValueError('Registered pair execution configuration differs')
    for key in PAIR_ASSETS:
        if not (plan_path.parent / pair[key]).is_file():
            raise ValueError(f'Missing registered asset: {key}')
    recorded = pair.get('registered_contents')
    if not isinstance(recorded, dict) or set(recorded) != set(PAIR_ASSETS):
        raise ValueError('Pair must retain registered contents for all five assets')
    for key, content in development_contents(plan_path.parent, pair).items():
        if recorded[key] != content:
            raise ValueError(f'Content differs from registered {key}')
    selected = [s for s in slots if all(s.get(k) == job.get(k) for k in ('run_id', 'variant', 'trial'))]
    if len(selected) != 1 or (plan_path.parent / selected[0]['run_dir']).resolve() != Path(out).resolve():
        raise ValueError('Invocation differs from registered slot')
    for supplied, key in ((public, job['variant']), (gold, 'reference'), (rules, 'rules')):
        if supplied is None or Path(supplied).resolve() != (plan_path.parent / pair[key]).resolve():
            raise ValueError(f'Invocation differs from registered {key}')
    return pair


def existing_state(out):
    out = Path(out)
    if not out.exists():
        return 'not_started'
    if not (out/'run.json').exists():
        return 'incomplete_preparation'
    metadata = read_json(out/'run.json')
    if metadata.get('status') in ACTIVE:
        pid = metadata.get('controller_pid')
        try:
            if not pid:
                return 'recovery_required'
            os.kill(pid,0)
            return 'active'
        except ProcessLookupError:
            return 'recovery_required'
    if metadata.get('status') == 'completed' and metadata.get('verification_status') == 'passed':
        required = ['solver_output/result.json','verification.json','isolation.json','invocation.json']
        if metadata.get('role','blind') == 'blind':
            required += ['answer.txt']
            if (out/'controller_scoring').exists():
                required += ['scoring/scores.json']
        return 'completed' if all((out/p).exists() for p in required) else 'missing_assets'
    return 'failed'


def validate_retry(out, approval_path, campaign):
    """A replacement is an explicit infrastructure repair, never score-based sampling."""
    approval = read_json(approval_path)
    previous = Path(approval['previous_run']).resolve()
    previous_meta = read_json(previous/'run.json')
    if previous == Path(out).resolve() or previous_meta.get('status') in ACTIVE | {'completed','invalid_output'}:
        raise ValueError('Cannot replace active/completed/model-parse-failure runs')
    if approval.get('classification') != 'infrastructure_failure' or not approval.get('evidence'):
        raise ValueError('Retry requires explicit infrastructure evidence')
    attempt = previous_meta.get('attempt',1)+1
    if attempt > 1 + min(1,campaign['repair_retries_allowed']):
        raise ValueError('Finite infrastructure repair allowance exhausted')
    return attempt, str(previous)
