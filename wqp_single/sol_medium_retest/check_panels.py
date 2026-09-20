#!/usr/bin/env python3
"""Check complete derived activity panels against the original eligible activity ledger."""
import collections,csv,json,pathlib
from decimal import Decimal,InvalidOperation
T=pathlib.Path(__file__).resolve().parent
ref=T.parent/'candidates/wqp_activity_panel_001/r03/private/reference/initial_state/activity_ledger.jsonl'
acts=[json.loads(l) for l in ref.read_text().splitlines()];acts=[a for a in acts if a['eligible']]
def norm(v):return format(Decimal(v).normalize(),'f')
expected=collections.Counter((a['organization'],a['activity'],a['site'],a['date'],a['time'],*[norm(a['values'][f]) for f in ['dissolved_oxygen_mg_L','temperature_deg_C','specific_conductance_uS_cm','pH']]) for a in acts)
aliases=[['org','organization','OrganizationIdentifier'],['aid','act','activity','ActivityIdentifier'],['sid','station','site','MonitoringLocationIdentifier'],['dt','adate','date','ActivityStartDate'],['tm','atime','time','ActivityStartTime/Time'],['oxy','oxygen','do','dissolved_oxygen_mg_L','do_mg_l'],['temp','temperature_deg_C'],['cond','sc','specific_conductance_uS_cm'],['ph','pH']]
results=[]
for job in json.loads((T/'analysis_plan.json').read_text())['jobs']:
 if job['comparison_task']!='new':continue
 run=pathlib.Path(job['out']);D=run/'downloaded_data'
 if not (D/'registry.json').exists():continue
 matches=[]
 for fid,m in json.loads((D/'registry.json').read_text()).items():
  if not m.get('derived'):continue
  rs=list(csv.DictReader((D/m['path']).open()))
  if not rs or not 800<=len(rs)<=1100:continue
  selected=[next((c for c in names if c in rs[0]),None) for names in aliases]
  if any(c is None for i,c in enumerate(selected) if i!=4):continue
  compared_expected=expected if selected[4] else collections.Counter(tuple(list(k[:4])+['']+list(k[5:])) for k in expected.elements())
  try:actual=collections.Counter(tuple(r[c] if c else '' for c in selected[:5])+tuple(norm(r[c]) for c in selected[5:]) for r in rs)
  except (InvalidOperation,ValueError):continue
  matches.append({'file_id':fid,'path':str((D/m['path']).relative_to(T)),'columns':selected,'rows':len(rs),'reference_eligible_rows':len(acts),'time_compared':bool(selected[4]),'exact_multiset_match':actual==compared_expected,'missing':sum((compared_expected-actual).values()),'different_or_extra':sum((actual-compared_expected).values())})
 results.append({'label':job['label'],'full_panel_checks':matches,'has_exact_panel_match':any(m['exact_multiset_match'] for m in matches)})
report={'fields':['organization','activity','station','actual_date','time','DO','temperature','conductance','pH'],'reference_eligible_rows':len(acts),'runs':results,'scope':'Only recognized derived complete panels (time compared when present; otherwise explicitly omitted from both projections), compared as full multisets to original eligible ledger using exact decimal equivalence. This supplements official raw response field checks; no inference from unrecognized/missing panels and no source fetch or model invocation.'}
(T/'panel_comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps([{'label':r['label'],'exact_panel_match':r['has_exact_panel_match']} for r in results]))
