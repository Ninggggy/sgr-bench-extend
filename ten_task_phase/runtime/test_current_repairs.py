"""Regression tests for the new protocol; no model or network calls."""
import copy
import json
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch
import campaign_runtime as cr
from model_config import tool_profile_config, render_config
from verify_run import verify_model_evidence
from test_model_config import recorded
from check_current_repairs import CURRENT, check

class CurrentRepairsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.campaign = json.loads((CURRENT/'campaign.json').read_text())
        self.path = self.root/'campaign.json'
        self.ledger = self.root/'session_ledger.jsonl'
        self.rows = []
        self.save()
    def tearDown(self):
        self.temp.cleanup()
    def save(self):
        self.path.write_text(json.dumps(self.campaign))
        self.ledger.write_text(''.join(json.dumps(r)+'\n' for r in self.rows))
    def allocate(self, **changes):
        metadata = dict(role='blind',purpose='development',run_id='new',controller_label='new',
                        allocated_at='now',model='gpt-5.6-sol',effort='medium',attempt=1,
                        candidate_id='reptile_001',revision='substantive02',variant='CG',trial=1)
        metadata.update(changes)
        # Exercise real campaign validation using a synthetic authorized root.
        with patch.object(cr, '__file__', str(self.root/'runtime/campaign_runtime.py')):
            return cr.allocate(self.path,self.ledger,self.root/'new',metadata)
    def test_actual_current_config(self):
        self.assertEqual(check()['offline_configuration'], 'passed')
    def test_profile_removes_data_tools_and_rejects_reintroduction(self):
        template = (Path(__file__).parent/'solver.config.toml').read_text()
        config = render_config(tool_profile_config(template,'blind','public_web'),'gpt-5.6-sol','medium')
        self.assertNotIn('mcp_servers',tomllib.loads(config))
        meta,inv,_,turns = recorded()
        meta['tool_profile'] = 'public_web'
        verify_model_evidence(meta,inv,config,turns)
        with self.assertRaises(ValueError):
            verify_model_evidence(meta,inv,config+'\n[mcp_servers.data]\ncommand="python3"\n',turns)
    def test_removed_request_direction_limits_do_not_prevent_allocation(self):
        self.allocate()
        self.assertEqual(len(self.ledger.read_text().splitlines()),1)
    def test_other_tasks_do_not_escape_scope_or_budgets(self):
        with self.assertRaisesRegex(ValueError,'task scope'):
            self.allocate(candidate_id='unregistered_task')
    def test_inherited_blinds_cannot_be_resampled(self):
        with self.assertRaisesRegex(RuntimeError,'resampling'):
            self.campaign['candidate_ids'].append('waterquality_003')
            self.save()
            self.allocate(candidate_id='waterquality_003',revision='sanmarcos01')
    def test_new_blind_identity_cannot_repeat(self):
        self.allocate()
        with self.assertRaisesRegex(RuntimeError,'resampling'):
            self.allocate()
    def test_blind_budget_includes_history(self):
        self.rows = [dict(role='blind',status='completed') for _ in range(26)]
        self.save()
        with self.assertRaisesRegex(RuntimeError,'blind session budget'):
            self.allocate()
    def test_review_budget_and_medium(self):
        with self.assertRaisesRegex(ValueError,'medium'):
            self.allocate(role='audit',purpose='audit',model='gpt-6-astra',effort='high')
        self.rows = [dict(role='audit',status='completed') for _ in range(11)]
        self.save()
        with self.assertRaisesRegex(RuntimeError,'audit session budget'):
            self.allocate(role='audit',purpose='audit',model='gpt-6-astra')
    def test_controller_counts_toward_concurrency(self):
        self.rows = [dict(role='audit',status='running') for _ in range(3)]
        self.save()
        with self.assertRaisesRegex(RuntimeError,'concurrent'):
            self.allocate()
    def test_version_budget_includes_old_revision(self):
        self.rows = [dict(role='blind',status='completed',candidate_id='reptile_001',revision=r) for r in ['v1','v2','v3']]
        self.save()
        with self.assertRaisesRegex(RuntimeError,'version budget'):
            self.allocate()
    def test_other_face_is_not_cancelled_by_first_face_score(self):
        self.rows=[dict(role='blind',status='completed',candidate_id='reptile_001',revision='substantive02',variant='CG',trial=1,item_f1=1.0)]
        self.save()
        self.allocate(variant='GO')
    def test_pair_registration_matches_inputs_and_rejects_missing_face(self):
        for name in ['CG','GO','reference','rules','recompute']:
            (self.root/name).write_text('{}')
        pair=dict(candidate_id='reptile_001',revision='substantive02',protocol_version=self.campaign['protocol_version'],registered_at='2026-01-01T00:00:00+00:00',model='gpt-5.6-sol',effort='medium',tool_profile='public_web',CG='CG',GO='GO',reference='reference',rules='rules',recompute='recompute',slots=[dict(run_id=v,variant=v,trial=1,run_dir=v+'-run') for v in ['CG','GO']])
        pair['registered_contents'] = cr.development_contents(self.root, pair)
        plan=self.root/'plan.json'
        job=dict(candidate_id=pair['candidate_id'],revision=pair['revision'],protocol_version=pair['protocol_version'],plan_path=str(plan),run_id='CG',variant='CG',trial=1)
        plan.write_text(json.dumps(dict(development_rounds=[pair])))
        cr.check_development_pair(self.campaign,job,self.root/'CG',self.root/'reference',self.root/'rules',self.root/'CG-run')
        with self.assertRaisesRegex(ValueError,'registered CG'):
            cr.check_development_pair(self.campaign,job,self.root/'GO',self.root/'reference',self.root/'rules',self.root/'CG-run')
        # Same filenames do not establish that either face uses the recorded version.
        for name in cr.PAIR_ASSETS:
            with self.subTest(changed_asset=name):
                (self.root/name).write_text('{"changed": true}')
                with self.assertRaisesRegex(ValueError, 'Content differs from registered '+name):
                    cr.check_development_pair(self.campaign,job,self.root/'CG',self.root/'reference',self.root/'rules',self.root/'CG-run')
                (self.root/name).write_text('{}')
        second = dict(job, run_id='GO', variant='GO')
        cr.check_development_pair(self.campaign,second,self.root/'GO',self.root/'reference',self.root/'rules',self.root/'GO-run')
        prior = self.root/'CG-run'
        prior.mkdir()
        (prior/'development_registration.json').write_text(json.dumps(pair))
        changed = copy.deepcopy(pair)
        changed['registered_contents']['GO'] = '{"changed":true}'
        (self.root/'GO').write_text(changed['registered_contents']['GO'])
        plan.write_text(json.dumps(dict(development_rounds=[changed])))
        with self.assertRaisesRegex(ValueError, 'already prepared face'):
            cr.check_development_pair(self.campaign,second,self.root/'GO',self.root/'reference',self.root/'rules',self.root/'GO-run')
        (self.root/'GO').write_text('{}')
        (prior/'development_registration.json').unlink()
        saved = pair.pop('registered_contents')
        plan.write_text(json.dumps(dict(development_rounds=[pair])))
        with self.assertRaisesRegex(ValueError, 'retain registered contents'):
            cr.check_development_pair(self.campaign,job,self.root/'CG',self.root/'reference',self.root/'rules',self.root/'CG-run')
        pair['registered_contents'] = saved
        pair['slots'].pop()
        plan.write_text(json.dumps(dict(development_rounds=[pair])))
        with self.assertRaisesRegex(ValueError,'CG and GO'):
            cr.check_development_pair(self.campaign,job,self.root/'CG',self.root/'reference',self.root/'rules',self.root/'CG-run')

    def test_repeat_blinds_cannot_consume_other_tasks_first_pair(self):
        self.rows=[dict(role='blind',status='completed',candidate_id='reptile_001',revision='substantive02',variant='GO',trial=1) for _ in range(24)]
        self.save()
        with self.assertRaisesRegex(RuntimeError,'reserved first review/pair blind'):
            self.allocate()

    def test_ended_history_stays_ended(self):
        self.campaign['ended_at']='2026-09-18T12:00:00+00:00'
        self.save()
        with self.assertRaisesRegex(RuntimeError,'already ended'):
            self.allocate()

    def test_first_reservation_includes_both_active_tasks(self):
        self.assertEqual(cr.first_attempt_reservations(self.campaign, []), {'audit':2,'blind':4})

    def test_repeat_reviews_cannot_consume_other_tasks_first_review(self):
        self.rows=[dict(role='audit',status='completed',candidate_id='reptile_001',revision='substantive02') for _ in range(10)]
        self.save()
        with self.assertRaisesRegex(RuntimeError,'reserved first review/pair audit'):
            self.allocate(role='audit',purpose='audit',model='gpt-6-astra')

    def test_stopped_task_releases_unused_reserve_but_keeps_started_pair(self):
        self.campaign['stopped_candidate_ids']=['reptile_001']
        self.assertEqual(cr.first_attempt_reservations(self.campaign, []), {'audit':1,'blind':2})
        row=dict(role='blind',candidate_id='reptile_001',revision='substantive02',variant='CG')
        self.assertEqual(cr.first_attempt_reservations(self.campaign,[row]), {'audit':1,'blind':3})

    def test_reviews_count_toward_version_limit(self):
        self.rows=[dict(role='audit',status='completed',candidate_id='reptile_001',revision=r) for r in ['v1','v2','v3']]
        self.save()
        with self.assertRaisesRegex(RuntimeError,'version budget'):
            self.allocate(role='audit',purpose='audit',model='gpt-6-astra')

    def test_exited_task_review_rejected(self):
        with self.assertRaisesRegex(ValueError,'task scope'):
            self.allocate(role='audit',purpose='audit',model='gpt-6-astra',candidate_id='wateroffice_002')

if __name__ == '__main__':
    unittest.main()
