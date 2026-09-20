"""Separate data-section traversal and publication-provenance check; no reference import."""
import json
import pathlib
import re
from xml.dom import minidom

C = pathlib.Path(__file__).resolve().parent
S = C / 'sources'

def words(node):
    if node.nodeType in (node.TEXT_NODE, node.CDATA_SECTION_NODE):
        return node.data
    return ''.join(words(x) for x in node.childNodes)

def check():
    records = json.loads((S / 'downstream_2020.json').read_text())
    ids = [x['pmcid'] for x in records['resultList']['result']]
    assert len(ids) == len(set(ids)) == records['hitCount'] == 14
    found = set()
    for pmc in ids:
        doc = minidom.parse(str(S / 'fulltext' / (pmc + '.xml')))
        assert 'GSE145926' in words(doc)
        for p in doc.getElementsByTagName('p'):
            t = ' '.join(words(p).split())
            if t.startswith('The mass spectrometry proteomics data have been deposited'):
                clause = t
            elif t.startswith('All blood scRNA-seq data used in this study'):
                clause = t[:t.index('Integrated BALF')]
            elif t.startswith('RNA-seq data that support the findings'):
                clause = t[:t.index('Previously published')]
            else:
                continue
            for accession in re.findall(r'(?<![A-Z0-9])(?:PXD[0-9]+|GSE[0-9]+|E-MTAB-[0-9]+)(?![0-9])', clause):
                found.add((pmc, accession))
    assert len(found) == 4
    # Independent provenance traversal identifies the prior-study deposit.
    paper_ids = {x['pmcid']: x['id'] for x in records['resultList']['result']}
    excluded = []
    for pmc, acc in list(found):
        f = S / 'deposit_records' / (acc + '.soft')
        if not f.exists():
            continue
        linked = re.findall(r'^!Series_pubmed_id = (\d+)$', f.read_text(), re.M)
        if paper_ids[pmc] not in linked:
            old = json.loads((S / 'alveolosphere_identity.json').read_text())['resultList']['result']
            linked_papers = [x for x in old if x['id'] in linked]
            current = next(x for x in old if x['id'] == paper_ids[pmc])
            assert len(linked_papers) == 1
            assert linked_papers[0]['firstPublicationDate'] < current['firstPublicationDate']
            assert acc in (S / 'prior_alveolosphere_nature.html').read_text()
            found.remove((pmc, acc)); excluded.append([pmc, acc, linked])
    actual = {tuple(line.split('|')) for line in (C / 'oracle.psv').read_text().splitlines()[1:]}
    assert found == actual and len(found) == 3
    return {'status': 'passed', 'complete_indexed_pool': 14, 'deposited_pairs_before_provenance': 4,
            'excluded_prior_experimental_studies': excluded, 'answer_pairs': sorted(found),
            'limits': 'Independent source parsing and provenance cross-check, not human expert validation or completed external quality audit.'}

if __name__ == '__main__':
    result = check()
    (C / 'independent_result.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result))
