"""Independent annual scan and source-header/calendar check.
Run: python independent_check.py /directory/containing/artifacts_and_responses
Does not import reference.py. Reads sources; makes no network requests.
The pool supplies identity/evidence locators, never publication-date inputs.
Not executed by the source explorer.
"""
import csv
import json
import re
import sys
from pathlib import Path


MONTHS = {name: number for number, name in enumerate(
    ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
     'Sep', 'Oct', 'Nov', 'Dec'], 1)}
COLUMNS = ['cve', 'repository_advisory', 'repository_published',
           'catalogue_published', 'delay_days']


def ordinal(iso):
    year, month, day = map(int, iso.split('-'))
    adjustment = (14 - month) // 12
    y = year + 4800 - adjustment
    m = month + 12 * adjustment - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def output_texts(value):
    pending = [value]
    result = []
    while pending:
        item = pending.pop()
        if isinstance(item, str):
            try:
                decoded = json.loads(item)
            except ValueError:
                result.append(item)
            else:
                pending.append(decoded)
        elif isinstance(item, list):
            pending.extend(item)
        elif isinstance(item, dict):
            pending.extend(v for k, v in item.items()
                           if k in {'output', 'text', 'value', 'content'})
    return result


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    annual_text = (root / 'd0011.response').read_text(encoding='utf-8-sig')
    decoder = json.JSONDecoder()
    previous_end = 0
    identities = set()
    day_count = 0
    selected = {}
    for match in re.finditer(r'"cve"\s*:\s*', annual_text):
        if match.start() < previous_end:
            continue
        record, previous_end = decoder.raw_decode(annual_text, match.end())
        identifier = record['id']
        assert re.fullmatch(r'CVE-2023-\d+', identifier)
        assert identifier not in identities
        identities.add(identifier)
        value = record['published']
        # The saved NVD timestamps are UTC with no offset suffix.
        # Accept explicit UTC too, but never silently slice a nonzero offset.
        assert re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)?', value)
        if value[:10] == '2023-12-13':
            day_count += 1
            if record['sourceIdentifier'] == 'security-advisories@github.com':
                selected[identifier] = record
    declared = int(re.search(r'"totalResults"\s*:\s*(\d+)', annual_text)[1])
    assert len(identities) == declared == 31404
    assert day_count == 150 and len(selected) == 15
    del annual_text
    log = load(root / 'd0010.txt')
    texts = [text for entry in log for text in output_texts(entry['output'])]
    corpus = '\n'.join(texts)
    pool = load(root / 'candidate_pool.json')['rows']
    assert len(pool) == len({r['cve'] for r in pool}) == len(selected)
    assert {r['cve'] for r in pool} == set(selected)
    computed = []
    all_delays = {}
    for locator in pool:
        identifier = locator['cve']
        record = selected[identifier]
        assert record['published'] == locator['nvd_published']
        references = {r['url'] for r in record['references']}
        advisory = locator['repository_advisory']
        repository_url = locator['repository_url']
        assert repository_url.endswith('/' + advisory)
        assert repository_url in corpus
        if 'issue' in locator:
            assert locator['disclosure_url'] in references
            code_name = locator['code_reference_filename']
            assert any(u.split('#')[0].rsplit('/', 1)[-1] == code_name
                       for u in references if '/blob/' in u)
            issue = locator['issue']
            assert any('### Issue' in line and code_name in line and issue in line
                       for line in corpus.splitlines())
            # A repository page title explicitly naming the same issue
            # connects the locator to issue-level evidence, not package name.
            assert any(repository_url in line and issue in line
                       for line in corpus.splitlines())
        else:
            assert repository_url in references
        pattern = (r'published ' + re.escape(advisory)
                   + r' ([A-Z][a-z]{2}) (\d{1,2}), (\d{4})')
        dates = {f'{int(y):04d}-{MONTHS[m]:02d}-{int(d):02d}'
                 for m, d, y in re.findall(pattern, corpus)}
        assert len(dates) == 1, (identifier, dates)
        repository_date = dates.pop()
        catalogue_date = record['published'][:10]
        delay = ordinal(catalogue_date) - ordinal(repository_date)
        all_delays[identifier] = delay
        assert repository_date == locator['repository_published']
        assert delay == locator['delay_days']
        assert (delay > 0) == locator['included']
        if delay > 0:
            computed.append(dict(zip(COLUMNS, [identifier, advisory, repository_date,
                                               catalogue_date, str(delay)])))
    computed.sort(key=lambda r: r['cve'])
    with (root / 'oracle.psv').open(encoding='utf-8', newline='') as handle:
        expected = list(csv.DictReader(handle, delimiter='|'))
    assert computed == expected, {'computed': computed, 'oracle': expected}
    # Preserve the conflicting timeline as a separate source field and
    # check its alternative arithmetic without substituting it in answers.
    assert any('2023-11-01:' in line and 'Advisory Published' in line
               for line in corpus.splitlines())
    assert ordinal('2023-12-13') - ordinal('2023-11-01') == 42
    assert ordinal('2023-12-13') - ordinal('2023-10-29') == 45
    assert ordinal('2023-12-13') - ordinal('2023-10-13') == 61
    assert sum(value == 0 for value in all_delays.values()) == 9
    print(json.dumps({
        'annual_unique': len(identities), 'publication_day': day_count,
        'cohort': len(selected), 'qualifying': len(computed),
        'source_derived_delays': dict(sorted(all_delays.items())),
        'audiobookshelf_timeline_alternative_days': 42,
        'oracle_matches': True,
        'qualification': 'Independent arithmetic/header and annual check; issue-link traversal is additionally reconstructed by reference.py.'
    }, indent=2))


if __name__ == '__main__':
    main()
