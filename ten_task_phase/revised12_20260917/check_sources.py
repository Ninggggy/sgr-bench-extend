"""Bounded constructor-only GETs, no retries, no model or blind environment."""
import concurrent.futures, datetime as dt, json, subprocess, sys, time
from pathlib import Path
BASE=Path(__file__).resolve().parent
PHASE=BASE.parent
def fetch(job):
    label,url,phase=job
    root=BASE/'source_checks'/phase;root.mkdir(parents=True,exist_ok=True)
    out=root/(label+'.response');meta=root/(label+'.json')
    if meta.exists():return json.loads(meta.read_text())
    if out.exists():raise RuntimeError('Existing incomplete request: '+str(out))
    t=time.monotonic();start=dt.datetime.now(dt.timezone.utc).isoformat()
    p=subprocess.run(['curl','--silent','--show-error','--location','--max-redirs','3','--max-time','40','--retry','0','--output',str(out),'--write-out','%{http_code}\n%{url_effective}',url],capture_output=True,text=True)
    fields=p.stdout.splitlines();row={'label':label,'url':url,'started_at':start,'ended_at':dt.datetime.now(dt.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-t,'exit_code':p.returncode,'status':int(fields[0]) if fields and fields[0].isdigit() else None,'final_url':fields[1] if len(fields)>1 else None,'error':p.stderr,'bytes':out.stat().st_size if out.exists() else 0,'response':str(out),'retry':False,'constructor_only':True}
    meta.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:row[k] for k in ['label','status','bytes']}),flush=True);return row
def main():
    phase=sys.argv[1] if len(sys.argv)>1 else 'pre'
    jobs=[]
    stap=PHASE/'rolling_five/candidates/stap_replication_protocol_001/r01/post_development_a/request_index.jsonl'
    for line in stap.read_text().splitlines():
        x=json.loads(line);jobs.append(('stap_'+x['label'],x['url'],phase))
    if phase=='pre':
        epmc=json.loads((PHASE/'candidates/europemc_reuse_deposit_001/r01/sources.json').read_text())
        for x in epmc:
            if x.get('url') and (x['file_id'] in ['d0001','d0230','d0231'] or x.get('pmcid')):
                jobs.append(('reuse_'+x['file_id'],x['url'].replace('pageSize=1000','pageSize=20'),phase))
        for name,url in [
          ('genome_examples','https://www.kegg.jp/kegg/genome/genome.html'),
          ('genome_buc','https://www.kegg.jp/kegg-bin/show_organism?org=buc'),
          ('module_leu','https://rest.kegg.jp/get/M00432'),
          ('module_trp','https://rest.kegg.jp/get/M00023'),
          ('genome_joint','https://www.kegg.jp/kegg-bin/show_organism?org=api+buc'),
        ]:jobs.append((name,url,phase))
        for x in json.loads((PHASE/'candidates/kegg_initial_cdx_001/r02/sources.json').read_text()):
            if x.get('url') and x['id'] not in ['cap_device_label']:
                jobs.append(('cdx_'+x['id'],x['url'],phase))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool: rows=list(pool.map(fetch,jobs))
    (BASE/'source_checks'/phase/'index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    print('SOURCE_CHECKS_DONE',len(rows),flush=True)
if __name__=='__main__':main()
