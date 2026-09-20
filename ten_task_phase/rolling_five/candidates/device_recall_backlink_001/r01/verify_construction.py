"""Offline artifact/schema/scorer compatibility checks; no solver invocation."""
from pathlib import Path
import importlib.util,json,subprocess,sys
from datetime import datetime,timezone
sys.dont_write_bytecode=True
C=Path(__file__).resolve().parent
ROOT=next(p for p in C.parents if (p/'construction_pipeline/scripts/prepare.py').is_file())
RUNTIME=ROOT/'construction_pipeline/ten_task_phase/runtime'
sys.path.insert(0,str(RUNTIME))
from stage_results import validate
from score import parse,score
import reference

def put(name,value):
 (C/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

candidate=json.loads((C/'candidate.json').read_text())
schema=json.loads((ROOT/'construction_pipeline/schemas/candidate.schema.json').read_text())
validate(candidate,schema)
(C/'candidate.schema.json').write_text(json.dumps(schema,ensure_ascii=False,indent=2)+'\n')
checks={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Offline constructor verification; no model test or independent human/content review','complete_candidate_schema':{'status':'passed','validator':'runtime/stage_results.validate; every keyword in the existing candidate.schema.json supported','schema_copy':'candidate.schema.json'}}
public={k:json.loads((C/(k+'.json')).read_text()) for k in ['cg','go']}
assert candidate['public']==public
assert all(set(p)=={'instruction','output_format'} for p in public.values())
assert public['cg']['output_format']==public['go']['output_format']
alignment=json.loads((C/'pair_alignment.json').read_text())
for p in alignment['predicates']:
 for v in ['cg','go']: assert p[v+'_quote'] in public[v]['instruction']
for text in [json.dumps(p) for p in public.values()]:
 assert all(forbidden not in text for forbidden in ['K050369','K081137','123823','accessdata.fda.gov','da Vinci','34 results','seven results'])
checks['public_pair']={'exact_two_keys':True,'same_output_format':True,'candidate_pair_equal':True,'alignment_quotes_present':True,'no_discovered_ids_or_website_or_brand':True}
reference.build(C,C/'rebuilt')
assert (C/'oracle.psv').read_bytes()==(C/'rebuilt/oracle.psv').read_bytes()
manifest=json.loads((C/'source_manifest.json').read_text())
provenance=[]
for item in manifest['sources']:
 raw=(C/item['raw_response_file']).read_text().split('--------------------------------------------------------------------------------')[item['raw_response_segment']].strip()
 assert (C/item['file']).read_text().strip()==raw
 provenance.append({'id':item['id'],'raw_segment_equal':True})
checks['source_provenance']=provenance
inv=json.loads((C/'inventory.json').read_text())
checks['reference']={'status':'passed','all_applications_from_source':True,'rows':len(inv['applications']),'view_rows':sum(x['announced_total'] for x in inv['applications']),'exact_targets_for_absent':True,'positive_exact_witness':True,'no_hardcoded_final_mapping':'Reference joins source IDs, discovered registrations, actual view links and resolved target IDs.'}
root_before=reference.source_identity(reference.parsed_capture(next(x for x in manifest['sources'] if x['id']==manifest['root_source']),C))
latest=[reference.parsed_capture(x,C) for x in manifest['sources'] if x['role']=='refresh']
root_latest=reference.source_identity(latest[0]);assert root_before==root_latest
checks['refresh']={'root_required_identity_equal':True,'K050369_recheck_returned_rows':len(reference.row_links(latest[1])),'K081137_recheck_returned_rows':len(reference.row_links(latest[2])),'K081137_latest_full_table_verified':False,'limitation':'K081137 title-only response is not a full refresh; earlier complete repeated view is reference. K050369 only first page rechecked. Future evaluation needs relevant current-source verification.'}
prior=[reference.parsed_capture(x,C) for x in manifest['sources'] if x['role']=='prior_observation']
negative=next(x for x in inv['applications'] if len(x['rows'])==7)
prior_rows=reference.row_links(prior[1])
assert len(prior_rows)==len(negative['rows'])
assert all(all(a[k]==b[k] for k in ['display_description','display_class','display_posted']) for a,b in zip(prior_rows,negative['rows']))
checks['refresh']['prior_complete_seven_row_view_equal']=True
checks['refresh']['prior_complete_source_ref']=prior[1]['id']
rules=json.loads((C/'rules.json').read_text());gold=(C/'oracle.psv').read_text();g=parse(gold,rules['columns'])
fixtures={'ordinary_both_correct':gold,'absent_wrongly_inferred_present':gold.replace('|ABSENT','|PRESENT'),'positive_wrongly_absent':gold.replace('|PRESENT','|ABSENT'),'drop_boundary_row':'\n'.join(gold.splitlines()[:-1])+'\n','reverse_order':'\n'.join([gold.splitlines()[0],*reversed(gold.splitlines()[1:])])+'\n'}
fixture_results={}
(C/'scorer_witnesses').mkdir(exist_ok=True)
for name,answer in fixtures.items():
 (C/'scorer_witnesses'/f'{name}.psv').write_text(answer)
 result=score(g,parse(answer,rules['columns']),rules)
 fixture_results[name]={k:result[k] for k in ['status','metrics','counts']}
assert fixture_results['ordinary_both_correct']['metrics']=={'Item-F1':1.0,'Row-F1':1.0,'P.O.A.':1.0}
assert fixture_results['absent_wrongly_inferred_present']['metrics']['Row-F1']==0.5
assert fixture_results['positive_wrongly_absent']['metrics']['Row-F1']==0.5
assert fixture_results['reverse_order']['metrics']['P.O.A.']==0.0
checks['scorer_compatibility']={'entry_point':'construction_pipeline/ten_task_phase/runtime/score.py','purpose':'Ordinary and boundary label handling and two-row order only; deliberately altered gold fixtures are not model measurements','fixtures':fixture_results,'UNRESOLVED':'Readable output token is allowed. Actual source/infrastructure failure invalidates capability interpretation and must be handled before scoring; this scorer alone cannot diagnose tool failures.'}
put('execution_checks.json',checks)
cmd=[sys.executable,str(ROOT/'construction_pipeline/scripts/prepare.py'),'validate-candidate','--candidate',str(C/'candidate.json'),'--check-files']
r=subprocess.run(cmd,text=True,capture_output=True)
checks['prepare_validation']={'status':'passed' if r.returncode==0 else 'failed','exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
assert r.returncode==0,r.stderr
checks['model_tests']=0;checks['human_validation']='not_performed';checks['difficulty']='untested'
put('execution_checks.json',checks)
print(json.dumps({'schema':'passed','prepare':'passed','reference':'passed','scorer_compatibility':'passed','source_captures':len(provenance),'model_tests':0}))
