"""Exact reports from the reused scorer; no model or score adjustment."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent/'runtime'))
from summarize_current_repairs import face_result

def evaluate(run):
    run = Path(run)
    result = face_result(run)
    scores = json.loads((run/'scoring/scores.json').read_text())
    parsed = json.loads((run/'scoring/parsed.json').read_text())
    c = scores['counts']
    n, d = 2*c['correct_fields'], c['gold_fields']+c['pred_fields']
    result['item_fraction_unreduced'] = {'n': n, 'd': d}
    result['exact_threshold_comparison'] = {'left': 10*n, 'right': 7*d}
    result['format_issues'] = parsed['issues']
    result['whole_task_correct'] = bool(result['whole_task_correct'] and not parsed['issues'] and not parsed['ignored_lines'] and all(x['correct'] for x in scores['order_pairs']))
    if scores['metrics'] is None or parsed['status']=='parse_failure':
        result.update(valid=False, strictly_below_70=False, item_f1_exact=None, row_f1_exact=None, whole_task_correct=False)
    return result

if __name__ == '__main__':
    print(json.dumps(evaluate(sys.argv[1]), ensure_ascii=False, indent=2))
