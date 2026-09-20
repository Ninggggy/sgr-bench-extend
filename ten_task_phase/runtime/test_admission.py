"""Synthetic fixtures exercise rejection conditions; none are research task records."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import admission as a


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def text(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


class AdmissionTests(unittest.TestCase):
    def test_audit_effort_change_preserves_history_and_enforces_new_setting(self):
        policy = {'construction_effort': 'medium', 'nonblind_effort_change': {
            'effective_at': '2026-09-09T00:30:00+00:00',
            'previous_effort': 'high', 'effort': 'medium'}}
        a.verify_audits(['audit'], self.root, self.c, 'v1', policy)
        self.common_run(self.root/'audit', 'gpt-6-astra', 'medium', '2026-09-09T00:30:00+00:00')
        a.verify_audits(['audit'], self.root, self.c, 'v1', policy)
        self.common_run(self.root/'audit', 'gpt-6-astra', 'high', '2026-09-09T00:30:00+00:00')
        with self.assertRaises(ValueError):
            a.verify_audits(['audit'], self.root, self.c, 'v1', policy)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.scorer = a.module(a.ROOT / 'construction_pipeline/wqp_single/runtime/score.py', 'fixture_scorer')
        self.rules = {'columns': ['id'] + [f'f{i}' for i in range(1, 10)], 'row_key': ['id']}
        self.gold = '|'.join(self.rules['columns']) + '\n' + '|'.join(['x'] * 10)
        self.c = {'candidate_id': 'new_synthetic', 'revision': 1, 'ecosystem': 'KEGG', 'domain': 'KEGG',
                  'status': 'content_validated', 'validation': {'content': 'passed', 'human_validation': 'not_performed'},
                  'public': {v: {'instruction': 'Synthetic ' + v, 'output_format': 'table'} for v in ('cg', 'go')},
                  'private': {'oracle_path': 'oracle.psv', 'source_manifest_path': 'source.json', 'reference_script_path': 'reference.py',
                              'state_graph_path': 'state.json', 'start_urls': ['https://rest.kegg.jp'], 'predicates': ['synthetic']}}
        put(self.root/'candidate.json', self.c)
        text(self.root/'oracle.psv', self.gold)
        for asset in ['source.json', 'reference.py', 'state.json']:
            text(self.root/asset, 'synthetic fixture')
        put(self.root/'rules.json', self.rules)
        self.campaign = {'protocol_version': 'v1', 'current_date': '2026-09-09', 'max_seconds_per_session': 6000, 'stall_seconds': 3000}
        self.campaign['protocol_assets'] = {'registered_at': '2026-09-09T00:30:00+00:00', 'solver_config_path': 'protocol/solver.config.toml', 'scorer_path': 'protocol/score.py', 'data_tools_path': 'protocol/data_tools.py', 'image_id': 'synthetic_image'}
        put(self.root/'campaign.json', self.campaign)
        self.round = {'candidate_id': 'new_synthetic', 'revision': 1, 'protocol_version': 'v1',
                      'registered_at': '2026-09-09T01:00:00+00:00', 'audit_paths': ['audit'], 'rules_path': 'rules.json',
                      'slots': [{'variant': v, 'trial': i, 'run_id': f'{v}{i}', 'run_dir': f'{v}{i}', 'label': f'retest_{v}_{i}'} for v in ('CG','GO') for i in (1,2,3)]}
        self.plan = {'protocol_version': 'v1', 'admission_rounds': [self.round]}
        put(self.root/'plan.json', self.plan)
        self.common_run(self.root/'audit', 'gpt-6-astra', 'high', '2026-09-09T00:00:00+00:00')
        text(self.root/'audit/evidence.txt', 'Synthetic evidence, not a real audit.')
        checks = {k: {'verdict': 'pass', 'evidence_paths': ['evidence.txt'], 'substantive_progress': True,
                      'error_category': 'scope', 'explanation': 'Fixture explanation.'} for k in
                  ['content','sgr','semantic_alignment','substantive_errors_cg','substantive_errors_go']}
        put(self.root/'audit/solver_output/result.json', {'candidate_id': 'new_synthetic', 'revision': 1, 'protocol_version': 'v1', 'checks': checks})
        ledger = []
        for slot in self.round['slots']:
            run = self.root/slot['run_dir']
            meta = self.common_run(run, 'gpt-5.6-sol', 'medium', '2026-09-09T02:00:00+00:00')
            meta.update(candidate_id='new_synthetic', revision=1, protocol_version='v1', stage='admission_retest',
                        variant=slot['variant'], trial=slot['trial'], controller_label=slot['label'])
            put(run/'run.json', meta)
            put(run/'admission_registration.json', self.round)
            put(run/'public/input.json', {**self.c['public'][slot['variant'].lower()], 'current_date': '2026-09-09'})
            put(run/'isolation.json', {'image_id': 'synthetic_image', 'bind_mounts': [], 'read_only_rootfs': True, 'probe': [{'readable': False}]*3,
                                      'cap_drop': ['ALL'], 'security_opt': ['no-new-privileges']})
            put(run/'controller_scoring/rules.json', self.rules)
            text(run/'controller_scoring/oracle.psv', self.gold)
            (run/'implementation').mkdir()
            shutil.copy(a.ROOT/'construction_pipeline/wqp_single/runtime/score.py', run/'implementation/score.py')
            text(run/'implementation/data_tools.py', '# synthetic tool fixture')
            self.score(run, 6)
            ledger.append({'run_dir': slot['run_dir'], 'label': slot['label']})
        for source, target in [('solver.config.toml', 'solver.config.toml'), ('implementation/score.py', 'score.py'), ('implementation/data_tools.py', 'data_tools.py')]:
            text(self.root/'protocol'/target, (self.root/'CG1'/source).read_text())
        text(self.root/'ledger.jsonl', ''.join(json.dumps(x)+'\n' for x in ledger))
        self.manifest = {'campaign_path': 'campaign.json', 'plan_path': 'plan.json', 'ledger_path': 'ledger.jsonl',
                         'candidates': [{'candidate_path': 'candidate.json', 'family': 'synthetic'}]}
        put(self.root/'manifest.json', self.manifest)

    def common_run(self, run, model, effort, started):
        meta = {'model': model, 'effort': effort, 'provider': 'openai', 'status': 'completed', 'exit_code': 0,
                'completed_event': True, 'errors': [], 'started_at': started, 'ended_at': started,
                'current_date': '2026-09-09', 'maximum_seconds': 6000, 'stall_seconds': 3000}
        put(run/'run.json', meta)
        put(run/'invocation.json', ['docker','exec','-i',run.name,'codex','exec','--model',model,'-c',f'model_reasoning_effort="{effort}"'])
        text(run/'solver.config.toml', f'model="{model}"\nmodel_reasoning_effort="{effort}"\nmodel_provider="openai"\n')
        records = [{'type': 'session_meta', 'payload': {'id': run.name}}, {'type': 'turn_context', 'payload': {'model':model,'effort':effort}}]
        text(run/'sessions/trace.jsonl', ''.join(json.dumps(r)+'\n' for r in records))
        text(run/'events.jsonl', '{"type":"turn.completed"}\n')
        return meta

    def score(self, run, correct):
        answer = '|'.join(self.rules['columns'])+'\n'+'|'.join(['x']*correct+['wrong']*(10-correct))
        text(run/'answer.txt', answer)
        put(run/'solver_output/result.json', {'final_answer': answer})
        computed = self.scorer.score(self.scorer.parse(self.gold,self.rules['columns']),self.scorer.parse(answer,self.rules['columns']),self.rules)
        put(run/'scoring/scores.json', {k:v for k,v in computed.items() if k!='field_differences'})
        put(run/'scoring/field_differences.json', computed['field_differences'])

    def result(self):
        return a.evaluate(self.root/'manifest.json')[0]['candidates'][0]

    def mutate(self, path, field, value):
        obj = a.read(self.root/path)
        obj[field] = value
        put(self.root/path,obj)

    def test_valid_export(self):
        result = self.result()
        self.assertTrue(result['admitted'], result)
        self.assertEqual(result['CG']['mean_exact'], '3/5')
        summary = a.export(self.root/'manifest.json', self.root/'export')
        self.assertTrue(summary['partial_delivery'])
        self.assertEqual(len((self.root/'export/constraint.jsonl').read_text().splitlines()), 1)
        self.assertEqual(a.read(self.root/'export/constraint.jsonl')['task_id'], 'new_synthetic')
        self.assertEqual(a.read(self.root/'export/goal.jsonl')['task_id'], 'new_synthetic-g')

    def test_campaign_protocol_change(self):
        text(self.root/'GO3/implementation/data_tools.py', '# changed tool')
        with self.assertRaisesRegex(ValueError, 'campaign protocol'):
            self.result()

    def test_other_campaign_blind_run_protocol(self):
        shutil.copytree(self.root/'GO3', self.root/'old_control')
        text(self.root/'old_control/implementation/data_tools.py', '# different tools for old control')
        with (self.root/'ledger.jsonl').open('a') as f:
            f.write(json.dumps({'run_dir': 'old_control', 'label': 'comparison_old'})+'\n')
        with self.assertRaisesRegex(ValueError, 'campaign protocol'):
            self.result()

    def test_inline_audit_asset(self):
        result = a.read(self.root/'audit/solver_output/result.json')
        content = json.dumps(result)
        put(self.root/'audit/solver_output/result.json', {'files': [{'path': 'audit.json', 'content': content}]})
        text(self.root/'audit/stage_assets/audit.json', content)
        self.assertTrue(self.result()['admitted'])
        text(self.root/'audit/stage_assets/audit.json', '{}')
        self.assertFalse(self.result()['admitted'])

    def test_exact_boundary_rejected(self):
        for v in ['CG','GO']:
            for i in [1,2,3]: self.score(self.root/f'{v}{i}', 7)
        result = self.result()
        self.assertEqual(result['CG']['mean_exact'], '7/10')
        self.assertFalse(result['admitted'])

    def test_either_variant_above_rejected(self):
        for v in ['CG','GO']:
            with self.subTest(variant=v):
                for i in [1,2,3]: self.score(self.root/f'{v}{i}',8)
                self.assertFalse(self.result()['admitted'])
                for i in [1,2,3]: self.score(self.root/f'{v}{i}',6)

    def test_missing_score(self):
        (self.root/'GO3/scoring/scores.json').unlink()
        self.assertEqual(self.result()['status'], 'inconclusive')

    def test_non_numeric_score(self):
        saved = a.read(self.root/'GO3/scoring/scores.json')
        saved['metrics']['Item-F1'] = None
        put(self.root/'GO3/scoring/scores.json', saved)
        self.assertFalse(self.result()['admitted'])

    def test_mixed_version(self):
        self.mutate('GO1/run.json','revision',2)
        self.assertFalse(self.result()['admitted'])

    def test_unplanned_substitution(self):
        self.round['slots'][0]['label'] = 'replacement'
        put(self.root/'plan.json',self.plan)
        self.assertFalse(self.result()['admitted'])

    def test_duplicate_trial(self):
        self.round['slots'][0]['trial'] = 2
        put(self.root/'plan.json',self.plan)
        self.assertFalse(self.result()['admitted'])

    def test_repeated_round(self):
        self.plan['admission_rounds'].append(copy.deepcopy(self.round))
        put(self.root/'plan.json',self.plan)
        self.assertFalse(self.result()['admitted'])

    def test_development_trial(self):
        self.mutate('CG1/run.json','stage','shortcut_attack')
        self.assertFalse(self.result()['admitted'])

    def test_failed_audit(self):
        result = a.read(self.root/'audit/solver_output/result.json')
        result['checks']['sgr']['verdict'] = 'fail'
        put(self.root/'audit/solver_output/result.json',result)
        self.assertFalse(self.result()['admitted'])

    def test_user_exception_cannot_admit_other_candidate(self):
        self.manifest['candidates'][0]['user_designated_exception'] = {'authorized_by': 'user'}
        put(self.root/'manifest.json', self.manifest)
        with self.assertRaisesRegex(ValueError, 'only authorized for WQP r03'):
            a.evaluate(self.root/'manifest.json')

    def test_wqp_exception_preserves_standard_rejection(self):
        self.c.update(candidate_id='wqp_activity_panel_001', revision=3)
        put(self.root/'candidate.json', self.c)
        decision = {'authorized_by': 'user', 'historical_evidence_paths': ['oracle.psv']}
        self.manifest['candidates'][0]['user_designated_exception'] = decision
        put(self.root/'manifest.json', self.manifest)
        with self.assertRaisesRegex(ValueError, 'missing recorded user'):
            a.evaluate(self.root/'manifest.json')
        self.campaign['admission_amendments'] = [decision]
        put(self.root/'campaign.json', self.campaign)
        summary, results = a.evaluate(self.root/'manifest.json')
        self.assertEqual(summary['accepted_count'], 1)
        self.assertEqual(summary['standard_accepted_count'], 0)
        self.assertEqual(summary['user_designated_count'], 1)
        report = results[0][0]
        self.assertFalse(report['standard_assessment']['admitted'])
        self.assertIsNone(report['protocol_version'])
        self.assertEqual(report['CG']['trials'], [])

    def test_actual_model_mismatch(self):
        text(self.root/'GO2/sessions/trace.jsonl', json.dumps({'type':'turn_context','payload':{'model':'gpt-6-astra','effort':'high'}})+'\n')
        self.assertFalse(self.result()['admitted'])

    def test_arxiv_r03_exception_exports_and_preserves_threshold_failure(self):
        # Synthetic records exercise the explicit exception without changing research scores.
        def identity(value):
            if isinstance(value, dict):
                if value.get('candidate_id') == 'new_synthetic':
                    value.update(candidate_id='arxiv_historical_title_002', revision=3)
                for child in value.values():
                    identity(child)
            elif isinstance(value, list):
                for child in value:
                    identity(child)
        for path in self.root.rglob('*.json'):
            if path.name in {'source.json', 'state.json'}:
                continue  # These two fixture evidence files intentionally contain plain text.
            value = a.read(path)
            identity(value)
            put(path, value)
        candidate = a.read(self.root/'candidate.json')
        candidate['private']['scoring_rules_path'] = 'rules.json'
        candidate['validation']['difficulty'] = 'user_designated_exception'
        put(self.root/'candidate.json', candidate)
        for i in (1, 2, 3):
            self.score(self.root/f'CG{i}', 8)
        decision = {'authorized_by': 'user', 'historical_evidence_paths': ['oracle.psv']}
        self.manifest['candidates'][0]['user_designated_exception'] = decision
        put(self.root/'manifest.json', self.manifest)
        self.campaign['admission_amendments'] = [decision]
        put(self.root/'campaign.json', self.campaign)
        summary = a.export(self.root/'manifest.json', self.root/'export')
        report = summary['candidates'][0]
        self.assertTrue(report['admitted'])
        self.assertEqual(report['status'], 'user_designated_exception')
        self.assertEqual(report['standard_assessment']['status'], 'rejected_threshold')
        self.assertEqual(report['standard_assessment']['CG']['mean_exact'], '4/5')
        self.assertEqual(report['standard_assessment']['GO']['mean_exact'], '3/5')
        exported = a.read(self.root/'export/constraint.jsonl')
        self.assertFalse(exported['metadata']['standard_protocol_passed'])
        self.assertEqual(exported['oracle_output_cardinality'], 1)


if __name__ == '__main__':
    unittest.main()


class RetrievalAdmissionTests(unittest.TestCase):
    def test_requires_injected_policy_and_evidenced_compliance(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);run=base/'trial';run.mkdir()
            text(base/'policy.md','Bounded retrieval')
            campaign={'protocol_version':'ten-task-v2-bounded-retrieval',
                      'protocol_assets':{'retrieval_policy_path':'policy.md'}}
            text(run/'public/retrieval_policy.md','Bounded retrieval')
            text(run/'public/prompt.md','Bounded retrieval\n\nTask')
            with self.assertRaises(FileNotFoundError): a.verify_retrieval_policy(run,campaign,base)
            review={'run_id':'trial','protocol_version':campaign['protocol_version'],'verdict':'passed',
                    'checks':{n:{'verdict':'passed','explanation':'Synthetic trajectory check',
                                 'evidence_paths':['tool_events.jsonl']} for n in
                              ('bulk_scope','query_dependencies','pagination','request_count','concurrency','safety')}}
            text(run/'tool_events.jsonl','Synthetic fixture, not an experiment')
            put(run/'retrieval_review.json',review)
            a.verify_retrieval_policy(run,campaign,base)
            review['checks']['safety']['verdict']='failed';put(run/'retrieval_review.json',review)
            with self.assertRaises(ValueError): a.verify_retrieval_policy(run,campaign,base)
            text(run/'public/prompt.md','Task without policy')
            with self.assertRaises(ValueError): a.verify_retrieval_policy(run,campaign,base)
