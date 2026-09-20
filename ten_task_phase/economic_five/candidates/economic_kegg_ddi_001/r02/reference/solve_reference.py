#!/usr/bin/env python3
"""Rebuild this reference from exported raw HTTP bodies. Standard library only.
Run from the stage directory, choosing an output directory that does not exist:
  python3 reference/solve_reference.py --root . --out reference/replay-02
This program performs no network I/O and requires the original delivered oracle.
"""
import argparse
import csv
import io
import itertools
import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def jsonl(rows):
    return ''.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) + '\n'
                   for x in rows)


def read_sources(root, manifest):
    sources = {}
    for spec in manifest['sources']:
        if spec['role'] == 'failed_optional_boundary':
            continue
        require(spec['status'] == 200, 'Required source failed: ' + spec['file_id'])
        require(spec['file_id'] not in sources, 'Duplicate source file ID: ' + spec['file_id'])
        raw = (root / spec['path']).read_bytes()
        require(len(raw) == spec['bytes'], 'Byte count differs: ' + spec['file_id'])
        sources[spec['file_id']] = raw.decode('utf-8')
    return sources


def parse_members(text, file_id):
    members = []
    group = None
    active = False
    entries, terminated = [], []
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith('ENTRY'):
            require(group is None, 'Unterminated member entry')
            match = re.match(r'ENTRY\s+(DG\d{5})\b', line)
            require(match is not None, 'Bad group ENTRY')
            group = match.group(1)
            entries.append(group)
        if line == '///':
            require(group is not None, 'Unexpected terminator')
            terminated.append(group)
            group, active = None, False
            continue
        label = line[:12].strip()
        if label == 'MEMBER':
            active = True
        elif label and label != 'MEMBER':
            active = False
        if active:
            match = re.match(r'\s*(D\d{5})\s+(.+)$', line[12:])
            if match:
                members.append({
                    'group_id': group, 'drug_id': match.group(1),
                    'name_as_reported': match.group(2).strip(),
                    'source': {'file_id': file_id, 'line': number}
                })
    require(group is None and entries == terminated, 'Incomplete group body')
    require(len(entries) == len(set(entries)), 'Duplicate group ENTRY')
    require(len(members) == len({(x['group_id'], x['drug_id']) for x in members}),
            'Duplicate leaf membership')
    return sorted(members, key=lambda x: (x['group_id'], x['drug_id']))


def parse_ddi_endpoint(value, file_id, number, column, d_only):
    location = '%s:%d column %d' % (file_id, number, column)
    require(re.fullmatch(r'(?:dr:D[0-9]{5}|cpd:C[0-9]{5})', value) is not None,
            'Unexpected DDI identity at %s: %r' % (location, value))
    require(not d_only or value.startswith('dr:'),
            'Non-drug endpoint in D-only response at %s: %r' % (location, value))
    # Match official D-ID membership keys, while keeping chemical identities
    # explicitly namespaced. No valid endpoint or row is discarded here.
    return value[3:] if value.startswith('dr:') else value


def parse_ddi(text, file_id, d_only=False):
    result = []
    reader = csv.reader(io.StringIO(text), delimiter='\t', strict=True)
    for number, row in enumerate(reader, 1):
        require(len(row) == 4, 'Malformed DDI row: %s:%d' % (file_id, number))
        raw_a, raw_b, raw_classes, mechanism = row
        a = parse_ddi_endpoint(raw_a, file_id, number, 1, d_only)
        b = parse_ddi_endpoint(raw_b, file_id, number, 2, d_only)
        tokens = raw_classes.split(',')
        require(tokens and set(tokens) <= {'CI', 'P'} and len(tokens) == len(set(tokens)),
                'Unknown/duplicate classification at %s:%d: %r' %
                (file_id, number, raw_classes))
        result.append((a, b, ','.join(sorted(tokens)), number, mechanism, file_id))
    require(bool(result), 'Required DDI response is empty: ' + file_id)
    return result


def normalize(records, ssri, mao, cross_only=True):
    classes, evidence = defaultdict(set), defaultdict(list)
    for a, b, c, line, mechanism, file_id in records:
        if a in ssri and b in mao:
            key = (a, b)
        elif b in ssri and a in mao:
            key = (b, a)
        elif not cross_only and a in ssri | mao and b in ssri | mao:
            key = tuple(sorted((a, b)))
        else:
            # Exclusion depends on actual membership, not a parser namespace filter.
            continue
        require(a != b, 'Self pair in selected records')
        classes[key].update(c.split(','))
        evidence[key].append({'file_id': file_id, 'line': line})
    return {k: ','.join(sorted(v)) for k, v in classes.items()}, evidence


def member_html_check(text, expected):
    start = text.index('<span class="nowrap">Member</span>')
    end = text.index('<span class="nowrap">Class</span>', start)
    section = text[start:end]
    found = set(re.findall(r'href="/entry/(D\d{5})"', section))
    require(found == expected, 'HTML/API leaf membership differs')
    return {'count': len(found), 'member_start_char': start, 'member_end_char': end,
            'hidden_css': '.mem1{display:none;}' in section}


def psv(pairs):
    rows = ['ssri_id|mao_id|classes']
    rows += ['|'.join((a, b, pairs[(a, b)])) for a, b in sorted(pairs)]
    if not pairs:
        rows.append('NONE')
    return '\n'.join(rows) + '\n'


def write_csv(path, header, rows):
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = json.loads((root / 'source_manifest.json').read_text(encoding='utf-8'))
    definition = json.loads((root / 'candidate_definition.json').read_text(encoding='utf-8'))
    source = read_sources(root, manifest)
    by_role = defaultdict(list)
    for spec in manifest['sources']:
        by_role[spec['role']].append(spec)

    def one(role):
        require(len(by_role[role]) == 1, 'Expected one source: ' + role)
        return by_role[role][0]

    gm, bm = one('members'), one('batch')
    members = parse_members(source[gm['file_id']], gm['file_id'])
    group_ids = definition['private_source']['group_ids']
    require({m['group_id'] for m in members} == set(group_ids.values()), 'Wrong groups')
    ssri = {m['drug_id'] for m in members if m['group_id'] == group_ids['ssri']}
    mao = {m['drug_id'] for m in members if m['group_id'] == group_ids['mao']}
    require(ssri and mao and not (ssri & mao), 'Empty or overlapping groups need review')
    member_ids = ssri | mao
    require(set(bm['requested_drug_ids']) == member_ids, 'Batch omits discovered members')
    require(len(bm['requested_drug_ids']) == len(member_ids), 'Duplicate requested ID')
    batch = parse_ddi(source[bm['file_id']], bm['file_id'], d_only=True)
    require(all(a in member_ids and b in member_ids for a, b, *_ in batch),
            'Batch returned outside-scope IDs')
    directed = {(a, b): c for a, b, c, *_ in batch}
    require(len(directed) == len(batch), 'Duplicate/conflicting directed batch rows')
    require(all(directed.get((b, a)) == c for (a, b), c in directed.items()),
            'Unresolved reverse-orientation classification conflict')
    pairs, evidence = normalize(batch, ssri, mao)

    single_spec = {s['drug_id']: s for s in by_role['singleton']}
    require(len(single_spec) == len(by_role['singleton']) and set(single_spec) == member_ids,
            'Singleton coverage incomplete or duplicated')
    independent_specs = [bm] + list(single_spec.values())
    require(len({s['file_id'] for s in independent_specs}) == len(independent_specs),
            'Batch and singleton paths reuse source file IDs')
    require(len({(root / s['path']).resolve() for s in independent_specs}) ==
            len(independent_specs), 'Batch and singleton paths reuse source files')
    singles, ssri_only = [], []
    for drug_id, spec in sorted(single_spec.items()):
        rows = parse_ddi(source[spec['file_id']], spec['file_id'])
        require(all(a == drug_id for a, b, *_ in rows),
                'Singleton orientation changed: ' + spec['file_id'])
        singles.extend(rows)
        if drug_id in ssri:
            ssri_only.extend(rows)
    # This path uses the separately saved singleton responses for EVERY member
    # of BOTH groups. It does not fill gaps from batch-derived pairs.
    single_pairs, _ = normalize(singles, ssri, mao)
    require(single_pairs == pairs, 'Batch and BOTH endpoint singleton paths differ')
    ssri_pairs, _ = normalize(ssri_only, ssri, mao)

    # Independent relational computation: raw directed rows joined to member tables.
    db = sqlite3.connect(':memory:')
    db.execute('CREATE TABLE members(group_id TEXT, drug_id TEXT PRIMARY KEY)')
    db.executemany('INSERT INTO members VALUES (?,?)',
                   [(m['group_id'], m['drug_id']) for m in members])
    db.execute('CREATE TABLE ddi(a TEXT,b TEXT,classes TEXT)')
    db.executemany('INSERT INTO ddi VALUES (?,?,?)', [(a, b, c) for a, b, c, *_ in batch])
    sql_rows = db.execute(
        'SELECT DISTINCT d.a,d.b,d.classes FROM ddi d '
        'JOIN members s ON d.a=s.drug_id JOIN members m ON d.b=m.drug_id '
        'WHERE s.group_id=? AND m.group_id=? ORDER BY d.a,d.b',
        (group_ids['ssri'], group_ids['mao'])).fetchall()
    require(sql_rows == [(a, b, pairs[(a, b)]) for a, b in sorted(pairs)],
            'SQL and Python normalization differ')
    db.close()
    html_checks = {}
    for spec in by_role['member_html']:
        target = ssri if spec['group_id'] == group_ids['ssri'] else mao
        html_checks[spec['group_id']] = member_html_check(source[spec['file_id']], target)
    require(set(html_checks) == set(group_ids.values()), 'Missing HTML coverage check')
    repeated_groups = one('members_repeat')
    require(source[repeated_groups['file_id']] == source[gm['file_id']],
            'Repeated members differ')
    repeated_batch = one('batch_repeat')
    rb = parse_ddi(source[repeated_batch['file_id']], repeated_batch['file_id'], d_only=True)
    require(all(a in member_ids and b in member_ids for a, b, *_ in rb),
            'Repeated batch returned outside-scope IDs')
    require(sorted((a, b, c, m) for a, b, c, n, m, f in rb) ==
            sorted((a, b, c, m) for a, b, c, n, m, f in batch), 'Repeated DDI differs')
    for spec in by_role['boundary']:
        ids = set(spec['url'].rsplit('/', 1)[1].split('+'))
        local, _ = normalize(parse_ddi(source[spec['file_id']], spec['file_id']),
                             ssri, mao)
        expected = {k: v for k, v in pairs.items() if set(k) <= ids}
        require(local == expected, 'Fresh boundary slice differs')

    by_id = {m['drug_id']: m for m in members}
    ledger = []
    for a, b in itertools.product(sorted(ssri), sorted(mao)):
        key = (a, b)
        ledger.append({
            'ssri_id': a, 'mao_id': b, 'included': 'true' if key in pairs else 'false',
            'classes': pairs.get(key),
            'reason': 'reported_cross_group_pair' if key in pairs else
                      'not_reported_in_complete_successful_coverage',
            'evidence': {'batch': bm['file_id'],
                         'lines': [e['line'] for e in evidence.get(key, [])],
                         'endpoint_sources': [single_spec[a]['file_id'],
                                              single_spec[b]['file_id']]}})
    fields = []
    for a, b in sorted(pairs):
        fields.append({
            'row_key': [a, b],
            'ssri_id': dict(by_id[a]['source'], selector=a),
            'mao_id': dict(by_id[b]['source'], selector=b),
            'classes': {'file_id': bm['file_id'],
                        'lines': [x['line'] for x in evidence[(a, b)]],
                        'columns': [1, 2, 3],
                        'formula': 'Union the comma-separated CI/P tokens for both orientations of this exact D-ID pair; serialize CI before P.'}})
    all_pairs, all_evidence = normalize(batch, ssri, mao, False)
    within = {k: v for k, v in all_pairs.items()
              if (k[0] in ssri and k[1] in ssri) or (k[0] in mao and k[1] in mao)}
    # Deliberately wrong identity inheritance, selected from saved member names.
    free = [m['drug_id'] for m in members
            if m['name_as_reported'].split(' (', 1)[0] == 'Paroxetine']
    salt = [m['drug_id'] for m in members
            if m['name_as_reported'].startswith('Paroxetine hydrochloride hemihydrate (')]
    require(len(free) == len(salt) == 1, 'Salt boundary identity no longer unique')
    inherited = {(free[0], b): c for (a, b), c in pairs.items() if a == salt[0]}
    salt_added = {k: v for k, v in inherited.items() if k not in pairs}
    salt_changed = {k: (pairs[k], v) for k, v in inherited.items()
                    if k in pairs and pairs[k] != v}
    cf = {
        'baseline_rows': len(pairs),
        'within_group_exclusion': {
            'wrong_rows': len(pairs) + len(within),
            'added_rows': [{'row_key': list(k), 'classes': within[k],
                            'evidence': all_evidence[k]} for k in sorted(within)]},
        'salt_identity': {
            'wrong_rule': 'Inherit every selected paroxetine hydrate record for free paroxetine.',
            'source_id': salt[0], 'destination_id': free[0],
            'wrong_rows': len(pairs) + len(salt_added),
            'added_rows': [{'row_key': list(k), 'classes': salt_added[k]}
                           for k in sorted(salt_added)],
            'changed_values': [{'row_key': list(k), 'values': v}
                               for k, v in sorted(salt_changed.items())]},
        'ssri_endpoint_only': {
            'wrong_rows': len(ssri_pairs),
            'removed_rows': [{'row_key': list(k), 'classes': pairs[k]}
                             for k in sorted(pairs.keys() - ssri_pairs.keys())]},
        'worst_class_only': {
            'changed_values': [{'row_key': list(k), 'correct': v, 'wrong': 'CI'}
                               for k, v in sorted(pairs.items()) if v == 'CI,P']}}
    require(within and salt_added, 'Claimed counterfactual has no actual effect')
    oracle = psv(pairs)
    delivered = root / 'reference/oracle.psv'
    require(delivered.is_file(), 'Original delivered oracle missing; equality cannot be checked')
    require(delivered.read_text(encoding='utf-8') == oracle, 'Delivered oracle differs')
    require(len(ledger) == len(ssri) * len(mao), 'Incomplete ledger')
    require(len({(r['ssri_id'], r['mao_id']) for r in ledger}) == len(ledger),
            'Duplicate ledger row keys')
    require(all(v in {'CI', 'P', 'CI,P'} for v in pairs.values()), 'Null or invalid output class')
    # All required comparisons precede output creation. Never replace an old run.
    args.out.mkdir(parents=True, exist_ok=False)
    out = args.out
    for name, rows in [('candidate_universe.jsonl', members), ('inclusion_ledger.jsonl', ledger),
                       ('field_evidence.jsonl', fields)]:
        (out / name).write_text(jsonl(rows), encoding='utf-8')
    (out / 'oracle.psv').write_text(oracle, encoding='utf-8')
    (out / 'counterfactuals.json').write_text(json.dumps(cf, indent=2) + '\n', encoding='utf-8')
    write_csv(out / 'normalized_members.csv',
              ['group_id', 'drug_id', 'name_as_reported', 'source_file_id', 'source_line'],
              [(m['group_id'], m['drug_id'], m['name_as_reported'],
                m['source']['file_id'], m['source']['line']) for m in members])
    ddi_header = ['drug1', 'drug2', 'classes', 'source_line', 'mechanism', 'source_file_id']
    write_csv(out / 'normalized_ddi.csv', ddi_header, batch)
    # Retain the complete singleton parse, including out-of-group chemical rows.
    write_csv(out / 'normalized_singleton_ddi.csv', ddi_header, singles)
    checks = {
        'member_counts': {group_ids['ssri']: len(ssri), group_ids['mao']: len(mao)},
        'candidate_pairs': len(ledger), 'reported_pairs': len(pairs),
        'not_reported_pairs': sum(r['included'] == 'false' for r in ledger),
        'unknown_pairs': 0,
        'class_counts': {c: sum(v == c for v in pairs.values())
                         for c in sorted(set(pairs.values()))},
        'batch_directed_rows': len(batch), 'singleton_directed_rows': len(singles),
        'singleton_chemical_endpoint_rows': sum(
            a.startswith('cpd:') or b.startswith('cpd:') for a, b, *_ in singles),
        'singleton_outside_member_rows': sum(
            a not in member_ids or b not in member_ids for a, b, *_ in singles),
        'singleton_sources': len(single_spec),
        'source_file_independence': 'distinct batch and singleton file IDs and resolved paths',
        'both_endpoint_comparison': 'equal', 'sql_comparison': 'equal',
        'html_membership': html_checks, 'construction_repeat': 'equal',
        'fresh_boundary_slices': 'equal', 'delivered_oracle': 'equal',
        'campaign_stability': 'not established by this offline program'}
    (out / 'validation.json').write_text(json.dumps(checks, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(checks, sort_keys=True))


if __name__ == '__main__':
    main()
