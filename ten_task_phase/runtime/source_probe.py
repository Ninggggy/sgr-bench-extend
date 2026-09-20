#!/usr/bin/env python3
import os, json, pathlib, sys
os.environ['SGR_RATE_LIMITER']='http://127.0.0.1:18763/kegg'
sys.path.insert(0,str(pathlib.Path(__file__).parent))
import data_tools as d
b=pathlib.Path(__file__).resolve().parents[1]/'research/source_probe';b.mkdir(exist_ok=True);d.DATA=b
if (b/'registry.json').exists():d.REG.update(json.loads((b/'registry.json').read_text()))
urls=sys.argv[1:] or ['https://comptox.epa.gov/chemexpo/static/user_guide/bulk_data.html','https://comptox.epa.gov/chemexpo/downloads/','https://rest.kegg.jp/info/kegg','https://reptile-database.reptarium.cz/advanced_search','https://wateroffice.ec.gc.ca/search/historical_e.html','https://www.waterqualitydata.us/webservices_documentation/']
for u in urls:
 try:
  r=d.fetch({'url':u});print(json.dumps({'url':u,'id':r['file_id'],'status':r['status'],'bytes':r['bytes'],'preview':r.get('preview','')[:150]}),flush=True)
 except Exception as e:print(json.dumps({'url':u,'error':str(e)}),flush=True)
