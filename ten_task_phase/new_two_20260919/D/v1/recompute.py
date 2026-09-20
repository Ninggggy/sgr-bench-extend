"""Extract candidate bodies and Chile rows; join inventory with source predicates.

Legal classification of agreement exclusions is in law_predicates.json, with
locators for independent review. It contains no lot-level eligibility answers.
"""
from pathlib import Path
import json,re
P=Path(__file__).parent
def compute():
    src=(P/'amendment.txt').read_text()
    recital=next(x for x in src.splitlines() if x.startswith('The Commission has received'))
    names=re.findall('‘([^’]+)’',recital)
    annex=src.split('\nANNEX I\n')[1].split('\nANNEX II\n')[0]
    candidates=[]
    for i,name in enumerate(names):
        start=annex.index(name);end=annex.index(names[i+1],start) if i+1<len(names) else len(annex)
        lines=annex[start:end].splitlines();rows=[]
        for j,line in enumerate(lines):
            if re.fullmatch('CL-BIO-\\d+',line):
                assert lines[j+1]=='Chile'
                cells=lines[j+2:j+9];assert len(cells)==7 and all(x in ('x','x°','—') for x in cells)
                rows.append(dict(code=line,categories=dict(zip('ABCDEFG',cells))))
        candidates.append(dict(name=name,chile_rows=rows,inclusion='Has newly inserted Chile recognition' if rows else 'New entry has no Chile row'))
    assert len(candidates)==15
    countries=(P/'country_list.txt').read_text().split('\nANNEX I\n')[1].split('\nANNEX II\n')[0]
    country_names=re.findall(r'(?m)^([A-Z][A-Z ]+)\n1\.\nProduct categories$',countries)
    assert set(country_names)=={'ARGENTINA','AUSTRALIA','CANADA','COSTA RICA','ISRAEL','INDIA','JAPAN','REPUBLIC OF KOREA','NEW ZEALAND','TUNISIA','UNITED STATES'}
    assert 'PERU' not in country_names and 'CHILE' not in country_names
    law=json.loads((P/'law_predicates.json').read_text());out=[];decisions=[]
    for lot in json.loads((P/'inventory.json').read_text()):
        assert (lot['lot'],lot['hs'],lot['category']) in {(f'L{i}',h,c) for i,(h,c) in enumerate([('0903','A'),('0602','A'),('1521','G'),('3301','G'),('3301','G'),('2007','D'),('2007','D'),('0302','C'),('2204','F')],1)}
        assert set(lot['origins']) <= {'Chile','France','Peru'}, 'Country membership alone cannot prove regime scope for new origins'
        rule=law['chapter_rules'][lot['hs'][:2]]
        listed=rule['base'] and lot['kind'] not in rule.get('excluded_kinds',[]) and (not rule.get('food_only') or lot['food'])
        origins=all(o=='Chile' or o in law['EU_origins_in_inventory'] or o.upper() in country_names for o in lot['origins'])
        covered=listed and (not lot['processed'] or lot['food']) and origins
        eligible=[];why=[]
        for c in candidates:
            for r in c['chile_rows']:
                cell=r['categories'][lot['category']]
                ok=cell=='x' or (cell=='x°' and not covered)
                if ok:eligible.append(r['code'])
                why.append(dict(code=r['code'],cell=cell,eligible=ok,reason='category absent' if cell=='—' else 'equivalence exception' if cell=='x°' and covered else 'scope available'))
        out.append([lot['lot'],'YES' if covered else 'NO',';'.join(sorted(eligible)) or 'NONE'])
        decisions.append(dict(lot=lot['lot'],tariff_scope=listed,ingredient_origin_qualifies=origins,agreement_covered=covered,decisions=why))
    return out,dict(candidates=candidates,country_equivalence_headings=country_names,lot_decisions=decisions)
if __name__=='__main__':
    rows,trace=compute();(P/'derived.json').write_text(json.dumps(trace,ensure_ascii=False,indent=2)+'\n')
    (P/'oracle.psv').write_text('lot | agreement_covered | eligible_control_body_codes\n'+'\n'.join(' | '.join(r) for r in rows)+'\n')
    print((P/'oracle.psv').read_text())
