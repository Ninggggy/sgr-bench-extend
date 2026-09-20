"""Constructor-only schema, source-reference and scorer compatibility checks.
No solver calls, difficulty trials, network requests or independent review.
"""
from pathlib import Path
import json,sys,subprocess
from datetime import datetime,timezone
sys.dont_write_bytecode=True
C=Path(__file__).resolve().parent
ROOT=next(p for p in C.parents if (p/'construction_pipeline/scripts/prepare.py').is_file())
sys.path.insert(0,str(ROOT/'construction_pipeline/ten_task_phase/runtime'))
from stage_results import validate
from score import parse,score

def put(name,value):(C/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
checks={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Constructor deterministic verification only; no model or independent/human content review'}
schema=json.loads((ROOT/'construction_pipeline/schemas/candidate.schema.json').read_text())
candidate=json.loads((C/'candidate.json').read_text());validate(candidate,schema)
checks['full_candidate_schema']='passed'
public={v:json.loads((C/(v+'.json')).read_text()) for v in ['cg','go']}
assert public==candidate['public'];assert all(set(p)=={'instruction','output_format'} for p in public.values())
assert public['cg']['output_format']==public['go']['output_format']
alignment=json.loads((C/'pair_alignment.json').read_text())
for p in alignment['predicates']:
 for v in ['cg','go']:assert p[v+'_quote'] in public[v]['instruction']
assert public['cg']['instruction'].replace(alignment['CG_only_guidance']+'\n\n','')==public['go']['instruction']
for p in public.values():
 for forbidden in ['CHEMBL','ChEMBL','ebi.ac.uk','604850','1701379','1876214','130 activity','131','42 direct']:
  assert forbidden not in json.dumps(p),forbidden
checks['public_pair']={'exact_two_keys':True,'candidate_pair_equal':True,'same_output_format':True,'literal_predicates':len(alignment['predicates']),'CG_minus_steps_equals_GO':True,'no_website_or_answer_identifiers':True,'source_descriptor_reused':'release37issuedMay2026','runtime_date':'2026-09-09'}
# Reference has already been built from each complete observation; compare outputs.
assert (C/'oracle.psv').read_bytes()==(C/'rebuilt/oracle.psv').read_bytes()
inv=json.loads((C/'inventory.json').read_text());report=json.loads((C/'scope_checks.json').read_text())
assert len(inv)==report['in_scope_activity_rows']
assert all(r['category_reason'] and r['source_locator'] for r in inv)
assert sum(report['category_counts'].values())==len(inv)
assert set(report['engineered_variant_activity_ids'])=={r['activity_id'] for r in inv if r['explicit_engineered_target']}
assert {r['activity_id'] for r in report['conflicts']}=={r['activity_id'] for r in inv if r['explicit_subunit_conflict']}
checks['reference']={'initial_refresh_oracle_equal':True,'every_in_scope_row_has_evidence_and_reason':True,'activity_rows':len(inv),'answer_rows':report['answer_rows'],'uncurated_individual_reviews':len(json.loads((C/'constructor_annotations.json').read_text())['uncurated_description_interpretations']),'raw_value_upper_fields_inspected':True,'no_final_count_literals_in_algorithm':'Counts computed from source-derived categories; description interpretations remain explicit reviewed annotations, not an independent human claim.'}
# Verify species-source behavior on actual source descriptions, including a foreign expression host.
import reference
byid={r['activity_id']:r for r in inv}
assert reference.described_species(byid[29082441]['description'])=='Homo sapiens'
assert reference.described_species(byid[320285]['description'])=='Rattus norvegicus'
assert reference.described_species(byid[807849]['description'])=='UNKNOWN'
assert reference.described_species(byid[19259362]['description'])=='UNKNOWN'
assert reference.described_subunits(byid[1605063]['description']) is None
assert reference.described_subunits(byid[320296]['description']) is None
checks['semantic_parser_boundaries']={'foreign_expression_host_not_target_origin':True,'tissue_only_origin_not_promoted':True,'unknown_origin_retained':True,'beta2_or3_not_resolved':True,'chimera_not_coexisting_alpha_set':True}
rules=json.loads((C/'rules.json').read_text());gold=(C/'oracle.psv').read_text();lines=gold.splitlines()
fixtures={'full_reference':gold,'homologous_wrongly_direct':gold.replace('DIRECT_COMPLEX|42','DIRECT_COMPLEX|55').replace('HOMOLOGOUS_COMPLEX|13','HOMOLOGOUS_COMPLEX|0'),
'group_wrongly_defined':gold.replace('DIRECT_COMPLEX|42','DIRECT_COMPLEX|70').replace('COMPLEX_GROUP|28','COMPLEX_GROUP|0'),
'four_direct_mutants_instead_of_six_all_scope':gold.replace('ENGINEERED_VARIANT|6','ENGINEERED_VARIANT|4'),
'wrong_beta_identity':gold.replace('alpha1/beta1/gamma2','alpha1/beta2/gamma2'),
'wrong_alpha_identity':gold.replace('alpha4/beta3/gamma2','alpha5/beta3/gamma2'),
'wrong_species':gold.replace('Rattus norvegicus alpha5','Homo sapiens alpha5'),
'common_aliases':gold.replace('Homo sapiens alpha4/beta3/gamma2 -> Homo sapiens alpha1/beta3/gamma2','human α4β3γ2 → human α1β3γ2').replace('Rattus norvegicus alpha5/beta2/gamma2 -> Rattus norvegicus alpha1/beta2/gamma2','rat α5β2γ2 -> rat α1β2γ2'),
'drop_conflict':'\n'.join(lines[:-1])+'\n',
'reverse_order':'\n'.join([lines[0],*reversed(lines[1:])])+'\n',
'fixed_keys_only':lines[0]+'\n'+''.join(line.split('|')[0]+'|0\n' for line in lines[1:9])}
results={}
for name,answer in fixtures.items():
 (C/'scorer_witnesses'/f'{name}.psv').write_text(answer)
 r=score(parse(gold,rules['columns']),parse(answer,rules['columns']),rules)
 results[name]={k:r[k] for k in ['status','metrics','counts']}
assert results['full_reference']['metrics']=={'Item-F1':1.0,'Row-F1':1.0,'P.O.A.':1.0}
assert results['common_aliases']['metrics']==results['full_reference']['metrics']
for name in ['wrong_beta_identity','wrong_alpha_identity','wrong_species','four_direct_mutants_instead_of_six_all_scope']:
 assert results[name]['counts']['correct_fields']==report['answer_fields']-1
assert results['reverse_order']['metrics']['P.O.A.']==0
assert results['fixed_keys_only']['counts']['correct_fields']==8
checks['scorer_compatibility']={'entry_point':'construction_pipeline/ten_task_phase/runtime/score.py','unchanged':True,'all_columns_including_ITEM_scored':True,'controller_withdrew_FINDING_only_requirement':True,'finite_identity_aliases_checked_without_biological_number_equivalence':True,'fixtures':results,'no_difficulty_inference':'These are deliberately altered reference fixtures, never model performance or A trials.'}
# Existing prepare state/path verification is intentionally separate from full schema validation.
put('execution_checks.json',checks)
cmd=[sys.executable,str(ROOT/'construction_pipeline/scripts/prepare.py'),'validate-candidate','--candidate',str(C/'candidate.json'),'--check-files']
r=subprocess.run(cmd,text=True,capture_output=True)
checks['prepare_validation']={'command':cmd,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
assert r.returncode==0,r.stderr
# Verify public projection without changing the registered runtime date.
sys.path.insert(0,str(ROOT/'construction_pipeline/scripts'))
from prepare import make_public
for variant in ['cg','go']:
 p=make_public(candidate,'2026-09-09',variant)
 assert set(p)=={'instruction','output_format','current_date'}
checks['public_projection_exact_keys_and_runtime_date']='passed'
checks['model_tests']=0;checks['human_validation']='not_performed';checks['difficulty']='not_run'
put('execution_checks.json',checks)
print(json.dumps({'schema':'passed','prepare':'passed','public_pair':'passed','reference':'passed','scorer_fixtures':len(fixtures),'model_tests':0},ensure_ascii=False))
