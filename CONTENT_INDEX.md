# Content index

This repository is a curated export of the construction pipeline. It keeps the
substantive benchmark assets and review history without publishing raw session
captures or repetitive execution debris. See `UPLOAD_SCOPE.md` for the exact
boundary.

## Pipeline

The root `scripts/`, `docs/`, `prompts/`, `schemas/`, `smoke_test/`,
`stage_registry.json`, and configuration examples contain the complete reusable
pipeline. Phase-specific runtime and protocol material remains under
`ten_task_phase/` and `wqp_single/`.

## Formal task set

The retained formal set consists of the 31-task retest corpus, including the
service-interrupted BALF task, plus the final WQP panel task:

- `arxiv_assumption_scope_001` r03
- `arxiv_historical_title_001` r02
- `arxiv_historical_title_002` r03
- `cfpb_app_issuer_version_001` r01
- `chembl_stereochemical_peers_001` r02
- `comptox_012` r00
- `device_recall_backlink_001` r01
- `diazepam_receptor_identity_001` r01
- `economic_kegg_ddi_001` r02
- `economic_nvd_daily_001` r02
- `epmc_quantitative_001` r02
- `europemc_balf_provenance_001` r01
- `europemc_declared_patent_001` r01
- `europemc_republication_title_001` r01
- `europemc_reuse_deposit_001` r01
- `genome_002` r00
- `iana_dtls_001` r04
- `kegg_initial_cdx_001` r02
- `kegg_module_products_001` r01
- `kegg_prodrug_identity_001` r01
- `nvd_configuration_environment_001` r01
- `nvd_initial_assessment_001` r01
- `nvd_repository_publication_001` r01
- `optimization_guarantee_001` r02
- `reptile_001` r00
- `reptile_type_referral_001` r01
- `scotus_joinder_001` r01
- `stap_replication_protocol_001` r01
- `wateroffice_002` r00
- `waterquality_003` r00
- `wqp_censored_screening_001` r02
- `wqp_activity_panel_001` r03

Each retained task directory includes the available final prompt/specification,
oracle, rules, reference computation, evidence index, and review result. The
formal 31-task retest summaries are in
`ten_task_phase/rolling_five/retest_31_v2/`; the WQP formal retest summary is in
`wqp_single/sol_medium_retest/`.

## Additional final construction sets

- Twelve repaired tasks: `ten_task_phase/revised12_20260917/candidates/`
- Current targeted-repair conclusions:
  `ten_task_phase/revised12_20260917/targeted_repairs_20260917/current_20260919/`
- New construction tasks: A/v3, B/v2, C/v1, D/v1, and E/v1 under
  `ten_task_phase/new_two_20260919/`

## Representative failures

Only three run-level cases are retained, each stripped of event streams,
stderr, copied implementations, CLI dumps, and repeated inputs:

- incomplete-scope case: `arxiv_historical_title_001-r02-cg-v2-once`
- zero-score case: `economic_nvd_daily_001-r02-go-v2-once`
- unscored case: `wqp_censored_screening_001-r02-go-v2-once`

All other historical executions are represented by phase reports, score tables,
review summaries, and issue indexes rather than duplicated run directories.
