"""Prepare the user-authorized revision batch. Never starts model sessions."""
import copy, datetime as dt, importlib.util, json
from pathlib import Path

BASE = Path(__file__).resolve().parent
PHASE = BASE.parent
OLD = PHASE / 'rolling_five/retest_31_v2'
IDS = ['arxiv_historical_title_001','arxiv_historical_title_002','economic_kegg_ddi_001','economic_nvd_daily_001','europemc_reuse_deposit_001','genome_002','kegg_initial_cdx_001','nvd_initial_assessment_001','reptile_001','stap_replication_protocol_001','wateroffice_002','waterquality_003']

def save(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')

COMMON = '\n\nFollow the experiment retrieval policy. Put only the requested table in final_answer. Put source URLs and locators in evidence, and incomplete evidence or access problems in limitations. A failed request is not evidence that a record or result does not exist.'
TEXT = {}
STEPS = {}
TEXT['arxiv_historical_title_001'] = '''Find withdrawn preprints first submitted in 2021 (UTC) whose categories include cs.LG, including cross-listings. Use catalogue metadata as observed on 9 September 2026.

For each preprint, its latest recorded version must be withdrawn, and its current notice must explicitly name another archive record as the replacement or continuation of the same work. Supersession, subsumption, mergers, revised resubmissions and corrections of duplicate submissions qualify when the notice names that replacement. Ordinary citations, administrative overlap notices, incoming mergers and active companion papers do not qualify on their own. Follow only the directly named replacement.

Use the submission timestamp of the predecessor's latest withdrawn version as the cutoff. In the replacement's history, select the version with the latest submission timestamp at or before that cutoff. Compare exact UTC submission timestamps, not announcement dates. Omit a relationship if no replacement version existed by the cutoff.

Keep the relationship only if that selected version's title differs in wording from the replacement's current title. Ignore layout whitespace and equivalent mathematical rendering. Return every qualifying relationship.'''
STEPS['arxiv_historical_title_001'] = 'Establish the year/category scope; verify withdrawal and replacement direction; compare the two submission histories; then check the selected historical title against the current title.'
TEXT['arxiv_historical_title_002'] = '''Reconstruct the replacement citations for withdrawn preprints first submitted in 2020 (UTC) whose current categories include cs.LG, including cross-listings. Use public metadata current through 9 September 2026.

Include every direct successor named by the withdrawn source record as its replacement, updated or corrected version, or merger result. A correction redirecting a mistaken separate submission qualifies. Related papers, independently obtained equivalent results and unnamed forthcoming work do not qualify. Successors may belong to any year or category.

For each source–successor relationship, use the source record's last listed submission timestamp as the cutoff. This is a bibliography convention, not the date when withdrawal happened. Select the successor version with the latest submission timestamp at or before the cutoff, and report that version's title. Include all versions tied at that timestamp. Omit a relationship if no successor version existed by the cutoff. Do not filter for title changes.

If a source's last submission is later than 9 September 2026 UTC, report version drift rather than silently changing the cutoff. Return every qualifying relationship.'''
STEPS['arxiv_historical_title_002'] = 'Establish the annual category scope, identify withdrawn records and their directly named successors, then use both submission histories to locate the eligible version and its title.'
TEXT['economic_kegg_ddi_001'] = '''Compile the reported interaction classes between the complete drug groups “Selective serotonin reuptake inhibitor (SSRI)” and “MAO inhibitor” (also called “Monoamine oxidase inhibitors”). The reference observations were made on 11–13 September 2026; this does not require you to pretend that your actual access occurred then. Report any evidence that relevant source records have since changed.

Include every leaf D-number drug entry in both official group records, including nested branches, salts and hydrates. Keep distinct D numbers separate. Do not filter by country tags or common antidepressant use.

Return a cross-group pair if either direction reports CI (contraindication), P (precaution), or both. Merge the two directions into one row, preserving all reported classes. Exclude within-group pairs. Absence from one direction is insufficient to exclude a pair. Only complete successful coverage can establish that no interaction is reported; it does not establish clinical safety.

Return the complete result. If access or conflicting records prevent this, state the limitation and identify the answer as partial.'''
STEPS['economic_kegg_ddi_001'] = 'Discover both complete group memberships, inspect interaction records for the discovered ingredients in both directions, then combine and sort the cross-group pairs.'
TEXT['economic_nvd_daily_001'] = '''Find the vulnerable configuration criteria with no dictionary coverage among CVEs whose published timestamp falls on 17 November 2003 UTC. Use the current published field, not the year in the identifier or a reconstruction of the records in 2003. Do not exclude a CVE based on its status. The reference records were observed on 11–13 September 2026; record actual access dates separately and disclose relevant source changes.

A result must satisfy all three conditions: it occurs anywhere in a CVE's configurations with vulnerable=true; the Match Criteria record for that exact matchCriteriaId is Active; and a successful Official CPE Dictionary query for that exact UUID returns totalResults=0. Deprecated dictionary entries count as coverage.

Keep the full identity (CVE ID, matchCriteriaId, criteria), including version boundaries when matching records. Deduplicate repeated occurrences within a CVE, but keep the same UUID in different CVEs as separate rows. Similar or overlapping criteria do not share coverage automatically.

A nonempty matches list establishes coverage. An empty or missing list does not establish zero coverage. Failed requests, mismatched identities and conflicting revisions remain unresolved. Return all qualifying identities, with no top-k limit.'''
STEPS['economic_nvd_daily_001'] = 'Find the full daily intake and its vulnerable criteria; follow discovered UUIDs to their Active status; verify each proposed zero using an exact-UUID dictionary response; then deduplicate within each CVE.'
TEXT['europemc_reuse_deposit_001'] = '''Which later articles reused the expression matrices from the 2019 single-cell atlas of entorhinal cortex in Alzheimer's disease and also reported new experimental data deposited in GEO?

Use the biomedical literature catalogue as observed on 9 September 2026. Define the candidate articles by these catalogue fields: ACCESSION_ID matches the atlas cohort's GEO series; FIRST_PDATE is between 2020-01-01 and 2021-12-31 inclusive; and OPEN_ACCESS is Y. Use FIRST_PDATE rather than substituting an article's displayed publication date. The seed atlas need only have a publicly readable data-availability statement; the open-access filter applies to the later articles.

An article qualifies only if it actually reanalysed the cohort's single-cell or single-nucleus expression matrices. Computational method benchmarks count. Merely citing the atlas or using its published differential-expression gene lists does not count.

Report a GEO series only if it contains experimental data newly generated by the later study. Reused datasets, purely computational derivatives and deposits in other repositories do not qualify. Check the methods, data-availability statements and relevant supplements. Return every qualifying article–series pair.'''
STEPS['europemc_reuse_deposit_001'] = 'Find the atlas data-availability statement, use its cohort accession in the catalogue query with the stated filters, then assess each returned article for matrix reuse and newly generated GEO data.'
TEXT['genome_002'] = '''For a lecture on animal endosymbiosis, find the qualifying species-level host–symbiont example in the KEGG GENOME page's examples. Taxonomic-group examples are outside this species-level scope.

The bacterial symbiont's GENOME entry must have Created year 2005 or earlier and list named extra replicons. A replicon qualifies when its name refers to an amino acid whose biosynthesis is represented by a module on the combined host–symbiont pathway map.

For every qualifying example, list its pathway–module–replicon combinations. Include only specific amino-acid biosynthesis pathway maps. Exclude global or overview metabolic maps, broad secondary-metabolite maps and degradation pathways, even if they display the same module. The Created year refers to the bacterial GENOME entry, not the host or module.'''
STEPS['genome_002'] = 'Find the species-level examples, inspect each bacterial GENOME entry for its Created year and replicons, then use the discovered host–symbiont combination to inspect its specific biosynthesis maps and modules.'
TEXT['kegg_initial_cdx_001'] = '''Build a historical list of genomic companion-diagnostic eligibility for protein kinase inhibitors first approved by the FDA in 2023 and classified under an ATC code beginning L01E. Use approval and classification information available through 9 September 2026.

Include a drug only if an FDA-approved companion diagnostic covered its initial indication on the date of its first drug approval. Use the original drug label, including corrections effective for that approval, and the historical diagnostic approval or supplement applicable to that indication.

For each qualifying drug–gene pair, report the approved ingredient form (preserving salts and hydrates), gene, reference transcript for individually named amino-acid substitutions, complete named substitution set, and any additional eligible open-ended alteration classes. Combine applicable diagnostics for the same initial indication and approval date.

This is an inventory of the diagnostic definition's named substitutions and specific class names. The cited definition retains their biological qualifications. You do not need to reconstruct every prescribing condition, specimen requirement, assay parameter or hypothetical variant. Report specific eligible classes rather than broad assay headings; do not turn examples within a class into extra classes.

Do not substitute whole-panel coverage, drug targets, biomarkers for earlier treatments, later indications or general assay detection capabilities for the original drug-specific eligibility.'''
STEPS['kegg_initial_cdx_001'] = 'Identify the full approval/classification scope; use each first approval date and initial indication to select the applicable historical diagnostic approval; then follow it to the detailed genomic definition.'
TEXT['nvd_initial_assessment_001'] = '''Audit changes to NIST's CVSS v3.1 assessments of Apache HTTP Server vulnerabilities first published from 1 January 2020 through 31 December 2023 inclusive. Use catalogue records as observed on 9 September 2026 and the catalogue publication timestamp, not the year in a CVE identifier.

Include only records whose current configurations mark an Apache HTTP Server CPE match as vulnerable. An environment-only, non-vulnerable match does not qualify.

For each record, compare the NIST CVSS v3.1 base vector added by the earliest NIST Initial Analysis event with the current NIST v3.1 base vector. Both must exist and their base metric values must differ. Ignore display prefixes and assessments from CNAs or other contributors.

Report the CVE ID, the base score calculated from the initial vector, the current NIST base score, and the UTC date of the first later NIST history event that actually changed the base vector. NIST Reanalysis and Modified Analysis count when they change it. Reference edits, CPE changes and other contributors' additions do not.'''
STEPS['nvd_initial_assessment_001'] = 'Establish the product/publication scope, distinguish vulnerable product matches from environment matches, then follow the CVE identities into their NIST analysis histories to compare vectors and locate the first actual revision.'
TEXT['reptile_001'] = '''Compile a historical-name concordance for snake species recorded in Boulenger's 1890 The Fauna of British India, Including Ceylon and Burma.

Include a current Reptile Database entry only if its genus differs from the name used in the book, its species page retains BMNH type-specimen information, and its type locality lies in present-day India. A distribution in India is not enough.

For each species, choose the most recently dated historical binomial listed on its current page that still uses a different genus from the accepted name. Check whether an exact search for that full historical name returns only this species (UNIQUE) or multiple records (AMBIG). Record the BMNH type status. If the dated synonymy does not uniquely determine the old label, report the ambiguity rather than guessing.'''
STEPS['reptile_001'] = 'Establish the book-based species scope, match current database entries and their type localities, select the last dated name before the current genus, then inspect the exact-name search results.'
TEXT['wateroffice_002'] = '''Check whether Bulkley River mainstem stations between Houston and Hazelton have complete daily flow records for April–July in both 1948 and 1950.

The candidate set is the Historical Results list restricted to stations on this mainstem reach whose summary date span covers both years and whose summary carries a Flow label. This preliminary label alone does not prove that the target years have flow records.

For each candidate, check the target years in the station's detailed availability tables. Use PASS if all eight target months have complete daily flow (C); LEVEL_ONLY if the target years have water-level records but no daily flow; and FLOW_GAP if flow exists but any target month is incomplete. Map PASS to KEEP and the other two statuses to REJECT. Missing or inaccessible evidence is unresolved, not FLOW_GAP.

List every candidate, including rejected ones, from downstream to upstream, with ranks beginning at 1.'''
STEPS['wateroffice_002'] = 'Find the preliminary candidates in Historical Results, inspect each station’s Flow and Level availability by year and month, and establish their river order from station metadata.'
TEXT['waterquality_003'] = '''Select one long-term water-quality reference station in each of HUC 12060202, 12070101 and 12070104, along the Brazos River mainstem downstream of Brazos Rv at Waco, TX.

Each station must be a TCEQ monitoring location whose detail page gives the type River/Stream and whose name identifies the Brazos mainstem rather than a tributary or another waterbody. Each of these five characteristic groups must have a start year no later than 2012 and an end year no earlier than 2018: Inorganics, Major, Non-metals; Microbiological; Nutrient; Organics, Other; Physical. These summary spans do not imply observations in every intervening year.

The common start year is the latest of the five group start years. Report the selected station and all five start years, in upstream-to-downstream order. If more than one station qualifies in a HUC, report that the selection is underdetermined: the original task supplies no tie-breaker. Do not assume that one preferred reference station is the only valid answer.'''
STEPS['waterquality_003'] = 'Identify mainstem candidates in each HUC, inspect each station’s five group spans, then calculate the common start year and check whether the station choice is unique.'

BLOCKED = {
 'arxiv_historical_title_001': ('有界完整路径未证实：旧证据由完整年度语料和705条评论前沿建立范围，再查历史版本。不能把旧全量构造路径直接当作v2盲测路径；未证明60请求/10页内完整替代路径。','candidates/arxiv_historical_title_001/r02/exploration.md'),
 'arxiv_historical_title_002': ('有界完整路径未证实：r03曾需25890条完整处置修复词法筛选漏项。不能直接以关键词搜索代替完整范围证明；未证明当前额度内合法完整路径。','candidates/arxiv_historical_title_002/r03/revision_history.json'),
 'economic_kegg_ddi_001': ('完整已验证单条路径为20+40个端点，尚需组身份/成员发现，超过60请求。仅SSRI端点实测漏14对；完整60-ID导出禁止。历史观测期也不能冒充当前数据。未证明另一完整合法路径。','economic_five/candidates/economic_kegg_ddi_001/r02/reference_report.md'),
 'economic_nvd_daily_001': ('需逐UUID成功零覆盖证据；参考答案的不同UUID数和必要请求将在本轮程序统计。旧全量/批量路径不能用于v2；不以额度耗尽产生低分。','economic_five/candidates/economic_nvd_daily_001/r02/development_decision.json'),
 'nvd_initial_assessment_001': ('旧完整44个CVE历史包含按每页20条计算至少63页，尚未包含发现与当前状态查询。旧联合历史批量响应禁止；未证明其他60请求内完整合法路径。','candidates/nvd_initial_assessment_001/r01/sources/apache_2020_2023_history.response'),
 'reptile_001': ('已澄清最近旧属名称和现代印度边界，但原8行答案的完整性及这些修订下的纳排尚未得到完整证据支持；保留公开答案暴露史。不得仅修改措辞后沿用未核实oracle。','comparisons/reptile_001/error_review.md'),
 'wateroffice_002': ('可按旧审查修正排序和CG/GO条件，但本轮关键08EE004 Flow可用性页面被web明确拒绝为non-retryable。未重试或换工具；当前可访问性未确认，不启动盲测绕过该阻塞。','comparisons/wateroffice_002/error_review.md'),
 'waterquality_003': ('已证实同HUC多个合格站点；没有公开唯一择优规则。不能为保住原三行答案事后挑选规则；当前修订明确欠定，旧oracle只保留为历史附件，不作为本轮金标准。','comparisons/waterquality_003/error_review.md'),
}

def main():
    assert not (BASE/'plan.json').exists(), 'Do not revise a registered batch'
    oldplan=json.loads((OLD/'plan.json').read_text())
    jobs={}
    for j in oldplan['jobs']:
        m=json.loads(Path(j['job_metadata']).read_text())
        if m['candidate_id'] in IDS: jobs[(m['candidate_id'],m['variant'])]=(j,m)
    # Preserve all substantive STAP tag definitions while shortening its framing.
    oldstap=json.loads(Path(jobs[('stap_replication_protocol_001','GO')][0]['public']).read_text())
    st=oldstap['instruction']
    st=st.replace('Audit published attempts to reproduce the claim that a brief low-pH treatment can turn somatic cells into pluripotent STAP cells. I need the procedures actually reported by each study and the evidence supporting its conclusion about pluripotency.', 'Which studies tried to reproduce STAP-cell induction by briefly exposing somatic cells to low pH? Summarize each study’s own procedure, marker findings and functional evidence.')
    st=st.replace('observed on 13 September 2026 (UTC)', 'observed on 13 September 2026 (UTC); this is the reference observation date, not your actual access date')
    st=st.replace('Do not list reagent amounts, durations, animal counts or every technical difference.', 'Only the fields defined below are requested.')
    TEXT['stap_replication_protocol_001']=st
    STEPS['stap_replication_protocol_001']='Identify the original experimental article and its indexed open-access citing records; inspect the potentially eligible studies’ own experiments; then distinguish marker signals from functional pluripotency evidence.'
    reviews=[]
    for cid in IDS:
        j,m=jobs[(cid,'CG')];dest=BASE/'candidates'/cid;dest.mkdir(parents=True,exist_ok=True)
        gold=Path(j['gold']).read_text();rules=json.loads(Path(j['rules']).read_text())
        (dest/'historical_oracle.psv').write_text(gold)
        changes=['按任务、范围、判定条件分段；解释必要术语；CG/GO使用相同实质条件，仅CG增加步骤。','引用和限制放独立字段；删除与v2冲突的批量许可；历史输入不覆盖。']
        fmt=json.loads(Path(j['public']).read_text())['output_format']
        fmt=fmt.replace('Keep cells on one line and put citations after the table, identifying the historical diagnostic definition and original approval/indication evidence.', 'Keep cells on one line. Put citations identifying the historical diagnostic definition and original approval/indication evidence in the separate evidence field, outside final_answer.')
        if cid=='genome_002':
            gold='group|symbiont|pathway|module|replicon|created_year\n'+gold.strip().replace(',','\n')+'\n'
            rules.pop('record_separator',None);rules.pop('source',None)
            rules['fields'].update({'group':{'aliases':{'api buc':'api+buc'}},'pathway':{'aliases':{'map00290':'00290','map00400':'00400'}}})
            fmt='Return a pipe-separated table with header group|symbiont|pathway|module|replicon|created_year, one combination per row, sorted by pathway ID. Write group as host-code+symbiont-code, symbiont as its organism code, pathway as five digits without map, module as its M identifier, replicon with its source spelling, and Created year as an integer. Return NONE if no combination qualifies.'
            changes+=['实质澄清：只取物种级示例、专门氨基酸生物合成图，排除总览图；输出由逗号单行改为表格。','有限等价别名：api buc与api+buc、两个map前缀；不将只有host的缺失身份自动补成正确组合。']
        if cid=='wateroffice_002':
            byid={r.split('|')[1]:r.split('|') for r in gold.splitlines() if r.strip()}
            gold='rank|station_number|target_window_status|final_verdict\n'+'\n'.join('|'.join([str(i)]+byid[s][1:]) for i,s in enumerate(['08EE001','08EE005','08EE004','08EE003'],1))+'\n'
            changes+=['参考排序改为Hazelton→Smithers→Quick→Houston；只据已有源审查修改rank，状态仍为历史参考、未获本轮重新验证。','GO补齐候选窗口、Flow初筛和KEEP/REJECT映射。']
        if cid=='waterquality_003':changes+=['明确原任务欠定；不凭空添加择优规则，不把历史oracle当唯一答案。']
        if cid=='reptile_001':changes+=['实质草稿澄清：最近一次旧属名称、现代印度；参考答案尚未按这些条件核实，不可测试。']
        for variant in ['CG','GO']:
            source=Path(jobs[(cid,variant)][0]['public'])
            save(dest/(variant+'_historical.json'),json.loads(source.read_text()))
            instruction=TEXT[cid]+ ('\n\nSuggested approach: '+STEPS[cid] if variant=='CG' else '')+COMMON
            save(dest/(variant+'.json'),{'instruction':instruction,'output_format':fmt,'current_date':'2026-09-09'})
        save(dest/'rules.json',rules);(dest/'oracle.psv').write_text(gold)
        status='blocked' if cid in BLOCKED else 'pending_preflight'
        reason,evidence=BLOCKED.get(cid,('需完成本轮源与评分核对后才能登记测试。',''))
        review={'candidate_id':cid,'historical_revision':m['revision'],'revision':m['revision']+1,'batch_revision':'polish01','status':status,'reason':reason,'changes':changes,'evidence_paths':[str(PHASE/evidence)] if evidence else [],'historical_inputs':str(Path(j['public']).parent),'independent_human_review':'not_performed','formal_admission':False}
        if cid=='economic_nvd_daily_001':
            count=len({x.split('|')[1] for x in gold.splitlines()[1:] if x.strip()});review['distinct_required_zero_uuids']=count
            review['reason']+=f'历史答案含{count}个不同UUID；仅必需成功零覆盖核对已需{count}次单UUID请求。'
        save(dest/'review.json',review);reviews.append(review)
    save(BASE/'reviews.json',reviews)
    (BASE/'blind.md').write_text('Solve the single public task using the available live web and official-source data tools. Follow the supplied bounded retrieval policy and task output rules. Use current_date as the fixed experiment anchor; historical observation dates explicitly stated in the task are separate, and actual access dates must be truthful. Search, normal bounded pagination, individual records, individual original articles and evidence-dependent follow-up queries are allowed; complete bulk exports are prohibited. Local calculation on lawfully obtained data is allowed. All CSV columns are TEXT: CAST for numeric operations. Put only the requested table in final_answer, citations in evidence and unresolved issues in limitations. Do not retry non-retryable denied resources through another tool or representation. If incomplete, return the actual partial answer without inventing values.\n')
    (BASE/'README.md').write_text('# 12题润色与修复：单轮诊断盲测\n\n用户授权：修订12题，修复已有证据支持的缺陷；每个可测底题CG/GO各一次Sol/medium，最多24次；不执行全局方法/skill整理。\n\n当前为构造侧预检，尚未启动测试。所有候选及受阻原因见reviews.json；候选目录含原题、修订题、原答案、修订参考和变更说明。受阻题的oracle.psv不代表已验证金标准。旧数据和旧阶段用量不修改。\n')
    print(json.dumps({'candidates':len(reviews),'blocked':sum(r['status']=='blocked' for r in reviews),'pending':sum(r['status']=='pending_preflight' for r in reviews)}))

if __name__=='__main__':main()
