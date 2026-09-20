Reference and paired construction: economic_kegg_ddi_001/r01

Decision: the current source reconstruction is complete and internally consistent. The stage remains needs_revision until the controller executes the supplied Python reference and completes its independent checks during actual evaluation. No historical September 9 oracle, permanent stability, clinical safety conclusion, model score or blind test is claimed.

Actual reference acquisition: 2026-09-11 18:27:48.594876 through 18:34:44.918128 UTC. The task window is September 11–13, 2026 UTC. The input's configuration date 2026-09-09 is retained privately and is not a source cutoff. DRUG info reports 2026/09/04 (d0090); DGROUP info reports 2026/08/25 (d0178). A DDI revision identifier was not supplied by the inspected sources and is recorded as unavailable. Those database dates and the API/checker documentation dates are not substituted for a DDI revision.

Sources and completeness:
- The complete response https://rest.kegg.jp/get/DG01659+DG01568 (d0041, 4,105 bytes) has two ENTRY records, both terminated by ///. Deterministic parsing of MEMBER only, excluding exact DG identifiers, yields 20 SSRI and 40 MAO leaves. All salts, hydrates, A/B/non-selective branches and the Isoniazid branch remain in scope.
- Independent official HTML responses d0088 and d0089 expose the same 20 and 40 leaf links within the Member section. Their .mem1{display:none;} CSS shows why the default presentation can hide nested leaves. This was inspected in actual HTML, not through a claimed click or screenshot.
- The derived 60-ID DDI request (exact URL in source_manifest.json) is 444 characters. It succeeded with a complete 46,680-byte body, d0044. No pagination is documented for these get/ddi operations. The DDI API section supports multiple entries but supplies no numeric DDI item or URL-length limit. The manual's 10-entry limits apply to get/list, not to DDI. The official API page specifies at most three calls per second; this run stayed below it. We do not infer an undocumented maximum.
- All 60 ingredient endpoint singleton requests also returned HTTP 200 and were fully saved: d0048–d0067 and d0095–d0134. Their 19,430 rows provide a second coverage path. No candidate was decided from a preview or search summary.

Observed computations:
1. tabulate(d0044, tsv, [drug1,drug2,class,mechanism]) produced d0045 with 1,072 rows. Exact member joins over complete CSV data yielded 592 directed cross-group rows, corresponding to 296 distinct ingredient pairs. There are 294 CI-only pairs, two CI,P pairs, and no P-only cross-group pairs.
2. The Cartesian member universe has 20 * 40 = 800 distinct keys. The ledger has 296 true, 504 false ('not reported in complete successful coverage'), and zero unknown entries. False never means clinically safe.
3. SQL joins and independent JavaScript parsing/set normalization produced exactly the same sorted 296 rows. Directed batch keys are unique, every reverse orientation has the same class set, and there are no conflicting duplicate keys (d0184, d0185). The PSV has exactly ssri_id, mao_id, classes; identifiers retain salt/hydrate identity. Names remain in the member universe for source review and are not added to scoring.
4. Critically, the SSRI-only singleton route produced 282 pairs, missing 14 CI pairs involving D03731 (d0091/d0092). This is a real source-scope discrepancy with the broad wording in the API manual. It was not silently treated as absence. Unioning singleton records from BOTH endpoints produced exactly the batch set and classes; both set differences were zero (d0175). All 19,430 singleton rows use their requested endpoint as drug1 (d0193).
5. Fresh small requests checked different boundaries: d0176 confirms D00326–D03731 CI; d0177 confirms both dual-class rows; d0179 confirms D02260–D00346 CI and D02260–D02362 P while omitting D02362–D00346. The optional direct request for the latter pair returned HTTP 404 (d0181). Its failure is recorded and is not used as zero; absence is established by successful full batch and both-endpoint coverage.
6. Fresh complete group response d0190 equals d0041. Fresh complete DDI response d0189/d0191 has zero differences from d0044/d0045, including mechanisms (d0192). This supports consistency during this construction interval only. It does not establish stability throughout later testing.

Actual counterfactuals (all changed rows are saved in reference/counterfactuals.json):
- Ignoring within-group exclusion increases 296 to 536 pairs: 85 SSRI P pairs plus 150 MAO CI pairs and five MAO P pairs are added (d0183/d0187). D02260–D02362 P is a directly re-fetched example.
- Treating Paroxetine D02362 as interchangeable with Paroxetine hydrochloride hemihydrate D02260 and inheriting the latter's records creates 36 false extra rows, increasing 296 to 332 (d0188). D02362–D00346 is a re-fetched boundary example; no missing interaction is clinically interpreted.
- Using the SSRI endpoint only loses 14 rows, reducing 296 to 282.
- Keeping only the 'worst' class changes two values from CI,P to CI. The source really reports both; neither the oracle nor the paired wording drops P.
These demonstrate identity, orientation and scope dependencies. No difficulty score, blind solve or model comparison was performed.

Reproducibility and execution status:
The actual tool calls, exact SQL arguments, table mappings and observed result IDs are in reference/execution_log.json. Full downloaded bodies are automatically saved registered assets; source_manifest.json maps every exact file ID to its URL, request/response UTC times, status, byte count and delivery destination. Sources remain unmodified. The read-only worker did not write to the filesystem.

The Python program reads those exported RAW group, HTML and DDI bodies, reconstructs members, normalizes records, verifies coverage with SQL, compares the fresh boundaries and repeats, emits normalized CSV tables and JSONL records, and regenerates the oracle and counterfactuals. It does not hardcode the answer rows or generate an oracle by printing an analyst-authored table. Its paroxetine counterfactual selects the two identities from the saved source names.

Required controller command, NOT RUN in this worker:
  python3 reference/solve_reference.py --root . --out reference/replay-01

The program requires a new output directory and compares its regenerated oracle with reference/oracle.psv. It also checks member termination, row-key uniqueness, deterministic order, allowed non-null output classes, full endpoint coverage, reverse-class agreement, independent SQL normalization and fresh boundary slices. The actual JavaScript/SQL checks above are not represented as Python execution. No shell/Python tool was available, and no other model or agent was run.

Paired wording:
cg.json and go.json each contain only instruction and output_format. Their substantive rules and output_format are exact shared text; only CG appends three short research steps. Pair alignment quotes each shared predicate and checks concrete alternative interpretations against observed row/value changes. Neither public instruction gives a website name, entry URL, group ID, member count, result ID or answer list. Exact D identifiers are required solely to disambiguate ingredient forms. The shared format handles CI,P, sorting, complete output, NONE, missing evidence and access/revision notes. This is first construction; there are no prior test scores to inherit.

Remaining issues:
- Controller must export the already-saved assets and execute the Python command; no execution result is invented.
- Controller must independently check complete answer-bearing membership, identity, class and absence boundaries during the actual campaign. The short construction repeat is not that audit.
- The relative language-example Markdown and any local stage schema/scorer source could not be opened because this worker has no filesystem reader. The supplied role rules and stage-result schema were used; semantic alignment was checked directly. Existing Item-F1 integration has not been executed.

Delivery:
The registered CSV delivery bundle contains the exact path/content of every authored artifact, including the complete 800-row ledger, 296-row field evidence and PSV oracle. It is a file container, not a plan or a manually truncated preview. Use the supplied materializer with an asset index exported by the controller. Its manifest also locates all original source bodies and SQL-derived check assets. The materializer and reference program are intentionally labeled unexecuted here.
