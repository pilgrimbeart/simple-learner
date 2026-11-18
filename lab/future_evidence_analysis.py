"""D84 exact All-Net history/firing validation and purely offline deleted-unit replay.
External timeout240s, one maths thread. No fitting, learning, or ghost feedback.
"""
from bisect import bisect_left
from collections import Counter
import hashlib
import json
from pathlib import Path
import pickle
import sys
import time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'lab'),str(ROOT)]
from future_evidence import write_history,signature,activates,native_expression_fires
BASE=ROOT/'lab/v/future_evidence_analysis'
RAW=ROOT/'lab/v/future_evidence.pkl'
HORIZON=100.


def family(name):
    return 'integrator' if name.startswith('lb') else 'rhythm' if name.startswith('rt') else 'clock' if name.startswith('clock') else 'event'


def closure(defs,k,memo):
    if k in memo:return memo[k]
    d=defs[k]
    result={k} if d['sym'] is not None else {k}|closure(defs,d['u'],memo)|closure(defs,d['v'],memo)
    memo[k]=result;return result


def validate_history(raw):
    """Every native prelearn living/firing set is the independent live positive control."""
    assert all(c=='Net' for c in raw['classes'])
    defs=[{k:r['definition'] for k,r in ds.items()} for ds in raw['definitions']]
    words=[{} for ds in defs]
    for j,ds in enumerate(defs):
        for k in ds:signature(ds,k,words[j])
    hist=[dict(h) for h in raw['initial_histories']];versions=[0]*len(hist);calls=[0]*len(hist)
    contexts=[[] for h in hist];deaths=[];checked_units=0;checked_contexts=0
    for e in raw['events']:
        if e['kind']=='write':
            j=e['stream'];changed=write_history(hist[j],e['i'],e['sym'],e['keep'],raw['hist_limit'])
            versions[j]+=int(changed);calls[j]+=1
            assert changed==e['changed'] and versions[j]==e['version']
        elif e['kind']=='learn':
            j=e['stream'];assert versions[j]==e['version'] and calls[j]==e['write_call']
            assert all(raw['definitions'][j][k]['birth_seq']<e['seq'] for k in e['living'])
            fired={k for k in e['living'] if activates(words[j][k],hist[j],e['i'])}
            assert fired==set(e['firing']),('Native firing mismatch',e['seq'],fired^set(e['firing']))
            # Second implementation checks recursive parent semantics too, not just a flattened test.
            memo={};recursive={k for k in e['living'] if native_expression_fires(defs[j],k,hist[j],e['i'],memo)}
            assert recursive==fired
            contexts[j].append(dict(e,hist=dict(hist[j]),living_words={words[j][k] for k in e['living']}))
            checked_units+=len(e['living']);checked_contexts+=1
        elif e['kind']=='remove':deaths.append(e)
    assert checked_contexts==raw['counters']['learn_calls']
    return defs,words,contexts,deaths,dict(native_learn_contexts=checked_contexts,native_living_unit_evaluations=checked_units,
        native_history_writes=raw['counters']['write_calls'],all_firing_sets_exact=True,recursive_and_word_models_exact=True)


def replay_candidates(raw,defs,words,contexts,deaths):
    positions=raw['prediction_positions'];assert positions==sorted(positions)
    death_seq={(e['stream'],e['k']):e['seq'] for e in deaths}
    closure_cache=[{} for d in defs];results=[]
    for e in deaths:
        if sum(e['counts'])!=1:continue
        j,k=e['stream'],e['k'];d=raw['definitions'][j][k];word=words[j][k]
        assert defs[j][k]['sym'] is None,'Fixed units should not be removed'
        retained=closure(defs[j],k,closure_cache[j])
        grown={a for a in retained if defs[j][a]['sym'] is None}
        born=d['birth_seq'];remaining=300.-e['t']
        assert remaining>=-1e-10
        r=dict(stream=j,name=raw['names'][j],family=family(raw['names'][j]),k=k,word=word,
            death_t=e['t'],death_seq=e['seq'],remaining_s=max(0.,remaining),span=len(word),
            same_taste_birth=d['birth_taste'] is not None and d['birth_taste']==e['taste'],
            survived_prediction=bisect_left(positions,e['seq'])>bisect_left(positions,born),
            actually_spoke=(j,k) in raw['speaking'],closure_grown_units=len(grown),
            future_lessons=0,future_firings=0,future_firings_label_consistent=0,future_firings_with_equivalent=0,
            unchanged_context_firings=0,changed_index_firings=0,new_history_firings=0,first_delay_s=None,
            same_taste_remaining_firings=0,eligible_100s=e['t']<=200.,lessons_100s=0,firings_100s=0,
            firings_100s_with_equivalent=0,first_100s_delay_s=None,max_extra_dead_ancestors_on_firing=0)
        unique_contexts=set();label=int(e['counts'][1]==1)
        for c in contexts[j]:
            if c['seq']<=e['seq']:continue
            hit=activates(word,c['hist'],c['i'])
            if e['taste'] is not None and c['taste']==e['taste']:
                r['same_taste_remaining_firings']+=int(hit)
                continue
            delay=c['t']-e['t'];assert delay>=-1e-12
            r['future_lessons']+=1
            within=delay<=HORIZON
            if r['eligible_100s'] and within:r['lessons_100s']+=1
            if not hit:continue
            r['future_firings']+=1
            r['future_firings_label_consistent']+=int(c['letter']==label)
            represented=word in c['living_words']
            r['future_firings_with_equivalent']+=int(represented)
            r['unchanged_context_firings']+=int(c['i']==e['i'] and c['version']==e['version'])
            r['changed_index_firings']+=int(c['i']!=e['i'])
            r['new_history_firings']+=int(c['version']!=e['version'])
            unique_contexts.add((c['version'],c['i']))
            if r['first_delay_s'] is None:r['first_delay_s']=max(0.,delay)
            extra=sum((j,a) in death_seq and death_seq[j,a]<c['seq'] for a in grown if a!=k)
            r['max_extra_dead_ancestors_on_firing']=max(r['max_extra_dead_ancestors_on_firing'],extra)
            if r['eligible_100s'] and within:
                r['firings_100s']+=1;r['firings_100s_with_equivalent']+=int(represented)
                if r['first_100s_delay_s'] is None:r['first_100s_delay_s']=max(0.,delay)
        r['distinct_firing_contexts']=len(unique_contexts)
        results.append(r)
    return results


def distribution(a):
    a=np.array(a,dtype=float)
    if not len(a):return dict(n=0)
    return dict(n=len(a),minimum=float(a.min()),median=float(np.median(a)),q90=float(np.quantile(a,.9)),maximum=float(a.max()))


def summarize(rows):
    n=len(rows)
    return dict(removed_units=n,distinct_definitions=len({(r['stream'],r['word']) for r in rows}),
        same_taste_birth=sum(r['same_taste_birth'] for r in rows),survived_any_prediction=sum(r['survived_prediction'] for r in rows),
        actually_spoke=sum(r['actually_spoke'] for r in rows),no_later_accepted_lesson=sum(r['future_lessons']==0 for r in rows),
        any_later_firing=sum(r['future_firings']>0 for r in rows),no_later_firing=sum(r['future_firings']==0 for r in rows),
        future_lessons=sum(r['future_lessons'] for r in rows),future_firings=sum(r['future_firings'] for r in rows),
        label_consistent_firings=sum(r['future_firings_label_consistent'] for r in rows),
        firings_with_exact_living_equivalent=sum(r['future_firings_with_equivalent'] for r in rows),
        any_firing_without_exact_living_equivalent=sum(r['future_firings']>r['future_firings_with_equivalent'] for r in rows),
        unchanged_context_firings=sum(r['unchanged_context_firings'] for r in rows),
        changed_index_firings=sum(r['changed_index_firings'] for r in rows),new_history_firings=sum(r['new_history_firings'] for r in rows),
        distinct_firing_contexts=sum(r['distinct_firing_contexts'] for r in rows),
        first_firing_delay_s=distribution([r['first_delay_s'] for r in rows if r['first_delay_s'] is not None]),
        remaining_life_s=distribution([r['remaining_s'] for r in rows]),
        same_taste_remaining_firings=sum(r['same_taste_remaining_firings'] for r in rows),
        closure_grown_units=distribution([r['closure_grown_units'] for r in rows]),
        extra_dead_ancestors_on_later_firing=distribution([r['max_extra_dead_ancestors_on_firing'] for r in rows if r['future_firings']]),
        horizon_100s=dict(eligible_units=sum(r['eligible_100s'] for r in rows),
            no_accepted_lesson=sum(r['eligible_100s'] and not r['lessons_100s'] for r in rows),
            units_with_firing=sum(r['eligible_100s'] and r['firings_100s']>0 for r in rows),
            units_without_firing=sum(r['eligible_100s'] and r['firings_100s']==0 for r in rows),
            future_lessons=sum(r['lessons_100s'] for r in rows),firings=sum(r['firings_100s'] for r in rows),
            firings_with_exact_living_equivalent=sum(r['firings_100s_with_equivalent'] for r in rows)))


def main():
    start=time.monotonic();out=dict(failures=[])
    try:
        data=pickle.loads(RAW.read_bytes());s,raw=data['summary'],data['raw']
        assert 'failure' not in s and all(s['identity'].values())
        for p,h in s['provenance']['source_sha256'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
        defs,words,contexts,deaths,checks=validate_history(raw)
        rows=replay_candidates(raw,defs,words,contexts,deaths)
        out.update(provenance=dict(raw_sha256=hashlib.sha256(RAW.read_bytes()).hexdigest(),raw_path=str(RAW),
            analysis_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            command='timeout --signal=TERM --kill-after=5s 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/future_evidence_analysis.py'),
            validation=checks,full_remaining_life=summarize(rows),
            by_churn={str(c):summarize([r for r in rows if r['same_taste_birth']==c]) for c in (False,True)},
            by_family={f:summarize([r for r in rows if r['family']==f]) for f in ('event','clock','integrator','rhythm')},
            by_remaining_time={f'{lo}-{hi}s':summarize([r for r in rows if lo<=r['remaining_s']<hi]) for lo,hi in ((0,30),(30,100),(100,200),(200,301))},
            samples=[{k:v for k,v in r.items() if k!='word'} for r in rows[:3]],
            limits=['Exact frozen-history activation only; no hypothetical learning or influence on live actions.',
                'Later accepted lessons exclude the same taste. Repeated unchanged contexts remain correlated evidence.',
                'Equivalent words prove identical activation only, not identical prediction counts or unique utility.',
                'Retention includes removed ancestor definitions; per-unit closure costs overlap and are not a matched-cap intervention.',
                'No future firing by life end is censored, especially for late deletions;100s sensitivity includes only deletions by200s.',
                'Label agreement is not information gain, an independence test or reward benefit.'])
        BASE.with_suffix('.pkl').write_bytes(pickle.dumps(dict(unit_results=rows,summary=out)))
        print('VALIDATION',checks,flush=True)
        print('SUMMARY',json.dumps(out['full_remaining_life']),flush=True)
    except Exception as e:
        out['failures'].append(dict(type=type(e).__name__,message=str(e)));raise
    finally:
        out['wall_s']=time.monotonic()-start
        BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
        print('wall_s',out['wall_s'],flush=True)


if __name__=='__main__':main()
