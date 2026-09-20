"""Independent pre-A reconstruction. No author solver/checker imports."""
import json,itertools,re,collections
from pathlib import Path
out=Path(__file__).resolve().parent
root=out.parent
raw=root.parents[2]/'opportunities'/'nvd_configuration_environment'/'raw'
cve_response=json.loads((raw/'d0001.response').read_text())
assert cve_response['totalResults']==cve_response['resultsPerPage']==1 and cve_response['startIndex']==0
cve=cve_response['vulnerabilities'][0]['cve']
assert cve['id']=='CVE-2023-28771'
criteria={}
def collect(o):
 for c in o.get('cpeMatch',[]):
  k=c['matchCriteriaId'];assert k not in criteria or criteria[k]==c;criteria[k]=c
 for n in o.get('nodes',[]):collect(n)
for c in cve['configurations']:collect(c)
matches={};receipts=[]
for path in raw.glob('d*.response'):
 d=json.loads(path.read_text())
 if 'matchStrings' not in d:continue
 assert d['totalResults']==d['resultsPerPage']==len(d['matchStrings'])==1 and d['startIndex']==0
 m=d['matchStrings'][0]['matchString'];k=m['matchCriteriaId'];assert k in criteria and k not in matches
 for f in ['criteria','versionStartIncluding','versionEndIncluding','versionStartExcluding','versionEndExcluding']:assert m.get(f)==criteria[k].get(f),(k,f)
 assert m['status']=='Active' and isinstance(m['matches'],list)
 names=[x['cpeName'] for x in m['matches']];assert len(names)==len(set(names))
 matches[k]=set(names)
 receipts.append({'file':path.name,'uuid':k,'names':len(names),'cpeLastModified':m.get('cpeLastModified'),'criteria':m['criteria']})
assert set(matches)==set(criteria)
# Evaluate literal membership at every leaf, then recorded Boolean operators.
# vulnerable is an affected/environment role, never negation of leaf membership.
def evaluate(o,inventory):
 truth=[bool(matches[c['matchCriteriaId']] & inventory) for c in o.get('cpeMatch',[])]
 truth += [evaluate(n,inventory) for n in o.get('nodes',[])]
 assert truth and o['operator'] in ('AND','OR')
 v=all(truth) if o['operator']=='AND' else any(truth)
 return not v if o.get('negate',False) else v
def applicable(inventory):return any(evaluate(c,inventory) for c in cve['configurations'])
def split(c):
 a=re.split(r'(?<!\\):',c);assert len(a)==13;return a
all_names=set().union(*matches.values())
hw=sorted(n for n in all_names if split(n)[2]=='h');fw=sorted(n for n in all_names if split(n)[2]=='o')
assert len(all_names)==len(hw)+len(fw)
pairs=[(h,f) for h,f in itertools.product(hw,fw) if applicable({h,f})]
assert not any(applicable({f}) for f in fw)
# Verify projection loses no distinguishing attributes in this actual dataset.
for h in hw:assert split(h)[3]=='zyxel' and split(h)[5:]==['-']+['*']*7
for f in fw:assert split(f)[3]=='zyxel' and split(f)[7:]==['*']*6
assert all((split(n)[2]=='h') != criteria[k]['vulnerable'] for k,ns in matches.items() for n in ns)
groups=collections.defaultdict(set)
for h,f in pairs:
 a,b=split(h),split(f);groups[(a[4],b[4])].add(f'{b[5]}({b[6]})')
psv='hardware_product|firmware_product|registered_releases\n'+'\n'.join('|'.join([*k,';'.join(sorted(v))]) for k,v in sorted(groups.items()))+'\n'
(out/'independent_oracle.psv').write_text(psv)
(out/'independent_pairs.json').write_text(json.dumps(pairs,indent=2)+'\n')
# Comparison happens only after independent derivation is complete.
author=(root/'oracle.psv').read_text()
result={'criterion_count':len(criteria),'criterion_responses':len(matches),'configurations':len(cve['configurations']),'hardware_count':len(hw),'firmware_count':len(fw),'complete_pair_count':len(pairs),'grouped_rows':len(groups),'exact_oracle_equal':psv==author,'projection_lossless':True,'standalone_firmware_accepted':0,'response_receipts':receipts,'nonstar_updates':sorted({split(f)[6] for f in fw if split(f)[6]!='*'}),'configuration_operators':collections.Counter(c['operator'] for c in cve['configurations'])}
(out/'independent_derivation.json').write_text(json.dumps(result,indent=2)+'\n');assert psv==author
print({k:v for k,v in result.items() if k!='response_receipts'})
