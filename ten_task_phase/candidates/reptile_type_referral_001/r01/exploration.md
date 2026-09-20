# Admission decision

Rejected for admission, with a complete provisional construction preserved. A source-dependent cross-genus retrieval was observed, but the advertised historical full-dump bypass remains untested. This is not a claim that no qualifying task can exist in this ecosystem. Neither delivered Python program was executed; content_validated is false.

# Official access and bulk investigation

The [official download index](https://www.reptile-database.org/data/index.html), saved as d0003.response, links the taxa CSV, dated checklists, a synonym workbook and historical complete dumps. The downloaded CSV d0006.response contains accepted names, authorities and rank fields, but no specimen Types or comments. The June workbook d0007.response additionally has a type_species marker; that marker identifies genus type species, not museum specimens.

The synonym workbook d0021.response was successfully downloaded after an SSL failure. Its notes identify the May 2023 release, explain that authors were removed, and explicitly allow a historical name to map to multiple current names. It does not supply specimen Types.

The official FAQ points to a programmatic interface. Its landing page returned HTTP 500, while the documented CSV export worked. The old home and unparameterized search form initially returned 503. Later species and parameterized searches succeeded. A synonym search returned an empty HTTP 522 response. These are preserved access observations, not evidence of task hardness or negative taxonomic results.

The index documents complete historical dumps with names, years, synonyms, comments and Types. The latest linked full dump is April 2020. More recent full versions are described as available to academic collaborators on request. The registered tool rejected Figshare and DOI hosts as outside its configured sources; web attempts also failed. These tool failures do not establish legal unavailability, missing content, or absence of a bypass. No contact request was sent. The newer search frontend also remains incompletely investigated.

# Historical-name branch and why it was insufficient

The current oblonga page records a name-bearing specimen number. Searching that number actually returned both accepted Chelodina oblonga and Chelodina rugosa: d0036.response. Thus an earlier field genuinely changed a later query. However, both records already belong to the bounded pre-1900 Chelodina pool. Moreover, rows 8864–8865 of the historical synonym workbook already map Chelodina oblonga to both accepted names. This branch does not establish a necessary expansion beyond the initial collection.

The overlapping specimen treatment should not be converted into a biological assertion that the two accepted species share one valid type. The records contain historical interpretations and invalidated designations. Their disagreement is preserved rather than silently resolved.

# Stronger provisional construction

The full accepted Chelodina search contains sixteen species. Filtering original authority years before 1900 gives five seed records; all five were downloaded and their Types fields inspected.

Only the [expansa type account](https://reptile-database.reptarium.cz/Chelodina/expansa) satisfies the proposed accession-book condition. It identifies a former catalogue number as Emydura macquarii. A back-search on that number redirects to expansa alone, so the number search itself does not discover the other accepted record. Reading the textual referral changes the next record retrieval to Emydura macquarii and the next genus filter to Emydura.

The broad Emydura search returns six substring matches, including Pseudemydura umbrina. Exact genus matching returns five and agrees with the live CSV and June checklist. Filtering those five by original description year before 1900 gives three provisional answer rows. Their own holotype identifiers were read from the current species pages; separately labelled synonym and subspecies types were excluded.

This collection has a natural museum-catalogue audit purpose and a complete, explicit seed boundary. Public questions do not disclose the referred species, specimen number, target genus, authors or expected row count.

# Checks actually performed

JavaScript inspection of saved raw responses derived the unique referral and provisional rows. An independent pass through the June XLSX XML reproduced the same target names and years as the live CSV. The three target years span 46 years (1876 minus 1830). This arithmetic is an audit observation, not an extra answer condition. Current target pages supplied the holotype identifiers. The broad-search extra match was explained by substring semantics and eliminated with a successfully tested exact filter.

# Stability and remaining uncertainty

The June checklist and September live export agree on both exact genus memberships and the selected target names/years. That is cross-date corroboration, not immutability. Saved responses provide a reproducible observation snapshot. The australis page describes a 2024 synonymy change, so an older dump cannot simply be assumed to represent current accepted taxonomy.

Conversely, an older full dump might already contain the accession referral and all required holotype identifiers; joining it to the current checklist could collapse the retrieval dependency. Its actual contents must be inspected. Adding a current-date condition does not automatically defeat this shortcut. No valid API or bulk path is forbidden in either public question.

The delivered reference.py and independent_check.py reconstruct the provisional answer from saved raw files using different membership sources and HTML parsing methods. Their execution and the complete admission audit remain pending. CG.json, GO.json and oracle.psv are review artifacts, not an accepted benchmark candidate.
