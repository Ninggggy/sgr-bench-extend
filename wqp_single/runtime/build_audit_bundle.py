#!/usr/bin/env python3
"""Copy exact authorized candidate evidence into an audit-only isolated data bundle."""
import argparse,json,pathlib,shutil,datetime
p=argparse.ArgumentParser();p.add_argument('--revision',type=pathlib.Path,required=True);p.add_argument('--out',type=pathlib.Path,required=True);p.add_argument('--adjudication',action='store_true');a=p.parse_args();rev=a.revision.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
files=[rev/'candidate.json']
files+=sorted((rev/'public').glob('*.json'))
files+=sorted(x for x in (rev/'private').rglob('*') if x.is_file() and '__pycache__' not in x.parts and 'audit_bundle' not in str(x) and 'adjudication_bundle' not in str(x) and x!=out and out not in x.parents)
for run in sorted((rev/'runs').iterdir()):
 if not run.is_dir():continue
 for rel in ['public/input.json','public/prompt.md','run.json','isolation.json','verification.json','extraction.json','answer.txt','solver_output/result.json','scoring/scores.json','scoring/field_differences.json','tool_events.jsonl','events.jsonl','invocation.json','input_inventory.json','input_inventory_observed.json','data_recovery.json','data_copy_error.txt','downloaded_data/tool_calls.jsonl','downloaded_data/registry.json','solver.config.toml','implementation/run.py','implementation/data_tools.py','implementation/Dockerfile']:
  if (run/rel).is_file():files.append(run/rel)
 for f in (run/'sessions').glob('*.jsonl'):files.append(f)
 # Source bodies are already present in private/sources; per-run exact raw downloads remain in the deliverable.
 # Auditors receive full requests/results, registry, implementation and raw session traces without duplicating every source file.
base=rev.parents[2]
for rel in ['runtime/SCORING.md','runtime/score.py','runtime/environment_report.md','comparisons/analysis_plan.json','comparisons/reference_verification.json','comparisons/old_pair_review.md']:
 f=base/rel
 if f.exists():files.append(f)
registry={};index=[]
for i,f in enumerate(dict.fromkeys(files),1):
 fid='d'+str(i).zfill(4);name=fid+('.csv' if f.suffix=='.csv' else '.response');shutil.copyfile(f,out/name)
 rel=str(f.relative_to(rev)) if f.is_relative_to(rev) else str(f.relative_to(base))
 registry[fid]={'path':name,'audit_source_path':rel,'bytes':f.stat().st_size,'copied_at':datetime.datetime.now(datetime.timezone.utc).isoformat()};index.append({'file_id':fid,'source':rel,'bytes':f.stat().st_size})
(out/'registry.json').write_text(json.dumps(registry,indent=2)+'\n')
(rev/'private'/('adjudication_bundle_index.json' if a.adjudication else 'audit_bundle_index.json')).write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'files':len(index),'bytes':sum(x['bytes'] for x in index),'bundle':str(out)},indent=2))
