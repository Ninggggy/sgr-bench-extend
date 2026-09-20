#!/usr/bin/env python3
"""Recompute admission evidence and export only paired, strictly qualifying tasks."""
import argparse
from collections import Counter
from datetime import datetime
from fractions import Fraction
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VERIFY = ROOT / 'construction_pipeline/wqp_single/runtime/verify_run.py'
ECOSYSTEMS = {'WQP', 'Water Office', 'CFPB', 'ChemExpo/CompTox', 'Census', 'NVD', 'KEGG', 'Reptile Database', 'Europe PMC', 'arXiv', 'NOAA CAG', 'CDC WONDER'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text())


def resolve(base, value):
    p = Path(value)
    return p if p.is_absolute() else (base / p).resolve()


def stamp(value):
    t = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(t.tzinfo is not None, 'timestamps must include timezone')
    return t


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def model_evidence(run, expected):
    meta = read(run / 'run.json')
    records = [json.loads(line) for path in sorted((run / 'sessions').glob('*.jsonl'))
               for line in path.read_text().splitlines() if line.strip()]
    turns = [r['payload'] for r in records if r.get('type') == 'turn_context']
    evidence = module(VERIFY, 'admission_model_verifier').verify_model_evidence(
        meta, read(run / 'invocation.json'), (run / 'solver.config.toml').read_text(), turns)
    require((evidence['model'], evidence['effort']) == expected, 'wrong model or effort')
    require(meta.get('status') == 'completed' and meta.get('exit_code') == 0
            and meta.get('completed_event') is True and not meta.get('errors'), 'incomplete or failed run')
    evidence['session_ids'] = [r['payload']['id'] for r in records if r.get('type') == 'session_meta']
    require(len(set(evidence['session_ids'])) == 1, 'missing or multiple actual sessions')
    events = [json.loads(line) for line in (run / 'events.jsonl').read_text().splitlines() if line.strip()]
    require(any(e.get('type') == 'turn.completed' for e in events), 'actual completion event missing')
    return meta, evidence


def isolated(run):
    iso = read(run / 'isolation.json')
    require(iso.get('bind_mounts') == [] and iso.get('read_only_rootfs') is True,
            'isolation filesystem evidence failed')
    probes = iso.get('probe', [])
    require(len(probes) >= 3 and all(p.get('readable') is False for p in probes), 'isolation probes missing or readable')
    require('ALL' in iso.get('cap_drop', []) and 'no-new-privileges' in iso.get('security_opt', []), 'isolation restrictions missing')
    argv = read(run / 'invocation.json')
    require('resume' not in argv and 'fork' not in argv, 'resumed or forked blind session')
    require(len(argv) > 3 and argv[:2] == ['docker', 'exec'], 'no actual isolated docker invocation')
    return argv[3] if argv[2] == '-i' else argv[2]


def verify_audits(paths, base, candidate, protocol, campaign=None):
    checks = {}
    reports = []
    for path in paths:
        run = resolve(base, path)
        requested = read(run / 'run.json')
        policy = (campaign or {}).get('nonblind_effort_change')
        effort = (campaign or {}).get('construction_effort', 'high')
        if policy:
            effort = policy['effort'] if stamp(requested['started_at']) >= stamp(policy['effective_at']) else policy['previous_effort']
        meta, evidence = model_evidence(run, ('gpt-6-astra', effort))
        result = read(run / 'solver_output/result.json')
        if 'checks' not in result:
            files = [f for f in result.get('files', []) if f.get('path') == 'audit.json']
            require(len(files) == 1, 'missing unique inline audit.json')
            require((run / 'stage_assets/audit.json').read_text() == files[0]['content'], 'audit asset differs from actual model output')
            result = json.loads(files[0]['content'])
        require(result.get('candidate_id') == candidate['candidate_id'] and result.get('revision') == candidate['revision']
                and result.get('protocol_version') == protocol, 'audit identity/version mismatch')
        for name, item in result.get('checks', {}).items():
            require(name not in checks, 'duplicate/conflicting audit check: ' + name)
            refs = item.get('evidence_paths', [])
            require(item.get('verdict') == 'pass' and refs, 'audit not passed with evidence: ' + name)
            require(all(resolve(run, p).is_file() and resolve(run, p).stat().st_size > 0 for p in refs), 'missing audit evidence: ' + name)
            checks[name] = item
        reports.append({'run_dir': str(run), 'model_evidence': evidence, 'ended_at': meta['ended_at']})
    required = {'content', 'sgr', 'semantic_alignment', 'substantive_errors_cg', 'substantive_errors_go'}
    require(required <= checks.keys(), 'required content/SGR/alignment/substantive-error audits missing')
    for variant in ('cg', 'go'):
        item = checks['substantive_errors_' + variant]
        require(item.get('error_category') in {'domain', 'identity', 'scope', 'retrieval_decision'}, 'non-substantive error category')
        require(bool(item.get('substantive_progress')) and bool(item.get('explanation')), 'substantive progress/error explanation missing')
    return {'checks': checks, 'runs': reports}


def recompute(run, candidate, candidate_dir, rules):
    saved_rules = read(run / 'controller_scoring/rules.json')
    require(saved_rules == rules, 'scoring rules mismatch')
    oracle = resolve(candidate_dir, candidate['private']['oracle_path']).read_text()
    require((run / 'controller_scoring/oracle.psv').read_text() == oracle, 'mixed oracle/version')
    answer = (run / 'answer.txt').read_text()
    require(answer == read(run / 'solver_output/result.json')['final_answer'], 'answer extraction mismatch')
    scorer = module(run / 'implementation/score.py', 'saved_admission_scorer')
    parse_args = (rules['columns'], rules['record_separator']) if rules.get('record_separator') else (rules['columns'],)
    gold, pred = scorer.parse(oracle, *parse_args), scorer.parse(answer, *parse_args)
    require(gold['status'] == 'parsed' and pred['status'] in {'parsed', 'empty'}, 'unresolved parse failure')
    computed = json.loads(json.dumps(scorer.score(gold, pred, rules)))
    saved = read(run / 'scoring/scores.json')
    require(saved == {k: v for k, v in computed.items() if k != 'field_differences'}, 'saved score differs from historical scorer recomputation')
    require(read(run / 'scoring/field_differences.json') == computed['field_differences'], 'field score evidence mismatch')
    counts = computed['counts']
    n, d = counts['correct_fields'], counts['item_denominator']
    require(type(n) is int and type(d) is int and d > 0 and 0 <= 2*n <= d, 'invalid integer scoring counts')
    value = computed.get('metrics', {}).get('Item-F1')
    require(type(value) in (float, int) and math.isfinite(value) and 0 <= value <= 1, 'missing/non-numeric Item-F1')
    exact = Fraction(2*n, d)
    require(value == float(exact), 'metric/count mismatch')
    return exact, {'counts': counts, 'metrics': computed['metrics'], 'Item-F1_exact': str(exact),
                   'complete_correct': computed['metrics']['Item-F1'] == 1 and computed['metrics']['Row-F1'] == 1}


def verify_retrieval_policy(run, campaign, campaign_dir):
    path = campaign.get('protocol_assets', {}).get('retrieval_policy_path')
    require(campaign.get('protocol_version') != 'ten-task-v2-bounded-retrieval' or bool(path),
            'bounded retrieval policy missing')
    if not path:
        return
    policy = resolve(campaign_dir, path).read_text()
    require(bool(policy.strip()) and (run/'public/retrieval_policy.md').read_text() == policy,
            'retrieval policy absent or changed')
    require((run/'public/prompt.md').read_text().startswith(policy+'\n\n'),
            'retrieval policy was not injected into blind prompt')
    review = read(run/'retrieval_review.json')
    require(review.get('run_id') == run.name and review.get('protocol_version') == campaign['protocol_version'],
            'retrieval review identity mismatch')
    require(review.get('verdict') == 'passed', 'retrieval review incomplete or noncompliant')
    checks = review.get('checks', {})
    for name in ('bulk_scope', 'query_dependencies', 'pagination', 'request_count', 'concurrency', 'safety'):
        item = checks.get(name, {})
        require(item.get('verdict') == 'passed' and bool(item.get('explanation')) and bool(item.get('evidence_paths')),
                'missing retrieval trajectory check: '+name)
        for evidence in item['evidence_paths']:
            evidence_path = resolve(run, evidence)
            require(evidence_path.is_file() and evidence_path.stat().st_size > 0, 'missing retrieval evidence')


def verify_protocol(run, campaign, campaign_dir):
    verify_retrieval_policy(run, campaign, campaign_dir)
    assets = campaign['protocol_assets']
    meta = read(run / 'run.json')
    require(stamp(assets['registered_at']) < stamp(meta['started_at']), 'tools/scorer protocol registered after blind run')
    for local, declared in [('solver.config.toml', 'solver_config_path'),
                            ('implementation/score.py', 'scorer_path'),
                            ('implementation/data_tools.py', 'data_tools_path')]:
        require((run / local).read_text() == resolve(campaign_dir, assets[declared]).read_text(),
                'run differs from campaign protocol: ' + local)
    require(read(run / 'isolation.json').get('image_id') == assets['image_id'] and bool(assets['image_id']),
            'actual tool image differs from campaign protocol')


def assess(entry, manifest_dir, plan, plan_dir, campaign, campaign_dir, ledger, ledger_dir):
    candidate_path = resolve(manifest_dir, entry['candidate_path'])
    c = read(candidate_path)
    identity = c['candidate_id'], c['revision'], plan['protocol_version']
    report = {'candidate_id': identity[0], 'revision': identity[1], 'protocol_version': identity[2],
              'family': entry['family'], 'ecosystem': c['ecosystem'], 'scores_are_selection_scores': True,
              'status': 'inconclusive', 'admitted': False, 'CG': {'trials': []}, 'GO': {'trials': []}}
    try:
        require(type(c['revision']) is int and 1 <= c['revision'] <= 3, 'more than two substantive revisions')
        old = {read_line['task_id'] for read_line in (json.loads(x) for x in (ROOT / 'runs/open-source/sgr-bench/constraint.jsonl').read_text().splitlines())}
        require(c['candidate_id'] not in old and not (c['candidate_id'] == 'wqp_activity_panel_001' and c['revision'] == 3), 'excluded old task or WQP r03 family')
        require(c['ecosystem'] in ECOSYSTEMS and entry['family'].strip(), 'unsupported ecosystem or missing family')
        require(c['status'] == 'content_validated' and c['validation']['content'] == 'passed', 'content not validated')
        require(c['validation']['human_validation'] in {'not_performed', 'partial', 'completed'}, 'unknown human review state')
        require(c['public']['cg']['output_format'] == c['public']['go']['output_format'], 'CG/GO output rules differ')
        for key in ('source_manifest_path', 'oracle_path', 'reference_script_path', 'state_graph_path'):
            p = resolve(candidate_path.parent, c['private'][key])
            require(p.is_file() and p.stat().st_size > 0, 'missing candidate asset: ' + key)
        rounds = [r for r in plan['admission_rounds'] if (r['candidate_id'], r['revision'], r['protocol_version']) == identity]
        require(len(rounds) == 1, 'missing or repeated admission round for same version/protocol')
        rnd = rounds[0]
        require(identity[2] == campaign['protocol_version'], 'campaign protocol mismatch')
        slots = rnd['slots']
        require(len(slots) == 6 and {(s['variant'], s['trial']) for s in slots} == {(v, n) for v in ('CG', 'GO') for n in (1, 2, 3)}, 'need exactly three unique preplanned trials per variant')
        require(len({s['run_id'] for s in slots}) == 6, 'duplicate run_id')
        require(all(type(s['trial']) is int for s in slots), 'invalid trial number')
        audit = verify_audits(rnd['audit_paths'], plan_dir, c, identity[2], campaign)
        report['audits'] = audit
        require(all(stamp(x['ended_at']) < stamp(rnd['registered_at']) for x in audit['runs']), 'content audits must finish before registration')
        rules = read(resolve(plan_dir, rnd['rules_path']))
        containers, runs, sessions, sums = set(), set(), set(), {'CG': Fraction(0), 'GO': Fraction(0)}
        tools_text = None
        scorer_text = None
        image_id = None
        for slot in sorted(slots, key=lambda x: (x['variant'], x['trial'])):
            run = resolve(plan_dir, slot['run_dir'])
            require(run not in runs and run.name == slot['run_id'], 'duplicate path or run_id/path mismatch')
            runs.add(run)
            meta, evidence = model_evidence(run, ('gpt-5.6-sol', 'medium'))
            verify_protocol(run, campaign, campaign_dir)
            session_id = evidence['session_ids'][0]
            require(session_id not in sessions, 'reused actual blind session')
            sessions.add(session_id)
            config_text = (run / 'solver.config.toml').read_text()
            require(tools_text is None or config_text == tools_text, 'nonuniform tool configuration')
            tools_text = config_text
            saved_scorer = (run / 'implementation/score.py').read_text()
            require(scorer_text is None or scorer_text == saved_scorer, 'nonuniform historical scoring implementation')
            scorer_text = saved_scorer
            saved_image = read(run / 'isolation.json').get('image_id')
            require(isinstance(saved_image, str) and saved_image and (image_id is None or saved_image == image_id), 'missing or nonuniform actual tool image')
            image_id = saved_image
            require(stamp(rnd['registered_at']) < stamp(meta['started_at']), 'trial was not preregistered')
            for key, value in zip(('candidate_id', 'revision', 'protocol_version'), identity):
                require(meta.get(key) == value, 'run identity mismatch: ' + key)
            require(meta.get('stage') == 'admission_retest' and meta.get('variant') == slot['variant'] and meta.get('trial') == slot['trial'], 'development/attack/wrong trial mixed into retest')
            require(meta.get('controller_label') == slot['label'], 'preplanned run label mismatch')
            registration = read(run / 'admission_registration.json')
            require(registration == rnd, 'preplanned registration changed or run substituted')
            matches = [x for x in ledger if x.get('run_dir') and resolve(ledger_dir, x['run_dir']) == run]
            require(len(matches) == 1 and matches[0].get('label') == slot['label'], 'run absent/duplicated in campaign ledger')
            require(meta['current_date'] == campaign['current_date'] and meta['maximum_seconds'] == campaign['max_seconds_per_session'] and meta['stall_seconds'] == campaign['stall_seconds'], 'nonuniform date or budget')
            public = read(run / 'public/input.json')
            require(public == {**c['public'][slot['variant'].lower()], 'current_date': campaign['current_date']}, 'blind input differs from finalized public variant')
            container = isolated(run)
            require(container not in containers, 'blind sessions reused environment')
            containers.add(container)
            exact, detail = recompute(run, c, candidate_path.parent, rules)
            sums[slot['variant']] += exact
            report[slot['variant']]['trials'].append({'trial': slot['trial'], 'run_id': slot['run_id'], 'run_dir': str(run), 'model_evidence': evidence, **detail})
        for variant in ('CG', 'GO'):
            mean = sums[variant] / 3
            report[variant].update(mean=float(mean), mean_exact=str(mean), threshold_passed=mean < Fraction(7, 10))
        report['admitted'] = all(report[v]['threshold_passed'] for v in ('CG', 'GO'))
        report['status'] = 'screened' if report['admitted'] else 'rejected_threshold'
    except (ValueError, KeyError, TypeError, OSError, AssertionError, ImportError, ZeroDivisionError) as exc:
        report['reason'] = str(exc)
    return report, c


def evaluate(manifest_path):
    manifest_path = Path(manifest_path).resolve()
    base, m = manifest_path.parent, read(manifest_path)
    plan_path, campaign_path, ledger_path = [resolve(base, m[k]) for k in ('plan_path', 'campaign_path', 'ledger_path')]
    plan, campaign = read(plan_path), read(campaign_path)
    ledger = [json.loads(x) for x in ledger_path.read_text().splitlines() if x.strip()]
    # Every actually launched blind run in this campaign uses the registered protocol,
    # including development, attacks, comparison runs and failed model attempts.
    for row in ledger:
        if not row.get('run_dir'):
            continue
        run = resolve(ledger_path.parent, row['run_dir'])
        if not (run / 'run.json').exists():
            continue
        meta = read(run / 'run.json')
        if meta.get('model') == 'gpt-5.6-sol' and meta.get('started_at') and (run / 'invocation.json').exists():
            verify_protocol(run, campaign, campaign_path.parent)
    results = [assess(e, base, plan, plan_path.parent, campaign, campaign_path.parent, ledger, ledger_path.parent) for e in m['candidates']]
    # Explicit user decision for this historical version; ordinary assessment stays intact.
    for entry, (report, candidate) in zip(m['candidates'], results):
        decision = entry.get('user_designated_exception')
        if decision is None:
            continue
        require((candidate['candidate_id'], candidate['revision']) in {
                    ('wqp_activity_panel_001', 3), ('arxiv_historical_title_002', 3)},
                'user exception only authorized for WQP r03 and arxiv_historical_title_002 r03')
        require(decision in campaign.get('admission_amendments', []) and decision.get('authorized_by') == 'user',
                'missing recorded user admission decision')
        for evidence in decision['historical_evidence_paths']:
            require(resolve(base, evidence).is_file(), 'missing historical exception evidence')
        report['standard_assessment'] = dict(report)
        report.update(admitted=True, status='user_designated_exception', admission_basis=decision,
                      protocol_version=None, standard_protocol_passed=False)
    accepted = [r for r, _ in results if r['admitted']]
    target = campaign.get('target_base_tasks', 10)
    require(type(target) is int and 1 <= target <= 10, 'invalid campaign task target')
    require(len({r['candidate_id'] for r in accepted}) == len(accepted), 'duplicate accepted base task/version')
    require(len(accepted) <= target, 'more accepted base tasks than campaign target')
    require(all(n <= 2 for n in Counter(r['family'] for r in accepted).values()), 'more than two accepted tasks in same construction family')
    return {'accepted_count': len(accepted), 'target': target, 'partial_delivery': len(accepted) != target,
            'standard_accepted_count': sum(r['status'] == 'screened' for r in accepted),
            'user_designated_count': sum(r['status'] == 'user_designated_exception' for r in accepted),
            'scores_are_selection_scores': True, 'candidates': [r for r, _ in results]}, results


def export(manifest_path, output_dir):
    summary, results = evaluate(manifest_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = {'CG': [], 'GO': []}
    manifest = read(manifest_path)
    for (r, c), entry in zip(results, manifest['candidates']):
        if not r['admitted']:
            continue
        base = resolve(Path(manifest_path).resolve().parent, entry['candidate_path']).parent
        oracle = resolve(base, c['private']['oracle_path']).read_text().strip()
        manual = r['status'] == 'user_designated_exception'
        rules = read(resolve(base, c['private'].get('scoring_rules_path', 'private/scoring_rules.json'))) if manual else read(Path(r['CG']['trials'][0]['run_dir']) / 'controller_scoring/rules.json')
        if manual:
            scorer = module(ROOT / 'construction_pipeline/wqp_single/runtime/score.py', 'manual_export_scorer')
            gold = scorer.parse(oracle, rules['columns'])
            require(gold['status'] == 'parsed', 'manual candidate oracle is not parseable')
            cardinality = scorer.score(gold, gold, rules)['counts']['gold_rows']
        for variant in rows:
            rows[variant].append({'task_id': c['candidate_id'] + ('-g' if variant == 'GO' else ''), 'domain': c['domain'], 'autonomy_type': 'ordered table',
                'oracle_output_cardinality': cardinality if manual else r[variant]['trials'][0]['counts']['gold_rows'],
                **c['public'][variant.lower()], 'start_url': c['private']['start_urls'][0], 'oracle_answer': oracle,
                'metadata': {'State-Gated Retrieval': c['private']['predicates'], 'revision': c['revision'],
                             'status': 'content_validated', 'difficulty': c['validation']['difficulty'] if manual else 'screened',
                             'admission_basis': r['status'], 'standard_protocol_passed': not manual,
                             'human_validation': c['validation']['human_validation'],
                             'protocol_version': r['protocol_version'], 'construction_family': r['family'], 'scores_are_selection_scores': True},
                'rubric': rules})
    for variant, records in rows.items():
        (out / ('constraint.jsonl' if variant == 'CG' else 'goal.jsonl')).write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in records))
    (out / 'admission_report.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['check', 'export'])
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.command == 'export':
        require(args.out is not None, '--out required for export')
        summary = export(args.manifest, args.out)
    else:
        summary = evaluate(args.manifest)[0]
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
