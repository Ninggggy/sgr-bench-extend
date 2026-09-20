#!/usr/bin/env python3
"""Recompute the claim comparison from the supplied primary excerpts.

Source-specific semantic adapters are explicit below. They recognize printed
query formulas, theorem context, and quantifier structure; they do not verify
proofs. No expected row table or oracle.psv is read by this program.
"""
import argparse
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

COLUMNS = ['ARXIV_ID', 'VERSION', 'THEOREM', 'QUERY_MODEL', 'GAP_FORM', 'ITERATES']


def check(condition, message):
    if not condition:
        raise ValueError(message)


def clean(text):
    text = text.replace('\\u0002', '').replace('\u0002', '')
    return re.sub(r'[\x00-\x1f]', '', unicodedata.normalize('NFKC', text))


def compact(text):
    return re.sub(r'\s+', '', clean(text))


def identity_text(text):
    return ''.join(c for c in clean(text).casefold() if c.isalnum())


class Document:
    def __init__(self, name):
        self.name, self.lines, self.pages, self.used, self.files = name, {}, {}, {}, []

    def add(self, path):
        self.files.append(path.name)
        for raw in path.read_text(encoding='utf-8').splitlines():
            m = re.fullmatch(r'L(\d+)@P([\d-]+): ?(.*)', raw)
            if not m:
                continue
            n, page, text = int(m[1]), m[2], m[3]
            check(n not in self.lines or self.lines[n] == text,
                  f'Conflicting original line {self.name}:L{n}')
            self.lines[n], self.pages[n] = text, page

    def get(self, first, last=None):
        last = first if last is None else last
        result = []
        for n in range(first, last + 1):
            check(n in self.lines, f'Missing {self.name}:L{n}')
            self.used[n] = {'line': n, 'page': self.pages[n], 'text': self.lines[n]}
            result.append(self.lines[n])
        return '\n'.join(result)

    def need(self, n, fragment):
        text = self.get(n)
        check(fragment in clean(text), f'Changed anchor {self.name}:L{n}: {fragment}')
        return text

    def early(self):
        return '\n'.join(self.lines[n] for n in sorted(self.lines) if n <= 90)


def load_documents(directory):
    docs = {}
    for path in sorted(directory.glob('*.excerpt.txt')):
        m = re.match(r'^(\d{4}\.\d{4,5}v\d+).*\.excerpt\.txt$', path.name)
        if m:
            docs.setdefault(m[1], Document(m[1])).add(path)
    for name, doc in docs.items():
        check('arXiv:' + name in doc.early(), 'Missing document identity: ' + name)
    return docs


def load_history(path):
    text = path.read_text(encoding='utf-8')
    text = re.sub(r'cite[^†]*†([^]*)', r'\1', text)
    starts = list(re.finditer(r'(?m)^\[(\d{4}\.\d{4,5})\]', text))
    histories, announced = {}, {}
    for i, start in enumerate(starts):
        base = start[1]
        block = text[start.end():starts[i + 1].start() if i + 1 < len(starts) else len(text)]
        histories.setdefault(base, {})
        announced.setdefault(base, set()).update(re.findall(r'this version, (v\d+)', block))
        pattern = r'\[(v\d+)\]\s+((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun), \d{1,2} [A-Z][a-z]{2} \d{4} \d{2}:\d{2}:\d{2} UTC)'
        for version, stamp in re.findall(pattern, block):
            date = datetime.strptime(stamp, '%a, %d %b %Y %H:%M:%S UTC').replace(tzinfo=timezone.utc)
            old = histories[base].get(version)
            check(old is None or old == date, 'Conflicting history: ' + base + version)
            histories[base][version] = date
    for base, versions in histories.items():
        check(len(announced[base]) == 1, 'Ambiguous latest-version metadata: ' + base)
        latest = int(next(iter(announced[base]))[1:])
        check(set(versions) == {'v' + str(n) for n in range(1, latest + 1)},
              'Incomplete version history: ' + base)
    return histories


def citation_universe(survey):
    begins = [n for n, t in survey.lines.items() if clean(t).startswith('• ZO-SCG')]
    check(len(begins) == 1, 'Ambiguous complete ZO-SCG bullet')
    start = begins[0]
    ends = [n for n, t in survey.lines.items() if n > start and clean(t).startswith('• ')]
    check(bool(ends), 'Missing end of citation bullet')
    end = min(ends)
    survey.need(end, '• ZO-AdaMM')
    bullet = survey.get(start, end - 1)
    citations = list(dict.fromkeys(int(n) for n in re.findall(r'\[(\d+)\]', bullet)))
    check(bool(citations), 'Empty or unrecognized citation universe; no NONE generated')
    refs_text = survey.get(1210, 1327)
    starts = list(re.finditer(r'(?m)^\[(\d+)\]', refs_text))
    refs = {}
    for i, m in enumerate(starts):
        refs[int(m[1])] = refs_text[m.end():starts[i + 1].start() if i + 1 < len(starts) else len(refs_text)]
    check(all(n in refs for n in citations), 'Missing bibliography entry')
    return citations, refs


def resolve(citations, refs, docs):
    groups, ledger = {}, []
    originals = {name: doc for name, doc in docs.items() if name != '2006.06224v2'}
    for citation in citations:
        entry = refs[citation]
        titles = re.findall('“([^”]+)”', entry, flags=re.S)
        check(len(titles) == 1, f'Ambiguous title for citation {citation}')
        title = identity_text(titles[0])
        matches = [name for name, doc in originals.items()
                   if title in identity_text(doc.get(0, 10))]
        bases = {name.split('v')[0] for name in matches}
        check(len(bases) == 1, f'Missing or ambiguous identity for citation {citation}')
        base = next(iter(bases))
        explicit = re.findall(r'arXiv:(\d{4}\.\d{4,5})', entry)
        check(not explicit or set(explicit) == {base}, 'Bibliographic ID/title disagreement')
        surnames = re.findall(r'(?:[A-Z]\.\s*)+([A-Z][a-z]+)', entry.split('“')[0])
        check(bool(surnames), 'No auditable author identity for citation ' + str(citation))
        for name in matches:
            header = identity_text(originals[name].get(0, 10))
            check(all(identity_text(surname) in header for surname in surnames),
                  'Cited-author mismatch: ' + name)
        duplicate = base in groups
        groups.setdefault(base, {'citations': [], 'title_versions': []})
        groups[base]['citations'].append(citation)
        groups[base]['title_versions'].extend(matches)
        ledger.append({'citation': citation, 'arxiv_id': base, 'title': clean(titles[0]),
                       'matching_title_versions': matches,
                       'action': 'merge_same_work' if duplicate else 'include_work',
                       'reason': 'Matching original title and every cited author surname; common arXiv identity determines merging.'})
    return groups, ledger


def theorem(doc, line, part=None):
    text = doc.get(line)
    m = re.search(r'Theorem (\d+\.\d+)', text)
    check(m is not None, 'Missing theorem locator')
    return 'Theorem ' + m[1] + (f'({part})' if part else '')


def query_model(formula):
    q = compact(formula)
    shared = re.search(r'F\([^()]*[,;]([a-zξ]+)\)−F\([^()]*[,;]\1\)', q)
    exact = 'f(x+δui)−f(x−δui)' in q
    check(bool(shared) != bool(exact), 'Unrecognized or ambiguous function-query formula')
    return 'SAMPLE_FUNCTION' if shared else 'EXACT_FUNCTION'


def endpoint(variable, end, shift=0):
    subscript = f'({end}-{shift})' if shift else str(end)
    return variable + '_' + subscript


def classify(doc):
    # The adapters encode auditable selection reasoning, not per-ID gold labels.
    # Each output category below follows a checked formula or quantifier pattern.
    notes, conflicts = [], []
    if 'Assumption 1 Let' in clean(doc.lines.get(167, '')):
        doc.need(172, 'E[F(x, ξ)] = f(x)')
        doc.need(179, 'we do not observe')
        doc.need(182, 'Lipschitz continuous gradient')
        doc.need(193, 'standard Gaussian')
        doc.need(316, 'Algorithm 1 Zeroth-order Stochastic Conditional Gradient Method')
        doc.need(323, 'according to (1.4)')
        doc.get(330, 341)
        doc.need(407, 'generated by Algorithm 1')
        doc.need(408, 'Let f be nonconvex')
        doc.need(231, 'Theorem 1.1')
        doc.need(271, 'Theorem 1.2')
        doc.need(1134, 'Method with Inexact Updates')
        part = re.match(r'(\d+)\.', clean(doc.get(408)))
        check(part is not None, 'Missing nonconvex theorem part')
        locator = theorem(doc, 407, part[1])
        query = query_model(doc.get(221, 223))
        definition = compact(doc.get(389, 394))
        gap = re.search(r'g([a-z])X≡gX\(([a-z])\1−(\d+)\)', definition)
        distribution = re.search(r'([A-Z])isuniformlydistributedover\{(\d+),\.\.\.,([A-Z])\}', compact(doc.get(438)))
        lhs = compact(doc.get(426, 429))
        check(gap is not None and distribution is not None, 'Missing gap-index definition or uniform law')
        check(lhs == 'E[g' + distribution[1] + 'X]≤', 'Changed expected random gap')
        shift = int(gap[3])
        lower = int(distribution[2]) - shift
        check(lower >= 0, 'Unsupported negative iterate index')
        iterate_range = endpoint(gap[2], lower) + '..' + endpoint(gap[2], distribution[3], shift)
        form = 'EXPECTED_UNIFORM_GAP'
        notes.append('The preliminary theorems concern smoothing/Stein identities. The first own conditional-gradient gap theorem explicitly has a nonconvex part. A later inexact-updates method does not supersede that first statement.')
        notes.append('The lhs is the expectation of the random-index gap. The definition places gap k at iterate k-1; the printed uniform index law supplies both range endpoints.')
    elif 'Theorem 4.8.' in doc.lines.get(396, ''):
        doc.get(162, 170)
        doc.need(166, 'attack loss function')
        doc.need(210, '∇f(xt)')
        doc.need(336, 'Theorem 4.4.')
        doc.need(339, 'Algorithm 1')
        doc.need(245, 'Black-box Attack Algorithm')
        doc.need(250, 'GRAD EST')
        doc.get(266, 284)
        doc.get(294, 296)
        doc.need(394, 'Algorithm')
        doc.need(395, '2.')
        doc.get(396, 415)
        query = query_model(doc.get(273) + '\n' + doc.get(280))
        locator = theorem(doc, 396)
        check(compact(doc.get(402)) == 'E[geT]≤', 'Changed expected minimum abbreviation')
        definition = compact(doc.get(412))
        gap = re.search(r'min(\d+)≤([a-z])≤([A-Z])([a-zA-Z]+)\(([a-z])\2\)', definition)
        check(gap is not None, 'Missing printed minimum range')
        doc.need(412, 'randomness of the gradient estimator')
        iterate_range = endpoint(gap[5], int(gap[1])) + '..' + endpoint(gap[5], gap[3])
        form = 'EXPECTED_MIN_GAP'
        notes.append('The earlier gap theorem names the white-box algorithm, whose update queries gradients. The selected statement names the black-box algorithm; its symmetric differences evaluate the fixed attack loss.')
        notes.append('Expectation applies to the abbreviation for the trajectory minimum, over the exact printed range. The statement explicitly attributes randomness to gradient estimation.')
    elif 'Theorem 3.6.' in doc.lines.get(1021, ''):
        doc.get(188, 196)
        doc.need(195, 'unbiased estimate')
        doc.need(196, 'F (xt; yt)')
        doc.need(265, 'convex')
        doc.get(285, 295)
        doc.need(448, '(13)')
        doc.need(753, 'Convex Case')
        doc.need(762, 'Assumptions A1-A5')
        doc.need(828, 'Assumptions A1-A5')
        doc.need(978, 'Non-Convex')
        doc.need(981, 'Algorithm 3')
        doc.get(998, 1023)
        doc.need(1021, 'Assumptions A4-A6')
        doc.need(1023, '(13)')
        query = query_model(doc.get(1009))
        locator = theorem(doc, 1021)
        lhs = compact(doc.get(1024, 1030))
        gap = re.fullmatch(r'Emin([a-z])=(\d+),[·.]+,([A-Z])−(\d+)([A-Za-z]+)\(([a-z])\1\)≤', lhs)
        check(gap is not None, 'Changed expectation/minimum structure')
        iterate_range = endpoint(gap[6], int(gap[2])) + '..' + endpoint(gap[6], gap[3], int(gap[4]))
        form = 'EXPECTED_MIN_GAP'
        doc.get(824, 827)
        doc.need(827, '∇F(x)')
        doc.need(3689, 'Assumptions A3-A6')
        algorithm_power = re.search(r'\(t\+8\)(\d+/\d+)', compact(doc.get(992)))
        appendix_power = re.search(r'\(t\+8\)(\d+/\d+)', compact(doc.get(3777)))
        check(algorithm_power is not None and appendix_power is not None, 'Missing schedule comparison anchors')
        check(algorithm_power[1] != appendix_power[1], 'Previously observed schedule discrepancy changed')
        conflicts.append({'kind': 'schedule_text', 'algorithm_power': algorithm_power[1], 'appendix_power': appendix_power[1], 'lines': [992, 3777]})
        conflicts.append({'kind': 'assumption_text', 'lines': [265, 1021, 3689], 'observation': 'Main statement names A4-A6; appendix lemma names A3-A6; A3 includes convexity.'})
        conflicts.append({'kind': 'gap_notation', 'lines': [188, 192, 827, 1028], 'observation': 'The printed G definition differentiates F(x), while the stochastic setup distinguishes F(x;y) and f(x). No replacement of F by f is made.'})
        notes.append('The preceding main results are under convex assumptions. The selected nonconvex statement references update (13); its surrounding Algorithm 3 evaluates shared-sample finite differences.')
        notes.append('The lhs directly places expectation outside the minimum. Its printed range excludes x_T, although Algorithm 3 lists x_T as output. G is retained as the paper-defined symbol.')
    else:
        raise ValueError('No audited semantic adapter for selected source ' + doc.name)
    return [locator, query, form, iterate_range], notes, conflicts


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    docs = load_documents(args.source_dir)
    check('2006.06224v2' in docs, 'Missing survey')
    histories = load_history(args.source_dir / 'history_metadata.txt')
    check('2006.06224' in histories and 'v2' in histories['2006.06224'], 'Missing cutoff history')
    cutoff = histories['2006.06224']['v2']
    citations, refs = citation_universe(docs['2006.06224v2'])
    groups, ledger = resolve(citations, refs, docs)
    rows, inventory, discrepancies = [], [], []
    for base, group in groups.items():
        check(base in histories, 'Missing original history: ' + base)
        eligible = [(date, int(version[1:]), version) for version, date in histories[base].items() if date <= cutoff]
        check(bool(eligible), 'No version at cutoff: ' + base)
        _, _, version = max(eligible)
        selected = base + version
        check(selected in docs, 'Missing selected original: ' + selected)
        fields, notes, conflicts = classify(docs[selected])
        rows.append([base, version] + fields)
        inventory.append({'arxiv_id': base, 'citations': group['citations'],
                          'identity_title_versions': sorted(set(group['title_versions'])),
                          'selected_version': version,
                          'history': {v: d.isoformat() for v, d in histories[base].items()},
                          'selection_rule': 'latest posting no later than survey v2 posting',
                          'field_derivation': notes})
        discrepancies.extend(dict(source=selected, **c) for c in conflicts)
    check(len(rows) == len(groups) and len(ledger) == len(citations), 'Incomplete inclusion ledger')
    check(len({row[0] for row in rows}) == len(rows), 'Duplicate output identities')
    check(all(len(row) == len(COLUMNS) and all(isinstance(v, str) and v for v in row) for row in rows), 'Incomplete output fields')
    anchors = {name: [doc.used[n] for n in sorted(doc.used)] for name, doc in docs.items() if doc.used}
    result = {'status': 'source_claims_recomputed', 'cutoff': cutoff.isoformat(),
              'citation_count': len(citations), 'distinct_work_count': len(rows),
              'every_citation_accounted_for': True, 'unknown_gold_cells': 0,
              'discrepancies_retained': discrepancies,
              'proof_verification': 'not_performed', 'solver_tests': 'not_run'}
    # Publish only after every required source and classification has succeeded.
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / 'oracle.psv').write_text('\n'.join('|'.join(row) for row in [COLUMNS] + rows) + '\n', encoding='utf-8')
    write_json(args.out_dir / 'inventory.json', inventory)
    write_json(args.out_dir / 'inclusion_ledger.json', ledger)
    write_json(args.out_dir / 'evidence_anchors.json', anchors)
    write_json(args.out_dir / 'execution_checks.json', result)
    print(f'source_claims_recomputed: {len(citations)} citations, {len(rows)} distinct works')


if __name__ == '__main__':
    main()
