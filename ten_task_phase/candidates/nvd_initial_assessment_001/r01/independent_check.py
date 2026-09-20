"""Independent replay using a second JSON traversal and floating-point CVSS implementation."""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent

def parse_vector(text):
    return dict(part.split(':') for part in text.replace('NIST ', '').replace('CVSS:3.1/', '').split('/'))

def base_score(text):
    v = parse_vector(text)
    av = [0.85, 0.62, 0.55, 0.20]['NALP'.index(v['AV'])]
    ac = 0.77 if v['AC'] == 'L' else 0.44
    pr = {'U': {'N': .85, 'L': .62, 'H': .27}, 'C': {'N': .85, 'L': .68, 'H': .50}}[v['S']][v['PR']]
    ui = .85 if v['UI'] == 'N' else .62
    impact_weights = {'H': .56, 'L': .22, 'N': 0}
    unaffected = math.prod(1 - impact_weights[v[k]] for k in ['C', 'I', 'A'])
    iss = 1 - unaffected
    impact = 6.42 * iss if v['S'] == 'U' else 7.52 * (iss - .029) - 3.25 * (iss - .02) ** 15
    raw = min(10, (impact + 8.22 * av * ac * pr * ui) * (1 if v['S'] == 'U' else 1.08)) if impact > 0 else 0
    # FIRST Appendix A recommended five-decimal integer conversion, avoiding binary round-up errors.
    integer = round(raw * 100000)
    return integer / 100000 if integer % 10000 == 0 else (integer // 10000 + 1) / 10

current = json.loads((HERE / 'sources/apache_current.response').read_text())
history = json.loads((HERE / 'sources/apache_2020_2023_history.response').read_text())
eligible = {}
environment_only = []
for wrapper in current['vulnerabilities']:
    c = wrapper['cve']
    if int(c['published'][:4]) not in range(2020, 2024):
        continue
    stack = list(c.get('configurations', []))
    vulnerable = False
    while stack:
        node = stack.pop()
        stack.extend(node.get('nodes', []))
        stack.extend(node.get('children', []))
        for match in node.get('cpeMatch', []):
            if match['criteria'].split(':')[2:5] == ['a', 'apache', 'http_server'] and match['vulnerable']:
                vulnerable = True
    if vulnerable:
        eligible[c['id']] = c
    else:
        environment_only.append(c['id'])

assert len(eligible) == 44 and len(environment_only) == 4
assert len(history['cveChanges']) == history['totalResults'] == 851
assert set(x['change']['cveId'] for x in history['cveChanges']) == set(eligible)
result = {}
checked_vectors = 0
for identifier, c in eligible.items():
    events = sorted([w['change'] for w in history['cveChanges']
                     if w['change']['cveId'] == identifier and w['change']['sourceIdentifier'] == 'nvd@nist.gov'],
                    key=lambda e: e['created'])
    first = next(e for e in events if e['eventName'] == 'Initial Analysis')
    initial = next(d['newValue'] for d in first['details'] if d['action'] == 'Added' and d['type'] == 'CVSS V3.1')
    metric = next(m['cvssData'] for m in c['metrics']['cvssMetricV31'] if m['source'] == 'nvd@nist.gov')
    assert base_score(metric['vectorString']) == metric['baseScore']
    first_changed_date = None
    present = parse_vector(initial)
    for event in events:
        if event['created'] <= first['created']:
            continue
        for detail in event['details']:
            if detail['type'] != 'CVSS V3.1' or detail['action'] != 'Added':
                continue
            new = parse_vector(detail['newValue'])
            if new != present and first_changed_date is None:
                first_changed_date = event['created'].split('T')[0]
            present = new
    assert present == parse_vector(metric['vectorString'])
    checked_vectors += 2
    if parse_vector(initial) != present:
        result[identifier] = [base_score(initial), metric['baseScore'], first_changed_date]

oracle = {}
for line in (HERE / 'oracle.psv').read_text().splitlines()[1:]:
    identifier, old, new, day = line.split('|')
    oracle[identifier] = [float(old), float(new), day]
assert result == oracle
print(json.dumps({'status': 'passed', 'complete_pool': len(eligible), 'environment_exclusions': environment_only,
    'independent_rows': result, 'vector_scores_checked': checked_vectors,
    'limits': 'Verifies source computation and cohort; does not independently certify SGR or difficulty.'}, indent=2))
