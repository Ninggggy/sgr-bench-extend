#!/usr/bin/env python3
"""Controller-only replay of first screening SQL from its own captured data."""
import csv,json,pathlib,sqlite3
T=pathlib.Path(__file__).resolve().parent
j=json.loads((T/'analysis_plan.json').read_text())['jobs'][0];R=pathlib.Path(j['out']);D=R/'downloaded_data';reg=json.loads((D/'registry.json').read_text())
source=reg['d0007'];assert source['derived']
rows=list(csv.reader((D/source['path']).open()));columns=rows.pop(0)
con=sqlite3.connect(':memory:');q=lambda x:'"'+x.replace('"','""')+'"';con.execute('CREATE TABLE c ('+','.join(q(c)+' TEXT' for c in columns)+')');con.executemany('INSERT INTO c VALUES ('+','.join('?' for _ in columns)+')',rows)
original=reg['d0008']['sql'];assert reg['d0008']['inputs']['c']['file_id']=='d0007'
corrected="""WITH RECURSIVE yrs(y) AS (VALUES(2000) UNION ALL SELECT y+1 FROM yrs WHERE y<2019),
 sy AS (SELECT sid,yr FROM c GROUP BY sid,yr HAVING COUNT(DISTINCT q)=4),
 ints(s,e) AS (SELECT y,y FROM yrs UNION ALL SELECT s,e+1 FROM ints WHERE e<2019),
 members AS (
  SELECT i.s,i.e,sy.sid FROM ints i JOIN sy ON sy.yr BETWEEN i.s AND i.e
  GROUP BY i.s,i.e,sy.sid HAVING COUNT(DISTINCT sy.yr)=i.e-i.s+1
 ),
 feas AS (SELECT s,e,e-s+1 dur,COUNT(*) cov FROM members GROUP BY s,e HAVING COUNT(*)>=2),
 front AS (SELECT f.* FROM feas f WHERE NOT EXISTS
  (SELECT 1 FROM feas d WHERE d.dur>=f.dur AND d.cov>=f.cov AND (d.dur>f.dur OR d.cov>f.cov)))
SELECT f.s,f.e,f.dur,f.cov,
 (SELECT group_concat(sid,';') FROM (SELECT sid FROM members m WHERE m.s=f.s AND m.e=f.e ORDER BY sid)) cohort
FROM front f ORDER BY s,e
"""
bad=con.execute(original).fetchall();good=con.execute(corrected).fetchall()
assert [(r[0],r[1],r[3]) for r in good]==[(2013,2019,2),(2014,2014,4),(2014,2015,3)]
(T/'diagnostics').mkdir(exist_ok=True);(T/'diagnostics/first_original_frontier.sql').write_text(original+'\n');(T/'diagnostics/first_corrected_frontier.sql').write_text(corrected)
score=json.loads((R/'scoring/scores.json').read_text())
finding={'label':j['label'],'run':str(R.relative_to(T)),'method':'Replay recorded model SQL on its own full833-activity derived CSV, then correct only cohort construction; no model invocation and no changes to task/oracle/scorer','original_query_registry_file_id':'d0008','source_activity_file_id':'d0007','columns':['start','end','duration','coverage','cohort'],'observed_original_frontier':bad,'corrected_frontier':good,'failure':'Feasibility grouped by interval alone and required COUNT(*)=COUNT(DISTINCT sid)*duration. That demands every station appearing in even one supported year be complete for the interval. Public rule instead retains ALL and ONLY stations individually supporting EVERY year. Partly supported stations therefore incorrectly invalidate legitimate intervals. Same faulty aggregation used after withdrawals.','outcome':{'pred_rows':score['counts']['pred_rows'],'correct_rows':score['counts']['correct_rows'],'omitted_rows':len(score['omitted_ids']),'extra_rows':len(score['extra_ids']),'metrics':score['metrics']},'classification':'reasoning/implementation error in cohort completeness and downstream state selection; not formatting, runtime or observed source drift','limits':'Single screening outcome does not establish comparative difficulty. Confirmation remains fixed and fresh.'}
(T/'diagnostics/first_cg_error.json').write_text(json.dumps(finding,ensure_ascii=False,indent=2)+'\n');print(json.dumps(finding,ensure_ascii=False))
