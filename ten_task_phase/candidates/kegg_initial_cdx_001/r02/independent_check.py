#!/usr/bin/env python3
"""Independent r02 reconstruction and source cross-check; standard library only.
Usage: python independent_check.py SOURCE_DIRECTORY [oracle.psv] > independent.psv
Uses line-oriented Table 9 parsing, physician-label named lists, and the original
quizartinib drug label. Does not import reference.py or use oracle values to derive rows.
No Python execution by the explorer is claimed.
"""
import csv
import re
import sys
from datetime import datetime
from html import unescape
from pathlib import Path

COLUMNS = ['drug', 'biomarker', 'reference_transcript', 'named_substitutions', 'additional_classes']


def recovered_csv(root, file_id, required):
    for p in sorted(root.rglob(file_id + '*')):
        if not p.is_file():
            continue
        try:
            with p.open(encoding='utf-8-sig', newline='') as f:
                rd = csv.DictReader(f)
                if set(required).issubset(rd.fieldnames or []):
                    return list(rd)
        except (UnicodeError, csv.Error):
            pass
    raise FileNotFoundError(file_id + ' registered CSV')


def lines(s):
    result = []
    for line in s.splitlines():
        match = re.match(r'^L\d+(?:@P[\d-]+)?:\s?(.*)$', line)
        if match:
            result.append(match.group(1).replace('\x02', '').strip())
    return result


def plain(s):
    return ' '.join(re.sub(r'L\d+(?:@P[\d-]+)?:\s?', '', s).replace('\x02', '').split())


def substitutions(s):
    return sorted({t for t in re.split(r'[^A-Za-z0-9_]+', s) if re.fullmatch(r'[A-Z][0-9]+[A-Z]', t)})


def token(s):
    return '_'.join(s.lower().replace('-', ' ').split())


def compute(root):
    html_files = sorted(root.rglob('d0023.response'))
    if not html_files:
        raise FileNotFoundError('d0023.response')
    html = html_files[0].read_text(encoding='utf-8')
    approval_rows = []
    for block in re.findall(r'<tr\b[^>]*>(.*?)</tr>', html, re.S | re.I):
        cells = [' '.join(unescape(re.sub(r'<[^>]*>', '', c)).split()) for c in re.findall(r'<td\b[^>]*>(.*?)</td>', block, re.S | re.I)]
        if len(cells) == 9 and re.fullmatch(r'D\d{5}', cells[3]):
            approval_rows.append(cells)
    pool = [r for r in approval_rows if r[0].split('/')[0] == '2023' and re.search(r'\bL01E[A-Z0-9]+\b', r[4])]
    metadata = recovered_csv(root, 'd0028', ['metadata'])
    by_id = {re.search(r'ENTRY\s+(D\d{5})', r['metadata']).group(1): r['metadata'] for r in metadata}
    for row in pool:
        codes = re.findall(r'\bL01E[A-Z0-9]+\b', row[4])
        assert all(code in by_id[row[3]] for code in codes)
        assert row[5].casefold() in by_id[row[3]].casefold()
    brands = {r[6].lower(): r for r in pool}
    label_map = {'truqap': 'cap', 'vanflyta': 'quiz', 'augtyro': 'repo', 'ojjaara': 'mome', 'fruzaqla': 'fruq', 'jaypirca': 'pirt'}
    assert set(brands) == set(label_map) and len(brands) == len(pool)
    web = {r['source_key']: r['web_response'] for r in recovered_csv(root, 'd0029', ['source_key', 'web_response'])}
    texts = {k: plain(v) for k, v in web.items()}
    for brand, prefix in label_map.items():
        assert brand in texts[prefix + '_label'].lower()
    # Explicit source-based exclusion adjudications, independently checked for presence.
    assert 'not currently available' in texts['repo_label']
    assert 'ROS1 rearrangement' in texts['repo_label']
    assert 'intermediate or high-risk myelofibrosis' in texts['mome_label']
    assert 'in adults with anemia' in texts['mome_label']
    assert 'relapsed or refractory mantle cell lymphoma' in texts['pirt_label']
    assert 'including a BTK inhibitor' in texts['pirt_label']
    assert 'previously treated' in texts['fruq_label'] and 'anti-EGFR' in texts['fruq_label'] and 'RAS' in texts['fruq_label']
    for brand, prefix in [('truqap', 'cap'), ('vanflyta', 'quiz')]:
        date = re.search(r'Decision Date (\d{2}/\d{2}/\d{4})', texts[prefix + '_pma']).group(1)
        assert datetime.strptime(date, '%m/%d/%Y').date() == datetime.strptime(brands[brand][0], '%Y/%m/%d').date()
    source_lines = lines(web['cap_ssed'])
    start = next(i for i, s in enumerate(source_lines) if s.startswith('Table 9. Biomarker definition'))
    end = next(i for i in range(start + 1, len(source_lines)) if source_lines[i].startswith('VI. ALTERNATIVE PRACTICES'))
    table = source_lines[start:end]
    heads = [i for i in range(len(table) - 1) if re.fullmatch(r'[A-Z][A-Z0-9]+', table[i]) and re.fullmatch(r'\(NM_[0-9]+(?:\.[0-9]+)?\)', table[i + 1])]
    derived = {}
    for n, i in enumerate(heads):
        stop = heads[n + 1] if n + 1 < len(heads) else len(table)
        gene, transcript = table[i], table[i + 1][1:-1]
        body = table[i + 2:stop]
        cut = next((j for j, s in enumerate(body) if s.startswith('Any ')), len(body))
        named = substitutions(' '.join(body[:cut]))
        classes = []
        for s in body:
            if s.startswith('Any ') and s.endswith(' alteration'):
                phrase = s[len('Any '):-len(' alteration')]
                classes.extend(token(x) for x in phrase.replace(', or ', ',').replace(' or ', ',').split(','))
            elif '(HD) represents a deletion' in s:
                classes.append(token(s.split(' (HD)', 1)[0]))
            elif s == 'Rearrangement':
                classes.append(token(s))
        if classes:
            joined = ' '.join(body)
            for qualifier in ['start codon', 'M1?', 'included in this category', 'one or more exons', 'both alleles', 'regardless of transcript', 'disrupts protein function', 'duplications of only part of the gene', 'another gene or intergenic region']:
                assert qualifier in joined
        derived[gene] = [brands['truqap'][5], gene, transcript if named else 'NONE', ';'.join(named) or 'NONE', ';'.join(sorted(set(classes))) or 'NONE']
    # Independently extract the intended-use list, avoiding the adjacent alpelisib row.
    physician = texts['cap_device_label']
    intended_start = re.search(r'\bAKT1\s+', physician).start()
    intended = physician[intended_start:physician.index('and PTEN alterations', intended_start)]
    akt, pik = intended.split('PIK3CA', 1)
    physician_akt = substitutions(akt)
    physician_pik = substitutions(pik)
    assert derived['AKT1'][3].split(';') == physician_akt
    assert derived['PIK3CA'][3].split(';') == physician_pik
    # These observed counts are independent key-calculation checks, not output data.
    assert len(physician_akt) == 1 and len(physician_pik) == 19
    assert len(derived['PTEN'][3].split(';')) == 13
    # Derive the quizartinib class from the original drug indication, then corroborate PMA.
    q = texts['quiz_label']
    indication = q[q.index('VANFLYTA is indicated'):q.index('Limitations of Use')]
    match = re.search(r'\b([A-Z0-9]+) ([a-z ]+?) \(([A-Z]+)\)-positive', indication)
    assert match
    gene, class_name, abbreviation = match.groups()
    assert gene + '-' + abbreviation + '+ AML for whom VANFLYTA' in texts['quiz_pma']
    assert 'tyrosine kinase domain (TKD)' in texts['quiz_pma']
    assert 'not indicated as maintenance monotherapy following allogeneic' in q
    result = list(derived.values()) + [[brands['vanflyta'][5], gene, 'NONE', 'NONE', token(class_name)]]
    result.sort(key=lambda r: (r[0], r[1]))
    assert len({(r[0], r[1]) for r in result}) == len(result)
    print('Source checks: physician/SSED AKT1 and PIK3CA sets agree; PTEN named set and source qualifiers recovered; original quizartinib class agrees with PMA.', file=sys.stderr)
    return result


if __name__ == '__main__':
    result = compute(Path(sys.argv[1]))
    if len(sys.argv) > 2:
        with Path(sys.argv[2]).open(encoding='utf-8-sig', newline='') as f:
            oracle = list(csv.reader(f, delimiter='|'))
        assert oracle == [COLUMNS] + result, 'Independent reconstruction differs from oracle'
        print('Independent reconstruction equals supplied oracle.', file=sys.stderr)
    writer = csv.writer(sys.stdout, delimiter='|', lineterminator='\n')
    writer.writerow(COLUMNS)
    writer.writerows(result)
