#!/usr/bin/env python3
"""Specific standard-library reference for scotus_joinder_001 r01.
Reads controller captures and source-supported annotations, never oracle.psv.
Writes answer.psv and compact provenance/check files only after validation.
"""
import argparse
import datetime
import json
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

JUSTICES = {x.casefold(): x for x in (
    'Roberts Thomas Alito Sotomayor Kagan Gorsuch Kavanaugh Barrett Jackson'
).split()}
AUTHOR_CODES = dict(zip(
    ['R', 'T', 'A', 'SS', 'EK', 'NG', 'BK', 'AB', 'KJ'],
    ['Roberts', 'Thomas', 'Alito', 'Sotomayor', 'Kagan', 'Gorsuch',
     'Kavanaugh', 'Barrett', 'Jackson']))
COLUMNS = ['docket', 'min_justices', 'max_justices']


def require(ok, message):
    if not ok:
        raise ValueError(message)


def normalize(s, collapse=True):
    s = unicodedata.normalize('NFKC', s).replace('\r\n', '\n')
    # Delete only extraction word-break markers and hyphens at line wraps.
    # Do not repair missing letters (for example, extracted 'fled').
    s = re.sub(r'(?<=\w)[\x02\u00ad]\s*(?=\w)', '', s)
    s = re.sub(r'(?<=\w)-[ \t]*\n[ \t]*(?=\w)', '', s)
    s = s.translate(str.maketrans({'\u2018': "'", '\u2019': "'",
                                  '\u2013': '-', '\u2011': '-',
                                  '\u2010': '-'}))
    return re.sub(r'\s+', ' ', s).strip() if collapse else s


def compact(s):
    return re.sub(r'\s+', '', normalize(s)).casefold()


def read_capture(root, path, expected):
    data = (root / path).read_bytes()
    require(len(data) == expected, 'Capture size mismatch: ' + path)
    return data


def quote_match(base, quote, label):
    pattern = r'\s+'.join(re.escape(x) for x in normalize(quote).split())
    matches = list(re.finditer(pattern, base, re.I))
    require(len(matches) == 1, 'Missing or nonunique source anchor: ' + label)
    return matches[0]


class TermTable(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.cells = None
        self.cell = None
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.cells, self.links = [], []
        elif tag in ('td', 'th') and self.cells is not None:
            self.cell = []
        elif tag == 'a' and self.cells is not None:
            href = dict(attrs).get('href', '')
            if href:
                self.links.append(href)
        elif tag == 'br' and self.cell is not None:
            self.cell.append(' ')

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None:
            self.cells.append(normalize(''.join(self.cell)))
            self.cell = None
        elif tag == 'tr' and self.cells is not None:
            self.rows.append((self.cells, self.links))
            self.cells, self.cell = None, None


def inventory(html, term):
    require('Opinions of the Court' in html and '2022' in html,
            'Wrong term-table identity')
    parser = TermTable()
    parser.feed(html)
    parser.close()
    records = []
    date_re = r'\d{1,2}/\d{1,2}/\d{2}'
    for cells, links in parser.rows:
        if not any(re.fullmatch(date_re, c) for c in cells):
            continue
        require(len(cells) == 6 and re.fullmatch(date_re, cells[1])
                and cells[0].isdigit(), 'Malformed dated table row: ' + repr(cells))
        date = datetime.datetime.strptime(cells[1], '%m/%d/%y').date().isoformat()
        pdfs = sorted({urljoin(term['url'], x) for x in links
                       if re.search(r'/opinions/22pdf/[^?#]+\.pdf(?:[?#].*)?$', x, re.I)})
        records.append(dict(r=int(cells[0]), date=date, docket=cells[2],
                            name=cells[3], author_code=cells[4],
                            citation=cells[5], pdf_urls=pdfs))
    require(len(records) == term['dated_records'], 'Incomplete dated universe')
    require(sorted(x['r'] for x in records) == list(range(1, term['dated_records'] + 1)),
            'Missing or duplicate release sequence in complete table')
    return records


def names(text):
    text = re.sub(r'\b(?:C\.\s*J\.|JJ\.|J\.)', '', text, flags=re.I)
    tokens = [x.strip() for x in re.split(r',|\band\b', text, flags=re.I) if x.strip()]
    require(all(x.casefold() in JUSTICES for x in tokens), 'Unrecognized named joiner')
    result = [JUSTICES[x.casefold()] for x in tokens]
    require(len(result) == len(set(result)), 'Duplicate name in joinder declaration')
    return result


def parts(text):
    result = [x.strip().upper() for x in re.split(r',|\band\b', text, flags=re.I) if x.strip()]
    require(result and all(re.fullmatch(r'[IVX]+(?:-[A-Z])?', x) for x in result),
            'Unresolved formal part scope')
    require(len(set(result)) == len(result), 'Duplicate formal part scope')
    return result


def parse_groups(header):
    ordinary = re.fullmatch(
        r'(\w+), (?:C\. J\.|J\.), delivered the opinion of the Court, in which (.*?) joined\.',
        header, re.I)
    if ordinary:
        return ordinary[1], [{'parts': ['ALL'], 'joiners': names(ordinary[2])}]
    divided = re.fullmatch(
        r'(\w+), J\., announced the judgment of the Court, delivered the opinion of the Court '
        r'with respect to Parts (.*?), in which (.*?) joined, and an opinion with respect to '
        r'Parts (.*?), in which (.*?) joined\.', header, re.I)
    require(divided is not None, 'Unresolved lead-opinion attribution')
    return divided[1], [
        {'parts': parts(divided[2]), 'joiners': names(divided[3])},
        {'parts': parts(divided[4]), 'joiners': names(divided[5])}]


def canonical_groups(groups):
    return sorted((tuple(sorted(g['parts'])), tuple(sorted(g['joiners']))) for g in groups)


def verify_case(source_dir, record, annotation, doc):
    docket = record['docket']
    require(record['pdf_urls'] == [doc['url']], docket + ': discovered PDF link mismatch')
    for key, value in annotation['table'].items():
        actual = record[key]
        require(actual == value if isinstance(value, int) else compact(actual) == compact(value),
                docket + ': table identity mismatch: ' + key)
    require(AUTHOR_CODES.get(record['author_code']) == annotation['author'],
            docket + ': author-code mismatch')
    pdf = read_capture(source_dir, doc['path'], doc['bytes'])
    require(pdf.startswith(b'%PDF-') and b'%%EOF' in pdf[-1024:],
            docket + ': invalid PDF framing')
    raw = read_capture(source_dir, doc['text_path'], doc['text_bytes']).decode('utf-8')
    base = normalize(raw, collapse=False)
    flat = normalize(base)
    cover = compact(flat[:2000])
    for token in ['PRELIMINARY PRINT', 'Volume 600 U. S. Part 1',
                  'Page Proof Pending Publication', 'June 27, 2023',
                  'Pages ' + str(doc['first_printed_page']) + '-' + str(doc['last_printed_page'])]:
        require(compact(token) in cover, docket + ': preliminary-print version mismatch')
    for token in [annotation['identity_title'], 'No. ' + docket,
                  'Decided June 27, 2023', record['citation'] + ' (2023)']:
        require(compact(token) in compact(flat), docket + ': text identity mismatch: ' + token)
    pages = None
    if '\f' in raw:
        pages = raw.split('\f')
        if not pages[-1].strip():
            pages.pop()
        require(len(pages) == doc['pdf_pages'], docket + ': extracted page count mismatch')
    hits, evidence = {}, []
    for key, anchor in annotation['anchors'].items():
        hit = quote_match(base, anchor['quote'], docket + '/' + key)
        hits[key] = hit
        if pages is not None:
            index = anchor['page'] - doc['first_printed_page'] + 1
            require(0 <= index < len(pages), docket + ': invalid page locator')
            require(normalize(anchor['quote']).casefold() in normalize(pages[index]).casefold(),
                    docket + ': anchor absent from declared printed page: ' + key)
        evidence.append({'anchor': key, 'source': doc['text_path'],
                         'url': doc['url'], 'printed_page': anchor['page'],
                         'normalized_offset': hit.start(),
                         'quote': normalize(hit.group())})
    require(hits['formal'].end() < hits['lead'].start() < hits['separate'].start(),
            docket + ': attribution/lead/separate ownership order mismatch')
    author, groups = parse_groups(normalize(hits['formal'].group()))
    require(author.casefold() == annotation['author'].casefold(), docket + ': lead author mismatch')
    author = annotation['author']
    require(re.match(r'(?:Chief )?Justice ' + re.escape(author) + r'\b',
                     normalize(hits['lead'].group()), re.I) is not None,
            docket + ': body author not confirmed')
    require(canonical_groups(groups) == canonical_groups(annotation['groups']),
            docket + ': parsed named groups differ from annotation')
    require(all(author not in g['joiners'] for g in groups), docket + ': author duplicated as joiner')
    units = annotation['units']
    require(units and len(units) == len(set(units)), docket + ': invalid scope partition')
    if units != ['ALL']:
        # In the divided lead writing, verify the actual body divisions, not syllabus headings.
        body = base[hits['lead'].end():hits['separate'].start()]
        headings = list(re.finditer(r'(?m)^[ \t]*(I|II|III|IV|V|VI|VII|VIII|IX|X)[ \t]*$', body))
        require([m[1] for m in headings] == ['I', 'II', 'III', 'IV'],
                docket + ': unresolved complete lead part inventory')
        third = body[headings[2].end():headings[3].start()]
        subheads = re.findall(r'(?m)^[ \t]*([A-Z])[ \t]*$', third)
        require(subheads == ['A', 'B'], docket + ': unresolved Part III subdivision inventory')
        derived_units = ['I', 'II'] + ['III-' + x for x in subheads] + ['IV']
        require(units == derived_units, docket + ': incomplete annotated part coverage')
    require(set().union(*(set(g['parts']) for g in groups)) == set(units),
            docket + ': missing or extraneous joinder scope')
    rosters = {unit: {author} for unit in units}
    for group in groups:
        for unit in group['parts']:
            rosters[unit].update(group['joiners'])
    for relation in annotation['relations']:
        opening = hits[relation['open']]
        statement = hits[relation['statement']]
        closing = hits[relation['close']]
        require(opening.start() <= statement.start() and statement.end() <= closing.start(),
                docket + ': separate declaration assigned to wrong owner')
        owner = relation['owner']
        require(normalize(opening.group()).casefold().startswith(('Justice ' + owner).casefold()),
                docket + ': separate author heading mismatch')
        if relation['effect'] == 'confirm':
            joined = {unit for unit, roster in rosters.items() if owner in roster}
            require(joined == set(relation['parts']), docket + ': confirmation conflicts with formal groups')
            text = normalize(statement.group())
            if relation['parts'] == ['ALL']:
                require(text.casefold() == "i join the court's opinion in full.",
                        docket + ': unrestricted confirmation missing')
            else:
                prefix = "I join the Court's opinion as stated in Parts "
                require(text.startswith(prefix) and set(parts(text[len(prefix):])) == joined,
                        docket + ': partial confirmation scope mismatch')
        elif relation['effect'] in ('separate_only', 'conclusion_only'):
            require(all(person not in roster for person in relation['excluded_from_lead']
                        for roster in rosters.values()), docket + ': separate support transferred to lead')
            if relation['effect'] == 'conclusion_only':
                require("join the court's conclusion" in normalize(statement.group()).casefold(),
                        docket + ': conclusion-only source mismatch')
        else:
            raise ValueError('Unknown annotation relation')
    counts = [len(roster) for roster in rosters.values()]
    require(all(count > 0 for count in counts), docket + ': empty named roster')
    result = {'docket': docket, 'min_justices': min(counts), 'max_justices': max(counts)}
    return result, {'docket': docket, 'author': author, 'groups': groups,
                    'scope_rosters': {k: sorted(v) for k, v in rosters.items()},
                    'anchors': evidence, 'relations_checked': annotation['relations'],
                    'capture_pair': {'pdf': doc['path'], 'text': doc['text_path'],
                                     'pdf_bytes': len(pdf), 'text_bytes': len(raw.encode('utf-8'))},
                    'page_locators': 'verified against extracted pages' if pages is not None
                                     else 'curated printed-page locators; source quotes verified globally'}


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def construct(source_dir, out_dir):
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / 'source_manifest.json').read_text(encoding='utf-8'))
    annotations = json.loads((root / 'annotations.json').read_text(encoding='utf-8'))
    rules = json.loads((root / 'rules.json').read_text(encoding='utf-8'))
    require(rules['columns'] == COLUMNS and rules['row_key'] == ['docket'], 'Output schema mismatch')
    term = manifest['term']
    html = read_capture(source_dir, term['path'], term['bytes']).decode('utf-8-sig')
    records = inventory(html, term)
    selected, ledger = [], []
    for record in records:
        if record['date'] != term['release_date']:
            reason, include = 'outside release date', False
        elif record['author_code'] == 'PC':
            reason, include = 'unsigned per curiam', False
        else:
            require(record['author_code'] in AUTHOR_CODES, 'Unresolved dated decision category')
            reason, include = 'dated signed decision', True
            selected.append(record)
        ledger.append({'r': record['r'], 'docket': record['docket'],
                       'date': record['date'], 'included': include, 'reason': reason})
    selected.sort(key=lambda x: (x['r'], x['docket']))
    cases = {x['docket']: x for x in annotations['cases']}
    require(len(cases) == len(annotations['cases']), 'Duplicate annotation identity')
    require(len({x['docket'] for x in selected}) == len(selected), 'Duplicate selected docket')
    require({x['docket'] for x in selected} == set(cases),
            'Selected universe and source annotations differ; do not omit unresolved cases')
    results, evidence = [], []
    for record in selected:
        annotation = cases[record['docket']]
        result, facts = verify_case(source_dir, record, annotation,
                                    manifest['documents'][annotation['source']])
        results.append(result)
        evidence.append(facts)
    answer = 'NONE\n' if not results else '|'.join(COLUMNS) + '\n' + ''.join(
        '|'.join(str(row[column]) for column in COLUMNS) + '\n' for row in results)
    write_json(out_dir / 'inventory.json', records)
    write_json(out_dir / 'inclusion_ledger.json', ledger)
    write_json(out_dir / 'evidence.json', evidence)
    checks = {'status': 'passed', 'dated_records': len(records),
              'selected_records': len(selected), 'verified_cases': len(evidence),
              'verified_named_groups': sum(len(x['groups']) for x in evidence),
              'unresolved': [], 'oracle_read': False,
              'pdf_validation': 'Supplied capture sizes and PDF framing; semantic identity/version from linked paired text.',
              'fresh_pdf_text_extraction': False}
    write_json(out_dir / 'execution_checks.json', checks)
    (out_dir / 'answer.psv').write_text(answer, encoding='utf-8')
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    # A failed rerun must not leave a previous answer looking current.
    for name in ['answer.psv', 'inventory.json', 'inclusion_ledger.json',
                 'evidence.json', 'execution_checks.json']:
        (args.out_dir / name).unlink(missing_ok=True)
    try:
        checks = construct(args.source_dir, args.out_dir)
    except (ValueError, OSError, KeyError, UnicodeError, IndexError) as error:
        write_json(args.out_dir / 'execution_checks.json',
                   {'status': 'failed', 'unresolved': [str(error)], 'answer_written': False})
        print('UNRESOLVED: ' + str(error), file=sys.stderr)
        return 1
    print(json.dumps({'status': checks['status'], 'rows': checks['verified_cases']}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
