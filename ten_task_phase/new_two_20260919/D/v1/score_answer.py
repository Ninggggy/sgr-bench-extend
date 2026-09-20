from pathlib import Path
import importlib.util, json, re, sys
ROOT=Path(__file__).parent
spec=importlib.util.spec_from_file_location('scorer',ROOT/'runtime_score_for_review.py')
scorer=importlib.util.module_from_spec(spec);spec.loader.exec_module(scorer)

def canon(v, field):
    v=scorer.clean(v).strip().replace('−','-').replace('–','-').replace('‑','-')
    if field=='lot': return re.sub(r'\s+','',v).upper()
    if field=='agreement_covered':
        z=v.lower().strip()
        if z in {'yes','true','covered'}:return 'YES'
        if z in {'no','false','not covered'}:return 'NO'
        return v
    if field=='eligible_control_body_codes':
        if v.lower() in {'none','n/a','empty set','∅','{}'}:return 'NONE'
        z=v.upper().strip()
        if z.startswith(('{','[')):
            closing='}' if z[0]=='{' else ']'
            if not z.endswith(closing):return '!invalid:'+v
            z=z[1:-1].strip()
            if not z:return 'NONE'
        code=r'CL\s*-\s*BIO\s*-\s*[0-9]{3}'
        sep=r'(?:\s*[;,/]\s*|\s+AND\s+)'
        if not re.fullmatch(code+r'(?:'+sep+code+r')*',z):return '!invalid:'+v
        return ';'.join(sorted({re.sub(r'\s+','',m.group()) for m in re.finditer(code,z)}))
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
    return p['status']=='parsed' and any(len(r['cells'])>=3 and re.fullmatch(r'L[1-9]',r['cells'][0]) and r['cells'][1] in {'YES','NO'} for r in p['rows'])

if __name__=='__main__':print(json.dumps(run(sys.argv[1],sys.argv[2]),indent=2))
