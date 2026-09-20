#!/usr/bin/env python3
"""Rebuild a finite registered diazepam target-attribution audit from original JSON.
Standard library only. No network, fitted answer counts, or solver invocation.
Constructor annotations document interpretation of uncurated descriptions and
explicit engineered targets; they are not a claim of independent human review.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlparse

CATEGORIES = ['DIRECT_COMPLEX','HOMOLOGOUS_COMPLEX','COMPLEX_GROUP',
              'GABA_SUBUNIT','TSPO','UNCURATED_GABA_BZD','OTHER']
FAMILIES = {'alpha':0,'beta':1,'gamma':2,'delta':3,'epsilon':4,'pi':5,'theta':6}
SPECIES = {'human':'Homo sapiens','rat':'Rattus norvegicus','bovine':'Bos taurus',
           'mouse':'Mus musculus'}

def require(ok, msg):
    if not ok: raise ValueError(msg)

def write(path, value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def complete(data, plural, key):
    rows=data[plural]; meta=data['page_meta']
    require(meta['next'] is None and meta['offset']==0 and len(rows)==meta['total_count'],
            'Incomplete '+plural+' response')
    require(len({r[key] for r in rows})==len(rows),'Duplicate '+key)
    return rows

def sorted_subunits(values):
    def key(v):
        m=re.fullmatch(r'(alpha|beta|gamma|delta|epsilon|pi|theta)(\d*)',v)
        require(m is not None,'Unknown GABA component label '+v)
        return FAMILIES[m[1]],int(m[2] or 0)
    return sorted(set(values),key=key)

def component_subunits(target):
    values=[]
    for c in target['target_components']:
        m=re.fullmatch(r'Gamma-aminobutyric acid receptor subunit (alpha|beta|gamma|delta|epsilon|pi|theta)-?(\d*)',c['component_description'])
        if m is None: return None
        values.append(m[1]+m[2])
    return sorted_subunits(values) if values else None

def described_subunits(text):
    """Extract explicit subunit kinds; alternatives/chimeras remain unresolvable."""
    normalized=text.lower().translate(str.maketrans({'α':'alpha','β':'beta','γ':'gamma'}))
    if re.search(r'(?:alpha|beta|gamma)-?\d+\s*/\s*\d+',normalized) or 'chimer' in normalized:
        return None
    vals=sorted_subunits(a+b for a,b in re.findall(r'(alpha|beta|gamma)[ -]?(\d+)',normalized))
    if len(vals)!=3 or {re.sub(r'\d+','',v) for v in vals}!={'alpha','beta','gamma'}:
        return None
    return vals

def described_species(text):
    # Host names after expressed/in cell wording do not set protein provenance.
    before_host=re.split(r'\bexpressed\b|\bco-expressed\b',text,flags=re.I)[0]
    if described_subunits(before_host) is None:
        return 'UNKNOWN'
    # Require species to modify a receptor/subunit description directly.
    # "bovine brain membranes" and "mouse LTK cells" alone do not qualify.
    pattern=r'\b(human|rat|bovine|mouse)(?:\s+(?:recombinant|chimeric))?\s+(?:GABA|gamma-aminobutyric|alpha[- ]?\d)'
    m=re.search(pattern,before_host,re.I)
    return SPECIES[m[1].lower()] if m else 'UNKNOWN'

def identity(species,subunits):
    return species+' '+ '/'.join(subunits)

def run(manifest_path,out_dir,observation='initial'):
    manifest=json.loads(manifest_path.read_text());base=manifest_path.parent
    entries={e['role']:e for e in manifest['sources'] if 'role' in e}
    def load(role): return json.loads((base/entries[role]['path']).read_text())
    identity_rows=complete(load('compound_identity'),'molecules','molecule_chembl_id')
    require(len(identity_rows)==1 and identity_rows[0]['pref_name'].casefold()=='diazepam',
            'Preferred-name diazepam record is not unique')
    compound=identity_rows[0]['molecule_chembl_id']
    require(parse_qs(urlparse(entries['compound_identity']['url']).query).get('pref_name__iexact')==['diazepam'],
            'Compound identity query does not match public preferred-name scope')
    require(compound==manifest['compound_id'],'Compound manifest disagrees with source identity')
    suffix='' if observation=='initial' else '_refresh'
    raw_a=load('activities'+suffix);raw_s=load('assays'+suffix);raw_t=load('targets'+suffix)
    activities=complete(raw_a,'activities','activity_id')
    assays=complete(raw_s,'assays','assay_chembl_id');targets=complete(raw_t,'targets','target_chembl_id')
    source=load('literature_source');status=load('version')
    require(source['src_description']=='Scientific Literature','Unexpected literature source')
    require(status['chembl_db_version']==manifest['source_release'],'Unexpected release')
    q=parse_qs(urlparse(entries['activities'+suffix]['url']).query)
    require(q.get('molecule_chembl_id')==[compound],'Compound scope differs')
    for key,val in [('standard_type','Ki'),('standard_units','nM'),('standard_relation','='),('assay_type','B')]:
        require(q.get(key)==[val],'Missing requested scope '+key)
        require(all(x[key]==val for x in activities),'Response predicate differs '+key)
    require(all(x['molecule_chembl_id']==compound and x['molecule_pref_name']=='DIAZEPAM' for x in activities),'Molecule identity mismatch')
    scope=[x for x in activities if x['src_id']==source['src_id']]
    excluded=[{'activity_id':x['activity_id'],'src_id':x['src_id'],'reason':'Source is not Scientific Literature'} for x in activities if x not in scope]
    aidx={x['activity_id']:i for i,x in enumerate(activities)}
    sb={x['assay_chembl_id']:x for x in assays};tb={x['target_chembl_id']:x for x in targets}
    require(set(sb)=={x['assay_chembl_id'] for x in scope},'Assay ID closure differs')
    require(set(tb)=={x['target_chembl_id'] for x in scope},'Target ID closure differs')
    for role,field,values in [('assays','assay_chembl_id__in',set(sb)),('targets','target_chembl_id__in',set(tb))]:
        params=parse_qs(urlparse(entries[role+suffix]['url']).query)
        require(set(params[field][0].split(','))==values,'Follow-up query is not activity-derived '+role)
    reviews=json.loads((base/manifest['annotation_path']).read_text())
    uncurated=reviews['uncurated_description_interpretations'];variants=reviews['engineered_target_interpretations']
    require(set(map(int,uncurated))=={x['activity_id'] for x in scope if tb[x['target_chembl_id']]['target_type']=='UNCHECKED'},'Uncurated review does not cover the complete set')
    require(set(map(int,variants))=={x['activity_id'] for x in scope if re.search(r'\bmutant\b|\bchimeric\b',x['assay_description'],re.I)},'Explicit engineering markers differ; interpretation review required')
    cbr=load('cbr_document')
    require('central benzodiazepine receptor (CBR)' in cbr['abstract'],'CBR expansion original unavailable')
    inventory=[];counts=Counter();conflicts=[];engineered=[]
    for x in sorted(scope,key=lambda r:r['activity_id']):
        assay=sb[x['assay_chembl_id']];target=tb[x['target_chembl_id']]
        require(x['target_chembl_id']==assay['target_chembl_id'] and x['assay_description']==assay['description'],'Activity-assay link differs')
        typ=target['target_type'];rel=assay['relationship_type'];components=target['target_components']
        kinds=component_subunits(target);description=x['assay_description']
        review=None
        if kinds is not None and typ=='PROTEIN COMPLEX':
            require(all(c['relationship']=='PROTEIN SUBUNIT' for c in components),'Complex components are not subunits')
            require(rel in ['D','H'],'Uncovered complex attribution relationship')
            require(assay['confidence_score']=={'D':7,'H':6}[rel],'Complex confidence interpretation differs')
            category='DIRECT_COMPLEX' if rel=='D' else 'HOMOLOGOUS_COMPLEX'
            reason=assay['confidence_description']+'; component relationships are PROTEIN SUBUNIT, identifying subunit kinds without stoichiometry.'
        elif kinds is not None and typ=='PROTEIN COMPLEX GROUP':
            require(all(c['relationship']=='GROUP MEMBER' for c in components),'Group components are not group members')
            category='COMPLEX_GROUP';reason='GABA-A complex group with GROUP MEMBER relationships; not a coexisting subunit combination, regardless of D/H.'
        elif kinds is not None and typ=='SINGLE PROTEIN':
            require(len(components)==1 and components[0]['relationship']=='SINGLE PROTEIN','Unexpected GABA subunit registration')
            category='GABA_SUBUNIT';reason='One GABA-A subunit identity is registered; any additional description subunits do not complete registered complex attribution.'
        elif typ=='SINGLE PROTEIN' and len(components)==1 and components[0]['component_description']=='Translocator protein':
            category='TSPO';reason='Registered translocator protein; kept separate from GABA-A even if the assay uses only a broad BzR label.'
        elif typ=='UNCHECKED':
            review=uncurated[str(x['activity_id'])]
            require(review['quote'] in description,'Reviewed uncurated quote changed')
            if review.get('document_evidence'):
                require(x['document_chembl_id']==cbr['document_chembl_id'],'CBR context belongs to another paper')
            category='UNCURATED_GABA_BZD' if review['scope']=='GABA_BZD' else 'OTHER'
            reason=review['reason']+' Target remains UNCHECKED/U; the description does not upgrade registry attribution.'
        else:
            category='OTHER';reason='Registered components identify '+target['pref_name']+', outside GABA-A, benzodiazepine-site and TSPO identity classes.'
        counts[category]+=1
        variant=variants.get(str(x['activity_id']))
        if variant:
            require(variant['quote'] in description,'Reviewed engineered-target quote changed')
            engineered.append(x['activity_id'])
        desc_kinds=described_subunits(description)
        conflict=bool(typ=='PROTEIN COMPLEX' and kinds is not None and desc_kinds is not None and kinds!=desc_kinds)
        desc_taxon=described_species(description)
        finding=None
        if conflict:
            finding=identity(desc_taxon,desc_kinds)+' -> '+identity(target['organism'],kinds)
            conflicts.append({'activity_id':x['activity_id'],'finding':finding,'description_subunits':desc_kinds,'registered_subunits':kinds,'assay_id':x['assay_chembl_id'],'target_id':x['target_chembl_id']})
        inventory.append({'activity_id':x['activity_id'],'assay_id':x['assay_chembl_id'],'target_id':x['target_chembl_id'],'document_id':x['document_chembl_id'],
          'category':category,'category_reason':reason,'description':description,'target_name':target['pref_name'],'target_type':typ,'registered_target_species':target['organism'],
          'assay_organism_not_assumed_target_origin':assay['assay_organism'],'assay_relationship':rel,'assay_relationship_description':assay['relationship_description'],'assay_confidence':assay['confidence_score'],'assay_confidence_description':assay['confidence_description'],
          'component_evidence':[{'description':c['component_description'],'relationship':c['relationship'],'component_id':c['component_id']} for c in components],
          'registered_subunit_kinds':kinds,'unambiguous_described_subunit_kinds':desc_kinds,'described_protein_species':desc_taxon,
          'explicit_engineered_target':bool(variant),'engineering_review':variant,'explicit_subunit_conflict':conflict,'conflict_finding':finding,'uncurated_review':review,
          'numeric_fields':{k:x[k] for k in ['type','relation','value','upper_value','units','standard_type','standard_relation','standard_value','standard_upper_value','standard_units']},
          'potential_duplicate_retained':x['potential_duplicate'],'source_locator':{'activity':entries['activities'+suffix]['path']+'#/activities/'+str(aidx[x['activity_id']]),'assay':entries['assays'+suffix]['path']+'#assay_chembl_id='+x['assay_chembl_id'],'target':entries['targets'+suffix]['path']+'#target_chembl_id='+x['target_chembl_id']}})
    require(sum(counts.values())==len(scope),'Categories are not a partition')
    rows=[[c,str(counts[c])] for c in CATEGORIES]+[['ENGINEERED_VARIANT',str(len(engineered))]]+[[str(c['activity_id']),c['finding']] for c in conflicts]
    out_dir.mkdir(parents=True,exist_ok=True)
    (out_dir/'oracle.psv').write_text('ITEM|FINDING\n'+''.join('|'.join(r)+'\n' for r in rows))
    write(out_dir/'inventory.json',inventory)
    (out_dir/'candidate_universe.jsonl').write_text(''.join(json.dumps({'activity_id':x['activity_id'],'included':x['src_id']==source['src_id'],'src_id':x['src_id'],'reason':'All standard-field predicates verified; '+('Scientific Literature source' if x['src_id']==source['src_id'] else 'different source')},ensure_ascii=False)+'\n' for x in activities))
    report={'observation':observation,'compound_identity':{'record':compound,'preferred_name':identity_rows[0]['pref_name'],'hierarchy':identity_rows[0]['molecule_hierarchy'],'complete_preferred_name_results':len(identity_rows),'scope':'This one registered compound, not expanded parent-family/salt/metabolite inventory'},'source_release':status['chembl_db_version'],'prepared_date_field':status['chembl_release_date'],'release_issued_month':'2026-05','initial_query_rows':len(activities),'in_scope_activity_rows':len(scope),'distinct_assays':len(sb),'distinct_targets':len(tb),'distinct_documents':len({x['document_chembl_id'] for x in scope}),'excluded_by_source':excluded,'category_counts':dict(counts),'engineered_variant_activity_ids':engineered,'conflicts':conflicts,'answer_rows':len(rows),'answer_fields':len(rows)*2,'numeric_audit':{'raw_type_counts':dict(Counter(x['type'] for x in scope)),'raw_unit_counts':dict(Counter(str(x['units']) for x in scope)),'raw_relations':dict(Counter(str(x['relation']) for x in scope)),'non_null_raw_upper_values':[x['activity_id'] for x in scope if x['upper_value'] is not None],'non_null_standard_upper_values':[x['activity_id'] for x in scope if x['standard_upper_value'] is not None],'interpretation':'Scope follows standard registered fields, including converted original pKi/unit representations; does not assert point estimates from relation alone or independent experiments.'},'complete_activity_assay_target_closure':True,'constructor_semantic_annotations':'All uncurated descriptions and explicit engineered targets reviewed by constructor; no independent human validation claimed.'}
    write(out_dir/'scope_checks.json',report)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,default=Path(__file__).with_name('source_manifest.json'));p.add_argument('--out-dir',type=Path,required=True);p.add_argument('--observation',choices=['initial','refresh'],default='initial');a=p.parse_args()
    r=run(a.manifest.resolve(),a.out_dir.resolve(),a.observation)
    print(json.dumps({k:r[k] for k in ['in_scope_activity_rows','distinct_assays','distinct_targets','category_counts','answer_rows','numeric_audit']},ensure_ascii=False))
