#!/usr/bin/env python3
"""Recompute the reported-evidence ledger from saved public records; no network."""
import csv, json, math
from collections import Counter, defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent
EVIDENCE=HERE.parents[2]/'opportunities/wqp_censored_screening/evidence'
SAMPLE_COLS=['result_id','evidence','lower_ug_l','upper_ug_l','hardness_state','hardness_mg_l','screen']
COLS=['evidence','hardness_state','screen','n_results']
def read(name):
    return list(csv.DictReader((EVIDENCE/name).open(encoding='utf-8-sig')))
def number(s):
    return format(float(s),'.12g')
def criterion(h):
    return math.exp(.7409*math.log(h)-4.719)*(1.101672-.041838*math.log(h))
def calculate():
    cadmium=read('d0002.response'); limits=defaultdict(list); hardness=defaultdict(list)
    for r in read('d0003.response'): limits[r['ResultIdentifier']].append(r)
    for r in read('d0004.response'): hardness[(r['OrganizationIdentifier'],r['ActivityIdentifier'])].append(r)
    assert len(cadmium)==len({r['ResultIdentifier'] for r in cadmium})
    output=[]; audit=[]; excluded=[]
    for r in cadmium:
        rid=r['ResultIdentifier']
        if r['ResultSampleFractionText']!='Dissolved':
            excluded.append({'result_id':rid,'fraction':r['ResultSampleFractionText'],'reason':'not_dissolved'});continue
        assert r['CharacteristicName']=='Cadmium'
        ls={}
        for l in limits[rid]:
            assert l['ActivityIdentifier']==r['ActivityIdentifier']
            assert l['DetectionQuantitationLimitMeasure/MeasureUnitCode']=='ug/L'
            t=l['DetectionQuantitationLimitTypeName'];v=float(l['DetectionQuantitationLimitMeasure/MeasureValue'])
            assert t not in ls or ls[t]==v
            ls[t]=v
        lo=hi=None;q=r['MeasureQualifierCode'];condition=r['ResultDetectionConditionText']
        if condition=='Not Reported': e='not_reported'
        elif q=='DL' and condition=='Not Detected':
            e='below_mdl';lo=0.;hi=ls.get('Method Detection Level')
        elif q=='U' and condition=='Not Detected':
            # U specifies an adjusted CRQL, not an arbitrary available limit.
            e='unresolved_u_limit'
        elif q=='J-R' and not condition:
            e='between_mdl_rl';lo=ls.get('Method Detection Level');hi=ls.get('Lower Reporting Limit')
            if lo is not None and hi is not None:
                assert lo<float(r['ResultMeasureValue'])<hi
        elif not q and not condition and r['ResultMeasureValue']:
            assert r['ResultMeasure/MeasureUnitCode']=='ug/L'
            e='point';lo=hi=float(r['ResultMeasureValue'])
        else: raise ValueError(('unhandled cadmium evidence',rid,q,condition))
        hh=hardness[(r['OrganizationIdentifier'],r['ActivityIdentifier'])]
        h=None
        if not hh: hs='missing'
        elif len(hh)!=1: hs='ambiguous'
        else:
            hr=hh[0]
            if hr['ResultDetectionConditionText']=='Not Reported' or hr['MeasureQualifierCode']=='QC': hs='withdrawn'
            # EPA SRS E1640416 maps this exact WQX-approved characteristic
            # to total hardness expressed as CaCO3 equivalents (indexed record).
            elif hr['CharacteristicName']!='Hardness, Ca, Mg': hs='basis_unverified'
            elif hr['ResultMeasure/MeasureUnitCode']!='mg/L' or not hr['ResultMeasureValue']: hs='unusable'
            else:
                h=float(hr['ResultMeasureValue']);assert h>0;hs='available'
        c=criterion(h) if h is not None else None
        if e=='not_reported':screen='not_reported'
        elif lo is None or hi is None:screen='unresolved_limit'
        elif c is None:screen='unresolved_hardness'
        elif hi<=c:screen='below_or_equal'
        elif lo>c or (e=='between_mdl_rl' and lo==c):screen='above'
        else:screen='crosses'
        output.append([rid,e,number(lo) if lo is not None else 'NA',number(hi) if hi is not None else 'NA',hs,number(h) if h is not None else 'NA',screen])
        audit.append({'result_id':rid,'activity_id':r['ActivityIdentifier'],'date':r['ActivityStartDate'],'qualifier':q,'limits':ls,'criterion_ug_l_unrounded':c,'hardness_record':hh,'screen':screen})
    output.sort()
    return output,{'source_rows':len(cadmium),'included_rows':len(output),'excluded':excluded,'counts':dict(Counter(r[-1] for r in output)),'hardness_counts':dict(Counter(r[4] for r in output)),'rows':audit}
def render(rows): return '|'.join(COLS)+'\n'+'\n'.join('|'.join(r) for r in rows)+'\n'
if __name__=='__main__':
    rows,audit=calculate()
    (HERE/'sample_ledger.psv').write_text('|'.join(SAMPLE_COLS)+'\n'+'\n'.join('|'.join(r) for r in rows)+'\n')
    counts=Counter((r[1],r[4],r[6]) for r in rows)
    grouped=[list(key)+[str(counts[key])] for key in sorted(counts)]
    (HERE/'oracle.psv').write_text(render(grouped))
    (HERE/'inclusion_and_calculation.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps({k:v for k,v in audit.items() if k not in ['rows','excluded']}))
