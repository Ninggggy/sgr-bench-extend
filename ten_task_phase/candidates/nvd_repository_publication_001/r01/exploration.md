# Catalogue publication-delay candidate

Decision: construct one candidate for a uniform source-reported publication-date difference. This is a pre-blind clarification of the requested field, not an adjudication of absolute first public access. The cohort is unchanged, including both Audiobookshelf records. No lag threshold, reporter condition, extra eligibility filter or additional cohort was introduced.

Research anchor: 2026-09-09. Actual access: 2026-09-10. Browser crawl labels are retained as crawl labels, not represented as origin-server access timestamps.

## Why the date clarification is sufficient

The question consistently requests the calendar date displayed in the issue-matched repository advisory's publication header. It applies that definition to every member, including all same-day exclusions. This is an observable field with a unique value in the inspected evidence. It does not ask when the information first became publicly accessible by any means.

The [Audiobookshelf repository advisory](https://github.com/advplyr/audiobookshelf/security/advisories/GHSA-mgj7-rfx8-vhpr) displays October 29, 2023. The [research disclosure](https://securitylab.github.com/advisories/GHSL-2023-203_GHSL-2023-204_audiobookshelf/) labels November 1 as advisory publication. Both observations remain in the source record. The controller's separately reported reopening agrees with October 29; that report is corroboration supplied in the task, not a new observation executed by this explorer. Under the clarified field, the two records each have a 45-day calendar difference. The alternative timeline would yield 42 days, but it is a different source-reported field and is not silently substituted.

## Complete scope and field review

The complete annual JSON is now d0011.response. Its header reports 31,404 results, startIndex 0, version 2.0 and timestamp 2026-09-09T03:02:02.5213535. The controller previously executed both annual checks successfully: 31,404 unique entries, 150 published on the specified date within the annual identifier-year scope, and 15 with the declared source identifier. Their actual result files are d0006.response and d0007.response. These executions are not claimed as work performed by this explorer.

This session reread the current annual header and all 15 complete selected CVE objects at their recorded character offsets. Every identifier, catalogue publication timestamp, sourceIdentifier and reference set was checked against the prior pool. The complete annual filter is also present in both delivered programs.

All 15 CVE List members in d0010.response report PUBLISHED and GitHub_M. Their recorded update dates precede the anchor. Their CNA advisory identifiers were checked individually. Those identifiers are not assumed to be the repository advisory identifiers.

Nine repository headers display December 13, 2023. Vyper displays December 12; Jellyfin December 6; the shared Scrypted advisory October 13; and the shared Audiobookshelf advisory October 29. Thus six CVEs qualify, with nine observed same-day exclusions. None is excluded because retrieval failed.

## Issue-level identity

Eleven records directly reference a repository advisory in the annual JSON; the saved repository output explicitly identifies the corresponding CVE. This includes Jellyfin, whose CNA source GHSA differs from the directly referenced repository GHSA.

The four remaining records reference shared research disclosures. For Audiobookshelf, the annual AuthorController.js reference selects the disclosure's GHSL-2023-203 issue; HlsRouter.js selects GHSL-2023-204. The disclosure's advisory-publication link was actually followed, and its destination is the repository advisory explicitly titled with both issue identifiers. The saved repository excerpt includes the first issue heading; the second issue is explicitly named in the repository title and separately mapped by the research disclosure's second issue heading. No claim is made that the saved repository excerpt contains an untruncated second issue section. The repository CVE field says No known CVE, so it is not used as a direct CVE match.

For Scrypted, plugin-http.ts selects GHSL-2023-218 and Login.vue selects GHSL-2023-219. The disclosure's publication link selects a repository advisory containing both issue headings. The repository CVE field names CVE-2023-47623; the separate mapping for CVE-2023-47620 is additionally supported by the actual OSV member's explicit CVE reference. These are issue-specific mappings, not same-package assumptions.

The reference program reconstructs the observed disclosure-to-advisory link from saved browser click metadata and the resulting page URL. It extracts the issue identifier from the disclosure heading matching the annual code-reference filename and checks that the destination advisory explicitly contains that issue identifier.

## Official APIs, bulk alternatives and dependency

The [global advisory API documentation](https://docs.github.com/en/rest/security-advisories/global-advisories) and [repository advisory API documentation](https://docs.github.com/en/rest/security-advisories/repository-advisories) establish legitimate public retrieval paths. CVE List and the advisory-database repository are legitimate bulk alternatives. All remain permitted.

The actual NVD records and CVE List members do not supply the complete required repository-publication fields. The inspected [Scrypted OSV member](https://raw.githubusercontent.com/github/advisory-database/main/advisories/github-reviewed/2024/02/GHSA-w4hv-vmv9-hgcr/GHSA-w4hv-vmv9-hgcr.json) reports February 16, 2024 for its publication/review metadata, has an empty aliases array, and has null nvd_published_at. It references the relevant CVEs and repository advisory but does not supply October 13, 2023 as the repository-publication field. The saved browser log preserves rendered excerpts and extracted trailing fields, not a standalone raw OSV JSON download.

Actual global/repository API attempts encountered configured-source restrictions or browser errors. These are preserved. Documentation examples are not cohort responses. No universal negative claim about APIs, no successful whole-scope API coverage claim and no inference that API failure creates SGR is made.

A nontrivial retrieval decision is nevertheless observed: annual evidence selects a disclosure; the disclosure's issue and publication-link evidence selects a different repository advisory identity from the CNA/global identity. That identity changes the subsequent URL or API parameters needed to retrieve the publication field. A legal repository API request after this discovery preserves the dependency. An alternative global API route might shorten it and remains permitted. The evidence does not demonstrate a fixed small set of public downloads containing every decision field, nor does it conclusively exclude every possible future shortcut.

The two-file offline reference computation does not itself demonstrate retrieval dependency. d0010.response is a research-session log assembled from adaptive source retrievals, not a public bulk product independently available to a solver before the identity decisions.

## Stability and quality assessment

Historical publication-date stability is supported, with limits. The annual export timestamp falls on the anchor. Inspected CVE List update metadata precedes it. Vyper's separate global history retains its December 12 repository date despite a November 2024 update. Scrypted's repository header, disclosure timeline and separate global history agree on October 13; its global metadata reports its last update in February 2024. The older saved Audiobookshelf header and the controller-reported reopening agree on October 29. These observations support the source-reported historical fields; they do not establish immutable pages or an exact archived reconstruction of every page at midnight on the anchor.

The candidate is strong on boundedness, field consistency, issue identity and unique output. Its limitation is incomplete actual-response API auditing and uneven independent corroboration of individual header dates. Those limitations are disclosed rather than converted into exclusions or invented difficulty claims. The task measures a catalogue-versus-repository date difference, not absolute disclosure latency or causation.

## Construction and verification

This session decoded all of d0010.response, reviewed the prior source list and failures, reread all selected annual objects, and reconstructed all 15 advisory mappings and dates in JavaScript from the saved source outputs. The extraction produced six earlier and nine same-day dates. Separate UTC epoch and Gregorian integer-day calculations agreed: October 13 gives 61 days; October 29 gives 45; November 1 gives 42; December 6 gives 7; December 12 gives 1; December 13 gives 0.

reference.py independently computes the public rows from d0011.response and d0010.response; it does not obtain answers from candidate_pool.json. independent_check.py separately scans annual objects and recomputes header dates and differences with integer Gregorian arithmetic. It uses the pool only for evidence locators and checks the source-derived results against the oracle. Both use only the standard library, make no network requests and print results without modifying source files. Python was not executed in this session.

Run with the delivered artifacts and saved responses in one directory:

    python reference.py /path/to/artifacts
    python independent_check.py /path/to/artifacts

## Preservation

Current registered-file meanings differ from identifiers embedded in older research. d0011.response is the annual JSON; d0010.response is the saved browser/tool-output log; d0001.response is the prior rejection narrative; d0002.response is the prior source list; d0003.response is the prior failure list; d0004.response is the prior unresolved pool; d0005.response is the prior dependency assessment; d0006.response and d0007.response are controller execution results; d0008.response and d0009.response are earlier programs.

The browser log includes filtered and truncated renderings. The programs rely only on metadata actually present in that log and do not reconstruct omitted text. No new network observation was needed to resolve the field definition or the issue mappings. Known nonretryable unsafe URLs were not retried, and no allowlist was changed. No services, packages, external messages, operational testing, new hashes, frozen contracts or additional admission gates were introduced. No final admission audit or scores are claimed.
