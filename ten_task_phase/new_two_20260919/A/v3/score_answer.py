"""Documented syntax and unambiguous identity normalization, followed by the existing five-field scorer."""
from pathlib import Path
import datetime, importlib.util, json, re, sys
ROOT=Path(__file__).resolve().parent
RUNTIME=ROOT/'runtime_score_for_review.py'
spec=importlib.util.spec_from_file_location('runtime_score',RUNTIME)
scorer=importlib.util.module_from_spec(spec);spec.loader.exec_module(scorer)

def canonical(value,field):
    value=scorer.clean(value).replace('−','-')
    if field=='zone':
        return {'Azores':'Atlantic/Azores','Madeira':'Atlantic/Madeira','Lisbon':'Europe/Lisbon'}.get(value,value)
    if field in ('start_local','end_local'):
        try:
            parsed=datetime.datetime.fromisoformat(value)
            if parsed.tzinfo is not None:return value
            return parsed.isoformat(timespec='seconds') if not parsed.microsecond else value
        except ValueError:return value
    if field.startswith('offsets_'):
        if value in ('{}','[]','∅','empty set'):return '{}'
        if not value:return value  # missing is not an empty set
        tokens=re.split(r'[;,]',value.strip('{}[]() '));numbers=[]
        for token in tokens:
            token=token.strip().upper().replace('UTC','').replace('GMT','').replace(' ','')
            if token=='Z':token='0'
            match=re.fullmatch(r'([+-]?)(\d{1,2})(?::(\d{2}))?',token)
            if not match:return value
            sign,hour,minute=match.groups();hour=int(hour);minute=int(minute or 0)
            if hour>24 or minute>59:return value
            numbers.append((-1 if sign=='-' else 1)*(hour*60+minute))
        return '{'+';'.join(('+' if n>=0 else '-')+f'{abs(n)//60:02d}:{abs(n)%60:02d}' for n in sorted(set(numbers)))+'}'
    return value

def parse(text,rules):
    parsed=scorer.parse(text,rules['columns'])
    for line in text.splitlines():
        if line.strip().startswith('```') and not re.fullmatch(r'```(?:csv|tsv|psv|text|markdown|md|table)?\s*',line.strip(),re.I):
            parsed['ignored_lines'].append({'text':line,'reason':'not_supported_fence_delimiter'})
    for row in parsed['rows']:
        row['cells']=[canonical(c,rules['columns'][i]) if i<len(rules['columns']) else c for i,c in enumerate(row['cells'])]
    return parsed

def run(answer,out):
    rules=json.loads((ROOT/'rules.json').read_text())
    gold=parse((ROOT/'oracle.psv').read_text(),rules);pred=parse(Path(answer).read_text(),rules)
    result=scorer.score(gold,pred,rules)
    substantive=pred['status']=='parsed' and any(any(c.strip() for c in row['cells']) for row in pred['rows'])
    result['substantive_submission']=substantive
    c=result['counts'];n=2*c['correct_fields'];d=c['item_denominator']
    result.update(item_fraction=f'{n}/{d}',strictly_below_70=10*n<7*d if substantive and result['metrics'] else None,
                  semantic_table_correct=c['correct_rows']==c['gold_rows']==c['pred_rows'] and pred['status']=='parsed',
                  whole_answer_correct=c['correct_rows']==c['gold_rows']==c['pred_rows'] and pred['status']=='parsed' and not pred['ignored_lines'] and not pred['issues'] and c['correct_pairs']==c['pair_denominator'])
    result['offset_field_accuracy']={f:{'correct':sum(x['correct'] for x in result['field_differences'] if x['field']==f),'gold':c['gold_rows']} for f in ('offsets_2024a','offsets_2024b')}
    out=Path(out);out.mkdir(exist_ok=True,parents=True)
    for name,value in [('parsed.json',pred),('scores.json',result)]:
        (out/name).write_text(json.dumps(value,indent=2)+'\n')
    return {k:result[k] for k in ('item_fraction','strictly_below_70','whole_answer_correct','counts')}

if __name__=='__main__':print(json.dumps(run(sys.argv[1],sys.argv[2]),indent=2))
