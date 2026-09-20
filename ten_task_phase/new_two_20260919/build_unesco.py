import json
from pathlib import Path
P=Path(__file__).resolve().parent/'A/v1';P.mkdir(parents=True,exist_ok=True)
def put(n,x): (P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
items=[
('749ter','W-Arly-Pendjari Complex','IUCN','approve','IUCN printed pp5–6, PDF pp9–10'),
('985ter','Maloti-Drakensberg Park','ICOMOS','refer','ICOMOS printed p27, PDF p74'),
('1619bis','Ḥimā Cultural Area','ICOMOS','approve','ICOMOS printed p2, PDF p10'),
('806bis','Hallstatt-Dachstein / Salzkammergut Cultural Landscape','ICOMOS','approve','ICOMOS printed p4, PDF p16'),
('970bis','Wachau Cultural Landscape','ICOMOS','approve','ICOMOS printed p6, PDF p20'),
('1613bis','The Great Spa Towns of Europe','ICOMOS','approve','ICOMOS printed p8, PDF p24'),
('1608bis','Frontiers of the Roman Empire – The Danube Limes (Western Segment)','ICOMOS','approve','ICOMOS printed p10, PDF p30'),
('230quater','Abbey Church of Saint-Savin sur Gartempe','ICOMOS','approve','ICOMOS printed p13, PDF p41'),
('600bis','Paris, Banks of the Seine','ICOMOS','approve','ICOMOS printed p16, PDF p47'),
('933ter','The Loire Valley between Sully-sur-Loire and Chalonnes','ICOMOS','not_approve','ICOMOS printed p19, PDF p53'),
('288bis','Castles of Augustusburg and Falkenlust at Brühl','ICOMOS','approve','ICOMOS printed p21, PDF p58'),
('1127bis','Muskauer Park / Park Mużakowski','ICOMOS','approve','ICOMOS printed p23, PDF p62'),
('526bis','Colonial City of Santo Domingo','ICOMOS','approve','ICOMOS printed p25, PDF p68')]
raw=[]
for ident,name,body,rec,loc in items:
 raw.append(dict(id=ident,property=name,recommendations=[dict(body=body,action=rec,location=loc,source='https://whc.unesco.org/document/'+('206982' if body=='IUCN' else '206978'))]))
raw[1]['recommendations'].append(dict(body='IUCN',action='approve',location='IUCN printed pp11–12, PDF pp15–16',source='https://whc.unesco.org/document/206982'))
put('source_fields.json',dict(acquired='2026-09-19',universe_source='https://whc.unesco.org/document/206974',universe_location='printed p1: 13 requests',candidates=raw,
 decisions=[dict(id='985ter',action='approve',code='46 COM 8B.32',source='https://whc.unesco.org/en/decisions/8623/',location='operative paragraphs 2–3',deadline='2024-12-01'),dict(id='933ter',action='not_approve',code='46 COM 8B.40',source='https://whc.unesco.org/en/decisions/8632/',location='operative paragraph 2',deadline=None)],
 buffer_components=[dict(id='985ter',country='Lesotho',status='existing',ha=46630,source='https://whc.unesco.org/document/206982',location='printed p11 §2 final area paragraph'),dict(id='985ter',country='South Africa',status='new',layer=1,ha=69754,source='https://whc.unesco.org/document/206982',location='printed p11 §2'),dict(id='985ter',country='South Africa',status='new',layer=2,ha=213525,source='https://whc.unesco.org/document/206982',location='printed p11 §2')]))
put('rules.json',dict(columns=['property','advisory_body','recommendation','new_buffer_country','added_buffer_ha','total_buffer_ha','followup_due'],row_key=['property'],fields={
 'property':{'aliases':{'Maloti–Drakensberg Park':'Maloti-Drakensberg Park','Maloti Drakensberg Park':'Maloti-Drakensberg Park','985':'Maloti-Drakensberg Park','985ter':'Maloti-Drakensberg Park','985 Ter':'Maloti-Drakensberg Park'}},
 'advisory_body':{'uppercase':True},'recommendation':{'uppercase':True,'aliases':{'Referral':'REFER','referral':'REFER','Referred back':'REFER','referred back':'REFER','Refer':'REFER'}},
 'new_buffer_country':{'aliases':{'Republic of South Africa':'South Africa','ZA':'South Africa','ZAF':'South Africa'}},
 'added_buffer_ha':{'type':'integer','aliases':{'283,279':'283279','283 279':'283279'},'units':{'ha':{},'hectares':{}}},
 'total_buffer_ha':{'type':'integer','aliases':{'329,909':'329909','329 909':'329909'},'units':{'ha':{},'hectares':{}}},
 'followup_due':{'aliases':{'1 December 2024':'2024-12-01','December 1, 2024':'2024-12-01','2024/12/01':'2024-12-01','01 December 2024':'2024-12-01'}}}))
