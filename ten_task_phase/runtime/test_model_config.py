"""Offline checks for model selection and saved runtime evidence. No API/Docker."""
import copy
import json
import tempfile
import tomllib
import unittest
from pathlib import Path

from model_config import render_config, select_model, tool_profile_config
from verify_run import invocation_model, verify, verify_model_evidence

TEMPLATE = '''# Keep runtime and authentication settings intact.
model = "gpt-6-astra"
model_provider = "openai"
model_reasoning_effort = "high"
web_search = "live"
approval_policy = "never"
sandbox_mode = "read-only"
[features]
shell_tool = false
apps = false
[mcp_servers.wqp_data]
command = "python3"
args = ["/opt/wqp/data_tools.py"]
[model_providers.openai]
requires_openai_auth = true
'''


def recorded(model='gpt-5.6-sol', effort='medium'):
    return ({'model':model,'effort':effort,'provider':'openai','role':'audit' if model == 'gpt-6-astra' else 'blind'},
            ['docker','exec','-i','fixture','codex','exec','--strict-config',
             '--model',model,'-c','model_reasoning_effort='+json.dumps(effort),'-'],
            render_config(TEMPLATE,model,effort),
            [{'model':model,'effort':effort}])


class ModelSelectionTests(unittest.TestCase):
    def test_web_only_removes_mcp_and_keeps_provider_sandbox(self):
        original=tomllib.loads(TEMPLATE)
        result=tomllib.loads(tool_profile_config(TEMPLATE,'blind','web_only'))
        self.assertEqual(result,{k:v for k,v in original.items() if k!='mcp_servers'})
        self.assertEqual(tool_profile_config(TEMPLATE,'audit','web_only'),TEMPLATE)
        self.assertEqual(tool_profile_config(TEMPLATE,'blind'),TEMPLATE)
        with self.assertRaises(ValueError):
            tool_profile_config(TEMPLATE,'blind','unrestricted')

    def test_blind_defaults(self):
        self.assertEqual(select_model(),('gpt-5.6-sol','medium'))

    def test_explicit_historical_request(self):
        self.assertEqual(select_model('gpt-6-astra','high'),('gpt-6-astra','high'))

    def test_private_audit_uses_authorized_medium(self):
        self.assertEqual(select_model(audit=True),('gpt-6-astra','medium'))
        with self.assertRaises(ValueError):
            select_model('gpt-5.6-sol','medium',audit=True)
        self.assertEqual(select_model('gpt-6-astra','high',audit=True),('gpt-6-astra','high'))
        with self.assertRaises(ValueError):
            select_model('gpt-6-astra','low',audit=True)

    def test_invalid_options_rejected(self):
        for model,effort in [('', 'medium'),('model\n', 'medium'),('gpt-5.6-sol','invalid')]:
            with self.subTest(model=model,effort=effort),self.assertRaises(ValueError):
                select_model(model,effort)

    def test_config_preserves_every_other_setting(self):
        rendered=render_config(TEMPLATE,*select_model())
        original=tomllib.loads(TEMPLATE)
        self.assertEqual(tomllib.loads(rendered),{
            **original,'model':'gpt-5.6-sol','model_reasoning_effort':'medium'})
        # Also preserve all unrelated text, including nested tables and comments.
        self.assertEqual(rendered,TEMPLATE.replace('model = "gpt-6-astra"','model = "gpt-5.6-sol"').replace('model_reasoning_effort = "high"','model_reasoning_effort = "medium"'))
        self.assertEqual(tomllib.loads(TEMPLATE)['model'],'gpt-6-astra')

    def test_invalid_config_is_not_silently_rewritten(self):
        with self.assertRaises(ValueError):
            render_config('[nested]\nmodel="gpt-6-astra"\nmodel_reasoning_effort="high"\n',*select_model())


class RuntimeEvidenceTests(unittest.TestCase):
    def test_web_only_actual_config_and_forbidden_tools(self):
        meta,inv,_,turns=recorded()
        meta['tool_profile']='web_only'
        config=render_config(tool_profile_config((Path(__file__).parent/'solver.config.toml').read_text(),'blind','web_only'),meta['model'],meta['effort'])
        meta['provider']=tomllib.loads(config)['model_provider']
        verify_model_evidence(meta,inv,config,turns)
        bad_configs=[config+'\n[mcp_servers.accidental]\ncommand="python3"\n']
        for feature in ('shell_tool','unified_exec','apps','multi_agent'):
            bad=config.replace(feature+' = false',feature+' = true')
            self.assertNotEqual(bad,config)
            bad_configs.append(bad)
        for bad in bad_configs:
            with self.subTest(config=bad),self.assertRaises(ValueError):
                verify_model_evidence(meta,inv,bad,turns)

    def test_new_and_historical_evidence_accepted(self):
        for pair in [('gpt-5.6-sol','medium'),('gpt-6-astra','high'),('gpt-6-astra','medium')]:
            with self.subTest(pair=pair):
                checked=verify_model_evidence(*recorded(*pair))
                self.assertEqual((checked['model'],checked['effort']),pair)
                self.assertEqual(len(checked['model_evidence_sources']),4)

    def test_unapproved_role_effort_rejected_even_when_all_sources_agree(self):
        for pair in [('gpt-6-astra','low'), ('gpt-5.6-sol','high')]:
            with self.subTest(pair=pair), self.assertRaises(ValueError):
                verify_model_evidence(*recorded(*pair))

    def test_disagreement_in_any_source_is_rejected(self):
        for source in ('metadata','config','invocation','turn','second_turn','provider','actual_model','actual_effort'):
            meta,inv,config,turns=copy.deepcopy(recorded())
            if source=='metadata': meta['effort']='high'
            if source=='config': config=render_config(config,'gpt-6-astra','high')
            if source=='invocation': inv[inv.index('--model')+1]='gpt-6-astra'
            if source=='turn': turns[0]['effort']='high'
            if source=='second_turn': turns.append({'model':'gpt-6-astra','effort':'high'})
            if source=='provider': meta['provider']='different-provider'
            if source=='actual_model': meta['actual_model']='gpt-6-astra'
            if source=='actual_effort': meta['actual_effort']='high'
            with self.subTest(source=source),self.assertRaises(ValueError):
                verify_model_evidence(meta,inv,config,turns)

    def test_self_report_cannot_replace_actual_trace(self):
        meta,inv,config,_=recorded()
        meta['actual_model']='gpt-5.6-sol'
        meta['actual_effort']='medium'
        with self.assertRaises(ValueError):
            verify_model_evidence(meta,inv,config,[])

    def test_missing_or_ambiguous_argv_rejected(self):
        _,inv,_,_=recorded()
        for args in [inv+['--model','gpt-6-astra'],inv+['-c','model_reasoning_effort="high"'],['codex','exec','--model'],['codex','exec']]:
            with self.subTest(args=args),self.assertRaises(ValueError):
                invocation_model(args)

    def test_verification_keeps_the_run_scorer(self):
        # An archived scorer with intentionally distinctive semantics establishes
        # that verification does not substitute today's global score.py.
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for folder in ['implementation','public','sessions','solver_output','controller_scoring','scoring']:
                (root/folder).mkdir()
            def save(name,value): (root/name).write_text(json.dumps(value))
            meta,inv,config,turns=recorded()
            save('run.json',{**meta,'status':'completed'})
            save('invocation.json',inv)
            (root/'solver.config.toml').write_text(config)
            save('public/input.json',{'instruction':'fixture','output_format':'fixture','current_date':'2026-09-09'})
            save('isolation.json',{'bind_mounts':[],'read_only_rootfs':True,'probe':[{'readable':False}]})
            (root/'sessions/session.jsonl').write_text(json.dumps({'type':'turn_context','payload':turns[0]})+'\n')
            (root/'answer.txt').write_text('raw answer')
            save('solver_output/result.json',{'final_answer':'raw answer'})
            save('public/result.schema.json',{'type':'object'})
            save('controller_scoring/rules.json',{'columns':['fixture']})
            (root/'controller_scoring/oracle.psv').write_text('oracle')
            archived={'metrics':{'fixture_archived_metric':0.375},'field_differences':['fixture_difference']}
            (root/'implementation/score.py').write_text(
                'import json\n'
                'def parse(text,columns,record_separator=None): return {"status":"fixture_archived_parser"}\n'
                'def score(g,p,r): return '+repr(archived)+'\n'
                'def write(path,value): path.write_text(json.dumps(value))\n')
            save('scoring/scores.json',{'metrics':archived['metrics']})
            save('scoring/field_differences.json',archived['field_differences'])
            checked=verify(root)
            self.assertEqual(checked['metrics'],archived['metrics'])
            self.assertEqual(checked['parse_status'],'fixture_archived_parser')
            self.assertTrue(checked['scored'])


if __name__=='__main__':
    unittest.main()
