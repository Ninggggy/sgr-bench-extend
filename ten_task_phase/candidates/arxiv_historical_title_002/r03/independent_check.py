#!/usr/bin/env python3
"""Independent r03 recomputation. No import of reference, no reading oracle.
Standard library only. Not executed by explorer.
Usage: python independent_check.py RAW_DIR [ASSET_DIR]
"""
import csv, datetime as dt, html, io, json, re, sys, unicodedata
from pathlib import Path
R=Path(sys.argv[1])
D=Path(sys.argv[2]) if len(sys.argv)>2 else Path(__file__).resolve().parent
C=json.loads((D/'candidate_pool.json').read_text())
def raw(name):
    p=R/name
    if not p.exists() and p.suffix=='.csv': p=p.with_suffix('.response')
    return p.read_text(encoding='utf-8-sig')
B=json.loads(raw(C['bindings_file']))
def clean(s): return ' '.join(unicodedata.normalize('NFC',html.unescape(s)).split())
def blocks(filename):
    result=[]
    for b in re.findall(r'<entry>(.*?)</entry>',raw(filename),re.S):
        def value(tag):
            m=re.search('<'+re.escape(tag)+r'>(.*?)</'+re.escape(tag)+'>',b,re.S)
            return clean(m.group(1)) if m else ''
        v=value('id').split('/abs/',1)[-1]
        cats=re.findall(r'<category\s+term="([^"]+)"',b)
        pm=re.search(r'<arxiv:primary_category\s+term="([^"]+)"',b)
        result.append({'id':re.sub(r'v[0-9]+$','',v),'vid':v,
            'published':value('published'),'updated':value('updated'),
            'title':value('title'),'comment':value('arxiv:comment'),
            'categories':cats,'primary_category':pm[1] if pm else ''})
    return result
def plain(s): return clean(re.sub(r'<[^>]*>',' ',s))
def dates(filename):
    m=re.search(r'<div\s+class="submission-history">(.*?)</div>',raw(filename),re.S)
    assert m,filename
    result=[]
    for segment in re.split(r'<br\s*/?>',m[1]):
        n=re.search(r'\[v([0-9]+)\]',segment)
        if n:
            stamp=re.search(r'[A-Z][a-z]{2}, [0-9]{1,2} [A-Z][a-z]{2} [0-9]{4} [0-9:]{8} UTC',plain(segment))
            assert stamp,(filename,segment)
            result.append((dt.datetime.strptime(stamp[0],'%a, %d %b %Y %H:%M:%S UTC'),int(n[1])))
    assert result and len(result)==len(set(v for t,v in result)),filename
    return sorted(result)
def title(filename):
    h=re.search(r'<h1\b[^>]*class="[^"]*\btitle\b[^"]*"[^>]*>(.*?)</h1>',raw(filename),re.S)
    assert h,filename
    return re.sub(r'^Title:\s*','',plain(h[1]))
def iso(t): return t.strftime('%Y-%m-%dT%H:%M:%SZ')
annual={};observations=0
for f in C['raw_scope_files']:
    for row in blocks(f):
        if '2020-01-01T00:00:00Z'<=row['published']<'2021-01-01T00:00:00Z':
            observations+=1
            assert 'cs.LG' in row['categories']
            if row['id'] in annual: assert annual[row['id']]==row
            annual[row['id']]=row
assert len(annual)==25890 and observations==28432
assert observations-len(annual)==2542
assert sum(x['primary_category']!='cs.LG' for x in annual.values())==14793
assert max(x['updated'] for x in annual.values())=='2026-09-01T16:13:17Z'
tab=list(csv.DictReader(io.StringIO(raw('d0112.csv'))))
assert len(tab)==len({r['id'] for r in tab})==25890
for x in tab:
    row=annual[x['id']]
    assert all(' '.join(unicodedata.normalize('NFC',x[k]).split())==row[k] for k in ('title','comment','published','updated','primary_category'))
    assert x['categories'].split(';')==row['categories']
comments=[json.loads(l) for l in raw('d0114.jsonl').splitlines() if l.strip()]
assert len(comments)==15434
assert comments==[{'id':i,'comment':annual[i]['comment']} for i in sorted(annual) if annual[i]['comment']]
assert sum(not r['comment'] for r in annual.values())==10456
# Independent disjoint row-index accounting, not an independent semantic review.
indices=[]
def expand(ranges):
    return [n for lo,hi in ranges for n in range(lo,hi+1)]
pre=json.loads((D/'prefix_review.json').read_text())
indices+=expand(pre['negative_ranges_inclusive'])
indices += [r[0] for r in pre['exceptions']]
a=json.loads(raw('d0144.response'))
indices+=expand(a['negative_ranges_inclusive'])+[r[0] for r in a['exceptions']]
b=json.loads(raw('d0149.response'))
indices+=expand(b['ordinary_negative_ranges'])
indices += [n for group in b['explicit_negative_groups'].values() for n in group]
indices += [n for group in b['flag_groups'].values() for n in group]
c=json.loads(raw('d0154.response'))
indices += [r['global_row'] for r in c]
assert sorted(indices)==list(range(1,15435))
for label,first,last in [('a',1606,6215),('b',6216,10825),('c',10826,15434)]:
    records=[l.split('\t',2) for l in raw(C['partition_raw_files'][label]).splitlines()]
    assert [int(r[0]) for r in records]==list(range(first,last+1))
    assert [{'id':r[1],'comment':r[2]} for r in records]==comments[first-1:last]
cg=json.loads((D/'CG.json').read_text());go=json.loads((D/'GO.json').read_text())
assert set(cg)==set(go)=={'instruction','output_format'}
assert cg['instruction'].startswith(go['instruction']) and cg['output_format']==go['output_format']

timelines={**B['target_history_files'],**C['additional_target_history_files']}
titles={**B['title_html_files'],**C['additional_title_html_files']}
versions={}
for f in B['target_metadata_batches']+C['additional_target_metadata_files']:
    for row in blocks(f): versions[row['vid']]=row
result=[];selected={}
for rel in C['relations']:
    source,target=rel['source_id'],rel['target_id']
    assert 'This paper has been withdrawn' in plain(raw(rel['source_history']))
    cutoff=dates(rel['source_history'])[-1][0]
    if cutoff>=dt.datetime(2026,9,10): raise RuntimeError('Version drift: '+source)
    assert iso(cutoff)==annual[source]['updated']
    notice=annual[source]['comment']
    if rel['identity']=='numeric_notice':
        text=notice.lower()
        if 'superseded by' in text:
            pointer=notice[text.index('superseded by')+len('superseded by'):]
            inferred=re.search(r'[0-9]{4}\.[0-9]{4,5}',pointer)[0]
        else:
            ids=set(re.findall(r'\b[0-9]{4}\.[0-9]{4,5}\b',notice))-{source}
            assert len(ids)==1
            inferred=next(iter(ids))
        assert inferred==target
    elif source=='2008.13265':
        hits=blocks('d0261.response')
        assert len(hits)==1 and hits[0]['id']==target
        assert hits[0]['title'] in notice
    else:
        assert source=='2012.03115'
        assert [r['id'] for r in blocks('d0128.response')]==[target]
        assert {r['id'] for r in blocks('d0135.response')}=={source,target}
    winner=None;chosen=[]
    for when,number in dates(timelines[target]):
        if when>cutoff: continue
        if winner is None or when>winner: winner,chosen=when,[number]
        elif when==winner: chosen.append(number)
    if winner is None: continue
    selected[source]=(cutoff,winner,chosen)
    for number in sorted(chosen):
        vid=target+'v'+str(number)
        value=title(titles[vid])
        assert value==versions[vid]['title'] and iso(winner)==versions[vid]['updated']
        result.append([source,iso(cutoff),target,str(number),iso(winner),value])
result.sort(key=lambda r:(r[0],r[2],int(r[3])))
for source,seconds in [('2008.13265',1884853),('2012.03115',3399021)]:
    before,when,number=selected[source]
    delta=before-when
    assert delta.days*86400+delta.seconds==seconds
assert selected['2008.13265'][2]==[14]
later=next(t for t,v in dates(timelines['2102.10955']) if v==2)
assert (later-selected['2011.08470'][0]).total_seconds()==17324
assert selected['2011.08470'][2]==[1]
assert title(titles['2109.03866v1'])!=title(timelines['2109.03866'])
assert len(result)==len({(r[0],r[2]) for r in result})
for filename,total in C['publisher_relation']['catalogue_searches'].items():
    declared=int(re.search(r'<opensearch:totalResults>(\d+)</opensearch:totalResults>',raw(filename))[1])
    assert declared==total==len(blocks(filename))
# Publisher edition has no supported catalogue version: no invented row.
w=csv.writer(sys.stdout,delimiter='|',lineterminator='\n')
w.writerow(['source_id','source_last_submission_utc','target_id','target_version','target_submission_utc','target_title'])
w.writerows(result)
print(json.dumps({'raw_observations':observations,'scope':len(annual),'comments':len(comments),
 'review_index_coverage':len(indices),'rows':len(result),'key_deltas_seconds':[1884853,3399021,17324],
 'semantic_decisions_shared_manual_inputs':True}),file=sys.stderr)
