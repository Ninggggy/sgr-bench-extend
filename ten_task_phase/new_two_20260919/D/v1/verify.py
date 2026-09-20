from pathlib import Path
import json,importlib.util
p=Path('construction_pipeline/ten_task_phase/new_two_20260919/D/v1')
s=importlib.util.spec_from_file_location('d',p/'score_answer.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
r=json.loads((p/'rules.json').read_text());gold=(p/'oracle.psv').read_text();lines=gold.strip().splitlines();rows=lines[1:]
cases={'exact':(gold,54,54),'markdown':('| '+' |\n| '.join([lines[0],'--- | --- | ---']+rows)+' |\n',54,54),'missing':('\n'.join(lines[:-1]),48,51),'duplicate':(gold+rows[0]+'\n',54,57),'extra':(gold+'L10 | YES | NONE\n',54,57),'wrong_set':(gold.replace('CL-BIO-110;CL-BIO-171;CL-BIO-172','CL-BIO-171',1),52,54),'blank_not_none':(gold.replace('YES | NONE','YES | ',1),52,54),'set_aliases':(gold.replace('CL-BIO-110;CL-BIO-171;CL-BIO-172','{cl-bio-172, CL - BIO - 171 and CL-BIO-110}').replace('NONE','∅'),54,54),'duplicate_in_set':(gold.replace('CL-BIO-110;CL-BIO-171;CL-BIO-172','CL-BIO-110;CL-BIO-110;CL-BIO-171;CL-BIO-172'),54,54),'invalid_suffix':(gold.replace('CL-BIO-110;CL-BIO-171;CL-BIO-172','CL-BIO-110;CL-BIO-171;CL-BIO-172XYZ',1),52,54)}
res=[]
for name,(text,n,d) in cases.items():
 pp=m.parse(text,r);ss=m.scorer.score(m.parse(gold,r),pp,r);c=ss['counts'];actual=(2*c['correct_fields'],c['item_denominator']);assert actual==(n,d),(name,actual,n,d)
 res.append({'case':name,'input':text,'expected':[n,d],'actual':actual,'passed':True})
res.append({'case':'exact70rejected','n':7,'d':10,'passed':not 10*7<7*10})
(p/'verification.json').write_text(json.dumps(res,indent=2)+'\n')
print('passed',len(res),'scoring fixtures')
for name,cell in [('dangling_and','CL-BIO-171AND'),('leading_and','AND CL-BIO-171'),('unbalanced','{CL-BIO-171'),('concatenated','CL-BIO-171CL-BIO-110')]:
 assert m.canon(cell,'eligible_control_body_codes').startswith('!invalid:')
 res.append({'case':name,'input':cell,'expected':'invalid','passed':True})
assert m.canon('{  }','eligible_control_body_codes')=='NONE'
for name,text in [('reversed','\n'.join([lines[0]]+rows[::-1])),('extra_prose',gold+'Explanation follows.\n'),('empty',''),('failed','Could not access sources.')]:
 pp=m.parse(text,r);ss=m.scorer.score(m.parse(gold,r),pp,r)
 if name in ['empty','failed']:assert not m.is_substantive(pp)
 elif name=='reversed':assert ss['counts']['correct_rows']==9 and ss['counts']['correct_pairs']<ss['counts']['pair_denominator']
 else:assert ss['counts']['correct_rows']==9 and pp['ignored_lines']
 res.append({'case':name,'input':text,'passed':True,'parsed_status':pp['status'],'issues':pp['issues'],'ignored_lines':pp['ignored_lines']})
(p/'verification.json').write_text(json.dumps(res,indent=2)+'\n')
print('extended fixtures passed',len(res))
import tempfile
endcases=[('reversed', '\n'.join([lines[0]]+rows[::-1]),True,False,True,False),('extra_prose',gold+'Explanation follows.\n',True,False,True,False),('false_fence',gold+'```Explanation follows.\n',True,False,True,False),('empty','',False,False,False,None),('failed','Could not access sources.',False,False,False,None)]
for name,cell in [('dangling_and','CL-BIO-171AND'),('leading_and','AND CL-BIO-171'),('unbalanced','{CL-BIO-171'),('concatenated','CL-BIO-171CL-BIO-110')]:
 text=gold.replace('L8 | NO | CL-BIO-171','L8 | NO | '+cell)
 endcases.append((name+'_full',text,False,False,True,False))
 res.append({'case':name+'_actual','input':cell,'expected_invalid':True,'actual':m.canon(cell,'eligible_control_body_codes'),'passed':m.canon(cell,'eligible_control_body_codes').startswith('!invalid:')})
for cell in ['{   }','[   ]']:
 text=gold.replace('NONE',cell)
 endcases.append(('empty_wrapper_'+cell,text,True,True,True,False))
with tempfile.TemporaryDirectory() as td:
 for name,text,sem,whole,sub,low in endcases:
  a=Path(td)/'answer.txt';a.write_text(text);out=Path(td)/'out';m.run(a,out);sc=json.loads((out/'scores.json').read_text());actual={k:sc[k] for k in ['semantic_table_correct','whole_answer_correct','substantive_submission','strictly_below_70','qualified']};expected=dict(zip(actual,[sem,whole,sub,low,False]));assert actual==expected,(name,actual,expected)
  if name=='reversed':assert sc['counts']['correct_pairs']==0 and sc['counts']['pair_denominator']==36
  if name.endswith('_full'):assert sc['counts']['correct_fields']==26
  res.append({'case':name,'input':text,'expected':expected,'actual':actual,'counts':sc['counts'],'passed':True})
(p/'verification.json').write_text(json.dumps(res,indent=2)+'\n')
print('complete fixtures passed',len(res))
