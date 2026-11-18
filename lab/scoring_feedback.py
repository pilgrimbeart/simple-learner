"""D81: isolate selector-score correction in closed loop; lab instance patches only.

OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python
lab/scoring_feedback.py > lab/v/scoring_feedback.log 2>&1
"""
import hashlib
import json
import math
import os
from pathlib import Path
import pickle
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'lab'), str(ROOT)]
import numpy as np
import alloc_compare as C
from active_mixture_audit import fingerprint
from scoring_order_replay import update, checks

BASE = ROOT / 'lab/v/scoring_feedback'


class SelectorCredit:
    def __init__(self, lf, corrected):
        self.b, self.corrected = lf.brain, corrected
        self.current = None
        self.predictions, self.tastes = [], []
        self.same_update_max_error = 0.
        b = self.b
        import grownet
        assert b.BAYES and b.SHARE == .01 and grownet.BT == 1.
        assert all(type(n).says in (grownet.Net.says, grownet.Net2.says) for n in b.nets)
        for j, n in enumerate(b.nets, 1):
            original = n.learn

            def learn(i, letter, t, speaker, firing, _n=n, _j=j, _original=original):
                cur = self.current
                assert cur is not None and t == cur['t']
                assert cur['letter'] in (None, letter)
                cur['letter'] = int(letter)
                cur['actual_likelihood'][_j] = b._pk(_n, speaker, letter) if speaker is not None else np.nan
                return _original(i, letter, t, speaker, firing)
            n.learn = learn
        original_taste, original_predict = b.taste, b.predict

        def predict():
            cur = self.current
            if cur is not None and cur['letter'] is not None and not cur['applied']:
                letter = cur['letter']
                likelihood = cur['q'][letter]
                cur['actual_likelihood'][0] = likelihood[0]
                desired_w, desired_saved = cur['w'].copy(), cur['saved'].copy()
                # Exact p(label) captured from the count-based predictor, not 1 - rounded p(1).
                desired_bits = update(desired_w, likelihood, 1, desired_saved)
                native = np.array([getattr(b, 'w_def', 1.)] + [getattr(n, 'w', 1.) for n in b.nets])
                native_saved = np.array([0.] + [getattr(n, 'saved', 0.) for n in b.nets])
                different = not np.array_equal(likelihood, cur['actual_likelihood'], equal_nan=True)
                cur['changed_scores'] = int(np.sum(~(np.equal(likelihood, cur['actual_likelihood']) |
                    (np.isnan(likelihood) & np.isnan(cur['actual_likelihood'])))))
                cur['weight_change_max'] = float(np.max(abs(desired_w-native)))
                if not different:
                    err = max(float(np.max(abs(desired_w-native))), float(np.max(abs(desired_saved-native_saved))))
                    self.same_update_max_error = max(self.same_update_max_error, err)
                    assert err <= 1e-12, ('unchanged scoring update differs', err)
                    # Preserve native arithmetic exactly when there is no scientific intervention.
                elif corrected:
                    b.w_def = float(desired_w[0])
                    for j, n in enumerate(b.nets, 1):
                        if hasattr(n, 'w') or desired_w[j] != 1.:
                            n.w = float(desired_w[j])
                        if hasattr(n, 'saved') or desired_saved[j] != 0.:
                            n.saved = float(desired_saved[j])
                    b.pbits = cur['pbits'] + desired_bits
                cur['applied'] = True
            result = original_predict()
            self.predictions.append((float(b.t), float(b.p1), int(b.food), sum(len(n.units) for n in b.nets)))
            return result

        def taste(value, at):
            assert self.current is None
            t0 = b.t
            b.t = t0 + at
            try:
                q = [[b._pdef(letter)] for letter in (0, 1)]
                for n in b.nets:
                    k, _ = n.says(b.place(n)-1)
                    for letter in (0, 1):
                        q[letter].append(b._pk(n, k, letter) if k is not None else np.nan)
                cur = dict(t=float(b.t), q=np.array(q), letter=None, applied=False,
                    w=np.array([getattr(b, 'w_def', 1.)] + [getattr(n, 'w', 1.) for n in b.nets]),
                    saved=np.array([0.] + [getattr(n, 'saved', 0.) for n in b.nets]),
                    pbits=getattr(b, 'pbits', 0.), actual_likelihood=np.full(len(b.nets)+1, np.nan))
            finally:
                b.t = t0
            before = getattr(b, 'ntaste', 0)
            self.current = cur
            try:
                result = original_taste(value, at)
            finally:
                self.current = None
            assert getattr(b, 'ntaste', 0)-before == int(cur['letter'] is not None)
            assert cur['letter'] is None or cur['applied'], 'No prediction after accepted taste'
            self.tastes.append({k: cur.get(k) for k in ('t', 'letter', 'changed_scores', 'weight_change_max')})
            return result
        b.predict, b.taste = predict, taste


def one(job):
    rule, P, first, corrected = job
    from stage2_lang import arms as S
    C.G = 1000 if rule == 'W' else 258
    original, out = S.live, {}

    def live(lf, seconds):
        observer = SelectorCredit(lf, corrected)
        lived = original(lf, seconds)
        out.update(fingerprint=fingerprint(lf)[0], predictions=observer.predictions,
                   tastes=observer.tastes, same_update_max_error=observer.same_update_max_error,
                   meals=lf.meals, firings=lf.firings,
                   births=sum(n.births for n in lf.brain.nets))
        return lived
    S.live = live
    try:
        result = C.one(('seq', rule, P, 177000, first))
    finally:
        S.live = original
    return dict(**result, corrected=corrected, **out)


def first_difference(a, b):
    for x, y in zip(a, b):
        if x != y:
            return dict(original=x, corrected=y)
    return None if len(a) == len(b) else dict(common_prefix=len(a) if len(a)<len(b) else len(b))


def small(row):
    out = {k: v for k, v in row.items() if k not in ('predictions', 'tastes', 'meals', 'firings')}
    out['accepted'] = sum(t['letter'] is not None for t in row['tastes'])
    affected = [t for t in row['tastes'] if t['changed_scores']]
    out['affected_tastes'] = len(affected)
    out['first_affected_taste'] = affected[0] if affected else None
    out['whole_efficiency'] = row['result'][0]/row['result'][1]
    out['last_third_efficiency'] = row['result'][2]/row['result'][3]
    return out


def main():
    start = time.monotonic()
    source_paths = ('lab/scoring_feedback.py', 'lab/scoring_order_replay.py', 'lab/active_mixture_audit.py',
                    'lab/alloc_compare.py', 'lab/alloc_rules.py', 'lab/grownet.py', 'lab/teach.py',
                    'lab/stage2_lang/seconds.py', 'lab/stage2_lang/sim.py', 'lab/ladders.py')
    out = dict(config=dict(seed=177000, seconds=300., dt=.0025, rung=17, arm=C.ARM, workers=4),
        provenance=dict(revision=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
            dirty=subprocess.check_output(['git','status','--short'], cwd=ROOT, text=True),
            source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in source_paths},
            command='OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/scoring_feedback.py',
            environment={k:os.environ.get(k) for k in ('LB_FINE','LB_LIVE','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')}),
        arithmetic_checks=checks(), neutral_checks=[], lives=[], differences=[])
    raw = []
    try:
        historical = json.loads((ROOT/'lab/v/active_mixture_audit.json').read_text())['lives']
        configs = [(r,p,c) for r,p in (('none',4480),('W',560)) for c in ('red','blue')]
        with ProcessPoolExecutor(4) as pool:
            for row in pool.map(one, [(*c,False) for c in configs]):
                raw.append(row)
                h = next(x for x in historical if (x['rule'],x['first']) == (row['rule'],row['first']))
                same = json.loads(json.dumps(row['result'])) == h['result'] and row['fingerprint'] == h['fingerprint']
                out['neutral_checks'].append(dict(rule=row['rule'],first=row['first'],exact_match=same))
                assert same, out['neutral_checks'][-1]
                print('NEUTRAL PASS',row['rule'],row['first'],flush=True)
            for row in pool.map(one, [(*c,True) for c in configs]):
                raw.append(row)
                print('CORRECTED',row['rule'],row['first'],small(row),flush=True)
        for original in raw[:4]:
            fixed = next(r for r in raw[4:] if (r['rule'],r['first']) == (original['rule'],original['first']))
            out['differences'].append(dict(rule=original['rule'],first=original['first'],
                first_prediction=first_difference(original['predictions'],fixed['predictions']),
                first_meal=first_difference(original['meals'],fixed['meals']),
                first_firing=first_difference(original['firings'],fixed['firings']),
                total_gain=fixed['result'][0]-original['result'][0],
                last_third_gain=fixed['result'][2]-original['result'][2],
                final_units=fixed['final_units']-original['final_units']))
        out['lives'] = [small(r) for r in raw]
    except Exception as e:
        out['failure'] = repr(e)
        raise
    finally:
        out['wall_s'] = time.monotonic()-start
        BASE.with_suffix('.pkl').write_bytes(pickle.dumps(dict(summary=out,lives=raw)))
        BASE.with_suffix('.json').write_text(json.dumps(out,indent=2,default=str)+'\n')
        print('wall_s',out['wall_s'],flush=True)


if __name__ == '__main__':
    main()
