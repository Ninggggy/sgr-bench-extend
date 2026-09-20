"""Source-extracting reference for the repository-displayed-date candidate.
Run: python reference.py /directory/containing/artifacts_and_responses
Standard library only; no network or source writes.
Not executed by the source explorer. An equivalent saved-source extraction
was checked in JavaScript; controller execution of this Python is separate.
"""
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

COLUMNS = ['cve', 'repository_advisory', 'repository_published',
           'catalogue_published', 'delay_days']
DAY = '2023-12-13'
SOURCE = 'security-advisories@github.com'
REPOSITORY = re.compile(r'^https://github\.com/[^/]+/[^/]+/security/advisories/GHSA-')
HEADER = re.compile(
    r'cite(turn\d+view\d+) \[wordlim: \d+\][^\n]*?'
    r'Source: (open|click|find)\((\{[^\n]*?\})\);[^\n]*')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def strings(value):
    """Decode nested tool envelopes; never use the saved query code."""
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except (ValueError, TypeError):
            yield value
        else:
            yield from strings(decoded)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            if key in ('output', 'text', 'value', 'content'):
                yield from strings(item)


def browser_documents(log):
    documents = []
    for entry_number, entry in enumerate(log):
        for text in strings(entry['output']):
            matches = list(HEADER.finditer(text))
            for index, match in enumerate(matches):
                prior = text[:match.start()].rstrip().split('\n')
                end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
                documents.append({
                    'entry': entry_number, 'ref': match[1], 'operation': match[2],
                    'args': json.loads(match[3]),
                    'title': prior[-1] if prior else '',
                    'body': text[match.start():end],
                })
    urls = {}
    for doc in documents:
        title_url = re.search(r'\((https://[^()]+)\)$', doc['title'])
        if title_url:
            urls[doc['ref']] = title_url[1]
        ref = doc['args']['ref_id']
        if doc['operation'] == 'open' and ref.startswith('https://'):
            urls[doc['ref']] = ref
    # Finds and line-window opens refer to the same source. Clicks refer to
    # a different source, whose actual destination is in its saved title.
    for _ in range(len(documents)):
        changed = False
        for doc in documents:
            if doc['operation'] == 'click':
                continue
            parent = doc['args']['ref_id']
            child = doc['ref']
            if parent in urls and child not in urls:
                urls[child] = urls[parent]
                changed = True
            if child in urls and not parent.startswith('http') and parent not in urls:
                urls[parent] = urls[child]
                changed = True
        if not changed:
            break
    by_url = defaultdict(list)
    for doc in documents:
        if doc['ref'] in urls:
            by_url[urls[doc['ref']]].append(doc)
    return documents, urls, by_url


def body_for(by_url, url):
    return '\n'.join(doc['body'] for doc in by_url[url])


def one(values, label):
    values = set(values)
    if len(values) != 1:
        raise AssertionError(f'{label}: expected one observed value, got {values}')
    return next(iter(values))


def utc_day(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).date()


def source_rows(records, documents, urls, by_url):
    results = []
    for record in sorted(records, key=lambda r: r['id']):
        identifier = record['id']
        references = {r['url'] for r in record['references']}
        repository_urls = {u for u in references if REPOSITORY.match(u)}
        issue = None
        if not repository_urls:
            disclosure = one((u for u in references if u.startswith(
                'https://securitylab.github.com/advisories/')), identifier + ' disclosure')
            disclosure_body = body_for(by_url, disclosure)
            names = {u.split('#')[0].rsplit('/', 1)[-1]
                     for u in references if '/blob/' in u}
            issue_lines = [line for line in disclosure_body.splitlines()
                           if '### Issue' in line and any(name in line for name in names)]
            issue = one((value for line in issue_lines
                         for value in re.findall(r'GHSL-\d+-\d+', line)),
                        identifier + ' issue')
            # Recover an actually followed publication link, not a guessed
            # URL constructed from package identity or a CNA GHSA value.
            for doc in documents:
                if doc['operation'] != 'click':
                    continue
                if urls.get(doc['args']['ref_id']) != disclosure:
                    continue
                link_number = doc['args']['id']
                marker = f'cite{link_number}†'
                assert any(marker in line and 'Advisory' in line
                           for line in disclosure_body.splitlines()), identifier
                target = urls.get(doc['ref'])
                if target and REPOSITORY.match(target):
                    repository_urls.add(target)
        repository_url = one(repository_urls, identifier + ' repository URL')
        repository_body = body_for(by_url, repository_url)
        advisory = repository_url.rsplit('/', 1)[-1]
        if issue:
            assert issue in repository_body, (identifier, 'issue absent from destination')
        else:
            assert re.search(r'\b' + re.escape(identifier) + r'\b', repository_body), identifier
        displayed = one(re.findall(
            r'published ' + re.escape(advisory) + r' ([A-Z][a-z]{2} \d{1,2}, \d{4})',
            repository_body), identifier + ' displayed publication date')
        published = datetime.strptime(displayed, '%b %d, %Y').date()
        catalogue = utc_day(record['published'])
        numeric = identifier.split('-')[2]
        cve_url = ('https://raw.githubusercontent.com/CVEProject/cvelistV5/main/'
                   f'cves/2023/{numeric[:2]}xxx/{identifier}.json')
        cve_body = body_for(by_url, cve_url)
        assert one(re.findall(r'"state":\s*"([^"]+)"', cve_body), identifier) == 'PUBLISHED'
        assert one(re.findall(r'"assignerShortName":\s*"([^"]+)"', cve_body), identifier) == 'GitHub_M'
        cna_advisory = one(re.findall(r'"advisory":\s*"([^"]+)"', cve_body), identifier)
        results.append({
            'cve': identifier, 'repository_advisory': advisory,
            'repository_published': published.isoformat(),
            'catalogue_published': catalogue.isoformat(),
            'delay_days': str((catalogue - published).days),
            'repository_url': repository_url, 'issue': issue,
            'cna_source_advisory': cna_advisory,
        })
    return results


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    annual = read_json(root / 'd0011.response')
    records = [item['cve'] for item in annual['vulnerabilities']]
    assert annual['startIndex'] == 0
    assert len(records) == annual['totalResults'] == annual['resultsPerPage']
    assert len({r['id'] for r in records}) == len(records) == 31404
    assert all(r['id'].startswith('CVE-2023-') for r in records)
    day_records = [r for r in records if utc_day(r['published']).isoformat() == DAY]
    cohort = [r for r in day_records if r['sourceIdentifier'] == SOURCE]
    assert len(day_records) == 150 and len(cohort) == 15
    documents, urls, by_url = browser_documents(read_json(root / 'd0010.txt'))
    observed = source_rows(cohort, documents, urls, by_url)
    answer = [{key: row[key] for key in COLUMNS}
              for row in observed if int(row['delay_days']) > 0]
    with (root / 'oracle.psv').open(encoding='utf-8', newline='') as handle:
        expected = list(csv.DictReader(handle, delimiter='|'))
    assert answer == expected, {'computed': answer, 'oracle': expected}
    pool = read_json(root / 'candidate_pool.json')['rows']
    assert {r['cve'] for r in pool} == {r['cve'] for r in observed}
    observed_by_id = {r['cve']: r for r in observed}
    for row in pool:
        actual = observed_by_id[row['cve']]
        for key in ('repository_advisory', 'repository_published',
                    'repository_url', 'cna_source_advisory'):
            assert row[key] == actual[key], (row['cve'], key)
        assert row.get('issue') == actual['issue']
        assert row['delay_days'] == int(actual['delay_days'])
        assert row['included'] == (int(actual['delay_days']) > 0)
    cg, go = read_json(root / 'CG.json'), read_json(root / 'GO.json')
    assert set(cg) == set(go) == {'instruction', 'output_format'}
    assert cg['instruction'].startswith(go['instruction'] + '\n\nSearch guidance:')
    assert cg['output_format'] == go['output_format']
    rules = read_json(root / 'rules.json')
    assert rules['columns'] == COLUMNS and rules['row_key'] == ['cve']
    assert set(rules['fields']) == set(COLUMNS)
    writer = csv.DictWriter(sys.stdout, fieldnames=COLUMNS, delimiter='|', lineterminator='\n')
    writer.writeheader()
    writer.writerows(answer)
    print(json.dumps({'annual': len(records), 'day': len(day_records),
                      'cohort': len(cohort), 'earlier': len(answer),
                      'same_day': sum(r['delay_days'] == '0' for r in observed)}),
          file=sys.stderr)


if __name__ == '__main__':
    main()
