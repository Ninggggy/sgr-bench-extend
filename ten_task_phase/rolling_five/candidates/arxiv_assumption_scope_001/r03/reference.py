#!/usr/bin/env python3
"""Validate the archived corpus and reproduce r03. Standard library only.
No network, solver invocation, scoring experiment, or proof verification.
"""
import argparse
import datetime as dt
import json
import re
import sys
import unicodedata
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path


class Page(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.meta = {}
        self.feed(raw)
        self.close()

    def handle_data(self, value):
        self.parts.append(value)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta':
            self.meta[a.get('name', a.get('property', '')).lower()] = a.get('content', '')

    @property
    def text(self):
        return ' '.join(self.parts)


def norm(s):
    # Source-anchor normalization only; this is NOT scorer normalization.
    s = s.replace('\u00ad', '').replace('¨', '')
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.translate(str.maketrans({'‐': '-', '‑': '-', '–': '-', '−': '-'}))
    return re.sub(r'\s+', ' ', s).strip().lower()


def js(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n'


def jsonl(rows):
    return ''.join(json.dumps(x, ensure_ascii=False, sort_keys=True) + '\n' for x in rows)


def construct(source_dir, base, checks):
    def require(ok, label):
        checks.append({'check': label, 'passed': bool(ok)})
        if not ok:
            raise ValueError(label)

    def hit(pattern, text, label):
        m = re.search(pattern, text, re.S)
        require(m is not None, label)
        return m

    ann = json.loads((base / 'annotations.json').read_text(encoding='utf-8'))
    rules = json.loads((base / 'rules.json').read_text(encoding='utf-8'))
    cg = json.loads((base / 'cg.json').read_text(encoding='utf-8'))
    go = json.loads((base / 'go.json').read_text(encoding='utf-8'))
    alignment = json.loads((base / 'pair_alignment.json').read_text(encoding='utf-8'))
    require(set(cg) == set(go) == {'instruction', 'output_format'}, 'public file keys')
    require(cg['output_format'] == go['output_format'], 'identical public output contract')
    require(cg['instruction'].startswith(go['instruction'] + '\n\n'), 'CG only appends procedure')
    for p in alignment['predicates']:
        for form, public in [('cg', cg), ('go', go)]:
            require(p[form + '_quote'] in public['instruction'] + '\n' + public['output_format'], p['id'] + '/' + form)

    raw = {}
    manifest = []
    for name, info in sorted(ann['sources'].items()):
        data = (source_dir / name).read_bytes()
        require(bool(data), 'nonempty source ' + name)
        raw[name] = data.decode('utf-8')
        manifest.append(dict(info, path=name, bytes=len(data)))
    for version in ann['versions']:
        name = version['version'] + '.pdf'
        path = source_dir / name
        if path.is_file():
            data = path.read_bytes()
            manifest.append({'path': name, 'kind': 'archived original PDF', 'url': ann['sources'][version['source']]['url'], 'bytes': len(data)})

    hp = Page(raw['history.html'])
    history_text = re.sub(r'\s+', ' ', hp.text)
    identity = hp.meta.get('citation_arxiv_id', '')
    if not identity:
        identity = hit(r'arXiv:\s*(\d{4}\.\d{4,5})(?:v\d+)?', history_text, 'history identity').group(1)
    identity = re.sub(r'v\d+$', '', identity.strip())
    require(identity == ann['paper_id'], 'official identity agrees with annotation')
    for term in ann['identity_terms']:
        require(norm(term) in norm(history_text), 'identity descriptor ' + term)

    start = hit(r'Submission\s+history', history_text, 'official history heading').end()
    tail = history_text[start:]
    stop = re.search(r'Full-text links:|Access Paper:', tail)
    if stop:
        tail = tail[:stop.start()]
    pattern = r'\[v(\d+)\]\s*([A-Za-z]{3},\s*\d{1,2}\s+[A-Za-z]{3}\s+\d{4}\s+\d{2}:\d{2}:\d{2}\s+UTC)'
    matches = list(re.finditer(pattern, tail))
    require(bool(matches), 'submission timestamps parsed')
    labels = re.findall(r'\[v(\d+)\]', tail)
    require(labels == [m.group(1) for m in matches], 'every history version has a parsed timestamp')
    require(len(set(labels)) == len(labels), 'unique official versions')
    cutoff = dt.date.fromisoformat(ann['snapshot_date'])
    universe = []
    history_evidence = {}
    for m in matches:
        timestamp = parsedate_to_datetime(m.group(2).replace('UTC', '+0000')).astimezone(dt.timezone.utc)
        v = 'v' + str(int(m.group(1)))
        universe.append({'paper_id': identity, 'version': v, 'version_number': int(m.group(1)), 'submitted_utc': timestamp.isoformat(), 'through_snapshot': timestamp.date() <= cutoff})
        history_evidence[v] = m.group(0)
    universe.sort(key=lambda x: x['version_number'])
    selected = [x for x in universe if x['through_snapshot']]
    require(selected[0]['submitted_utc'].startswith('2017-'), 'initial submission year')
    require([x['version_number'] for x in universe] == list(range(1, len(universe) + 1)), 'complete consecutive official history')
    require([x['submitted_utc'] for x in universe] == sorted(x['submitted_utc'] for x in universe), 'official version and timestamp order agree')
    annotations = {a['version']: a for a in ann['versions']}
    require(len(annotations) == len(ann['versions']), 'unique semantic annotations')
    require(set(annotations) == {x['version'] for x in selected}, 'annotations cover exactly the selected history')
    require(len(selected) == rules['output_contract']['expected_rows'], 'declared row count from history')

    rows, evidence, ledger = [], [], []
    nodes = [{'id': 'history', 'source': 'history.html'}, {'id': 'oracle', 'kind': 'ordered output'}]
    edges = []
    html_text = norm(Page(raw['v3.html']).text)
    for item in universe:
        ledger.append({'version': item['version'], 'included': item['through_snapshot'], 'reason': 'Official history version through snapshot' if item['through_snapshot'] else 'Submitted after snapshot', 'evidence_ref': 'history.html#Submission history'})
    for item in selected:
        v = item['version']
        a = annotations[v]
        source = a['source']
        text = norm(raw[source])
        hit(r'arxiv:\s*' + re.escape(identity) + r'\s*' + re.escape(v) + r'\b', text, v + ' PDF version identity')
        rel_start = hit(r'1\.\s*3\.\s*general position', text, v + ' section 1.3').start()
        rel = text[rel_start:rel_start + 1600]
        any_match = re.search(r'every collection of t columns of the block matrix m\s*[|∣]\s*n', rel)
        matched_match = re.search(r'every collection of t columns of m,?\s*together with the corresponding columns of n', rel)
        require(bool(any_match) != bool(matched_match), v + ' unique column-selection rule')
        selection = 'ANY_T' if any_match else 'MATCHED_T'
        selection_match = any_match or matched_match
        rank_match = hit(r'free and cofree rank\s*-\s*(2?\s*t)\s+submodule', rel, v + ' submodule rank')
        rank = re.sub(r'\s+', '', rank_match.group(1))

        main_start = hit(r'theorem\s+(\d+)\.\s+let\b', text, v + ' main theorem')
        main = text[main_start.start():main_start.start() + 1400]
        hit(r'log\s*-?\s*symplectic compact kahlerian poisson manifold', main, v + ' main scope')
        dimension = hit(r'2\s*n\s*(?:≥|>=)\s*(\d+)', main, v + ' dimension threshold')
        require(int(dimension.group(1)) == 4, v + ' public dimension threshold')
        hit(r'holomorphic poisson', text[:6000], v + ' holomorphic category')
        divisor_info = ann['scope']['divisor_definitions'][v]
        require(divisor_info['source'] == source, v + ' divisor definition source')
        divisor_definition = hit(
            r'(?:is said to be|is) log\s*-?\s*symplectic if\b.{0,1000}?\bis a (?P<divisor>(?:reduced )?divisor with \(local\) normal crossings)\b',
            text[:6000], v + ' divisor definition')
        divisor_wording = divisor_definition.group('divisor')
        require(divisor_wording == norm(divisor_info['quote']), v + ' version-specific divisor wording')
        # Lexical presence in this definition only; no inference about geometry.
        require(('reduced' in divisor_wording.split()) == divisor_info['reduced_explicit_in_definition'], v + ' explicit reduced wording')
        hit(r'locally trivial deformation', main, v + ' selected conclusion')
        basic = hit(r'assume.{0,160}?in\s+(\d+)\s*-\s*general position', main, v + ' basic named assumption')
        operative = basic.group(1) + '-general position'
        op_quote = basic.group(0)
        op_anchor = a['main_anchor']
        correction = re.search(r'theorem\s*\(\s*theorem\s+(\d+)\s+corrected\s*\)', text)
        require(bool(correction) == bool(a['correction_anchor']), v + ' correction annotation')
        if correction:
            require(correction.group(1) == main_start.group(1), v + ' correction targets main theorem')
            corrected = text[correction.start():correction.start() + 650]
            stronger = hit(r'additional hypothesis.{0,180}?in\s+(\d+)\s*-\s*very general position', corrected, v + ' corrected requirement')
            definition = hit(r'definition\s+11\.', text, v + ' stronger definition').start()
            def_text = text[definition:definition + 1800]
            inclusion = hit(r't\s*-\s*very general position if it is in\s*t\s*-\s*general position', def_text, v + ' stronger includes basic')
            hit(r'definition\s+11.*?very general position if it is in.*?general position', html_text, v + ' HTML definition cross-check')
            operative = stronger.group(1) + '-very general position'
            op_quote = stronger.group(0)
            op_anchor = a['correction_anchor']
            evidence.append({'key': v + '/named_condition_relation', 'source': source, 'anchor': 'Definition 11', 'matched_text': inclusion.group(0), 'crosscheck': 'v3.html#Definition 11', 'interpretation': ann['named_condition_relation']['meaning']})
        else:
            require(re.search(r'erratum|corrigendum', text) is None, v + ' no unhandled appended correction')
        row = {'version': v, 'column_selection': selection, 'free_cofree_rank': rank, 'operative_assumption': operative}
        require(all(row[k] == a[k] for k in rules['columns']), v + ' parsed fields agree with semantic annotation')
        rows.append(row)
        evidence.extend([
            {'key': v + '/version', 'source': 'history.html', 'anchor': 'Submission history', 'value': v, 'matched_text': history_evidence[v]},
            {'key': v + '/column_selection', 'source': source, 'anchor': a['relative_anchor'], 'value': selection, 'matched_text': selection_match.group(0)},
            {'key': v + '/free_cofree_rank', 'source': source, 'anchor': a['relative_anchor'], 'value': rank, 'matched_text': rank_match.group(0)},
            {'key': v + '/operative_assumption', 'source': source, 'anchor': op_anchor, 'value': operative, 'matched_text': op_quote},
            {'key': v + '/scope', 'source': source, 'anchor': 'p1; ' + a['main_anchor'], 'dimension_minimum': int(dimension.group(1)), 'meaning': ann['scope']['meaning'], 'divisor_definition_anchor': divisor_info['anchor'], 'divisor_wording': divisor_wording, 'matched_text': divisor_definition.group(0), 'reduced_explicit_in_definition': divisor_info['reduced_explicit_in_definition'], 'interpretation_boundary': ann['scope']['interpretation_boundary']}
        ])
        nodes.extend([{'id': v + '/text', 'source': source}, {'id': v + '/row', 'kind': 'validated fields'}])
        edges.extend([['history', v + '/text', 'select official historical document'], [v + '/text', v + '/row', 'definition and main statement; same-version correction takes precedence'], [v + '/row', 'oracle', 'ascending official version number']])
        if correction:
            nodes.append({'id': v + '/erratum', 'source': source, 'anchor': a['correction_anchor']})
            edges.extend([[v + '/text', v + '/erratum', 'appended correction'], [v + '/erratum', v + '/row', 'strongest named requirement; definition includes basic condition']])

    columns = rules['columns']
    require(columns == ['version', 'column_selection', 'free_cofree_rank', 'operative_assumption'], 'reference and scorer column agreement')
    require(rules['row_key'] == ['version'], 'reference and scorer key agreement')
    require(all(cell not in ('NONE', 'UNKNOWN', '') for row in rows for cell in row.values()), 'complete non-placeholder oracle')
    oracle = '|'.join(columns) + '\n' + ''.join('|'.join(row[c] for c in columns) + '\n' for row in rows)
    require(oracle == (base / 'oracle.psv').read_text(encoding='utf-8'), 'reproduced oracle equals supplied proposal')
    assets = []
    for name in ['candidate.json', 'annotations.json', 'rules.json', 'cg.json', 'go.json', 'pair_alignment.json', 'oracle.psv', 'reference.py']:
        data = (base / name).read_bytes()
        assets.append({'path': name, 'bytes': len(data)})
    symbol = '∉' in raw['v3.html'] or re.search(r'\\not\s*\\in', raw['v3.html']) is not None
    return {
        'oracle.psv': oracle,
        'candidate_universe.jsonl': jsonl(universe),
        'inclusion_ledger.jsonl': jsonl(ledger),
        'field_evidence.jsonl': jsonl(evidence),
        'source_manifest.json': js({'snapshot_date': ann['snapshot_date'], 'sources': manifest, 'construction_assets': assets, 'equation_13_nonmembership_present': symbol, 'equation_13_used_for_output': False}),
        'state_graph.json': js({'nodes': nodes, 'edges': edges, 'edge_columns': ['from', 'to', 'dependency'], 'scope': 'Source dependencies, not a solver trace'}),
        'preblind_checks.json': js({'status': 'passed', 'reference_executed': True, 'checks': checks, 'solver_tests': 'not_performed', 'scores': None, 'human_review': 'not_performed', 'independent_audit': 'not_performed'})
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    checks = []
    try:
        outputs = construct(args.source_dir, base, checks)
        # Preflight all destinations; never replace differing existing files.
        for name, content in outputs.items():
            path = args.out / name
            if path.exists() and path.read_bytes() != content.encode('utf-8'):
                raise FileExistsError('Refusing to replace differing file: ' + str(path))
        args.out.mkdir(parents=True, exist_ok=True)
        for name, content in outputs.items():
            path = args.out / name
            if not path.exists():
                path.write_bytes(content.encode('utf-8'))
    except Exception as exc:
        args.out.mkdir(parents=True, exist_ok=True)
        failure = args.out / 'preblind_checks.json'
        if not failure.exists():
            failure.write_text(js({'status': 'failed', 'reference_executed': True, 'checks': checks, 'error': str(exc), 'oracle_generated': False, 'solver_tests': 'not_performed'}), encoding='utf-8')
        print('Reference failed: ' + str(exc), file=sys.stderr)
        return 1
    print('Validated sources; reproduced oracle; generated six supporting files.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
