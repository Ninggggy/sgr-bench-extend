import json
from pathlib import Path
P=Path(__file__).resolve().parent/'B/v1';P.mkdir(parents=True,exist_ok=True)
def put(n,x): (P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
packets=[
 dict(id='P1',received=0,qname='alias.tree.example.',qtype='A',rcode='NXDOMAIN',cname=[['alias.tree.example.','dead.tree.example.']],compact=False,valid=True,soa_ttl=240,soa_minimum=600),
 dict(id='P2',received=10,qname='gone.compact.example.',qtype='AAAA',rcode='NXDOMAIN',cname=[],compact=True,valid=True,bitmap=['RRSIG','NSEC','NXNAME'],co=1,soa_ttl=180,soa_minimum=600),
 dict(id='P3',received=20,qname='branch.compact.example.',qtype='AAAA',rcode='NOERROR',cname=[],compact=True,valid=True,bitmap=['RRSIG','NSEC'],co=1,soa_ttl=180,soa_minimum=600),
 dict(id='P4',received=30,qname='bad.example.',qtype='A',rcode='NOERROR',cname=[],compact=False,valid=False,answer_ttl=3600)
]
queries=[(40,'leaf.dead.tree.example.','A',0),(40,'leaf.alias.tree.example.','A',0),(40,'gone.compact.example.','AAAA',0),(40,'gone.compact.example.','AAAA',1),(40,'child.gone.compact.example.','AAAA',1),(40,'branch.compact.example.','AAAA',1),(40,'leaf.branch.compact.example.','AAAA',1),(40,'bad.example.','A',0),(40,'bad.example.','AAAA',0),(90,'bad.example.','A',0),(240,'dead.tree.example.','MX',0)]
queries=[dict(id=f'Q{i}',time=t,qname=n,qtype=k,co=c) for i,(t,n,k,c) in enumerate(queries,1)]
put('inputs.json',dict(packets=packets,queries=queries,policy=dict(failure_ttl=60,failure_key=['qname','qtype'],aggressive_nsec=False,nxdomain_cut=True)))
common='''A resolver team is checking whether its negative-cache replay suppresses the right upstream queries after adding Compact Denial of Existence. Determine the local action for each probe below, using the published IETF specifications through 30 September 2025.

These are deliberately specified test inputs, not measurements from a live resolver. All names are absolute; all questions are IN, RD=1, CD=0, DO=1. The resolver validates DNSSEC, understands NXNAME and implements Compact Answers OK (CO) response-code restoration. It implements the recommended NXDOMAIN-cut behavior. Aggressive synthesis from cached NSEC ranges is disabled for this diagnostic; ordinary negative caching and NXDOMAIN cuts remain enabled. No stale serving, prefetch, local-zone overrides, other cached answers, or cached positive descendants exist.

Four upstream resolutions completed at the times shown (seconds relative to t=0). P1–P3 have successfully validated proof and SOA data, with signatures valid beyond t=1000; there are no shorter signature TTL limits. P1 is conventional denial, not Compact Denial. P2 and P3 are Compact Denial NSEC responses: the NSEC owner matches the queried name, its next name is the immediate lexicographic successor, and its bitmap is exactly the listed types. Their answer sections are empty. P4 is a completed DNSSEC validation failure for the exact question: no valid authentication path exists. Its apparent positive answer has TTL 3600, which has not been authenticated. There are no unresolved retries.

The resolver uses a 60-second duration for DNSSEC validation-failure cache entries and keys those entries by name, type and class. Ordinary negative answers have no additional local TTL cap. A valid CNAME in P1 has TTL 600. The SOA TTL values below are those received on the wire; MINIMUM is the field inside that SOA.

| packet | received | original question | response code | answer / NSEC bitmap | SOA TTL | SOA.MINIMUM | CO in response |
|---|---:|---|---|---|---:|---:|---:|
| P1 | 0 | alias.tree.example. A | NXDOMAIN | CNAME alias.tree.example. -> dead.tree.example.; conventional denial of the chain's last name | 240 | 600 | 0 |
| P2 | 10 | gone.compact.example. AAAA | NXDOMAIN | RRSIG NSEC NXNAME | 180 | 600 | 1 |
| P3 | 20 | branch.compact.example. AAAA | NOERROR | RRSIG NSEC | 180 | 600 | 1 |
| P4 | 30 | bad.example. A | NOERROR upstream, but validation failed | unauthenticated positive A answer | — | — | 0 |

Each probe independently observes the cache established by these four completed resolutions, aged to the probe time. Probes do not insert or refresh data. If the cache cannot answer locally, stop before any upstream response arrives; do not invent that response.

| probe | time | name | type | CO in query |
|---|---:|---|---|---:|
'''
common+='\n'.join(f"| {q['id']} | {q['time']} | {q['qname']} | {q['qtype']} | {q['co']} |" for q in queries)
common+='''

Return one table, in Q1–Q11 order, with columns `probe | action | packet | remaining_seconds`.
`action` is the local returned response code (NXDOMAIN, NOERROR or SERVFAIL), or RESOLVE when upstream work is required. `packet` identifies P1–P4 whose cached result supports the local answer. `remaining_seconds` is the remaining lifetime of that supporting negative/failure entry, not the CNAME TTL. For RESOLVE use `-` in both remaining columns. Give citations separately from the table. Do not count an unknown upstream outcome as a local answer.
'''
for variant in ['CG','GO']:
 text=common
 if variant=='CG': text+='\nSuggested approach: identify the denial semantics before deciding the cache key; follow aliases to the name actually denied, distinguish wire response codes from signed denial content, then apply query flags and cache aging. Check later updates to the base caching rules.\n'
 put(variant+'.json',dict(task_id='new-two-B',variant=variant,current_date='2026-09-19',task=text))
put('rules.json',dict(columns=['probe','action','packet','remaining_seconds'],row_key=['probe'],fields={
 'probe':{'uppercase':True},'action':{'uppercase':True,'aliases':{'FORWARD':'RESOLVE','UPSTREAM':'RESOLVE'}},
 'packet':{'uppercase':True,'aliases':{'N/A':'-','NA':'-','—':'-'}},
 'remaining_seconds':{'type':'integer','aliases':{'N/A':'-','NA':'-','—':'-'}}}))
