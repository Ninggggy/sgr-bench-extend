# 修订题面（含受阻草稿）

测试资格以review.json为准；本文件不代表全部题目已完成质量修复。

## arxiv_historical_title_001 / polish01

状态：blocked；有界完整路径未证实：旧证据由完整年度语料和705条评论前沿建立范围，再查历史版本。不能把旧全量构造路径直接当作v2盲测路径；未证明60请求/10页内完整替代路径。

### CG

Find withdrawn preprints first submitted in 2021 (UTC) whose categories include cs.LG, including cross-listings. Use catalogue metadata as observed on 9 September 2026.

For each preprint, its latest recorded version must be withdrawn, and its current notice must explicitly name another archive record as the replacement or continuation of the same work. Supersession, subsumption, mergers, revised resubmissions and corrections of duplicate submissions qualify when the notice names that replacement. Ordinary citations, administrative overlap notices, incoming mergers and active companion papers do not qualify on their own. Follow only the directly named replacement.

Use the submission timestamp of the predecessor's latest withdrawn version as the cutoff. In the replacement's history, select the version with the latest submission timestamp at or before that cutoff. Compare exact UTC submission timestamps, not announcement dates. Omit a relationship if no replacement version existed by the cutoff.

Keep the relationship only if that selected version's title differs in wording from the replacement's current title. Ignore layout whitespace and equivalent mathematical rendering. Return every qualifying relationship.

Suggested approach: Establish the year/category scope; verify withdrawal and replacement direction; compare the two submission histories; then check the selected historical title against the current title.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Return only a pipe-separated table with header predecessor_id|replacement_id|selected_version. Use unversioned archive identifiers in the first two columns and v followed by the version number in the third. Use one row per qualifying direct relationship, sorted by predecessor_id then replacement_id.

### GO

Find withdrawn preprints first submitted in 2021 (UTC) whose categories include cs.LG, including cross-listings. Use catalogue metadata as observed on 9 September 2026.

For each preprint, its latest recorded version must be withdrawn, and its current notice must explicitly name another archive record as the replacement or continuation of the same work. Supersession, subsumption, mergers, revised resubmissions and corrections of duplicate submissions qualify when the notice names that replacement. Ordinary citations, administrative overlap notices, incoming mergers and active companion papers do not qualify on their own. Follow only the directly named replacement.

Use the submission timestamp of the predecessor's latest withdrawn version as the cutoff. In the replacement's history, select the version with the latest submission timestamp at or before that cutoff. Compare exact UTC submission timestamps, not announcement dates. Omit a relationship if no replacement version existed by the cutoff.

Keep the relationship only if that selected version's title differs in wording from the replacement's current title. Ignore layout whitespace and equivalent mathematical rendering. Return every qualifying relationship.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Return only a pipe-separated table with header predecessor_id|replacement_id|selected_version. Use unversioned archive identifiers in the first two columns and v followed by the version number in the third. Use one row per qualifying direct relationship, sorted by predecessor_id then replacement_id.

## arxiv_historical_title_002 / polish01

状态：blocked；有界完整路径未证实：r03曾需25890条完整处置修复词法筛选漏项。不能直接以关键词搜索代替完整范围证明；未证明当前额度内合法完整路径。

### CG

Reconstruct the replacement citations for withdrawn preprints first submitted in 2020 (UTC) whose current categories include cs.LG, including cross-listings. Use public metadata current through 9 September 2026.

Include every direct successor named by the withdrawn source record as its replacement, updated or corrected version, or merger result. A correction redirecting a mistaken separate submission qualifies. Related papers, independently obtained equivalent results and unnamed forthcoming work do not qualify. Successors may belong to any year or category.

For each source–successor relationship, use the source record's last listed submission timestamp as the cutoff. This is a bibliography convention, not the date when withdrawal happened. Select the successor version with the latest submission timestamp at or before the cutoff, and report that version's title. Include all versions tied at that timestamp. Omit a relationship if no successor version existed by the cutoff. Do not filter for title changes.

If a source's last submission is later than 9 September 2026 UTC, report version drift rather than silently changing the cutoff. Return every qualifying relationship.

Suggested approach: Establish the annual category scope, identify withdrawn records and their directly named successors, then use both submission histories to locate the eligible version and its title.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Return only a pipe-separated table with header source_id|source_last_submission_utc|target_id|target_version|target_submission_utc|target_title. Use unversioned record identifiers, an integer version number, UTC timestamps as YYYY-MM-DDTHH:MM:SSZ, and the selected version's title, preserving its wording. Use one row per source, direct successor and selected version; sort by those three fields.

### GO

Reconstruct the replacement citations for withdrawn preprints first submitted in 2020 (UTC) whose current categories include cs.LG, including cross-listings. Use public metadata current through 9 September 2026.

Include every direct successor named by the withdrawn source record as its replacement, updated or corrected version, or merger result. A correction redirecting a mistaken separate submission qualifies. Related papers, independently obtained equivalent results and unnamed forthcoming work do not qualify. Successors may belong to any year or category.

For each source–successor relationship, use the source record's last listed submission timestamp as the cutoff. This is a bibliography convention, not the date when withdrawal happened. Select the successor version with the latest submission timestamp at or before the cutoff, and report that version's title. Include all versions tied at that timestamp. Omit a relationship if no successor version existed by the cutoff. Do not filter for title changes.

If a source's last submission is later than 9 September 2026 UTC, report version drift rather than silently changing the cutoff. Return every qualifying relationship.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Return only a pipe-separated table with header source_id|source_last_submission_utc|target_id|target_version|target_submission_utc|target_title. Use unversioned record identifiers, an integer version number, UTC timestamps as YYYY-MM-DDTHH:MM:SSZ, and the selected version's title, preserving its wording. Use one row per source, direct successor and selected version; sort by those three fields.

## economic_kegg_ddi_001 / polish01

状态：blocked；完整已验证单条路径为20+40个端点，尚需组身份/成员发现，超过60请求。仅SSRI端点实测漏14对；完整60-ID导出禁止。历史观测期也不能冒充当前数据。未证明另一完整合法路径。

### CG

Compile the reported interaction classes between the complete drug groups “Selective serotonin reuptake inhibitor (SSRI)” and “MAO inhibitor” (also called “Monoamine oxidase inhibitors”). The reference observations were made on 11–13 September 2026; this does not require you to pretend that your actual access occurred then. Report any evidence that relevant source records have since changed.

Include every leaf D-number drug entry in both official group records, including nested branches, salts and hydrates. Keep distinct D numbers separate. Do not filter by country tags or common antidepressant use.

Return a cross-group pair if either direction reports CI (contraindication), P (precaution), or both. Merge the two directions into one row, preserving all reported classes. Exclude within-group pairs. Absence from one direction is insufficient to exclude a pair. Only complete successful coverage can establish that no interaction is reported; it does not establish clinical safety.

Return the complete result. If access or conflicting records prevent this, state the limitation and identify the answer as partial.

Suggested approach: Discover both complete group memberships, inspect interaction records for the discovered ingredients in both directions, then combine and sort the cross-group pairs.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Put only a pipe-separated table in the answer field, with the header ssri_id|mao_id|classes. Use exact D numbers without the dr: prefix; names are not required. Put the SSRI member first and the MAO inhibitor member second. Write one row per distinct ingredient pair. The classes value must be CI, P, or CI,P. Sort rows by ssri_id, then mao_id, both ascending. Include every qualifying pair; there is no row limit. If successful complete coverage finds no qualifying pairs, write the header followed by a single line NONE. In the separate evidence field, provide public evidence URLs, actual UTC access dates, and any relevant revision dates supplied by the source; say unavailable when a revision is not supplied. Put any access limitations or unresolved source conflicts in that field as well.

### GO

Compile the reported interaction classes between the complete drug groups “Selective serotonin reuptake inhibitor (SSRI)” and “MAO inhibitor” (also called “Monoamine oxidase inhibitors”). The reference observations were made on 11–13 September 2026; this does not require you to pretend that your actual access occurred then. Report any evidence that relevant source records have since changed.

Include every leaf D-number drug entry in both official group records, including nested branches, salts and hydrates. Keep distinct D numbers separate. Do not filter by country tags or common antidepressant use.

Return a cross-group pair if either direction reports CI (contraindication), P (precaution), or both. Merge the two directions into one row, preserving all reported classes. Exclude within-group pairs. Absence from one direction is insufficient to exclude a pair. Only complete successful coverage can establish that no interaction is reported; it does not establish clinical safety.

Return the complete result. If access or conflicting records prevent this, state the limitation and identify the answer as partial.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Put only a pipe-separated table in the answer field, with the header ssri_id|mao_id|classes. Use exact D numbers without the dr: prefix; names are not required. Put the SSRI member first and the MAO inhibitor member second. Write one row per distinct ingredient pair. The classes value must be CI, P, or CI,P. Sort rows by ssri_id, then mao_id, both ascending. Include every qualifying pair; there is no row limit. If successful complete coverage finds no qualifying pairs, write the header followed by a single line NONE. In the separate evidence field, provide public evidence URLs, actual UTC access dates, and any relevant revision dates supplied by the source; say unavailable when a revision is not supplied. Put any access limitations or unresolved source conflicts in that field as well.

## economic_nvd_daily_001 / polish01

状态：blocked；需逐UUID成功零覆盖证据；参考答案的不同UUID数和必要请求将在本轮程序统计。旧全量/批量路径不能用于v2；不以额度耗尽产生低分。历史答案含143个不同UUID；仅必需成功零覆盖核对已需143次单UUID请求。

### CG

Find the vulnerable configuration criteria with no dictionary coverage among CVEs whose published timestamp falls on 17 November 2003 UTC. Use the current published field, not the year in the identifier or a reconstruction of the records in 2003. Do not exclude a CVE based on its status. The reference records were observed on 11–13 September 2026; record actual access dates separately and disclose relevant source changes.

A result must satisfy all three conditions: it occurs anywhere in a CVE's configurations with vulnerable=true; the Match Criteria record for that exact matchCriteriaId is Active; and a successful Official CPE Dictionary query for that exact UUID returns totalResults=0. Deprecated dictionary entries count as coverage.

Keep the full identity (CVE ID, matchCriteriaId, criteria), including version boundaries when matching records. Deduplicate repeated occurrences within a CVE, but keep the same UUID in different CVEs as separate rows. Similar or overlapping criteria do not share coverage automatically.

A nonempty matches list establishes coverage. An empty or missing list does not establish zero coverage. Failed requests, mismatched identities and conflicting revisions remain unresolved. Return all qualifying identities, with no top-k limit.

Suggested approach: Find the full daily intake and its vulnerable criteria; follow discovered UUIDs to their Active status; verify each proposed zero using an exact-UUID dictionary response; then deduplicate within each CVE.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Return only a pipe-separated table with the header cve_id|matchCriteriaId|criteria and one row per qualifying identity. Use the full CVE ID, uppercase hyphenated UUID, and exact complete criteria string. Sort ascending by cve_id, then matchCriteriaId, then criteria, using case-sensitive lexicographic order. Return every qualifying identity; there is no top-k limit or tie truncation. Do not add columns, Markdown fences, or commentary. If the verified result is empty, return the single line NONE instead of a header or table.

### GO

Find the vulnerable configuration criteria with no dictionary coverage among CVEs whose published timestamp falls on 17 November 2003 UTC. Use the current published field, not the year in the identifier or a reconstruction of the records in 2003. Do not exclude a CVE based on its status. The reference records were observed on 11–13 September 2026; record actual access dates separately and disclose relevant source changes.

A result must satisfy all three conditions: it occurs anywhere in a CVE's configurations with vulnerable=true; the Match Criteria record for that exact matchCriteriaId is Active; and a successful Official CPE Dictionary query for that exact UUID returns totalResults=0. Deprecated dictionary entries count as coverage.

Keep the full identity (CVE ID, matchCriteriaId, criteria), including version boundaries when matching records. Deduplicate repeated occurrences within a CVE, but keep the same UUID in different CVEs as separate rows. Similar or overlapping criteria do not share coverage automatically.

A nonempty matches list establishes coverage. An empty or missing list does not establish zero coverage. Failed requests, mismatched identities and conflicting revisions remain unresolved. Return all qualifying identities, with no top-k limit.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Return only a pipe-separated table with the header cve_id|matchCriteriaId|criteria and one row per qualifying identity. Use the full CVE ID, uppercase hyphenated UUID, and exact complete criteria string. Sort ascending by cve_id, then matchCriteriaId, then criteria, using case-sensitive lexicographic order. Return every qualifying identity; there is no top-k limit or tie truncation. Do not add columns, Markdown fences, or commentary. If the verified result is empty, return the single line NONE instead of a header or table.

## europemc_reuse_deposit_001 / polish01

状态：ready；完整10篇索引候选与原范围一致，9篇XML逐字相同，种子和大学公开稿可访问；从本轮原件及原语义注释重算得到同一答案。旧补充材料审查复用，不宣称重新独立语义审计。

### CG

Which later articles reused the expression matrices from the 2019 single-cell atlas of entorhinal cortex in Alzheimer's disease and also reported new experimental data deposited in GEO?

Use the biomedical literature catalogue as observed on 9 September 2026. Define the candidate articles by these catalogue fields: ACCESSION_ID matches the atlas cohort's GEO series; FIRST_PDATE is between 2020-01-01 and 2021-12-31 inclusive; and OPEN_ACCESS is Y. Use FIRST_PDATE rather than substituting an article's displayed publication date. The seed atlas need only have a publicly readable data-availability statement; the open-access filter applies to the later articles.

An article qualifies only if it actually reanalysed the cohort's single-cell or single-nucleus expression matrices. Computational method benchmarks count. Merely citing the atlas or using its published differential-expression gene lists does not count.

Report a GEO series only if it contains experimental data newly generated by the later study. Reused datasets, purely computational derivatives and deposits in other repositories do not qualify. Check the methods, data-availability statements and relevant supplements. Return every qualifying article–series pair.

Suggested approach: Find the atlas data-availability statement, use its cohort accession in the catalogue query with the stated filters, then assess each returned article for matrix reuse and newly generated GEO data.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Return only a pipe-separated table with header pmcid|new_geo_series. Use one row per distinct article–series pair, canonical PMC and GSE identifiers, and ascending lexical order by pmcid then new_geo_series.

### GO

Which later articles reused the expression matrices from the 2019 single-cell atlas of entorhinal cortex in Alzheimer's disease and also reported new experimental data deposited in GEO?

Use the biomedical literature catalogue as observed on 9 September 2026. Define the candidate articles by these catalogue fields: ACCESSION_ID matches the atlas cohort's GEO series; FIRST_PDATE is between 2020-01-01 and 2021-12-31 inclusive; and OPEN_ACCESS is Y. Use FIRST_PDATE rather than substituting an article's displayed publication date. The seed atlas need only have a publicly readable data-availability statement; the open-access filter applies to the later articles.

An article qualifies only if it actually reanalysed the cohort's single-cell or single-nucleus expression matrices. Computational method benchmarks count. Merely citing the atlas or using its published differential-expression gene lists does not count.

Report a GEO series only if it contains experimental data newly generated by the later study. Reused datasets, purely computational derivatives and deposits in other repositories do not qualify. Check the methods, data-availability statements and relevant supplements. Return every qualifying article–series pair.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Return only a pipe-separated table with header pmcid|new_geo_series. Use one row per distinct article–series pair, canonical PMC and GSE identifiers, and ascending lexical order by pmcid then new_geo_series.

## genome_002 / polish01

状态：blocked；已澄清专门图范围并修正标识/输出格式；普通GENOME记录和模块可读，但联合图入口（包括源页面真实链接及旧成功路径）现为HTTP 400。最后native web访问旧合法路径收到明确non-retryable拒绝，之后不重试或换表示。联合状态证据未能确认，不测。

### CG

For a lecture on animal endosymbiosis, find the qualifying species-level host–symbiont example in the KEGG GENOME page's examples. Taxonomic-group examples are outside this species-level scope.

The bacterial symbiont's GENOME entry must have Created year 2005 or earlier and list named extra replicons. A replicon qualifies when its name refers to an amino acid whose biosynthesis is represented by a module on the combined host–symbiont pathway map.

For every qualifying example, list its pathway–module–replicon combinations. Include only specific amino-acid biosynthesis pathway maps. Exclude global or overview metabolic maps, broad secondary-metabolite maps and degradation pathways, even if they display the same module. The Created year refers to the bacterial GENOME entry, not the host or module.

Suggested approach: Find the species-level examples, inspect each bacterial GENOME entry for its Created year and replicons, then use the discovered host–symbiont combination to inspect its specific biosynthesis maps and modules.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Return a pipe-separated table with header group|symbiont|pathway|module|replicon|created_year, one combination per row, sorted by pathway ID. Write group as host-code+symbiont-code, symbiont as its organism code, pathway as five digits without map, module as its M identifier, replicon with its source spelling, and Created year as an integer. Return NONE if no combination qualifies.

### GO

For a lecture on animal endosymbiosis, find the qualifying species-level host–symbiont example in the KEGG GENOME page's examples. Taxonomic-group examples are outside this species-level scope.

The bacterial symbiont's GENOME entry must have Created year 2005 or earlier and list named extra replicons. A replicon qualifies when its name refers to an amino acid whose biosynthesis is represented by a module on the combined host–symbiont pathway map.

For every qualifying example, list its pathway–module–replicon combinations. Include only specific amino-acid biosynthesis pathway maps. Exclude global or overview metabolic maps, broad secondary-metabolite maps and degradation pathways, even if they display the same module. The Created year refers to the bacterial GENOME entry, not the host or module.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Return a pipe-separated table with header group|symbiont|pathway|module|replicon|created_year, one combination per row, sorted by pathway ID. Write group as host-code+symbiont-code, symbiont as its organism code, pathway as five digits without map, module as its M identifier, replicon with its source spelling, and Created year as an integer. Return NONE if no combination qualifies.

## kegg_initial_cdx_001 / polish01

状态：blocked；原题措辞和评分输出已修正，但本轮FDA关键历史文件返回HTTP 404的abuse-detection/excessive-requests拦截页；不换工具绕过。现有私有缓存不能替代盲解可达来源，因此本轮不测。

### CG

Build a historical list of genomic companion-diagnostic eligibility for protein kinase inhibitors first approved by the FDA in 2023 and classified under an ATC code beginning L01E. Use approval and classification information available through 9 September 2026.

Include a drug only if an FDA-approved companion diagnostic covered its initial indication on the date of its first drug approval. Use the original drug label, including corrections effective for that approval, and the historical diagnostic approval or supplement applicable to that indication.

For each qualifying drug–gene pair, report the approved ingredient form (preserving salts and hydrates), gene, reference transcript for individually named amino-acid substitutions, complete named substitution set, and any additional eligible open-ended alteration classes. Combine applicable diagnostics for the same initial indication and approval date.

This is an inventory of the diagnostic definition's named substitutions and specific class names. The cited definition retains their biological qualifications. You do not need to reconstruct every prescribing condition, specimen requirement, assay parameter or hypothetical variant. Report specific eligible classes rather than broad assay headings; do not turn examples within a class into extra classes.

Do not substitute whole-panel coverage, drug targets, biomarkers for earlier treatments, later indications or general assay detection capabilities for the original drug-specific eligibility.

Suggested approach: Identify the full approval/classification scope; use each first approval date and initial indication to select the applicable historical diagnostic approval; then follow it to the detailed genomic definition.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Return a pipe-separated table with header drug|biomarker|reference_transcript|named_substitutions|additional_classes. Use one row per drug–gene pairing, sorted by drug and then gene. Use standard gene symbols. Give transcript accessions exactly as stated, including a version only if the definition supplies one; use NONE when no individually named substitutions are enumerated. Write substitutions in bare one-letter amino-acid notation without a p. prefix, as an unordered comma-, semicolon-, or whitespace-separated list; use NONE when there are none. For additional_classes, use the source's full class names in singular form, omitting introductory 'any' and generic suffixes 'mutation', 'alteration', or 'event'; replace internal spaces and hyphens with underscores so each class is one list token. Separate class tokens with commas, semicolons, or whitespace, in any order; use NONE when there are no additional classes. Keep cells on one line. Put citations identifying the historical diagnostic definition and original approval/indication evidence in the separate evidence field, outside final_answer. The cited definitions retain all their qualifications; the table is a classification inventory, not a standalone prescribing rule.

### GO

Build a historical list of genomic companion-diagnostic eligibility for protein kinase inhibitors first approved by the FDA in 2023 and classified under an ATC code beginning L01E. Use approval and classification information available through 9 September 2026.

Include a drug only if an FDA-approved companion diagnostic covered its initial indication on the date of its first drug approval. Use the original drug label, including corrections effective for that approval, and the historical diagnostic approval or supplement applicable to that indication.

For each qualifying drug–gene pair, report the approved ingredient form (preserving salts and hydrates), gene, reference transcript for individually named amino-acid substitutions, complete named substitution set, and any additional eligible open-ended alteration classes. Combine applicable diagnostics for the same initial indication and approval date.

This is an inventory of the diagnostic definition's named substitutions and specific class names. The cited definition retains their biological qualifications. You do not need to reconstruct every prescribing condition, specimen requirement, assay parameter or hypothetical variant. Report specific eligible classes rather than broad assay headings; do not turn examples within a class into extra classes.

Do not substitute whole-panel coverage, drug targets, biomarkers for earlier treatments, later indications or general assay detection capabilities for the original drug-specific eligibility.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Return a pipe-separated table with header drug|biomarker|reference_transcript|named_substitutions|additional_classes. Use one row per drug–gene pairing, sorted by drug and then gene. Use standard gene symbols. Give transcript accessions exactly as stated, including a version only if the definition supplies one; use NONE when no individually named substitutions are enumerated. Write substitutions in bare one-letter amino-acid notation without a p. prefix, as an unordered comma-, semicolon-, or whitespace-separated list; use NONE when there are none. For additional_classes, use the source's full class names in singular form, omitting introductory 'any' and generic suffixes 'mutation', 'alteration', or 'event'; replace internal spaces and hyphens with underscores so each class is one list token. Separate class tokens with commas, semicolons, or whitespace, in any order; use NONE when there are no additional classes. Keep cells on one line. Put citations identifying the historical diagnostic definition and original approval/indication evidence in the separate evidence field, outside final_answer. The cited definitions retain all their qualifications; the table is a classification inventory, not a standalone prescribing rule.

## nvd_initial_assessment_001 / polish01

状态：blocked；旧完整44个CVE历史包含按每页20条计算至少63页，尚未包含发现与当前状态查询。旧联合历史批量响应禁止；未证明其他60请求内完整合法路径。

### CG

Audit changes to NIST's CVSS v3.1 assessments of Apache HTTP Server vulnerabilities first published from 1 January 2020 through 31 December 2023 inclusive. Use catalogue records as observed on 9 September 2026 and the catalogue publication timestamp, not the year in a CVE identifier.

Include only records whose current configurations mark an Apache HTTP Server CPE match as vulnerable. An environment-only, non-vulnerable match does not qualify.

For each record, compare the NIST CVSS v3.1 base vector added by the earliest NIST Initial Analysis event with the current NIST v3.1 base vector. Both must exist and their base metric values must differ. Ignore display prefixes and assessments from CNAs or other contributors.

Report the CVE ID, the base score calculated from the initial vector, the current NIST base score, and the UTC date of the first later NIST history event that actually changed the base vector. NIST Reanalysis and Modified Analysis count when they change it. Reference edits, CPE changes and other contributors' additions do not.

Suggested approach: Establish the product/publication scope, distinguish vulnerable product matches from environment matches, then follow the CVE identities into their NIST analysis histories to compare vectors and locate the first actual revision.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Return only a pipe-separated table with header cve_id|initial_base_score|current_base_score|first_revision_date. Use standard CVE identifiers, decimal base scores and YYYY-MM-DD dates. Sort rows lexicographically by cve_id.

### GO

Audit changes to NIST's CVSS v3.1 assessments of Apache HTTP Server vulnerabilities first published from 1 January 2020 through 31 December 2023 inclusive. Use catalogue records as observed on 9 September 2026 and the catalogue publication timestamp, not the year in a CVE identifier.

Include only records whose current configurations mark an Apache HTTP Server CPE match as vulnerable. An environment-only, non-vulnerable match does not qualify.

For each record, compare the NIST CVSS v3.1 base vector added by the earliest NIST Initial Analysis event with the current NIST v3.1 base vector. Both must exist and their base metric values must differ. Ignore display prefixes and assessments from CNAs or other contributors.

Report the CVE ID, the base score calculated from the initial vector, the current NIST base score, and the UTC date of the first later NIST history event that actually changed the base vector. NIST Reanalysis and Modified Analysis count when they change it. Reference edits, CPE changes and other contributors' additions do not.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Return only a pipe-separated table with header cve_id|initial_base_score|current_base_score|first_revision_date. Use standard CVE identifiers, decimal base scores and YYYY-MM-DD dates. Sort rows lexicographically by cve_id.

## reptile_001 / polish01

状态：blocked；已澄清最近旧属名称和现代印度边界，但原8行答案的完整性及这些修订下的纳排尚未得到完整证据支持；保留公开答案暴露史。不得仅修改措辞后沿用未核实oracle。

### CG

Compile a historical-name concordance for snake species recorded in Boulenger's 1890 The Fauna of British India, Including Ceylon and Burma.

Include a current Reptile Database entry only if its genus differs from the name used in the book, its species page retains BMNH type-specimen information, and its type locality lies in present-day India. A distribution in India is not enough.

For each species, choose the most recently dated historical binomial listed on its current page that still uses a different genus from the accepted name. Check whether an exact search for that full historical name returns only this species (UNIQUE) or multiple records (AMBIG). Record the BMNH type status. If the dated synonymy does not uniquely determine the old label, report the ambiguity rather than guessing.

Suggested approach: Establish the book-based species scope, match current database entries and their type localities, select the last dated name before the current genus, then inspect the exact-name search results.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Output the results as a single line sorted alphabetically by current accepted name, in the format <accepted name>|<old label>|<UNIQUE/AMBIG>|<BMNH status>; separate entries with semicolons. If no qualifying entries exist, output NONE.

### GO

Compile a historical-name concordance for snake species recorded in Boulenger's 1890 The Fauna of British India, Including Ceylon and Burma.

Include a current Reptile Database entry only if its genus differs from the name used in the book, its species page retains BMNH type-specimen information, and its type locality lies in present-day India. A distribution in India is not enough.

For each species, choose the most recently dated historical binomial listed on its current page that still uses a different genus from the accepted name. Check whether an exact search for that full historical name returns only this species (UNIQUE) or multiple records (AMBIG). Record the BMNH type status. If the dated synonymy does not uniquely determine the old label, report the ambiguity rather than guessing.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Output the results as a single line sorted alphabetically by current accepted name, in the format <accepted name>|<old label>|<UNIQUE/AMBIG>|<BMNH status>; separate entries with semicolons. If no qualifying entries exist, output NONE.

## stap_replication_protocol_001 / polish01

状态：ready；完整49条索引记录与原记录一致，16篇纳排/答案关键全文逐字相同，离线原参考程序重算3行一致。语义注释复用，不冒称人类复审。

### CG

Which studies tried to reproduce STAP-cell induction by briefly exposing somatic cells to low pH? Summarize each study’s own procedure, marker findings and functional evidence.

Use the public European index of life-science publications and archived full text. The reference scope is its citing-publication records marked open access, observed on 13 September 2026 (UTC); this is the reference observation date, not your actual access date, for the January 2014 Nature experimental article introducing stimulus-triggered conversion of somatic cells into pluripotency. Use that original experimental article, not its retraction notice or the companion article about bidirectional developmental potential. This is an audit of that indexed open-access cohort, not every freely readable paper or all worldwide citations.

Include a citing publication only if it reports its own experimental attempt to induce STAP-like pluripotency in somatic cells by transient low-pH treatment. Include unsuccessful, partial and modified-protocol attempts, even if they stopped at marker testing. Exclude reviews, news, commentary, computational reanalysis and reports of others' experiments unless the publication also reports its own qualifying attempt. Chronic acidic-culture studies, other chemical stresses and maintenance of existing stem cells do not qualify. Use each main article's observed version; peer-review comments and experiments merely cited by the article are not that study's results.

Record the study's own described procedure, including the relevant changes it reports. This is an audit of author-reported methods, not a certification that every step faithfully reproduced the original protocol. For the procedure summary, cover only the acidifying agents, use of FGF2 after treatment, CD45 sorting in the described spleen-cell preparation, and an explicitly reported difference in the Oct4-GFP reporter line from the original study. Only the fields defined below are requested.

Use these PROCEDURE tags when supported by the reported methods:
- HCL or ATP: that agent was used to create the transient low-pH condition; include both if both were tested.
- FGF2: FGF2 was included in at least one post-treatment culture condition.
- CD45_SORTED or CD45_UNSORTED: the described spleen-cell preparation did or did not include selection of CD45-positive cells by sorting. Density separation alone is not CD45 sorting. Use CD45_UNCLEAR if this cannot be determined, or NO_SPLEEN if no spleen cells were used.
- REPORTER_DIFFERENT: the authors explicitly identify their Oct4-GFP reporter mouse line as different from that of the original report. Do not use a constitutive lineage-tracing GFP line to decide this tag.

In MARKERS, use NEGATIVE if the reported induction assays found no convincing pluripotency-marker induction; RARE_POSITIVE if rare cells or aggregates had reported molecular marker evidence, even if preliminary or most assays were negative; POSITIVE for convincing marker induction not described as rare; UNCLEAR for an unresolved signal without supporting molecular marker evidence; or NOT_REPORTED. Green fluorescence alone is not proof of endogenous pluripotency-marker induction, and markers alone do not establish functional pluripotency.

In FUNCTIONAL_EVIDENCE, report four tags for the same study's treated cells:
- CHIMERA_POSITIVE or CHIMERA_NEGATIVE for observed contribution or no significant contribution after embryo injection; CHIMERA_NOT_PERFORMED if explicitly not done; CHIMERA_NOT_REPORTED if the article gives no such assay result or statement.
- TERATOMA_POSITIVE or TERATOMA_NEGATIVE for a reported teratoma pluripotency assay; TERATOMA_NOT_PERFORMED if explicitly not done; TERATOMA_NOT_REPORTED if unstated. Tumor growth alone without differentiation evidence is not a positive teratoma pluripotency assay.
- LINES_ESTABLISHED or LINES_FAILED for successful or unsuccessful derivation of stable secondary STAP-related stem-cell lines; LINES_NOT_ATTEMPTED if explicitly not attempted; LINES_NOT_REPORTED if unstated. Transient aggregates or short-lived colonies are not stable cell lines.
- PLURIPOTENCY_ESTABLISHED or PLURIPOTENCY_NOT_ESTABLISHED according to whether the study establishes functional pluripotency of its induced cells under its tested conditions. Preserve the distinction between a negative assay, an explicitly unperformed assay and an unreported assay; do not convert any of these into a universal claim that induction is impossible.

Do not infer missing experiments or treat a positive control as successful induction. If a required source or the complete indexed cohort cannot be resolved, return UNRESOLVED rather than guess.

Suggested approach: Identify the original experimental article and its indexed open-access citing records; inspect the potentially eligible studies’ own experiments; then distinguish marker signals from functional pluripotency evidence.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Return only a pipe-separated table with header PMID|PROCEDURE|MARKERS|FUNCTIONAL_EVIDENCE. Give one row per eligible publication, sorted by numeric PMID ascending. PROCEDURE is the set of applicable tags above, separated by semicolons; MARKERS is one tag; FUNCTIONAL_EVIDENCE contains one CHIMERA tag, one TERATOMA tag, one LINES tag and one PLURIPOTENCY tag. Tag order within a cell does not matter. Use the numeric publication identifier, not a full-text archive identifier. If no publication qualifies, return NONE without a header. If required evidence is unresolved, return UNRESOLVED without a header.

### GO

Which studies tried to reproduce STAP-cell induction by briefly exposing somatic cells to low pH? Summarize each study’s own procedure, marker findings and functional evidence.

Use the public European index of life-science publications and archived full text. The reference scope is its citing-publication records marked open access, observed on 13 September 2026 (UTC); this is the reference observation date, not your actual access date, for the January 2014 Nature experimental article introducing stimulus-triggered conversion of somatic cells into pluripotency. Use that original experimental article, not its retraction notice or the companion article about bidirectional developmental potential. This is an audit of that indexed open-access cohort, not every freely readable paper or all worldwide citations.

Include a citing publication only if it reports its own experimental attempt to induce STAP-like pluripotency in somatic cells by transient low-pH treatment. Include unsuccessful, partial and modified-protocol attempts, even if they stopped at marker testing. Exclude reviews, news, commentary, computational reanalysis and reports of others' experiments unless the publication also reports its own qualifying attempt. Chronic acidic-culture studies, other chemical stresses and maintenance of existing stem cells do not qualify. Use each main article's observed version; peer-review comments and experiments merely cited by the article are not that study's results.

Record the study's own described procedure, including the relevant changes it reports. This is an audit of author-reported methods, not a certification that every step faithfully reproduced the original protocol. For the procedure summary, cover only the acidifying agents, use of FGF2 after treatment, CD45 sorting in the described spleen-cell preparation, and an explicitly reported difference in the Oct4-GFP reporter line from the original study. Only the fields defined below are requested.

Use these PROCEDURE tags when supported by the reported methods:
- HCL or ATP: that agent was used to create the transient low-pH condition; include both if both were tested.
- FGF2: FGF2 was included in at least one post-treatment culture condition.
- CD45_SORTED or CD45_UNSORTED: the described spleen-cell preparation did or did not include selection of CD45-positive cells by sorting. Density separation alone is not CD45 sorting. Use CD45_UNCLEAR if this cannot be determined, or NO_SPLEEN if no spleen cells were used.
- REPORTER_DIFFERENT: the authors explicitly identify their Oct4-GFP reporter mouse line as different from that of the original report. Do not use a constitutive lineage-tracing GFP line to decide this tag.

In MARKERS, use NEGATIVE if the reported induction assays found no convincing pluripotency-marker induction; RARE_POSITIVE if rare cells or aggregates had reported molecular marker evidence, even if preliminary or most assays were negative; POSITIVE for convincing marker induction not described as rare; UNCLEAR for an unresolved signal without supporting molecular marker evidence; or NOT_REPORTED. Green fluorescence alone is not proof of endogenous pluripotency-marker induction, and markers alone do not establish functional pluripotency.

In FUNCTIONAL_EVIDENCE, report four tags for the same study's treated cells:
- CHIMERA_POSITIVE or CHIMERA_NEGATIVE for observed contribution or no significant contribution after embryo injection; CHIMERA_NOT_PERFORMED if explicitly not done; CHIMERA_NOT_REPORTED if the article gives no such assay result or statement.
- TERATOMA_POSITIVE or TERATOMA_NEGATIVE for a reported teratoma pluripotency assay; TERATOMA_NOT_PERFORMED if explicitly not done; TERATOMA_NOT_REPORTED if unstated. Tumor growth alone without differentiation evidence is not a positive teratoma pluripotency assay.
- LINES_ESTABLISHED or LINES_FAILED for successful or unsuccessful derivation of stable secondary STAP-related stem-cell lines; LINES_NOT_ATTEMPTED if explicitly not attempted; LINES_NOT_REPORTED if unstated. Transient aggregates or short-lived colonies are not stable cell lines.
- PLURIPOTENCY_ESTABLISHED or PLURIPOTENCY_NOT_ESTABLISHED according to whether the study establishes functional pluripotency of its induced cells under its tested conditions. Preserve the distinction between a negative assay, an explicitly unperformed assay and an unreported assay; do not convert any of these into a universal claim that induction is impossible.

Do not infer missing experiments or treat a positive control as successful induction. If a required source or the complete indexed cohort cannot be resolved, return UNRESOLVED rather than guess.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Return only a pipe-separated table with header PMID|PROCEDURE|MARKERS|FUNCTIONAL_EVIDENCE. Give one row per eligible publication, sorted by numeric PMID ascending. PROCEDURE is the set of applicable tags above, separated by semicolons; MARKERS is one tag; FUNCTIONAL_EVIDENCE contains one CHIMERA tag, one TERATOMA tag, one LINES tag and one PLURIPOTENCY tag. Tag order within a cell does not matter. Use the numeric publication identifier, not a full-text archive identifier. If no publication qualifies, return NONE without a header. If required evidence is unresolved, return UNRESOLVED without a header.

## wateroffice_002 / polish01

状态：blocked；可按旧审查修正排序和CG/GO条件，但本轮关键08EE004 Flow可用性页面被web明确拒绝为non-retryable。未重试或换工具；当前可访问性未确认，不启动盲测绕过该阻塞。

### CG

Check whether Bulkley River mainstem stations between Houston and Hazelton have complete daily flow records for April–July in both 1948 and 1950.

The candidate set is the Historical Results list restricted to stations on this mainstem reach whose summary date span covers both years and whose summary carries a Flow label. This preliminary label alone does not prove that the target years have flow records.

For each candidate, check the target years in the station's detailed availability tables. Use PASS if all eight target months have complete daily flow (C); LEVEL_ONLY if the target years have water-level records but no daily flow; and FLOW_GAP if flow exists but any target month is incomplete. Map PASS to KEEP and the other two statuses to REJECT. Missing or inaccessible evidence is unresolved, not FLOW_GAP.

List every candidate, including rejected ones, from downstream to upstream, with ranks beginning at 1.

Suggested approach: Find the preliminary candidates in Historical Results, inspect each station’s Flow and Level availability by year and month, and establish their river order from station metadata.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Output a table in downstream-to-upstream order with columns rank|station_number|target_window_status|final_verdict.

### GO

Check whether Bulkley River mainstem stations between Houston and Hazelton have complete daily flow records for April–July in both 1948 and 1950.

The candidate set is the Historical Results list restricted to stations on this mainstem reach whose summary date span covers both years and whose summary carries a Flow label. This preliminary label alone does not prove that the target years have flow records.

For each candidate, check the target years in the station's detailed availability tables. Use PASS if all eight target months have complete daily flow (C); LEVEL_ONLY if the target years have water-level records but no daily flow; and FLOW_GAP if flow exists but any target month is incomplete. Map PASS to KEEP and the other two statuses to REJECT. Missing or inaccessible evidence is unresolved, not FLOW_GAP.

List every candidate, including rejected ones, from downstream to upstream, with ranks beginning at 1.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

Output a table in downstream-to-upstream order with columns rank|station_number|target_window_status|final_verdict.

## waterquality_003 / polish01

状态：blocked；已证实同HUC多个合格站点；没有公开唯一择优规则。不能为保住原三行答案事后挑选规则；当前修订明确欠定，旧oracle只保留为历史附件，不作为本轮金标准。

### CG

Select one long-term water-quality reference station in each of HUC 12060202, 12070101 and 12070104, along the Brazos River mainstem downstream of Brazos Rv at Waco, TX.

Each station must be a TCEQ monitoring location whose detail page gives the type River/Stream and whose name identifies the Brazos mainstem rather than a tributary or another waterbody. Each of these five characteristic groups must have a start year no later than 2012 and an end year no earlier than 2018: Inorganics, Major, Non-metals; Microbiological; Nutrient; Organics, Other; Physical. These summary spans do not imply observations in every intervening year.

The common start year is the latest of the five group start years. Report the selected station and all five start years, in upstream-to-downstream order. If more than one station qualifies in a HUC, report that the selection is underdetermined: the original task supplies no tie-breaker. Do not assume that one preferred reference station is the only valid answer.

Suggested approach: Identify mainstem candidates in each HUC, inspect each station’s five group spans, then calculate the common start year and check whether the station choice is unique.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

List the 3 results in order from upstream to downstream, each row formatted as: <HUC>|<MonitoringLocationIdentifier>|<earliest year when all five categories are jointly available>|<Inorganics, Major, Non-metals start year>|<Microbiological start year>|<Nutrient start year>|<Organics, Other start year>|<Physical start year>.

### GO

Select one long-term water-quality reference station in each of HUC 12060202, 12070101 and 12070104, along the Brazos River mainstem downstream of Brazos Rv at Waco, TX.

Each station must be a TCEQ monitoring location whose detail page gives the type River/Stream and whose name identifies the Brazos mainstem rather than a tributary or another waterbody. Each of these five characteristic groups must have a start year no later than 2012 and an end year no earlier than 2018: Inorganics, Major, Non-metals; Microbiological; Nutrient; Organics, Other; Physical. These summary spans do not imply observations in every intervening year.

The common start year is the latest of the five group start years. Report the selected station and all five start years, in upstream-to-downstream order. If more than one station qualifies in a HUC, report that the selection is underdetermined: the original task supplies no tie-breaker. Do not assume that one preferred reference station is the only valid answer.

Follow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.

List the 3 results in order from upstream to downstream, each row formatted as: <HUC>|<MonitoringLocationIdentifier>|<earliest year when all five categories are jointly available>|<Inorganics, Major, Non-metals start year>|<Microbiological start year>|<Nutrient start year>|<Organics, Other start year>|<Physical start year>.
