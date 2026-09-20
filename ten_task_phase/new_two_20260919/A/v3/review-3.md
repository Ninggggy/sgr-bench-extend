# Review of targeted A v3 repairs

Verdict: **needs_revision**. The principal scoring repairs are visible and internally consistent, but two validity edge cases remain. The current inline package also omits the artifacts needed for independent source and recomputation review. This review uses static inspection only; it does not claim fixture execution, fresh browser retrieval, or model trials. Prior review labels are neither proof nor testing authorization. Difficulty remains unassessed.

## Scoring integration and fixtures

score_answer.py now explicitly imports ROOT/runtime_score_for_review.py. This resolves the visible dependency-path mismatch. Five-field weighting, key gating, duplicate handling, extra-column penalties, and order-independent Item-F1 remain unchanged. Blank offset cells remain distinct from empty offset sets, and the listed identity aliases are explicit; Portugal is not silently converted to Lisbon.

The wrapper now makes strictly_below_70 null for empty and parse-failure statuses. Its separate semantic_table_correct and whole_answer_correct flags correctly distinguish table content from sorting and ordinary ignored prose. With all eight rows correct, checking all 28 gold-order pairs establishes the required order. Extra, missing, duplicate, wrong-width, and incorrectly split rows prevent full correctness.

The fixture program contains 20 cases, matching scorer_fixtures.json. The visible counts and fractions are consistent with the code. The exact-threshold fixture has 28 correct fields and denominator 80, so 56/80 is exactly 70% and correctly fails the strict-below comparison. Seven fixtures call the wrapper directly, covering four empty/header cases and three whole-answer cases. These are supplied execution claims, not reviewer rerun results.

Two corrections remain:

1. **Require substantive content independently of parsed status.** The input `||||||` becomes five empty cells, has parsed status, and yields strictly_below_70=true with fraction 0/45. A syntactically detected row is insufficient to establish the substantive-table eligibility promised in rules.json. Add an explicit gold-independent eligibility predicate that rejects all-empty/delimiter-only tables while preserving scoring for substantive but incorrect answers. Use it in the threshold flag and test it through run.

2. **Do not discard arbitrary backtick-prefixed prose.** parse skips every line beginning with three backticks. The exact oracle plus a line such as ` ``` This answer is correct because ...` remains whole-answer correct. Track supported code-fence syntax explicitly and record other content as ignored prose or an issue. Add a wrapper fixture for this bypass. The ordinary Explanation fixture covers only the non-fence path.

The reported offset-field accuracies correctly supplement the unchanged weighting. As before, getting keys, endpoints, and old sets right while getting every new set wrong produces 64/80 Item-F1. This is a metric property, not a prediction of solver performance. A threshold result still requires the separately documented trajectory/access/exposure review.

## Pairing, identities, and reference consistency

CG and GO have identical scope, historical versions, date window, inverse-set semantics, and output requirements. CG adds only a suggested method. A shared oracle is consistent with this pairing.

The prompts clearly select PT membership in 2024b zone1970.tab, rather than timezone-name prefixes or former Portuguese possessions. They resolve historical uncertainty by asking for the published database assumptions. They also explicitly exclude abbreviation-only and DST-flag-only changes and require all fold candidates and genuine empty sets. No substantive ambiguity is apparent in those requirements.

Conditioned on the transition sequence narrated in reference.md, mapping constant-offset UTC spans into local coordinates reproduces the eight oracle intervals, including both March 1992 differences, the September fold and winter difference, the December gap, and the March/June 1993 differences. The adjacent listed intervals have distinct pairs of offset sets. No oracle correction follows from this conditional calculation.

However, the actual zone1970.tab, active europe records, and referenced rules are absent from this input. The assertion that the complete scope is Europe/Lisbon, Atlantic/Madeira, and Atlantic/Azores, and that Lisbon and Madeira each agree across releases, cannot be independently source-verified here. review-2.md supplies assertions and line references, not the underlying evidence. Retain the oracle provisionally rather than describing those claims as independently verified by this review.

## Recomputation and verification evidence

recompute.py and derived.json are not supplied. Neither are the boundary verification script nor its log. The described algorithm—map UTC spans, overlay local-image endpoints, compare inverse offset sets, and merge equal adjacent pairs—is appropriate, but its implementation, clipping, transition coverage, sorting, and independence from the oracle cannot be inspected here.

The revised claim is correctly phrased as 162 total probes using per-release partitions. The earlier review's reported components sum to 162, but the missing script and log prevent independent confirmation. Such probes can corroborate an inversion implementation; completeness comes from the exhaustive interval partition and source coverage, not the probe count. Shared compilation or boundary discovery also limits the independence of a ZoneInfo cross-check.

Provide the referenced source, acquisition, recomputation, derived-output, and verification artifacts. Their omission is an evidence gap, not a demonstrated execution or access failure. This review does not require adding hashes merely to compensate for absent files.

## Browser evidence, retrieval dependencies, and shortcuts

reference.md now expressly limits browser evidence to constructor captures and disclaims independent reviewer reproduction. That is appropriately narrower. The captures themselves are absent here, so even their contents cannot be inspected in this review. A reported IANA download-navigation block concerns one access path; it does not by itself establish missing source data or task infeasibility. Ordinary webfetch and browser-plugin access must remain separately attributed.

The reasoning dependencies are country membership, active release-specific states, referenced rule semantics, time suffix conversion, total offsets, and inversion. They do not establish a requirement for many sequential retrieval calls: known pinned source documents can be retrieved together. Tagged diffs, direct source retrieval, local search, manual derivation, and permitted compilation remain legitimate shortcuts. No exhaustive absence of a precomputed answer is established or needed for this quality review.

The visible repairs improve auditability and scoring validity. They do not demonstrate difficulty. Address the two concrete validity cases and supply the missing evidence before issuing an independent full-quality pass. No blind trials are authorized or recommended by this verdict.
