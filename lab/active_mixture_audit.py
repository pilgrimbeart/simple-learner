"""D79 bounded, read-only active-mixture diagnostic. See lab/v/d79_work_order.md.
Run: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/active_mixture_audit.py
"""
from __future__ import annotations
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
import alloc_compare as C
import numpy as np

BASE = ROOT / 'lab/v/active_mixture_audit'
FAMS = ('event', 'clock', 'integrator', 'rhythm')
WINDOWS = ((0,30), (30,100), (100,200), (200,300), (0,300))
CLIP = 1e-12


def canonical(x):
    """Stable complete data state, excluding methods and replacing network object links by names."""
    if isinstance(x, np.random.Generator):
        return canonical(x.bit_generator.state)
    if isinstance(x, np.ndarray):
        return ('array', str(x.dtype), x.shape, canonical(x.tolist()))
    if isinstance(x, np.generic):
        return canonical(x.item())
    if isinstance(x, dict):
        return sorted(((repr(k), canonical(v)) for k,v in x.items() if not callable(v)), key=lambda kv:kv[0])
    if isinstance(x, (list,tuple)):
        return [canonical(v) for v in x]
    if isinstance(x, set):
        return sorted((canonical(v) for v in x), key=repr)
    if isinstance(x, complex):
        return ('complex', x.real, x.imag)
    if x is None or isinstance(x, (str,int,float,bool)):
        return x
    if isinstance(getattr(x, 'kind', None), str):
        return ('net', x.kind)
    # Shared pool/market links point back to this same brain; data is fingerprinted separately.
    if hasattr(x, 'nets'):
        return ('brain_or_pool', type(x).__name__)
    raise TypeError((type(x).__name__, repr(x)))


def fingerprint(lf):
    b = lf.brain
    rngs = []
    for n in b.nets:
        # Allocator RNG belongs to a closure, not the brain's data dictionary.
        for cell in (getattr(n._room, '__closure__', None) or ()):
            if isinstance(cell.cell_contents, np.random.Generator):
                rngs.append(cell.cell_contents.bit_generator.state)
    state = dict(behaviour=dict(meals=lf.meals, scored=lf.scored, firings=lf.firings),
                 brain={k:v for k,v in b.__dict__.items() if k not in ('nets','byk') and not callable(v)},
                 nets=[{k:v for k,v in n.__dict__.items() if not callable(v)} for n in b.nets],
                 allocator_rngs=rngs)
    data = canonical(state)
    return hashlib.sha256(repr(data).encode()).hexdigest(), data


def mixture(weights, probabilities, keep=None):
    """Probability mixture with explicit abstention (NaN); the default is entry zero."""
    use = np.isfinite(probabilities)
    if keep is not None:
        use = use & keep
    return float(np.dot(weights[use], probabilities[use]) / weights[use].sum())


def loss(p, letter):
    return -math.log2(max(CLIP, min(1-CLIP, p if letter else 1-p)))


def measurement_checks():
    # Expected answers are computed independently by hand: (2*.25 + 1*.75)/3 = 5/12.
    w, q = np.array([2.,1.,1000.]), np.array([.25,.75,np.nan])
    assert abs(mixture(w,q)-5/12) < 1e-15
    w[2] = 1e12
    assert abs(mixture(w,q)-5/12) < 1e-15
    assert mixture(w,q,np.array([True,True,False])) == mixture(w,q)
    # Correct label 1: helpful predictor changes probability .5 -> .75, saving log2(1.5).
    delta = loss(.5,1)-loss(.75,1)
    assert abs(delta-math.log2(1.5)) < 1e-15 and delta > 0
    assert loss(.5,0)-loss(.75,0) < 0
    return dict(sleeping_invariance=True, empty_removal=True, delta_sign=True)


class Observer:
    def __init__(self, lf):
        self.b, self.lf = lf.brain, lf
        self.names = ['default']+[n.kind for n in self.b.nets]
        self.families = ['default']+[C.family(n.kind) for n in self.b.nets]
        self.predictions, self.tastes = [], []
        self.issuing = None
        self.current = None
        self.learning = None
        self.max_error = 0.
        # These arms use N/ClockN only. JointN.says writes _act, and must never be probed.
        import grownet
        assert all(type(n).says in (grownet.Net.says, grownet.Net2.says) for n in self.b.nets), [(type(n),n.kind) for n in self.b.nets]
        for j,n in enumerate(self.b.nets,1):
            self.wrap_net(n,j)
        self.wrap_brain()

    def snapshot(self):
        b = self.b
        w, q, keys = [getattr(b,'w_def',1.)], [b._pdef(1)], [None]
        for n in b.nets:
            k,_ = n.says(b.place(n)-1)
            keys.append(k)
            w.append(getattr(n,'w',1.))
            q.append(b._pk(n,k,1) if k is not None else np.nan)
        return dict(w=np.array(w), q=np.array(q), keys=keys)

    def wrap_net(self,n,j):
        says, learn, remove = n.says, n.learn, n._remove
        def _says(i):
            r = says(i)
            if self.issuing is not None:
                k = r[0]
                assert self.issuing['seen'][j] == 0
                self.issuing['seen'][j] += 1
                self.issuing['keys'][j] = k
                self.issuing['w'][j] = getattr(n,'w',1.)
                self.issuing['q'][j] = self.b._pk(n,k,1) if k is not None else np.nan
            return r
        def _learn(i,letter,t,speaker,firing):
            cur = self.current
            if cur is not None:
                if cur['letter'] is None:
                    cur['letter'] = int(letter)
                assert cur['letter'] == letter
                cur['learn_calls'] += 1
                cur['scored_q'][j] = self.b._pk(n,speaker,1) if speaker is not None else np.nan
                cur['scored_keys'][j] = speaker
                cur['learn_times'].append(t)
            old, self.learning = self.learning, j
            try:
                return learn(i,letter,t,speaker,firing)
            finally:
                self.learning = old
        def _remove(k):
            if self.current is not None and self.learning is not None and j > self.learning and k in n.units:
                self.current['later_removals'].append((self.learning,j,k,k==self.current['entry']['keys'][j]))
            return remove(k)
        n.says,n.learn,n._remove = _says,_learn,_remove

    def wrap_brain(self):
        b = self.b
        predict,taste = b.predict,b.taste
        def _predict():
            assert self.issuing is None
            count = len(self.names)
            row = dict(t=float(b.t), w=np.zeros(count), q=np.full(count,np.nan),
                       keys=[None]*count, seen=np.zeros(count,dtype=np.int8))
            row['w'][0],row['q'][0],row['seen'][0] = getattr(b,'w_def',1.),b._pdef(1),1
            self.issuing = row
            try:
                answer = predict()
            finally:
                self.issuing = None
            assert np.all(row.pop('seen') == 1), 'predict did not ask every stream exactly once'
            row['p1'] = float(b.p1)
            error = abs(mixture(row['w'],row['q'])-row['p1'])
            self.max_error = max(self.max_error,error)
            assert error <= 1e-12, ('issued prediction reconstruction',error)
            self.predictions.append(row)
            return answer
        def _taste(value,at):
            # Outer wrapper is installed after Seconds._timed_taste. Its temporary clock must be honoured.
            end = b.t
            b.t = end+at
            try:
                entry = self.snapshot()
                moment = float(b.t)
            finally:
                b.t = end
            row = dict(t=moment, value=value, issued=len(self.predictions)-1 if self.predictions else None,
                       entry=entry, entry_p1=float(getattr(b,'p1',.5)), letter=None,learn_calls=0,
                       scored_q=np.array([entry['q'][0]]+[np.nan]*(len(self.names)-1)),
                       scored_keys=[None]*len(self.names),later_removals=[],learn_times=[])
            before = getattr(b,'ntaste',0)
            bits = getattr(b,'pbits',0.)
            assert self.current is None
            self.current = row
            try:
                answer = taste(value,at)
            finally:
                self.current = None
            row['accepted'] = row['letter'] is not None
            assert getattr(b,'ntaste',0)-before == int(row['accepted'])
            if row['accepted']:
                assert row['learn_calls'] == len(b.nets)
                assert all(t == moment for t in row['learn_times']), 'taste clock differs'
                row['actual_scored_bits'] = getattr(b,'pbits',0.)-bits
                row['reconstructed_scored_bits'] = loss(mixture(entry['w'],row['scored_q']),row['letter'])
                assert abs(row['actual_scored_bits']-row['reconstructed_scored_bits']) < 1e-10
            self.tastes.append(row)
            return answer
        b.predict,b.taste = _predict,_taste


def one(job):
    rule,P,first,observe,seconds = job
    from stage2_lang import arms as S
    original = S.live
    out = {}
    C.G = 1000 if rule == 'W' else 258
    def live(lf,secs):
        ob = Observer(lf) if observe else None
        lived = original(lf,secs)
        digest, state = fingerprint(lf)
        out.update(fingerprint=digest)
        if seconds == 1.:
            out['canonical_state'] = state
            with BASE.with_suffix('.pkl').open('ab') as f:
                pickle.dump(dict(smoke=observe,state_repr=repr(state),result=list(lived)),f)
        if ob:
            out.update(predictions=ob.predictions,tastes=ob.tastes,names=ob.names,families=ob.families,
                       max_reconstruction_error=ob.max_error)
        return lived
    S.live = live
    # Only for the authorised short smoke run; full run remains 300 seconds.
    saved = C.FAMILIES['seq']
    C.FAMILIES['seq'] = (17,seconds,*saved[2:])
    t0 = time.monotonic()
    try:
        result = C.one(('seq',rule,P,177000,first))
    finally:
        S.live = original
        C.FAMILIES['seq'] = saved
    return dict(**result,observe=observe,wall_s=time.monotonic()-t0,**out)


def shares(rows,families):
    if not rows:
        return dict(n=0)
    w,q = np.stack([r['w'] for r in rows]),np.stack([r['q'] for r in rows])
    awake = np.isfinite(q)
    aw = w*awake
    active,stored = aw/aw.sum(1)[:,None],w/w.sum(1)[:,None]
    return dict(n=len(rows),sleeping_fraction=float((1-aw.sum(1)/w.sum(1)).mean()),
                active={f:float(active[:,np.array(families)==f].sum(1).mean()) for f in ('default',*FAMS)},
                stored={f:float(stored[:,np.array(families)==f].sum(1).mean()) for f in ('default',*FAMS)})


def summarise(life):
    ps,ts,fs = life['predictions'],life['tastes'],life['families']
    windows = []
    for lo,hi in WINDOWS:
        tastes = [t for t in ts if lo <= t['t'] < hi]
        accepted = [t for t in tastes if t['accepted']]
        use = [t for t in accepted if t['issued'] is not None]
        r = dict(window=[lo,hi],tastes=len(tastes),accepted=len(accepted),without_prior_prediction=sum(t['issued'] is None for t in tastes),
                 accepted_without_prior_prediction=len(accepted)-len(use),
                 prediction_shares=shares([p for p in ps if lo <= p['t'] < hi],fs),
                 accepted_taste_shares=shares([ps[t['issued']] for t in use],fs),delta_bits={})
        for family in (*FAMS,'non_event'):
            remove = tuple(FAMS[1:]) if family == 'non_event' else (family,)
            keep = np.array([f not in remove for f in fs])
            ds,changed = [],0
            for t in use:
                p = ps[t['issued']]
                without = mixture(p['w'],p['q'],keep)
                ds.append(loss(without,t['letter'])-loss(p['p1'],t['letter']))
                changed += (without>.5)!=(p['p1']>.5)
            r['delta_bits'][family] = dict(n=len(ds),total=float(sum(ds)),mean=float(np.mean(ds)) if ds else None,changed_choices=int(changed))
        differing = lambda a,b: not np.array_equal(a,b,equal_nan=True)
        r['scoring_order'] = dict(
            accepted_with_later_removal=sum(bool(t['later_removals']) for t in accepted),
            accepted_with_prelearning_speaker_deleted=sum(any(x[3] for x in t['later_removals']) for t in accepted),
            accepted_with_scored_forecast_difference=sum(differing(t['entry']['q'],t['scored_q']) for t in accepted),
            total_simultaneous_minus_scored_bits=float(sum(loss(mixture(t['entry']['w'],t['entry']['q']),t['letter'])-t['reconstructed_scored_bits'] for t in accepted)),
            scored_reconstruction_max_error=max([abs(t['actual_scored_bits']-t['reconstructed_scored_bits']) for t in accepted],default=0))
        r['issued_vs_entry'] = dict(
            p1_attribute_differences=sum(ps[t['issued']]['p1']!=t['entry_p1'] for t in use),
            active_mixture_differences=sum(abs(ps[t['issued']]['p1']-mixture(t['entry']['w'],t['entry']['q']))>1e-12 for t in use),
            max_active_mixture_difference=max([abs(ps[t['issued']]['p1']-mixture(t['entry']['w'],t['entry']['q'])) for t in use],default=0))
        windows.append(r)
    return dict(rule=life['rule'],P=life['P'],first=life['first'],seed=life['seed'],result=life['result'],
                fingerprint=life['fingerprint'],max_reconstruction_error=life['max_reconstruction_error'],windows=windows)


def provenance():
    paths = ['lab/active_mixture_audit.py','lab/alloc_compare.py','lab/alloc_rules.py','lab/grownet.py','lab/teach.py',
             'lab/ladders.py','lab/stage2_lang/seconds.py','lab/stage2_lang/sim.py','lab/stage2_lang/arms.py','lab/v/alloc_confirm.json']
    return dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip(),
                dirty=subprocess.check_output(['git','status','--short'],text=True,cwd=ROOT),
                sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
                command='OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python '+' '.join(sys.argv),
                environment={k:os.environ.get(k) for k in ('LB_FINE','LB_LIVE','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')})


def paired_descriptions(lives):
    """Pool the two colour lives descriptively; no sampling interval from one reused seed pair."""
    result = {}
    for rule in ('none','W'):
        rr = [r for r in lives if r['rule']==rule]
        rows = []
        for i,window in enumerate(WINDOWS):
            ws = [r['windows'][i] for r in rr]
            row = dict(window=list(window),tastes=sum(w['tastes'] for w in ws),accepted=sum(w['accepted'] for w in ws),
                       shares={},delta_bits={})
            for field in ('prediction_shares','accepted_taste_shares'):
                n = sum(w[field]['n'] for w in ws)
                row['shares'][field] = dict(n=n,
                    sleeping_fraction=sum(w[field]['n']*w[field]['sleeping_fraction'] for w in ws)/n,
                    **{mode:{f:sum(w[field]['n']*w[field][mode][f] for w in ws)/n for f in ('default',*FAMS)} for mode in ('active','stored')})
            for family in (*FAMS,'non_event'):
                ds = [w['delta_bits'][family] for w in ws]
                n,total = sum(d['n'] for d in ds),sum(d['total'] for d in ds)
                row['delta_bits'][family] = dict(n=n,total=total,mean=total/n,changed_choices=sum(d['changed_choices'] for d in ds))
            row['scoring_order'] = {k:sum(w['scoring_order'][k] for w in ws) for k in ws[0]['scoring_order'] if k!='scored_reconstruction_max_error'}
            rows.append(row)
        result[rule] = rows
    return result


def main():
    if '--analyse' in sys.argv:
        out = json.loads(BASE.with_suffix('.json').read_text())
        out['paired_descriptions'] = paired_descriptions(out['lives'])
        out['analysis_only_final_script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
        return
    checks = measurement_checks()
    if '--checks' in sys.argv:
        print(checks)
        return
    seconds = 1. if '--smoke' in sys.argv else 300.
    jobs = [(rule,P,c,obs,seconds) for rule,P in (('none',4480),('W',560)) for c in ('red','blue') for obs in (True,False)]
    if seconds == 1:
        jobs = jobs[:2]
    payload = dict(provenance=provenance(),checks=checks,config=dict(seconds=seconds,dt=.0025,seed=177000,rung=17,workers=4,clip=CLIP),lives=[])
    start = time.monotonic()
    try:
        with ProcessPoolExecutor(4) as ex:
            for r in ex.map(one,jobs):
                payload['lives'].append(r)
                print(json.dumps({k:r[k] for k in ('rule','P','first','observe','wall_s','fingerprint')}),flush=True)
    except Exception as e:
        payload['failure'] = repr(e)
        payload['wall_s'] = time.monotonic()-start
        BASE.with_suffix('.json').write_text(json.dumps({k:v for k,v in payload.items() if k!='lives'},indent=2)+'\n')
        raise
    payload['wall_s'] = time.monotonic()-start
    if seconds == 1:
        with BASE.with_suffix('.pkl').open('wb') as f:
            pickle.dump(payload,f)
        assert payload['lives'][0]['fingerprint']==payload['lives'][1]['fingerprint']
        print('SMOKE PASS',payload['wall_s'],flush=True)
        return
    with BASE.with_suffix('.pkl').open('wb') as f:
        pickle.dump(payload,f)
    historical = json.loads((ROOT/'lab/v/alloc_confirm.json').read_text())['families']['seq']['lives']
    out = {k:v for k,v in payload.items() if k!='lives'}
    out['identity_checks'],out['lives'] = [],[]
    for r in payload['lives']:
        if not r['observe']:
            continue
        u = next(x for x in payload['lives'] if (x['rule'],x['first'],x['observe'])==(r['rule'],r['first'],False))
        h = next(x for x in historical if (x['rule'],x['seed'],x['first'])==(r['rule'],r['seed'],r['first']))
        result_fields = [i for i in range(len(r['result'])) if i!=5]  # wall-clock field is explicitly non-behavioural
        same = all(r['result'][i]==u['result'][i] for i in result_fields)
        normalized = json.loads(json.dumps(r['result'],default=str))
        hist_diff = [dict(index=i,historical=h['result'][i],now=normalized[i]) for i in result_fields if h['result'][i]!=normalized[i]]
        out['identity_checks'].append(dict(rule=r['rule'],first=r['first'],fingerprint_equal=r['fingerprint']==u['fingerprint'],
                                          result_equal=same,historical_differences=hist_diff,
                                          ignored_result_field=5,observed_wall_s=r['wall_s'],unobserved_wall_s=u['wall_s']))
        if r['fingerprint']!=u['fingerprint'] or not same:
            out['failure']='Observer changes life; no scientific analysis permitted'
        out['lives'].append(summarise(r) if 'failure' not in out else dict(rule=r['rule'],first=r['first']))
    out['paired_descriptions'] = paired_descriptions(out['lives']) if 'failure' not in out else {}
    BASE.with_suffix('.json').write_text(json.dumps(out,indent=2,default=str)+'\n')
    assert 'failure' not in out,out.get('failure')
    print('PASS: issued reconstruction and observed/unobserved identity; historical differences retained',out['identity_checks'],flush=True)
    print('wall_s',payload['wall_s'],flush=True)


if __name__=='__main__':
    main()
