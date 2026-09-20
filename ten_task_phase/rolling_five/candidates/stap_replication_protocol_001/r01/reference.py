#!/usr/bin/env python3
"""Offline reference rebuild. Scientific decisions are explicit constructor annotations.
Checks source identities/coverage/quotes and computes the requested token table.
No model invocation or independent scientific-validation claim.
"""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path

def load(p):return json.loads(p.read_text())
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def require(v,msg):
 if not v:raise ValueError(msg)
def main_paragraphs(path):
 root=ET.parse(path).getroot()
 for e in root.iter():e.tag=e.tag.rsplit('}',1)[-1]
 body=root.find('body');require(body is not None,'No top-level main article body')
 return root,[' '.join(''.join(e.itertext()).split()) for e in body.iter('p')]
def run(base,out,observation='initial'):
 m=load(base/'source_manifest.json');suffix='' if observation=='initial' else '_refresh'
 cohort=load(base/(m['cohort'] if not suffix else 'sources/raw/cohort_refresh.response'))
 records=cohort['resultList']['result'];require(len(records)==cohort['hitCount'],'Incomplete cohort');require(not cohort.get('nextCursorMark'),'Unexpected more results')
 require(cohort['request']['queryString']==m['query'],'Cohort scope query mismatch')
 by={x['id']:x for x in records};require(len(by)==len(records),'Duplicate PMIDs')
 require(all(x.get('isOpenAccess')=='Y' and x.get('pmcid') and x.get('source')=='MED' for x in records),'OA/identity scope mismatch')
 seed=load(base/m['seed'])['resultList']['result'];orig=[x for x in seed if x['id']==m['seed_pmid'] and x['source']==m['seed_source']]
 require(len(orig)==1 and orig[0]['doi']=='10.1038/nature12968','Original-vs-retraction identity mismatch')
 eligibility=load(base/m['eligibility_annotations']);require({x['pmid'] for x in eligibility}==set(by),'Eligibility review incomplete')
 bodies={};versions={}
 for pmc,path in m['fulltexts'].items():
  path=path if not suffix else 'sources/raw/'+pmc+'_refresh.response'
  root,ps=main_paragraphs(base/path);bodies[pmc]=ps
  ids={e.attrib.get('pub-id-type'):''.join(e.itertext()) for e in root.findall('./front/article-meta/article-id')}
  require(ids.get('pmcid',ids.get('pmc','')).split('.')[0].removeprefix('PMC')==pmc.removeprefix('PMC'),'Fulltext PMCID mismatch '+pmc)
  versions[pmc]=ids
 for a in eligibility:
  require(a['pmcid']==by[a['pmid']]['pmcid'],'Eligibility identity mismatch')
  require(a['decision_reason'] and a['evidence'],'Missing individual review evidence')
  for ev in a['evidence']:
   actual=bodies[a['pmcid']][ev['paragraph']-1] if 'paragraph' in ev else by[a['pmid']].get('abstractText')
   require(actual==ev['quote'],'Evidence changed '+a['pmid'])
 studies=load(base/m['study_annotations']);require({s['pmid'] for s in studies}=={a['pmid'] for a in eligibility if a['included']},'Included study closure differs')
 rows=[]
 for s in sorted(studies,key=lambda s:int(s['pmid'])):
  require(s['pmcid']==by[s['pmid']]['pmcid'],'Study identity mismatch')
  for ev in s['evidence']:require(bodies[s['pmcid']][ev['paragraph']-1]==ev['quote'],'Study quote changed')
  require(s['markers'] in ['NEGATIVE','RARE_POSITIVE','POSITIVE','UNCLEAR','NOT_REPORTED'],'Marker state')
  require(s['chimera'] in ['POSITIVE','NEGATIVE','NOT_PERFORMED','NOT_REPORTED'],'Chimera state')
  require(s['teratoma'] in ['POSITIVE','NEGATIVE','NOT_PERFORMED','NOT_REPORTED'],'Teratoma state')
  require(s['lines'] in ['ESTABLISHED','FAILED','NOT_ATTEMPTED','NOT_REPORTED'],'Line state')
  evidence=['CHIMERA_'+s['chimera'],'TERATOMA_'+s['teratoma'],'LINES_'+s['lines'],'PLURIPOTENCY_'+s['pluripotency']]
  rows.append([s['pmid'],';'.join(sorted(s['procedure'])),s['markers'],';'.join(evidence)])
 out.mkdir(parents=True,exist_ok=True)
 (out/'oracle.psv').write_text('PMID|PROCEDURE|MARKERS|FUNCTIONAL_EVIDENCE\n'+''.join('|'.join(r)+'\n' for r in rows))
 dump(out/'scope_checks.json',{'observation':observation,'candidate_records':len(records),'included':len(rows),'excluded':len(records)-len(rows),'abstractless_records':sum(not x.get('abstractText') for x in records),'fulltexts':len(bodies),'output_fields':4*len(rows),'main_article_versions':versions,'semantic_limit':'Revalidates citations and computes annotations; does not independently adjudicate scientific meaning.'})
 dump(out/'inventory.json',[{'pmid':a['pmid'],'pmcid':a['pmcid'],'included':a['included'],'reason':a['decision_reason']} for a in eligibility])
 return {'candidate_records':len(records),'included':len(rows),'excluded':len(records)-len(rows),'fields':4*len(rows)}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out-dir',type=Path,required=True);p.add_argument('--observation',choices=['initial','refresh'],default='initial');a=p.parse_args();print(json.dumps(run(Path(__file__).resolve().parent,a.out_dir,a.observation)))
