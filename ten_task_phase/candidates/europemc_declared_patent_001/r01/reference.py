#!/usr/bin/env python3
"""Recompute from registered responses and attributed source excerpts.
Not executed by the constructing agent. Standard library only.
Usage: python reference.py --raw-dir /path/to/registered/responses > computed.psv
The supplied construction files must remain beside this script.
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
CUTOFF = '2026-09-09'
COLUMNS = ['paper_doi', 'jurisdiction', 'application_identifier',
           'first_application_publication', 'publication_date']

def text_of(el):
    return ' '.join(''.join(el.itertext()).split())

def field(text, label):
    m = re.search(r'^' + re.escape(label) + r'\s*\n\s*([^\n]+)', text, re.M)
    if not m:
        raise ValueError('Missing source field: ' + label)
    return m.group(1).strip()

def parse_patent(path):
    text = path.read_text(encoding='utf-8')
    app = field(text, 'Application number')
    jurisdiction = field(text, 'Authority')
    family = re.search(r'^## ID=(\d+)$', text, re.M).group(1)
    block = text.split('## Publications (', 1)[1].split('# Family', 1)[0]
    pubs = []
    for line in block.splitlines():
        m = re.match(r'((?:WO|EP|US)\d+([AB]\d))\s*\|\s*(\d{4}-\d{2}-\d{2})$', line.strip())
        if m:
            pubs.append((m.group(1), m.group(2), m.group(3)))
    countries = set(re.findall(r'^([A-Z]{2}) \(\d+\) \|', text, re.M))
    if not pubs or not countries:
        raise ValueError('Incomplete saved publication/family fields: ' + str(path))
    return {'application': app, 'jurisdiction': jurisdiction,
            'family': family, 'publications': pubs, 'countries': countries}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw-dir', type=Path, default=BASE)
    args = ap.parse_args()
    def raw(name):
        return (args.raw_dir / name).read_text(encoding='utf-8')

    corpus = json.loads(raw('d0024.response'))
    records = corpus['resultList']['result']
    assert len(records) == corpus['hitCount']
    identity = {r['pmid'] for r in records}
    assert len(identity) == len(records)
    for filename in ('d0001.response', 'd0003.response'):
        other = json.loads(raw(filename))
        assert len(other['resultList']['result']) == other['hitCount']
        assert {r['pmid'] for r in other['resultList']['result']} == identity

    # Mapping only: deliberately do not read included/reason values for selection.
    mapping = json.loads((BASE / 'candidate_pool.json').read_text())['papers']
    files_by_pmid = {p['pmid']: p['file'] for p in mapping}
    assert set(files_by_pmid) == identity
    disclosed = []
    for record in records:
        assert record['pubYear'] == '2019'
        assert record['journalInfo']['journal']['title'].lower() == 'genome biology'
        article = ET.fromstring(raw(files_by_pmid[record['pmid']]))
        ids = {x.attrib.get('pub-id-type'): text_of(x)
               for x in article.findall('./front/article-meta/article-id')}
        assert ids['doi'].lower() == record['doi'].lower()
        assert ids['pmid'] == record['pmid']
        assert any('10.1038/ncomms14049' in ET.tostring(r, encoding='unicode')
                   for r in article.findall('.//ref'))
        declarations = []
        for element in article.iter():
            if element.tag not in ('notes', 'sec'):
                continue
            title = element.find('title')
            if title is not None and text_of(title).lower() == 'competing interests':
                declarations.extend(text_of(p) for p in element.findall('p'))
        if not declarations:
            raise ValueError('Missing declaration for ' + record['doi'])
        declaration = ' '.join(declarations)
        if not re.search(r'\bpatent\b', declaration, re.I):
            continue
        # This is the observed unnumbered form, extracted from the raw declaration.
        match = re.search(r'patent application for the (.+?) method', declaration, re.I)
        if not match:
            raise ValueError('Observed declaration requires separate interpretation: ' + declaration)
        disclosed.append((ids['doi'].lower(), match.group(1)))

    bridge = (BASE / 'web/bridge.txt').read_text(encoding='utf-8')
    bridge_dois = set(re.findall(r'10\.1186/s13059-\d{3}-\d{4}-[a-z0-9]+', bridge, re.I))
    # The actual DOI uses a three-digit year fragment (019), matching the pattern.
    bridge_patents = set(re.findall(r'\bWO\d+A1\b', bridge))
    patents = [parse_patent(p) for p in sorted((BASE / 'web').glob('patent_*.txt'))]
    rows = []
    for doi, method in disclosed:
        if doi not in {d.lower() for d in bridge_dois}:
            raise ValueError('No saved explicit primary DOI bridge for ' + doi)
        if method.lower() not in bridge.lower():
            raise ValueError('No saved explicit primary method bridge for ' + method)
        seeds = [p for p in patents if any(pub in bridge_patents
                 for pub, kind, date in p['publications'])]
        if len(seeds) != 1:
            raise ValueError('Primary bridge does not resolve one saved patent record')
        seed = seeds[0]
        members = [p for p in patents if p['family'] == seed['family']]
        assert {p['jurisdiction'] for p in members} == seed['countries']
        assert all(p['countries'] == seed['countries'] for p in members)
        assert len({p['application'] for p in members}) == len(members)
        for p in members:
            # Saved histories contain A1 application publications and, for US, B2 grant.
            eligible = [(date, pub) for pub, kind, date in p['publications']
                        if kind == 'A1' and date <= CUTOFF]
            if eligible:
                date, pub = min(eligible)
                rows.append((doi, p['jurisdiction'], p['application'], pub, date))
    writer = csv.writer(sys.stdout, delimiter='|', lineterminator='\n')
    writer.writerow(COLUMNS)
    writer.writerows(sorted(set(rows)))

if __name__ == '__main__':
    main()
