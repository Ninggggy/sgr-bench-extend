"""Recompute complete catalogue cohort and oracle from preserved official JSON."""
import collections
import json
import pathlib
import re
from decimal import Decimal as D, ROUND_CEILING

HERE = pathlib.Path(__file__).resolve().parent
PREFIX = 'cpe:2.3:a:apache:http_server:'
BASE = ('AV', 'AC', 'PR', 'UI', 'S', 'C', 'I', 'A')

def vector(raw):
    value = raw.replace('NIST ', '').replace('CVSS:3.1/', '').strip()
    fields = dict(x.split(':', 1) for x in value.split('/'))
    assert set(fields) == set(BASE), raw
    return fields

def score(v):
    weights = {k: {a: D(b) for a, b in pairs.items()} for k, pairs in {
        'AV': {'N': '.85', 'A': '.62', 'L': '.55', 'P': '.2'},
        'AC': {'L': '.77', 'H': '.44'}, 'UI': {'N': '.85', 'R': '.62'},
        'impact': {'N': '0', 'L': '.22', 'H': '.56'}}.items()}
    pr = {'N': D('.85'), 'L': D('.62') if v['S'] == 'U' else D('.68'),
          'H': D('.27') if v['S'] == 'U' else D('.5')}[v['PR']]
    iss = 1 - (1 - weights['impact'][v['C']]) * (1 - weights['impact'][v['I']]) * (1 - weights['impact'][v['A']])
    impact = D('6.42') * iss if v['S'] == 'U' else D('7.52') * (iss - D('.029')) - D('3.25') * (iss - D('.02')) ** 15
    exploit = D('8.22') * weights['AV'][v['AV']] * weights['AC'][v['AC']] * pr * weights['UI'][v['UI']]
    if impact <= 0:
        return D('0')
    value = min(D('10'), (impact + exploit) * (D('1') if v['S'] == 'U' else D('1.08')))
    return (value * 10).to_integral_value(rounding=ROUND_CEILING) / 10

def matches(obj):
    if isinstance(obj, dict):
        if str(obj.get('criteria', '')).startswith(PREFIX):
            yield obj
        for value in obj.values():
            yield from matches(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from matches(value)

def derive():
    current = json.loads((HERE / 'sources/apache_current.response').read_text())
    history = json.loads((HERE / 'sources/apache_2020_2023_history.response').read_text())
    assert current['startIndex'] == history['startIndex'] == 0
    assert len(current['vulnerabilities']) == current['totalResults']
    assert len(history['cveChanges']) == history['totalResults']
    assert len({x['cve']['id'] for x in current['vulnerabilities']}) == current['totalResults']
    changes = collections.defaultdict(list)
    for item in history['cveChanges']:
        event = item['change']
        changes[event['cveId']].append(event)
    pool, excluded, answers, evidence = [], [], [], []
    for entry in current['vulnerabilities']:
        cve = entry['cve']
        if not ('2020-01-01' <= cve['published'] < '2024-01-01'):
            continue
        products = list(matches(cve.get('configurations', [])))
        if not any(x.get('vulnerable') is True for x in products):
            excluded.append({'cve_id': cve['id'], 'reason': 'environment_only', 'matches': products})
            continue
        pool.append(cve['id'])
        events = sorted(changes[cve['id']], key=lambda e: (e['created'], e['cveChangeId']))
        nist = [e for e in events if e['sourceIdentifier'] == 'nvd@nist.gov']
        initials = [e for e in nist if e['eventName'] == 'Initial Analysis']
        assert initials, cve['id']
        initial = initials[0]
        old = [d for d in initial['details'] if d['type'] == 'CVSS V3.1' and d['action'] == 'Added']
        latest = [m for m in cve.get('metrics', {}).get('cvssMetricV31', []) if m['source'] == 'nvd@nist.gov']
        if not old or not latest:
            excluded.append({'cve_id': cve['id'], 'reason': 'missing_required_v31_assessment'})
            continue
        assert len(old) == len(latest) == 1
        old_v, current_v = vector(old[0]['newValue']), vector(latest[0]['cvssData']['vectorString'])
        assert score(current_v) == D(str(latest[0]['cvssData']['baseScore']))
        if old_v == current_v:
            excluded.append({'cve_id': cve['id'], 'reason': 'same_initial_and_current_base_vector'})
            continue
        state = old_v
        first_revision = None
        for e in nist:
            if e['created'] <= initial['created']:
                continue
            additions = [d for d in e['details'] if d['type'] == 'CVSS V3.1' and d['action'] == 'Added']
            for addition in additions:
                next_v = vector(addition['newValue'])
                if next_v != state and first_revision is None:
                    first_revision = e
                state = next_v
        assert first_revision is not None and state == current_v, cve['id']
        row = [cve['id'], str(score(old_v)), str(score(current_v)), first_revision['created'][:10]]
        answers.append(row)
        evidence.append({'row': row, 'published': cve['published'], 'current_matches': products,
            'initial_event': initial, 'first_revision_event': first_revision, 'current_metric': latest[0]})
    assert set(pool) == set(changes), 'History request must cover exactly the source-derived cohort'
    answers.sort(key=lambda row: row[0])
    return {'complete_product_response': current['totalResults'], 'complete_pool': sorted(pool),
        'history_events': history['totalResults'], 'excluded': excluded, 'answers': answers, 'field_evidence': evidence}

if __name__ == '__main__':
    result = derive()
    (HERE / 'reference_result.json').write_text(json.dumps(result, indent=2))
    table = 'cve_id|initial_base_score|current_base_score|first_revision_date\n' + ''.join('|'.join(row) + '\n' for row in result['answers'])
    (HERE / 'oracle.psv').write_text(table)
    print(table, end='')
