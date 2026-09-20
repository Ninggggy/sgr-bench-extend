"""Independent pre-A finite-cohort audit; reads original API JSON only.

No constructor annotations, reference program, or expected oracle are inputs.
All 130 assay descriptions were also inspected by the reviewer, including all
30 UNCHECKED registrations (26 GABA/BZD and four UGT records).
"""
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
RAW = BASE / 'sources/raw'

def original(name, rows=None, key=None):
    doc = json.loads((RAW / name).read_text())
    if rows:
        data = doc[rows]
        assert doc['page_meta']['total_count'] == len(data)
        assert doc['page_meta']['offset'] == 0 and doc['page_meta']['next'] is None
        assert len({r[key] for r in data}) == len(data)
        return data
    return doc

def kinds(text):
    return sorted(set(a + b for a, b in re.findall(r'(alpha|beta|gamma)[ -]?(\d+)', text.lower())))

def audit(refresh=False):
    activities = original('07_activities_refresh.json' if refresh else '01_activities.json', 'activities', 'activity_id')
    assays = original('09_assays_refresh.json' if refresh else '03_assays.json', 'assays', 'assay_chembl_id')
    targets = original('08_targets_refresh.json' if refresh else '02_targets.json', 'targets', 'target_chembl_id')
    compounds = original('10_exact_diazepam_identity.json', 'molecules', 'molecule_chembl_id')
    assert len(compounds) == 1 and compounds[0]['pref_name'].lower() == 'diazepam'
    cid = compounds[0]['molecule_chembl_id']
    source = original('04_source.json')
    assert source['src_description'] == 'Scientific Literature'
    for a in activities:
        assert (a['molecule_chembl_id'], a['assay_type'], a['standard_type'], a['standard_units'], a['standard_relation']) == (cid, 'B', 'Ki', 'nM', '=')
    scoped = [a for a in activities if a['src_id'] == source['src_id']]
    sb = {a['assay_chembl_id']: a for a in assays}
    tb = {t['target_chembl_id']: t for t in targets}
    assert set(sb) == {a['assay_chembl_id'] for a in scoped}
    assert set(tb) == {a['target_chembl_id'] for a in scoped}
    doc = original('06_cbr_document.json')
    assert 'central benzodiazepine receptor (CBR)' in doc['abstract']
    counts, rows, conflicts = Counter(), [], []
    for a in sorted(scoped, key=lambda a: a['activity_id']):
        s, t = sb[a['assay_chembl_id']], tb[a['target_chembl_id']]
        assert a['assay_description'] == s['description']
        assert a['target_chembl_id'] == s['target_chembl_id']
        assert a['document_chembl_id'] == s['document_chembl_id']
        typ, comps, txt = t['target_type'], t['target_components'], s['description']
        is_gaba = bool(comps) and all(c['component_description'].startswith('Gamma-aminobutyric acid receptor subunit ') for c in comps)
        if is_gaba and typ == 'PROTEIN COMPLEX':
            assert {c['relationship'] for c in comps} == {'PROTEIN SUBUNIT'}
            assert s['relationship_type'] in ('D', 'H')
            category = {'D': 'DIRECT_COMPLEX', 'H': 'HOMOLOGOUS_COMPLEX'}[s['relationship_type']]
        elif is_gaba and typ == 'PROTEIN COMPLEX GROUP':
            assert {c['relationship'] for c in comps} == {'GROUP MEMBER'}
            category = 'COMPLEX_GROUP'
        elif is_gaba and typ == 'SINGLE PROTEIN':
            assert len(comps) == 1 and comps[0]['relationship'] == 'SINGLE PROTEIN'
            category = 'GABA_SUBUNIT'
        elif typ == 'SINGLE PROTEIN' and t['pref_name'] == 'Translocator protein':
            category = 'TSPO'
        elif typ == 'UNCHECKED':
            if re.search(r'GABA|benzodiazepine|\bBZD\b', txt, re.I):
                category = 'UNCURATED_GABA_BZD'
            elif re.search(r'\bCBR\b', txt):
                assert a['document_chembl_id'] == doc['document_chembl_id']
                assert 'from CBR at ' in txt
                category = 'UNCURATED_GABA_BZD'
            else:
                assert 'glucuronidation by human UGT enzymes' in txt
                category = 'OTHER'
        else:
            category = 'OTHER'
        # Every engineering occurrence in this actual cohort directly modifies
        # the receptor bound in the assay; no control/background mention occurs.
        engineered = bool(re.search(r'affinity (?:for mutant|to rat chimeric)', txt, re.I))
        assert engineered == bool(re.search(r'mutant|chimer|mutation|mutated', txt, re.I))
        counts[category] += 1
        registered = kinds(' '.join(c['component_description'] for c in comps)) if is_gaba else []
        described = kinds(txt)
        ambiguous = bool(re.search(r'(alpha|beta|gamma)[ -]?\d+/\d+|chimer', txt, re.I))
        conflict = typ == 'PROTEIN COMPLEX' and is_gaba and len(described) == 3 and not ambiguous and described != registered
        if conflict:
            # Explicit receptor-modifying origins in the actual conflict rows;
            # expression-host and assay_organism fields are not used.
            m = re.search(r'\b(human|rat) (?:recombinant )?GABA', txt)
            species = {'human': 'Homo sapiens', 'rat': 'Rattus norvegicus'}[m[1]] if m else 'UNKNOWN'
            finding = species + ' ' + '/'.join(described) + ' -> ' + t['organism'] + ' ' + '/'.join(registered)
            conflicts.append([str(a['activity_id']), finding])
        rows.append({'activity_id': a['activity_id'], 'assay_id': a['assay_chembl_id'], 'target_id': a['target_chembl_id'], 'document_id': a['document_chembl_id'], 'category': category, 'target_type': typ, 'assay_relationship': s['relationship_type'], 'description': txt, 'registered_component_relationships': [c['relationship'] for c in comps], 'registered_subunits': registered, 'described_subunits': described, 'ambiguous_composition': ambiguous, 'engineered': engineered, 'conflict': bool(conflict)})
    order = ['DIRECT_COMPLEX', 'HOMOLOGOUS_COMPLEX', 'COMPLEX_GROUP', 'GABA_SUBUNIT', 'TSPO', 'UNCURATED_GABA_BZD', 'OTHER']
    answer = [[c, str(counts[c])] for c in order] + [['ENGINEERED_VARIANT', str(sum(r['engineered'] for r in rows))]] + conflicts
    psv = 'ITEM|FINDING\n' + ''.join('|'.join(r) + '\n' for r in answer)
    report = {'compound': cid, 'raw_activity_count': len(activities), 'scope_count': len(scoped), 'distinct_assays': len(sb), 'distinct_targets': len(tb), 'category_counts': dict(counts), 'unchecked_registration_count': sum(r['target_type'] == 'UNCHECKED' for r in rows), 'engineered_ids': [r['activity_id'] for r in rows if r['engineered']], 'conflicts': conflicts, 'excluded_source_ids': [a['activity_id'] for a in activities if a not in scoped], 'activity_has_relationship_field': any('relationship_type' in a for a in activities), 'all_rows': rows}
    return report, psv

if __name__ == '__main__':
    first, psv = audit()
    second, second_psv = audit(True)
    assert first == second and psv == second_psv
    equality = {}
    for x, y in [('01_activities.json', '07_activities_refresh.json'), ('02_targets.json', '08_targets_refresh.json'), ('03_assays.json', '09_assays_refresh.json')]:
        equality[x] = original(x) == original(y)
    first['full_source_json_equal_to_refresh'] = equality
    (HERE / 'recomputed.json').write_text(json.dumps(first, indent=2, ensure_ascii=False) + '\n')
    (HERE / 'recomputed.psv').write_text(psv)
    # Comparison occurs only after independent derivation.
    first['constructor_oracle_matches'] = psv == (BASE / 'oracle.psv').read_text()
    summary = {k: v for k, v in first.items() if k != 'all_rows'}
    (HERE / 'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(summary, ensure_ascii=False))
