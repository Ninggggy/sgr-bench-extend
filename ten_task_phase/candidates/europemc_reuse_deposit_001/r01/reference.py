#!/usr/bin/env python3
"""Compute from saved sources and explicit reviewed provenance annotations.
Usage: python reference.py SOURCE_ROOT [FILE_ID_PATH_MAP.json]
Only standard library; no network. Not executed by the constructing agent.
"""
import json
import re
import sys
import html
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE
PATHS = json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 else {}
HINTS = {
    'd0230': 'europepmc_seed_nature.html',
    'd0232': 'tau_author_manuscript.txt',
    'd0233': 'tau_author_manuscript_source.json',
    'd0235': 'review.json',
    'd0248': 'd0101.txt',
}

def read_raw(fid):
    if fid in PATHS:
        p = Path(PATHS[fid])
        if not p.is_absolute():
            p = ROOT / p
        return p.read_text(encoding='utf-8-sig')
    names = [fid + '.response']
    if fid in HINTS:
        names.append(HINTS[fid])
    names += [fid + '.json', fid + '.xml', fid + '.html', fid + '.txt']
    for name in names:
        found = sorted(p for p in ROOT.rglob(name) if p.is_file())
        if found:
            texts = {p.read_text(encoding='utf-8-sig') for p in found}
            if len(texts) != 1:
                raise ValueError('Multiple differing sources for ' + fid)
            return texts.pop()
    raise FileNotFoundError('Cannot resolve ' + fid + '; use the optional file-ID path mapping')

def norm(s):
    return ' '.join(html.unescape(s).split())

def xml_text(e):
    return norm(' '.join(e.itertext()))

def series(s):
    return set(re.findall(r'\bGSE[0-9]+\b', s))

def seed_accession():
    raw = read_raw('d0230')
    section = re.search(r'<section\b[^>]*data-title="Data availability"[^>]*>(.*?)</section>', raw, re.S)
    if section is None:
        raise ValueError('Seed data-availability section missing')
    values = series(html.unescape(section.group(1)))
    if len(values) != 1:
        raise ValueError('Seed series is not unique in its data statement')
    return values.pop()

def inspect_sources():
    seed = seed_accession()
    catalog = json.loads(read_raw('d0001'))
    query = f'ACCESSION_ID:{seed} AND FIRST_PDATE:[2020-01-01 TO 2021-12-31] AND OPEN_ACCESS:Y'
    assert catalog['request']['queryString'] == query
    records = catalog['resultList']['result']
    assert catalog['hitCount'] == len(records)
    assert len({r['pmcid'] for r in records}) == len(records)
    metadata = {r['pmcid']: r for r in records}
    pool = json.loads((HERE / 'candidate_pool.json').read_text())['rows']
    assert {r['pmcid'] for r in pool} == set(metadata)
    audit = []
    answer = set()
    for row in pool:
        pmcid = row['pmcid']
        meta = metadata[pmcid]
        assert meta['isOpenAccess'] == 'Y'
        assert '2020-01-01' <= meta['firstPublicationDate'] <= '2021-12-31'
        assert meta['firstPublicationDate'] == row['firstPublicationDate']
        raw = read_raw(row['file_id'])
        if row['file_id'] == 'd0232':
            text = norm(raw)
            assert meta['doi'] in text
            paragraphs = None
        else:
            tree = ET.fromstring(raw)
            ids = [norm(e.text or '') for e in tree.iter('article-id')
                   if e.get('pub-id-type') in ('pmc', 'pmcid')]
            assert any(v == pmcid or 'PMC' + v == pmcid for v in ids)
            text = xml_text(tree)
            paragraphs = [xml_text(e) for e in tree.iter('p')]
        assert seed in text, pmcid
        for anchor in row['anchors']:
            assert norm(anchor) in text, (pmcid, anchor)
        new_series = set()
        selector = row['new_selector']
        evidence = ''
        if selector:
            if paragraphs is None:
                start = text.index(selector)
                evidence = text[start:start + 600]
            else:
                candidates = [p for p in paragraphs if selector in p]
                assert candidates, pmcid
                evidence = min(candidates, key=len)
            new_series = series(evidence)
            assert new_series, pmcid
            assert seed not in new_series, pmcid
        # Inclusion is semantic annotation + source-backed evidence, not an oracle literal.
        if row['matrix_reuse']:
            answer.update((pmcid, accession) for accession in new_series)
        audit.append({'pmcid': pmcid, 'matrix_reuse': row['matrix_reuse'],
                      'new_series_from_source': sorted(new_series),
                      'evidence_locator': row['locators'], 'decision': row['decision']})
    review = json.loads(read_raw('d0235'))
    assert all(r['state'] == 'extracted' and not r['error'] for r in review)
    # This verifies supplied extraction records, not a fresh semantic review of every cell.
    supplements = [{'file_id': r['file_id'], 'source_url': r['source_url'],
                    'reported_accessions': r['geo_series']} for r in review]
    return sorted(answer), {'seed': seed, 'articles': audit, 'supplement_review': supplements}

def render(rows):
    return 'pmcid|new_geo_series\n' + ''.join(a + '|' + b + '\n' for a, b in rows)

def main():
    rows, audit = inspect_sources()
    result = render(rows)
    expected = (HERE / 'oracle.psv').read_text()
    assert result == expected, 'Computed result differs from supplied oracle'
    print(result, end='')
    print(json.dumps(audit, ensure_ascii=False), file=sys.stderr)

if __name__ == '__main__':
    main()
