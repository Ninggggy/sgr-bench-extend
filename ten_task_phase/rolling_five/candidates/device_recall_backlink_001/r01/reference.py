#!/usr/bin/env python3
"""Recompute finite source scope and exact backlink membership from live-web captures.
No network calls. No final application-to-status mapping is encoded here.
"""
import argparse,json,re
from pathlib import Path
from urllib.parse import urlparse,parse_qs

HERE=Path(__file__).resolve().parent

def dump(out,name,value):
 (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def field(text,label,next_label):
 return text.split(label,1)[1].split(next_label,1)[0]

def parsed_capture(item,source_dir):
 text=(source_dir/item['file']).read_text()
 ref=re.search(r'(turn\d+view\d+)',text)[1]
 url=re.search(r'\((https://[^\n]+)\)\n',text)[1]
 origin=re.search(r'Source: (click|open)\((\{.*?\})\);',text)
 assert ref==item['id'] and url==item['url']
 return {**item,'text':text,'url':url,'origin':{'op':origin[1],**json.loads(origin[2])} if origin else None}

def query(page,key):
 return {k.lower():v for k,v in parse_qs(urlparse(page['url']).query).items()}.get(key.lower(),[None])[0]

def row_links(page):
 matches=re.findall(r'(\d+)†([^\n]*?) \| ([123])  \| (\d{2}/\d{2}/\d{4})  \| FEI',page['text'])
 return [{'link_id':int(n),'display_description':title,'display_class':cl,'display_posted':date} for n,title,cl,date in matches]

def source_identity(page):
 t=page['text']
 return {'record_id':query(page,'id'),'recall_number':re.search(r'Recall Number (Z-\d+-\d+)',t)[1],'date_posted':re.search(r'Date Posted ([^\n]+)',t)[1]}

def build(source_dir,out):
 manifest=json.loads((source_dir/'source_manifest.json').read_text())
 captures=[parsed_capture(x,source_dir) for x in manifest['sources']]
 byref={x['id']:x for x in captures}
 clicked={}
 for cap in captures:
  orig=cap['origin']
  if orig and orig['op']=='click':
   clicked[(orig['ref_id'],orig['id'])]=cap
 root=byref[manifest['root_source']]
 rootid=source_identity(root)
 appfield=field(root['text'],'510(K)Number','Product Classification')
 apps=re.findall(r'(\d+)†(K\d{6})',appfield)
 assert apps and len({a for _,a in apps})==len(apps)
 scope=[]; oracle=[]; derivation=[]
 for source_link,app in apps:
  registration=clicked[(root['id'],int(source_link))]
  assert query(registration,'id')==app
  assert re.search(r'510\(k\) Number '+re.escape(app),registration['text'])
  recalls_link=int(re.search(r'(\d+)†CDRH Recalls',registration['text'])[1])
  first=clicked[(registration['id'],recalls_link)]
  assert first['role']=='index' and query(first,'knumber')==app
  pages=sorted([c for c in captures if c['role']=='index' and query(c,'knumber')==app],key=lambda c:int(query(c,'start_search')))
  assert pages[0]['id']==first['id']
  expected_start=1; total=None; allrows=[]; page_ranges=[]
  for page in pages:
   a,b,n=map(int,re.search(r'(\d+) to (\d+) of (\d+) Results',page['text']).groups())
   if total is None: total=n
   assert n==total and a==expected_start and int(query(page,'start_search'))==a
   assert re.search(r'510\(K\) Number: '+re.escape(app),page['text'])
   if page is not first:
    orig=page['origin']; assert orig['op']=='click' and orig['ref_id']==first['id']
    assert f'{orig["id"]}†' in first['text']
   rs=row_links(page)
   assert len(rs)==b-a+1
   for offset,row in enumerate(rs):
    row.update(application=app,position=a+offset,page_ref=page['id'])
    target=clicked.get((page['id'],row['link_id']))
    if target and target['role']=='linked_detail':
     record_id=query(target,'id')
     assert re.fullmatch(r'\d+',record_id or '')
     row.update(target_record_id=record_id,target_url=target['url'],target_source=target['id'])
     rn=re.search(r'Recall Number (Z-\d+-\d+)',target['text'])
     row['target_recall_number']=rn[1] if rn else None
    else:
     row.update(target_record_id=None,target_url=None,target_source=None,target_recall_number=None)
    allrows.append(row)
   page_ranges.append([a,b,n]); expected_start=b+1
  assert expected_start==total+1 and len(allrows)==total
  matching=[r for r in allrows if r['target_record_id']==rootid['record_id']]
  if matching:
   assert all(r['target_recall_number']==rootid['recall_number'] for r in matching)
   status='PRESENT'
   basis='At least one actual displayed link resolves to the exact source record; remaining unresolved targets are immaterial to positive membership.'
  else:
   assert all(r['target_record_id'] is not None for r in allrows), 'Unresolved exact targets cannot prove ABSENT'
   status='ABSENT'
   basis='Every displayed row has a resolved official record ID, and none equals the source ID. No date/name inference.'
  scope.append({'application':app,'source_reference_link':int(source_link),'registration_ref':registration['id'],'index_ref':first['id'],'announced_total':total,'page_ranges':page_ranges,'complete':True,'rows':allrows})
  oracle.append((app,status));derivation.append({'application':app,'status':status,'basis':basis,'resolved_target_count':sum(r['target_record_id'] is not None for r in allrows),'matching_targets':matching})
 oracle.sort()
 out.mkdir(parents=True,exist_ok=True)
 (out/'oracle.psv').write_text('APPLICATION_510K|BACKLINK_STATUS\n'+''.join(f'{a}|{s}\n' for a,s in oracle))
 dump(out,'inventory.json',{'root':rootid,'application_set_complete':True,'applications':scope})
 dump(out,'reference_derivation.json',{'root':rootid,'rows':derivation,'identity_method':'Actual click source ref/link ID to official final record URL; no title/date equivalence assumption','all_application_rows_included':True,'excluded_applications':[],'observation_date':manifest['source_observation_date']})
 print(json.dumps({'applications':len(oracle),'oracle':oracle,'scope_rows':sum(x['announced_total'] for x in scope)}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,default=HERE);p.add_argument('--out-dir',type=Path,default=HERE)
 args=p.parse_args();build(args.source_dir,args.out_dir)
