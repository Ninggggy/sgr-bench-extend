#!/usr/bin/env python3
"""Independent field/history check; not executed by constructing agent.
Usage: python independent_check.py computed.psv
Uses distinct Info fields for WO/EP, original US front-page fields, and a
separate history display. Does not import reference.py or read oracle.psv.
"""
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent

def read(name):
    return (BASE / name).read_text(encoding='utf-8')

def field(text, label):
    match = re.search(r'^' + re.escape(label) + r'\s*\n\s*([^\n]+)', text, re.M)
    assert match, label
    return match.group(1).strip()

def main():
    cg, go = (json.loads(read(n)) for n in ('CG.json', 'GO.json'))
    assert set(cg) == set(go) == {'instruction', 'output_format'}
    assert cg['instruction'].startswith(go['instruction'] + ' ')
    assert cg['output_format'] == go['output_format']

    publisher = read('web/publisher.txt')
    doi = field(publisher, 'DOI')
    method = re.search(r'patent application for the (.+?) method', publisher).group(1)
    bridge = read('web/bridge.txt')
    assert doi in bridge and method.lower() in bridge.lower()
    expected = []
    # Separate metadata fields from the publication-table selection in reference.py.
    for name in ('web/patent_wo.txt', 'web/patent_ep.txt'):
        text = read(name)
        expected.append((doi, field(text, 'Authority'), field(text, 'Application number'),
                         field(text, 'Publication number'), field(text, 'Publication date')))

    front = read('web/us_frontpage.txt')
    publication = re.search(r'US 2019 / 0002953 A1', front).group(0).replace(' ', '').replace('/', '')
    app = re.search(r'15 / 765 , 742', front).group(0).replace(' ', '')
    date_text = re.search(r'Jan\. 3, 2019', front).group(0)
    date = datetime.strptime(date_text, '%b. %d, %Y').date()
    assert 'Patent Application Publication' in front
    expected.append((doi, 'US', 'US' + app, publication, date.isoformat()))

    history = read('web/us_history.txt')
    entries = []
    for kind, number, written_date, application in re.findall(
            r'^(Application|Grant)\|([^|]+)\|([^|]+)\|([^\n]+)$', history, re.M):
        entries.append((kind, number, datetime.strptime(written_date, '%b %d, %Y').date(), application))
    apps = [x for x in entries if x[0] == 'Application' and x[3] == app]
    grants = [x for x in entries if x[0] == 'Grant' and x[3] == app]
    first = min(apps, key=lambda x: x[2])
    assert first[2] == date
    assert publication == 'US' + first[1] + 'A1'
    grant = min(grants, key=lambda x: x[2])
    assert date < grant[2]
    interval = (grant[2] - date).days
    # Independently inspected dates: the expected arithmetic result is 719 days.
    assert interval == 719

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / 'computed.psv'
    with target.open(newline='', encoding='utf-8') as stream:
        reader = csv.reader(stream, delimiter='|')
        header = next(reader)
        actual = [tuple(row) for row in reader]
    assert header == ['paper_doi', 'jurisdiction', 'application_identifier',
                      'first_application_publication', 'publication_date']
    assert actual == sorted(expected)
    print(json.dumps({'rows_checked': len(actual), 'us_publication_to_grant_days': interval,
                      'field_check': 'matches supplied independent evidence',
                      'limit': 'WO/EP checks use distinct fields of the same display; US uses an original-document facsimile.'}))

if __name__ == '__main__':
    main()
