#!/usr/bin/env python3
"""Deterministic, provisional strict scorer. No model judges or gold-dependent selection."""
import argparse, csv, io, json, re, unicodedata
from pathlib import Path
def clean(s):
    s = unicodedata.normalize('NFKC', str(s)).strip()
    s = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', s)
    return re.sub(r'\s+', ' ', s.strip('`* ')).strip()

def norm(s, field, rules):
    if s is None: return None
    from decimal import Decimal, InvalidOperation
    s=clean(s);rule=rules.get('fields',{}).get(field,{})
    s=rule.get('aliases',{}).get(s,s)
    if rule.get('uppercase'): s=s.upper()
    kind=rule.get('type','string')
    if kind=='id_list':
        members=[x.strip("\"'[]") for x in re.split(r'[;,\s]+',s) if x.strip("\"'[]")]
        return ';'.join(sorted(set(members)))
    if kind in ['integer','decimal']:
        try:
            if rule.get('units'):
                m=re.fullmatch(r'([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*(.*)',s)
                if not m: return 'INVALID:'+s
                number=Decimal(m[1]);unit=m[2]
                if unit:
                    conversion={clean(k):v for k,v in rule['units'].items()}.get(unit)
                    if conversion is None: return 'INVALID_UNIT:'+s
                    number=(number-Decimal(str(conversion.get('offset',0))))*Decimal(str(conversion.get('scale_num',1)))/Decimal(str(conversion.get('scale_den',1)))
            else: number=Decimal(s)
            if not number.is_finite() or (kind=='integer' and number!=number.to_integral()): return 'INVALID:'+s
            return format(number.normalize(),'f')
        except (InvalidOperation,ValueError): return 'INVALID:'+s
    return s

def parse(answer, schema):
    """Keep every data row, duplicates and malformed widths; never use gold values."""
    if not answer.strip() or answer.strip().upper() == 'NONE':
        return {'status':'empty', 'rows':[], 'ignored_lines':[], 'issues':[]}
    lines = answer.splitlines(); rows=[]; ignored=[]; issues=[]; header=False
    for n, line in enumerate(lines, 1):
        if not line.strip() or line.strip().startswith('```'): continue
        if '|' in line:
            body=line.strip()
            if body.startswith('|'): body=body[1:]
            if body.endswith('|'): body=body[:-1]
            cells=[x.strip().replace(r'\|','|') for x in re.split(r'(?<!\\)\|',body)]
        elif '\t' in line:
            cells=line.split('\t')
        elif ',' in line:
            cells=next(csv.reader([line]))
        else:
            ignored.append({'line':n,'text':line}); continue
        if all(re.fullmatch(r':?-{3,}:?', x.strip()) for x in cells): continue
        if [clean(x).casefold() for x in cells] == [x.casefold() for x in schema]:
            header=True; continue
        # Prose with commas is not a CSV row unless a header has established a table.
        if '|' not in line and '\t' not in line and not header:
            ignored.append({'line':n,'text':line}); continue
        if len(cells)!=len(schema): issues.append({'line':n,'kind':'wrong_width','actual':len(cells),'expected':len(schema)})
        rows.append({'line':n,'raw':line,'cells':cells})
    # Header is optional, consistent with WQP's public data-rows-only format.
    status='parsed' if rows else 'parse_failure'
    return {'status':status,'rows':rows,'ignored_lines':ignored,'issues':issues}

def score(gold, pred, rules):
    schema=rules['columns']; key_indices=[schema.index(f) for f in rules['row_key']]
    k=len(schema)
    def vals(row): return [norm(row['cells'][j], f, rules) if j<len(row['cells']) else None for j,f in enumerate(schema)]
    gv=[vals(r) for r in gold['rows']]; pv=[vals(r) for r in pred['rows']]
    row_key=lambda v:tuple(v[j] for j in key_indices)
    gi={row_key(v):i for i,v in enumerate(gv)}
    assert len(gi)==len(gv), 'Duplicate gold keys require adjudication'
    seen={}; duplicates=[]; diffs=[]; ci=cr=0
    for i,v in enumerate(pv):
        key=row_key(v); duplicate=key in seen
        if duplicate: duplicates.append({'id':key,'pred_index':i,'first_index':seen[key]})
        else: seen[key]=i
        target=gv[gi[key]] if key in gi and not duplicate else None
        correct=[]
        for j,f in enumerate(schema):
            ok=target is not None and v[j] is not None and v[j]!='' and v[j]==target[j]
            correct.append(ok); ci+=int(ok)
            diffs.append({'pred_index':i,'id':key,'field':f,'pred_raw':pred['rows'][i]['cells'][j] if j<len(pred['rows'][i]['cells']) else None,'pred_normalized':v[j],'gold':target[j] if target else None,'correct':ok,'reason':'duplicate_id_no_credit' if duplicate else 'unmatched_id' if target is None else 'match' if ok else 'missing_or_different'})
        cr+=int(all(correct) and len(pred['rows'][i]['cells'])==k)
    missing=[row_key(v) for v in gv if row_key(v) not in seen]
    for key in missing:
        for j,f in enumerate(schema): diffs.append({'pred_index':None,'id':key,'field':f,'pred_raw':None,'pred_normalized':None,'gold':gv[gi[key]][j],'correct':False,'reason':'omitted_row'})
    shared=[row_key(v) for v in gv if row_key(v) in seen]
    pairs=[{'first':a,'second':b,'correct':seen[a]<seen[b]} for i,a in enumerate(shared) for b in shared[i+1:]]
    ng=len(gv)*k; np=sum(max(k,len(r['cells'])) for r in pred['rows'])
    counts={'correct_fields':ci,'gold_fields':ng,'pred_fields':np,'item_denominator':ng+np,'correct_rows':cr,'gold_rows':len(gv),'pred_rows':len(pv),'row_denominator':len(gv)+len(pv),'correct_pairs':sum(p['correct'] for p in pairs),'pair_denominator':len(pairs),'shared_ids':len(shared)}
    return {'status':rules.get('status','deterministic_explicit') if pred['status']!='parse_failure' else 'parse_failure_unscored','metrics': {'Item-F1':2*ci/(ng+np) if ng+np else 0,'Row-F1':2*cr/(len(gv)+len(pv)) if gv or pv else 0,'P.O.A.':sum(p['correct'] for p in pairs)/len(pairs) if pairs else 0} if pred['status']!='parse_failure' else None,'counts':counts,'omitted_ids':missing,'extra_ids':[x for x in seen if x not in gi],'duplicate_ids':duplicates,'order_pairs':pairs,'poa_note':'fewer than two shared IDs => 0' if len(shared)<2 else 'first occurrence positions; no reordering','field_differences':diffs}

def write(path,obj): path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

def main():
    p=argparse.ArgumentParser()
    for name in ['answer','gold','rules','out']: p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    rules=json.loads(a.rules.read_text());schema=rules['columns']
    g=parse(a.gold.read_text(),schema);pred=parse(a.answer.read_text(),schema)
    assert g['status']=='parsed' and len(rules['row_key'])>0
    result=score(g,pred,rules)
    write(a.out/'parsed.json',pred);write(a.out/'gold_parsed.json',g)
    write(a.out/'scores.json',{k:v for k,v in result.items() if k!='field_differences'})
    write(a.out/'field_differences.json',result['field_differences'])
    print(json.dumps({k:result[k] for k in ['status','metrics','counts']},ensure_ascii=False))
if __name__=='__main__': main()
