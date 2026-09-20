import csv
import json
import sys
from datetime import datetime
from pathlib import Path

# Independent implementation: line-based regulator extraction, explicit shared
# alias resolution, and a separate action/document selection path. Does not
# import reference.py. Supplied for controller execution, not claimed executed.
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent

def j(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))

rules = j('rules.json')
columns = rules['columns']

def canonical(field, value):
    value = str(value).strip()
    for alias, target in rules['fields'][field]['aliases'].items():
        if value.casefold() in {alias.casefold(), target.casefold()}:
            return target
    return value

def primary(stem):
    filenames = [ROOT / (stem + '.txt'), ROOT / (stem + '.response'), ROOT / stem]
    p = next((x for x in filenames if x.exists()), None)
    if p is None:
        raise FileNotFoundError(stem)
    data = p.read_text(encoding='utf-8')
    while True:
        if isinstance(data, dict):
            if 'result' in data:
                data = data['result']
            elif 'text' in data:
                data = data['text']
            elif 'content' in data:
                data = data['content'][0]['text']
            else:
                raise ValueError('Unknown source envelope')
        elif isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return data.replace('\\n', '\n').splitlines()
        else:
            raise ValueError('Invalid primary record')

certificates = {}
current_name = None
for line in primary('d0004'):
    if 'Legal Name: ' in line:
        current_name = line.split('Legal Name: ', 1)[1].strip()
    elif 'FDIC Certificate #: ' in line:
        if current_name is None:
            raise AssertionError('Certificate without legal name')
        value = line.split('FDIC Certificate #: ', 1)[1].strip()
        certificates[canonical('issuer_bank', current_name)] = value
        current_name = None

cra_lines = primary('d0005')
front_name = next(line.split('L4@P0: ', 1)[1] for line in cra_lines if line.startswith('L4@P0: '))
front_certificate = next(line.split('Certificate Number: ', 1)[1] for line in cra_lines
                         if line.startswith('L5@P0: Certificate Number: '))
certificates[canonical('issuer_bank', front_name)] = front_certificate

selected = {}
for record in j('evidence/actions.json')['records']:
    q = record['quotes']
    stamp = datetime.strptime(q['date'], '%B %d, %Y')
    words = q['description'].split()
    characterized = any(word in ('fintech', 'financial-technology') for word in words)
    if stamp.year == 2024 and stamp.month in (4, 5, 6) and characterized:
        selected[q['title'].split()[0].casefold()] = (q['title'], stamp.strftime('%Y-%m-%d'))

linked = set()
for index in j('evidence/indexes.json')['records']:
    for link in index['links']:
        if link['label'].endswith('Deposit Account Agreement'):
            linked.add(link['url'])

actual = []
for record in j('evidence/agreements.json')['records']:
    if record['url'] not in linked:
        continue
    q = record['quotes']
    if 'mobile' not in q['mobile'].lower():
        continue
    if not ('personal' in q['product'] or 'consumer' in q['product']):
        continue
    program_words = q['program'].casefold().split()
    identities = [value for key, value in selected.items() if key in program_words]
    if len(identities) != 1:
        raise AssertionError('Nonunique respondent')
    respondent, filing = identities[0]
    issuer = q['issuer']
    if issuer.startswith('available from '):
        bank = issuer.split('available from ', 1)[1].removesuffix(',')
    else:
        bank = issuer.split('issued by ', 1)[1].removesuffix('.')
    bank = canonical('issuer_bank', bank)
    rev = canonical('disclosure_revision', q['revision'])
    if len(rev) == 7:
        before_cutoff = rev <= '2026-09'
    else:
        before_cutoff = rev <= '2026-09-09'
    if before_cutoff:
        actual.append((respondent, filing, bank, certificates[bank], rev))

with (ROOT / 'oracle.psv').open(encoding='utf-8', newline='') as f:
    reader = csv.DictReader(f, delimiter='|')
    assert reader.fieldnames == columns
    expected = [tuple(canonical(c, row[c]) for c in columns) for row in reader]

assert len(actual) == len(set(actual)), 'Duplicate reconstructed rows'
assert set(actual) == set(expected), {'reconstructed': actual, 'oracle': expected}
keys = [tuple(row[columns.index(c)] for c in rules['row_key']) for row in actual]
assert len(keys) == len(set(keys)), 'Duplicate shared row keys'

go = j('GO.json')
cg = j('CG.json')
assert set(go) == set(cg) == {'instruction', 'output_format'}
assert cg['instruction'].startswith(go['instruction'])
assert cg['output_format'] == go['output_format']

print(json.dumps({'result': 'matched', 'rows': len(actual), 'shared_oracle': 'oracle.psv',
                  'shared_rules': 'rules.json'}, indent=2))
