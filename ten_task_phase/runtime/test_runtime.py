import datetime as dt
import json
import os
import tempfile
import unittest
from pathlib import Path
from campaign_runtime import allocate, check_campaign, existing_state, validate_retry
from stage_results import materialize_files, validate
from run import session_stop_reason


class SessionLimitTests(unittest.TestCase):
    def test_unlimited_session_retains_stall_and_campaign_deadline(self):
        now=dt.datetime.now(dt.timezone.utc)
        metadata={'maximum_seconds':None,'stall_seconds':3000}
        self.assertIsNone(session_stop_reason({'deadline':None},metadata,600000,10,now))
        self.assertEqual(session_stop_reason({'deadline':None},metadata,600000,3001,now),'stalled')
        self.assertEqual(session_stop_reason({'deadline':now.isoformat()},metadata,600000,10,now),'campaign_deadline')

    def test_null_campaign_deadline_preserves_session_limits(self):
        campaign={'deadline':None}
        metadata={'maximum_seconds':6000,'stall_seconds':3000}
        now=dt.datetime.now(dt.timezone.utc)
        self.assertIsNone(session_stop_reason(campaign,metadata,10,2,now))
        self.assertIsNone(session_stop_reason(campaign,metadata,6000,3000,now))
        self.assertEqual(session_stop_reason(campaign,metadata,6001,2,now),'timeout')
        self.assertEqual(session_stop_reason(campaign,metadata,100,3001,now),'stalled')

    def test_explicit_deadline_still_stops_at_boundary(self):
        now=dt.datetime.now(dt.timezone.utc)
        campaign={'deadline':now.isoformat()}
        metadata={'maximum_seconds':6000,'stall_seconds':3000}
        self.assertIsNone(session_stop_reason(campaign,metadata,10,2,now-dt.timedelta(seconds=1)))
        self.assertEqual(session_stop_reason(campaign,metadata,10,2,now),'campaign_deadline')
        self.assertEqual(session_stop_reason(campaign,metadata,6001,3001,now),'timeout')


class StageTests(unittest.TestCase):
    def test_recovered_registered_artifact_requires_real_safe_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); data=root/'data'; data.mkdir()
            (data/'rows.csv').write_text('id\n1\n')
            registry=data/'registry.json'
            result={'files':[{'path':'note.md','content':'Evidence.'}],
                    'artifacts':[{'path':'d0109'}]}
            registry.write_text(json.dumps({'d0109':{'path':'rows.csv'}}))
            self.assertEqual(len(materialize_files(result,root/'assets',registered_data=data)),2)
            materialize_files(result,root/'assets',registered_data=data,write=False)
            for bad in ['../outside.csv','missing.csv','/etc/passwd']:
                registry.write_text(json.dumps({'d0109':{'path':bad}}))
                with self.assertRaises(ValueError):
                    materialize_files(result,root/'other',registered_data=data)

    def test_inline_content_and_reported_artifacts(self):
        result={'files':[{'path':'src/ref.py','content':'print(42)\n'},
                         {'path':'oracle.json','content':'{"x":42}\n'}],
                'artifacts':[{'path':'src/ref.py'},{'path':'oracle.json'}]}
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)/'assets'
            self.assertEqual(len(materialize_files(result,out)),2)
            materialize_files(result,out,write=False)
            (out/'oracle.json').write_text('{}')
            with self.assertRaises(ValueError):
                materialize_files(result,out,write=False)

    def test_bad_path_missing_content_and_bad_program_rejected(self):
        fixtures=[{'files':[{'path':'../escape','content':'x'}]},
                  {'files':[{'path':'/absolute','content':'x'}]},
                  {'files':[{'path':'ref.py','content':'def ( :'}]},
                  {'files':[{'path':'oracle.json','content':'not json'}]},
                  {'files':[],'artifacts':[{'path':'missing'}]},
                  {'files':[{'path':'same','content':'x'},{'path':'same','content':'y'}]}]
        with tempfile.TemporaryDirectory() as directory:
            for value in fixtures:
                with self.subTest(value=value),self.assertRaises((ValueError,SyntaxError)):
                    materialize_files(value,Path(directory)/'assets')

    def test_stage_schema_not_solver_fields(self):
        schema=json.loads((Path(__file__).parent/'construction_result.schema.json').read_text())
        result={'status':'completed','summary':'reference saved','artifacts':[],
                'evidence_refs':[],'issues':[],'next_action':'audit','files':[]}
        validate(result,schema)
        with self.assertRaises(ValueError):
            validate({'status':'complete','final_answer':'solver output'},schema)


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent.parent, prefix='.runtime-test-')
        self.root=Path(self.temp.name)/'ten_task_phase';self.root.mkdir()
        self.path=self.root/'campaign.json';self.ledger=self.root/'session_ledger.jsonl'
        now=dt.datetime.now(dt.timezone.utc)
        self.campaign={'started_at':now.isoformat(),'deadline':(now+dt.timedelta(hours=48)).isoformat(),
                       'current_date':'2026-09-09','max_sessions':300,
                       'maximum_concurrent_model_sessions':4,'repair_retries_allowed':1,
                       'reserved_pending_sessions':0}
        self.save()

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        self.path.write_text(json.dumps(self.campaign))

    def allocate(self,purpose='development'):
        return allocate(self.path,self.ledger,self.root/'run',
                        {'purpose':purpose,'run_id':'run','controller_label':'fixture',
                         'allocated_at':'now','model':'gpt-5.6-sol','effort':'medium',
                         'role':'blind','attempt':1})

    def test_new_campaign_ledger_and_exact_budget(self):
        with self.assertRaises(ValueError):
            check_campaign(self.path,self.root.parent/'old.jsonl')
        self.campaign['max_sessions']=1;self.save()
        self.allocate()
        with self.assertRaises(RuntimeError):
            self.allocate()
        self.assertEqual(len(self.ledger.read_text().splitlines()),1)

    def test_reservation_and_concurrency(self):
        self.campaign['max_sessions']=3;self.campaign['reserved_pending_sessions']=3;self.save()
        with self.assertRaises(RuntimeError):
            self.allocate()
        self.allocate('admission')
        self.campaign['maximum_concurrent_model_sessions']=1;self.save()
        with self.assertRaises(RuntimeError):
            self.allocate('admission')

    def test_wall_clock_window_never_resets(self):
        self.campaign['deadline']=(dt.datetime.now(dt.timezone.utc)-dt.timedelta(seconds=1)).isoformat();self.save()
        with self.assertRaises(RuntimeError):
            self.allocate()

    def test_uncapped_campaign_keeps_ledger_concurrency_and_deadline(self):
        self.campaign['max_sessions']=None
        self.campaign['reserved_pending_sessions']=65
        self.save()
        self.ledger.write_text(''.join(json.dumps({'status':'completed'})+'\n' for _ in range(301)))
        self.assertEqual(self.allocate()['session_number'],302)
        self.campaign['maximum_concurrent_model_sessions']=1;self.save()
        with self.assertRaisesRegex(RuntimeError,'concurrent'):
            self.allocate()
        self.campaign['deadline']=(dt.datetime.now(dt.timezone.utc)-dt.timedelta(seconds=1)).isoformat();self.save()
        with self.assertRaisesRegex(RuntimeError,'wall-clock'):
            self.allocate()

    def test_round_subdirectory_keeps_ledger_ownership(self):
        directory=self.root/'new_round';directory.mkdir()
        self.path=directory/'campaign.json';self.save()
        self.ledger=directory/'session_ledger.jsonl'
        check_campaign(self.path,self.ledger)
        with self.assertRaises(ValueError):
            check_campaign(self.path,self.root/'session_ledger.jsonl')

    def test_invalid_limits_still_rejected(self):
        for value in [True,0,-1,301,'unlimited',1.5]:
            self.campaign['max_sessions']=value;self.save()
            with self.subTest(value=value),self.assertRaises(ValueError):
                check_campaign(self.path,self.ledger)

    def test_directory_is_not_completion(self):
        run=self.root/'run'
        self.assertEqual(existing_state(run),'not_started')
        run.mkdir()
        self.assertEqual(existing_state(run),'incomplete_preparation')
        (run/'run.json').write_text(json.dumps({'status':'running','controller_pid':os.getpid()}))
        self.assertEqual(existing_state(run),'active')
        (run/'run.json').write_text(json.dumps({'status':'completed','verification_status':'passed'}))
        self.assertEqual(existing_state(run),'missing_assets')

    def test_only_one_explicit_infrastructure_retry(self):
        run=self.root/'failed';run.mkdir()
        (run/'run.json').write_text(json.dumps({'status':'environment_error','attempt':1}))
        approval=self.root/'repair.json'
        approval.write_text(json.dumps({'previous_run':str(run),'classification':'infrastructure_failure','evidence':'copy_errors.txt'}))
        self.assertEqual(validate_retry(self.root/'retry',approval,self.campaign)[0],2)
        for status,attempt in [('invalid_output',1),('completed',1),('environment_error',2)]:
            (run/'run.json').write_text(json.dumps({'status':status,'attempt':attempt}))
            with self.assertRaises(ValueError):
                validate_retry(self.root/'retry',approval,self.campaign)

    def test_same_failure_cannot_receive_multiple_replacements(self):
        metadata={'purpose':'development','run_id':'retry','controller_label':'fixture',
                  'allocated_at':'now','model':'gpt-5.6-sol','effort':'medium',
                  'role':'blind','attempt':2,'previous_run':str(self.root/'failed')}
        allocate(self.path,self.ledger,self.root/'retry',metadata)
        with self.assertRaises(RuntimeError):
            allocate(self.path,self.ledger,self.root/'other_retry',metadata)


if __name__=='__main__':
    unittest.main()


class RetrievalPolicyTests(unittest.TestCase):
    def test_historical_and_nonblind_inputs_unchanged(self):
        from run import retrieval_policy
        self.assertEqual(retrieval_policy({'protocol_version':'ten-task-v1'},Path('.'),'blind'),'')
        self.assertEqual(retrieval_policy({'protocol_version':'ten-task-v2-bounded-retrieval'},Path('.'),'audit'),'')

    def test_new_protocol_missing_empty_or_valid_policy(self):
        from run import retrieval_policy
        campaign={'protocol_version':'ten-task-v2-bounded-retrieval'}
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)
            with self.assertRaises(ValueError): retrieval_policy(campaign,base,'blind')
            campaign['protocol_assets']={'retrieval_policy_path':'policy.md'}
            (base/'policy.md').write_text('')
            with self.assertRaises(ValueError): retrieval_policy(campaign,base,'blind')
            (base/'policy.md').write_text('Fixed retrieval restrictions')
            self.assertEqual(retrieval_policy(campaign,base,'blind'),'Fixed retrieval restrictions')
