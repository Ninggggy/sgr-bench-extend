#!/usr/bin/env python3
"""Recompute suggested reference from captured inputs; no network or model calls.
Event extraction is mechanical. annotations.json records the reviewer's
source-grounded inclusion decisions, and is not inferred from event authors alone.
"""
import json,re,csv,argparse
from pathlib import Path
from html.parser import HTMLParser
from datetime import datetime
import xml.etree.ElementTree as ET
B=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(description='Offline r04 reference; never reads the supplied oracle. No network/model calls.')
ap.add_argument('--source-dir',type=Path,default=B/'sources')
ap.add_argument('--out-dir',type=Path,required=True)
args=ap.parse_args(); S=args.source_dir; P=args.out_dir
if P.resolve() in (S.resolve(),B): raise ValueError('Output must be distinct from sources and candidate bundle')
P.mkdir(parents=True,exist_ok=True)
class Text(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]
    def handle_data(self,d): self.parts.append(d)
    def handle_starttag(self,t,a):
        if t in ('br','p','div'): self.parts.append('\n')
    def value(self): return re.sub(r'[ \t\xa0]+',' ',''.join(self.parts)).strip()
def txt(s):
    p=Text(); p.feed(s); return p.value()
def write(name,obj): (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
ns={'i':'http://www.iana.org/assignments'}
root=ET.parse(S/'registry.xml').getroot()
table=root.find("i:registry[@id='tls-extensiontype-values-1']",ns)
records=[]
for i,e in enumerate(table.findall('i:record',ns),1):
    rec={'record_index':i,**{k:e.findtext('i:'+k,default='',namespaces=ns) for k in ('value','name','dtls-only')}}
    rec['references']=[x.attrib for x in e.findall('i:xref',ns)]
    rec['included']=rec['value'].isdigit() and rec['dtls-only']=='Y' and 'deprecated' in rec['name'].lower()
    rec['reason']='individual numeric, DTLS-only Y, deprecated name' if rec['included'] else 'outside conjunction: '+', '.join(x for x,b in [('individual numeric',rec['value'].isdigit()),('DTLS-only Y',rec['dtls-only']=='Y'),('deprecated name','deprecated' in rec['name'].lower())] if not b)
    records.append(rec)
write('registry_scope.json',records)
html=(S/'history.html').read_text()
events=[]
for m in re.finditer(r'<tr id="(history-\d+)">(.*?)</tr>',html,re.S):
    cells=re.findall(r'<td\b[^>]*>(.*?)</td>',m[2],re.S)
    if len(cells)!=4: raise ValueError((m[1],len(cells)))
    action=re.sub(r'<div class="snippet">.*?</div>','',cells[3],flags=re.S)
    stamp=re.search(r'title="([^"]+)"',cells[0])[1]
    body=txt(action)
    if 'IANA Functions Operator has completed its review' in body:
        cat='substantive_iana_review_candidate'
    elif re.search(r'IANA.*[Ss]tate changed|IANA state changed',body): cat='iana_administrative_state'
    elif 'IANA' in body or re.search(r'\b53\b',body): cat='other_comment_with_iana_or_53'
    else: cat='other_event'
    events.append({'event_id':m[1],'html_line':html.count('\n',0,m.start())+1,'timestamp':stamp,'date':txt(cells[0]),'revision':txt(cells[1]),'actor':txt(cells[2]),'category':cat,'action':body})
assert len(events)==len(set(x['event_id'] for x in events))
write('events.json',events)
from collections import Counter
write('observation.json',{'registry_record_count':len(records),'in_scope':[x for x in records if x['included']], 'history_event_count':len(events),'date_min':min(x['date'] for x in events),'date_max':max(x['date'] for x in events),'categories':dict(Counter(x['category'] for x in events)),'has_pagination_marker':bool(re.search(r'pagination|load.more|rel="next"|page=',html,re.I)), 'history_first_event':events[0]['event_id'],'history_last_event':events[-1]['event_id'],'coverage_limit':'Complete returned official draft-family History HTML, including expanded full comment bodies; no assertion of all unrecorded/off-page correspondence.'})
with (P/'event_index.tsv').open('w') as f:
    w=csv.writer(f,delimiter='\t');w.writerow(['event_id','date','revision','actor','category','html_line','summary'])
    for e in events: w.writerow([e[k] for k in ['event_id','date','revision','actor','category','html_line']]+[e['action'][:180].replace('\n',' ')])
annfile=B/'annotations.json'
if annfile.exists():
    ann=json.loads(annfile.read_text()); byid={e['event_id']:e for e in events}; rows=[]
    if {e['event_id'] for e in ann['event_decisions']} != set(byid): raise ValueError('UNRESOLVED: event annotation coverage differs')
    if {e['value'] for e in records if e['included']} != set(ann['allocation_mappings']): raise ValueError('UNRESOLVED: registry scope differs from reviewed mappings')
    for record in (x for x in records if x['included']):
        mapping=ann['allocation_mappings'][record['value']]
        spec=(S/mapping['source_file']).read_text()
        section=spec.split('10.2.  New Entry in the TLS ExtensionType Values Registry')[-1].split('10.3.')[0]
        replacement=re.search(r'connection_id\((\d+)\)',section)[1]
        early=re.search(r'value (\d+) had been allocated by early allocation',section)[1]
        assert early==record['value'] and 'deprecated in' in section
        eligible=[]
        for review in ann['event_decisions']:
            if review['include'] and review['deprecated_value']==record['value']:
                event=byid[review['event_id']]
                draft=re.search(r'completed its review of (draft-[\w-]+-\d+)\.',event['action'])[1]
                proposed=re.search(r'\nValue: (\d+)\n',event['action'])[1]
                assert draft==mapping['draft_family']+'-'+event['revision']
                assert event['date'] < mapping['publication_month']+'-01'
                eligible.append((datetime.strptime(event['timestamp'],'%Y-%m-%d %H:%M:%S %z'),event,draft,proposed))
        eligible.sort(key=lambda x:x[0],reverse=True)
        if not eligible:
            rows.append([record['value'],replacement,'NONE','NONE','NONE']); continue
        assert len(eligible)==1 or eligible[0][0]!=eligible[1][0], 'ambiguous latest'
        _,event,draft,proposed=eligible[0]
        rows.append([record['value'],replacement,event['date'],draft,proposed])
    rows.sort(key=lambda x:int(x[0]))
    with (P/'oracle.psv').open('w') as f:
        if rows: f.write('deprecated_value|published_replacement_value|review_date|reviewed_draft|proposed_permanent_value\n')
        else: f.write('NONE\n')
        for row in rows: f.write('|'.join(row)+'\n')
    write('reference_derivation.json',{'rows':rows,'semantic_annotation_required':True,'formal_oracle':True,'model_tests':0})
print((P/'observation.json').read_text())
