#!/usr/bin/env python3
"""Offline configuration check. No experiment allocation or external access."""
import json
import tomllib
from pathlib import Path
from model_config import render_config, tool_profile_config
from run import retrieval_policy
from campaign_runtime import check_campaign

BASE = Path(__file__).resolve().parent
CURRENT = BASE.parent / 'revised12_20260917/targeted_repairs_20260917/current_20260919'

def check(directory=CURRENT):
    directory = Path(directory)
    campaign = check_campaign(directory/'campaign.json', directory/'session_ledger.jsonl')
    assert campaign['candidate_ids'] == ['reptile_001', 'arxiv_historical_title_001']
    assert campaign['inherited_versions'] == {'waterquality_003': ['sanmarcos01']}
    assert campaign['reserve_first_review_and_pair'] is True
    assert campaign['blind_tool_profile'] == 'public_web'
    assert (campaign['blind_model'], campaign['blind_effort']) == ('gpt-5.6-sol', 'medium')
    assert (campaign['review_model'], campaign['review_effort']) == ('gpt-6-astra', 'medium')
    expected = render_config(tool_profile_config((BASE/'solver.config.toml').read_text(), 'blind', 'public_web'), 'gpt-5.6-sol', 'medium')
    assert tomllib.loads((directory/'solver.config.toml').read_text()) == tomllib.loads(expected)
    policy = retrieval_policy(campaign, directory, 'blind')
    assert 'ordinary webpage fetch/read' in policy and 'Do not directly query data APIs' in policy
    assert (directory / campaign['protocol_assets']['blind_prompt_path']).is_file()
    historical = directory / campaign['historical_usage_source']
    rows = [json.loads(line) for line in historical.read_text().splitlines() if line.strip()]
    actual = {role: sum(r.get('role') == role and bool(r.get('run_dir')) for r in rows) for role in ('blind', 'audit')}
    assert actual == {'blind': campaign['inherited_blind_sessions'], 'audit': campaign['inherited_review_sessions']}
    state = json.loads((directory/'state.json').read_text())
    assert state['construction_request_limit'] is None and state['blind_request_limit'] is None
    assert state['max_directions_per_task'] is None and state['external_request_concurrency_limit'] is None
    assert state['goal_completed'] is False
    assert set(state['versions_used']) == set(campaign['candidate_ids']) | set(campaign['paused_candidate_ids'])
    assert state['active_candidate_ids'] == campaign['candidate_ids']
    assert campaign['success_scope'] == campaign['candidate_ids']
    return {'offline_configuration': 'passed', 'inherited_sessions': actual,
            'new_sessions': len((directory/'session_ledger.jsonl').read_text().splitlines()),
            'data_mcp_exposed': False, 'ordinary_page_fetch': 'configured_native_web',
            'browser_plugin_in_isolated_runner': False, 'blind_browser_plugin_required': False,
            'live_runtime_verified': False,
            'retrieval_compliance': 'requires_per_trial_trace_review'}

if __name__ == '__main__':
    print(json.dumps(check(), ensure_ascii=False, indent=2))
