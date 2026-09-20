Keep the existing reference.py, independent_check.py, field_boundaries.json, candidate_pool.json, oracle.psv and rules.json from d0003. Their exact contents were inspected; no reference implementation change is needed. recover_private_assets.py below can recover those exact files and all saved failed/successful outputs from the saved d0003.response, without network access or installations.

reference.py reads sources_raw/d0009.response and maps PMCID to sources_raw/notice_xml/<registry path> through sources_raw/live_registry_private.json. For each eligible notice, it reads pone.<correction suffix>.s001.pdf and .s002.pdf. It asserts notice DOI identity and the same research DOI in both PDFs. The three first-author strings in field_boundaries.json delimit the title; they are not answer strings.

independent_check.py reads sources_raw/d0010.csv, parses notice bodies using HTMLParser, resolves research DOI from XML text, and reconstructs maximum-font PDF headings using physical character gaps. It does not import reference.py, read the oracle, or use field_boundaries.json. Its literal corpus size assertion is an existing source sanity check, not a public row-count condition. Both eligibility regexes are narrower than arbitrary English paraphrases but match the observed notices; the full inventory review supports their use for this corpus.

The controller saved controller_computed.psv and controller_independent.psv, both equal to oracle.psv. Controller reference stderr reports scope_records=164, republication_notices=18, title_republication_notices=3; independent stderr is empty. This session compared those complete strings directly in JavaScript. It also independently reconstructed the six positive title strings from d0002 header excerpts and verified their equality. No Python was run in this session.

Preserve independent_check.attempt1.py and controller_independent.attempt1.psv: the first attempt incorrectly joined KRAS- or into KRAS-or in both titles. Do not normalize that failure away. The supplied corrected implementation uses spatial character gaps and matches the oracle.

Controller rerun commands, using its existing bundled environment and recovered raw files:

python reference.py sources_raw
python independent_check.py sources_raw

The 164 raw XMLs and 26 PDFs remain controller-owned existing downloads. Registered d0001/d0004 in this review are private JSON assets; they must not be confused with source116 notice_xml/d0001.response or source116 PDF-member d0004. Do not replace raw XML/PDF files with construction summaries. Do not expose d0001-d0004, these review files, oracle, programs or saved outputs in blind materials.
