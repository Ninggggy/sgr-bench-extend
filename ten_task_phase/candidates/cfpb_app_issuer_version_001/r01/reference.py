import csv
import io
import json
import re
import sys
from datetime import datetime, date
from pathlib import Path

# Offline reconstruction only. No network access or model calls.
# This script was supplied for controller execution; it was not run by the constructor.
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent

def read_json(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

def registered_text(stem):
    paths = [ROOT / (stem + '.txt'), ROOT / (stem + '.response'), ROOT / stem]
    path = next((p for p in paths if p.is_file()), None)
    if path is None:
        raise FileNotFoundError('Missing registered primary input: ' + stem + '.response')
    value = path.read_text(encoding='utf-8')
    # The supplied primary web records are JSON envelopes. Handle a read_text
    # envelope as well if the controller preserves that representation.
    for _ in range(5):
        if isinstance(value, dict):
            if 'result' in value:
                value = value['result']
            elif 'text' in value:
                value = value['text']
            elif 'content' in value:
                value = value['content'][0]['text']
            else:
                raise ValueError('Unrecognized registered input envelope')
        elif isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                break
        else:
            raise ValueError('Unrecognized registered input type')
    if not isinstance(value, str):
        raise ValueError('Expected primary source text')
    return value.replace('\\n', '\n')

def institution_key(name):
    s = name.casefold().strip()
    s = re.sub(r',\s*the$', '', s)
    s = re.sub(r'^the\s+', '', s)
    s = s.replace('national association', 'na')
    return re.sub(r'[^a-z0-9]', '', s)

def revision(label):
    m = re.fullmatch(r'Rev\. (\d{2})/(\d{4})', label)
    if m:
        month, year = map(int, m.groups())
        return f'{year:04d}-{month:02d}', date(year, month, 1)
    prefix = 'Last Updated: '
    if label.startswith(prefix):
        d = datetime.strptime(label[len(prefix):], '%B %d, %Y').date()
        return d.isoformat(), d
    raise ValueError('Unrecognized source revision label: ' + label)

def reconstruct():
    actions = read_json('evidence/actions.json')['records']
    eligible = []
    for a in actions:
        q = a['quotes']
        filed = datetime.strptime(q['date'], '%B %d, %Y').date()
        if date(2024, 4, 1) <= filed <= date(2024, 6, 30):
            if re.search(r'\b(?:fintech|financial-technology) company\b', q['description']):
                eligible.append((q['title'], filed.isoformat()))

    indexes = read_json('evidence/indexes.json')['records']
    current_standard_urls = {
        link['url']
        for index in indexes for link in index['links']
        if 'Deposit Account Agreement' in link['label']
        and 'Archived' not in link['label']
    }

    nic = registered_text('d0004')
    registry = {}
    for name, cert in re.findall(
        r'Legal Name: ([^\n]+)[\s\S]*?FDIC Certificate #: (\d+)', nic
    ):
        key = institution_key(name)
        if key in registry and registry[key] != cert:
            raise ValueError('Conflicting regulator identities')
        registry[key] = cert

    cra = registered_text('d0005')
    m = re.search(r'L4@P0: ([^\n]+)\nL5@P0: Certificate Number: (\d+)', cra)
    if not m:
        raise ValueError('2021 CRA front-page identity evidence not found')
    registry[institution_key(m[1])] = m[2]

    result = set()
    for document in read_json('evidence/agreements.json')['records']:
        if document['url'] not in current_standard_urls:
            continue
        q = document['quotes']
        if 'mobile' not in q['mobile'].casefold():
            continue
        if not any(x in q['product'] for x in ('personal, checkless account', 'consumer deposit account')):
            continue
        label, revision_floor = revision(q['revision'])
        if revision_floor > date(2026, 9, 9):
            continue
        # Match the source program identity to the qualifying corporate name.
        # No answer names or certificates are embedded in this computation.
        matches = [(name, filed) for name, filed in eligible
                   if name.split()[0].casefold() in q['program'].casefold().split()]
        if len(matches) != 1:
            raise ValueError('Program-to-respondent identity is not unique')
        respondent, filed = matches[0]
        if q['issuer'].startswith('available from '):
            issuer = q['issuer'][len('available from '):].rstrip(',')
        else:
            issuer = re.search(r'issued by (.+)\.$', q['issuer']).group(1)
        cert = registry[institution_key(issuer)]
        result.add((respondent, filed, issuer, cert, label))
    return sorted(result)

if __name__ == '__main__':
    columns = read_json('rules.json')['columns']
    output = io.StringIO(newline='')
    writer = csv.writer(output, delimiter='|', lineterminator='\n')
    writer.writerow(columns)
    writer.writerows(reconstruct())
    sys.stdout.write(output.getvalue())
