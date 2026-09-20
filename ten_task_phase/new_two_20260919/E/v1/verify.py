from pathlib import Path
import json,tempfile
import score_answer as sa
import recompute as rc
p=Path(__file__).parent
assert rc.fold['\u03d2']=='\u03c5'
assert rc.inranges('\u1d2c',rc.prohibited['A.1'])
assert not rc.inranges('\u03c5',rc.prohibited['A.1'])
assert rc.U.normalize('NFKC','\U0002f868')=='\U0002136a'
assert rc.inranges('\u0301',rc.marks)
rows,tr=rc.compute();assert len(rows)==6
assert rows==[[x.strip() for x in line.split('|')] for line in (p/'oracle.psv').read_text().splitlines()[1:]]
assert tr==json.loads((p/'derived.json').read_text())
assert sa.canon('U+20','any_prepared')=='U+0020'
assert sa.canon('U+D800','any_prepared').startswith('!invalid:')
assert sa.canon('U+0020JUNK','any_prepared').startswith('!invalid:')
assert rows[2][-1]=='FALSE' and rows[4][-1]=='UNDEFINED'
gold=(p/'oracle.psv').read_text();ls=gold.strip().splitlines();checks=[]
cases=[('exact',gold,72,72,True,True,True,False),('missing','\n'.join(ls[:-1]),60,66,False,False,True,False),('duplicate',gold+ls[1]+'\n',72,78,False,False,True,False),('reverse','\n'.join([ls[0]]+ls[:0:-1]),72,72,True,False,True,False),('prose',gold+'```Explanation follows.\n',72,72,True,False,True,False),('empty','',0,36,False,False,False,None),('failed','Access failed.',0,36,False,False,False,None),('suffix',gold.replace('U+03C5','U+03C5JUNK',1),70,72,False,False,True,False),('blank_failure',gold.replace('FAIL','',1),70,72,False,False,True,False),('aliases',gold.replace('U+','0x').replace('FAIL','FAILED'),72,72,True,True,True,False)]
with tempfile.TemporaryDirectory() as td:
 for name,text,n,d,sem,whole,sub,low in cases:
  a=Path(td)/'answer.txt';a.write_text(text);out=Path(td)/'out';sa.run(a,out);s=json.loads((out/'scores.json').read_text());actual=[2*s['counts']['correct_fields'],s['counts']['item_denominator'],s['semantic_table_correct'],s['whole_answer_correct'],s['substantive_submission'],s['strictly_below_70']];expected=[n,d,sem,whole,sub,low];assert actual==expected,(name,actual,expected);checks.append({'name':name,'input':text,'expected':expected,'actual':actual,'passed':True})
assert not 10*7<7*10
(p/'verification.json').write_text(json.dumps(checks,indent=2)+'\n');print('PASS',len(checks))

import platform,sys,datetime
(p/'recomputation_verification.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,'implementation':platform.python_implementation(),'ucd':rc.U.unidata_version,'all_rows_equal':True,'all_stages_equal':True,'computed_rows':rows,'computed_stages':tr,'historical_2F868_actual':rc.hx(rc.U.normalize('NFKC','\U0002f868')),'short_hex_actual':sa.canon('U+20','any_prepared'),'surrogate_actual':sa.canon('U+D800','any_prepared')},indent=2)+'\n')
