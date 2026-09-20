#!/usr/bin/env python3
"""Separate computation and final transcription errors using archived SQL and data."""
import csv,importlib.util,itertools,json,pathlib,sqlite3
T=pathlib.Path(__file__).resolve().parent;j=next(j for j in json.loads((T/'analysis_plan.json').read_text())['jobs'] if j['label']=='confirmation_new_CG_2');R=pathlib.Path(j['out']);D=R/'downloaded_data';reg=json.loads((D/'registry.json').read_text());spec=importlib.util.spec_from_file_location('sc',R/'implementation/score.py');sc=importlib.util.module_from_spec(spec);spec.loader.exec_module(sc)
query=reg['d0013'];assert set(query['inputs'])=={'p'};fid=query['inputs']['p']['file_id'];data=list(csv.reader((D/reg[fid]['path']).open()));cols=data.pop(0);con=sqlite3.connect(':memory:');q=lambda s:'"'+s.replace('"','""')+'"';con.execute('CREATE TABLE p ('+','.join(q(c)+' TEXT' for c in cols)+')');con.executemany('INSERT INTO p VALUES ('+','.join('?' for c in cols)+')',data)
sql=query['sql'];assert sql.count('ORDER BY e.oxy,e.adate')==1;fixed=sql.replace('ORDER BY e.oxy,e.adate','ORDER BY CAST(e.oxy AS REAL),e.adate')
psv=lambda rows:'\n'.join('|'.join(map(str,r)) for r in rows)+'\n'
computed=psv(con.execute(sql));corrected=psv(con.execute(fixed));raw=(R/'answer.txt').read_text();gold=(T/'controller_reference/new_oracle.psv').read_text();assert corrected==gold
rules=json.loads((R/'controller_scoring/rules.json').read_text());schema=rules['columns'];g=sc.parse(gold,schema)
computed_score=sc.score(g,sc.parse(computed,schema),rules);raw_score=sc.score(g,sc.parse(raw,schema),rules)
changes=[]
for i,(a,b) in enumerate(zip(sc.parse(computed,schema)['rows'],sc.parse(raw,schema)['rows'])):
 for col,x,y in itertools.zip_longest(schema,a['cells'],b['cells']):
  if sc.norm(x,col,rules)!=sc.norm(y,col,rules):changes.append({'row_index':i,'field':col,'computed':x,'raw_final':y})
(T/'diagnostics/confirmation_cg2_computed.psv').write_text(computed);(T/'diagnostics/confirmation_cg2_numeric_order.psv').write_text(corrected);(T/'diagnostics/confirmation_cg2_original.sql').write_text(sql+'\n')
result={'label':j['label'],'run':str(R.relative_to(T)),'raw_score':raw_score['metrics'],'computed_pre_transcription_score':computed_score['metrics'],'transcription_differences':changes,'numeric_order_fix_recovers_all_reference_fields':True,'classification':['numeric sorting as TEXT','final-output transcription corrupts3row identity keys'], 'state_finding':'Archived computation already has the correct5changing withdrawals,12interval/cohort/quarter/count rows. Apparent final omissions/extra rows come from transcription of keys, not an additional state-selection failure.','score_policy':'Keep raw0.495370... score as prescribed. Computed0.657407... is a diagnostic, never substitute it in headline means. Even without transcription errors, no full row is correct because numeric sorting chooses wrong events.','scope':'No model retries, no changes to public input, oracle or grader.'}
(T/'diagnostics/confirmation_cg2_error.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result))
