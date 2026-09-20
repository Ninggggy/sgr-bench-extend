from pathlib import Path
import importlib.util, json, re, sys
ROOT=Path(__file__).parent
spec=importlib.util.spec_from_file_location('scorer',ROOT/'runtime_score_for_review.py')
scorer=importlib.util.module_from_spec(spec);spec.loader.exec_module(scorer)

def canon(v, field):
    v=scorer.clean(v).strip().replace('−','-')
    if field=='configuration': return v.upper().replace(' ','').replace('/','')
    if field=='VS': return v.title()
    nulls={'v0_offset':{'none','n/a','not saved','absent','∅'},'overwritten_integer_bytes':{'none','n/a','no overwrite','no overwrites','∅'}}
    if v.lower() in nulls.get(field,set()): return 'NONE'
    if field in ('frame_bytes','ra_offset','f0_offset','v0_offset'):
        try:return str(int(v,16) if v.lower().startswith('0x') else int(v))
        except ValueError:return v
    if field in ('fcsr_range','overwritten_integer_bytes'):
        v=re.sub(r'\s+','',v)
        number=r'(?:0x[0-9a-f]+|[0-9]+)'
        interval=r'\[('+number+r'),('+number+r')\)'
        pattern=interval if field=='fcsr_range' else r'(ra|x(?:[0-9]|[12][0-9]|3[01])):'+interval
        parts=[]
        for part in v.split(';'):
            m=re.fullmatch(pattern,part,re.I)
            if not m:return '!invalid:'+v
            values=m.groups();lo,hi=[int(n,16) if n.lower().startswith('0x') else int(n) for n in values[-2:]]
            if hi<=lo:return '!invalid:'+v
            reg='' if field=='fcsr_range' else ('x1' if values[0].lower()=='ra' else values[0].lower())+':'
            parts.append(f'{reg}[{lo},{hi})')
        if field=='fcsr_range' and len(parts)!=1:return '!invalid:'+v
        v=';'.join(sorted(parts))
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
    return p['status']=='parsed' and any(len(r['cells'])>=8 and r['cells'][0] in {'RV32F32','RV32F64','RV64F32','RV64F64'} and r['cells'][1] in {'Clean','Dirty'} and any(re.fullmatch(r'[0-9]+',v) for v in r['cells'][2:5]) for r in p['rows'])

if __name__=='__main__':print(json.dumps(run(sys.argv[1],sys.argv[2]),indent=2))
