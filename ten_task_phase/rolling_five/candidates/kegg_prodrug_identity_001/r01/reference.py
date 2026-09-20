#!/usr/bin/env python3
"""Derive the documented D-to-D relations from supplied complete flatfiles."""
import argparse
import json
import re
import sys
from pathlib import Path

GROUP = 'DG00739'
MARKER = 'Active form of prodrug:'
OUTPUTS = ('oracle.psv', 'inventory.json', 'inclusionledger.json', 'evidence.json')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parse_records(path):
    records = {}
    current = None
    block = None
    for number, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if raw.strip() == '///':
            require(current is not None, f'{path.name}:{number}: orphan terminator')
            current['end_line'] = number
            ident = current['id']
            require(ident not in records, f'{path.name}: duplicate ENTRY {ident}')
            records[ident] = current
            current = block = None
            continue
        if not raw.strip():
            continue
        require(len(raw) >= 12, f'{path.name}:{number}: invalid field width')
        label, value = raw[:12].strip(), raw[12:].rstrip()
        if label == 'ENTRY':
            require(current is None, f'{path.name}:{number}: missing record terminator')
            parts = value.split()
            require(len(parts) == 2, f'{path.name}:{number}: invalid ENTRY')
            current = {'id': parts[0], 'kind': parts[1],
                       'path': '../sources/' + path.name,
                       'start_line': number, 'fields': []}
            block = None
        require(current is not None, f'{path.name}:{number}: text outside a record')
        if label:
            block = {'field': label, 'lines': []}
            current['fields'].append(block)
        require(block is not None, f'{path.name}:{number}: orphan continuation')
        block['lines'].append({'line': number, 'text': value})
    require(current is None, f'{path.name}: unterminated final record')
    return records


def blocks(record, field):
    return [b for b in record['fields'] if b['field'] == field]


def lines(record, field):
    return [line for b in blocks(record, field) for line in b['lines']]


def values(record, field):
    return [line['text'].strip() for line in lines(record, field)]


def primary_name(record):
    names = values(record, 'NAME')
    require(names and names[0], f"{record['id']}: missing NAME")
    return names[0].rstrip(';').strip()


def anchor(record, field=None):
    result = {'path': record['path'], 'record': record['id'],
              'record_lines': [record['start_line'], record['end_line']]}
    if field is not None:
        result['field'] = field
        result['field_lines'] = [line['line'] for line in lines(record, field)]
    return result


def own_relations(record):
    sections = []
    for block in blocks(record, 'COMMENT'):
        current = None
        for line in block['lines']:
            text = line['text'].strip()
            if text.startswith(MARKER):
                current = {'text': [text[len(MARKER):].strip()],
                           'lines': [line['line']]}
                sections.append(current)
            elif MARKER in text:
                raise ValueError(f"{record['id']}: unresolved annotation placement")
            elif current is not None:
                # Another named comment clause ends this relation section.
                if re.match(r'^[A-Za-z][A-Za-z /()-]*:', text):
                    current = None
                else:
                    current['text'].append(text)
                    current['lines'].append(line['line'])
    relations = []
    for section in sections:
        text = ' '.join(section['text'])
        targets = []
        for match in re.finditer(r'\[DR:([^\]]+)\]', text):
            tokens = match.group(1).split()
            require(tokens and all(re.fullmatch(r'D\d{5}', t) for t in tokens),
                    f"{record['id']}: malformed active-form drug reference")
            targets.extend(tokens)
        require(targets, f"{record['id']}: active-form annotation lacks a resolved D reference")
        for target in sorted(set(targets)):
            relations.append({'target': target, 'annotation': MARKER + ' ' + text,
                              'comment_lines': section['lines']})
    return relations


def derive(source_dir):
    groups = parse_records(source_dir / 'DG00739.txt')
    require(set(groups) == {GROUP}, 'Group archive must contain exactly DG00739')
    group = groups[GROUP]
    require(group['kind'] == 'DGroup', 'DG00739 is not a DGroup record')
    require(primary_name(group) == 'Mycophenolic acid', 'Group name mismatch')
    require(values(group, 'TYPE') == ['Chemical'], 'Group Type is not Chemical')
    require(blocks(group, 'MEMBER'), 'Group MEMBER field unavailable')
    members = {}
    other_members = []
    for line in lines(group, 'MEMBER'):
        match = re.fullmatch(r'(DG\d{5}|D\d{5})\s+(.+)', line['text'].strip())
        require(match is not None, f"Unparsed MEMBER line {line['line']}")
        ident, name = match.groups()
        item = {'id': ident, 'name': name, 'line': line['line']}
        if ident.startswith('DG'):
            other_members.append(item)  # Direct drug scope does not recurse.
            continue
        require(ident not in members, f'Duplicate direct member {ident}')
        members[ident] = item
    drugs = parse_records(source_dir / 'D_members.txt')
    require(set(drugs) == set(members),
            'Loaded drug records differ from direct members: missing=' +
            str(sorted(set(members) - set(drugs))) + ', extra=' +
            str(sorted(set(drugs) - set(members))))
    for ident, record in drugs.items():
        require(re.fullmatch(r'D\d{5}', ident) and record['kind'] == 'Drug',
                f'{ident}: invalid drug identity')
        member_name = re.sub(r'\s+<[^>]*>\s*$', '', members[ident]['name']).strip()
        require(member_name == primary_name(record), f'{ident}: member/record name mismatch')
    inventory = {'group': {'id': GROUP, 'name': primary_name(group),
                           'type': values(group, 'TYPE')[0],
                           'member_evidence': anchor(group, 'MEMBER')},
                 'other_direct_members': other_members,
                 'loaded_drug_ids': sorted(drugs), 'members': []}
    ledger, evidence, pairs = [], [], set()
    for ident in sorted(members):
        record = drugs[ident]
        relations = own_relations(record)
        member_ref = dict(anchor(group, 'MEMBER'), member_line=members[ident]['line'])
        targets = sorted({r['target'] for r in relations})
        inventory['members'].append({'id': ident, 'name': primary_name(record),
                                     'formula': values(record, 'FORMULA'),
                                     'comment_present': bool(blocks(record, 'COMMENT')),
                                     'record_evidence': anchor(record)})
        ledger.append({'id': ident, 'decision': 'include' if targets else 'exclude',
                       'reason': 'explicit_own_active_form' if targets else
                                 'no_qualifying_comment' if blocks(record, 'COMMENT') else
                                 'comment_absent_in_complete_record',
                       'active_ids': targets, 'comment': values(record, 'COMMENT'),
                       'member_evidence': member_ref,
                       'comment_evidence': anchor(record, 'COMMENT')})
        for relation in relations:
            target = relation['target']
            # This is an evidence-availability check, not a target-membership filter.
            require(target in drugs,
                    f'{ident}: target identity record {target} unavailable in supplied archive')
            target_record = drugs[target]
            target_name = primary_name(target_record)
            pairs.add((ident, target))
            evidence.append({'pair': [ident, target], 'member_evidence': member_ref,
                             'annotation': relation['annotation'],
                             'comment_evidence': dict(anchor(record, 'COMMENT'),
                                                      relation_lines=relation['comment_lines']),
                             'target_identity': {'id': target, 'kind': target_record['kind'],
                                                 'name': target_name,
                                                 'entry_evidence': anchor(target_record, 'ENTRY'),
                                                 'name_evidence': anchor(target_record, 'NAME')}})
    ordered = sorted(pairs)
    oracle = ('PRODRUG_D|ACTIVE_D\n' + ''.join(a + '|' + b + '\n' for a, b in ordered)
              if ordered else 'NONE\n')
    checks = {'status': 'passed', 'reference_executed': True,
              'checks': ['12-column fields and continuations parsed',
                         'every loaded record terminated',
                         'group identity and Chemical type verified',
                         'complete MEMBER field enumerated without subgroup expansion',
                         'loaded drug IDs exactly equal direct member IDs',
                         'member names agree with independent Drug records',
                         'own COMMENT evaluated only after complete parsing',
                         'every emitted target has a verified Drug identity',
                         'all members have an inclusion or exclusion ledger entry',
                         'all distinct pairs emitted in two-key string order'],
              'member_count': len(members), 'loaded_drug_count': len(drugs),
              'included_member_count': sum(row['decision'] == 'include' for row in ledger),
              'pair_count': len(ordered), 'field_count': 2 * len(ordered),
              'source_stability_rechecks': 'not_performed_by_this_script',
              'independent_final_audit': 'not_performed', 'human_review': 'not_performed'}
    return {'oracle.psv': oracle, 'inventory.json': inventory,
            'inclusionledger.json': ledger, 'evidence.json': evidence,
            'executionchecks.json': checks}


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', required=True, type=Path)
    parser.add_argument('--out-dir', required=True, type=Path)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    try:
        outputs = derive(args.source_dir)
        for name, value in outputs.items():
            if name.endswith('.psv'):
                (args.out_dir / name).write_text(value, encoding='utf-8')
            else:
                write_json(args.out_dir / name, value)
    except (OSError, ValueError) as exc:
        # Remove this program's result artifacts so a prior oracle cannot look current.
        for name in OUTPUTS:
            path = args.out_dir / name
            if path.is_file():
                path.unlink()
        failure = {'status': 'unresolved', 'reference_executed': True,
                   'error': str(exc), 'oracle_emitted': False}
        write_json(args.out_dir / 'executionchecks.json', failure)
        print(json.dumps(failure), file=sys.stderr)
        return 2
    checks = outputs['executionchecks.json']
    print(json.dumps({key: checks[key] for key in
                      ('status', 'member_count', 'pair_count', 'field_count')}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
