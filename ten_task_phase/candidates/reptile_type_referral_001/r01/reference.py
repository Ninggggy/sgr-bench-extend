"""Provisional reconstruction only. Not executed during source exploration.
Usage: python reference.py /path/to/preserved/raw > computed.psv
Uses only the standard library and saved downloads. Performs no network access.
"""
import csv
import html
import io
import json
import re
import sys
from pathlib import Path

BASE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
HERE = Path(__file__).resolve().parent
SOURCES = json.loads((HERE / 'sources.json').read_text(encoding='utf-8'))
PAGES = {s['species']: s['raw_file'] for s in SOURCES if 'species' in s}

def locate(name):
    direct = BASE / name
    if direct.is_file():
        return direct
    hits = list(BASE.rglob(name))
    if len(hits) != 1:
        raise RuntimeError(f'Expected one preserved raw file {name}, found {len(hits)}')
    return hits[0]

def read(name):
    return locate(name).read_text(encoding='utf-8-sig')

def clean(s):
    return ' '.join(html.unescape(re.sub(r'<[^>]*>', ' ', s)).split())

def fields(raw):
    result = {}
    for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>', raw, re.S | re.I):
        cells = re.findall(r'<td\b[^>]*>(.*?)</td>', row, re.S | re.I)
        if len(cells) >= 2:
            result[clean(cells[0])] = clean(cells[1])
    return result

def species_fields(name):
    raw = read(PAGES[name])
    title = re.search(r'<h1\b[^>]*>(.*?)</h1>', raw, re.S | re.I)
    assert title and clean(title.group(1)).startswith(name + ' '), name
    return fields(raw)

def year(authority):
    years = re.findall(r'\b\d{4}\b', authority)
    assert len(years) == 1, authority
    return int(years[0])

reader = csv.DictReader(io.StringIO(read('d0006.response')), delimiter=';')
required = {'genus', 'specific_epithet', 'authority', 'infraspecific_marker'}
assert required.issubset(reader.fieldnames)
accepted = {}
for row in reader:
    if row.get('infraspecific_marker'):
        continue
    name = row['genus'] + ' ' + row['specific_epithet']
    assert name not in accepted, name
    accepted[name] = row

seed = sorted(name for name, row in accepted.items()
              if row['genus'] == 'Chelodina' and year(row['authority']) < 1900)
assert seed, 'Empty seed collection'
referrals = []
for name in seed:
    text = species_fields(name)['Types']
    if 'accession books' not in text:
        continue
    for match in re.finditer(r'while\s+([0-9.]+)\s+is identified as\s+([A-Z][a-z]+ [a-z]+)', text):
        number, target = match.groups()
        assert target in accepted, f'Referred name needs additional resolution: {target}'
        if accepted[target]['genus'] != 'Chelodina':
            referrals.append((name, number, target))
assert len(referrals) == 1, referrals
referred = referrals[0][2]
species_fields(referred)  # Confirm the retrieved accepted record exists.
target_genus = accepted[referred]['genus']
targets = sorted(name for name, row in accepted.items()
                 if row['genus'] == target_genus and year(row['authority']) < 1900)

out = csv.writer(sys.stdout, delimiter='|', lineterminator='\n')
out.writerow(['accepted_species', 'description_year', 'holotype_catalogue'])
for name in targets:
    account = species_fields(name)['Types']
    # Inspected records place the unqualified own-species holotype first.
    # Later lines explicitly attribute other specimens to synonyms/subspecies.
    match = re.match(r'Holotype:\s*([A-Z][A-Z-]*\s+[0-9]+(?:\.[0-9]+)*)\b', account)
    assert match, f'Own-species holotype requires review: {name}: {account}'
    out.writerow([name, year(accepted[name]['authority']), match.group(1)])
