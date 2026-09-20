"""Independent pre-A audit bookkeeping. Manual scientific decisions derive from raw
core abstracts and direct article/body, not constructor annotations or reference code.
Uses the existing unchanged protocol scorer solely for normalization verification.
"""
from pathlib import Path
import json,xml.etree.ElementTree as ET,importlib.util,datetime
P=Path(__file__).resolve().parents[1]; O=Path(__file__).resolve().parent

def read(n):return json.loads((P/n).read_text())
def write(n,x): (O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
raw=read('sources/raw/cohort_initial.response'); recs=raw['resultList']['result']
reasons='''40503367|RPE therapy review, explicitly reviews transplantation and molecular processes.
40217002|Bibliometric analysis of retracted authors' careers; units are publications and researchers.
33433463|Review of stem-cell therapy for spinal cord injury.
32894201|Double sperm cloning strategy; sperm nuclear injection, not somatic transient acid induction.
30705711|Editorial review of adult pluripotency; STAP section attributes acid experiments to original authors.
29291747|Debate/review of ethical, commercial and biomedical limits of stem-cell medicine.
28428163|Twitter sentiment study of the STAP controversy, not experiments on cells.
28246071|Comparison of Twitter/newspaper attention to STAP, not cell experiments.
28123930|Discussion of research irreproducibility; STAP is a cited example of failed findings.
27302093|Own fibroblast study, but pH 6.5 chronic culture for seven days, not transient STAP induction.
27292224|INCLUDE: Niwa own HCl/ATP transient treatment and marker, chimera, secondary-line experiments.
27385103|RNA-seq allelic/chromosomal computational analysis, not own transient acid-treated cells.
27610221|INCLUDE: Aizawa supervised own transient HCl/ATP attempt, marker observations and chimera testing.
26539021|Letter on publication figures; retracted STAP is an example of graphical bias.
26074753|Survey of scientists and peer-review channels, not cell experiments.
26559758|Discussion advocating accessible peer review; STAP cited as publication controversy.
26177855|Cancer treatment strategy/commentary; no transient low-pH STAP induction experiment.
26064951|Metformin exposure in marrow/adipogenic cells; different chemical treatment.
26594336|Commentary on pressure to publish and retractions.
25472549|EXACT2 ontology and protocol representation; STAP appears as cited motivation, no laboratory replication.
25243705|RNA-seq SNP quality-control/computational reanalysis, not experimental induction.
24974102|Ethical/risk assessment of iPSC clinical use, not transient acid induction.
26417315|HCV infection and possible liver cancer stem-cell development; viral rather than transient low-pH route.
25447808|Review of ocular neoplasia, UV and viral etiologies; not acid-STAP experiments.
25763379|Review of cardiac direct reprogramming.
25364739|Editorial on stress and pluripotency; evaluates others' STAP/Muse findings, no own attempt.
24940477|Review of adipose-derived Muse cells; not own transient acid-STAP attempt.
24860566|Review of iPSC applications to cancer immunotherapy.
24852251|StemCellNet computational web server, not cell induction experiment.
24830454|Xenopus oncogene/bioelectric tumor experiments; acidity is tumor milieu, not somatic STAP induction.
24759906|PBMC transcriptional-network measurements; no induced pluripotency by acid.
24628920|Rat vascular smooth-muscle cell characterization and serum/DAPT perturbation; no acid-STAP induction.
24671607|Prenatal ethanol/corticosterone/swim-stress depression and neural stem-cell therapy; not low-pH STAP.
24649403|Marmoset embryonic stem-cell culture maintenance with FGF/TGF-beta, not somatic induction.
25157428|Review of stem-cell ethics.
24984077|News article on reproducibility initiatives; experiments described are other researchers' work.
25078608|AICAR/microRNA experiments in existing embryonic stem cells; maintenance, not somatic acid induction.
24895014|Kainic-acid brain injury and VSEL response; chemical neurotoxicity/existing stem cells, not low-pH STAP.
25031174|Letter reviewing hematopoietic reprogramming; low-pH results attributed to cited STAP authors.
24638034|Small-molecule cocktail plus hypoxia induces neural progenitors; not transient low-pH treatment.
24832604|Review/roadmap of pluripotency regulation.
25075303|INCLUDE: Tang own low-pH HCl CD45-positive splenocyte and lung-fibroblast replication attempt.
25002192|Lucky iPSCs review, despite research-article metadata; STAP explicitly another recent study.
25206856|Dipping cells in acidic bath commentary; attributed Obokata results and request for future replication.
24782779|Review of stem-cell therapies for muscle disease.
24736840|Commentary on Saccone and colleagues' dystrophic-muscle work, not own STAP attempt.
24686321|Commentary summarizing authors' prior forced-factor GBM reprogramming, not acid-STAP induction.
24724061|Review of iPSC disease modeling and therapies.
24675390|Arsenic exposure of epithelial cells for six months; chronic different chemical, not transient acid-STAP.'''
byreason=dict(line.split('|',1) for line in reasons.splitlines()); assert len(byreason)==49
assert raw['hitCount']==len(recs)==len({x['id'] for x in recs})==49
assert set(byreason)=={x['id'] for x in recs}
assert raw['request']['queryString']=='CITES:24476887_MED AND OPEN_ACCESS:Y'
assert not raw.get('nextCursorMark')
assert all(x['source']=='MED' and x['isOpenAccess']=='Y' for x in recs)
full={}; body={}; ids={}
for f in (P/'sources/raw').glob('*.response'):
 if 'refresh' in f.name:continue
 try:r=ET.fromstring(f.read_bytes())
 except ET.ParseError:continue
 b=r.find('body')
 if b is None:continue
 aid={x.get('pub-id-type'):''.join(x.itertext()) for x in r.findall('./front/article-meta/article-id')}
 pmc=aid.get('pmcid',aid.get('pmc','')).split('.')[0]
 if not pmc.startswith('PMC'):pmc='PMC'+pmc
 full[pmc]=f; ids[pmc]=aid;body[pmc]=[' '.join(' '.join(x.itertext()).split()) for x in b.findall('.//p')]
assert len(full)==16
for r in recs:
 if r['pmcid'] in ids:assert ids[r['pmcid']]['pmid']==r['id']
noabs=[r['id'] for r in recs if not r.get('abstractText')]
assert len(noabs)==7 and all(r['pmcid'] in full for r in recs if r['id'] in noabs)
elig=[{'pmid':r['id'],'pmcid':r['pmcid'],'included':byreason[r['id']].startswith('INCLUDE:'),'independent_reason':byreason[r['id']],'source':'direct main body plus core' if r['pmcid'] in full else 'core abstract','main_file':str(full[r['pmcid']].relative_to(P)) if r['pmcid'] in full else None} for r in recs]
# Decisive locators are one-based direct-body descendant p positions, including captions.
locators={
'25075303':{'procedure':[8,9,21],'markers':[14,16,20,21],'functional_absence':'Entire main body (23 paragraphs); positive spermatogonia are controls; cited chimera reports are not this study.'},
'27292224':{'procedure':[4,5,6,10,11,16,17],'markers':[7,8,9,14],'chimera':[12],'lines':[13,14],'teratoma_absence':'Entire main body; no own teratoma assay statement.'},
'27610221':{'procedure':[4,5,7,23],'markers':[16,17,18,19],'chimera':[13,14],'teratoma':[15],'lines':[21]}}
quotes={}
for pmid,axes in locators.items():
 pmc=next(r['pmcid'] for r in recs if r['id']==pmid)
 quotes[pmid]={'pmcid':pmc,'ids':ids[pmc],'axes':{a:([{'paragraph':i,'text':body[pmc][i-1]} for i in v] if isinstance(v,list) else v) for a,v in axes.items()}}
# Explicit independent raw-evidence conclusions, then compared against constructor oracle.
expected='''PMID|PROCEDURE|MARKERS|FUNCTIONAL_EVIDENCE
25075303|CD45_SORTED;HCL;REPORTER_DIFFERENT|NEGATIVE|CHIMERA_NOT_REPORTED;TERATOMA_NOT_REPORTED;LINES_NOT_REPORTED;PLURIPOTENCY_NOT_ESTABLISHED
27292224|ATP;CD45_UNSORTED;FGF2;HCL|RARE_POSITIVE|CHIMERA_NEGATIVE;TERATOMA_NOT_REPORTED;LINES_FAILED;PLURIPOTENCY_NOT_ESTABLISHED
27610221|ATP;CD45_UNSORTED;FGF2;HCL|RARE_POSITIVE|CHIMERA_NEGATIVE;TERATOMA_NOT_PERFORMED;LINES_NOT_ATTEMPTED;PLURIPOTENCY_NOT_ESTABLISHED
'''
(O/'independent_expected.psv').write_text(expected)
assert {x['pmid'] for x in elig if x['included']}=={'25075303','27292224','27610221'}
assert (P/'oracle.psv').read_text()==expected
# Only now compare constructor classification; no constructor decision code imported.
ann=read('eligibility_annotations.json')
assert {x['pmid']:x['included'] for x in ann}=={x['pmid']:x['included'] for x in elig}
refresh=read('sources/raw/cohort_refresh.response')
assert {r['id']:r for r in recs}=={r['id']:r for r in refresh['resultList']['result']}
stability={pmc:f.read_bytes()==(P/'sources/raw'/f'{pmc}_refresh.response').read_bytes() for pmc,f in full.items()}; assert all(stability.values())
cg=read('cg.json');go=read('go.json');guidance=read('pair_alignment.json')['CG_only_guidance']; assert cg['instruction'].replace(guidance+'\n\n','')==go['instruction'];assert cg['output_format']==go['output_format']
scorepath=P.parents[4]/'protocol/ten-task-v1/score.py'
# Resolve repository rather than candidate-private helpers.
repo=next(x for x in P.parents if (x/'construction_pipeline/ten_task_phase/protocol/ten-task-v1/score.py').exists())
scorepath=repo/'construction_pipeline/ten_task_phase/protocol/ten-task-v1/score.py'
spec=importlib.util.spec_from_file_location('registered_score',scorepath);score=importlib.util.module_from_spec(spec);spec.loader.exec_module(score)
rules=read('rules.json');gold=score.parse(expected,rules['columns']);scored={}
for f in (P/'scorer_witnesses').glob('*.psv'):
 out=score.score(gold,score.parse(f.read_text(),rules['columns']),rules);scored[f.stem]={'metrics':out['metrics'],'counts':out['counts']}
assert scored['reference']['counts']['correct_fields']==12
assert scored['case_and_set_order']['metrics']['Item-F1']==1
for name in ['omit_atp','markers_mistaken_for_function','unperformed_mistaken_for_negative','reported_mistaken_for_unperformed','miss_rare_markers']:assert scored[name]['counts']['correct_fields']==11
assert scored['drop_study']['metrics']['Item-F1']==0.8
assert scored['reverse_rows']['metrics']['P.O.A.']==0
write('eligibility_review.json',elig);write('decisive_evidence.json',quotes);write('scorer_results.json',scored)
files=['candidate.json','cg.json','go.json','rules.json','reference.py','oracle.psv','eligibility_annotations.json','study_annotations.json','inventory.json','construction_report.json','source_stability.json']
write('reviewed_files.json',[{'path':n,'bytes':(P/n).stat().st_size,'mtime_utc':datetime.datetime.fromtimestamp((P/n).stat().st_mtime,datetime.timezone.utc).isoformat()} for n in files])
summary={'cohort':49,'included':3,'excluded':46,'without_abstract':noabs,'main_texts':16,'main_article_ids':ids,'all_core_fields_equal':True,'all_raw_fulltext_bytes_equal':stability,'oracle_matches_independent_raw_conclusions':True,'all_49_eligibility_match':True,'cg_minus_guidance_equals_go':True,'output_format_equal':True,'scorer_fields_including_pmid':12,'scorer_fixture_count':len(scored),'constructor_reference_imported':False,'network_calls':0,'new_model_tests':0,'subagents':0}
write('summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ['main_article_ids','all_raw_fulltext_bytes_equal']},ensure_ascii=False))
