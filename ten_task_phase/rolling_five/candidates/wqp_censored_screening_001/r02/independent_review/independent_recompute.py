import csv,json,math,collections
from pathlib import Path
out=Path(__file__).resolve().parent
root=out.parents[3]
e=root/'opportunities/wqp_censored_screening/evidence'
def read(n):return list(csv.DictReader((e/n).open(encoding='utf-8-sig')))
cad=read('d0002.response');base=read('d0001.response');limits=read('d0003.response');hard=read('d0004.response')
assert len(cad)==len({r['ResultIdentifier'] for r in cad})==137
shared=set(cad[0])&set(base[0]); assert collections.Counter(tuple(r[k] for k in sorted(shared)) for r in cad)==collections.Counter(tuple(r[k] for k in sorted(shared)) for r in base)
ld=collections.defaultdict(dict)
for r in limits:
 k=(r['OrganizationIdentifier'],r['ResultIdentifier']);typ=r['DetectionQuantitationLimitTypeName'];v=float(r['DetectionQuantitationLimitMeasure/MeasureValue'])
 assert r['DetectionQuantitationLimitMeasure/MeasureUnitCode']=='ug/L'
 assert typ not in ld[k];ld[k][typ]=v
hd=collections.defaultdict(list)
for r in hard:hd[r['OrganizationIdentifier'],r['ActivityIdentifier']].append(r)
counts=collections.Counter();ledger=[]
for r in cad:
 if r['ResultSampleFractionText']!='Dissolved':continue
 assert r['CharacteristicName']=='Cadmium' and (r['ResultMeasure/MeasureUnitCode']=='ug/L' or r['ResultDetectionConditionText']=='Not Reported')
 hrows=hd[r['OrganizationIdentifier'],r['ActivityIdentifier']];assert len(hrows)==1
 h=hrows[0];assert h['ActivityStartDate']==r['ActivityStartDate']
 assert h['ResultMeasure/MeasureUnitCode']=='mg/L' or h['ResultDetectionConditionText']=='Not Reported'
 if h['ResultDetectionConditionText']=='Not Reported':
  assert 'recalled' in h['ResultCommentText']; hs='withdrawn';H=None
 else:
  assert h['CharacteristicName']=='Hardness, Ca, Mg';H=float(h['ResultMeasureValue']);assert H>0;hs='available'
 bound=ld[r['OrganizationIdentifier'],r['ResultIdentifier']];q=r['MeasureQualifierCode'];lo=hi=None
 if r['ResultDetectionConditionText']=='Not Reported':ev='not_reported'
 elif q=='U':
  assert set(bound)=={'Lower Reporting Limit'};ev='unresolved_u_limit'
 elif q=='DL':lo=0;hi=bound['Method Detection Level'];ev='below_mdl'
 elif q=='J-R':lo=bound['Method Detection Level'];hi=bound['Lower Reporting Limit'];assert lo<hi;ev='between_mdl_rl'
 else:
  assert q=='';lo=hi=float(r['ResultMeasureValue']);ev='point'
 criterion=None if H is None else math.exp(.7409*math.log(H)-4.719)*(1.101672-.041838*math.log(H))
 if ev=='not_reported':screen='not_reported'
 elif ev=='unresolved_u_limit':screen='unresolved_limit'
 elif H is None:screen='unresolved_hardness'
 elif hi<=criterion:screen='below_or_equal'
 elif lo>criterion or (ev=='between_mdl_rl' and lo==criterion):screen='above'
 else:screen='crosses'
 counts[ev,hs,screen]+=1
 ledger.append(dict(result_id=r['ResultIdentifier'],date=r['ActivityStartDate'],evidence=ev,hardness_state=hs,screen=screen,hardness=H,criterion=criterion,lower=lo,upper=hi))
lines=['evidence|hardness_state|screen|n_results']+['|'.join((*k,str(v))) for k,v in sorted(counts.items())]
(out/'independent_oracle.psv').write_text('\n'.join(lines)+'\n')
(out/'independent_ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
expected=(out.parent/'oracle.psv').read_text().strip().splitlines()
result={'source_rows':len(cad),'limits_rows':len(limits),'hardness_rows':len(hard),'included':len(ledger),'groups':len(counts),'oracle_exact_match':lines==expected,'default_narrow_shared_multisets_equal':True,'unique_result_ids':True,'all_exact_activity_joins_unique':True,'basis_note':'Exact WQX approved characteristic basis established by EPA SRS indexed official record E1640416.'}
(out/'recompute_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
