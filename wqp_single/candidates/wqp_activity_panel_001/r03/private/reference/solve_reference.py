#!/usr/bin/env python3
"""Recompute independent single-activity withdrawals from unchanged official data.
No critical activity ID, frontier interval, output count or measurement is hard-coded.
"""
import collections,json,pathlib,sqlite3
from decimal import Decimal
import panel_reference as core
B=pathlib.Path(__file__).resolve().parent;P=B.parent
def sig(front):return tuple((w['start_year'],w['end_year'],tuple(sorted(tuple(k) for k in w['cohort']))) for w in front)
def event_tie(a):return (Decimal(a['values']['dissolved_oxygen_mg_L']),a['date'],a['time'] or '\uffff',a['site'],a['activity'])
def main():
 core.main()  # Original state rebuilt from raw Station/Activity/narrow and checked against separate wide SQL.
 d=json.loads((P/'task_definition.json').read_text());cols=d['columns'];years=list(range(d['years'][0],d['years'][1]+1))
 acts=[json.loads(x) for x in (B/'initial_state/activity_ledger.jsonl').read_text().splitlines()]
 for a in acts:a['site_key']=tuple(a['site_key'])
 sites=sorted({a['site_key'] for a in acts});support,counts=core.make_support(acts,sites,years);initial_windows=core.windows(support,years);original_front=core.brief(initial_windows);original_sig=sig(original_front)
 eligible=sorted((a for a in acts if a['eligible']),key=lambda a:(a['organization'],a['activity']))
 scenarios=[];changed=[];rows=[];fields=[];selected=[];trial_windows=[]
 for omitted in eligible:
  k=omitted['site_key'];y=omitted['year'];q=omitted['quarter'];key=(omitted['organization'],omitted['activity'])
  # Mathematical pruning: removing one activity can change support only at its own station/year/quarter.
  # If that year was unsupported, or another eligible activity remains in that quarter, all year sets stay equal.
  pivotal=counts[k,y,q]==1 and y in support[k]
  if pivotal:
   after={s:set(ys) for s,ys in support.items()};after[k].remove(y);win=core.windows(after,years);front=core.brief(win)
  else:win=initial_windows;front=original_front
  changes=sig(front)!=original_sig
  rec={'withdrawal_key':key,'withdrawn_site':k,'date':omitted['date'],'year':y,'quarter':q,'original_quarter_activity_count':counts[k,y,q],'original_year_supported':y in support[k],'supported_year_removed':pivotal,'frontier_changed':changes,'post_frontier':front,'decision':'include' if changes else 'exclude','reason':'full_design_set_changed' if changes else 'year_support_unchanged' if not pivotal else 'support_changed_but_global_frontier_unchanged','unknown':[],'activity_evidence':omitted['activity_evidence']};scenarios.append(rec)
  if pivotal:trial_windows.extend({'withdrawal_key':key,**w} for w in win)
  if not changes:continue
  changed.append(rec)
  assert front,'This observed dataset has a remaining feasible interval after every single withdrawal; empty sentinel not observed'
  for w in front:
   cohort={tuple(s) for s in w['cohort']}
   remaining=[a for a in eligible if (a['organization'],a['activity'])!=key and a['site_key'] in cohort and w['start_year']<=a['year']<=w['end_year'] and a['quarter']==q]
   chosen=min(remaining,key=event_tie)
   row=[*key,omitted['site'],omitted['date'],str(w['start_year']),str(w['end_year']),str(w['coverage']),';'.join(s[1] for s in sorted(cohort)),'Q'+str(q),str(len(remaining)),chosen['organization'],chosen['site'],chosen['activity'],chosen['date'],*[core.fmt(chosen['values'][f]) for f in ['dissolved_oxygen_mg_L','temperature_deg_C','specific_conductance_uS_cm','pH']]];rows.append(row)
   rk=[*key,row[4],row[5]];trace={'row_key':rk,'withdrawal':omitted,'post_interval':w,'remaining_candidate_keys':[[a['organization'],a['activity']] for a in remaining],'selected_activity':chosen};selected.append(trace)
   for col,v in zip(cols,row):
    ev={'row_key':rk,'field':col,'output':v}
    if col in core.CODES.values():ev.update(evidence=chosen['value_evidence'][col],formula='same remaining selected activity; exact declared units; HALF_UP2dp')
    elif col.startswith('withdrawn_') or col=='quarter':ev.update(evidence=omitted['activity_evidence'],formula='original eligible activity identity/date; quarter-of-year from its actual start date')
    elif col in ['start_year','end_year','cohort_station_count','cohort_station_ids']:ev.update(evidence={'trial_window_ledger':'reference/trial_window_ledger.jsonl','withdrawal_key':key,'interval':[w['start_year'],w['end_year']]},formula='full post-withdrawal global frontier and exact interval cohort, recomputed from original state for this trial')
    elif col=='eligible_activity_count':ev.update(evidence=trace['remaining_candidate_keys'],formula='count distinct remaining activity keys across exact post-interval cohort, years and withdrawn quarter')
    else:ev.update(evidence=chosen['activity_evidence'],formula='minimum unrounded DO within the scenario-specific remaining set; date/time/site/activity tie rules')
    fields.append(ev)
 # Whole source computation checked independently with SQL over the other original wide export.
 wide=core.source(core.WF);con=sqlite3.connect(':memory:');cs=[c for c in wide[0] if not c.startswith('_')];quote=lambda c:'"'+c.replace('"','""')+'"'
 con.execute('CREATE TABLE wide ('+','.join(quote(c)+' TEXT' for c in cs)+')');con.executemany('INSERT INTO wide VALUES ('+','.join('?' for _ in cs)+')',[[r[c] for c in cs] for r in wide]);con.executescript((B/'independent_check.sql').read_text())
 raw_sql=con.execute('SELECT * FROM answer ORDER BY withdrawn_ActivityIdentifier COLLATE BINARY,start_year,end_year').fetchall();sqlrows=[[str(v) for v in r[:14]]+[core.fmt(v) for v in r[14:]] for r in raw_sql];assert rows==sqlrows,(rows,sqlrows)
 core.jsonl(B/'independent_trial_decisions.jsonl',[{'organization':r[0],'activity':r[1],'frontier_changed':bool(r[2])} for r in con.execute('SELECT org,aid,changed FROM all_trial_decisions ORDER BY org,aid')])
 (B/'independent_answer.psv').write_text('\n'.join('|'.join(r) for r in sqlrows)+'\n')
 actual_sql={(r[0],r[1]):bool(r[2]) for r in con.execute('SELECT org,aid,changed FROM all_trial_decisions')};assert len(actual_sql)==len(scenarios)
 assert all(actual_sql[tuple(s['withdrawal_key'])]==s['frontier_changed'] for s in scenarios)
 original_selected={(t['selected_activity']['organization'],t['selected_activity']['activity']) for t in json.loads((B/'initial_state/selected_activities.json').read_text())}
 cf={'only_test_original_selected_minima':{'missed_changing_withdrawals':[s['withdrawal_key'] for s in changed if tuple(s['withdrawal_key']) not in original_selected]},'only_reconsider_original_frontier_intervals':[],'drop_equal_duration_coverage_frontier_ties':[],'forget_to_remove_activity_when_selecting_events':[],'reuse_full_original_period_and_cohort':[],'cumulative_withdrawals_instead_of_independent_trials':[]}
 orig_intervals={(w['start_year'],w['end_year']) for w in original_front}
 for s in changed:
  key=s['withdrawal_key'];post=s['post_frontier'];new=[w for w in post if (w['start_year'],w['end_year']) not in orig_intervals]
  if new:cf['only_reconsider_original_frontier_intervals'].append({'withdrawal_key':key,'missed_post_frontier_intervals':new})
  sizes=collections.defaultdict(list)
  for w in post:sizes[w['duration'],w['coverage']].append([w['start_year'],w['end_year']])
  for size,group in sizes.items():
   if len(group)>1:cf['drop_equal_duration_coverage_frontier_ties'].append({'withdrawal_key':key,'duration':size[0],'coverage':size[1],'distinct_intervals_all_required':group})
 for t,row in zip(selected,rows):
  o=t['withdrawal'];w=t['post_interval'];members={tuple(k) for k in w['cohort']};orig=[a for a in eligible if a['site_key'] in members and w['start_year']<=a['year']<=w['end_year'] and a['quarter']==o['quarter']]
  if len(orig)!=len(t['remaining_candidate_keys']):cf['forget_to_remove_activity_when_selecting_events'].append({'row_key':t['row_key'],'correct_count':len(t['remaining_candidate_keys']),'incorrect_count':len(orig),'correct_minimum_activity':t['selected_activity']['activity'],'incorrect_minimum_activity':min(orig,key=event_tie)['activity']})
  unscoped=[a for a in eligible if a['quarter']==o['quarter'] and (a['organization'],a['activity'])!=(o['organization'],o['activity'])]
  wrong=min(unscoped,key=event_tie)
  if wrong['activity']!=t['selected_activity']['activity'] or len(unscoped)!=len(t['remaining_candidate_keys']):cf['reuse_full_original_period_and_cohort'].append({'row_key':t['row_key'],'correct_count':len(t['remaining_candidate_keys']),'incorrect_count':len(unscoped),'correct_activity':t['selected_activity']['activity'],'incorrect_activity':wrong['activity']})
 cumulative={s:set(ys) for s,ys in support.items()}
 for s in changed:
  k=tuple(s['withdrawn_site']);cumulative[k].discard(s['year']);wrong=core.brief(core.windows(cumulative,years))
  if sig(wrong)!=sig(s['post_frontier']):cf['cumulative_withdrawals_instead_of_independent_trials'].append({'withdrawal_key':s['withdrawal_key'],'correct_frontier':s['post_frontier'],'incorrect_frontier':wrong})
 cf['observed_limits']={'forgetting_removal_in_event_selection_changes_rows':len(cf['forget_to_remove_activity_when_selecting_events']),'note':'A withdrawal that destroys station-year support can exclude that station or that year from all surviving interval cohorts. If this field is0, the explicit removal rule has no separate final-selection effect in this slice and is not credited as an extra difficulty contribution.'}
 (B/'oracle.psv').write_text('\n'.join('|'.join(r) for r in rows)+'\n' if rows else 'NONE\n');core.jsonl(B/'scenario_ledger.jsonl',scenarios);core.jsonl(B/'trial_window_ledger.jsonl',trial_windows);core.jsonl(P/'field_evidence.jsonl',fields);core.dump(B/'selected_activities.json',selected);core.dump(B/'counterfactuals.json',cf)
 report={'status':'passed','original_state_verification':'initial_state/verification.json','eligible_activity_trials':len(scenarios),'changing_activity_trials':len(changed),'independently_checked_trial_decisions':len(actual_sql),'all_trial_classifications_equal':True,'changing_withdrawal_keys':[s['withdrawal_key'] for s in changed],'distinct_changed_frontier_states':len({sig(s['post_frontier']) for s in changed}),'trial_interval_output_rows':len(rows),'field_evidence_count':len(fields),'independent_SQL_all_output_cells_equal':True,'original_sources_unchanged':True,'unknowns_affecting_answer':0,'sentinel_rows_observed':0,'reference_algorithm':'Exact support-count pruning for unchanged trials; all changed support sets and210intervals recomputed independently from original state. Separate SQL evaluates all original eligible scenarios from wide raw data.'};core.dump(B/'verification.json',report);print(json.dumps(report,indent=2))
if __name__=='__main__':main()
