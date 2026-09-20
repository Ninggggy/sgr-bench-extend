import json, shutil
from pathlib import Path
P=Path(__file__).resolve().parent
def put(name,obj):
    (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
src=P.parent/'revised12_20260917/targeted_repairs_20260917/current_20260919'
# Only reusable protocol text is copied. No prior task or result is loaded.
for f in ['blind.md','audit.md','retrieval_policy.md']:
    shutil.copyfile(src/f,P/f)
put('campaign.json',dict(name='Two wholly new independent tasks, 2026-09-19',
    protocol_version='six-repairs-public-web-20260919',
    protocol_compatibility_note='Identifier selects the existing public_web runner and its existing pair checks; this is a separate campaign and ledger with zero inherited use.',
    started_at='2026-09-19T08:32:36+00:00',deadline=None,current_date='2026-09-19',
    max_sessions=27,max_blind_sessions=12,max_review_sessions=15,
    inherited_blind_sessions=0,inherited_review_sessions=0,
    maximum_concurrent_model_sessions=4,controller_concurrency_slots=1,
    max_seconds_per_session=6000,stall_seconds=3000,
    blind_model='gpt-5.6-sol',blind_effort='medium',blind_tool_profile='public_web',
    review_model='gpt-6-astra',review_effort='medium',
    reserve_first_review_and_pair=True,candidate_ids=['A','B'],max_versions_per_task=3,
    session_ledger='session_ledger.jsonl',protocol_assets={
        'blind_prompt_path':'blind.md','retrieval_policy_path':'retrieval_policy.md'}))
