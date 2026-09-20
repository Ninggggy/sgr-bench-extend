from pathlib import Path
import importlib.util, json, re, sys
ROOT=Path(__file__).parent
spec=importlib.util.spec_from_file_location('scorer',ROOT/'runtime_score_for_review.py')
scorer=importlib.util.module_from_spec(spec);spec.loader.exec_module(scorer)

def canon(v,field):
    v=scorer.clean(v).strip()
    if field=='case':return re.sub(r'\s+','',v).upper()
    if field=='result':return {'yes':'TRUE','true':'TRUE','no':'FALSE','false':'FALSE','undefined':'UNDEFINED','indeterminate':'UNDEFINED'}.get(v.lower(),v)
    if field.endswith('_prepared'):
        if v.upper() in {'FAIL','FAILED','PREPARATION FAILED','PROHIBITED'}:return 'FAIL'
        if v.upper() in {'EMPTY','EMPTY STRING','[]'}:return 'EMPTY'
        z=v.upper().strip()
        if z.startswith('['):
            if not z.endswith(']'):return '!invalid:'+v
            z=z[1:-1].strip()
            if not z:return 'EMPTY'
        token=r'(?:U\+|0X)?[0-9A-F]{1,6}'
        if not re.fullmatch(token+r'(?:(?:\s+|\s*,\s*)'+token+r')*',z):return '!invalid:'+v
        values=[int(re.sub(r'^(?:U\+|0X)','',m.group()),16) for m in re.finditer(token,z)]
        if any(n>0x10FFFF or 0xD800<=n<=0xDFFF for n in values):return '!invalid:'+v
        return ' '.join(f'U+{n:04X}' for n in values)
    return v

def parse(text,rules):
    p=scorer.parse(text,rules['columns'])
    for row in p['rows']:
        row['cells']=[canon(v,rules['columns'][i]) if i<len(rules['columns']) else v for i,v in enumerate(row['cells'])]
    return p

def run(answer,out):
    rules=json.loads((ROOT/'rules.json').read_text());g=parse((ROOT/'oracle.psv').read_text(),rules);p=parse(Path(answer).read_text(),rules)
    s=scorer.score(g,p,rules);c=s['counts'];n=2*c['correct_fields'];d=c['item_denominator']
    substantive=is_substantive(p)
    s.update(item_fraction=f'{n}/{d}',substantive_submission=substantive,strictly_below_70=(10*n<7*d if substantive and s['metrics'] else None),qualification='pending independent trajectory/access/exposure review',qualified=False,semantic_table_correct=c['correct_rows']==c['gold_rows']==c['pred_rows'] and p['status']=='parsed',whole_answer_correct=c['correct_rows']==c['gold_rows']==c['pred_rows'] and p['status']=='parsed' and not p['issues'] and not p['ignored_lines'] and c['correct_pairs']==c['pair_denominator'])
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for f,obj in [('parsed.json',p),('scores.json',s)]: (out/f).write_text(json.dumps(obj,indent=2)+'\n')
    return {k:s[k] for k in ['item_fraction','strictly_below_70','whole_answer_correct','counts']}
def is_substantive(p):
    return p['status']=='parsed' and any(len(r['cells'])>=6 and re.fullmatch(r'T[1-6]',r['cells'][0]) and r['cells'][5] in {'TRUE','FALSE','UNDEFINED'} for r in p['rows'])

if __name__=='__main__':print(json.dumps(run(sys.argv[1],sys.argv[2]),indent=2))
