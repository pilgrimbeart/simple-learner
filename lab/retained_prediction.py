"""D85 causal offline tally reconstruction and per-deleted-unit prediction comparison.
No simulated steps or effect on the living brain. Protocol: discrete/NOTEBOOK.md D85.
"""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import pickle
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'lab'), str(ROOT)]
from future_evidence import signature, activates, write_history
from future_evidence_analysis import family, distribution

BASE = ROOT/'lab/v/retained_prediction'
RAW = ROOT/'lab/v/future_evidence.pkl'


def probability(counts):
    return (counts[1] + .5)/(sum(counts) + 1.)


def speaker(living, words, hist, i):
    best, key = None, None
    for k, counts in living.items():
        if counts[0] == counts[1] or not activates(words[k], hist, i):
            continue
        rank = (len(words[k]), abs(counts[1]-counts[0])/sum(counts))
        if key is None or rank > key:
            best, key = k, rank
    return best


def new_score():
    return dict(n=0, baseline_bits=0., retained_bits=0., mixture_bits=0.,
                baseline_silent=0, baseline_errors=0., retained_errors=0., mixture_errors=0.)


def score_and_update(candidate, baseline_p, label, within, silent=False):
    """Return pre-outcome probabilities; all model writes follow scoring."""
    p = probability(candidate['counts'])
    weight = candidate['weight']
    mix = weight*p + (1-weight)*baseline_p
    likelihoods = [q if label else 1-q for q in (baseline_p, p, mix)]
    losses = [-math.log2(q) for q in likelihoods]
    for score in (candidate['full'], candidate['horizon']) if within else (candidate['full'],):
        score['n'] += 1
        score['baseline_silent'] += int(silent)
        for name, loss, q in zip(('baseline','retained','mixture'), losses, (baseline_p,p,mix)):
            score[name+'_bits'] += loss
            score[name+'_errors'] += .5 if q == .5 else int((q > .5) != bool(label))
    candidate['weight'] = weight*likelihoods[1]/likelihoods[2]
    candidate['counts'][label] += 1
    return p, mix


def reconstruct(raw):
    assert all(c == 'Net' for c in raw['classes'])
    assert all(not h for h in raw['initial_histories'])
    definitions = [{k:r['definition'] for k,r in ds.items()} for ds in raw['definitions']]
    words = [{} for ds in definitions]
    for j, ds in enumerate(definitions):
        for k in ds:
            signature(ds,k,words[j])
    living = [{k:[0,0] for k,r in ds.items() if r['birth_seq'] == -1} for ds in raw['definitions']]
    assert all(definitions[j][k]['sym'] is not None for j, ns in enumerate(living) for k in ns)
    hist = [dict(h) for h in raw['initial_histories']]
    index = [-1]*len(hist)
    versions = [0]*len(hist)
    last_learn = {}
    seen_tastes = {}
    speaking = {}
    candidates = []
    last_prediction = None
    pending_write = None
    checks = Counter()
    for e in raw['events']:
        kind = e['kind']
        if kind == 'write':
            j = e['stream']
            assert e['i'] == index[j]+1, ('Nonsequential write', e['seq'])
            index[j] = e['i']
            pending_write = j
            changed = write_history(hist[j], e['i'], e['sym'], e['keep'], raw['hist_limit'])
            versions[j] += int(changed)
            assert changed == e['changed'] and versions[j] == e['version']
            checks['writes'] += 1
        elif kind == 'predict':
            pending_write = None
            probabilities, speakers = [], []
            for j, ns in enumerate(living):
                k = speaker(ns, words[j], hist[j], index[j])
                speakers.append(k)
                probabilities.append(.5 if k is None else probability(ns[k]))
                if k is not None:
                    key = (j,k)
                    if key not in speaking:
                        speaking[key] = dict(first_seq=e['seq'],count=0)
                    speaking[key]['count'] += 1
                checks['stream_predictions'] += 1
            last_prediction = dict(seq=e['seq'], hist=[dict(h) for h in hist], index=list(index),
                                   probabilities=probabilities, speakers=speakers)
            checks['predictions'] += 1
        elif kind == 'learn':
            pending_write = None
            j = e['stream']
            assert index[j] == e['i']
            assert list(living[j]) == e['living'], ('Living set mismatch', e['seq'])
            fired = [k for k in living[j] if activates(words[j][k], hist[j], index[j])]
            assert fired == e['firing'], ('Firing mismatch', e['seq'])
            if e['taste'] not in seen_tastes:
                assert last_prediction is not None
                # Freeze references from the last actual prediction, before ANY learn at this taste.
                seen_tastes[e['taste']] = dict(t=e['t'], label=e['letter'])
                for c in candidates:
                    if c['death_taste'] == e['taste']:
                        continue
                    assert c['death_seq'] < last_prediction['seq'] < e['seq']
                    cj = c['stream']
                    c['later_lessons'] += 1
                    if not activates(c['word'], last_prediction['hist'][cj], last_prediction['index'][cj]):
                        continue
                    delay = e['t']-c['death_t']
                    assert delay >= 0
                    within = c['eligible_100s'] and delay <= 100.
                    score_and_update(c, last_prediction['probabilities'][cj], e['letter'], within,
                                     last_prediction['speakers'][cj] is None)
                checks['accepted_tastes'] += 1
            else:
                assert seen_tastes[e['taste']] == dict(t=e['t'],label=e['letter'])
            last_learn[j] = e
            for k in fired:
                living[j][k][e['letter']] += 1
            checks['learns'] += 1
            checks['living_count_checkpoints'] += len(living[j])
        elif kind == 'birth':
            pending_write = None
            j,k = e['stream'],e['k']
            assert k not in living[j]
            assert last_learn[j]['taste'] == e['taste']
            counts = [0,0]
            counts[last_learn[j]['letter']] = 1
            living[j][k] = counts
            checks['births'] += 1
        elif kind == 'remove':
            j,k = e['stream'],e['k']
            if index[j] != e['i']:
                assert e['i'] == index[j]-1 and pending_write == j, ('Unexplained removal index',e['seq'])
                checks['tidy_removals_before_index_increment'] += 1
            assert living[j][k] == e['counts'], ('Removal tally mismatch', e['seq'],living[j][k],e['counts'])
            if sum(e['counts']) == 1:
                birth = raw['definitions'][j][k]
                candidates.append(dict(stream=j,k=k,family=family(raw['names'][j]),name=raw['names'][j],
                    word=words[j][k],death_seq=e['seq'],death_t=e['t'],death_taste=e['taste'],
                    same_taste_birth=birth['birth_taste'] == e['taste'],eligible_100s=e['t'] <= 200.,
                    counts=list(e['counts']),weight=.5,later_lessons=0,full=new_score(),horizon=new_score()))
            del living[j][k]
            checks['removal_tallies_exact'] += 1
        else:
            raise AssertionError(('Unknown event',kind))
    assert speaking == raw['speaking'], 'Native speaking first positions/counts differ'
    checks['native_speaking_records_exact'] = len(speaking)
    assert checks['predictions'] == raw['counters']['predict_calls']
    assert checks['learns'] == raw['counters']['learn_calls']
    assert checks['births'] == raw['counters']['adds']
    assert checks['removal_tallies_exact'] == raw['counters']['removals']
    for c in candidates:
        for score in (c['full'], c['horizon']):
            score['retained_saving_bits'] = score['baseline_bits']-score['retained_bits']
            score['mixture_saving_bits'] = score['baseline_bits']-score['mixture_bits']
            assert score['mixture_bits'] <= min(score['baseline_bits'],score['retained_bits'])+1+1e-9
            g = score['retained_saving_bits']
            expected = float(max(0.,g)+math.log2(1+2**(-abs(g)))-1)
            assert abs(score['mixture_saving_bits']-expected) < 1e-9
    return candidates, dict(checks), seen_tastes


def summarize(rows, key='full'):
    scores = [r[key] for r in rows]
    active = [s for s in scores if s['n']]
    return dict(units=len(rows), units_with_predictions=len(active), units_without_predictions=len(rows)-len(active),
        candidate_lesson_pairs=sum(s['n'] for s in scores),
        evidence_count=distribution([s['n'] for s in scores]),
        retained_better=sum(s['retained_saving_bits'] > 1e-10 for s in active),
        retained_worse=sum(s['retained_saving_bits'] < -1e-10 for s in active),
        retained_numerically_equal=sum(abs(s['retained_saving_bits']) <= 1e-10 for s in active),
        retained_saving_bits_among_active=distribution([s['retained_saving_bits'] for s in active]),
        mixture_saving_bits_among_active=distribution([s['mixture_saving_bits'] for s in active]),
        baseline_silent_pairs=sum(s['baseline_silent'] for s in scores),
        baseline_silent_fraction=(sum(s['baseline_silent'] for s in scores)/sum(s['n'] for s in scores)) if active else None,
        retained_more_than_one_bit=sum(s['retained_saving_bits'] > 1 for s in active),
        # Descriptive overlap-weighted sums, explicitly NOT a brain-wide information measure.
        overlapping_sums={k:sum(s[k] for s in scores) for k in ('baseline_bits','retained_bits','mixture_bits',
            'retained_saving_bits','mixture_saving_bits','baseline_errors','retained_errors','mixture_errors')})


def main():
    started = time.monotonic()
    out = dict(failures=[])
    try:
        data = pickle.loads(RAW.read_bytes())
        s,raw = data['summary'],data['raw']
        assert 'failure' not in s and all(s['identity'].values())
        for p,h in s['provenance']['source_sha256'].items():
            assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h,p
        import alloc_compare  # Frozen import environment; no simulation is invoked.
        import grownet as GN
        assert not GN.SURP and not GN.SAYS_N
        rows,checks,tastes = reconstruct(raw)
        accepted = len(tastes)
        print('VALIDATION',json.dumps(checks),flush=True)
        print('EVIDENCE',json.dumps(dict(accepted_labels=accepted,life_s=300.,labels_per_s=accepted/300.,
            candidate_count=distribution([r['full']['n'] for r in rows]))),flush=True)
        out.update(validation=checks,evidence=dict(accepted_labels=accepted,life_s=300.,labels_per_s=accepted/300.,
            maximum_binary_entropy_bits_per_s=accepted/300.,independent_evidence_rate_unknown=True),
            full=summarize(rows),horizon_100s=summarize([r for r in rows if r['eligible_100s']],'horizon'),
            by_family={f:summarize([r for r in rows if r['family']==f]) for f in ('event','clock','integrator','rhythm')},
            by_churn={str(c):summarize([r for r in rows if r['same_taste_birth']==c]) for c in (False,True)},
            family_horizon_100s={f:summarize([r for r in rows if r['family']==f and r['eligible_100s']],'horizon')
                for f in ('event','clock','integrator','rhythm')},
            provenance=dict(raw_path=str(RAW),raw_sha256=hashlib.sha256(RAW.read_bytes()).hexdigest(),
                revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                dirty=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),
                source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                    ('lab/retained_prediction.py','lab/retained_prediction_checks.py','lab/future_evidence.py','lab/future_evidence_analysis.py')},
                command='timeout --signal=TERM --kill-after=5s 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/retained_prediction.py'),
            limits=['One reused life, overlapping and selected units; no independent-unit confidence intervals.',
                'Reference is the native surviving stream at the last actual prediction, completed with 1/2 when silent, not the whole brain.',
                'Retained readout assumes a stationary Bernoulli probability with Beta(1/2,1/2) prior; not a true-world bound.',
                'Pairwise mixture gives each candidate its own supplied half prior; not a combined allocator or a free prior over all candidates.',
                'No cap, displacement, action changes, ancestor storage, physical energy or communication savings are simulated.',
                'Overlapping sums are descriptions of candidate-lesson pairs, not independent learned bits or brain-wide gain.'])
        BASE.with_suffix('.pkl').write_bytes(pickle.dumps(dict(rows=rows,tastes=tastes,summary=out)))
        print('SUMMARY',json.dumps(out['full']),flush=True)
    except Exception as exc:
        out['failures'].append(dict(type=type(exc).__name__,message=str(exc)))
        raise
    finally:
        out['wall_s'] = time.monotonic()-started
        BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
        print('wall_s',out['wall_s'],flush=True)


if __name__ == '__main__':
    main()
