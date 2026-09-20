"""Recompute deposited-study pairs from saved sources plus explicit reviewed pool decisions."""
import json
import pathlib
import re
import xml.etree.ElementTree as ET

C = pathlib.Path(__file__).resolve().parent
S = C / 'sources'

def text(pmcid):
    return ' '.join(''.join(ET.parse(S / 'fulltext' / (pmcid + '.xml')).getroot().itertext()).split())

def solve():
    raw = json.loads((S / 'downstream_2020.json').read_text())
    pool = json.loads((C / 'candidate_pool.json').read_text())
    assert raw['hitCount'] == len(raw['resultList']['result']) == len(pool) == 14
    assert {x['pmcid'] for x in raw['resultList']['result']} == {x['pmcid'] for x in pool}
    assert 'GSE145926' in (S / 'primary_seed.html').read_text()
    for x in pool:
        assert '2020-05-13' <= x['firstPublicationDate'] <= '2020-12-31'
        assert 'GSE145926' in text(x['pmcid'])
        assert x['decision'] and x['evidence']
    # Semantic paper-level inclusion/exclusion decisions are review inputs, not
    # invented source facts. These assertions check their decisive field evidence.
    pairs = []
    for pmcid, acc, marker in [
        ('PMC7367032', 'PXD019157', 'Filtered feature-barcode matrix'),
        ('PMC7405878', 'E-MTAB-9221', 'integrated with our own blood'),
        ('PMC7577733', 'GSE152586', 'Bulk RNA-seq from SARS-CoV-2 infected alveolospheres')]:
        t = text(pmcid)
        assert acc in t and marker in t
    geo = (S / 'deposit_records/GSE152586.soft').read_text()
    assert '!Series_pubmed_id = 33128895' in geo
    pride = json.loads((S / 'deposit_records/PXD019157.json').read_text())
    assert pride['accession'] == 'PXD019157' and '32697943' in json.dumps(pride)
    ae = json.loads((S / 'deposit_records/E-MTAB-9221.json').read_text())
    assert ae['accno'] == 'E-MTAB-9221' and '32810439' in json.dumps(ae)
    prior = (S / 'deposit_records/GSE141634.soft').read_text()
    assert '!Series_pubmed_id = 32661339' in prior
    assert 'GSE141634' in (S / 'prior_alveolosphere_nature.html').read_text()
    identities = json.loads((S / 'alveolosphere_identity.json').read_text())['resultList']['result']
    byid = {x['id']: x for x in identities}
    assert byid['32661339']['firstPublicationDate'] < byid['33128895']['firstPublicationDate']
    assert byid['32661339']['doi'] != byid['33128895']['doi']
    # Extract identities from the reviewed experimental-data clauses, then
    # apply the independently retrieved earlier-publication exclusion.
    annotations = json.loads((C / 'experimental_deposit_annotations.json').read_text())
    for annotation in annotations:
        pmcid = annotation['pmcid']
        paragraphs = list(ET.parse(S / 'fulltext' / (pmcid + '.xml')).getroot().iter('p'))
        actual = ' '.join(''.join(paragraphs[annotation['p_ordinal']].itertext()).split())
        assert actual == annotation['source_text']
        clause = annotation['generated_clause']
        assert clause in actual
        for acc in set(re.findall(r'\b(?:GSE\d+|E-MTAB-\d+|PXD\d+)\b', clause)):
            if acc == 'GSE141634':
                # This is excluded by the checked repository-to-earlier-paper
                # evidence above, not by a later paper's ambiguous label.
                continue
            pairs.append((pmcid, acc))
    return 'pmcid|deposit_accession\n' + ''.join('|'.join(x) + '\n' for x in sorted(pairs))

if __name__ == '__main__':
    result = solve()
    (C / 'oracle.psv').write_text(result)
    print(result, end='')
