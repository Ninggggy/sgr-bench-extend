#!/usr/bin/env python3
"""Inspect omitted public output fields without repairing the recorded answer or score."""
import csv,importlib.util,io,json,pathlib
T=pathlib.Path(__file__).resolve().parent;j=next(j for j in json.loads((T/'analysis_plan.json').read_text())['jobs'] if j['label']=='confirmation_new_GO_3');R=pathlib.Path(j['out']);D=R/'downloaded_data';reg=json.loads((D/'registry.json').read_text());rows=list(csv.DictReader((D/reg['d0017']['path']).open()))
cols=['worg','waid','wsite','wdt','sy','ey','coverage','cohort','qtr','eligible_count','sorg','ssite','said','sdt','oxy','temp','cond','ph']
computed='\n'.join('|'.join(('Q'+r[c] if c=='qtr' else r[c]) for c in cols) for r in rows)+'\n'
spec=importlib.util.spec_from_file_location('sc',R/'implementation/score.py');sc=importlib.util.module_from_spec(spec);spec.loader.exec_module(sc);rules=json.loads((R/'controller_scoring/rules.json').read_text());gold=sc.parse((T/'controller_reference/new_oracle.psv').read_text(),rules['columns']);diag=sc.score(gold,sc.parse(computed,rules['columns']),rules);assert all(v==1 for v in diag['metrics'].values())
raw=list(csv.reader(io.StringIO((R/'answer.txt').read_text())));assert len(raw)==13 and all(len(r)==12 for r in raw)
indices=[0,2,1,3,10,11,12,13,14,15,16,17];pred=raw[1:];expected_projection=[[g['cells'][i] for i in indices] for g in gold['rows']]
# Compare rows in emitted order only for content diagnosis, never infer omitted interval keys.
visible=[]
for ri,(got,expected) in enumerate(zip(pred,expected_projection)):
 for ci,(a,b) in enumerate(zip(got,expected)):
  field=rules['columns'][indices[ci]];visible.append({'row_index':ri,'field':field,'actual':a,'reference_projection':b,'equal':sc.norm(a,field,rules)==sc.norm(b,field,rules)})
assert all(f['equal'] for f in visible)
(T/'diagnostics/confirmation_go3_computed_full_table.psv').write_text(computed)
report={'label':j['label'],'run':str(R.relative_to(T)),'raw_parse_status':'parse_failure','official_metrics':None,'raw_content_rows':12,'raw_columns':12,'omitted_required_columns':['start_year','end_year','cohort_station_count','cohort_station_ids','quarter','eligible_activity_count'],'visible_projection_matching_fields':len(visible),'visible_projection':visible,'saved_computation_file_id':'d0017','computed_full_table_diagnostic_metrics':diag['metrics'],'classification':'Final-output completeness/schema deviation. Saved model computation contains all correct216fields, but final answer drops72required fields. This is not evidence of state or minimum-selection reasoning failure.','score_policy':'Keep raw answer and original scorer metrics=null. No gold-dependent repair, no zero imputation, no replacement attempt. Diagnostic full-table score is not substituted into planned means.','limits':'Visible projection checked by emitted row order; missing interval/cohort identity cannot be inferred or awarded from that projection alone.'}
(T/'diagnostics/confirmation_go3_error.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='visible_projection'}))
