#!/usr/bin/env python3
"""Offline reconstruction of epmc_quantitative_001 r01 from saved public responses.

No network, third-party dependencies, hardcoded final rows, or historical replay.
The controller executes this program; constructor execution is not claimed.
"""
import argparse
import csv
import json
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import parse_qsl, urlsplit
import xml.etree.ElementTree as ET

BASE = 'https://www.ebi.ac.uk/europepmc/webservices/rest/'
ANNUAL = BASE + 'search?query=ISSN%3A0940-1334%20AND%20PUB_YEAR%3A2026&format=json&resultType=lite&pageSize=1000'
COLUMNS = ['original_pmcid', 'original_doi', 'initial_n', 'analyzed_n', 'help_n', 'nondepressed_n', 'analysis_population']
SCOPE_FIELDS = ['source', 'id', 'pmcid', 'doi', 'title', 'pubYear', 'journalVolume', 'issue', 'pubType', 'journalIssn']
BUNDLE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def norm(value):
    return ' '.join(unicodedata.normalize('NFKC', str(value)).split())


def text(element):
    require(element is not None, 'Missing XML element')
    return norm(' '.join(element.itertext()))


def paragraph(root, ident):
    nodes = root.findall(".//body//p[@id='%s']" % ident)
    require(len(nodes) == 1, 'Missing or duplicate paragraph ' + ident)
    return text(nodes[0])


def match(pattern, value):
    result = re.search(pattern, value, re.I)
    require(result is not None, 'Unmatched source anchor: ' + pattern)
    return result


def article_id(root, kind):
    nodes = root.findall("./front/article-meta/article-id[@pub-id-type='%s']" % kind)
    require(len(nodes) == 1, 'Missing or duplicate article identity: ' + kind)
    return text(nodes[0])


def url_key(url):
    p = urlsplit(url)
    return (p.netloc.lower(), p.path.rstrip('/'), tuple(sorted(parse_qsl(p.query))))


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def jsonl(path, rows):
    path.write_text(''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in rows), encoding='utf-8')


class SourceBank:
    """Resolve registry URL/path records, including paths relocated by copying."""
    def __init__(self, directory):
        self.directory = Path(directory).resolve()
        registry = self.directory / 'registry.json'
        require(registry.is_file(), 'Missing source registry: ' + str(registry))
        self.entries = []
        self.used = {}
        self.walk(json.loads(registry.read_text(encoding='utf-8')))

    def walk(self, value, inherited_url=None):
        if isinstance(value, dict):
            url = value.get('url') or value.get('requested_url') or value.get('final_url') or inherited_url
            if isinstance(url, str) and url.startswith('https://'):
                for key in ('path', 'file_path', 'local_path', 'saved_path', 'body_path', 'response_path', 'filename', 'file', 'file_id'):
                    pointer = value.get(key)
                    if isinstance(pointer, str):
                        self.entries.append((url, pointer))
            for key, child in value.items():
                if isinstance(key, str) and key.startswith('https://'):
                    if isinstance(child, str):
                        self.entries.append((key, child))
                    else:
                        self.walk(child, key)
                elif isinstance(child, (dict, list)):
                    self.walk(child, url)
        elif isinstance(value, list):
            for child in value:
                self.walk(child, inherited_url)

    def paths(self, pointer):
        p = Path(pointer)
        candidates = []
        if not p.is_absolute():
            candidates.append(self.directory / p)
        candidates.append(self.directory / p.name)
        candidates.extend(self.directory.rglob(p.name))
        if not p.suffix:
            candidates.extend(self.directory.rglob(p.name + '.*'))
        return sorted({q.resolve() for q in candidates if q.is_file() and q.name != 'registry.json'})

    def read(self, url):
        candidates = set()
        for registered_url, pointer in self.entries:
            if url_key(registered_url) == url_key(url):
                candidates.update(self.paths(pointer))
        valid = []
        wanted_pmcid = re.search(r'/(PMC\d+)/fullTextXML', url)
        for path in sorted(candidates):
            raw = path.read_bytes()
            try:
                if wanted_pmcid:
                    parsed = ET.fromstring(raw)
                    if article_id(parsed, 'pmcid') != wanted_pmcid.group(1):
                        continue
                    signature = ET.tostring(parsed, encoding='unicode')
                else:
                    parsed = json.loads(raw)
                    if not isinstance(parsed, dict) or 'resultList' not in parsed:
                        continue
                    if norm(parsed.get('request', {}).get('queryString', '')) != 'ISSN:0940-1334 AND PUB_YEAR:2026':
                        continue
                    signature = json.dumps(scope_snapshot(parsed), sort_keys=True)
                valid.append((path, raw, parsed, signature))
            except (ValueError, TypeError, ET.ParseError, UnicodeError):
                continue
        require(valid, 'No valid saved response resolved for ' + url)
        require(len({v[3] for v in valid}) == 1, 'Conflicting saved responses for ' + url)
        path, raw, parsed, _ = valid[0]
        self.used[url] = {'url': url, 'path': str(path.relative_to(self.directory)), 'bytes': len(raw)}
        return parsed


def scope_snapshot(document):
    rows = document.get('resultList', {}).get('result', [])
    selected = [{k: str(r.get(k, '')) for k in SCOPE_FIELDS} for r in rows]
    return {'hitCount': document.get('hitCount'), 'records': sorted(selected, key=lambda r: (r['source'], r['id']))}


def notice_flags(row):
    types = str(row.get('pubType', '')).lower()
    by_type = bool(re.search(r'\b(correction|corrigendum|erratum)\b', types))
    by_title = bool(re.match(r'^\s*(Correction|Corrigendum|Erratum)\b', str(row.get('title', '')), re.I))
    return by_type, by_title


def annual_scope(bank):
    document = bank.read(ANNUAL)
    rows = document['resultList']['result']
    request = document.get('request', {})
    require(request.get('resultType') == 'lite', 'Annual response is not lite')
    require(request.get('cursorMark') == '*', 'Annual response does not start at first cursor')
    require(len(rows) == int(document['hitCount']), 'Incomplete annual response; pagination required')
    keys = [(str(r.get('source', '')), str(r.get('id', ''))) for r in rows]
    require(len(keys) == len(set(keys)), 'Duplicate annual source/id records')
    require(all(str(r.get('pubYear')) == '2026' for r in rows), 'Unexpected indexed year')
    issue = sorted([r for r in rows if str(r.get('journalVolume')) == '276' and str(r.get('issue')) == '2'], key=lambda r: (r['source'], r['id']))
    return document, rows, issue


def evidence(field, row, sources, formula):
    return {'row_key': [row['original_pmcid'], row['original_doi']], 'field': field, 'value': row[field], 'sources': sources, 'formula': formula}


def solve(bank, out):
    document, annual, issue = annual_scope(bank)
    jsonl(out / 'annual_index.jsonl', sorted(annual, key=lambda r: (r['source'], r['id'])))
    jsonl(out / 'issue_index.jsonl', issue)
    dump(out / 'scope_snapshot.json', scope_snapshot(document))
    screening = []
    for record in issue:
        by_type, by_title = notice_flags(record)
        screening.append({**record, 'notice_by_type': by_type, 'notice_by_title': by_title, 'candidate_notice': by_type or by_title})
    jsonl(out / 'issue_screening.jsonl', screening)
    notices = [r for r in screening if r['candidate_notice']]
    jsonl(out / 'candidate_universe.jsonl', notices)
    inventory_path = BUNDLE / 'sources' / 'issue_membership.psv'
    with inventory_path.open(encoding='utf-8', newline='') as handle:
        inventory = list(csv.DictReader(handle, delimiter='|'))
    observed_inventory = [(r['source'], r['id'], r.get('pmcid', ''), str(r['candidate_notice']).lower()) for r in screening]
    saved_inventory = [(r['source'], r['id'], r['pmcid'], r['candidate_notice']) for r in inventory]
    require(observed_inventory == saved_inventory, 'Issue membership differs from saved construction observation')
    require(len(annual) == 360 and len(issue) == 47 and len(notices) == 2, 'Observed slice changed; do not reuse this reference silently')
    typed = {(r['source'], r['id']) for r in screening if r['notice_by_type']}
    titled = {(r['source'], r['id']) for r in screening if r['notice_by_title']}
    require(typed == titled, 'Independent metadata notice screens disagree')
    ledger, fields, intermediate, counterfactuals, rows = [], [], [], [], []
    try:
        for notice in notices:
            pmcid = notice.get('pmcid', '')
            require(re.fullmatch(r'PMC\d+', pmcid) is not None, 'Candidate notice has no resolved PMCID')
            notice_url = BASE + pmcid + '/fullTextXML'
            root = bank.read(notice_url)
            require(root.attrib.get('article-type') == 'correction', 'Unexpected candidate XML type')
            require(article_id(root, 'doi') == notice['doi'], 'Notice metadata/XML DOI mismatch')
            entry = {'notice_pmcid': pmcid, 'issue_member': 'true', 'candidate_notice': 'true', 'body_inspected': 'true', 'include': 'unknown'}
            ledger.append(entry)
            body_paragraphs = [text(p) for p in root.findall('./body/p')]
            author_pattern = r'^In this article the author’s name .+ was incorrectly written as .+\.$'
            author_changes = [p for p in body_paragraphs if re.match(author_pattern, p)]
            if author_changes:
                allowed = all(re.match(author_pattern, p) or p.startswith('Correction: European Archives') or re.fullmatch(r'10\.\d{4,9}/\S+', p) or p == 'The original article has been corrected.' for p in body_paragraphs)
                require(allowed and len(author_changes) == 1 and not root.findall('./body//table-wrap'), 'Author notice has additional unresolved substantive content')
                entry.update({'participant_count_or_population_correction': 'false', 'author_only': 'true', 'include': 'false', 'original_population_evidence': 'unknown', 'evidence': author_changes, 'reason': 'Only substantive correction is an author name; no original data retrieval required.'})
                continue
            p4 = paragraph(root, 'Par4')
            help_match = match(r'professional psychiatric or psychological help has been corrected to n\s*=\s*(\d+), replacing the previously stated n\s*=\s*(\d+)', p4)
            group_match = match(r'outpatient individuals has been corrected to n\s*=\s*(\d+) from n\s*=\s*(\d+)', p4)
            require('erroneously referred to admissions to psychiatric units or day clinics' in p4, 'Admissions/help semantic anchor missing')
            entry.update({'participant_count_or_population_correction': 'true', 'author_only': 'false', 'include': 'true'})
            original_doi = match(r'10\.\d{4,9}/[^\s]+', paragraph(root, 'Par1')).group(0)
            metadata_matches = [r for r in annual if r.get('doi') == original_doi]
            require(len(metadata_matches) == 1, 'Original DOI identity join is not unique')
            original_meta = metadata_matches[0]
            original_pmcid = original_meta.get('pmcid', '')
            require(re.fullmatch(r'PMC\d+', original_pmcid) is not None, 'Original PMCID unresolved')
            links = root.findall("./front/article-meta/related-article[@related-article-type='corrected-article']/ext-link[@ext-link-type='pmcid']")
            linked = {el.attrib.get('{http://www.w3.org/1999/xlink}href') for el in links}
            require(linked == {original_pmcid}, 'Notice PMCID link and DOI metadata join disagree')
            original_url = BASE + original_pmcid + '/fullTextXML'
            original = bank.read(original_url)
            require(article_id(original, 'pmcid') == original_pmcid and article_id(original, 'doi') == original_doi, 'Original XML identity mismatch; PMCAID must not substitute for PMCID')
            p9, p12, p32 = [paragraph(original, ident) for ident in ('Par9', 'Par12', 'Par32')]
            cohort = match(r'A subset of (\d+) participants \(of initially (\d+), incl\. (\d+) dropouts\)', p12)
            analyzed, initial, dropouts = map(int, cohort.groups())
            require('the current analysis is limited to the cross-sectional data collected at study inclusion' in p9, 'Analysis window semantic anchor missing')
            assessment = match(r'completed the (.+?) diagnostic assessment at baseline and returned the questionnaires that were part of the assessment', p12).group(1)
            population = ';'.join(['baseline', assessment, 'returned'])
            help_n, old_help = map(int, help_match.groups())
            nondep, old_nondep = map(int, group_match.groups())
            headers = text(root.find("./body/table-wrap[@id='Tab1']/table/thead"))
            table_nondep = int(match(r'Non-depressed\s*\(N\s*=\s*(\d+)\)', headers).group(1))
            table_dep = int(match(r'(?<!-)\bDepressed\s*\(N\s*=\s*(\d+)\)', headers).group(1))
            result_groups = match(r'with \(n\s*=\s*(\d+)\) and without \(n\s*=\s*(\d+)\) depression, as determined via a SCID-5 rating', p32)
            result_dep, result_nondep = map(int, result_groups.groups())
            result_help = int(match(r'(\d+) participants reported having sought professional psychiatric or psychological help in the past', p32).group(1))
            require(nondep == table_nondep == result_nondep, 'Non-depressed count/meaning disagreement')
            require(table_dep == result_dep and table_dep + table_nondep == analyzed, 'Group-sum and direct analyzed-total disagreement')
            require(help_n == result_help, 'Notice/original prior-help count disagreement')
            require(0 <= help_n <= analyzed <= initial and 0 <= dropouts <= initial, 'Invalid population count bounds')
            row = dict(zip(COLUMNS, [original_pmcid, original_doi, initial, analyzed, help_n, nondep, population]))
            rows.append(row)
            entry.update({'original_doi': original_doi, 'original_pmcid': original_pmcid, 'identity_agreement': 'true', 'numerical_agreement': 'true', 'semantic_scope': 'true'})
            anchors = {
                'original_pmcid': [(notice_url, 'corrected-article/ext-link/@xlink:href'), (ANNUAL, 'DOI-matched result.pmcid'), (original_url, "article-id[@pub-id-type='pmcid']")],
                'original_doi': [(notice_url, 'Par1'), (ANNUAL, 'DOI-matched result.doi'), (original_url, "article-id[@pub-id-type='doi']")],
                'initial_n': [(original_url, 'Par12')],
                'analyzed_n': [(original_url, 'Par12'), (notice_url, 'Tab1/thead')],
                'help_n': [(notice_url, 'Par4'), (original_url, 'Par32')],
                'nondepressed_n': [(notice_url, 'Par4'), (notice_url, 'Tab1/thead'), (original_url, 'Par32')],
                'analysis_population': [(original_url, 'Par9'), (original_url, 'Par12')]
            }
            formulas = {
                'original_pmcid': 'Agreement of source-linked PMCID, annual DOI join and original XML PMCID; ignore PMCAID.',
                'original_doi': 'Extract notice original DOI and verify annual join and original XML.',
                'initial_n': 'Extract initially integer without subtracting source-included dropouts.',
                'analyzed_n': 'Extract subset integer; verify corrected Tab1 non-depressed N + depressed N.',
                'help_n': 'Extract corrected help integer; verify original Results prior-help count.',
                'nondepressed_n': 'Extract revised integer; verify corrected table group and original diagnostic group.',
                'analysis_population': 'Validate cross-section-at-inclusion anchor; extract completed baseline assessment; validate returned-questionnaires inclusion clause.'
            }
            for field in COLUMNS:
                fields.append(evidence(field, row, [{'url': u, 'locator': loc} for u, loc in anchors[field]], formulas[field]))
            intermediate.append({'notice_pmcid': pmcid, **row, 'source_included_dropouts': dropouts, 'depressed_n_check': table_dep, 'old_help_value_quoted_by_notice': old_help, 'old_nondepressed_value_quoted_by_notice': old_nondep, 'source_anchors': {'Par9': p9, 'Par12': p12, 'Par32': p32, 'notice_Par4': p4}})
            for field, wrong, interpretation in [('analyzed_n', initial, 'Mistake initial cohort for analyzed subset'), ('help_n', old_help, 'Substitute quoted admissions value for prior help'), ('nondepressed_n', old_nondep, 'Retain notice-quoted superseded group count')]:
                counterfactuals.append({'row_key': [original_pmcid, original_doi], 'field': field, 'correct': row[field], 'wrong': wrong, 'delta': wrong - row[field], 'interpretation': interpretation, 'historical_replay': False})
            notice_all = text(root)
            counterfactuals.append({'row_key': [original_pmcid, original_doi], 'path': 'notice_only', 'has_initial_cohort_anchor': bool(re.search(r'of initially \d+', notice_all)), 'has_completed_assessment_inclusion_anchor': 'completed the SCID-5 diagnostic assessment at baseline' in notice_all, 'has_questionnaire_return_inclusion_anchor': 'returned the questionnaires that were part of the assessment' in notice_all, 'claim': 'Notice supplies corrected counts but does not establish all required population fields.'})
        require(all(r['include'] != 'unknown' for r in ledger), 'Unresolved notice qualification')
    finally:
        jsonl(out / 'inclusion_ledger.jsonl', ledger)
        jsonl(out / 'field_evidence.jsonl', fields)
        jsonl(out / 'normalized_studies.jsonl', intermediate)
        dump(out / 'resolved_source_manifest.json', list(bank.used.values()))
    consolidated = {}
    conflicts = []
    for row in rows:
        doi = row['original_doi']
        if doi not in consolidated:
            consolidated[doi] = dict(row)
        else:
            previous = consolidated[doi]
            require(previous['original_pmcid'] == row['original_pmcid'], 'Conflicting original identity requires revision')
            for field in COLUMNS[2:]:
                if previous[field] != row[field]:
                    conflicts.append({'doi': doi, 'field': field, 'values': [previous[field], row[field]]})
                    previous[field] = 'UNKNOWN'
    result = sorted(consolidated.values(), key=lambda r: (r['original_doi'], r['original_pmcid']))
    require(len({(r['original_pmcid'], r['original_doi']) for r in result}) == len(result), 'Duplicate output row keys')
    with (out / 'oracle.psv').open('w', encoding='utf-8', newline='') as handle:
        if not result:
            handle.write('NONE\n')
        else:
            writer = csv.DictWriter(handle, fieldnames=COLUMNS, delimiter='|', lineterminator='\n')
            writer.writeheader()
            writer.writerows(result)
    dump(out / 'counterfactuals.json', {'execution': 'offline Python source reconstruction', 'cases': counterfactuals, 'conflicts': conflicts})
    dump(out / 'nalpa_comparison.json', {'notice_keys_by_type': sorted(typed), 'notice_keys_by_title': sorted(titled), 'sets_equal': typed == titled, 'included_notice_keys': [e['notice_pmcid'] for e in ledger if e['include'] == 'true'], 'excluded_notice_keys': [e['notice_pmcid'] for e in ledger if e['include'] == 'false'], 'unknown_notice_keys': [e['notice_pmcid'] for e in ledger if e['include'] == 'unknown']})
    return {'annual_records': len(annual), 'issue_records': len(issue), 'issue_pmcids': len({r['pmcid'] for r in issue if r.get('pmcid')}), 'candidate_notices': len(notices), 'output_rows': len(result), 'conflicts': conflicts, 'checks': ['complete annual range', 'complete issue inventory', 'type/title notice set agreement', 'all candidate notices classified', 'author-only boundary excluded', 'DOI and PMCID identity agreement', 'notice/table/original numerical agreement', 'semantic source anchors validated', 'unique sorted output keys']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', required=True)
    parser.add_argument('--out-dir', default='rebuilt')
    parser.add_argument('--expected-oracle')
    parser.add_argument('--compare-source-dir', help='Separately saved later live observation; compare full scope and required XMLs without network')
    args = parser.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    try:
        bank = SourceBank(args.source_dir)
        report = solve(bank, out)
        if args.expected_oracle:
            expected = Path(args.expected_oracle).read_text(encoding='utf-8').replace('\r\n', '\n')
            actual = (out / 'oracle.psv').read_text(encoding='utf-8')
            require(actual == expected, 'Rebuilt oracle differs from supplied provisional oracle')
            report['expected_oracle_equal'] = True
        if args.compare_source_dir:
            later = SourceBank(args.compare_source_dir)
            old_document, _, old_issue = annual_scope(bank)
            new_document, _, new_issue = annual_scope(later)
            stability = {'annual_scope_equal': scope_snapshot(old_document) == scope_snapshot(new_document), 'issue_scope_equal': [{k: str(r.get(k, '')) for k in SCOPE_FIELDS} for r in old_issue] == [{k: str(r.get(k, '')) for k in SCOPE_FIELDS} for r in new_issue], 'required_xml_equal': {}}
            for url in list(bank.used):
                if url.endswith('/fullTextXML'):
                    stability['required_xml_equal'][url] = ET.tostring(bank.read(url)) == ET.tostring(later.read(url))
            dump(out / 'stability.json', stability)
            require(stability['annual_scope_equal'] and stability['issue_scope_equal'] and all(stability['required_xml_equal'].values()), 'Later live source differs; review before reusing oracle')
            report['stability_check'] = 'passed'
        report.update({'status': 'passed', 'execution_command': [sys.executable, *sys.argv], 'human_validation': 'not_performed', 'final_audit': 'pending'})
        dump(out / 'execution_report.json', report)
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    except Exception as exc:
        report = {'status': 'needs_revision', 'error': str(exc), 'execution_command': [sys.executable, *sys.argv], 'human_validation': 'not_performed', 'final_audit': 'pending'}
        dump(out / 'execution_report.json', report)
        print(json.dumps(report, ensure_ascii=False), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
