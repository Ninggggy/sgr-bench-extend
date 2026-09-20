"""Read saved results without rescoring or calling models."""
import json
from fractions import Fraction
from pathlib import Path
from check_current_repairs import CURRENT


def read(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def face_result(run, expected=None):
    meta = read(run/'run.json', {})
    score = read(run/'scoring/scores.json', {})
    review = read(run/'retrieval_review.json', {})
    counts = score.get('counts', {})
    def ratio(num, den):
        n, d = counts.get(num), counts.get(den)
        return Fraction(2*n, d) if type(n) is int and type(d) is int and d > 0 and 0 <= 2*n <= d else None
    item = ratio('correct_fields', 'item_denominator')
    row = ratio('correct_rows', 'row_denominator')
    identity_matches = expected is None or all(value is not None and meta.get(key) == value for key, value in expected.items())
    eligible = (identity_matches and meta.get('status') == 'completed' and meta.get('verification_status') == 'passed'
                and (meta.get('actual_model'), meta.get('actual_effort')) == ('gpt-5.6-sol', 'medium')
                and review.get('verdict') == 'passed' and review.get('capability_score_eligible') is True
                and review.get('access_confounded') is False and review.get('format_confounded') is False
                and review.get('answer_exposure_review') == 'passed' and item is not None)
    return dict(item_f1_exact=str(item) if item is not None else None,
                row_f1_exact=str(row) if row is not None else None,
                whole_task_correct=item == 1 and row == 1, valid=eligible,
                strictly_below_70=eligible and 10*item.numerator < 7*item.denominator,
                retrieval_review=review, elapsed_seconds=meta.get('elapsed_seconds'), usage=meta.get('usage'),
                run_dir=str(run))


def qualifies(quality, faces):
    return quality == 'passed' and set(faces) == {'CG', 'GO'} and all(f['valid'] and f['strictly_below_70'] for f in faces.values())


def summarize(directory=CURRENT):
    campaign=read(directory/'campaign.json')
    rows=[json.loads(line) for line in (directory/'session_ledger.jsonl').read_text().splitlines() if line.strip()]
    tasks=[]
    for cid in campaign['candidate_ids']:
        versions=set(campaign.get('inherited_versions', {}).get(cid, []))
        versions.update(r['revision'] for r in rows if r.get('candidate_id') == cid and r.get('revision'))
        final=read(directory/cid/'final.json', {})
        faces={v:face_result(directory/p, dict(candidate_id=cid, revision=final.get('revision'), variant=v, trial=1)) for v,p in final.get('runs', {}).items()}
        quality=read(directory/final['quality_review'], {}).get('verdict') if final.get('quality_review') else 'not_reviewed'
        tasks.append(dict(candidate_id=cid, revision=final.get('revision'), quality=quality, faces=faces,
                          qualified=qualifies(quality, faces), versions_used=len(versions),
                          incomplete_reason=final.get('incomplete_reason', 'Source completeness, substantive revision and final paired trials not yet verified.')))
    return dict(goal_completed=all(t['qualified'] for t in tasks) and len(tasks)==2 and campaign['candidate_ids']==['reptile_001', 'arxiv_historical_title_001'], tasks=tasks,
                blind_sessions_used=campaign['inherited_blind_sessions']+sum(r.get('role')=='blind' for r in rows),
                review_sessions_used=campaign['inherited_review_sessions']+sum(r.get('role')=='audit' for r in rows),
                interpretation='Development-selected single paired tests; not unbiased final evaluation or historical three-trial means.')

if __name__ == '__main__':
    print(json.dumps(summarize(), ensure_ascii=False, indent=2))
