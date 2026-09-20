# One changed-mechanism investigation

Protocol date: 2026-09-09. Actual visits: 2026-09-10. One candidate was constructed; no acceptance score or independent campaign audit is asserted.

The inherited registry mapping is d0021.txt (source audit), d0022.txt (prior exploration/rejection), and d0023.txt (root native-web output). The prior rejection remains correct for its original predicate: no declaration in this corpus contains a numeric patent/application identity. It does not establish that the unnumbered disclosed invention cannot be identified with additional explicit primary evidence.

## Scope and declaration inclusion

The complete fresh official REST response d0024.response contains 16 CORE records, service version 6.9. Its PMID set matches both d0001.response and d0003.response, which were reread completely. All records have indexed publication year 2019 and journal Genome biology. Registered XML for every record was read and its competing-interest section re-extracted. Every XML also contains the seed DOI. The prior audit supplies independent publisher checks of journal, publication year, citation and declaration for all 16; these checks were reused as requested. The selected paper's publisher declaration was freshly corroborated.

Eleven declarations report no competing interests. Four report commercial relationships without a method-related patent declaration. One declares an unnumbered application for BART-Seq. The complete included/excluded population and field locators are in candidate_pool.json. The reference code does not use that file's inclusion flags or reasons to select the answer; it uses the file-to-article mapping and re-extracts the original XML declarations.

The new [primary transfer document](https://www.ascenion.de/fileadmin/user_upload/Technology/Images/Technologies/TO_01-00890_Multiplexed_Targeted_Barcoding_Technology_for_NGS_Applications.pdf) expressly associates BART-seq, the original paper DOI, and its technology patent. It also identifies EP and US nationalization. This is the missing identity bridge, not an author/title similarity hypothesis. The candidate therefore admits the unnumbered declaration under an explicit condition present in both public variants.

## Lawful APIs, bulk sources and actual access

The [official OPS documentation](https://www.epo.org/en/searching-for-patents/data/web-services/ops) describes a supported REST XML route with registration and OAuth. Its family/equivalents services can combine patent metadata retrievals. A direct unauthenticated family request did not yield a record; the registered downloader separately rejected the configured host. Neither result invalidates the API.

The [official DOCDB documentation](https://www.epo.org/en/searching-for-patents/data/bulk-data-sets/docdb) describes worldwide bibliographic and simple-family XML data. Its stated approximately 3 GB compressed frontfiles and 200 GB backfile exceed this downloader's 512 MB response bound. Those figures are documentation, not measured downloads. No complete DOCDB file was fetched, and smaller relevant alternatives have not been exhaustively ruled out. The public sample landing page returned a JavaScript shell.

Linked open EP documentation and attempted data pages did not yield usable records. USPTO API pages and Patent Center rendered no usable metadata; the Global Dossier request returned 403. Official publication/family links and transport failures are retained in failures.json. No accounts, authentication bypass, services, packages or external messages were used.

## Publication records and completeness

The resolved [WO record](https://patents.google.com/patent/WO2017060316A1/en) displays family 54266422 and three jurisdiction branches. The EP and US application-publication pages display the same family and country set. This agrees with the primary transfer document. No additional published application in that family was observed. The priority claim EP15188404.6 is not silently converted into another published-application row.

The US branch link from the WO page is a grant. A discovery lookup through its patent history revealed the application publication, which was then separately retrieved. Its [original US publication front page](https://patentimages.storage.googleapis.com/5a/c9/ea/28001fbb244264/US20190002953A1.pdf) identifies an application publication dated 3 January 2019, the US application number, and the PCT application. The later grant is dated 22 December 2020. The displayed US publication history has these two entries, so selecting the grant would change both the requested identifier and date. Their interval is 719 days, computed in JavaScript in this session; the independent Python check recomputes it from the separately saved history fields.

The EP and WO publication lists each contain one application-publication entry. The US list contains the application publication and subsequent grant. Selecting the earliest application-publication entry per application yields the three rows in oracle.psv. These historical bibliographic facts are the requested output; no legal-status, priority-entitlement or rights conclusion is made.

Official family/register responses were not accessible in this session. Complete-family corroboration therefore relies on the explicit transfer document and matching secondary family displays. The US publication itself was checked in an original-document facsimile delivered by a mirror. EP first-publication metadata and WO first-publication metadata were not independently obtained from an official-host bibliographic response. These are material evidence limits, not omitted work disguised as successful verification.

## Dependency after accounting for shortcuts

The disclosure changes the next retrieval: it supplies the method identity used to locate explicit transfer evidence. The transfer evidence then supplies the exact publication identity used to retrieve patent metadata. Neither the complete CORE responses nor the fixed article XML collection contains those patent publication histories. No retrieved fixed source independent of that invention discovery contains the declaration-to-invention bridge together with every decision field.

A stronger claim about separate family-to-jurisdiction lookups would be false. The discovered [US application page](https://patents.google.com/patent/US20190002953A1/en) already contains the application identifiers across the three branches, its own publication history, and the WO/EP publication dates under Also Published As. Thus the patent-side catalogue can be computed from one discovered page. OPS or a suitable bulk extraction could likewise collapse that portion. The candidate retains only the substantive earlier disclosure/identity-dependent retrieval; it does not require separate office visits or prohibit valid API/bulk solutions.

The uninspected global DOCDB export is an unresolved alternative, not proof of either global collapse or global non-collapse. In particular, a patent bibliographic export does not by its documented fields establish the author's unnumbered declaration-to-transfer-document identity link. No complete all-decision-field bulk shortcut was actually demonstrated.

## Actual counterexample

The resolved WO page links US20230151358A1 as a citing patent. Its own metadata was retrieved: family 75690287, US application 17/920,694, international application PCT/EP2021/060704, and a Patent Citations entry for the resolved WO publication. Following the citation would therefore retrieve another family, not a national phase of the declared invention. This is a family-versus-citation counterexample; it is not claimed to be a patent citing the BART article. The prohibited retry of EP4321629A4 was not attempted.

## Stability, reproduction and limits

Scope stability is supported by agreement of three complete CORE responses, original XML declarations, and inherited publisher corroboration. Eleven XML files explicitly report PMC version 1; five omit that field, as recorded in d0021.txt. Missing versions were not invented. The selected publisher page identifies a 2019 version of record. The answer uses publication dates from 2017–2019, with the US date also printed on the original publication.

The source visit was one day after the protocol anchor. The public instructions apply a publication-date cutoff, not a claim that today's index, transfer document or family display was archived on the preceding day. The transfer PDF is not assigned an invented issue date.

Registered responses remain the full raw article/index sources. Native web responses are also preserved by the controller. The supplied web/*.txt files are attributed, selected metadata excerpts/transcriptions from those actual responses, not fabricated downloads or full-page copies. They exclude scientific procedures and inferred legal-status fields. failures.json retains the actual failure messages; no failed request is treated as an empty dataset.

reference.py reads registered JSON/XML and the supplied web evidence, recomputes inclusion, joins the discovered patent identity to its family, and selects the first observed application publication. independent_check.py uses separate Info fields for WO/EP, the original US front page, and distinct US history fields. It also checks both public variants share the same substantive instruction and output format. Neither script was executed here because no Python tool is available. Actual JavaScript inspection confirmed the matching corpus sets, declaration classification, three catalogue rows and 719-day interval. Controller execution remains necessary.

Construction evidence, pool, oracle, rules and code are private construction assets. Only CG.json or GO.json is suitable for a blind solve. No hashes, frozen contracts, baselines or additional campaign gates were introduced.
