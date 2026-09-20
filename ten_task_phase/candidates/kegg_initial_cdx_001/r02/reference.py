#!/usr/bin/env python3
"""Reconstruct r02 from recovered registered sources; standard library only.
Usage: python reference.py SOURCE_DIRECTORY > computed.psv
Inputs: d0023.response; d0028 registered CSV; d0029 registered CSV.
The FDA CSV contains actual web-tool text responses, not PDF binaries.
This program was not executed by the explorer.
"""
import csv
import re
import sys
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

COLUMNS = ['drug', 'biomarker', 'reference_transcript', 'named_substitutions', 'additional_classes']
LABELS = {'truqap': 'cap', 'vanflyta': 'quiz', 'augtyro': 'repo', 'ojjaara': 'mome', 'fruzaqla': 'fruq', 'jaypirca': 'pirt'}


def locate(root, file_id, columns=None):
    paths = sorted(p for p in root.rglob(file_id + '*') if p.is_file())
    if columns:
        for p in paths:
            try:
                with p.open(encoding='utf-8-sig', newline='') as f:
                    rd = csv.DictReader(f)
                    if set(columns).issubset(rd.fieldnames or []):
                        return p
            except (UnicodeError, csv.Error):
                continue
        raise FileNotFoundError('Recover registered CSV ' + file_id)
    paths = [p for p in paths if p.name == file_id + '.response']
    if not paths:
        raise FileNotFoundError(file_id + '.response')
    return paths[0]


def read_csv(root, file_id, columns):
    with locate(root, file_id, columns).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def flat(s):
    s = re.sub(r'L\d+(?:@P[\d-]+)?:\s?', '', s)
    return ' '.join(s.replace('\x02', '').replace('\u00ad', '').split())


def require(s, *phrases):
    t = flat(s).casefold()
    for p in phrases:
        if flat(p).casefold() not in t:
            raise ValueError('Required source passage absent: ' + p)


class Approvals(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows, self.row, self.cell = [], None, None

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.row = []
        elif tag == 'td' and self.row is not None:
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag == 'td' and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split()))
            self.cell = None
        elif tag == 'tr' and self.row is not None:
            if len(self.row) == 9 and re.fullmatch(r'D\d{5}', self.row[3]):
                self.rows.append(self.row)
            self.row = None


def scope(root):
    parser = Approvals()
    parser.feed(locate(root, 'd0023').read_text(encoding='utf-8'))
    pool = [r for r in parser.rows if r[0].startswith('2023/') and re.search(r'\bL01E[A-Z0-9]*\b', r[4])]
    metadata = {}
    for r in read_csv(root, 'd0028', ['metadata']):
        m = re.search(r'^ENTRY\s+(D\d{5})\b', r['metadata'], re.M)
        if m:
            metadata[m.group(1)] = r['metadata']
    # d0028 is the preserved complete six-record metadata derivation from d0024.
    # The full approval HTML independently determines which records are needed.
    for r in pool:
        code = re.search(r'\bL01E[A-Z0-9]*\b', r[4]).group()
        require(metadata[r[3]], r[5], 'ATC code: ' + code)
    by_brand = {r[6].casefold(): r for r in pool}
    if len(by_brand) != len(pool) or set(by_brand) != set(LABELS):
        raise ValueError('Scope cannot be covered by the preserved historical-label audit')
    return by_brand


def class_token(s):
    return re.sub(r'[\s-]+', '_', s.strip().lower())


def additional_classes(body):
    classes = []
    m = re.search(r'\bAny ([a-z ,]+?) alteration\b', body)
    if m:
        classes.extend(class_token(x) for x in re.split(r',\s*(?:or\s+)?|\s+or\s+', m.group(1)) if x)
    m = re.search(r'\b(Homozygous deletion) \(HD\) represents', body)
    if m:
        classes.append(class_token(m.group(1)))
    m = re.search(r'\b(Rearrangement) \(RE\)', body)
    if m:
        classes.append(class_token(m.group(1)))
    if classes:
        # These checks preserve the source interpretation behind the class projection.
        require(body, 'start codon', 'M1?', 'included in this category',
                'one or more exons', 'both alleles', 'regardless of transcript',
                'disrupts protein function', 'duplications of only part of the gene',
                'another gene or intergenic region')
    return sorted(set(classes))


def exclusion_evidence(web):
    # Semantic dispositions were adjudicated from the original indications.
    # They are not inferred from a failed search or a missing current-table row.
    require(web['repo_label'], 'ROS1 rearrangement', 'not currently available')
    require(web['mome_label'], 'intermediate or high-risk myelofibrosis', 'in adults with anemia')
    require(web['pirt_label'], 'relapsed or refractory mantle cell lymphoma',
            'at least two lines of systemic therapy', 'including a BTK inhibitor')
    require(web['fruq_label'], 'previously treated', 'RAS', 'anti-EGFR')


def decision_matches(row, pma):
    match = re.search(r'Decision Date (\d{2}/\d{2}/\d{4})', pma)
    if not match:
        raise ValueError('PMA decision date absent')
    if datetime.strptime(match.group(1), '%m/%d/%Y').date() != datetime.strptime(row[0], '%Y/%m/%d').date():
        raise ValueError('Historical diagnostic decision does not match initial drug approval')
    require(pma, row[6])


def compute(root):
    pool = scope(root)
    web = {r['source_key']: flat(r['web_response']) for r in read_csv(root, 'd0029', ['source_key', 'source_url', 'web_response'])}
    for brand, prefix in LABELS.items():
        require(web[prefix + '_label'], brand)
    exclusion_evidence(web)
    cap, quiz = pool['truqap'], pool['vanflyta']
    decision_matches(cap, web['cap_pma'])
    decision_matches(quiz, web['quiz_pma'])
    require(web['cap_pma'], 'breast cancer', 'fulvestrant', 'PIK3CA/AKT1/PTEN')
    require(web['cap_label'], 'HR-positive, HER2-negative', 'PIK3CA/AKT1/PTEN', 'fulvestrant')
    text = web['cap_ssed']
    table = text.split('Table 9. Biomarker definition', 1)[1].split('VI. ALTERNATIVE PRACTICES', 1)[0]
    entries = list(re.finditer(r'\b([A-Z][A-Z0-9]+)\s*\((NM_\d+(?:\.\d+)?)\)', table))
    if not entries:
        raise ValueError('No transcript-defined source rows recovered')
    output = []
    for i, m in enumerate(entries):
        end = entries[i + 1].start() if i + 1 < len(entries) else len(table)
        body = table[m.end():end]
        named_region = body.split('Any ', 1)[0]
        named = sorted(set(re.findall(r'\b[A-Z]\d+[A-Z]\b', named_region)))
        classes = additional_classes(body)
        output.append([cap[5], m.group(1), m.group(2) if named else 'NONE',
                       ';'.join(named) or 'NONE', ';'.join(classes) or 'NONE'])
    # Select the drug-specific ITD claim, not the assay's preceding ITD/TKD detection scope.
    q = web['quiz_pma']
    claim = re.search(r'patients with ([A-Z0-9]+)-([A-Z]+)\+ AML for whom VANFLYTA', q)
    if not claim:
        raise ValueError('Drug-specific quizartinib companion claim absent')
    gene, abbreviation = claim.groups()
    label_class = re.search(r'\b' + re.escape(gene) + r' ([a-z ]+?) \(' + re.escape(abbreviation) + r'\)-positive', web['quiz_label'])
    if not label_class:
        raise ValueError('Original drug label does not expand the companion class')
    require(q, 'tyrosine kinase domain (TKD)', 'D835', 'I836')
    require(web['quiz_label'], gene + '-' + abbreviation + ' mutation', 'cytarabine',
            'anthracycline', 'not indicated as maintenance monotherapy following allogeneic')
    # This claim defines an open-ended class and enumerates no named substitutions.
    output.append([quiz[5], gene, 'NONE', 'NONE', class_token(label_class.group(1))])
    return sorted(output, key=lambda r: (r[0], r[1]))


if __name__ == '__main__':
    writer = csv.writer(sys.stdout, delimiter='|', lineterminator='\n')
    writer.writerow(COLUMNS)
    writer.writerows(compute(Path(sys.argv[1])))
