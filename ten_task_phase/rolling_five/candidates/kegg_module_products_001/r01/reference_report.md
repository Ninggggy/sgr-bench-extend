The supplied primary records support the delivered two-row oracle. This is an annotation comparison: a compound omitted from a module line is not inferred to be absent biologically.

The full enzyme ALL_REAC includes R00024 and the other entry R03140. The complete direct link response identifies M00165, M00532, and M00968. These scopes come from [the enzyme response](../sources/enzyme.txt) and [the direct links](../sources/module_links.tsv), with transport provenance in [the controller manifest](../sources/controller_downloads.json).

The decisive module evidence is in [the complete module response](../sources/modules.txt):

| Reaction | Module | Explicit products in consuming direction | Decision |
|---|---|---|---|
| R00024 | M00165 | C00197 | Exclude: only one qualifying module |
| R03140 | M00532 | C00197, C00988 | Include: differing reaction group |
| R03140 | M00968 | C00197 | Include: all qualifying rows of that group |

R00024 has no matching REACTION line in M00532 or M00968. R03140 has none in M00165. Those absences create no pairs and no empty product sets. The module fields contain 34 logical reaction lines altogether; three match the root scope. The other 31 are outside ALL_REAC. The reference program preserves all those row-level scope decisions, all matching-line decisions, and all absent-pair decisions.

Each of the three matching lines uses -> with C01182 on the left only. Thus the consuming direction is explicit. The enzyme's naming direction does not control these module annotations. The optional [generic reaction response](../sources/reactions.txt) lists both products for R03140; copying that EQUATION into every module would erase the observed difference. Generic reaction records are audit context only.

Run from the package parent:

```sh
python3 r01/reference.py --source-dir sources --out-dir r01/generated
```

The program generates oracle.psv, inventory.json, inclusion_ledger.json, evidence_anchors.json, and execution_checks.json. It reads every 12-column flat-field line, tracks continuations, requires record terminators, verifies enzyme identity and exact module-body coverage against the full direct-link set, and inspects every module REACTION row. It derives products and grouping decisions without embedding the discovered answer IDs. Evidence anchors include exact source excerpts and physical line numbers computed from the input files.

The supported expression grammar covers the supplied explicit compound cases, optional positive numeric coefficients, comma-separated reaction IDs, and the publicly specified arrow forms. It does not solve arbitrary chemical expressions. Unrecognized or conflicting relevant annotations fail explicitly rather than becoming exclusions or NONE. An absent optional reactions.txt is allowed. If supplied, that file is parsed as context without contributing product IDs or imposing reaction-to-module scope agreement.

Structural checks establish terminated records and link/body coverage. The supplied controller capture metadata establishes transport provenance; a terminator alone cannot prove that an arbitrary replacement response has no internal omissions. Preserve the supplied full responses, rather than reconstructing shortened records from the evidence excerpts.

Execution status: NOT RUN by this constructor. The supplied deterministic scorer preflight passed for the supplied provisional answer and id_list rules; that is not execution of this reference.py and is not a solver-performance result. The delivered oracle is derived directly from the supplied primary lines. Controller comparison with regenerated output remains pending.

Runtime metadata remains 2026-09-09. The reference observation is 2026-09-12, not a claim about historical 9 September annotations. Pre/post-A source-field stability: not_performed; details are in source_manifest.json. Content validation: not_run. Difficulty testing: not_run. Independent final audit: not_performed. Human review: not_performed.
