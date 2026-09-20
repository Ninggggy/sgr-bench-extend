"""Recompute the complete June notice scope and titles from saved official XML/PDFs.
Usage: bundled-python reference.py [sources_raw_directory]
Dependency: pypdf. No network and no oracle reads.
"""
from pathlib import Path
import json,re,sys,datetime,xml.etree.ElementTree as ET
from pypdf import PdfReader
here=Path(__file__).resolve().parent
raw=Path(sys.argv[1]) if len(sys.argv)>1 else here/'sources_raw'
registry=json.loads((raw/'live_registry_private.json').read_text())
by_pmc={m['url'].split('/')[-2]:raw/'notice_xml'/m['path'] for m in registry.values() if m.get('url','').endswith('/fullTextXML')}
metadata=json.loads((raw/'d0009.response').read_text())
records=metadata['resultList']['result']
assert metadata['hitCount']==len(records)==len({r['pmcid'] for r in records})
boundaries=json.loads((here/'field_boundaries.json').read_text())
def title(pdf,author):
 text=PdfReader(pdf).pages[0].extract_text()
 start=re.search(r'RESEARCH\s+ARTICLE\s*',text).end()
 end=text.index(author,start)
 return re.sub(r'\s+',' ',text[start:end]).strip()
rows=[]; republications=0
for r in records:
 assert '2015-06-01'<=r['firstPublicationDate']<='2015-06-30'
 assert 'Published Erratum' in r['pubTypeList']['pubType']
 xml=ET.parse(by_pmc[r['pmcid']]).getroot()
 assert xml.find("./front/article-meta/article-id[@pub-id-type='doi']").text==r['doi']
 body=xml.find('body'); text=' '.join(' '.join(body.itertext()).split())
 is_republication=bool(re.search(r'\brepublished\b|\brepublication\b',text,re.I))
 republications+=is_republication
 if not(is_republication and re.search(r'correct (?:an? )?errors? in the title',text,re.I)):continue
 dt=re.search(r'republished on ([A-Za-z]+ \d{1,2}, 2015)',text).group(1)
 date=datetime.datetime.strptime(dt,'%B %d, %Y').date().isoformat()
 ids=set(re.findall(r'10\.1371/journal\.pone\.\d{7}',' '.join(xml.itertext()))) - {r['doi']}
 assert len(ids)==1
 article=ids.pop(); stem='pone.'+r['doi'].rsplit('.',1)[1]
 old=title(raw/(stem+'.s001.pdf'),boundaries[stem]);new=title(raw/(stem+'.s002.pdf'),boundaries[stem])
 assert old!=new
 for suffix in ['s001','s002']:
  content=PdfReader(raw/(stem+'.'+suffix+'.pdf')).pages[0].extract_text()
  assert article in re.sub(r'\s+','',content),'PDF/notice article identity mismatch'
 rows.append((article,date,old,new))
print('article_doi|republication_date|original_title|corrected_title')
for row in sorted(rows): print('|'.join(row))
print(json.dumps({'scope_records':len(records),'republication_notices':republications,'title_republication_notices':len(rows)}),file=sys.stderr)
