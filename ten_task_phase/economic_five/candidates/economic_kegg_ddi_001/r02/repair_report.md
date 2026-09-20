# Bounded integration repair: economic_kegg_ddi_001 r01

Status: UNTESTED. Corrected files are delivered as text for controller materialization. This repair did not write workspace files or execute the reference program, scorer, network requests, blind solvers, or other model sessions.

## Evidence and changes

The supplied `reference/execution_failure_01.json` records `python3 reference/solve_reference.py --root . --out reference/replay-01`, exit code 1, and `Unexpected DDI identity`. Its 28 listed rows contain legitimate chemical endpoints; examples are `d0055` lines 1–3 and `d0117` lines 1–10. This is supplied controller evidence, not a new execution or source observation.

The reference parser now validates exact `dr:D[0-9]{5}` and `cpd:C[0-9]{5}` identities. It converts drug endpoints to membership D keys and retains chemical endpoints with their `cpd:` namespace. Every valid singleton row survives parsing. Actual group membership determines selection. Invalid identities, malformed widths, and unknown or duplicate class tokens still fail; CSV parsing is strict. Initial and repeated batch parsing explicitly require drug endpoints, and both retain actual-member containment checks.

The reference still obtains its comparison result from singleton sources for every member of BOTH groups. It does not replace that path with SSRI-only coverage or fill its result from batch pairs. Added assertions reject reused batch/singleton file IDs or resolved paths. These assertions establish distinct saved inputs, not independent collection times. Complete parsed singleton rows are additionally written to `normalized_singleton_ddi.csv`; chemical and outside-member row counts are computed at runtime. The original delivered oracle is now required and compared before creating output. No oracle content is supplied or changed here.

`rules.json` uses only existing string fields, aliases, and uppercase options. Alias lookup precedes uppercase in the supplied scorer, so the class aliases explicitly cover both orders, all letter cases, and comma-adjacent spaces for exactly one CI and one P token. Existing `clean()` handles surrounding and repeated whitespace. No alias deletes extra or repeated labels. Prediction D IDs use uppercase only; optional prediction `dr:` wrapper stripping is not configured. The public format already requires bare D IDs. Source wrapper handling remains in the reference parser.

`score.py` remains unchanged. Predictions go directly to its parser in their original order. There is no prediction deduplication, orientation inference, row reordering, class merging, or best-duplicate selection. Only the first occurrence of an ordered normalized key is eligible for credit. Every duplicate remains in the denominator with zero field credit. Unmatched, reversed, missing, and malformed rows retain the existing protocol. Item-F1 remains `2 * correct_fields / (gold_fields + pred_fields)` using the existing counts.

Both public variants now require a table-only answer and place provenance and limitations in the solver schema's separate evidence field. This removes the source-note collision with the existing parser's comma-bearing prose handling after a header. No answer columns were added. Their shared scope and output conditions are quoted verbatim in `pair_alignment.json`; CG alone includes the three procedural steps. The wording removes redundant treatment-advice and internal evaluation prose while preserving the clinical meaning of absence, access/conflict limitations, and all domain conditions.

The campaign is exactly `2026-09-11T16:26:15.871Z` inclusive through `2026-09-13T16:26:15.871Z` exclusive: 48 hours. No budget extension or September 9 historical observation is asserted. The input runtime `current_date` remains `2026-09-09`. The supplied construction observation date is retained as metadata, not represented as a new observation by this repair.

## Validation status and controller actions

Actual shell commands executed in this repair: none. Review was by inspection of the supplied code, failure record, and returned text. No Python syntax check, saved-data replay, scorer test, or campaign stability check was executed. No successful count, oracle equality, or score is claimed.

After preserving the previous files, raw builder output, delivered oracle, and failed run, the controller should materialize these files and run the following command only if its output directory is unused:

```text
python3 reference/solve_reference.py --root . --out reference/replay-02
```

The rerun must complete the BOTH-singleton equality check, SQL comparison, HTML membership check, repeated-source comparisons, boundary slices, original counterfactuals, ledger uniqueness, valid output classes, and exact delivered-oracle comparison. The repaired program retains these gates. Its runtime chemical-row count can be checked against the 28 rows listed in the supplied failure record; this repair has not independently recounted the raw responses.

The controller must also test the original scorer with these rules: canonical rows; lowercase IDs; CI/P order, case, and spacing variants; identical and conflicting duplicate keys; wrong-first/correct-later duplicates; reversed pairs; missing rows; malformed widths; and extra or repeated class labels. These are pending checks, not reported test results. Evidence must be passed separately and only the answer field scored.

Existing limitation: the supplied parser returns `parse_failure` for a header followed only by `NONE`, and scorer main requires parsed gold. The shared public NONE rule is preserved, without modifying the scorer or disguising NONE as a prediction row. An actually empty oracle would need separate protocol adjudication. No empty oracle or revised scope is asserted here.

## Repair accounting

Charge this bounded integration delivery as one substantive pretest repair toward the at-most-two limit, including its parser, scorer configuration, and paired-output corrections. Prior cumulative accounting was not supplied, so no remaining repair allowance is asserted. Preserve the old public variants and raw builder output; these returned variants remain UNTESTED and inherit no execution results. No further construction or difficulty adjustment is proposed.
