Verdict: pass for the preserved 9 September 2026 catalogue state.

I inspected d0119/reference.py and d0117/independent_check.py and their preserved executed results, d0174 and d0175. I additionally executed a separate JavaScript reconstruction directly over the preserved Atom/XML and HTML sources; I did not merely rerun their classifications or claim to execute the supplied Python here. The reconstruction checked identifiers, first-submission dates, category membership, duplicate consistency, comment-frontier equality, withdrawal flags, direct targets, maximum eligible timestamps, historical titles, and the final oracle diff.

Across all 20 complete Atom pages d0025–d0044, the independently executed checks returned 26,533 unique records, 97 duplicate occurrences with no conflicting metadata, no out-of-year or missing-cs.LG records, and no discrepancy against the official full-year total. Page entries total 26,630. The complementary date partitions and boundary response close the partial full-year pagination. In d0044, entry 2111.00629 has published=2021-10-31T23:59:29Z and categories cs.MM/cs.CV/cs.IR/cs.LG. Thus both the recovered month-end record and crosslists are included; identifier-month prefixes were not substituted for first-submission times.

I read every one of d0109's 705 comments/classifications and matched each comment to its cohort entry. Independent semantic review agrees with 23 direct withdrawn relationships and 682 exclusions: 577 overlap/derivative notices without the required designation, 83 reference/proceedings/incoming-derivative cases, 21 latest-version-active cases, and one withdrawn prior-method citation. These labels were comparison targets, not proof.

The 21 active cases were checked against raw latest submission-history entries in d0006, d0015–d0016, d0022, d0055, d0058–d0059, d0063, and d0090–d0102. For example, 2110.08884/d0015 explicitly names a replacement but its latest v2 is not withdrawn. The reciprocal merger comment in active 2101.12365/d0016 does not create the reverse relationship. In withdrawn 2101.02966/d0050, 2011.10115 identifies the prior Fit-DNN method; the withdrawal explains discovery of a more efficient existing algorithm. It does not designate that arXiv record as this work's replacement.

All 75 additional comments in d0176 were read and independently matched to cohort comments. Continual/Emerging wording includes ordinary false matches. Other cases describe within-record revisions, withdrawal without a named replacement, future intentions, or incoming relationships. Examples: 2106.07989 explicitly has no replacement; 2108.11976 identifies no distinct replacement record; 2109.14200 describes replacing a PsyArXiv preprint, not an outgoing withdrawn-record relationship. Corrected archive-prefix/old-style-ID scanning of the full cohort found no old-style targets. These checks supply closure beyond the numeric-ID frontier.

Each of the 23 remaining relationships has one directly designated distinct target, an actually withdrawn latest predecessor version, and a unique latest replacement submission at or before the cutoff. d0088 supplies 22 distinct selected-version Atom records for those 23 relationships; two predecessors share one target/version. Historical Atom updated timestamps agree with the selected HTML-history timestamps. Eight title differences are substantive wording changes, not whitespace or equivalent mathematics.

The reproduced answer and field-level source locators are below. P identifies the predecessor HTML: citation identifier, Comments, and Submission history. R identifies the replacement HTML: Submission history and current Title. H is the matching entry/id, updated, and title in d0088.

| Predecessor | Replacement | Version | P | R | H |
|---|---|---|---|---|---|
|2102.13653|1809.04564|v1|d0053|d0073|d0088#1809.04564v1|
|2103.00222|2011.10443|v1|d0067|d0074|d0088#2011.10443v1|
|2103.06490|1911.00234|v3|d0049|d0076|d0088#1911.00234v3|
|2104.13818|1908.06077|v1|d0057|d0078|d0088#1908.06077v1|
|2106.14997|2101.12365|v6|d0014|d0016|d0088#2101.12365v6|
|2107.01273|2011.09052|v1|d0061|d0081|d0088#2011.09052v1|
|2108.08647|2005.01026|v2|d0069|d0082|d0088#2005.01026v2|
|2111.03536|2103.07364|v1|d0064|d0084|d0088#2103.07364v1|

The title changes respectively concern stability/convergence versus generalization; gradient regularisation versus Variational Laplace; adding machine translation; improved versus provably efficient communication; dictionaries versus sharp neural-network bounds; changed visual-forecasting wording; adding the clients-clustering subtitle; and a unified game-theoretic interpretation. All 24 output fields match d0118 exactly.

The other 15 direct relationships were excluded after selected/current title equality checks: predecessors 2102.07344, 2102.07684, 2102.12736, 2103.03102, 2103.13342, 2103.16938, 2106.01072, 2106.02249, 2106.08943, 2107.10443, 2109.02344, 2109.03890, 2110.13400, 2112.06410, and 2112.13121. Their source mappings and independently agreeing comparisons are individually located in d0174/r01 and d0175/comparisons, backed by d0088 and the corresponding raw HTML histories. Later replacement chains were not followed. For 2109.03890/d0070, latest withdrawn v7 governs despite earlier withdrawn v5 and intervening v6.

Critical boundary: raw d0014 marks predecessor v2 withdrawn at 2021-09-08 22:12:13 UTC. Raw d0016 lists replacement v6 at 2021-06-28 21:54:22 and v7 at 2021-09-08 22:16:05. Independent timestamp subtraction gives +232 seconds for v7, requiring v6. Separately, d0061/d0081 place 2011.09052v2 710 seconds after its cutoff, requiring v1.

All six final answers were independently rescored against this reconstruction: r-arxiv-title-r02-cg-dev-a-repair (d0127/d0132), r-arxiv-title-r02-cg-dev-b (d0135/d0140), r-arxiv-title-r02-cg-attack (d0143/d0148), r-arxiv-title-r02-go-dev-a (d0151/d0156), r-arxiv-title-r02-go-dev-b (d0159/d0164), and r-arxiv-title-r02-go-attack (d0167/d0172). Their submitted rows are all correct; deficits are omitted rows. The accompanying error reviews establish which omissions have independent causal evidence.
