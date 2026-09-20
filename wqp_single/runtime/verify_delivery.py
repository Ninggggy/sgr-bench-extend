#!/usr/bin/env python3
"""Summarize delivered evidence and run existing candidate checks; no model invocation."""
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys

B = Path(__file__).resolve().parent.parent
ROOT = B.parents[1]
REV = B / 'candidates/wqp_activity_panel_001/r03'
ledger = [json.loads(line) for line in (B / 'session_ledger.jsonl').read_text().splitlines()]
issues = []
if len(ledger) > 60 or len({x['session_number'] for x in ledger}) != len(ledger):
    issues.append('Session accounting exceeds budget or contains duplicate numbers.')
run_checks = []
for row in ledger:
    run = B / row['run_dir']
    meta = json.loads((run / 'run.json').read_text())
    checks = json.loads((run / 'verification.json').read_text()) if (run / 'verification.json').exists() else {}
    recovery = json.loads((run / 'data_recovery.json').read_text()) if (run / 'data_recovery.json').exists() else {}
    item = dict(label=row['label'], run=row['run_dir'], status=meta['status'], verification=checks.get('status'),
                recovery_successful=recovery.get('successful'), recovered_files=(len(recovery.get('files', [])) if isinstance(recovery.get('files', []), list) else recovery.get('files', 0)))
    if meta['status'] in ('running', 'preparing'):
        issues.append(f"Unfinished run: {row['label']}")
    if meta['status'] == 'completed' and (meta.get('actual_model') != 'gpt-6-astra' or checks.get('status') != 'passed'):
        issues.append(f"Completed run lacks expected model/verification: {row['label']}")
    if row['run_dir'].startswith('candidates/wqp_activity_panel_001/r03/') and meta['status'] == 'completed' and not recovery.get('successful'):
        issues.append(f"Final revision download recovery not confirmed: {row['label']}")
    run_checks.append(item)

comparison_checks = []
for phase in ('screening', 'confirmation'):
    plan_path = B / 'comparisons' / (phase + '_run_plan.json')
    if not plan_path.exists():
        issues.append(f'Missing prescribed {phase} plan.')
        continue
    plan = json.loads(plan_path.read_text())
    for job in plan['jobs']:
        run = Path(job['out'])
        source_public = json.loads(Path(job['public']).read_text())
        actual_public = json.loads((run / 'public/input.json').read_text())
        same_public = all(actual_public.get(k) == source_public.get(k) for k in ('instruction', 'output_format'))
        same_rules = json.loads((run / 'controller_scoring/rules.json').read_text()) == json.loads(Path(job['rules']).read_text())
        same_gold = (run / 'controller_scoring/oracle.psv').read_bytes() == Path(job['gold']).read_bytes()
        same_config = (run / 'solver.config.toml').read_bytes() == (B / 'runtime/solver.config.toml').read_bytes()
        same_data_tools = (run / 'implementation/data_tools.py').read_bytes() == (B / 'runtime/data_tools.py').read_bytes()
        record = dict(label=job['label'], public_semantics=same_public, controller_rules=same_rules,
                      controller_gold=same_gold, shared_config=same_config, shared_data_tools=same_data_tools)
        if not all((same_public, same_rules, same_gold, same_config, same_data_tools)):
            issues.append(f"Comparison input/configuration mismatch: {job['label']}")
        comparison_checks.append(record)

auth = Path.home() / '.codex/auth.json'
secrets = []
def visit(value, key=''):
    if isinstance(value, dict):
        for name, child in value.items():
            visit(child, name)
    elif isinstance(value, str) and len(value) >= 24 and ('token' in key.lower() or 'api_key' in key.lower()):
        secrets.append(value.encode())
if auth.exists():
    visit(json.loads(auth.read_text()))
hits = []
file_count = 0
for file in B.rglob('*'):
    if not file.is_file():
        continue
    file_count += 1
    data = file.read_bytes()
    if any(secret in data for secret in secrets):
        hits.append(str(file.relative_to(B)))
if hits:
    issues.append('Known authentication values found in delivered files; see paths only.')
validation = subprocess.run([sys.executable, str(ROOT / 'construction_pipeline/scripts/prepare.py'),
    'validate-candidate', '--candidate', str(REV / 'candidate.json'), '--check-files'], capture_output=True, text=True)
if validation.returncode:
    issues.append('Existing candidate declaration/reference check failed.')
report = {'recorded_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'status': 'passed' if not issues else 'needs_attention',
    'sessions': len(ledger), 'run_checks': run_checks, 'comparison_checks': comparison_checks, 'issues': issues,
    'known_credential_scan': {'files_scanned': file_count, 'known_values_checked': len(secrets), 'matching_paths': hits,
        'scope': 'Exact current runtime token/key values only; no credential value printed or persisted. Not a general security audit.'},
    'candidate_check': {'exit_code': validation.returncode, 'output': validation.stdout + validation.stderr},
    'limitations': 'Existing checks cover declarations, references, recorded isolation/model/extraction/scoring and retained downloads. They do not replace source interpretation or establish hardness. Historical r01 download gaps remain disclosed.'}
(B / 'delivery_verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': report['status'], 'sessions': len(ledger), 'issues': issues, 'credential_matches': len(hits)}))
