#!/usr/bin/env python3
"""Collect observed public benchmark snippets and tool calls for controller review."""
import datetime as dt
import json
from pathlib import Path
import re

B = Path(__file__).resolve().parent
W = B
pattern = re.compile(r'huggingface\.co|SGR[-_/ ]BENCH|github\.com/[^\s]*sgr', re.I)
rows = []
for phase in ('screening', 'confirmation'):
    plan = B / 'analysis_plan.json'
    if not plan.exists():
        continue
    for job in json.loads(plan.read_text())['jobs']:
        if job['phase'] != phase:
            continue
        run = Path(job['out'])
        if not (run / 'run.json').exists():
            continue
        meta = json.loads((run / 'run.json').read_text())
        if meta['status'] != 'completed':
            continue
        snippets, blocks, calls = [], [], []
        for file in (run / 'sessions').glob('*.jsonl'):
            for number, line in enumerate(file.read_text().splitlines(), 1):
                event = json.loads(line)
                value = event.get('payload', {})
                item = value.get('item', {})
                locator = dict(file=str(file.relative_to(W)), line=number)
                if event.get('type') == 'event_msg' and item.get('kind', '').startswith('web.'):
                    for result in item.get('results', []):
                        if pattern.search(result.get('url', '') + ' ' + result.get('title', '')):
                            snippets.append(dict(**locator, result=result))
                if event.get('type') == 'response_item' and value.get('type') in ('custom_tool_call', 'function_call'):
                    calls.append(dict(**locator, name=value.get('name'), input=value.get('input', value.get('arguments', ''))))
                if event.get('type') == 'response_item' and value.get('type') == 'custom_tool_call_output' and isinstance(value.get('output'), list):
                    for output in value['output']:
                        for block in output.get('text', '').split('--------------------------------------------------------------------------------'):
                            if pattern.search(block):
                                blocks.append(dict(**locator, returned_text=block.strip()))
        result = json.loads((run / 'solver_output/result.json').read_text())
        rows.append(dict(label=job['label'], run=str(run.relative_to(W)), phase=phase,
                         reported_limitations=result.get('limitations', []), snippets=snippets,
                         returned_blocks=blocks, native_tool_calls=calls,
                         classification='requires_controller_inspection' if snippets or blocks else 'no_matching_benchmark_response_detected'))
report = dict(recorded_at=dt.datetime.now(dt.timezone.utc).isoformat(), runs=rows,
              scope='Pattern-based collection from actual completed-run search results/tool returns. Not proof of no prior training exposure, no latent memory, or no other unrecognized channel. Controller must inspect matching text and subsequent calls; a task/format snippet is not automatically a gold-answer leak. No scores changed or replacement attempts created.')
(B / 'public_exposure_review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps([dict(label=r['label'], snippets=len(r['snippets']), blocks=len(r['returned_blocks'])) for r in rows]))
