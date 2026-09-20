#!/usr/bin/env python3
"""Read-only research MCP: official HTTPS retrieval, paged text, in-memory SQLite.
No shell, arbitrary Python, filesystem paths, extensions, or database attachments.
Only response files registered in this isolated session can be read.
"""
import os, html
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
import csv, datetime as dt, io, json, re, sqlite3, sys, time, urllib.request, urllib.parse, urllib.error, zipfile
from pathlib import Path
DATA=Path('/work/data')
ALLOWED={
'www.waterqualitydata.us','waterqualitydata.us','www.epa.gov','cdx.epa.gov','comptox.epa.gov','gaftp.epa.gov','figshare.com','doi.org','epa.figshare.com','api.figshare.com','ndownloader.figshare.com','epa.ndownloader.figshare.com',
'www.kegg.jp','kegg.jp','rest.kegg.jp','www.genome.jp','genome.jp',
'reptile-database.reptarium.cz','reptile-database.org','www.reptile-database.org','search.reptile-database.org',
'wateroffice.ec.gc.ca','api.weather.gc.ca','collaboration.cmc.ec.gc.ca','dd.weather.gc.ca','dd.meteo.gc.ca','wateroffice.ec.gc.ca',
'api.census.gov','www.census.gov','data.census.gov','www2.census.gov',
'www.consumerfinance.gov','files.consumerfinance.gov','nvd.nist.gov','services.nvd.nist.gov',
'europepmc.org','www.ebi.ac.uk','www.europepmc.org','arxiv.org','export.arxiv.org',
'www.ncei.noaa.gov','www.ncdc.noaa.gov','wonder.cdc.gov','www.cdc.gov','data.cdc.gov'
}
KEGG_HOSTS={'www.kegg.jp','kegg.jp','rest.kegg.jp','www.genome.jp','genome.jp'}
def throttle(url):
 # The host-side shared limiter serves timing tokens only, never files or queries.
 host=urllib.parse.urlsplit(url).hostname
 if host=='services.nvd.nist.gov':
  endpoint=os.environ.get('SGR_NVD_RATE_LIMITER','http://host.docker.internal:18764/nvd')
  with urllib.request.urlopen(endpoint,timeout=120) as r:
   if r.status!=200:raise RuntimeError('Shared site limiter unavailable; no request sent')
 if host in KEGG_HOSTS:
  endpoint=os.environ.get('SGR_RATE_LIMITER','http://host.docker.internal:18763/kegg')
  with urllib.request.urlopen(endpoint,timeout=60) as r:
   if r.status!=200: raise RuntimeError('Shared site limiter unavailable; no request sent')

MAX=512_000_000
MAX_EXPANDED=2_000_000_000
REG={}
def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def check_url(url):
 p=urllib.parse.urlsplit(url)
 if p.scheme!='https' or p.hostname not in ALLOWED or p.port not in (None,443) or p.username or p.password: raise ValueError('Only configured official-source HTTPS URLs are supported')
 return url
class Redirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  check_url(newurl);throttle(newurl)
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def register(data,suffix,meta):
 fid='d'+str(len(REG)+1).zfill(4);p=DATA/(fid+suffix);p.write_bytes(data)
 REG[fid]={'path':p.name,**meta};(DATA/'registry.json').write_text(json.dumps(REG,indent=2))
 return fid

def fetch(a):
 url=check_url(a['url']);throttle(url);meta={'url':url,'requested_at':now(),'method':'GET','query':urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)}
 req=urllib.request.Request(url,headers={'User-Agent':'SGR-research-validation/1.0','Accept-Encoding':'identity'})
 try:
  with urllib.request.build_opener(Redirect).open(req,timeout=120) as r:
   data=r.read(MAX+1);meta.update(status=r.status,headers=dict(r.headers),final_url=r.url)
 except urllib.error.HTTPError as e:
  data=e.read(MAX+1);meta.update(status=e.code,headers=dict(e.headers),error=str(e))
 if len(data)>MAX: raise ValueError('Response exceeds 512MB resource bound. No partial data registered; report this limitation, not a source absence.')
 meta.update(bytes=len(data),received_at=now());fid=register(data,'.response',meta)
 ans={'file_id':fid,**meta};ct=meta['headers'].get('Content-Type','').lower()
 if data[:2]==b'PK':
  with zipfile.ZipFile(io.BytesIO(data)) as z:
   if sum(x.file_size for x in z.infolist())>MAX_EXPANDED: raise ValueError('Uncompressed ZIP exceeds 2GB resource bound; archive remains registered')
   ans['members']=[]
   for member in z.infolist():
    if member.is_dir(): continue
    raw=z.read(member);mid=register(raw,'.csv' if member.filename.lower().endswith('.csv') else '.response',{'parent_file':fid,'zip_member':member.filename,**meta})
    ans['members'].append({'file_id':mid,'name':member.filename,'bytes':len(raw)})
 else:
  text=data.decode('utf-8-sig',errors='replace');ans['preview']=text[:4000];ans['preview_truncated']=len(text)>4000
  if 'csv' in ct or text.startswith('OrganizationIdentifier') or text.startswith('"OrganizationIdentifier"'):
   reader=csv.reader(io.StringIO(text));ans['columns']=next(reader,[]);ans['data_rows']=sum(1 for _ in reader)
 return ans

def read(a):
 if a['file_id'] not in REG: raise ValueError('Unknown file_id; only files downloaded in this session are available')
 text=(DATA/REG[a['file_id']]['path']).read_text(errors='replace')
 if a.get('html_text'): text=html.unescape(re.sub('<[^>]+>', ' ', re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', text, flags=re.S|re.I)))
 off=max(0,a.get('offset',0));limit=min(30000,max(1,a.get('limit',15000)))
 return {'text':text[off:off+limit],'offset':off,'next_offset':min(len(text),off+limit),'characters':len(text),'complete':off+limit>=len(text)}
def query(a):
 con=sqlite3.connect(':memory:');con.enable_load_extension(False)
 inputs={}
 for t,fid in a['tables'].items():
  if not re.fullmatch('[A-Za-z][A-Za-z0-9_]*',t): raise ValueError('Invalid table name')
  if fid not in REG: raise ValueError('Unknown file_id')
  reader=csv.reader(io.StringIO((DATA/REG[fid]['path']).read_text(encoding='utf-8-sig')));cols=next(reader)
  if len(set(cols))!=len(cols): raise ValueError('CSV has duplicate header names')
  qc=lambda s:'"'+s.replace('"','""')+'"'
  con.execute('CREATE TABLE '+qc(t)+' ('+','.join(qc(c)+' TEXT' for c in cols)+')')
  rows=list(reader)
  if any(len(r)!=len(cols) for r in rows): raise ValueError('Malformed CSV width; inspect response')
  con.executemany('INSERT INTO '+qc(t)+' VALUES ('+','.join('?' for _ in cols)+')',rows)
  inputs[t]={'file_id':fid,'rows':len(rows),'columns':cols}
 con.commit()
 allowed={sqlite3.SQLITE_SELECT,sqlite3.SQLITE_READ,sqlite3.SQLITE_FUNCTION,sqlite3.SQLITE_RECURSIVE}
 def auth(op,x,y,db,trigger):
  if op==sqlite3.SQLITE_FUNCTION and (y or x or '').lower() in ['load_extension','readfile','writefile']: return sqlite3.SQLITE_DENY
  return sqlite3.SQLITE_OK if op in allowed else sqlite3.SQLITE_DENY
 con.set_authorizer(auth);start=time.monotonic();con.set_progress_handler(lambda: int(time.monotonic()-start>60),10000)
 cur=con.execute(a['sql']);cols=[x[0] for x in cur.description];rows=cur.fetchall()
 out=io.StringIO();writer=csv.writer(out);writer.writerow(cols);writer.writerows(rows)
 fid=register(out.getvalue().encode(),'.csv',{'derived':True,'sql':a['sql'],'inputs':inputs,'created_at':now()})
 limit=min(500,max(1,a.get('limit',100)));off=max(0,a.get('offset',0))
 return {'file_id':fid,'columns':cols,'total_rows':len(rows),'rows':rows[off:off+limit],'truncated':off+limit<len(rows),'offset':off,'input_rows':{k:v['rows'] for k,v in inputs.items()},'reload_types':'All CSV columns including derived columns reload as TEXT; explicitly CAST numeric values in each query.'}

def query_database(a):
 """Read an actual downloaded SQLite archive without permitting host paths or writes."""
 fid=a['file_id']
 if fid not in REG: raise ValueError('Unknown file_id')
 path=(DATA/REG[fid]['path']).resolve()
 if path.parent!=DATA.resolve(): raise ValueError('Invalid registered path')
 con=sqlite3.connect(path.as_uri()+'?mode=ro&immutable=1',uri=True)
 con.enable_load_extension(False)
 con.execute('PRAGMA trusted_schema=OFF');con.execute('PRAGMA query_only=ON')
 allowed={sqlite3.SQLITE_SELECT,sqlite3.SQLITE_READ,sqlite3.SQLITE_FUNCTION,sqlite3.SQLITE_RECURSIVE}
 def auth(op,x,y,db,trigger):
  if op==sqlite3.SQLITE_FUNCTION and (y or x or '').lower() in ['load_extension','readfile','writefile']:return sqlite3.SQLITE_DENY
  return sqlite3.SQLITE_OK if op in allowed else sqlite3.SQLITE_DENY
 con.set_authorizer(auth);start=time.monotonic();con.set_progress_handler(lambda:int(time.monotonic()-start>60),10000)
 try:
  cur=con.execute(a['sql']);cols=[x[0] for x in cur.description];rows=cur.fetchall()
 finally:con.close()
 out=io.StringIO();w=csv.writer(out);w.writerow(cols);w.writerows(rows)
 result_id=register(out.getvalue().encode(),'.csv',{'derived':True,'parent_file':fid,'sql':a['sql'],'created_at':now()})
 limit=min(500,max(1,a.get('limit',100)));off=max(0,a.get('offset',0))
 return {'file_id':result_id,'columns':cols,'total_rows':len(rows),'rows':rows[off:off+limit],'truncated':off+limit<len(rows),'offset':off,'reload_types':'Derived CSV reloads as TEXT; explicitly cast numeric values.'}

def tabulate(a):
 """Lossless generic conversion, never a site-specific answer helper."""
 fid=a['file_id']
 if fid not in REG: raise ValueError('Unknown file_id')
 mode=a['format'];cols=a.get('columns',[])
 raw=(DATA/REG[fid]['path']).read_bytes()
 text=raw.decode('utf-8-sig') if mode!='xlsx' else ''
 if mode=='xlsx':
  ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
  with zipfile.ZipFile(io.BytesIO(raw)) as z:
   if sum(x.file_size for x in z.infolist())>MAX_EXPANDED: raise ValueError('Uncompressed XLSX exceeds 2GB resource bound')
   shared=[]
   if 'xl/sharedStrings.xml' in z.namelist():
    shared=[''.join(t.text or '' for t in si.findall('.//s:t',ns)) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
   names=sorted(n for n in z.namelist() if re.fullmatch(r'xl/worksheets/sheet[0-9]+\.xml',n))
   index=a.get('sheet_index',1)-1
   if not 0<=index<len(names): raise ValueError('sheet_index out of range')
   parsed=[];width=0
   for row in ET.fromstring(z.read(names[index])).findall('.//s:sheetData/s:row',ns):
    values={}
    for c in row.findall('s:c',ns):
     label=re.match('[A-Z]+',c.get('r',''))
     if not label:raise ValueError('Cell coordinate missing')
     pos=0
     for ch in label.group():pos=pos*26+ord(ch)-64
     value=c.find('s:v',ns);v=value.text if value is not None else ''
     if c.get('t')=='s':v=shared[int(v)]
     elif c.get('t')=='inlineStr':v=''.join(t.text or '' for t in c.findall('.//s:t',ns))
     values[pos-1]=v; width=max(width,pos)
    parsed.append(values)
   rows=[[r.get(i,'') for i in range(width)] for r in parsed]
   if not cols:cols=rows.pop(0)
 elif mode in ('csv','tsv'):
  rows=list(csv.reader(io.StringIO(text),delimiter='\t' if mode=='tsv' else ','))
  if not cols: cols=rows.pop(0)
 elif mode=='json':
  obj=json.loads(text)
  for key in a.get('json_path',[]): obj=obj[int(key)] if isinstance(obj,list) else obj[key]
  if not isinstance(obj,list): raise ValueError('Selected JSON value must be an array')
  if not cols: cols=list(dict.fromkeys(k for row in obj if isinstance(row,dict) for k in row))
  rows=[[json.dumps(row.get(c),ensure_ascii=False) if isinstance(row.get(c),(dict,list)) else row.get(c,'') for c in cols] if isinstance(row,dict) else row for row in obj]
 else: raise ValueError('Unsupported format')
 if not cols or any(len(r)!=len(cols) for r in rows): raise ValueError('Inconsistent table width')
 out=io.StringIO();w=csv.writer(out);w.writerow(cols);w.writerows(rows)
 outid=register(out.getvalue().encode(),'.csv',{'derived':True,'parent_file':fid,'conversion':a,'created_at':now()})
 return {'file_id':outid,'columns':cols,'total_rows':len(rows),'rows':rows[:20],'truncated':len(rows)>20,'types':'TEXT on CSV reload; cast numeric fields explicitly'}

TOOLS=[{'name':'download','description':'Download a bounded configured official-source HTTPS response (CSV/ZIP/HTML/JSON/TSV). Full body saved; returns opaque file_id, HTTP metadata, CSV row count and columns. Max512MB response /2GB expanded ZIP; larger-source limitations must be reported. Public APIs and ZIP bulk exports supported; no host filesystem access.','inputSchema':{'type':'object','properties':{'url':{'type':'string'}},'required':['url'],'additionalProperties':False}}, {'name':'read_text','description':'Read a page of a previously downloaded response using its file_id. offset/limit count characters; can page through complete raw content.','inputSchema':{'type':'object','properties':{'file_id':{'type':'string'},'offset':{'type':'integer'},'limit':{'type':'integer'},'html_text':{'type':'boolean'}},'required':['file_id'],'additionalProperties':False}}, {'name':'query_csv','description':'Run one read-only SQLite SELECT/WITH query over complete downloaded CSV files. tables maps SQL table names to file_ids. All source columns loaded as TEXT: quote column names with double quotes, explicitly cast numeric values. Supports joins, aggregates, DISTINCT, window functions, arithmetic, date functions, CTEs. Result is also saved as a CSV file_id for further queries. Pagination affects returned rows only, not computation. No shell, file paths, ATTACH or extensions.','inputSchema':{'type':'object','properties':{'tables':{'type':'object','additionalProperties':{'type':'string'}},'sql':{'type':'string'},'offset':{'type':'integer'},'limit':{'type':'integer'}},'required':['tables','sql'],'additionalProperties':False}}]
TOOLS.append({'name':'tabulate','description':'Convert a downloaded CSV, headerless TSV (provide columns), XLSX sheet (sheet_index, default 1; formula cells use saved cached values), or JSON array (json_path selects nested keys) into a registered CSV for SQL. Preserves rows; all columns reload as TEXT. No inference or site-specific interpretation.','inputSchema':{'type':'object','properties':{'file_id':{'type':'string'},'format':{'type':'string','enum':['csv','tsv','json','xlsx']},'columns':{'type':'array','items':{'type':'string'}},'sheet_index':{'type':'integer','minimum':1},'json_path':{'type':'array','items':{'type':'string'}}},'required':['file_id','format'],'additionalProperties':False}})
TOOLS.append({'name':'query_database','description':'Read-only SELECT/WITH over a downloaded SQLite database (including a ZIP member). Inspect table names and schemas with SELECT name,sql FROM sqlite_master. Original database column types are preserved. Only registered files, no paths, ATTACH, extensions, PRAGMA or writes. Result saved as CSV for later joins.','inputSchema':{'type':'object','properties':{'file_id':{'type':'string'},'sql':{'type':'string'},'offset':{'type':'integer'},'limit':{'type':'integer'}},'required':['file_id','sql'],'additionalProperties':False}})
for t in TOOLS: t['annotations']={'readOnlyHint':True,'destructiveHint':False,'idempotentHint':True,'openWorldHint':t['name']=='download'}

def main():
 DATA.mkdir(parents=True,exist_ok=True)
 if (DATA/'registry.json').exists(): REG.update(json.loads((DATA/'registry.json').read_text()))
 for line in sys.stdin:
  try:
   m=json.loads(line);method=m.get('method');ident=m.get('id')
   if ident is None: continue
   if method=='initialize': result={'protocolVersion':m['params']['protocolVersion'],'capabilities':{'tools':{}},'serverInfo':{'name':'sgr-data','version':'ten-task-v1'}}
   elif method=='tools/list': result={'tools':TOOLS}
   elif method=='ping': result={}
   elif method=='tools/call':
    p=m['params'];started=now()
    try: out={'download':fetch,'read_text':read,'query_csv':query,'tabulate':tabulate,'query_database':query_database}[p['name']](p.get('arguments',{}));error=False
    except Exception as e: out={'error':type(e).__name__+': '+str(e)};error=True
    with (DATA/'tool_calls.jsonl').open('a') as f: f.write(json.dumps({'started_at':started,'ended_at':now(),'name':p['name'],'arguments':p.get('arguments',{}),'result':out,'is_error':error})+'\n')
    result={'content':[{'type':'text','text':json.dumps(out,ensure_ascii=False)}],'isError':error}
   else:
    print(json.dumps({'jsonrpc':'2.0','id':ident,'error':{'code':-32601,'message':'Method not found'}}),flush=True);continue
   print(json.dumps({'jsonrpc':'2.0','id':ident,'result':result}),flush=True)
  except Exception as e: print(str(e),file=sys.stderr,flush=True)
if __name__=='__main__':main()
