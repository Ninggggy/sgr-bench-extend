#!/usr/bin/env python3
"""Recompute complete station/year/window evidence and seasonal event panels.
Reads original official CSV/ZIP bodies; contains no winning site/window/event IDs.
"""
import collections,csv,datetime,io,itertools,json,pathlib,sqlite3,zipfile
from decimal import Decimal,InvalidOperation,ROUND_HALF_UP
B=pathlib.Path(__file__).resolve().parent/'initial_state';B.mkdir(exist_ok=True);P=B.parent.parent;S=P/'sources'
CODES={'00010':'temperature_deg_C','00095':'specific_conductance_uS_cm','00300':'dissolved_oxygen_mg_L','00400':'pH'}
SF='station_2000_2019_explicit_hucs';AF='activity_2000_2019_trinity_zip';RF='narrow_2000_2019_trinity_panel_zip';WF='wide_mainstem_2000_2019_panel_zip'
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def jsonl(p,x):p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in x))
def source(stem):
 receipt=json.loads((S/(stem+'.json')).read_text());assert receipt['complete'] and receipt['receipt']['http_code']==200,stem
 data=(S/(stem+'.response')).read_bytes();member=None
 if data[:2]==b'PK':
  with zipfile.ZipFile(io.BytesIO(data)) as z:
   files=[n for n in z.namelist() if n.lower().endswith('.csv')];assert len(files)==1;member=files[0];data=z.read(member)
 rows=list(csv.DictReader(io.StringIO(data.decode('utf-8-sig'))))
 for i,r in enumerate(rows,2):r['_record']=i;r['_source']=stem;r['_member']=member
 return rows
def ak(r):return (r['OrganizationIdentifier'],r['ActivityIdentifier'])
def sk(r):return (r['OrganizationIdentifier'],r['MonitoringLocationIdentifier'])
def evidence(r,field=None):return {'source_id':r['_source'],'archive_member':r['_member'],'csv_record':r['_record'],'organization':r['OrganizationIdentifier'],'activity':r.get('ActivityIdentifier'),'result_id':r.get('ResultIdentifier'),'field':field,'raw_value':r.get(field) if field else None}
def value(r):
 c=r['USGSPCode'];u=r['ResultMeasure/MeasureUnitCode'];v=Decimal(r['ResultMeasureValue'])
 if not v.is_finite():raise ValueError('nonfinite')
 if c=='00010':
  if u=='deg C':return v
  if u=='deg F':return (v-32)*5/9
 if c=='00095':
  if u in ['uS/cm @25C','uS/cm','umho/cm']:return v
  if u=='mS/cm':return v*1000
 if c=='00300':
  if u in ['mg/l','mg/L']:return v
  if u in ['ug/l','ug/L']:return v/1000
 if c=='00400' and u in ['std units','None','SU','s.u.']:return v
 raise ValueError('incompatible_or_missing_unit')
def valid(r,relax_status=False):
 if r['USGSPCode'] not in CODES:return False,'outside_panel'
 if not relax_status and r['ResultStatusIdentifier'] not in ['Accepted','Final']:return False,'status'
 if r['ResultValueTypeName']!='Actual':return False,'value_type'
 if r['ResultDetectionConditionText'].strip() or r['MeasureQualifierCode'].strip():return False,'qualifier'
 try:value(r)
 except (InvalidOperation,ValueError):return False,'numeric_or_unit'
 return True,'usable'
def fmt(v):return str(Decimal(v).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
def tie(a):return (Decimal(a['values']['dissolved_oxygen_mg_L']),a['date'],a['time'] or '\uffff',a['activity'])
def make_support(acts,sites,years):
 counts=collections.Counter((a['site_key'],a['year'],a['quarter']) for a in acts if a['eligible'])
 return {k:{y for y in years if all(counts[k,y,q] for q in range(1,5))} for k in sites},counts
def windows(support,years):
 out=[]
 for lo in years:
  for hi in years:
   if hi<lo:continue
   cohort=sorted(k for k,ys in support.items() if all(y in ys for y in range(lo,hi+1)))
   out.append({'start_year':lo,'end_year':hi,'duration':hi-lo+1,'cohort':cohort,'coverage':len(cohort),'feasible':len(cohort)>=2})
 feasible=[w for w in out if w['feasible']]
 for w in out:
  w['dominators']=[[x['start_year'],x['end_year']] for x in feasible if x['duration']>=w['duration'] and x['coverage']>=w['coverage'] and (x['duration']>w['duration'] or x['coverage']>w['coverage'])] if w['feasible'] else []
  w['frontier']=w['feasible'] and not w['dominators']
 return out
def brief(wins):return [{'start_year':w['start_year'],'end_year':w['end_year'],'duration':w['duration'],'coverage':w['coverage'],'cohort':w['cohort']} for w in wins if w['frontier']]
def produce(front,acts,stations,cols,full_record=False,independent_minima=False):
 rows=[];trace=[]
 for w in front:
  for k in w['cohort']:
   st=stations[k]
   for q in range(1,5):
    eligible=[a for a in acts if a['eligible'] and a['site_key']==k and a['quarter']==q and (full_record or w['start_year']<=a['year']<=w['end_year'])]
    a=min(eligible,key=tie);v=dict(a['values'])
    if independent_minima:
     for f in ['temperature_deg_C','specific_conductance_uS_cm','pH']:v[f]=str(min(Decimal(x['values'][f]) for x in eligible))
    row=[str(w['start_year']),str(w['end_year']),str(w['coverage']),*k,st['HUCEightDigitCode'],'Q'+str(q),str(len(eligible)),a['activity'],a['date'],*[fmt(v[c]) for c in ['dissolved_oxygen_mg_L','temperature_deg_C','specific_conductance_uS_cm','pH']]]
    rows.append(row);trace.append({'row_key':[row[0],row[1],*k,row[6]],'window':[w['start_year'],w['end_year']],'site_key':k,'quarter':q,'selected_activity':a,'counted_activity_keys':[[x['organization'],x['activity']] for x in eligible],'station_evidence':evidence(st)})
 return rows,trace
def main():
 definition=json.loads((P/'task_definition.json').read_text());cols=definition['initial_state_columns'];years=list(range(definition['years'][0],definition['years'][1]+1));hucs=definition['hucs']
 stations=source(SF);activities=source(AF);results=source(RF);wide=source(WF)
 smap={sk(s):s for s in stations};amap={ak(a):a for a in activities};assert len(smap)==len(stations) and len(amap)==len(activities)
 assert all(s['OrganizationIdentifier']==definition['organization'] and s['HUCEightDigitCode'] in hucs for s in stations)
 assert all(sk(a) in smap and int(a['ActivityStartDate'][:4]) in years for a in activities)
 assert all(ak(r) in amap and sk(r)==sk(amap[ak(r)]) and r['ActivityStartDate']==amap[ak(r)]['ActivityStartDate'] for r in results)
 mainstem={k:s for k,s in smap.items() if s['MonitoringLocationName'].startswith('Trinity Rv ') and s['MonitoringLocationTypeName'] in ['Stream','Stream: Tidal stream']}
 mainacts=[a for a in activities if sk(a) in mainstem];mainresults=[r for r in results if sk(r) in mainstem]
 # Conservative result key, not a global bare identifier; same-key repeated bodies must agree.
 seen={};grouped=collections.defaultdict(list)
 for r in results:
  assert r['ResultIdentifier'];rk=(*ak(r),r['ResultIdentifier']);payload={k:v for k,v in r.items() if not k.startswith('_')}
  if rk in seen:assert seen[rk]==payload,'same scoped result key has conflicting payload'
  else:
   seen[rk]=payload
   if sk(r) in mainstem:grouped[ak(r)].append(r)
 projection=['OrganizationIdentifier','MonitoringLocationIdentifier','ActivityIdentifier','ActivityStartDate','USGSPCode','CharacteristicName','ResultMeasureValue','ResultMeasure/MeasureUnitCode','ResultStatusIdentifier','ResultValueTypeName','ResultDetectionConditionText','MeasureQualifierCode']
 assert collections.Counter(tuple(r[k] for k in projection) for r in mainresults)==collections.Counter(tuple(r[k] for k in projection) for r in wide),'independent wide export differs from regional narrow projection'
 for r in wide:
  for k in ['MonitoringLocationIdentifier','ActivityStartDate','ActivityStartTime/Time','ActivityTypeCode','ActivityMediaName','ActivityDepthHeightMeasure/MeasureValue','ActivityDepthHeightMeasure/MeasureUnitCode']:
   assert r[k]==amap[ak(r)][k],(ak(r),k)
 acts=[];resultledger=[];annual=collections.defaultdict(set);relaxed=[]
 for a in mainacts:
  vals=collections.defaultdict(set);relaxed_vals=collections.defaultdict(set);ev=collections.defaultdict(list)
  for r in grouped[ak(a)]:
   yes,reason=valid(r);resultledger.append({'key':[*ak(r),r['ResultIdentifier']],'eligible':yes,'reason':reason,'evidence':evidence(r)})
   if yes:vals[CODES[r['USGSPCode']]].add(value(r));ev[CODES[r['USGSPCode']]].append(evidence(r,'ResultMeasureValue'))
   if valid(r,True)[0]:relaxed_vals[CODES[r['USGSPCode']]].add(value(r))
  y=int(a['ActivityStartDate'][:4]);q=(int(a['ActivityStartDate'][5:7])-1)//3+1;k=sk(a)
  missing=[c for c in CODES.values() if not vals[c]];conflicting=[c for c in CODES.values() if len(vals[c])>1];complete=not missing and not conflicting
  item={'site_key':k,'organization':k[0],'site':k[1],'activity':a['ActivityIdentifier'],'date':a['ActivityStartDate'],'time':a['ActivityStartTime/Time'],'time_zone':a['ActivityStartTime/TimeZoneCode'],'year':y,'quarter':q,'activity_type':a['ActivityTypeCode'],'media':a['ActivityMediaName'],'routine_water':a['ActivityTypeCode']=='Sample-Routine' and a['ActivityMediaName']=='Water','panel_complete':complete,'missing':missing,'conflicting':conflicting,'values':{c:str(next(iter(v))) for c,v in vals.items() if len(v)==1},'value_evidence':dict(ev),'activity_evidence':evidence(a),'depth_metadata':{k:v for k,v in a.items() if 'Depth' in k}}
  item['eligible']=complete and item['routine_water'];acts.append(item);annual[k,y].update(c for c,v in vals.items() if v)
  rr=dict(item);rr['eligible']=rr['routine_water'] and all(len(relaxed_vals[c])==1 for c in CODES.values());relaxed.append(rr)
 support,counts=make_support(acts,mainstem,years);wins=windows(support,years);front=[w for w in wins if w['frontier']];rows,trace=produce(front,acts,mainstem,cols)
 stationledger=[];yearledger=[]
 for k,s in smap.items():
  retain=k in mainstem;stationledger.append({'key':k,'name':s['MonitoringLocationName'],'type':s['MonitoringLocationTypeName'],'HUC':s['HUCEightDigitCode'],'scope':True,'mainstem_name':s['MonitoringLocationName'].startswith('Trinity Rv '),'stream_type':s['MonitoringLocationTypeName'] in ['Stream','Stream: Tidal stream'],'candidate_retained':retain,'supported_years':sorted(support[k]) if retain else None,'in_frontier_cohorts':any(k in w['cohort'] for w in front),'decision':'eligible_mainstem_candidate' if retain else 'outside_mainstem_scope','unknown':[],'evidence':evidence(s)})
  if retain:
   for y in years:yearledger.append({'site_key':k,'year':y,'quarter_counts':{f'Q{q}':counts[k,y,q] for q in range(1,5)},'supported':y in support[k],'annual_indicator_presence':{c:c in annual[k,y] for c in CODES.values()},'activity_keys':[[a['organization'],a['activity']] for a in acts if a['site_key']==k and a['year']==y],'unknown':[]})
 fields=[]
 for row,t in zip(rows,trace):
  for col,v in zip(cols,row):
   e={'row_key':t['row_key'],'field':col,'output':v}
   if col in CODES.values():e.update(evidence=t['selected_activity']['value_evidence'][col],formula='same selected activity, declared unit conversion then Decimal HALF_UP to2dp')
   elif col in ['start_year','end_year','cohort_station_count']:e.update(evidence={'window_ledger':'window_ledger.jsonl','window':t['window']},formula='all feasible intervals compared globally by duration and exact cohort coverage')
   elif col=='eligible_activity_count':e.update(evidence=t['counted_activity_keys'],formula='distinct eligible activity identities in this station/interval/quarter-of-year')
   elif col in ['OrganizationIdentifier','MonitoringLocationIdentifier','HUC']:e.update(evidence=t['station_evidence'],formula='source station metadata')
   else:e.update(evidence=t['selected_activity']['activity_evidence'],formula='lowest unrounded DO within exact interval/season; date/time/ID tie rules')
   fields.append(e)
 # Real changes from replacing exact support with annual presence, envelopes, or relaxed sample/result conditions.
 ann_support={k:{y for y in years if len(annual[k,y])==4} for k in mainstem}
 env_support={k:set(range(min(ys),max(ys)+1)) if ys else set() for k,ys in support.items()}
 inc_types=[dict(a,eligible=a['panel_complete'] and a['media']=='Water') for a in acts]
 type_support,_=make_support(inc_types,mainstem,years);status_support,_=make_support(relaxed,mainstem,years)
 cf={'correct_frontier':brief(wins),'annual_indicators_instead_of_joint_quarterly_panels':brief(windows(ann_support,years)),'fill_gaps_using_supported_year_envelope':brief(windows(env_support,years)),'include_other_activity_types':brief(windows(type_support,years)),'accept_Historical_and_Preliminary':brief(windows(status_support,years))}
 for label,wrong in [('reuse_full_period_events',produce(front,acts,mainstem,cols,full_record=True)[0]),('independent_companion_minima',produce(front,acts,mainstem,cols,independent_minima=True)[0])]:
  cf[label]=[{'row_key':trace[i]['row_key'],'field':c,'correct':x,'incorrect':y} for i,(r,w) in enumerate(zip(rows,wrong)) for c,x,y in zip(cols,r,w) if x!=y]
 cf['redundant_in_observed_slice']={'conflicting_activities':sum(bool(a['conflicting']) for a in acts),'note':'Required identity/unit/missing rules are not automatically difficulty contributions; inspect actual counterfactual changes.'}
 # Independent wide-profile SQL: different implementation and independently fetched source query.
 con=sqlite3.connect(':memory:')
 def import_table(name,rs):
  cs=[c for c in rs[0] if not c.startswith('_')];quote=lambda c:'"'+c.replace('"','""')+'"';con.execute('CREATE TABLE '+name+' ('+','.join(quote(c)+' TEXT' for c in cs)+')');con.executemany('INSERT INTO '+name+' VALUES ('+','.join('?' for _ in cs)+')',[[r[c] for c in cs] for r in rs])
 import_table('stations',list(mainstem.values()));import_table('wide',wide)
 units={'00010':'deg C','00095':'uS/cm @25C','00300':'mg/l','00400':'std units'}
 assert all(r['ResultMeasure/MeasureUnitCode']==units[r['USGSPCode']] for r in wide if r['USGSPCode'] in units and valid(r)[0]),'SQL shortcut must not silently ignore a conversion'
 independent=con.execute((B/'independent_check.sql').read_text()).fetchall();ind_rows=[[str(x) for x in r[:10]]+[fmt(x) for x in r[10:]] for r in independent];assert rows==ind_rows,(rows,ind_rows)
 (B/'oracle.psv').write_text('\n'.join('|'.join(r) for r in rows)+'\n' if rows else 'NONE\n')
 jsonl(P/'candidate_universe.jsonl',[{**s,'enumeration':'complete unfiltered Station export for explicit12HUC8s and2000–2019'} for s in stations]);jsonl(P/'inclusion_ledger.jsonl',stationledger);jsonl(B/'station_year_ledger.jsonl',yearledger);jsonl(B/'window_ledger.jsonl',wins);jsonl(B/'activity_ledger.jsonl',acts);jsonl(B/'result_ledger.jsonl',resultledger);jsonl(B/'field_evidence.jsonl',fields);dump(B/'selected_activities.json',trace);dump(B/'counterfactuals.json',cf)
 verification={'status':'passed','station_universe':len(stations),'all_scope_activities':len(activities),'all_scope_results':len(results),'scoped_result_ids':len(seen),'mainstem_candidates':len(mainstem),'mainstem_activities':len(mainacts),'mainstem_result_rows':len(mainresults),'independent_wide_rows':len(wide),'eligible_activities':sum(a['eligible'] for a in acts),'station_year_decisions':len(yearledger),'interval_decisions':len(wins),'feasible_intervals':sum(w['feasible'] for w in wins),'frontier':brief(wins),'output_rows':len(rows),'field_evidence_count':len(fields),'unknowns_affecting_answer':0,'narrow_wide_common_projection_equal':True,'activity_metadata_equal':True,'independent_SQL_all_output_cells_equal':True}
 dump(B/'verification.json',verification);print(json.dumps(verification,indent=2))
if __name__=='__main__':main()
