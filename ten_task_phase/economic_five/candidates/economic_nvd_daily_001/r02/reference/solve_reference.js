function solveReference(sourceText, manifest) {
 const RANGES=["versionStartIncluding","versionStartExcluding","versionEndIncluding","versionEndExcluding"];
 const entries=manifest.sources, get=e=>JSON.parse(sourceText[e.path]);
 const canonical=x=>JSON.stringify((function sort(v){if(Array.isArray(v))return v.map(sort);if(v&&typeof v==="object")return Object.fromEntries(Object.keys(v).sort().map(k=>[k,sort(v[k])]));return v;})(x));
 const require=(ok,msg)=>{if(!ok)throw Error(msg);};
 const one=role=>{const r=entries.filter(e=>e.role===role);require(r.length===1,"one "+role);return r[0];};
 const scopeEntry=one("scope"),scope=get(scopeEntry);
 function page(e,key){require(e.status===200,"HTTP "+e.path);const b=get(e);require(b.startIndex===0 && b.resultsPerPage===b[key].length && b.totalResults===b[key].length,"incomplete "+e.path);return b;}
 page(scopeEntry,"vulnerabilities");
 const cvs=scope.vulnerabilities.map(x=>x.cve), cvIds=cvs.map(x=>x.id);require(new Set(cvIds).size===cvIds.length,"duplicate CVE");
 const occ=[], universe=[];
 function walk(x,p,cve){if(Array.isArray(x)){x.forEach((v,i)=>walk(v,p+"["+i+"]",cve));}
 else if(x&&typeof x==="object"){for(const[k,v]of Object.entries(x)){if(k==="cpeMatch"){require(Array.isArray(v),"nonarray cpeMatch");v.forEach((criterion,i)=>occ.push({cve_id:cve,path:p+".cpeMatch["+i+"]",...criterion}));}else walk(v,p+"."+k,cve);}}}
 cvs.forEach((c,i)=>{require(c.published.slice(0,10)===manifest.published_day,"publication scope");const start=occ.length;walk(c.configurations,"$.vulnerabilities["+i+"].cve.configurations",c.id);universe.push({cve_id:c.id,published:c.published,lastModified:c.lastModified,vulnStatus:c.vulnStatus,source:scopeEntry.path,path:"$.vulnerabilities["+i+"].cve",configuration_occurrences:occ.length-start});});
 require((sourceText[scopeEntry.path].match(/"matchCriteriaId"\s*:/g)||[]).length===occ.length,"UUID occurrence coverage");
 const byCve={},byUuid={}, matchRefs={};
 const ident=x=>canonical({criteria:x.criteria,...Object.fromEntries(RANGES.map(k=>[k,x[k]??null]))});
 for(const e of entries.filter(e=>e.role==="match")){
   require(!byCve[e.cve_id],"duplicate CVE batch");const b=page(e,"matchStrings"),items={};
   b.matchStrings.forEach((v,i)=>{const x=v.matchString;require(!items[x.matchCriteriaId],"duplicate match UUID");items[x.matchCriteriaId]=x;matchRefs[e.cve_id+"|"+x.matchCriteriaId]={source:e.path,path:"$.matchStrings["+i+"].matchString"};
     if(byUuid[x.matchCriteriaId])require(canonical(byUuid[x.matchCriteriaId])===canonical(x),"conflicting match snapshots");byUuid[x.matchCriteriaId]=x;});
   const needed=occ.filter(x=>x.cve_id===e.cve_id);
   require(canonical(Object.keys(items).sort())===canonical([...new Set(needed.map(x=>x.matchCriteriaId))].sort()),"by-CVE coverage");
   needed.forEach(x=>require(ident(x)===ident(items[x.matchCriteriaId]),"criterion/range identity"));byCve[e.cve_id]=items;
 }
 require(canonical(Object.keys(byCve).sort())===canonical([...new Set(occ.map(x=>x.cve_id))].sort()),"CVE batch universe");
 const exact={};
 for(const e of entries.filter(e=>e.role==="cpe_zero"||e.role==="cpe_check")){
   require(e.status===200 && e.query.matchCriteriaId[0]===e.uuid,"exact UUID request");
   const b=page(e,"products");require(!exact[e.uuid],"duplicate exact primary query");exact[e.uuid]={entry:e,body:b};
   const x=byUuid[e.uuid];require(x,"extraneous CPE UUID");
   if(x.matches?.length){require(b.totalResults>0,"nonempty matches contradicted");const fromMatch=x.matches.map(m=>m.cpeNameId+"|"+m.cpeName).sort();const fromCpe=b.products.map(m=>m.cpe.cpeNameId+"|"+m.cpe.cpeName).sort();require(canonical(fromMatch)===canonical(fromCpe),"dictionary names differ");}
 }
 const groups={};for(const x of occ){const key=x.cve_id+"|"+x.matchCriteriaId;(groups[key]??=[]).push(x);}
 const ledger=[], evidence=[], oracle=[];
 for(const key of Object.keys(groups).sort()){
   const rows=groups[key], x=rows[0],m=byUuid[x.matchCriteriaId],ref=matchRefs[key];
   require(rows.every(y=>ident(y)===ident(x)),"duplicate config conflict");
   require(rows.every(y=>typeof y.vulnerable==="boolean"),"missing vulnerable flag");
   const vulnerable=rows.some(y=>y.vulnerable===true),active=m?.status==="Active";
   require(m&&["Active","Inactive"].includes(m.status),"unknown status");
   let zero=null,coverageSource=null;
   if(exact[x.matchCriteriaId]){zero=exact[x.matchCriteriaId].body.totalResults===0;coverageSource={source:exact[x.matchCriteriaId].entry.path,path:"$.totalResults",value:exact[x.matchCriteriaId].body.totalResults};}
   else if(m.matches?.length){zero=false;coverageSource={...ref,path:ref.path+".matches",value:m.matches.length,interpretation:"nonempty official dictionary name/ID list proves nonzero, not an exact dictionary count"};}
   require(!vulnerable||!active||zero!==null,"unknown inclusion "+key);
   const included=vulnerable&&active&&zero===true;
   const row={cve_id:x.cve_id,matchCriteriaId:x.matchCriteriaId,criteria:x.criteria,ranges:Object.fromEntries(RANGES.map(k=>[k,x[k]??null])),vulnerable,active,dictionary_zero:zero,included,reason:!vulnerable?"not_vulnerable":!active?"inactive":zero===true?"confirmed_exact_zero":zero===false?"dictionary_present":"unknown",configuration_sources:rows.map(y=>({source:scopeEntry.path,path:y.path})),match_source:ref,coverage_source:coverageSource};
   ledger.push(row);
   evidence.push({row_key:[x.cve_id,x.matchCriteriaId,x.criteria],fields:{cve_id:{source:scopeEntry.path,path:universe.find(c=>c.cve_id===x.cve_id).path+".id"},matchCriteriaId:row.configuration_sources.map(s=>({...s,path:s.path+".matchCriteriaId"})),criteria:row.configuration_sources.map(s=>({...s,path:s.path+".criteria"})),vulnerable:row.configuration_sources.map(s=>({...s,path:s.path+".vulnerable"})),active:{...ref,path:ref.path+".status"},dictionary_zero:coverageSource,included:{input_row_keys:[key],formula:"any(vulnerable === true) AND status === 'Active' AND exact dictionary totalResults === 0"}}});
   if(included)oracle.push({cve_id:x.cve_id,matchCriteriaId:x.matchCriteriaId,criteria:x.criteria});
 }
 const order=(a,b)=>a.cve_id<b.cve_id?-1:a.cve_id>b.cve_id?1:a.matchCriteriaId<b.matchCriteriaId?-1:a.matchCriteriaId>b.matchCriteriaId?1:a.criteria<b.criteria?-1:a.criteria>b.criteria?1:0;
 oracle.sort(order);ledger.sort(order);universe.sort((a,b)=>a.cve_id<b.cve_id?-1:1);
 function parts(s){const out=[];let p="",escaped=false;for(const ch of s){if(ch===":"&&!escaped){out.push(p);p="";}else p+=ch;if(ch==="\\")escaped=!escaped;else escaped=false;}out.push(p);return out;}
 const dropped=[];
 for(const row of ledger.filter(x=>x.included)){
   const p=parts(row.criteria);require(p.length===13,"CPE components");
   if(p[6]==="*")continue;
   const sibling=ledger.find(x=>{if(x.cve_id!==row.cve_id||x.dictionary_zero!==false||canonical(x.ranges)!==canonical(row.ranges))return false;const q=parts(x.criteria);return q[6]==="*"&&p.every((v,i)=>i===6||v===q[i]);});
   if(sibling)dropped.push({row_key:[row.cve_id,row.matchCriteriaId,row.criteria],incorrect_coverage_from:[sibling.cve_id,sibling.matchCriteriaId,sibling.criteria]});
 }
 const crossDropped=[],seen=new Set();for(const r of oracle){if(seen.has(r.matchCriteriaId))crossDropped.push(r);else seen.add(r.matchCriteriaId);}
 const counterfactuals={baseline_rows:oracle.length,patch_overlap:{rule:"Treat an otherwise identical same-CVE criterion with wildcard update and nonzero coverage as covering the update-specific UUID; ranges must be equal.",wrong_rows:oracle.length-dropped.length,removed:dropped},global_uuid_deduplication:{wrong_rows:oracle.length-crossDropped.length,removed:crossDropped},vulnerable_flag:{changes_rows:false,reason:occ.every(x=>x.vulnerable===true)?"All observed occurrences are vulnerable=true; no effectiveness claim.":"Not evaluated here."}};
 for(const e of evidence){
 const c=universe.find(x=>x.cve_id===e.row_key[0]), l=ledger.find(x=>x.cve_id===e.row_key[0]&&x.matchCriteriaId===e.row_key[1]);
 e.fields.published={source:scopeEntry.path,path:c.path+".published",value:c.published,formula:"UTC field date equals "+manifest.published_day};
 e.fields.ranges=Object.fromEntries(RANGES.map(k=>[k,{value:l.ranges[k],configuration_sources:l.configuration_sources.map(s=>({...s,path:s.path+"."+k})),match_source:{...l.match_source,path:l.match_source.path+"."+k},null_meaning:"field absent; no boundary stated"}]));
 }
 const psv=oracle.length?"cve_id|matchCriteriaId|criteria\n"+oracle.map(r=>[r.cve_id,r.matchCriteriaId,r.criteria].join("|")).join("\n")+"\n":"NONE\n";
 require(oracle.every(r=>Object.values(r).every(v=>typeof v==="string"&&v.length&&!/[|\r\n]/.test(v))),"invalid output field");
 return {universe,occurrences:occ,ledger,evidence,oracle,psv,counterfactuals,summary:{cves:universe.length,occurrences:occ.length,unique_uuid:Object.keys(byUuid).length,ledger_rows:ledger.length,oracle_rows:oracle.length,unknown:ledger.filter(x=>x.included===null).length}};
}
