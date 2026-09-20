#!/usr/bin/env python3
"""Identify literal old004 gold rows in observed benchmark tool-return blocks."""
import datetime as dt,json,pathlib,re
T=pathlib.Path(__file__).resolve().parent
raw=json.loads((T/'public_exposure_review.json').read_text());gold=(T/'controller_reference/old_oracle.psv').read_text().splitlines();jobs={j['label']:j for j in json.loads((T/'analysis_plan.json').read_text())['jobs']}
normal=lambda s:re.sub(r'\s+','',s)
findings=[]
for r in raw['runs']:
 matches=[]
 for block in r['returned_blocks']:
  n=normal(block['returned_text']);matched=[row for row in gold if row.strip() and normal(row) in n]
  if matched:matches.append({'file':block['file'],'line':block['line'],'matched_reference_rows':matched,'returned_text':block['returned_text']})
 calls=[c for c in r['native_tool_calls'] if re.search(r'huggingface\.co|SGR[-_/ ]BENCH',str(c['input']),re.I)]
 findings.append({'label':r['label'],'task':jobs[r['label']]['comparison_task'],'phase':r['phase'],'run':r['run'],'classification':'observed_exact_old004_answer_exposure' if matches else 'benchmark_response_without_literal_old004_gold_rows' if r['snippets'] or r['returned_blocks'] else 'no_matching_benchmark_response_detected','literal_gold_exposures':matches,'explicit_benchmark_related_calls':calls,'solver_reported_limitations':r['reported_limitations'],'scope_note':'An absent literal match is not proof of zero contamination or no prior exposure. Scores retained; no replacement attempts.'})
result={'recorded_at':dt.datetime.now(dt.timezone.utc).isoformat(),'findings':findings,'counts':{k:sum(f['classification']==k for f in findings) for k in sorted({f['classification'] for f in findings})},'interpretation':'Exact gold in a returned public benchmark snippet contaminates that attempt even if official values were verified afterward. Report full prescribed scores, never silently exclude or replace exposed runs. No clean ability inference from contaminated means.'}
(T/'public_exposure_findings.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
lines=['# 本轮公开答案暴露检查','','本轮与GPT-6历史检查分开。完整原参考答案出现在实际工具返回时，判为答案暴露；后续官方核验不能消除已见答案。保留全部固定试次，不删分、不替换，不据污染后的均值证明纯能力差。','','|尝试|判定|匹配原答案行数|','|---|---|---:|']
for f in findings:lines.append(f"|{f['label']}|{f['classification']}|{len(set(row for m in f['literal_gold_exposures'] for row in m['matched_reference_rows']))}|")
lines+=['','完整返回文本与行号见[public_exposure_findings.json](public_exposure_findings.json)；全部调用及搜索片段见[public_exposure_review.json](public_exposure_review.json)。未检出只表示已保存返回中未发现匹配片段，不能排除训练、记忆或未识别的暴露渠道。']
(T/'public_exposure_findings.md').write_text('\n'.join(lines)+'\n');print(json.dumps(result['counts']))
