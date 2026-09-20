"""Fixed-instance semantic checks over separately transcribed original fields."""
import json
import re
from decimal import Decimal
from pathlib import Path

def quality(header, target):
    target_parts=target.split(';')
    target_type,target_subtype=target_parts[0].split('/')
    target_params=dict(x.split('=',1) for x in target_parts[1:])
    matches=[]
    for raw in header.split(','):
        parts=[x.strip() for x in raw.split(';')]
        typ,sub=parts[0].split('/')
        params=dict(x.split('=',1) for x in parts[1:])
        q=Decimal(params.pop('q','1'))
        if typ not in ('*',target_type) or sub not in ('*',target_subtype): continue
        if any(target_params.get(k)!=v for k,v in params.items()): continue
        matches.append(((int(typ!='*')+int(sub!='*'),len(params)),q))
    return max(matches)[1]

def has_defect(obs):
    if obs['kind']=='accept_quality':
        assert quality(obs['new_example_header'],obs['media_type'])==Decimal(obs['erratum_corrected_quality'])
        return quality(obs['header'],obs['media_type'])!=Decimal(obs['printed_quality'])
    if obs['kind']=='range_grammar':
        rules=obs['rules']
        assert rules['byte-range-spec']=='first-byte-pos "-" [ last-byte-pos ]'
        assert rules['suffix-byte-range-spec']=='"-" suffix-length'
        assert obs['recipient_list_expansion']=='*( "," OWS ) element *( OWS "," [ OWS element ] )'
        element=r'(?:[0-9]+-[0-9]*|-[0-9]+)'
        ows=r'[ \t]*'
        lst=r'(?:,'+ows+r')*'+element+r'(?:'+ows+r',(?:'+ows+element+r')?)*'
        prefix=re.escape(rules['bytes-unit'].strip('"'))+'='
        rhs=rules['byte-ranges-specifier']
        gap=ows if '"=" OWS' in rhs else ''
        original=bool(re.fullmatch(prefix+gap+lst,obs['witness']))
        repaired=bool(re.fullmatch(prefix+ows+lst,obs['witness']))
        assert repaired
        return not original
    if obs['kind']=='charset_reference':
        header=obs['corrected_header']
        grammars=obs['legacy_header_grammars']
        return (obs['incorrect_new_header'] in obs['legacy_charset_text']
                or 'charset' not in grammars[header]
                or 'charset' in grammars[obs['incorrect_new_header']])
    raise ValueError('Unreviewed observation kind')

def main():
    d=json.loads((Path(__file__).parent/'source_fields.json').read_text())
    records={x['erratum_id']:x for x in d['legacy_observations']}
    candidates=sorted((x for x in d['candidate_catalog'] if x['status']=='Verified' and x['type']=='Technical'),key=lambda x:x['id'])
    print('erratum_id|legacy_rfc|legacy_section|legacy_has_defect')
    for c in candidates:
        o=records[c['id']]
        print('|'.join(map(str,[c['id'],o['legacy_rfc'],o['legacy_section'],'YES' if has_defect(o) else 'NO'])))

if __name__=='__main__': main()
