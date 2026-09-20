The constructor rebuilt the intended one-row answer from actual public sources observed on 12 September 2026. This report does not claim that reference.py was executed or that an independent audit passed.

Actual source operations used the official Europe PMC REST endpoints recorded in source_manifest.json. The annual GET returned HTTP 200, hitCount 360 and 360 rows. A complete JSON-to-table conversion retained those 360 rows. The actual read-only query was `SELECT * FROM a WHERE journalVolume='276' AND issue='2' ORDER BY source,id`, with all 47 rows returned and no truncation. Every returned title and publication type was inspected. Two records have both a correction title and correction/erratum types. Their complete bodies resolve one quantitative positive and one author-only exclusion. The complete issue identities are in sources/issue_membership.psv; the controller-preserved raw annual payload supplies the full annual list.

The constructor made only four fresh GETs: annual metadata and PMC12953317, PMC12953309 and PMC12953261 fullTextXML. All returned HTTP 200. It did not refetch the prior 24-paper batch. Existing batch recovery and coverage are accepted as the controller-supplied actual observation, not as a new constructor execution.

Identity is verified by three agreeing paths: the correction's original DOI, the annual DOI-to-PMCID row, and the correction's direct corrected-article PMCID link. The original XML contains the same DOI and prefixed PMCID. XML pub-id-type='pmcid' is used; the separate numeric PMCAID namespace is ignored.

The notice's revised help count is 271; its quoted old 109 belongs to the erroneously substituted admissions event. Revised 491 is the non-depressed group according to the corrected table and the original's SCID-5 Results definition. The original Methods paragraph explicitly reports 581 analyzed out of initially 730, including 18 dropouts. It states that the analysis uses a baseline cross-section and includes people who completed baseline SCID-5 and returned the assessment questionnaires.

Constructor JavaScript was actually executed over normalized text returned by the source-reading tools. It extracted 581, 730 and 18 from the original inclusion sentence, 271/109 and 491/481 from the notice, and 491/90 from the corrected table headers. It calculated 491+90=581 and confirmed agreement with the directly reported analyzed total. It calculated the wrong-scope delta 730-581=149, the wrong-event delta 109-271=-162, and the superseded-group delta 481-491=-10. The complete notice text did not contain the initial-cohort anchor or the completed-baseline-assessment inclusion anchor; the original did contain the latter and the questionnaire-return requirement. These actual constructor results are saved in reference/counterfactuals.json.

A second source path is visible in original Results Par32: help 271 and diagnostic groups 90/491 agree with the notice and its table. The initial total itself has one decisive original paragraph; no independent enrollment dataset is claimed. The corrected table group sum is a distinct arithmetic check on analyzed_n, after verifying compatible group definitions. No percentage is used to infer an exact count.

Boundary recheck used the separate author-only notice body, including its closing update paragraph, and separate original Results text rather than rereading only a generated table. The original's broader prospective design label was checked against its explicit current-analysis cross-section. The notice's current change-history text was observed, but no historical raw article response was retrieved. Old values are attributed only to the current notice's statements.

The offline program discovers source files through registry URL/path records, derives the whole issue and candidate set from annual metadata, validates the saved issue inventory, processes every notice, derives the original identity from source content, and parses numerical and semantic anchors. It writes complete annual and issue exports, metadata screening, candidate universe, a true/false/unknown ledger, normalized studies, field evidence, the oracle, counterfactuals, a type-versus-title candidate-set comparison and an execution report. Unknown classifications and identity/source conflicts fail visibly. It does not silently keep a supplied gold row. The provisional oracle is an optional comparison input, not a data source for reconstruction.

Controller command to execute after copying the preserved registry and payloads into sources:

```text
python3 reference.py --source-dir sources --out-dir rebuilt --expected-oracle oracle.psv
```

Execution status of that command: NOT EXECUTED BY CONSTRUCTOR. No exit code or Python result is asserted. Expected checks are 360 annual records, 47 issue records, 24 issue PMCIDs, two notices, one output row, source-anchor agreement and equality to the provisional oracle. Actual results must come from rebuilt/execution_report.json.

For a later independently saved live observation, the controller can execute:

```text
python3 reference.py --source-dir sources --out-dir stability_rebuild --expected-oracle oracle.psv --compare-source-dir later_sources
```

This compares complete annual membership fields, complete issue membership and all three required XMLs. It performs no network request and never substitutes a later response for the construction snapshot. A difference requires review before reusing the oracle. Raw annual responses and exports must be retained for the full stability check; winner-only checks are insufficient.

Full candidate.schema.json validation and cross-file pair validation remain pending controller execution. The missing distinct legacy task prevents the requested hardest-old-task comparison. No blind model run, score, human review or independent final audit is claimed. The constructor recommends continuing this small slice without broadening it.
