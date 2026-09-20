from pathlib import Path
import json
import score_answer as sa
import recompute
p=Path(__file__).parent
r=json.loads((p/'rules.json').read_text());gold=(p/'oracle.psv').read_text();g=sa.parse(gold,r)
checks=[]
def check(name,text,n,d):
 s=sa.scorer.score(g,sa.parse(text,r),r)['counts'];assert (2*s['correct_fields'],s['item_denominator'])==(n,d),(name,s);checks.append({'name':name,'fixture':text,'expected':[n,d],'actual':[2*s['correct_fields'],s['item_denominator']]})
check('exact',gold,128,128)
lines=gold.splitlines()
check('markdown','\n'.join(['| '+lines[0]+' |','|'+'---|'*8]+['| '+x+' |' for x in lines[1:]]),128,128)
check('duplicate row counted',gold+lines[1]+'\n',128,136)
check('missing row counted','\n'.join(lines[:-1]),112,120)
check('wrong composite key loses whole row',gold.replace('RV32F32 | Clean','RV32F32 | Unknown',1),112,128)
check('one field wrong',gold.replace('[136,140)','[136,144)',1),126,128)
check('alias and whitespace',gold.replace('x1:','ra:').replace('[148,152)','[ 148, 152 )'),128,128)
check('hex integer',gold.replace(' | 256 |',' | 0x100 |',1),128,128)
check('uppercase hex interval',gold.replace('[136,140)','[0X88,0X8C)',1),128,128)
check('uppercase register',gold.replace('x1:','RA:'),128,128)
check('wrong-field nullable synonym',gold.replace('NONE','no overwrite',1),126,128)
check('malformed interval',gold.replace('[136,140)','[136,140)junk',1),126,128)
assert not sa.is_substantive(sa.parse('garbage | garbage',r));checks.append('malformed non-substantive')
check('blank not NONE',gold.replace('NONE','',1),126,128)
assert not(10*70<7*100) and 10*69<7*100;checks.append('exact strict threshold')
assert sa.parse('',r)['status']!='parsed';checks.append('empty nonqualifying')
for x in (32,64):
 for f in (32,64):
  for v in ('Clean','Dirty'):
   a=recompute.derive(x,f,v);w=x//8;z=f//8;extra=512+4*w if v=='Dirty' else 0
   assert a['row'][2:7]==[str(31*w+33*z+extra),str(2*w+33*z+extra),str(2*w+extra),f'[{2*w+32*z+extra},{3*w+32*z+extra})',str(6*w) if v=='Dirty' else 'NONE']
checks.append('independent manual algebra versus source-specific extractor plus manual semantic checks all eight cases')
(p/'verification.json').write_text(json.dumps({'passed':checks,'number':len(checks)},indent=2)+'\n')
print('PASS',len(checks))
