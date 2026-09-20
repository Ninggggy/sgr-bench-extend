import json
import tempfile
import unittest
from pathlib import Path
from summarize_current_repairs import face_result, qualifies, summarize

class SummaryTests(unittest.TestCase):
    def test_wrong_revision_or_face_cannot_be_combined(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); (p/'scoring').mkdir()
            meta=dict(status='completed', verification_status='passed', actual_model='gpt-5.6-sol', actual_effort='medium', candidate_id='reptile_001', revision='v1', variant='CG', trial=1)
            (p/'run.json').write_text(json.dumps(meta))
            (p/'scoring/scores.json').write_text(json.dumps(dict(counts=dict(correct_fields=3,item_denominator=10))))
            (p/'retrieval_review.json').write_text(json.dumps(dict(verdict='passed', capability_score_eligible=True, access_confounded=False, format_confounded=False, answer_exposure_review='passed')))
            expected={k:meta[k] for k in ('candidate_id','revision','variant','trial')}
            self.assertTrue(face_result(p,expected)['valid'])
            for changes in [dict(revision='v2'),dict(variant='GO'),dict(candidate_id='arxiv_historical_title_001'),dict(revision=None)]:
                self.assertFalse(face_result(p,{**expected,**changes})['valid'])

    def face(self, n, d, **review_changes):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); (p/'scoring').mkdir()
            (p/'run.json').write_text(json.dumps(dict(status='completed', verification_status='passed',actual_model='gpt-5.6-sol',actual_effort='medium')))
            (p/'scoring/scores.json').write_text(json.dumps(dict(counts=dict(correct_fields=n,item_denominator=d,correct_rows=0,row_denominator=2))))
            r=dict(verdict='passed', capability_score_eligible=True, access_confounded=False,format_confounded=False,answer_exposure_review='passed');r.update(review_changes)
            (p/'retrieval_review.json').write_text(json.dumps(r))
            return face_result(p)
    def test_exact_boundary_and_independent_faces(self):
        low=self.face(3,10); boundary=self.face(7,20)
        self.assertTrue(qualifies('passed',{'CG':low,'GO':low}))
        self.assertFalse(qualifies('passed',{'CG':low,'GO':boundary}))
        self.assertEqual(boundary['item_f1_exact'],'7/10')
    def test_missing_and_invalid_do_not_qualify(self):
        low=self.face(3,10)
        self.assertFalse(qualifies('passed',{'CG':low}))
        for changes in [dict(access_confounded=True),dict(format_confounded=True),dict(answer_exposure_review='pending'),dict(verdict='pending'),dict(capability_score_eligible=False)]:
            self.assertFalse(qualifies('passed',{'CG':low,'GO':self.face(0,10,**changes)}))
        self.assertFalse(qualifies('pending',{'CG':low,'GO':low}))
    def test_current_scope_is_two_incomplete_tasks(self):
        result=summarize()
        self.assertEqual(len(result['tasks']),2)
        self.assertFalse(result['goal_completed'])
        self.assertEqual(result['blind_sessions_used'],4)
        self.assertEqual(result['review_sessions_used'],4)
