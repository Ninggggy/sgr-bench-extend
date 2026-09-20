"""Separate HTMLParser/minidom check; no reference.py import. Not executed here.
Run: python independent_check.py REGISTERED_ASSET_DIR
"""
from pathlib import Path
from html.parser import HTMLParser
from xml.dom import minidom
from email.utils import parsedate_to_datetime
from datetime import timezone
import csv, io, json, re, sys

HERE = Path(__file__).resolve().parent
DATA = Path(sys.argv[1]) if len(sys.argv)>1 else HERE

def read(fid):
    fid = fid.split('.')[0]
    registry = json.loads((DATA/'registry.json').read_text())
    if fid in registry:
        return (DATA/registry[fid]['path']).read_text(encoding='utf-8-sig')
    names = [fid+'.response',fid+'.csv',fid]
    if fid == 'd0103':
        names.append('arxiv_oai_actual_record.xml')
    for name in names:
        p = DATA/name
        if p.is_file():
            return p.read_text(encoding='utf-8-sig')
    raise FileNotFoundError(fid)

def norm(s):
    return ' '.join(s.split())

class Abstract(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.mode = None
        self.history = []
        self.title = []
        self.comment = []
        self.identifier = None
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta' and a.get('name') == 'citation_arxiv_id':
            self.identifier = a['content']
        if tag == 'div' and a.get('class') == 'submission-history':
            self.mode = 'history'
        elif tag == 'h1' and 'title' in a.get('class','').split():
            self.mode = 'title'
        elif tag == 'td' and 'comments' in a.get('class','').split():
            self.mode = 'comment'
    def handle_endtag(self, tag):
        if (tag,self.mode) in [('div','history'),('h1','title'),('td','comment')]:
            self.mode = None
    def handle_data(self, data):
        if self.mode:
            getattr(self,self.mode).append(data)
    def versions(self):
        text = norm(' '.join(self.history))
        parts = re.split(r'\[v(\d+)\]', text)
        result = []
        for i in range(1,len(parts),2):
            v, body = int(parts[i]), parts[i+1]
            date = re.search(r'[A-Z][a-z]{2}, \d+ [A-Z][a-z]{2} \d{4} \d{2}:\d{2}:\d{2} UTC',body).group()
            dt = parsedate_to_datetime(date.replace('UTC','GMT')).astimezone(timezone.utc)
            result.append((v,dt,'(withdrawn)' in body))
        return sorted(result)
    def title_text(self):
        return norm(''.join(self.title)).removeprefix('Title:').strip()

def node_text(node):
    return ''.join(c.data if c.nodeType in (c.TEXT_NODE,c.CDATA_SECTION_NODE) else node_text(c) for c in node.childNodes)

atom = minidom.parseString(read('d0088'))
ns = 'http://www.w3.org/2005/Atom'
titles = {}
for entry in atom.getElementsByTagNameNS(ns,'entry'):
    rid = node_text(entry.getElementsByTagNameNS(ns,'id')[0]).rsplit('/',1)[-1]
    titles[rid] = norm(node_text(entry.getElementsByTagNameNS(ns,'title')[0]))
assert len(titles) == 22

result = []
for row in csv.DictReader(io.StringIO((HERE/'evidence_index.psv').read_text()),delimiter='|'):
    p = Abstract(read(row['predecessor_file']))
    q = Abstract(read(row['replacement_file']))
    assert p.identifier == row['predecessor_id']
    assert q.identifier == row['replacement_id']
    assert q.identifier in norm(' '.join(p.comment))
    ph, qh = p.versions(), q.versions()
    assert ph[-1][2]
    cutoff = ph[-1][1]
    eligible = sorted((t,v) for v,t,w in qh if t<=cutoff)
    stamp, version = eligible[-1]
    assert len([x for x in eligible if x[0]==stamp]) == 1
    selected = titles[q.identifier+'v'+str(version)]
    current = q.title_text()
    result.append({'predecessor_id':p.identifier,'replacement_id':q.identifier,
                   'selected_version':'v'+str(version),'selected_title':selected,
                   'current_title':current,'changed':selected!=current})
    if p.identifier == '2106.14997':
        v7 = next(t for v,t,w in qh if v==7)
        assert (v7-cutoff).total_seconds() == 232
        assert version == 6
        # Independent clock-face arithmetic for this same-day comparison.
        assert (22*3600+16*60+5)-(22*3600+12*60+13) == 232
assert len(result) == 23
expected_changes = {'2102.13653','2103.00222','2103.06490','2104.13818',
                    '2106.14997','2107.01273','2108.08647','2111.03536'}
assert {r['predecessor_id'] for r in result if r['changed']} == expected_changes
supplied = list(csv.DictReader(io.StringIO((HERE/'oracle.psv').read_text()),delimiter='|'))
assert [{k:r[k] for k in supplied[0]} for r in result if r['changed']] == supplied

oai = minidom.parseString(read('d0103'))
x = 'http://arxiv.org/OAI/arXivRaw/'
record = oai.getElementsByTagNameNS(x,'arXivRaw')[0]
versions = record.getElementsByTagNameNS(x,'version')
all_titles = record.getElementsByTagNameNS(x,'title')
assert len(versions) == 10 and len(all_titles) == 1
assert all(not v.getElementsByTagNameNS(x,'title') for v in versions)
fields = {c.localName for v in versions for c in v.childNodes if c.nodeType==c.ELEMENT_NODE}
assert fields == {'date','size'}
key = next(r for r in result if r['predecessor_id']=='2106.14997')
assert norm(node_text(all_titles[0])) == key['current_title']
assert key['selected_title'] != key['current_title']
print(json.dumps({'relationships':len(result),'changed':sum(r['changed'] for r in result),
                  'gap_seconds':232,'oai_version_fields':sorted(fields),
                  'comparisons':result},indent=2))
