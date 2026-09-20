"""Independent provisional reconstruction; not executed during exploration.
Usage: python independent_check.py /path/to/preserved/raw > independent.psv
Uses the June XLSX rather than the live CSV, and HTMLParser rather than regex
HTML extraction. Does not import reference.py or read oracle.psv.
"""
import csv
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

BASE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
HERE = Path(__file__).resolve().parent
SOURCES = json.loads((HERE / 'sources.json').read_text(encoding='utf-8'))
PAGES = {s['species']: s['raw_file'] for s in SOURCES if 'species' in s}

def locate(name):
    direct = BASE / name
    if direct.is_file():
        return direct
    hits = list(BASE.rglob(name))
    assert len(hits) == 1, (name, len(hits))
    return hits[0]

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(locate('d0007.response')) as z:
    strings_root = ET.fromstring(z.read('xl/sharedStrings.xml'))
    strings = [''.join(si.itertext()) for si in strings_root.findall('m:si', NS)]
    sheet = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))

records = {}
header = None
for row in sheet.findall('.//m:sheetData/m:row', NS):
    cells = {}
    for cell in row.findall('m:c', NS):
        col = ''.join(ch for ch in cell.attrib['r'] if ch.isalpha())
        value = cell.find('m:v', NS)
        if value is None:
            continue
        cells[col] = strings[int(value.text)] if cell.get('t') == 's' else value.text
    if header is None:
        header = cells
        assert header['B'] == 'Species' and header['C'] == 'Author'
        continue
    name, authority = cells.get('B'), cells.get('C')
    if not name or not authority:
        continue
    years = re.findall(r'\b\d{4}\b', authority)
    if len(years) != 1:
        # A selected record with an unresolved authority cannot be accepted.
        if name.split()[0] in {'Chelodina', 'Emydura'}:
            raise AssertionError((name, authority))
        continue
    assert name not in records, name
    records[name] = int(years[0])

class TableReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.row = []
        self.cell = None
        self.fields = {}
    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.row = []
        elif tag == 'td':
            self.cell = []
        elif tag == 'br' and self.cell is not None:
            self.cell.append('\n')
    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)
    def handle_endtag(self, tag):
        if tag == 'td' and self.cell is not None:
            self.row.append(''.join(self.cell).strip())
            self.cell = None
        elif tag == 'tr' and len(self.row) >= 2:
            self.fields[self.row[0].strip()] = self.row[1]

def account(name):
    parser = TableReader()
    parser.feed(locate(PAGES[name]).read_text(encoding='utf-8-sig'))
    assert 'Types' in parser.fields, name
    return parser.fields['Types']

seeds = sorted(n for n, y in records.items() if n.split()[0] == 'Chelodina' and y < 1900)
referrals = []
for name in seeds:
    text = account(name)
    if 'accession books' not in text or 'is identified as ' not in text:
        continue
    remainder = text.split('is identified as ', 1)[1]
    matches = [n for n in records if n.split()[0] != 'Chelodina'
               and remainder.startswith(n)
               and (len(remainder) == len(n) or not remainder[len(n)].isalpha())]
    assert len(matches) == 1, (name, matches)
    referrals.append((name, matches[0]))
assert len(referrals) == 1, referrals
referred = referrals[0][1]
account(referred)
genus = referred.split()[0]
selected = sorted(n for n, y in records.items() if n.split()[0] == genus and y < 1900)

writer = csv.writer(sys.stdout, delimiter='|', lineterminator='\n')
writer.writerow(['accepted_species', 'description_year', 'holotype_catalogue'])
for name in selected:
    first_line = next(line.strip() for line in account(name).splitlines() if line.strip())
    assert first_line.startswith('Holotype: ') and '[' not in first_line, (name, first_line)
    words = first_line.removeprefix('Holotype: ').split()
    institution, number = words[:2]
    assert all(ch.isdigit() or ch == '.' for ch in number), (name, number)
    writer.writerow([name, records[name], institution + ' ' + number])
