# Reference derivation

The reference is an observation of two application-provided recall views, rooted in the unique official record for Z-0436-2014. The source record explicitly cites K050369 and K081137. Both cited applications are retained; no application is excluded.

The saved source capture supplies record ID 123823 and its Recall Number. The root's actual application links lead to the two official 510(k) records. Each record's actual CDRH Recalls control leads to its application-scoped view. K050369 has 34 results across contiguous 1–10, 11–20, 21–30 and 31–34 pages. K081137 has seven results on one page. Complete original view text is preserved. These totals characterize the returned views, not all historical recalls associated with a device, model or firm.

The K050369 page-two link 25 actually resolves to record ID 123823 and Recall Number Z-0436-2014. Positive membership needs one exact witness; resolving its other 33 targets is unnecessary, although all four result pages are saved and counted.

For K081137, each displayed link was actually clicked. The official target IDs are:

| Origin reference and link | Target record ID | Target source |
|---|---|---|
| turn55view1:21 | 143856 | turn59view0 |
| turn55view1:22 | 131929 | turn59view1 |
| turn55view1:23 | 122634 | turn59view2 |
| turn55view1:24 | 122388 | turn59view3 |
| turn55view1:25 | 119691 | turn59view4 |
| turn55view1:26 | 119692 | turn59view5 |
| turn55view1:27 | 116999 | turn59view6 |

No target is 123823. All seven exact official final URLs and their click provenance are exposed in the raw response, including records whose detail body was truncated. Absence therefore no longer rests on index dates or descriptions. The constructor's earlier date-only exclusion was insufficient and has been superseded in the opportunity check.

Run `python reference.py --out-dir rebuilt` from this directory to regenerate oracle.psv, inventory.json and reference_derivation.json. The program extracts the application set from the source field, follows actual click provenance through application records and view pages, verifies contiguous page counts, and joins each resolved link to its official final record ID. It assigns PRESENT on an exact source-ID witness and ABSENT only when every displayed target has a resolved exact ID and none matches. Missing target evidence raises an unresolved-reference error. The final mapping is not hardcoded.

The two output rows are K050369/PRESENT and K081137/ABSENT. The inventory records all 41 displayed scope rows, their origin pages and available exact target evidence. This is sufficient for the two-result membership question; unknown identities among the 33 remaining positive-view rows cannot change PRESENT.

Source observations span 13 September 2026 UTC. The root's required identity fields agree before and after the bounded audit. The seven-row original view agrees with a prior saved complete view. A final K081137 refresh returned only a title/URL, so it is not claimed as a complete new observation. K050369 has one complete four-page observation, followed by a first-page recheck; no second complete pagination is claimed. Page Last Updated and crawl metadata vary. Future evaluation requires a relevant source-state check and must not assume a fresh origin request or permanent stability from these captures.
