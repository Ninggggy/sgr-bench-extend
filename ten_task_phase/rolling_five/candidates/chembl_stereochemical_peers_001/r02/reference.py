#!/usr/bin/env python3
"""Recompute the finite quinine structure inventory from preserved API JSON.

Standard library only; no network access and no embedded answer rows.
Run: python reference.py --out-dir recomputed
An alternate --manifest may be supplied for a later source observation.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlparse


def require(condition, message):
    if not condition:
        raise ValueError(message)


def complete_page(data, label):
    rows, meta = data['molecules'], data['page_meta']
    require(meta['next'] is None and meta['offset'] == 0,
            label + ': incomplete pagination')
    require(len(rows) == meta['total_count'], label + ': count mismatch')
    ids = [row['molecule_chembl_id'] for row in rows]
    require(len(ids) == len(set(ids)), label + ': repeated record identity')
    return rows


def layers(inchi):
    require(isinstance(inchi, str) and inchi.startswith('InChI=1S/'),
            'Expected a complete Standard InChI')
    parts = inchi.split('/')
    result = {'formula': parts[1]}
    # Basic non-isotopic layers only. Do not confuse an isotopic /t with
    # the non-isotopic carbon-centre stereochemistry used by this task.
    for part in parts[2:]:
        if part[0] in 'ifr':
            break
        require(part[0] not in result, 'Repeated non-isotopic InChI layer')
        result[part[0]] = part[1:]
    return result


def basic(inchi):
    info = layers(inchi)
    return tuple(info.get(k, '') for k in ('formula', 'c', 'h', 'q', 'p'))


def single_component(row):
    st = row.get('molecule_structures') or {}
    smiles, inchi = st.get('canonical_smiles'), st.get('standard_inchi')
    require(bool(smiles) and bool(inchi),
            row['molecule_chembl_id'] + ': missing structure evidence')
    by_smiles = '.' not in smiles
    by_formula = '.' not in layers(inchi)['formula']
    require(by_smiles == by_formula, 'Component representations disagree')
    return by_smiles


def tetra(info):
    if not info.get('t'):
        return {}
    result = {}
    for token in info['t'].split(','):
        match = re.fullmatch(r'(\d+)([+?u-])', token)
        require(match is not None, 'Unsupported tetrahedral token: ' + token)
        index, parity = int(match[1]), match[2]
        require(index not in result, 'Duplicate tetrahedral atom')
        result[index] = parity
    return result


def classification(row, centres):
    st = row['molecule_structures']
    info = layers(st['standard_inchi'])
    markers = tetra(info)
    require(set(markers) <= centres, 'Unexpected non-isotopic tetrahedral atom')
    specified = sorted(i for i in centres if markers.get(i) in ('+', '-'))
    # Every observed specified structure uses the absolute /s1 mode.
    # Relative/racemic modes require scientific review, not silent grading.
    require(not specified or (info.get('s') == '1' and info.get('m') in ('0', '1')),
            'Unsupported stereo mode requires review')
    carbon_tags = len(re.findall(r'\[C@{1,2}H?\]', st['canonical_smiles']))
    require(carbon_tags == len(specified), 'SMILES carbon tags disagree with InChI')
    status = ('UNSPECIFIED' if not specified else
              'FULL' if len(specified) == len(centres) else 'PARTIAL')
    return status, specified, markers


def run(manifest_path, out_dir):
    manifest = json.loads(manifest_path.read_text())
    entries = {e['role']: e for e in manifest['sources'] if 'role' in e}
    raw = {role: json.loads((manifest_path.parent / e['path']).read_text())
           for role, e in entries.items()}
    require(raw['version_before']['chembl_db_version'] == manifest['source_release'],
            'Unexpected source release')
    require(raw['version_before'] == raw['version_after'], 'Version observation changed')
    require(raw['exact_name'] == raw['exact_name_repeat'], 'Identity observation changed')
    require(raw['prefix'] == raw['prefix_repeat'], 'Structure observation changed')
    exact = complete_page(raw['exact_name'], 'exact name')
    require(len(exact) == 1 and exact[0]['pref_name'].casefold() == 'quinine',
            'Quinine identity is not unique')
    seed = exact[0]
    st = seed['molecule_structures']
    prefix = st['standard_inchi_key'].split('-')[0]
    require(re.fullmatch('[A-Z]{14}', prefix) is not None, 'Invalid first key block')
    require(parse_qs(urlparse(entries['prefix']['url']).query).get(
        'molecule_structures__standard_inchi_key__startswith') == [prefix],
        'Saved query does not use the discovered structure key')
    require(parse_qs(urlparse(entries['connectivity']['url']).query).get(
        'molecule_structures__canonical_smiles__connectivity') == [st['canonical_smiles']],
        'Connectivity query does not use the discovered seed SMILES')
    base = basic(st['standard_inchi'])
    centres = set(tetra(layers(st['standard_inchi'])))
    carbon_count = int(re.match(r'C(\d+)', base[0])[1])
    require(len(centres) == 4 and all(1 <= i <= carbon_count for i in centres),
            'Seed must specify four carbon stereocentres')
    prefix_rows = complete_page(raw['prefix'], 'structure prefix')
    require(all(m['molecule_structures']['standard_inchi_key'].split('-')[0] == prefix
                for m in prefix_rows), 'Prefix response contains another key block')
    require(all(single_component(m) and basic(m['molecule_structures']['standard_inchi']) == base
                for m in prefix_rows), 'Key-prefix hit does not match actual basic layers')
    connected = complete_page(raw['connectivity'], 'connectivity')
    connected_single = [m for m in connected if single_component(m)]
    prefix_ids = {m['molecule_chembl_id'] for m in prefix_rows}
    require(prefix_ids == {m['molecule_chembl_id'] for m in connected_single},
            'Independent connectivity enumeration differs')
    by_id = {m['molecule_chembl_id']: m for m in connected_single}
    for m in prefix_rows:
        require(m['molecule_structures'] == by_id[m['molecule_chembl_id']]['molecule_structures'],
                'Structure evidence differs between independent queries')
    require(seed['molecule_chembl_id'] in prefix_ids, 'Seed omitted')
    inventory = []
    for m in sorted(prefix_rows, key=lambda row: int(row['molecule_chembl_id'][6:])):
        status, specified, markers = classification(m, centres)
        inventory.append({'chembl_id': m['molecule_chembl_id'], 'stereo_status': status,
                          'specified_carbon_centres': specified,
                          'tetrahedral_markers': markers,
                          'pref_name': m['pref_name'],
                          'molecule_hierarchy': m['molecule_hierarchy'],
                          'drug_chirality_not_used': m['chirality'],
                          'structure': {key: m['molecule_structures'][key] for key in
                                        ('standard_inchi', 'standard_inchi_key', 'canonical_smiles')},
                          'source_id': entries['prefix']['source_id']})
    name_rows = complete_page(raw['name_search'], 'name search')
    names = {m['molecule_chembl_id'] for m in name_rows}
    virtual = {m['molecule_chembl_id'] for m in prefix_rows if m['molecule_hierarchy'] is None}
    witnesses = [{'child': m['molecule_chembl_id'],
                  'parent': m['molecule_hierarchy']['parent_chembl_id']}
                 for m in connected if m.get('molecule_hierarchy') and
                 m['molecule_hierarchy'].get('parent_chembl_id') in virtual]
    exclusions = [{'chembl_id': m['molecule_chembl_id'], 'reason': 'multicomponent',
                   'molecule_hierarchy': m['molecule_hierarchy'],
                   'standard_inchi': m['molecule_structures']['standard_inchi'],
                   'canonical_smiles': m['molecule_structures']['canonical_smiles']}
                  for m in connected if not single_component(m)]
    report = {'source_release': manifest['source_release'],
              'seed_id': seed['molecule_chembl_id'], 'derived_key_prefix': prefix,
              'basic_layers': dict(zip(('formula', 'c', 'h', 'q', 'p'), base)),
              'carbon_centres': sorted(centres), 'rows': len(inventory),
              'status_counts': dict(Counter(r['stereo_status'] for r in inventory)),
              'connectivity_rows': len(connected), 'excluded_multicomponent': exclusions,
              'name_search_rows': len(name_rows),
              'name_search_overlap': sorted(prefix_ids & names),
              'name_search_missing': sorted(prefix_ids - names),
              'virtual_parent_ids': sorted(virtual), 'virtual_parent_witnesses': witnesses,
              'default_page_overlap': sorted(prefix_ids & {
                  m['molecule_chembl_id'] for m in raw['default_page']['molecules']}),
              'version_and_repeated_responses_equal': True,
              'independent_connectivity_set_equal': True}
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'oracle.txt').write_text('REGISTERED_ID|STEREO_STATUS\n' + ''.join(
        r['chembl_id'] + '|' + r['stereo_status'] + '\n' for r in inventory))
    (out_dir / 'inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')
    (out_dir / 'scope_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('rows', 'status_counts', 'carbon_centres',
                     'connectivity_rows', 'independent_connectivity_set_equal')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path,
                        default=Path(__file__).with_name('source_manifest.json'))
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    run(args.manifest.resolve(), args.out_dir.resolve())
