#!/usr/bin/env python3
import json,pathlib,re
T=pathlib.Path(__file__).resolve().parent;plan=json.loads((T/'analysis_plan.json').read_text());screen=pathlib.Path(plan['jobs'][2]['out']);rs=[]
for job in plan['jobs']:
 if job['comparison_task']!='new':continue
 run=pathlib.Path(job['out'])
 if not (run/'answer.txt').exists():continue
 eq=(run/'answer.txt').read_text().strip()==(screen/'answer.txt').read_text().strip();snippets=[]
 for fid,v in json.loads((run/'downloaded_data/registry.json').read_text()).items():
  sql=v.get('sql','')
  for match in re.finditer('ROW_NUMBER',sql,re.I):snippets.append({'file_id':fid,'sql_excerpt':sql[match.start():match.start()+500],'registry':str((run/'downloaded_data/registry.json').relative_to(T))})
 rs.append({'label':job['label'],'answer_equals_screening_GO':eq,'ranking_queries':snippets})
(T/'diagnostics/ranking_evidence.json').write_text(json.dumps(rs,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'reviewed_new_runs':len(rs),'same_wrong_answer_as_screening_GO':[r['label'] for r in rs if r['answer_equals_screening_GO']]}))
