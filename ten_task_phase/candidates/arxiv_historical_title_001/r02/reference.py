"""Offline source reconstruction. Run: python reference.py REGISTERED_ASSET_DIR
Not executed by the constructor. Semantic notice adjudications are in d0109.
"""
from pathlib import Path
import csv, html, io, json, re, sys
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE
A = '{http://www.w3.org/2005/Atom}'
X = '{http://arxiv.org/schemas/atom}'
O = '{http://a9.com/-/spec/opensearch/1.1/}'
NUM = re.compile(r'\b\d{4}\.\d{4,5}\b')
OLD = re.compile(r'\b(?:astro-ph|cond-mat|cs|gr-qc|hep-ex|hep-lat|hep-ph|hep-th|math|math-ph|nlin|nucl-ex|nucl-th|physics|quant-ph|q-bio|q-fin|stat|acc-phys|adap-org|alg-geom|ao-sci|atom-ph|bayes-an|chao-dyn|chem-ph|cmp-lg|comp-gas|dg-ga|funct-an|mtrl-th|patt-sol|plasm-ph|solv-int|supr-con)/\d{7}(?:v\d+)?\b', re.I)
HTML_FILES = [5,6,7,8,11,12,13,14,15,16,17,18,21,22] + list(range(49,88)) + list(range(90,103))
ALIASES = {'d0103':'arxiv_oai_actual_record.xml', 'd0045':'arxiv_full_pool_verified.json'}

def raw(fid):
    fid = fid.split('.')[0]
    registry = json.loads((DATA/'registry.json').read_text())
    if fid in registry:
        return (DATA/registry[fid]['path']).read_text(encoding='utf-8-sig')
    names = [fid+'.response', fid+'.csv', fid+'.json', fid]
    if fid in ALIASES:
        names.append(ALIASES[fid])
    for name in names:
        p = DATA / name
        if p.is_file():
            return p.read_text(encoding='utf-8-sig')
    raise FileNotFoundError(f'Registered asset {fid} missing under {DATA}')

def norm(s):
    return ' '.join(s.split())

def plain(s):
    return norm(html.unescape(re.sub(r'<[^>]+>', ' ', s)))

def iso(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))

def page(fid):
    s = raw(fid)
    rid = re.search(r'name="citation_arxiv_id" content="([^"]+)"', s).group(1)
    block = re.search(r'<div class="submission-history">(.*?)</div>', s, re.S).group(1)
    history = []
    for part in re.split(r'<strong>', block)[1:]:
        v = int(re.search(r'\[v(\d+)\]', part).group(1))
        stamp = re.search(r'\w{3}, \d{1,2} \w{3} \d{4} \d{2}:\d{2}:\d{2} UTC', part).group()
        dt = datetime.strptime(stamp, '%a, %d %b %Y %H:%M:%S UTC').replace(tzinfo=timezone.utc)
        history.append((v, dt, '(withdrawn)' in plain(part)))
    comment = re.search(r'<td class="tablecell comments[^"]*">(.*?)</td>', s, re.S)
    title = re.search(r'<h1 class="title[^"]*">(.*?)</h1>', s, re.S).group(1)
    return {'id':rid, 'file':fid+'.response', 'history':sorted(history),
            'comment':plain(comment.group(1)) if comment else '',
            'title':plain(title).removeprefix('Title:').strip()}

def cohort():
    records = {}
    expected = None
    for n in range(25,45):
        fid = f'd{n:04d}'
        root = ET.fromstring(raw(fid))
        if expected is None:
            expected = int(root.findtext(O+'totalResults'))
        for e in root.findall(A+'entry'):
            rid = re.sub(r'v\d+$', '', e.findtext(A+'id').rsplit('/',1)[-1])
            published = e.findtext(A+'published')
            cats = [c.attrib['term'] for c in e.findall(A+'category')]
            assert published.startswith('2021-') and 'cs.LG' in cats, rid
            row = {'id':rid, 'published':published, 'categories':cats,
                   'comment':norm(e.findtext(X+'comment','')), 'file':fid+'.response'}
            if rid in records:
                assert records[rid]['published'] == published
                assert records[rid]['comment'] == row['comment'], rid
            records[rid] = row
    assert len(records) == expected == 26533
    assert records['2111.00629']['published'] == '2021-10-31T23:59:29Z'
    old = {k:OLD.findall(v['comment']) for k,v in records.items() if OLD.search(v['comment'])}
    assert not old, ('Review old-style target frontier', old)
    frontier = {k:v for k,v in records.items() if set(NUM.findall(v['comment']))-{k}}
    assert len(frontier) == 705
    return records, frontier

def selected_metadata():
    root = ET.fromstring(raw('d0088'))
    entries = {}
    for e in root.findall(A+'entry'):
        rid = e.findtext(A+'id').rsplit('/',1)[-1]
        entries[rid] = {'title':norm(e.findtext(A+'title')), 'time':iso(e.findtext(A+'updated'))}
    assert len(entries) == 22
    return entries

def build():
    records, frontier = cohort()
    pages = {}
    for n in HTML_FILES:
        p = page(f'd{n:04d}')
        pages[p['id']] = p
    labels = {r['id']:r for r in csv.DictReader(io.StringIO(raw('d0109')))}
    assert set(labels) == set(frontier)
    for rid, label in labels.items():
        assert norm(label['comment']) == frontier[rid]['comment'], rid
        if label['classification'] == 'excluded_latest_version_active':
            assert not pages[rid]['history'][-1][2], rid
    metadata = selected_metadata()
    rows = []
    for rid, p in pages.items():
        if rid not in frontier or not p['history'][-1][2]:
            continue
        # Source adjudication: d0050 cites prior algorithms, not a replacement.
        if rid == '2101.02966':
            assert 'more efficient existing algorithm' in p['comment']
            assert labels[rid]['classification'] == 'withdrawn_prior_algorithm_citation_not_replacement'
            continue
        targets = set(NUM.findall(p['comment'])) - {rid}
        assert len(targets) == 1, (rid, targets)
        target = targets.pop()
        q = pages[target]
        withdrawal_version, cutoff, withdrawn = p['history'][-1]
        possible = [h for h in q['history'] if h[1] <= cutoff]
        if not possible:
            continue
        latest_time = max(h[1] for h in possible)
        choices = [h for h in possible if h[1] == latest_time]
        assert len(choices) == 1, (rid, 'timestamp tie')
        version, submitted, _ = choices[0]
        selected = metadata[target+'v'+str(version)]
        assert selected['time'] == submitted, target
        assert labels[rid]['classification'] == 'included_direct_replacement_currently_withdrawn'
        rows.append({'predecessor_id':rid, 'replacement_id':target,
                     'selected_version':'v'+str(version), 'selected_title':selected['title'],
                     'current_title':q['title'], 'title_changed':selected['title'] != q['title'],
                     'withdrawal_version':'v'+str(withdrawal_version),
                     'withdrawal_submission_utc':cutoff.isoformat(),
                     'selected_submission_utc':submitted.isoformat(),
                     'evidence':{'cohort':records[rid]['file'],
                                 'predecessor_id':p['file']+'#citation_arxiv_id',
                                 'replacement_id':p['file']+'#comments',
                                 'withdrawal':p['file']+'#submission-history',
                                 'selected_version':q['file']+'#submission-history',
                                 'selected_title':'d0088.response#'+target+'v'+str(version),
                                 'current_title':q['file']+'#title'}})
    rows.sort(key=lambda r:(r['predecessor_id'],r['replacement_id']))
    included = {k for k,v in labels.items() if v['classification'].startswith('included_')}
    assert {r['predecessor_id'] for r in rows} == included
    assert len(rows) == 23 and sum(r['title_changed'] for r in rows) == 8
    return rows

def r02_rows(rows):
    # All observed differences are substantive; independent check preserves both titles.
    return [{k:r[k] for k in ('predecessor_id','replacement_id','selected_version')}
            for r in rows if r['title_changed']]

def oai_check():
    root = ET.fromstring(raw('d0103'))
    ns = '{http://arxiv.org/OAI/arXivRaw/}'
    record = root.find('.//'+ns+'arXivRaw')
    versions = record.findall(ns+'version')
    titles = record.findall(ns+'title')
    fields = sorted({c.tag.split('}')[-1] for v in versions for c in v})
    assert len(titles) == 1 and len(versions) == 10
    assert fields == ['date','size']
    assert not any(v.findall('.//'+ns+'title') for v in versions)
    return {'titles':len(titles),'versions':len(versions),'version_fields':fields}

if __name__ == '__main__':
    rows = build()
    fields = json.loads((HERE/'rules.json').read_text())['columns']
    supplied = list(csv.DictReader(io.StringIO((HERE/'oracle.psv').read_text()), delimiter='|'))
    assert r02_rows(rows) == supplied
    print(json.dumps({'r01':rows, 'r02_projection':r02_rows(rows), 'oai':oai_check()}, indent=2))
