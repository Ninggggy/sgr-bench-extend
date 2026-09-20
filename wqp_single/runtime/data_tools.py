#!/usr/bin/env python3
"""Read-only research MCP: official HTTPS retrieval, paged text, in-memory SQLite.
No shell, arbitrary Python, filesystem paths, extensions, or database attachments.
Only response files registered in this isolated session can be read.
"""
import csv, datetime as dt, io, json, re, sqlite3, sys, time, urllib.request, urllib.parse, urllib.error, zipfile
from pathlib import Path
DATA=Path('/work/data')
ALLOWED={'www.waterqualitydata.us','waterqualitydata.us','www.epa.gov','cdx.epa.gov'}
MAX=50_000_000
REG={}
def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def check_url(url):
 p=urllib.parse.urlsplit(url)
 if p.scheme!='https' or p.hostname not in ALLOWED or p.port not in (None,443) or p.username or p.password: raise ValueError('Only official WQP/EPA HTTPS URLs are supported')
 return url
class Redirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  check_url(newurl)
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def register(data,suffix,meta):
 fid='d'+str(len(REG)+1).zfill(4);p=DATA/(fid+suffix);p.write_bytes(data)
 REG[fid]={'path':p.name,**meta};(DATA/'registry.json').write_text(json.dumps(REG,indent=2))
 return fid

def fetch(a):
 url=check_url(a['url']);meta={'url':url,'requested_at':now(),'method':'GET','query':urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)}
 req=urllib.request.Request(url,headers={'User-Agent':'WQP-research-validation/1.0','Accept-Encoding':'identity'})
 try:
  with urllib.request.build_opener(Redirect).open(req,timeout=120) as r:
   data=r.read(MAX+1);meta.update(status=r.status,headers=dict(r.headers),final_url=r.url)
 except urllib.error.HTTPError as e:
  data=e.read(MAX+1);meta.update(status=e.code,headers=dict(e.headers),error=str(e))
 if len(data)>MAX: raise ValueError('Response exceeds 50MB bound; narrow query. No partial data registered.')
 meta.update(bytes=len(data),received_at=now());fid=register(data,'.response',meta)
 ans={'file_id':fid,**meta};ct=meta['headers'].get('Content-Type','').lower()
 if data[:2]==b'PK':
  with zipfile.ZipFile(io.BytesIO(data)) as z:
   if sum(x.file_size for x in z.infolist())>MAX: raise ValueError('Uncompressed ZIP >50MB')
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
 text=(DATA/REG[a['file_id']]['path']).read_text(errors='replace');off=max(0,a.get('offset',0));limit=min(30000,max(1,a.get('limit',15000)))
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
 return {'file_id':fid,'columns':cols,'total_rows':len(rows),'rows':rows[off:off+limit],'truncated':off+limit<len(rows),'offset':off,'input_rows':{k:v['rows'] for k,v in inputs.items()}}
TOOLS=[{'name':'download','description':'Download a bounded official WQP/EPA HTTPS response (CSV/ZIP/HTML). Full body saved; returns opaque file_id, HTTP metadata, CSV row count and columns. Max50MB. Public APIs and ZIP bulk exports supported; no host filesystem access.','inputSchema':{'type':'object','properties':{'url':{'type':'string'}},'required':['url'],'additionalProperties':False}}, {'name':'read_text','description':'Read a page of a previously downloaded response using its file_id. offset/limit count characters; can page through complete raw content.','inputSchema':{'type':'object','properties':{'file_id':{'type':'string'},'offset':{'type':'integer'},'limit':{'type':'integer'}},'required':['file_id'],'additionalProperties':False}}, {'name':'query_csv','description':'Run one read-only SQLite SELECT/WITH query over complete downloaded CSV files. tables maps SQL table names to file_ids. All source columns loaded as TEXT: quote column names with double quotes, explicitly cast numeric values. Supports joins, aggregates, DISTINCT, window functions, arithmetic, date functions, CTEs. Result is also saved as a CSV file_id for further queries. Pagination affects returned rows only, not computation. No shell, file paths, ATTACH or extensions.','inputSchema':{'type':'object','properties':{'tables':{'type':'object','additionalProperties':{'type':'string'}},'sql':{'type':'string'},'offset':{'type':'integer'},'limit':{'type':'integer'}},'required':['tables','sql'],'additionalProperties':False}}]
for t in TOOLS: t['annotations']={'readOnlyHint':True,'destructiveHint':False,'idempotentHint':True,'openWorldHint':t['name']=='download'}

def main():
 DATA.mkdir(parents=True,exist_ok=True)
 if (DATA/'registry.json').exists(): REG.update(json.loads((DATA/'registry.json').read_text()))
 for line in sys.stdin:
  try:
   m=json.loads(line);method=m.get('method');ident=m.get('id')
   if ident is None: continue
   if method=='initialize': result={'protocolVersion':m['params']['protocolVersion'],'capabilities':{'tools':{}},'serverInfo':{'name':'wqp-data','version':'1.0'}}
   elif method=='tools/list': result={'tools':TOOLS}
   elif method=='ping': result={}
   elif method=='tools/call':
    p=m['params'];started=now()
    try: out={'download':fetch,'read_text':read,'query_csv':query}[p['name']](p.get('arguments',{}));error=False
    except Exception as e: out={'error':type(e).__name__+': '+str(e)};error=True
    with (DATA/'tool_calls.jsonl').open('a') as f: f.write(json.dumps({'started_at':started,'ended_at':now(),'name':p['name'],'arguments':p.get('arguments',{}),'result':out,'is_error':error})+'\n')
    result={'content':[{'type':'text','text':json.dumps(out,ensure_ascii=False)}],'isError':error}
   else:
    print(json.dumps({'jsonrpc':'2.0','id':ident,'error':{'code':-32601,'message':'Method not found'}}),flush=True);continue
   print(json.dumps({'jsonrpc':'2.0','id':ident,'result':result}),flush=True)
  except Exception as e: print(str(e),file=sys.stderr,flush=True)
if __name__=='__main__':main()
