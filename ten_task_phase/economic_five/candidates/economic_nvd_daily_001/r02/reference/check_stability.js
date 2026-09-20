function checkStability(sourceText, manifest) {
 const read=e=>JSON.parse(sourceText[e.path]);
 const canon=x=>JSON.stringify((function f(v){if(Array.isArray(v))return v.map(f);if(v&&typeof v==="object")return Object.fromEntries(Object.keys(v).sort().map(k=>[k,f(v[k])]));return v;})(x));
 const req=(b,s)=>{if(!b)throw Error(s);};
 const role=r=>manifest.sources.filter(e=>e.role===r);
 const scope=read(role("scope")[0]);
 const cveMap=b=>Object.fromEntries(b.vulnerabilities.map(x=>[x.cve.id,x.cve]));
 const original=cveMap(scope);
 const rechecks=role("scope_recheck");
 req(rechecks.length===1,"need current scope recheck");
 const re=read(rechecks[0]);req(rechecks[0].status===200&&re.totalResults===re.vulnerabilities.length&&re.startIndex===0,"scope recheck incomplete");
 req(canon(original)===canon(cveMap(re)),"CVE scope or full record changed");
 const wide=role("scope_broad");req(wide.length===1,"need broader independent scope");
 const w=read(wide[0]);req(wide[0].status===200&&w.totalResults===w.vulnerabilities.length&&w.startIndex===0,"broader scope incomplete");
 const chosen={};for(const x of w.vulnerabilities)if(x.cve.published.slice(0,10)===manifest.published_day)chosen[x.cve.id]=x.cve;
 req(canon(chosen)===canon(original),"broad day-filter check differs");
 const uuids=new Set();for(const e of role("match"))for(const x of read(e).matchStrings)uuids.add(x.matchString.matchCriteriaId);
 const delta=role("match_changes").sort((a,b)=>Number(a.query.startIndex[0])-Number(b.query.startIndex[0]));
 req(delta.length>0,"missing revision index");
 let offset=0,total=null,all=[];
 for(const e of delta){const b=read(e);req(e.status===200&&b.startIndex===offset&&b.resultsPerPage===b.matchStrings.length,"revision pagination");
 if(total===null)total=b.totalResults;req(total===b.totalResults,"revision total changed");all.push(...b.matchStrings);offset+=b.matchStrings.length;}
 req(offset===total,"revision index incomplete");
 const relevant=all.filter(x=>uuids.has(x.matchString.matchCriteriaId));
 req(relevant.length===0,"relevant Match/CPE revisions occurred; refresh required");
 const start=delta[0].query.lastModStartDate[0],end=delta[0].query.lastModEndDate[0];
 req(role("scope")[0].requested_at.slice(0,19)>=start.slice(0,19),"change index starts too late");
 let newest="";
 for(const e of role("match"))for(const x of read(e).matchStrings)for(const k of ["created","lastModified","cpeLastModified"]){
 const v=x.matchString[k];if(v){if(v>newest)newest=v;req(v<start,"a primary match already has a revision in the checked interval");}}
 return {scope_records_unchanged:Object.keys(original).length,broader_response_total:w.totalResults,broader_day_count:Object.keys(chosen).length,match_uuids_covered:uuids.size,revision_index_total:total,relevant_revision_rows:relevant.length,revision_index_start:start,revision_index_end:end,newest_primary_match_revision:newest,source_entries:rechecks.concat(wide,delta).map(x=>x.path),interpretation:"Construction-window stability is supported by full current CVE equality and the complete official Match revision index, whose documented fields cover status and relevant dictionary-name changes. This is not a historical replay, a proof excluding all transient changes, or certification of later blind evaluations."};
}
