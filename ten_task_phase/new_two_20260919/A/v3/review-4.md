# A v3 pre-blind quality audit

**Verdict: passed.** Independent inspection of the embedded source excerpts, complete index, programs, and supplied results supports substantive correctness, pairing, public-path completeness at the stated evidence level, and the targeted scoring repairs. No required correction remains. This review used static inspection and manual derivation; it did not execute the scripts, reproduce browser-plugin access, or launch model trials. Prior review labels were not used as proof or authorization.

## Scope, identities, and historical semantics

The complete 2024b country index contains exactly three rows whose country-code list includes PT: Europe/Lisbon, Atlantic/Madeira, and Atlantic/Azores. No additional multi-country row includes PT. Selecting country-code membership correctly excludes Africa/Maputo and Asia/Dili, irrespective of Portuguese historical connections. The oracle uses the scoped identifier Atlantic/Azores.

The active source records independently justify both exclusions. Lisbon uses base offset zero with W-Eur in 2024a and EU in 2024b before September 1992; at base zero, their relevant 01:00 standard and 01:00 UTC transition times coincide. Both releases then use the same base +01:00 EU era. Madeira uses base zero with EU throughout the requested window in both releases. Earlier Port-rule changes do not introduce differences in this window. See source_extracts.txt, 2024a lines 2161–2164 and 2201–2202, and 2024b lines 2290–2293 and 2386–2388.

The task explicitly fixes database semantics, releases, local-time window, POSIX time, and complete inverse offset sets. Consequently, uncertainty in the historical legal evidence—particularly the assumed June 1993 transition—does not make the requested answer ambiguous. Commented vanguard/rearguard alternatives are not simultaneous active rules. Abbreviation and DST-status changes alone are correctly excluded.

## Oracle and recomputation

The active Azores records and both releases' EU/W-Eur rules support this UTC transition sequence:

- 2024a: −01:00 to +00:00 at 1992-03-29 02:00 UTC; total offset remains +00:00 across the September 1992 and March 1993 era changes; return to −01:00 at 1993-09-26 01:00 UTC.
- 2024b: −01:00 to +00:00 at 1992-03-29 01:00 UTC; return to −01:00 at 1992-09-27 01:00 UTC; advance to +00:00 at 1992-12-27 02:00 UTC; advance to +01:00 at 1993-03-28 01:00 UTC; return to +00:00 at 1993-06-17 01:00 UTC; return to −01:00 at 1993-09-26 01:00 UTC.

These follow from 2024a lines 2182–2185, 2024b lines 2354–2356, and the supplied rule definitions. In particular, 01:00s at base −01:00 means 02:00 UTC.

Mapping those UTC spans into local time reproduces all eight oracle rows: two March 1992 intervals, the September fold and subsequent winter difference, the December gap, and the March gap, summer difference, and June fold in 1993. Every listed endpoint and offset set agrees. Adjacent listed intervals have different pairs of sets; equal periods are omitted. No missing interval or incorrect merge was found.

recompute.py implements the appropriate exhaustive construction: derive scope from the index, compile each source independently, map constant-offset TZif spans into local coordinates, clip to the window, overlay endpoints, compare complete offset sets, and merge equal adjacent pairs. It does not read the oracle. Its explicit-transition coverage is adequate for these sources and dates; this is not a general-purpose claim about arbitrary TZif inputs.

The supplied 162 boundary checks corroborate the inversion, including gaps, folds, and endpoints. They share compilation and endpoint discovery with the main computation, so they are not wholly independent source verification. Completeness rests on the finite partition and source coverage. The documented replacement of the earlier 192-check claim with the reproducible 162-check result is appropriate.

## Pairing and scoring

CG and GO have identical substantive requirements and output schemas. CG adds only methodological guidance. A shared oracle is appropriate; the guidance does not disclose the eight intervals or narrow the declared scope.

The scorer preserves five-field weighting, zone-plus-start key gating, duplicate and extra-row penalties, extra-column penalties, and order-independent Item-F1. Whole-answer correctness separately enforces complete rows and their order. Explicit aliases are documented, and Portugal remains unnormalized.

Both prior concrete scoring defects are repaired in the supplied implementation. The substantive-content predicate prevents all-empty or delimiter-only tables from setting strictly_below_70. The wrapper records unsupported triple-backtick-prefixed content, preventing the stated prose bypass from receiving whole-answer correctness. verify_scorer.py contains 23 fixtures, consistent with scorer_fixtures.json; the visible expected counts and fractions are internally consistent. These are inspected supplied results, not reviewer reruns.

Exactly 70% correctly fails the strict-below comparison. Correct keys, endpoints, and old sets with every new set wrong can still yield 80% Item-F1 under the declared weighting. That is a transparent metric property; offset-field accuracy and whole-answer correctness provide necessary separate context. Numerical threshold flags do not replace trajectory, access, and exposure review.

## Browser evidence, retrieval, and shortcuts

Constructor captures now contain both Portugal sections, both EU/W-Eur rule sets, and the complete country index. Their decisive contents agree with the supplied source excerpts and support a complete source-based solution path. acquisition.json separately records pinned IANA originals. This supports the stated constructor-access evidence; it does not establish fresh independent reviewer browser-plugin reproduction.

The reported IANA browser download-navigation block is an environmental limitation of that route. It is not a missing-source finding or proof of task infeasibility, given the supplied GitHub browser captures and separately reported ordinary-web retrieval. The previously missing decisive evidence is now embedded; unrelated countries from the full europe files are unnecessary for this substantive review.

Necessary reasoning dependencies are scope selection, release-specific active eras, referenced rules, suffix interpretation, total offsets, and inversion. They do not require many sequential network calls: the known source files can be retrieved together. Tagged diffs, direct retrieval, local search, manual derivation, and permitted compilation are legitimate shortcuts. Release notes or current third-party histories alone do not establish the requested historical inverse sets. No exhaustive absence of a precomputed answer is established.

The repairs establish auditability and quality, not difficulty. No difficulty inference or testing authorization follows from this pass.
