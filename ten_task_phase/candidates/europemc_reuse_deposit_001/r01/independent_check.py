#!/usr/bin/env python3
"""Independent key-result checks; shares file reading only, not decisions.
Usage matches reference.py. No network or third-party packages.
"""
import json
import re
import html
from pathlib import Path
import xml.etree.ElementTree as ET
from reference import read_raw

BASE = Path(__file__).resolve().parent

def clean(s):
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()

def text(e):
    return clean(' '.join(e.itertext()))

def main():
    # Different seed extraction: find the statement around its sequencing sentence.
    seed_html = read_raw('d0230')
    start = seed_html.index('All single-cell RNA sequencing data are available')
    seed_statement = seed_html[start:seed_html.index('</p>', start)]
    seed_values = set(re.findall(r'GSE\d+', seed_statement))
    assert len(seed_values) == 1
    seed = seed_values.pop()
    found = set()
    for n in range(11, 20):
        tree = ET.fromstring(read_raw(f'd{n:04d}'))
        pmc_ids = [e.text for e in tree.iter('article-id')
                   if e.get('pub-id-type') in ('pmc', 'pmcid')]
        pmcid = next(x if x.startswith('PMC') else 'PMC' + x for x in pmc_ids)
        ps = [text(p) for p in tree.iter('p')]
        # Independent positive-method witness, specifically linked to the seed cohort.
        reuse = any(seed in p and 'LogNormalize' in p and
                    'FindIntegrationAnchors' in p for p in ps)
        if not reuse:
            continue
        for sec in tree.iter():  # JATS stores availability under notes as well as sec.
            heading = sec.find('title')
            if heading is None or text(heading).lower() != 'data availability':
                continue
            for p in sec.iter('p'):
                ptext = text(p)
                if 'from this study' in ptext and 'raw and processed data' in ptext:
                    for accession in re.findall(r'\bGSE\d+\b', ptext):
                        found.add((pmcid, accession))
    # Separate primary-source corroboration: reporting PDF text, not XML annotation.
    report = clean(read_raw('d0248'))
    confirmation = re.search(r'All raw data and relevant processed data are deposited at (GSE\d+)\.', report)
    assert confirmation is not None
    assert len(found) == 1
    assert {s for _, s in found} == {confirmation.group(1)}
    # Tau exclusion checked without candidate_pool or reference eligibility flags.
    tau = clean(read_raw('d0232'))
    i = tau.index('For human Alzheimer’s disease brain single cell signatures')
    sentence = tau[i:tau.index('Gene Set Annotation', i)]
    assert 'Grubman et al., 2019' in sentence
    assert 'published differential gene expression data' in sentence
    assert 'FDR < 0.05' in sentence and 'logFC > 0.1' in sentence
    assert '10.1016/j.celrep.2020.108398' in tau
    new_tau = re.search(r'RNaseq data of mice microglia cultures.*?accession number GEO: (GSE\d+)', tau)
    assert new_tau is not None
    assert new_tau.group(1) not in {s for _, s in found}
    # Independent pool-completeness and tested broad-query counterexample checks.
    catalog = json.loads(read_raw('d0001'))
    records = catalog['resultList']['result']
    assert len(records) == catalog['hitCount']
    complete_ids = {r['pmcid'] for r in records}
    intersection = json.loads(read_raw('d0225'))
    intersection_rows = intersection['resultList']['result']
    assert intersection['hitCount'] == len(intersection_rows)
    missing = complete_ids - {r['pmcid'] for r in intersection_rows}
    assert missing == {'PMC7994447'}
    expected = {tuple(line.split('|')) for line in
                (BASE / 'oracle.psv').read_text().splitlines()[1:] if line}
    assert found == expected
    print(json.dumps({'checked_pairs': sorted(found),
                      'reporting_pdf_series': confirmation.group(1),
                      'tau_new_series_but_gene_list_reuse': new_tau.group(1),
                      'broad_query_missing': sorted(missing)}))

if __name__ == '__main__':
    main()
