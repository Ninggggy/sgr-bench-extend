"""Independent scope/field check using CSV, HTMLParser and font-selected PDF text.
Dependency: pdfplumber. No import from reference.py and no oracle reads.
"""
from pathlib import Path
from html.parser import HTMLParser
import csv,json,re,sys,calendar
import pdfplumber
here=Path(__file__).resolve().parent;raw=Path(sys.argv[1]) if len(sys.argv)>1 else here/'sources_raw'
csv.field_size_limit(10_000_000)
with (raw/'d0010.csv').open(newline='') as f: records=list(csv.DictReader(f))
registry=json.loads((raw/'live_registry_private.json').read_text())
by_pmc={m['url'].split('/')[-2]:raw/'notice_xml'/m['path'] for m in registry.values() if m.get('url','').endswith('/fullTextXML')}
class Body(HTMLParser):
 def __init__(self):super().__init__();self.depth=0;self.parts=[]
 def handle_starttag(self,t,a):
  if t=='body':self.depth+=1
 def handle_endtag(self,t):
  if t=='body':self.depth-=1
 def handle_data(self,d):
  if self.depth:self.parts.append(d)
def header(pdf):
 with pdfplumber.open(pdf) as d:
  page=d.pages[0];size=max(x['size'] for x in page.chars)
  assert 19<size<21, 'Unexpected title typography; inspect changed source'
  chars=[x for x in page.chars if abs(x['size']-size)<.1]
  pieces=[];previous=None
  for char in chars:
   if previous is not None:
    newline=abs(char['top']-previous['top'])>size*.5
    word_gap=char['x0']-previous['x1']>size*.125
    if newline or word_gap:pieces.append(' ')
   pieces.append(char['text']);previous=char
  title=' '.join(''.join(pieces).split())
 return title
assert len(records)==len({r['doi'] for r in records})==164
months={name:i for i,name in enumerate(calendar.month_name) if name}
rows=[]
for row in records:
 assert row['firstPublicationDate'].startswith('2015-06-')
 source=by_pmc[row['pmcid']].read_text();p=Body();p.feed(source);body=' '.join(p.parts)
 if not re.search(r'republished on .*?to correct an error in the title',body,re.I|re.S):continue
 month,day,year=re.search(r'republished on ([A-Za-z]+) (\d+), (\d+)',body).groups()
 date=f'{int(year):04d}-{months[month]:02d}-{int(day):02d}'
 # Resolve the referenced article DOI independently from all XML links/identifiers.
 dois=set(re.findall(r'10\.1371/journal\.pone\.\d{7}',source))-{row['doi']}
 assert len(dois)==1
 stem='pone.'+row['doi'].rsplit('.',1)[1]
 rows.append((dois.pop(),date,header(raw/(stem+'.s001.pdf')),header(raw/(stem+'.s002.pdf'))))
print('article_doi|republication_date|original_title|corrected_title')
for row in sorted(rows):print('|'.join(row))
