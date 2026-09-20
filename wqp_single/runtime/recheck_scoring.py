#!/usr/bin/env python3
"""Repair a declared Unicode unit alias implementation after retaining initial scores.
No task/rule/oracle edits. Original scores and per-run implementation copies retained.
"""
import datetime as dt,importlib.util,json,pathlib,shutil,subprocess,sys
B=pathlib.Path(__file__).resolve().parent;P=B.parent/'candidates/wqp_activity_panel_001/r01/private';marker=B/'scoring_maintenance.json'
if marker.exists():raise SystemExit(0)
plan=json.loads((P/'content_run_plan.json').read_text())
for j in plan['jobs']:
 r=pathlib.Path(j['out']);m=json.loads((r/'run.json').read_text());assert m['status']=='completed' and m['completed_event']
initial_spec=importlib.util.spec_from_file_location('initial_scorer',B/'score.py');initial=importlib.util.module_from_spec(initial_spec);initial_spec.loader.exec_module(initial)
rules_before=json.loads((P/'scoring_rules.json').read_text())
pre_repair=[{'input':x,'field':f,'old_normalized':initial.norm(x,f,rules_before),'expected':e} for x,f,e in [('1000 µg/L','dissolved_oxygen_mg_L','1'),('1000 μg/L','dissolved_oxygen_mg_L','1'),('1 µS/cm','specific_conductance_uS_cm','1'),('1 μS/cm','specific_conductance_uS_cm','1')]]
assert all(x['old_normalized']!=x['expected'] for x in pre_repair)
old=(B/'score.py').read_text();needle="conversion=rule['units'].get(unit)";assert needle in old
(B/'history').mkdir(exist_ok=True);shutil.copyfile(B/'score.py',B/'history/score_initial.py');shutil.copyfile(B/'verify_run.py',B/'history/verify_run_initial.py')
(B/'score.py').write_text(old.replace(needle,"conversion={clean(k):v for k,v in rule['units'].items()}.get(unit)"))
spec=importlib.util.spec_from_file_location('unicode_scorer',B/'score.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
rules=json.loads((P/'scoring_rules.json').read_text())
assert mod.norm('1000 µg/L','dissolved_oxygen_mg_L',rules)=='1'
assert mod.norm('1000 μg/L','dissolved_oxygen_mg_L',rules)=='1'
assert mod.norm('1 µS/cm','specific_conductance_uS_cm',rules)=='1'
assert mod.norm('1 μS/cm','specific_conductance_uS_cm',rules)=='1'
# Preserve/replay historical per-run scorer instead of accidentally using a later global implementation.
v=(B/'verify_run.py').read_text().replace('from score import parse,score,write','from score import write\nimport importlib.util')
v=v.replace("run=Path(sys.argv[1]);meta=", "run=Path(sys.argv[1]);spec=importlib.util.spec_from_file_location('run_scorer',run/'implementation/score.py');scorer=importlib.util.module_from_spec(spec);spec.loader.exec_module(scorer);parse=scorer.parse;score=scorer.score\nmeta=")
v=v.replace("for f in ['score.py','verify_run.py']:\n if (run/'implementation'/f).exists(): assert (run/'implementation'/f).read_bytes()==Path(__file__).with_name(f).read_bytes()", "checks['historical_scorer']='Recomputed with this run implementation/score.py; later global scorer edits do not replace recorded scoring semantics.'")
(B/'verify_run.py').write_text(v)
run=(B/'run.py').read_text().replace("str(BASE/'score.py'),'--answer'","str(run/'implementation/score.py'),'--answer'")
(B/'run.py').write_text(run)
checks=[]
for j in plan['jobs']:
 r=pathlib.Path(j['out']);out=r/'scoring_rule_recheck'
 subprocess.run([sys.executable,str(B/'score.py'),'--answer',str(r/'answer.txt'),'--gold',str(r/'controller_scoring/oracle.psv'),'--rules',str(r/'controller_scoring/rules.json'),'--out',str(out)],check=True,stdout=subprocess.DEVNULL)
 before=json.loads((r/'scoring/scores.json').read_text());after=json.loads((out/'scores.json').read_text());assert before==after
 checks.append({'run':str(r.relative_to(P.parent)),'original_scores_retained':True,'repaired_implementation_scores_equal':True})
report={'at':dt.datetime.now(dt.timezone.utc).isoformat(),'kind':'Implementation repair for an equivalence already declared before blind solves','issue':'NFKC converts micro sign U+00B5 to Greek mu U+03BC; initial code normalized predicted text but not the predeclared units dictionary keys. Four explicit alias checks reproduce then resolve the mismatch.','change':'Normalize both dictionary unit keys and prediction using the existing clean() function. No unit rule, oracle, public condition or tolerance change.','original_implementation':'history/score_initial.py and each run implementation/score.py','new_tests':'µg/L and μg/L at1000 ->1 mg/L; µS/cm and μS/cm ->1 microSiemens/cm','pre_repair_reproductions':pre_repair,'run_checks':checks,'substantive_candidate_revision':False,'score_changes':False,'future_replay':'Future runner scores with its own saved implementation/score.py. verify_run.py replays historical saved scorers.'}
marker.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(P/'protocol/scoring_maintenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');shutil.copyfile(B/'score.py',P/'protocol/score.py')
print(json.dumps({'unicode_alias_checks':'passed','all_initial_scores_retained_and_unchanged':True,'runs_recomputed':len(checks)}),flush=True)
