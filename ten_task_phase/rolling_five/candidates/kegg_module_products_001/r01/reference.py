#!/usr/bin/env python3
"""Derive module-specific product differences from supplied primary flat files.
Standard library only. No network, scorer calls, or hardcoded answer records.
"""
import argparse
import json
import re
import sys
from fractions import Fraction
from pathlib import Path

EC = '4.1.1.39'
TARGET = 'C01182'
OUTPUTS = ('oracle.psv', 'inventory.json', 'inclusion_ledger.json',
           'evidence_anchors.json', 'execution_checks.json')
RID = r'R[0-9]{5}'
ARROW = re.compile(r'<=>|<->|->|=>|<-|<=')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def flat_records(path):
    records, current, field = [], None, None
    text = path.read_text(encoding='utf-8')
    require(text.strip(), f'{path.name}: empty required flat file')
    for number, raw in enumerate(text.splitlines(), 1):
        if not raw.strip():
            continue
        if raw.strip() == '///':
            require(current is not None, f'{path.name}:{number}: orphan terminator')
            current['end_line'] = number
            records.append(current)
            current, field = None, None
            continue
        require(len(raw) >= 12, f'{path.name}:{number}: short flat-field line')
        label, value = raw[:12].strip(), raw[12:]
        if label:
            require(re.fullmatch(r'[A-Z][A-Z0-9_]*', label),
                    f'{path.name}:{number}: invalid field label')
            if label == 'ENTRY':
                require(current is None, f'{path.name}:{number}: missing terminator')
                current = {'start_line': number, 'fields': {}}
            require(current is not None, f'{path.name}:{number}: field before ENTRY')
            field = label
        else:
            require(current is not None and field is not None,
                    f'{path.name}:{number}: orphan continuation')
        current['fields'].setdefault(field, []).append(
            {'line': number, 'text': value, 'raw': raw})
    require(current is None, f'{path.name}: unterminated record')
    require(records, f'{path.name}: no records')
    return records


def field_text(record, field):
    return ' '.join(x['text'].strip() for x in record['fields'].get(field, []))


def anchor(filename, entries, **context):
    require(entries, f'{filename}: cannot anchor an absent field')
    numbers = [x['line'] for x in entries]
    return {'id': filename + ':' + ','.join(map(str, numbers)),
            'source_file': filename, 'lines': numbers,
            'quote': '\n'.join(x['raw'] for x in entries), **context}


def record_inventory(identifier, record):
    return {'id': identifier, 'start_line': record['start_line'],
            'terminator_line': record['end_line'],
            'field_line_counts': {k: len(v) for k, v in record['fields'].items()}}


def reaction_lines(record):
    rows = []
    header = re.compile(r'^(R[0-9]{5}(?:,R[0-9]{5})*)\s+(.+)$')
    for item in record['fields'].get('REACTION', []):
        value = item['text'].strip()
        match = header.fullmatch(value)
        if match:
            rows.append({'reaction_ids': sorted(set(match[1].split(','))),
                         'equation': match[2], 'entries': [item]})
        else:
            require(rows and value and not value.startswith('R'),
                    f'modules.txt:{item["line"]}: unresolved REACTION row header')
            rows[-1]['equation'] += ' ' + value
            rows[-1]['entries'].append(item)
    for row in rows:
        require(not re.search(r'\bR[0-9]{5}\b', row['equation']),
                f'modules.txt:{row["entries"][0]["line"]}: reaction ID in equation or malformed continuation')
    return rows


def compounds(side):
    result = set()
    for term in side.split('+'):
        match = re.fullmatch(
            r'(?:(\d+(?:\.\d+)?|\d+/\d+)\s+)?(C[0-9]{5})', term.strip())
        require(match is not None, 'unresolved compound expression: ' + repr(term))
        if match[1] is not None:
            require(Fraction(match[1]) > 0, 'nonpositive compound coefficient')
        result.add(match[2])
    require(result, 'unresolved empty compound side')
    return result


def interpret(equation):
    arrows = list(ARROW.finditer(equation))
    require(len(arrows) == 1, 'unresolved arrow in: ' + equation)
    match = arrows[0]
    left = compounds(equation[:match.start()])
    right = compounds(equation[match.end():])
    arrow = match.group()
    result = {'arrow': arrow, 'written_left_ids': sorted(left),
              'written_right_ids': sorted(right)}
    require(not (TARGET in left and TARGET in right),
            'C01182 occurs on both sides; consumption unresolved: ' + equation)
    if arrow in ('<->', '<=>'):
        if TARGET not in left | right:
            return {**result, 'qualifying': False, 'reason': 'C01182_absent',
                    'input_ids': None, 'product_ids': None}
        inputs, products = (left, right) if TARGET in left else (right, left)
    elif arrow in ('->', '=>'):
        inputs, products = left, right
    else:
        inputs, products = right, left
    qualifies = TARGET in inputs
    return {**result, 'input_ids': sorted(inputs), 'product_ids': sorted(products),
            'qualifying': qualifies,
            'reason': 'C01182_consumed' if qualifies else 'C01182_not_consumed'}


def build(source):
    enzymes = flat_records(source / 'enzyme.txt')
    require(len(enzymes) == 1, 'enzyme.txt: expected one enzyme record')
    enzyme = enzymes[0]
    require(re.fullmatch(r'EC\s+' + re.escape(EC) + r'\s+Enzyme',
                         field_text(enzyme, 'ENTRY')),
            'enzyme.txt: wrong enzyme ENTRY')
    all_reac = field_text(enzyme, 'ALL_REAC')
    roots = set(re.findall(r'\b' + RID + r'\b', all_reac))
    residue = re.sub(r'\b' + RID + r'\b', '', all_reac)
    residue = residue.replace('(other)', '')
    require(roots and re.fullmatch(r'[\s;]*', residue),
            'enzyme.txt: missing or unresolved full ALL_REAC field')
    anchors = [anchor('enzyme.txt', enzyme['fields']['ENTRY'], field='ENTRY'),
               anchor('enzyme.txt', enzyme['fields']['ALL_REAC'], field='ALL_REAC')]
    links, link_entries = set(), []
    for number, raw in enumerate((source / 'module_links.tsv').read_text(encoding='utf-8').splitlines(), 1):
        if not raw.strip():
            continue
        match = re.fullmatch(r'ec:' + re.escape(EC) + r'\tmd:(M[0-9]{5})', raw)
        require(match is not None, f'module_links.tsv:{number}: unresolved direct link')
        links.add(match[1])
        link_entries.append({'line': number, 'raw': raw})
    require(links, 'module_links.tsv: empty scope response is unresolved')
    anchors.append(anchor('module_links.tsv', link_entries, relation='enzyme_to_module'))

    modules = {}
    for record in flat_records(source / 'modules.txt'):
        match = re.fullmatch(r'(M[0-9]{5})\s+.*\bModule', field_text(record, 'ENTRY'))
        require(match is not None, 'modules.txt: invalid module ENTRY')
        mid = match[1]
        require(mid not in modules, 'modules.txt: duplicate module body ' + mid)
        require(field_text(record, 'NAME') and field_text(record, 'DEFINITION'),
                'modules.txt: incomplete identifying body for ' + mid)
        modules[mid] = record
    require(set(modules) == links,
            'module body/link mismatch: missing=' + str(sorted(links - set(modules))) +
            '; extra=' + str(sorted(set(modules) - links)))

    row_inventory, ledger, pairs, seen_pairs = [], [], {}, set()
    for mid in sorted(modules):
        record = modules[mid]
        anchors.append(anchor('modules.txt', record['fields']['ENTRY'], module_id=mid, field='ENTRY'))
        for row in reaction_lines(record):
            evidence = anchor('modules.txt', row['entries'], module_id=mid, field='REACTION')
            anchors.append(evidence)
            hits = sorted(set(row['reaction_ids']) & roots)
            row_inventory.append({'module_id': mid, 'reaction_ids': row['reaction_ids'],
                                  'matched_reaction_ids': hits, 'equation': row['equation'],
                                  'anchor_id': evidence['id'],
                                  'scope_decision': 'in_scope' if hits else 'outside_ALL_REAC'})
            if not hits:
                continue
            try:
                interpretation = interpret(row['equation'])
            except (ValueError, ZeroDivisionError) as error:
                raise ValueError(evidence['id'] + ': ' + str(error)) from error
            for rid in hits:
                key = (rid, mid)
                seen_pairs.add(key)
                decision = {'reaction_id': rid, 'module_id': mid,
                            'anchor_id': evidence['id'], **interpretation}
                if interpretation['qualifying']:
                    products = tuple(interpretation['product_ids'])
                    require(key not in pairs or pairs[key] == products,
                            'conflicting qualifying product sets for ' + repr(key))
                    decision['duplicate_qualifying_source'] = key in pairs
                    pairs[key] = products
                else:
                    decision['decision'] = 'exclude_not_consuming'
                ledger.append(decision)

    groups, retained = [], set()
    for rid in sorted(roots):
        members = sorted(mid for r, mid in pairs if r == rid)
        sets = sorted({products for (r, mid), products in pairs.items() if r == rid})
        if len(sets) >= 2:
            reason = 'different_products_across_modules'
            retained.add(rid)
        elif not members:
            reason = 'no_qualifying_module_rows'
        elif len(members) == 1:
            reason = 'single_qualifying_module'
        else:
            reason = 'same_products_across_modules'
        groups.append({'reaction_id': rid, 'qualifying_module_ids': members,
                       'distinct_product_sets': [list(x) for x in sets],
                       'decision': 'include' if rid in retained else 'exclude', 'reason': reason})
    group_reasons = {x['reaction_id']: x['reason'] for x in groups}
    for item in ledger:
        if item['qualifying']:
            item['decision'] = 'include_pair' if item['reaction_id'] in retained else 'exclude_group'
            item['group_reason'] = group_reasons[item['reaction_id']]
    for rid in sorted(roots):
        for mid in sorted(links):
            if (rid, mid) not in seen_pairs:
                ledger.append({'reaction_id': rid, 'module_id': mid,
                               'decision': 'no_matching_REACTION_line',
                               'product_ids': None,
                               'record_lines': [modules[mid]['start_line'], modules[mid]['end_line']],
                               'source_file': 'modules.txt'})

    audit = {'status': 'not_supplied', 'affects_selection': False, 'records': []}
    optional = source / 'reactions.txt'
    if optional.exists():
        audit['status'] = 'parsed_optional_context'
        audit_ids = set()
        for record in flat_records(optional):
            match = re.fullmatch(r'(R[0-9]{5})\s+Reaction', field_text(record, 'ENTRY'))
            require(match is not None, 'reactions.txt: invalid optional reaction ENTRY')
            rid = match[1]
            require(rid not in audit_ids, 'reactions.txt: duplicate optional reaction body')
            audit_ids.add(rid)
            audit['records'].append({'reaction_id': rid,
                                     'equation': field_text(record, 'EQUATION'),
                                     'module_annotation': field_text(record, 'MODULE')})
            for field in ('ENTRY', 'EQUATION', 'MODULE'):
                if record['fields'].get(field):
                    anchors.append(anchor('reactions.txt', record['fields'][field],
                                          reaction_id=rid, field=field, role='optional_context'))

    output_rows = [(rid, mid, products) for (rid, mid), products in sorted(pairs.items())
                   if rid in retained]
    if output_rows:
        oracle = 'REACTION_ID|MODULE_ID|PRODUCT_IDS\n' + ''.join(
            rid + '|' + mid + '|' + ','.join(products) + '\n'
            for rid, mid, products in output_rows)
    else:
        oracle = 'NONE\n'
    inventory = {'source_dir': str(source.resolve()),
                 'enzyme': record_inventory('ec:' + EC, enzyme),
                 'all_reaction_ids': sorted(roots), 'linked_module_ids': sorted(links),
                 'link_line_count': len(link_entries),
                 'duplicate_link_count': len(link_entries) - len(links),
                 'modules': [record_inventory(mid, modules[mid]) for mid in sorted(modules)],
                 'reaction_rows': row_inventory, 'optional_reaction_context': audit}
    checks = {'status': 'completed', 'source_parse': 'passed', 'flat_field_width': 12,
              'all_records_terminated': True, 'enzyme_identity_verified': True,
              'full_ALL_REAC_consumed': True, 'direct_link_module_coverage': 'exact',
              'module_count': len(modules), 'root_reaction_count': len(roots),
              'reaction_field_rows_inspected': len(row_inventory),
              'matching_source_rows': sum(bool(x['matched_reaction_ids']) for x in row_inventory),
              'qualifying_unique_pairs_before_difference_filter': len(pairs),
              'retained_reaction_count': len(retained), 'output_row_count': len(output_rows),
              'products_derived_only_from_module_REACTION': True,
              'unresolved_inputs': [], 'solver_tests': 'not_performed',
              'independent_final_audit': 'not_performed', 'human_review': 'not_performed',
              'source_field_stability': 'not_performed'}
    return {'oracle.psv': oracle, 'inventory.json': inventory,
            'inclusion_ledger.json': {'source_line_decisions': ledger, 'reaction_groups': groups},
            'evidence_anchors.json': {'source_dir': str(source.resolve()), 'anchors': anchors},
            'execution_checks.json': checks}


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    # These are this program's generated artifacts; remove stale results first.
    for name in OUTPUTS:
        path = args.out_dir / name
        if path.exists():
            path.unlink()
    try:
        artifacts = build(args.source_dir)
        for name in ('inventory.json', 'inclusion_ledger.json', 'evidence_anchors.json'):
            write_json(args.out_dir / name, artifacts[name])
        (args.out_dir / 'oracle.psv').write_text(artifacts['oracle.psv'], encoding='utf-8')
        write_json(args.out_dir / 'execution_checks.json', artifacts['execution_checks.json'])
    except (ValueError, OSError, ZeroDivisionError) as error:
        oracle = args.out_dir / 'oracle.psv'
        if oracle.exists():
            oracle.unlink()
        failure = {'status': 'failed', 'error': str(error), 'oracle_emitted': False,
                   'empty_result_claimed': False, 'solver_tests': 'not_performed',
                   'independent_final_audit': 'not_performed', 'human_review': 'not_performed'}
        write_json(args.out_dir / 'execution_checks.json', failure)
        print(json.dumps(failure), file=sys.stderr)
        return 2
    print(json.dumps({'status': 'completed',
                      'output_row_count': artifacts['execution_checks.json']['output_row_count']}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
