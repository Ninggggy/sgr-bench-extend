#!/usr/bin/env python3
"""Save real source body + headers + exact request receipt, with TLS verification."""
import argparse,datetime as dt,json,subprocess as sp,urllib.parse
from pathlib import Path

def fetch(url,name,out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 if (out/(name+'.response')).exists() or (out/(name+'.json')).exists(): raise ValueError('Source name already used; retain history')
 meta={'source_id':name,'url':url,'method':'GET','parameters':urllib.parse.parse_qs(urllib.parse.urlsplit(url).query),'requested_at':dt.datetime.now(dt.timezone.utc).isoformat()}
 r=sp.run(['curl','--silent','--show-error','--location','--proto','=https','--proto-redir','=https','--max-time','120','--max-filesize','50000000','--dump-header',str(out/(name+'.headers')),'--output',str(out/(name+'.response')),'--write-out','%{json}',url],text=True,capture_output=True)
 try: receipt=json.loads(r.stdout)
 except: receipt={'curl_output':r.stdout}
 meta.update(received_at=dt.datetime.now(dt.timezone.utc).isoformat(),curl_exit=r.returncode,curl_error=r.stderr,receipt=receipt,saved_file=name+'.response',complete=r.returncode==0)
 (out/(name+'.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
 return {'source_id':name,'status':receipt.get('http_code'),'bytes':receipt.get('size_download'),'complete':meta['complete'],'error':r.stderr}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--name',required=True);p.add_argument('--out',required=True);a=p.parse_args();print(json.dumps(fetch(a.url,a.name,a.out)))
