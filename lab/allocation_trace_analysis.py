"""D83 selected-removal diagnostics, not a return or lifetime-value estimate. No simulation."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import pickle
import time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'lab/v/allocation_trace_analysis'
RAW=ROOT/'lab/v/allocation_trace.pkl'


def describe(values):
    a=np.array(values,dtype=float)
    if not len(a):return dict(n=0)
    return dict(n=len(a),mean=float(a.mean()),minimum=float(a.min()),median=float(np.median(a)),
                q90=float(np.quantile(a,.9)),maximum=float(a.max()))


def rank(a):
    order=np.argsort(a,kind='stable');out=np.empty(len(a),float)
    i=0
    while i<len(order):
        j=i+1
        while j<len(order) and a[order[j]]==a[order[i]]:j+=1
        out[order[i:j]]=(i+j-1)/2
        i=j
    return out


def summarize(rows):
    out=dict(removal_transactions=len(rows),removed_units=sum(r['group_size'] for r in rows))
    for k in ('current_speaker_deleted','issued_speaker_deleted','speaker_changed','raw_probability_changed',
              'awake_to_silent','silent_to_awake','both_awake_choice_changed','without_birth_in_same_learn'):
        out[k]=sum(bool(r[k]) for r in rows)
    out['effective_abs_dp']=describe([r['effective_abs_dp'] for r in rows])
    out['victim_age_s']=describe([r['unit']['age_s'] for r in rows])
    out['victim_use_decayed']=describe([r['unit']['use_decayed'] for r in rows])
    out['victim_evidence_count']=describe([sum(r['unit']['counts']) for r in rows])
    out['victims_with_exactly_one_tally']=sum(sum(r['unit']['counts'])==1 for r in rows)
    out['stored_stream_share']=describe([r['weight_share'] for r in rows])
    labelled=[r for r in rows if r['diagnostic_loss_delta'] is not None]
    d=[r['diagnostic_loss_delta'] for r in labelled]
    out['conditional_stream_loss_diagnostic']=dict(n=len(d),sum_bits=float(sum(d)),absolute_sum_bits=float(sum(abs(x) for x in d)),
        positive=sum(x>1e-12 for x in d),negative=sum(x< -1e-12 for x in d),within_1e_12=sum(abs(x)<=1e-12 for x in d),
        maximum_absolute=max([abs(x) for x in d],default=0.))
    a=rank(np.array([r['weight_share'] for r in rows]));b=rank(np.array([r['effective_abs_dp'] for r in rows]))
    out['selected_victim_weight_share_vs_disturbance_spearman']=(float(np.corrcoef(a,b)[0,1])
        if len(rows)>2 and np.std(a)>0 and np.std(b)>0 else None)
    return out


def main():
    start=time.monotonic()
    data=pickle.loads(RAW.read_bytes());s,raw=data['summary'],data['raw']
    assert 'failure' not in s and all(s['identity'].values())
    source_checks={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in s['provenance']['source_sha256'].items()}
    assert all(source_checks.values()),source_checks
    assert hashlib.sha256((ROOT/'lab/v/issued_credit_compare.json').read_bytes()).hexdigest()==s['provenance']['baseline_sha256']
    contests,removals,learns=raw['contests'],raw['removals'],raw['learns']
    assert all(c['verified'] for c in contests)
    assert len(contests)==s['alloc']['contests'] and sum(c['won'] for c in contests)==s['alloc']['won']
    assert sum(len(l['adds']) for l in learns)==raw['counters']['add_calls']==s['result'][6][2]
    assert s['alloc']['fixed']+raw['counters']['add_calls']-len(removals)==s['alloc']['cap']
    groups={}
    for r in removals:groups.setdefault(r['group'],[]).append(r)
    roots=[]
    for g,rr in groups.items():
        r=dict(rr[0]);assert r['before'] is not None and r['after'] is not None
        a,b=r['before'],r['after'];ids={z['unit']['id'] for z in rr}
        r['group_size']=len(rr)
        r['current_speaker_deleted']=a['speaker'] is not None and a['speaker'] in ids
        r['issued_speaker_deleted']=any(z['issued_speaker'] for z in rr)
        r['speaker_changed']=a['speaker']!=b['speaker']
        r['raw_probability_changed']=(a['p0'],a['p1'])!=(b['p0'],b['p1'])
        r['awake_to_silent']=a['p1'] is not None and b['p1'] is None
        r['silent_to_awake']=a['p1'] is None and b['p1'] is not None
        r['both_awake_choice_changed']=a['choice'] is not None and b['choice'] is not None and a['choice']!=b['choice']
        # Silence is completed with the unchanged current default only for this labelled diagnostic.
        pa=r['default_p1'] if a['p1'] is None else a['p1']
        pb=r['default_p1'] if b['p1'] is None else b['p1']
        r['effective_abs_dp']=abs(pb-pa)
        if r['letter'] is None:r['diagnostic_loss_delta']=None
        else:
            q0,q1=(pa,pb) if r['letter'] else (1-pa,1-pb)
            r['diagnostic_loss_delta']=-math.log2(max(q1,1e-12))+math.log2(max(q0,1e-12))
        r['weight_share']=r['stream_weight']/r['stored_weight_total']
        r['without_birth_in_same_learn']=r['learn'] is not None and not learns[r['learn']]['adds']
        roots.append(r)
    by_reason={k:summarize([r for r in roots if r['reason']==k]) for k in sorted({r['reason'] for r in roots})}
    by_stage={k:summarize([r for r in roots if r['stage']==k]) for k in sorted({r['stage'] for r in roots})}
    by_reason_stage={f'{reason}/{stage}':summarize([r for r in roots if (r['reason'],r['stage'])==(reason,stage)])
        for reason,stage in sorted({(r['reason'],r['stage']) for r in roots})}
    birth_status={}
    for reason in ('contest_transfer','own_recycling'):
        birth_status[reason]={}
        for birth in (False,True):
            rr=[r for r in roots if r['reason']==reason and r['without_birth_in_same_learn']==(not birth)]
            birth_status[reason]['with_birth' if birth else 'without_birth']=summarize(rr)
    lrem=[l for l in learns if l['removals']]
    lnone=[l for l in lrem if not l['adds']]
    born={(a['stream'],a['id']):l for l in learns for a in l['adds']}
    newborn=[]
    for r in roots:
        birth=born.get((r['stream'],r['unit']['id']))
        if birth is not None and birth['taste']==r['taste']:
            assert birth['t']==r['t'] and birth['id']<r['learn']
            newborn.append(r)
    newborn_ids={r['id'] for r in newborn}
    older_transfers=[r for r in roots if r['reason']=='contest_transfer' and r['id'] not in newborn_ids]
    no_birth_by_reason={reason:dict(Counter(learns[r['learn']]['no_birth_diagnostic'] for r in roots
        if r['reason']==reason and r['without_birth_in_same_learn'])) for reason in ('contest_transfer','own_recycling')}
    out=dict(provenance=dict(analysis_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        raw_pickle=str(RAW),raw_sha256=hashlib.sha256(RAW.read_bytes()).hexdigest(),source_checks=source_checks,
        baseline_identity=s['identity'],simulation_wall_s=s['wall_s']),
        totals=dict(learn_calls=len(learns),learn_calls_with_removals=len(lrem),removing_learns_with_addition=sum(bool(l['adds']) for l in lrem),
            removing_learns_without_addition=len(lnone),no_birth_diagnostics=dict(Counter(l['no_birth_diagnostic'] for l in lnone)),
            additions=sum(len(l['adds']) for l in learns),removed_units=len(removals),removal_transactions=len(roots),
            contest_attempts=len(contests),won_contests=sum(c['won'] for c in contests),
            verified_room_rng_states=raw['counters']['verified_room_rng_states']),
        same_taste_birth_then_removal=summarize(newborn),
        transfers_other_than_same_taste_newborn=summarize(older_transfers),
        no_birth_diagnostics_by_reason=no_birth_by_reason,
        deepest_firing_unit_at_donor_removal_recorded=False,
        no_prediction_between_same_taste_birth_and_removal_basis='Exact add-ID/taste/learn-call linkage plus frozen native taste calls predict only after its sequential learn loop; no per-call prediction timestamps recorded by this observer.',
        all_transactions=summarize(roots),by_reason=by_reason,by_stage=by_stage,by_reason_stage=by_reason_stage,
        by_reason_birth_status=birth_status,
        windows=[dict(window=[lo,hi],summary=summarize([r for r in roots if lo<=r['t']<hi])) for lo,hi in ((0,30),(30,100),(100,200),(200,300))],
        no_birth_examples=[dict(learn=l['id'],t=l['t'],stream=raw['names'][l['stream']],reason=l['no_birth_diagnostic'],
            removal_ids=l['removals']) for l in lnone[:5]],
        limits=['One reused corrected contest life; no fresh-performance or generality test.',
            'Conditional deletion events are selected after seeing feedback, even when donor tallies are not yet updated.',
            'Before/after probes use the current context; silence is completed by current default for diagnostic loss only.',
            'Stage-specific summed loss is not an unbiased prequential mixture loss, action effect or lifetime memory value.',
            'Correlations among selected victims do not establish unbiased ranking of candidate deletion costs.',
            'A unit with zero own/use or initial tally can inherit trace/history; these fields do not establish past uselessness.'])
    out['analysis_wall_s']=time.monotonic()-start
    BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('windows','by_reason_stage','by_reason_birth_status')},indent=2))


if __name__=='__main__':main()
