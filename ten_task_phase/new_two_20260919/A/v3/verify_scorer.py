"""Deterministic conformance fixtures, not model trials."""
from copy import deepcopy
import json
import score_answer as s
R=s.ROOT
rules=json.loads((R/'rules.json').read_text());text=(R/'oracle.psv').read_text();g=s.parse(text,rules)
rows=[r['cells'] for r in g['rows']]
def evaluate(name, rr, correct, denominator, expected_rows=None):
    p=s.parse('\n'.join(' | '.join(r) for r in rr),rules)
    x=s.scorer.score(g,p,rules); c=x['counts'];n=2*c['correct_fields'];d=c['item_denominator']
    assert (c['correct_fields'],d)==(correct,denominator),(name,c)
    if expected_rows is not None:assert c['correct_rows']==expected_rows,(name,c)
    return {'fixture':name,'item_fraction':f'{n}/{d}','strictly_below_70':10*n<7*d,'correct_rows':c['correct_rows']}
results=[evaluate('exact',rows,40,80,8),evaluate('reordered',rows[::-1],40,80,8)]
x=deepcopy(rows)
for row in x:row[0]='Azores';row[1]=row[1].replace('T',' ');row[4]=row[4].replace('{-01:00;+00:00}','{UTC+0, UTC-1}')
results.append(evaluate('documented_aliases_and_syntax',x,40,80,8))
x=deepcopy(rows);x[0][1]='1992-03-29T00:00:01';results.append(evaluate('wrong_start_key',x,35,80,7))
x=deepcopy(rows);x[0][2]='1992-03-29T01:00:01';results.append(evaluate('wrong_nonkey',x,39,80,7))
results.append(evaluate('missing_row',rows[:-1],35,75,7))
x=deepcopy(rows);extra=deepcopy(rows[0]);extra[1]='1991-01-01T00:00:00';x.append(extra);results.append(evaluate('extra_row',x,40,85,8))
results.append(evaluate('duplicate',rows+[rows[0]],40,85,8))
x=deepcopy(rows);x[0].append('extra');results.append(evaluate('extra_column',x,40,81,7))
x=deepcopy(rows);x[0][2]='1992-03-29T00:30:00';extra=deepcopy(rows[0]);extra[1]='1992-03-29T00:30:00';x.append(extra);results.append(evaluate('split_maximal_interval',x,39,85,7))
x=deepcopy(rows);x[0][4]='';results.append(evaluate('blank_not_empty_set',x,39,80,7))
x=deepcopy(rows)
for i in range(2):x[i][1]='wrong'
x[2][2]='wrong';x[3][2]='wrong'
results.append(evaluate('exactly_70_is_not_success',x,28,80))
assert results[-1]['strictly_below_70'] is False
# Parse failure remains unscored, never a qualifying zero.
f=s.scorer.score(g,s.parse('No table could be produced.',rules),rules)
assert f['metrics'] is None
results.append({'fixture':'parse_failure','metrics':None,'qualifying':False})
assert s.canonical('Portugal','zone')=='Portugal'
import tempfile
with tempfile.TemporaryDirectory() as temp:
    tmp=__import__('pathlib').Path(temp)
    for name,answer in [('blank',''),('whitespace','   \n'),('NONE','NONE'),('header_only',' | '.join(rules['columns'])),('delimiter_only','||||||'),('empty_cells',' |  |  |  |  | ')]:
        (tmp/'answer.txt').write_text(answer);r=s.run(tmp/'answer.txt',tmp/name)
        assert r['strictly_below_70'] is None and not r['whole_answer_correct'],(name,r)
        results.append({'fixture':name,**r})
    for name,answer,whole in [('whole_exact',text,True),('whole_reversed','\n'.join(' | '.join(r) for r in rows[::-1]),False),('whole_prose','Explanation\n'+text,False),('backtick_prose',text+'\n``` This answer is correct because ...',False)]:
        (tmp/'answer.txt').write_text(answer);r=s.run(tmp/'answer.txt',tmp/name)
        assert r['whole_answer_correct']==whole,(name,r)
        results.append({'fixture':name,**r})
print(json.dumps({'passed':len(results),'fixtures':results},indent=2))
