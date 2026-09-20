#!/usr/bin/env python3
"""r03 constructor. Standard library, no network. Not executed by explorer.
Usage: python reference.py RAW_DIR [ASSET_DIR] [--pool-out FILE]
PSV to stdout; optional complete disposition ledger to FILE.
"""
import argparse, csv, io, json, re, sys, unicodedata
from pathlib import Path
from datetime import datetime
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
p=argparse.ArgumentParser()
p.add_argument('raw',type=Path)
p.add_argument('assets',nargs='?',type=Path,default=Path(__file__).resolve().parent)
p.add_argument('--pool-out',type=Path)
args=p.parse_args()
def read(name):
    q=args.raw/name
    if q.exists(): return q.read_text(encoding='utf-8-sig')
    if q.suffix=='.csv' and q.with_suffix('.response').exists():
        return q.with_suffix('.response').read_text(encoding='utf-8-sig')
    raise FileNotFoundError(q)
def asset(name): return json.loads((args.assets/name).read_text(encoding='utf-8'))
def norm(s): return ' '.join(unicodedata.normalize('NFC',s).split())
C=asset('candidate_pool.json')
B=json.loads(read(C['bindings_file']))
A='{http://www.w3.org/2005/Atom}'
X='{http://arxiv.org/schemas/atom}'
O='{http://a9.com/-/spec/opensearch/1.1/}'
def feed(name):
    root=ET.fromstring(read(name)); out=[]
    for e in root.findall(A+'entry'):
        vid=e.findtext(A+'id').split('/abs/',1)[-1]
        primary=e.find(X+'primary_category')
        out.append(dict(id=re.sub(r'v\d+$','',vid),vid=vid,
            published=e.findtext(A+'published'),updated=e.findtext(A+'updated'),
            categories=[x.attrib['term'] for x in e.findall(A+'category')],
            primary_category=primary.attrib['term'] if primary is not None else '',
            title=norm(e.findtext(A+'title','')),comment=norm(e.findtext(X+'comment','')),
            authors=[norm(x.findtext(A+'name','')) for x in e.findall(A+'author')]))
    return root,out
class Text(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=True); self.parts=[]
    def handle_data(self,s): self.parts.append(s)
def visible(name):
    parser=Text();parser.feed(read(name));return norm(' '.join(parser.parts))
def history(name):
    block=visible(name).split('Submission history',1)[1].split('Full-text links:',1)[0]
    found=re.findall(r'\[v(\d+)\]\s*([A-Za-z]{3}, \d{1,2} [A-Za-z]{3} \d{4} \d{2}:\d{2}:\d{2} UTC)',block)
    out=[(int(v),datetime.strptime(t,'%a, %d %b %Y %H:%M:%S UTC').strftime('%Y-%m-%dT%H:%M:%SZ')) for v,t in found]
    assert out and len(out)==len(set(v for v,t in out)),name
    return out
pool={}; duplicates=0
for filename in C['raw_scope_files']:
    root,rows=feed(filename)
    for row in rows:
        if not '2020-01-01T00:00:00Z'<=row['published']<'2021-01-01T00:00:00Z': continue
        assert 'cs.LG' in row['categories']
        if row['id'] in pool: assert pool[row['id']]==row; duplicates+=1
        else: pool[row['id']]=row
assert len(pool)==C['records']==25890
assert duplicates==C['duplicate_observations']
assert sum(r['primary_category']!='cs.LG' for r in pool.values())==C['crosslists']
assert max(r['updated'] for r in pool.values())==C['latest_scope_update']
saved_rows=list(csv.DictReader(io.StringIO(read(C['complete_pool_file']))))
saved={r['id']:r for r in saved_rows}
assert len(saved_rows)==len(saved)==len(pool) and set(saved)==set(pool)
for ident,row in pool.items():
    for k in ('published','updated','title','comment','primary_category'):
        assert norm(saved[ident][k])==norm(row[k]),(ident,k)
    assert saved[ident]['categories'].split(';')==row['categories']
comments=[json.loads(line) for line in read(C['all_comments_file']).splitlines() if line.strip()]
expected=[{'id':i,'comment':pool[i]['comment']} for i in sorted(pool) if pool[i]['comment']]
assert comments==expected and len(comments)==C['nonempty_comments']==15434
assert len(pool)-len(comments)==C['empty_comments']==10456

# Semantic judgments are explicit manual inputs. Counting is not a semantic review.
# The old 707-frontier labels never select rows.
review={}
def assign(n,status,origin,ident=None):
    assert n not in review and 1<=n<=len(comments),(n,status)
    if ident is not None: assert comments[n-1]['id']==ident
    review[n]={'review_status':status,'review_origin':origin}
def ranges(values,status,origin):
    for lo,hi in values:
        for n in range(lo,hi+1): assign(n,status,origin)
rf=C['review_files']
prefix=asset(rf['prefix'])
ranges(prefix['negative_ranges_inclusive'],'negative',rf['prefix'])
for n,ident,decision in prefix['exceptions']: assign(n,decision,rf['prefix'],ident)
ad=json.loads(read(rf['a']))
ranges(ad['negative_ranges_inclusive'],'negative',rf['a'])
for n,ident,status in ad['exceptions']: assign(n,'A:'+status,rf['a'],ident)
ae=json.loads(read(rf['a_evidence']))['entries']
for r in ae:
    assert comments[r['row']-1]=={'id':r['source_id'],'comment':norm(r['comment'])}
bd=json.loads(read(rf['b']))
ranges(bd['ordinary_negative_ranges'],'negative',rf['b'])
for group,nums in bd['explicit_negative_groups'].items():
    for n in nums: assign(n,'B:negative:'+group,rf['b'])
for group,nums in bd['flag_groups'].items():
    for n in nums: assign(n,'B:flag:'+group,rf['b'])
be=json.loads(read(rf['b_evidence']))['entries']
for r in be:
    assert comments[r['row']-1]=={'id':r['source_id'],'comment':norm(r['comment'])}
cd=json.loads(read(rf['c']))
for r in cd: assign(r['global_row'],'C:'+r['semantic_status'],rf['c'],r['source_id'])
for r in json.loads(read(rf['c_evidence']))['notes']:
    assert norm(r['comment'])==pool[r['source_id']]['comment']
assert set(review)==set(range(1,15435))
for label,(lo,hi) in {'a':(1606,6215),'b':(6216,10825),'c':(10826,15434)}.items():
    lines=read(C['partition_raw_files'][label]).splitlines()
    assert len(lines)==hi-lo+1
    for n,line in zip(range(lo,hi+1),lines):
        number,ident,comment=line.split('\t',2)
        assert int(number)==n and comments[n-1]=={'id':ident,'comment':comment}
assert len(read(C['all_comments_file'])[:155952].splitlines())==1605

relations=C['relations']; rel_by_id={}
for r in relations: rel_by_id.setdefault(r['source_id'],[]).append(r)
active=C['active_source_history_files']
for ident,filename in active.items():
    doc=visible(filename)
    assert 'This paper has been withdrawn' not in doc and 'View PDF' in doc,ident
    cutoff=max(t for v,t in history(filename))
    assert cutoff==pool[ident]['updated'],ident
    tail=doc.split('Submission history',1)[1].split('Full-text links:',1)[0]
    assert '(withdrawn)' not in re.split(r'\[v\d+\]',tail)[-1],ident
final={}
for n,item in enumerate(comments,1):
    ident=item['id']; state=review[n]['review_status']
    if ident in rel_by_id: decision='included_direct_named_successor'
    elif ident in active: decision='excluded_current_record_not_withdrawn'
    elif ident==C['publisher_relation']['source_id']: decision=C['publisher_relation']['disposition']
    elif state=='A:P':
        assert ident in C['a_boundary_p_ids'],ident
        decision='excluded_reverse_or_parallel_relation'
    elif state.startswith('B:flag:'):
        assert ident in C['b_boundary_flag_ids'],ident
        decision='excluded_reverse_relation'
    else:
        assert state not in ('C:potential_forward_relation','C:conservative_publication_version_check'),ident
        decision='excluded_no_direct_named_successor_in_reviewed_comment'
    final[ident]={**review[n],'final_disposition':decision}
for ident,row in pool.items():
    if not row['comment']:
        final[ident]={'review_status':'empty_comment','review_origin':'d0158.response official withdrawal documentation',
            'final_disposition':'excluded_no_named_current_withdrawal_notice'}
assert set(final)==set(pool)
assert {i for i,r in final.items() if r['final_disposition']=='included_direct_named_successor'}==set(rel_by_id)

# Publisher relation is retained, never converted into an invented catalogue ID.
pub=C['publisher_relation']; assert 'This paper has been withdrawn' in visible(pub['source_history'])
assert max(t for v,t in history(pub['source_history']))==pool[pub['source_id']]['updated']
publisher_ids=set()
for filename,total in pub['catalogue_searches'].items():
    root,rows=feed(filename)
    assert int(root.findtext(O+'totalResults'))==len(rows)==total
    assert int(root.findtext(O+'startIndex'))==0
    publisher_ids.update(r['id'] for r in rows)
pe=asset('publisher_evidence.json')
assert publisher_ids=={r[0] for r in pe['candidates']} and len(publisher_ids)==32
# Search meaning and identity exclusions are manual, documented in exploration.md.

hist={**B['target_history_files'],**C['additional_target_history_files']}
titles={**B['title_html_files'],**C['additional_title_html_files']}
metadata={}
for filename in B['target_metadata_batches']+C['additional_target_metadata_files']:
    for row in feed(filename)[1]:
        if row['vid'] in metadata: assert metadata[row['vid']]==row
        metadata[row['vid']]=row
out=[]
for relation in relations:
    source=relation['source_id'];target=relation['target_id'];notice=pool[source]['comment']
    assert 'This paper has been withdrawn' in visible(relation['source_history'])
    cutoff=max(t for v,t in history(relation['source_history']))
    if cutoff>='2026-09-10T00:00:00Z': raise RuntimeError('Version drift: '+source)
    assert cutoff==pool[source]['updated']
    if relation['identity']=='numeric_notice':
        m=re.search(r'superseded by(?: article)?\s+(?:arXiv:)?(\d{4}\.\d{4,5})',notice,re.I)
        ids={m.group(1)} if m else set(re.findall(r'\b\d{4}\.\d{4,5}\b',notice))-{source}
        assert ids=={target},source
    elif source=='2008.13265':
        named='Meta-Learning Guarantees for Online Receding Horizon Learning Control'
        assert named in notice
        root,resolved=feed('d0261.response')
        assert int(root.findtext(O+'totalResults'))==len(resolved)==1
        assert resolved[0]['id']==target and resolved[0]['title']==named
        assert 'Deepan Muthirayan' in pool[source]['authors'] and 'Deepan Muthirayan' in resolved[0]['authors']
    elif source=='2012.03115':
        root,resolved=feed('d0128.response')
        assert int(root.findtext(O+'totalResults'))==len(resolved)==1 and resolved[0]['id']==target
        root,by_author=feed('d0135.response')
        assert int(root.findtext(O+'totalResults'))==len(by_author)==2
        assert {r['id'] for r in by_author}=={source,target}
        assert set(pool[source]['authors'])<=set(resolved[0]['authors'])
    else: raise AssertionError(relation)
    eligible=[(v,t) for v,t in history(hist[target]) if t<=cutoff]
    if not eligible: continue
    best=max(t for v,t in eligible)
    for version,stamp in sorted(eligible):
        if stamp!=best: continue
        vid=target+'v'+str(version)
        title=visible(titles[vid]).split('Title:',1)[1].split('Authors:',1)[0].strip()
        assert norm(title)==metadata[vid]['title'] and stamp==metadata[vid]['updated'],vid
        out.append([source,cutoff,target,str(version),stamp,metadata[vid]['title']])
out.sort(key=lambda r:(r[0],r[2],int(r[3])))
assert len(out)==len({(r[0],r[2],r[3]) for r in out})
# These histories have no latest-timestamp ties; the existing scorer key is fair.
assert len(out)==len({(r[0],r[2]) for r in out})
if args.pool_out:
    with args.pool_out.open('w',encoding='utf-8') as f:
        for ident in sorted(pool):
            f.write(json.dumps({**saved[ident],**final[ident]},ensure_ascii=False)+'\n')
writer=csv.writer(sys.stdout,delimiter='|',lineterminator='\n')
writer.writerow(['source_id','source_last_submission_utc','target_id','target_version','target_submission_utc','target_title'])
writer.writerows(out)
print(json.dumps({'scope':len(pool),'comments':len(comments),'empty_comments':10456,
 'duplicate_observations':duplicates,'rows':len(out),'manual_semantics_not_proved_by_counts':True}),file=sys.stderr)
