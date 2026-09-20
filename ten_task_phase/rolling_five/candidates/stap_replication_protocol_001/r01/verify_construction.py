"""Deterministic constructor checks only; no model tests or independent review."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,subprocess,tempfile,xml.etree.ElementTree as ET
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent
ROOT=next(p for p in B.parents if (p/'construction_pipeline/scripts/prepare.py').is_file())
sys.path.insert(0,str(ROOT/'construction_pipeline/ten_task_phase/runtime'))
from stage_results import validate
sys.path.insert(0,str(ROOT/'construction_pipeline/ten_task_phase/protocol/ten-task-v1'))
from score import parse,score
import reference

def load(p):return json.loads(p.read_text())
def put(n,x):p=B/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
c=load(B/'candidate.json');validate(c,load(ROOT/'construction_pipeline/schemas/candidate.schema.json'))
pair={v:load(B/(v+'.json')) for v in ['cg','go']};assert pair==c['public'];assert all(set(p)=={'instruction','output_format'} for p in pair.values());assert pair['cg']['output_format']==pair['go']['output_format']
a=load(B/'pair_alignment.json')
for p in a['predicates']:
 for v in ['cg','go']:assert p[v+'_quote'] in pair[v]['instruction']
assert pair['cg']['instruction'].replace(a['CG_only_guidance']+'\n\n','')==pair['go']['instruction']
for p in pair.values():
 for forbidden in ['Europe PMC','EuropePMC','europepmc.org','ebi.ac.uk','24476887','24990753','25075303','27292224','27610221','49','three studies']:
  assert forbidden not in json.dumps(p),forbidden
report1=reference.run(B,B/'rebuilt','initial');report2=reference.run(B,B/'rebuilt_refresh','refresh');assert report1==report2
assert (B/'oracle.psv').read_bytes()==(B/'rebuilt/oracle.psv').read_bytes()==(B/'rebuilt_refresh/oracle.psv').read_bytes()
m=load(B/'source_manifest.json');a=load(B/m['cohort']);z=load(B/'sources/raw/cohort_refresh.response')
assert {x['id']:x for x in a['resultList']['result']}=={x['id']:x for x in z['resultList']['result']}
text_checks={}
for pmc,path in m['fulltexts'].items():
 original=B/path;refresh=B/'sources/raw'/(pmc+'_refresh.response')
 text_checks[pmc]={'bytes_equal':original.read_bytes()==refresh.read_bytes(),'main_paragraphs_equal':reference.main_paragraphs(original)[1]==reference.main_paragraphs(refresh)[1]}
 assert text_checks[pmc]['main_paragraphs_equal']
# Genuine source boundary and namespace parser checks. All bodies would mix reviews.
root,ps=reference.main_paragraphs(B/m['fulltexts']['PMC4995676']);all_ps=[' '.join(''.join(e.itertext()).split()) for body in root.findall('.//body') for e in body.iter('p')]
assert len(ps)==31 and len(all_ps)==86
assert '1,051' in ps[12] and '591' in ps[12]
assert any('1154' in p and '671' in p for p in reference.main_paragraphs(B/m['fulltexts']['PMC4904271'])[1])
# Namespace injection changes the XML representation, not the scientific text.
fixture=B/'scorer_witnesses/namespaced_article.xml';synthetic='<article xmlns="urn:fixture"><body><p>Own main result.</p></body><sub-article><body><p>Reviewer suggestion.</p></body></sub-article></article>';fixture.write_text(synthetic)
assert reference.main_paragraphs(fixture)[1]==['Own main result.']
som=reference.main_paragraphs(B/m['fulltexts']['PMC4908587'])[1];assert '7 days' in som[15] and '6.5' in som[15];assert not next(x for x in load(B/'eligibility_annotations.json') if x['pmcid']=='PMC4908587')['included']
gold=(B/'oracle.psv').read_text();lines=gold.splitlines();rules=load(B/'rules.json')
equivalent=[lines[0]]
for line in lines[1:]:
 cells=line.split('|');cells[1]=','.join(reversed(cells[1].lower().split(';')));cells[2]=cells[2].lower();cells[3]=' '.join(reversed(cells[3].lower().split(';')));equivalent.append('|'.join(cells))
fixtures={'reference':gold,'case_and_set_order':'\n'.join(equivalent)+'\n','drop_study':'\n'.join(lines[:-1])+'\n','omit_atp':gold.replace('ATP;CD45_UNSORTED;FGF2;HCL','CD45_UNSORTED;FGF2;HCL',1),'markers_mistaken_for_function':gold.replace('PLURIPOTENCY_NOT_ESTABLISHED','PLURIPOTENCY_ESTABLISHED',1),'unperformed_mistaken_for_negative':gold.replace('TERATOMA_NOT_PERFORMED','TERATOMA_NEGATIVE'),'reported_mistaken_for_unperformed':gold.replace('TERATOMA_NOT_REPORTED','TERATOMA_NOT_PERFORMED',1),'miss_rare_markers':gold.replace('RARE_POSITIVE','NEGATIVE',1),'reverse_rows':'\n'.join([lines[0],*reversed(lines[1:])])+'\n'}
scores={}
for name,text in fixtures.items():
 (B/'scorer_witnesses'/(name+'.psv')).write_text(text);r=score(parse(gold,rules['columns']),parse(text,rules['columns']),rules);scores[name]={k:r[k] for k in ['status','metrics','counts']}
assert scores['reference']['metrics']=={'Item-F1':1.0,'Row-F1':1.0,'P.O.A.':1.0}
assert scores['case_and_set_order']['metrics']==scores['reference']['metrics']
for n in ['omit_atp','markers_mistaken_for_function','unperformed_mistaken_for_negative','reported_mistaken_for_unperformed','miss_rare_markers']:assert scores[n]['counts']['correct_fields']==11,n
assert scores['drop_study']['counts']['correct_fields']==8
assert scores['reverse_rows']['metrics']['P.O.A.']==0
put('scorer_witnesses/results.json',{'scorer':'construction_pipeline/ten_task_phase/protocol/ten-task-v1/score.py','unchanged':True,'all_columns_including_pmid_scored':True,'synthetic_not_model_outputs':True,'results':scores})
requests=[json.loads(x) for x in (B/'sources/request_index.jsonl').read_text().splitlines()]
end=max(r['finished_at_utc'] for r in requests if r['label'].endswith('_refresh'))
put('source_stability.json',{'checked_at_utc':datetime.now(timezone.utc).isoformat(),'initial_cohort_utc':'2026-09-13T06:25:10.785712+00:00','final_refresh_utc':end,'complete_core_all_fields_equal':True,'cohort_records':49,'all_decisive_fulltext_checks':text_checks,'recomputed_outputs_equal':True,'scope_of_claim':'Only these observed construction endpoints; no perpetual stability claim.','future_run_plan':'Immediately before and after each model trial, repeat the complete original-seed citing/OA core query and all 16 main texts supporting eligibility or required fields. Compare the entire PMID/PMCID cohort and core records plus main-article identity/version and paragraphs. A new/removed record or changed relevant text requires fresh scientific adjudication and an explicit stability decision before the trial can support validation. Preserve the public task/runtime date and original score; never silently repair the answer from a later state. Prior private files are constructor evidence and cannot be passed to blind solvers.','supplement_policy':'No required current verdict depends on a missing supplement. Som excluded by its chronic protocol, so preliminary tumor-image classification need not be completed. Fetch a linked supplement only if a changed/new eligible verdict actually requires it.','estimated_one_observation_requests':17,'estimated_one_observation_bytes':sum(r.get('bytes',0) for r in requests if r['label'].endswith('_refresh'))})
put('execution_checks.json',{'status':'in_progress','scientific_content':'not independently validated','model_tests':0})
cmd=[sys.executable,str(ROOT/'construction_pipeline/scripts/prepare.py'),'validate-candidate','--candidate',str(B/'candidate.json'),'--check-files'];p=subprocess.run(cmd,text=True,capture_output=True);assert p.returncode==0,p.stdout+p.stderr
sys.path.insert(0,str(ROOT/'construction_pipeline/scripts'));from prepare import make_public
for v in ['cg','go']:
 q=make_public(c,'2026-09-09',v);assert set(q)=={'instruction','output_format','current_date'} and q['current_date']=='2026-09-09'
put('execution_checks.json',{'checked_at_utc':datetime.now(timezone.utc).isoformat(),'schema':'passed','prepare':{'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr},'pair':'all 8 predicates literal match; CG minus steps equals GO; exact 2-key files; same output_format','reference':report1,'scorer_fixtures':len(fixtures),'main_vs_review_paragraphs':{'main':len(ps),'all_bodies':len(all_ps),'namespaced_fixture_passed':True},'model_tests':0,'human_validation':'not_performed','content_review':'constructor only; independent quality audit not run','runtime_date':'2026-09-09'})
print(json.dumps({'schema':'passed','pair':'passed','reference':report1,'scorer_fixtures':len(fixtures),'main_vs_review':'31 versus 86','model_tests':0}))
