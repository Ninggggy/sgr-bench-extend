Verdict: pass for source-dependent historical retrieval; difficulty remains qualified.

The dependency is concrete: first-submission/category scope exposes predecessor comments; a qualifying outgoing designation supplies a replacement identifier; the actual withdrawn-version timestamp and replacement history select a version; that version's title determines membership. The output does not print titles, but inclusion still depends on them. d0014 → d0016 → d0088#2101.12365v6 is an explicit example: default/current replacement metadata cannot establish the historical-title difference.

Legal alternatives are available. The Atom API supports explicit versions in id_list and batched/paged retrieval. OAI-PMH supports bulk metadata harvesting; its date filters concern metadata modification, so first-submission scope requires subsequent filtering. Current OAI is available at oaipmh.arxiv.org/oai. See the [official API manual](https://info.arxiv.org/help/api/user-manual.html) and [OAI documentation](https://info.arxiv.org/help/oa/index.html). The [official bulk-data guide](https://info.arxiv.org/help/bulk_data.html) also identifies metadata datasets and PDF/source bulk access. These are permissible alternatives, not disallowed shortcuts.

Directly parsed d0103, the preserved current arXivRaw GetRecord for 2101.12365, has ten version elements containing date/size but only one current title. It is successful evidence against treating version-history metadata as a historical-title table, not evidence that OAI is inaccessible. d0089's schema is consistent with that observed structure.

Current metadata/history can eliminate ten of the 23 relationships because their selected version is current. Thirteen have an earlier selected version; only eight changed title. Thus treating every earlier version as a changed title produces five false positives: 2103.13342, 2106.02249, 2106.08943, 2110.13400, and 2109.02344. Independent source comparisons also show that predecessor-current titles are not valid substitutes for the selected replacement title. A bulk collection containing actual historical titles could batch the work, but would still supply the version-specific evidence; no inspected current/full-metadata source supplies an answer table that removes this dependency. This is not a universal claim about every possible external snapshot collection.

Complete navigation was reviewed for every run, with decisive actual responses inspected in the corresponding full traces. Event numbers below are full-trace ordinals; run-local download IDs must not be confused with this audit's global file IDs.

| Run ID | Navigation / trace | Item-F1 = Row-F1 | Historical-evidence locator |
|---|---|---:|---|
|r-arxiv-title-r02-cg-dev-a-repair|d0133 / d0132|0.5454545|request 278, response 281: selected version pages including 2101.12365v6|
|r-arxiv-title-r02-cg-dev-b|d0141 / d0140|0.8571429|405→425: actual selected/current title comparisons|
|r-arxiv-title-r02-cg-attack|d0149 / d0148|0.9333333|384–399: historical downloads; 404→422: 16 extracted historical titles|
|r-arxiv-title-r02-go-dev-a|d0157 / d0156|0.4000000|275→278 and 282→285: historical titles, including 1911.00234v3 and 2005.01026v2|
|r-arxiv-title-r02-go-dev-b|d0165 / d0164|0.6666667|277→280: six historical responses including 2101.12365v6|
|r-arxiv-title-r02-go-attack|d0173 / d0172|0.4000000|207→210 and 214→217: 2103.07364v1 and 2101.12365v6|

Scores d0128/d0136/d0144/d0152/d0160/d0168 agree with independent rescoring; P.O.A.=1 throughout. The 0.9333 CG attack is a high result and materially weakens any claim of uniformly strong difficulty. It does not bypass SGR: its actual successful historical downloads and extracted titles are visible. Ordinary CG B is also strong. GO's lower scores do not compensate for or erase those results. No admission screening or human expert validation is inferred from these development runs or from d0179/Method.tex.
