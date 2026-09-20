#!/usr/bin/env python3
"""Compare retrieved source fields to preserved official reference data, not model prose."""
import collections,csv,io,json,pathlib,zipfile
T=pathlib.Path(__file__).resolve().parent;S=T.parent/'candidates/wqp_activity_panel_001/r03/private/sources'
def csvrows(p):
 data=p.read_bytes()
 if data[:2]==b'PK':
  with zipfile.ZipFile(io.BytesIO(data)) as z:data=z.read(next(n for n in z.namelist() if n.lower().endswith('.csv')))
 return list(csv.DictReader(io.StringIO(data.decode('utf-8-sig'))))
def main():
 fields={'Station':['OrganizationIdentifier','MonitoringLocationIdentifier','MonitoringLocationName','MonitoringLocationTypeName','HUCEightDigitCode'],'Activity':['OrganizationIdentifier','ActivityIdentifier','MonitoringLocationIdentifier','ActivityStartDate','ActivityStartTime/Time','ActivityMediaName','ActivityTypeCode'],'Result':['OrganizationIdentifier','ActivityIdentifier','MonitoringLocationIdentifier','ActivityStartDate','USGSPCode','ResultMeasureValue','ResultMeasure/MeasureUnitCode','ResultStatusIdentifier','ResultValueTypeName','ResultDetectionConditionText','MeasureQualifierCode']}
 stems={'Station':'station_2000_2019_explicit_hucs','Activity':'activity_2000_2019_trinity_zip','Result':'narrow_2000_2019_trinity_panel_zip'}
 source={k:csvrows(S/(v+'.response')) for k,v in stems.items()};mainstem={r['MonitoringLocationIdentifier'] for r in source['Station'] if r['MonitoringLocationName'].startswith('Trinity Rv ') and r['MonitoringLocationTypeName'] in ['Stream','Stream: Tidal stream']}
 expected={k:collections.Counter(tuple(r.get(c,'') for c in fields[k]) for r in rows if (k=='Station' or r['MonitoringLocationIdentifier'] in mainstem) and (k!='Result' or r['USGSPCode'] in ['00010','00095','00300','00400'])) for k,rows in source.items()}
 output=[]
 for job in json.loads((T/'analysis_plan.json').read_text())['jobs']:
  if job['comparison_task']!='new':continue
  run=pathlib.Path(job['out']);d=run/'downloaded_data';rp=d/'registry.json'
  if not rp.exists():continue
  reg=json.loads(rp.read_text());files=[]
  for fid,m in reg.items():
   if m.get('derived') or m.get('status')!=200:continue
   kind=next((k for k in fields if '/data/'+k+'/search' in m.get('url','')),None)
   if kind is None:continue
   p=d/m['path']
   if p.read_bytes()[:2]==b'PK':continue # uncompressed registered member is checked once
   try:rs=csvrows(p)
   except (ValueError,UnicodeError):continue
   if not rs or not all(c in rs[0] for c in fields[kind]):continue
   actual=collections.Counter(tuple(r.get(c,'') for c in fields[kind]) for r in rs if (kind=='Station' or r.get('MonitoringLocationIdentifier') in mainstem) and (kind!='Result' or r.get('USGSPCode') in ['00010','00095','00300','00400']))
   extra=actual-expected[kind];missing=expected[kind]-actual
   files.append({'file_id':fid,'path':str(p.relative_to(T)),'kind':kind,'source_url':m.get('url'),'rows_total':len(rs),'rows_in_comparison_scope':sum(actual.values()),'reference_scope_rows':sum(expected[kind].values()),'different_or_extra_projected_rows':sum(extra.values()),'reference_rows_not_in_this_response':sum(missing.values()),'exact_full_scope_multiset':actual==expected[kind],'different_rows_preview':[{'fields':list(v),'count':n} for v,n in list(extra.items())[:20]]})
  output.append({'label':job['label'],'files':files})
 result={'comparison_fields':fields,'runs':output,'interpretation':'Fieldwise multiset comparison against original raw official responses. Narrow queries may legitimately omit reference rows; omission alone is not source drift or incomplete solver coverage. Exact-full-scope means these decisive fields match, not every metadata column or all future sources. Old004 HTML requires separate review.'}
 (T/'source_comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps([{'label':r['label'],'files':len(r['files']),'full_scope_matches':[f['kind'] for f in r['files'] if f['exact_full_scope_multiset']],'different_rows':sum(f['different_or_extra_projected_rows'] for f in r['files'])} for r in output]))
if __name__=='__main__':main()
