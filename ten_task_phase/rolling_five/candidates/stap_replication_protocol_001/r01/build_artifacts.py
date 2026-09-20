from pathlib import Path
import json,re,xml.etree.ElementTree as ET
B=Path(__file__).resolve().parent

def put(name,x):
 p=B/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
core=json.loads((B/'sources/raw/cohort_initial.response').read_text());rows=core['resultList']['result']
raw={'PMC4904271':'sources/raw/03_reproduction_fulltext.response','PMC4908587':'sources/raw/04_chronic_acid_boundary_fulltext.response','PMC4995676':'sources/raw/05_later_supervised_reproduction_fulltext.response'}
raw.update({p.stem:str(p.relative_to(B)) for p in (B/'sources/raw').glob('PMC*.response')})
def paragraphs(path):
 root=ET.parse(B/path).getroot()
 for e in root.iter():e.tag=e.tag.rsplit('}',1)[-1]
 body=root.find('body')
 return [' '.join(''.join(e.itertext()).split()) for e in body.iter('p')]
main={p:paragraphs(f) for p,f in raw.items()}
reasons={
1:'Review of retinal pigment epithelium therapeutics; the abstract states that it reviews molecular processes and transplantation progress, with no own STAP induction experiment.',
2:'Bibliometric study of retracted authors using Retraction Watch, Microsoft Academic Graph and Altmetric; its subjects are publishing careers, not acid-treated cells.',
3:'Review of cell therapy for spinal cord injury; the abstract explicitly describes a review of relevant cell types, not an own transient-acid experiment.',
4:'Perspective/review proposing double sperm cloning; its described reprogramming route is sperm injection into denucleated oocytes, not low-pH somatic-cell induction.',
5:'Discusses adult pluripotency and recounts the original STAP study as a cited report; does not report its own transient-acid induction experiment.',
6:'Review of the clinical/ethical limitations of stem-cell therapies, explicitly analyzing ethics and politics, not performing acid induction.',
7:'Own data are tweets and public sentiment following the STAP scandal; not own cell experiments.',
8:'Own data are Twitter and newspaper content about misconduct; not own cell experiments.',
9:'Discussion of irreproducibility; paragraph 11 treats STAP failures as external published examples.',
10:'Own chronic mildly acidic tumor-environment experiments, including pH 6.5 culture for seven days. Not transient low-pH STAP induction; OCT4 observations do not change this exclusion.',
11:'Own experimental replication investigation using transient HCl and ATP treatments; included irrespective of the negative overall conclusion.',
12:'RNA-seq chromosomal-aberration/allelic-bias method using gene-expression profiles; not own transient-acid reprogramming.',
13:'Reports the supervised experiment performed by Obokata and the examination team; included as this publication\'s own experiment, distinct from the cited Niwa investigation.',
14:'Letter about figures, image manipulation and scientific communication; STAP is among cited examples, not an experiment performed here.',
15:'Survey of peer-review mechanisms in 82 scientific-communication channels; not cell induction.',
16:'Commentary on improving peer review; paragraph 5 recounts post-publication STAP criticism and retraction.',
17:'Proposes a chemotherapy strategy protecting normal cells; no own transient low-pH pluripotency study in its described research scope.',
18:'Own metformin exposure of stromal cells and fibroblasts; drug effects on viability and IGF2, not acid-based STAP induction.',
19:'Commentary on pressure to publish; no own cellular reprogramming experiment.',
20:'Ontology and text-mining evaluation of biomedical protocols. Paragraph 78 invokes STAP as a cited reproducibility example, not a protocol the authors experimentally repeat.',
21:'Retrospective computational reanalysis of STAP RNA-seq SNP allele frequencies; does not produce new acid-treated cells.',
22:'Patient-centered ethical risk-benefit analysis of iPSC clinical research; no own low-pH induction experiment.',
23:'HCV infection mechanisms and associated models; stem-like cells arise in the context of viral infection, not transient low-pH STAP experiments.',
24:'Pathophysiology synthesis of ocular surface squamous neoplasia and UV/HIV/HPV mechanisms; not own STAP induction.',
25:'Review of cardiac reprogramming strategies and clinical challenges; no own acid-treatment replication study.',
26:'Conceptual discussion of stress and pluripotency. STAP evidence and failed attempts are explicitly attributed to other reports/labs.',
27:'Explicit review of Muse cells and their reported isolation under severe stress; no own transient-acid STAP replication.',
28:'Review of iPSC-derived cells for cancer immunotherapy; not own acid-induced somatic-cell pluripotency.',
29:'StemCellNet network-analysis web-server and molecular-interaction resource; not own cell-reprogramming experiment.',
30:'Own Xenopus oncogene and ion-channel experiments testing distant resting-voltage control of tumorigenesis; acidity is a tumor characteristic, not the induction being tested.',
31:'Own qPCR observational analysis of blood samples from healthy/hypertensive people; measures transcriptional networks, not low-pH induction.',
32:'Own characterization of vascular smooth-muscle cell lines with serum deprivation, adipogenic induction and Notch blockade; not low-pH STAP replication.',
33:'Own rat depression model with ethanol/corticosterone exposure and neural-stem-cell treatment; no transient-acid pluripotency induction.',
34:'Own study of growth factors/pathways maintaining established marmoset embryonic stem cells; not induction from acid-treated somatic cells.',
35:'Explicit review of ethical issues in stem-cell research and therapy; no own STAP experiment.',
36:'News report about reproducibility initiatives. Paragraph 3 reports other scientists\' acid-bath failures; these are not this article\'s experiments.',
37:'Own AICAR treatment and miRNA profiling in established J1 embryonic stem cells; the low-pH result is prior literature, not the intervention tested.',
38:'Own kainic-acid neurotoxicity model examining mobilization/expansion of pre-existing VSELs. Kainic acid is a neurotoxin here, not a low-pH bath inducing STAP pluripotency.',
39:'Perspective recounting the original CD45/acid experiment in paragraph 6 and calling for further studies; no own repetition.',
40:'Own chemical-cocktail plus hypoxia conversion to neural progenitors, not transient low-pH pluripotency induction.',
41:'Review/discussion of routes and mechanisms of induced pluripotency, reporting other studies; not own STAP induction.',
42:'Own HCl treatment of CD45-sorted neonatal splenocytes and lung fibroblasts to replicate the early induction stage; functional pluripotency testing is not required for eligibility.',
43:'Despite mixed research-article/Review metadata, the abstract and body discuss others\' published reprogramming findings. The STAP paragraph is explicitly about another study.',
44:'Commentary summarizing the original Nature claims and explicitly calling for replication; no own acid-bath experiment.',
45:'Explicit review of molecular and cell therapies for muscle degeneration; no own STAP replication.',
46:'Comment on Saccone and colleagues\' muscle-plasticity study; pH reprogramming is cited as an external unconfirmed finding.',
47:'Summarizes the authors\' prior glioblastoma reprogramming with exogenous OCT4/KLF4. The experimental route is transcription factors, not low-pH STAP induction.',
48:'Explicit review of disease modelling and iPSC therapy; no own acid induction.',
49:'Own six-month low-dose arsenic stress causing cancer-stem-cell traits; not transient low-pH STAP induction.'}
extra={5:[15],9:[1,11],10:[2,4,11,12,16,18],11:[3,4,5,6,7,8,9,10,11,12,13,14,16,17,23,24],13:[2,3,4,5,7,8,13,14,15,16,17,18,19,20,21,23,24],14:[1,3,6,7],16:[1,5],20:[78],26:[1,4,5],36:[1,3,7],39:[6],42:[3,4,8,9,14,16,20,21,22],43:[18],44:[1,9],46:[5],47:[1,9,10]}
annotations=[]
for i,x in enumerate(rows,1):
 pmc=x['pmcid'];ev=[]
 if x.get('abstractText'):ev.append({'source':'sources/raw/cohort_initial.response','locator':f'resultList.result[{i-1}].abstractText','quote':x['abstractText']})
 for n in extra.get(i,[]):ev.append({'source':raw[pmc],'locator':f'article/body descendant p[{n}] (1-based; excludes sub-articles)','paragraph':n,'quote':main[pmc][n-1]})
 assert ev
 annotations.append({'roster_index':i,'pmid':x['id'],'pmcid':pmc,'title':x['title'],'included':i in [11,13,42],'decision_reason':reasons[i],'evidence':ev,'abstract_present':bool(x.get('abstractText')),'pubtype_not_used_as_sufficient_exclusion':True,'semantic_review':'Constructor model assessment, not independent human adjudication'})
put('eligibility_annotations.json',annotations)
put('evidence/main_article_paragraphs.json',{p:[{'p':i,'text':t} for i,t in enumerate(ts,1)] for p,ts in main.items()})
# Explicit semantic annotations; the reference checks quotes and structured statuses,
# but does not claim to independently infer scientific meaning from arbitrary prose.
studies=[
 {'pmid':'25075303','pmcid':'PMC4032108','name':'Tang et al. (2014)','procedure':['HCL','CD45_SORTED','REPORTER_DIFFERENT'],'markers':'NEGATIVE','chimera':'NOT_REPORTED','teratoma':'NOT_REPORTED','lines':'NOT_REPORTED','pluripotency':'NOT_ESTABLISHED','source':raw['PMC4032108'],'locators':[3,8,9,14,16,20,21,22], 'notes':'Authors describe following the updated protocol but flag a different Oct4-GFP mouse strain/reporter. Necrotic apparent GFP signal was autofluorescence; endogenous Oct4/Sox2/Nanog not induced. This is an early-stage attempt; no functional test of induced cells is reported in the complete main article. Germ-cell GFP checks are controls, not proof of induced pluripotency.'},
 {'pmid':'27292224','pmcid':'PMC4904271','name':'Niwa (2016)','procedure':['HCL','ATP','FGF2','CD45_UNSORTED'],'markers':'RARE_POSITIVE','chimera':'NEGATIVE','teratoma':'NOT_REPORTED','lines':'FAILED','pluripotency':'NOT_ESTABLISHED','source':raw['PMC4904271'],'locators':[3,4,5,6,7,8,9,10,11,12,13,14,16,17,23,24], 'notes':'HCl attempt followed by ATP and FGF2 suggestions; spleen lymphocytes isolated by Lympholyte without a CD45 sorting step in the described preparation. Rare ATP-treated liver aggregate Oct3/4 expression by qPCR/immunostaining is real reported marker evidence, not full pluripotency. Own chimera assay negative and both ES-like/TS-like stable line derivations failed. The 1154/671 passage is another investigation and is not counted as this paper\'s own assay.'},
 {'pmid':'27610221','pmcid':'PMC4995676','name':'Aizawa (2016), version 2','procedure':['HCL','ATP','FGF2','CD45_UNSORTED'],'markers':'RARE_POSITIVE','chimera':'NEGATIVE','teratoma':'NOT_PERFORMED','lines':'NOT_ATTEMPTED','pluripotency':'NOT_ESTABLISHED','source':raw['PMC4995676'],'locators':[2,3,4,5,7,8,13,14,15,16,17,18,19,20,21,23,24], 'notes':'Both HCl and ATP used; FGF2 in culture, CD45 FACS explicitly omitted. Preliminary qPCR suggested rare one/multiple marker-positive aggregates; fluorescence cause unresolved and most assays negative. Own chimera assay showed no significant contribution; teratoma/tetraploid tests and secondary line establishment explicitly not done. Use main article only, not peer-review suggestions.'}
]
for s in studies:s['evidence']=[{'paragraph':n,'quote':main[s['pmcid']][n-1]} for n in s['locators']]
put('study_annotations.json',studies)
put('source_manifest.json',{'source_date_utc':'2026-09-13','cohort_observation_utc':'2026-09-13T06:25:10.785712+00:00','runtime_date':'2026-09-09','seed':'sources/raw/01_seed_search.response','cohort':'sources/raw/cohort_initial.response','query':'CITES:24476887_MED AND OPEN_ACCESS:Y','seed_pmid':'24476887','seed_source':'MED','fulltexts':raw,'eligibility_annotations':'eligibility_annotations.json','study_annotations':'study_annotations.json','new_requests':'sources/request_index.jsonl','reused_requests':'sources/opportunity_request_index.jsonl','protocol_claim_decision':'protocol_claim_decision.json','scope_note':'Current indexed citing publications registered open access; not every free or worldwide citing publication. One row per publication; main article version observed.'})
print(json.dumps({'eligibility':len(annotations),'included':sum(a['included'] for a in annotations),'fulltexts':len(raw),'no_abstract_reviewed':sum(not a['abstract_present'] for a in annotations)}))
