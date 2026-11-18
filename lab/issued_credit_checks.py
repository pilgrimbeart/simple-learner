"""D82 deterministic semantic checks on the frozen native brain; no simulated steps/lives.
Fixtures replace stream context reads/learning with known miniature cases, retaining
native brain taste/predict, scoring and recursive unit credit. Run with one maths thread.
"""
from __future__ import annotations
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'lab'),str(ROOT)]
import alloc_compare as C
from issued_credit import install,Forecast,_selector
from active_mixture_audit import fingerprint
import numpy as np

BASE=ROOT/'lab/v/issued_credit_checks'


def fixture():
    import stage3_random as R
    import teach as T
    from stage2_lang import arms as S
    R._init(.0025,False)
    old=S.live
    holder=[]
    class Constructed(Exception):pass
    def capture(lf,secs):
        holder.append(lf)
        raise Constructed
    S.live=capture
    try:
        T.job((C.world('seq'),C.ARM,4480,177000,'red',300.))
    except Constructed:
        pass
    finally:
        S.live=old
    lf=holder[0];b=lf.brain
    b.vouched=lambda:True
    b.bar=.5
    b.dl=0
    b.dt=0
    selected={n.kind:None for n in b.nets}
    for n in b.nets:
        def says(i,_n=n):
            k=selected[_n.kind]
            return (k,[k]) if k in _n.units else (None,[])
        n.says=says
        n.learn=lambda *a:None
        n.write=lambda *a,**k:None
        n.tidy=lambda *a:None
    return lf,selected,b.nets[1]


def add_speaker(n,counts=(0,3),parents=True):
    # Initial event alphabet is two roots, so their new child has ID 2.
    k=n._add(0 if parents else None,1 if parents else None,2,0.)
    n.units[k]['n']=list(counts)
    return k


def run_checks():
    results=[]
    def passed(name,**data):results.append(dict(name=name,passed=True,**data))
    # Independent hand answer for two weights 2 and a sleeper 7: likelihoods 1/4,3/4.
    f=(Forecast(None,0,.75,.25),Forecast(2,1,.25,.75),Forecast(None,None,None,None))
    w,s,loss=_selector([2.,2.,7.],[0.,0.,0.],f,1,.01)
    assert max(abs(a-b) for a,b in zip(w,[1.01,2.99,7.]))<1e-14 and loss==1.
    passed('known_selector_update_and_sleepers',weights=w)

    lf,chosen,n=fixture();k=add_speaker(n);chosen[n.kind]=k
    ob=install(lf);lf.brain.predict();lf.brain.taste(1.,0.)
    assert n.agree==1 and n.dis==0 and n.units[k]['use']==1. and n.units[k]['own']==1.
    assert all(n.units[j]['use']==1. and n.units[j]['own']==0. for j in (0,1))
    assert ob.counters['unit_use_credit_calls']==3 and ob.counters['unit_own_credit_calls']==1
    assert lf.brain.best is n
    passed('living_original_and_parents_once',summary=ob.summary())

    # Both a wrong and a correct current replacement must remain uncredited.
    for counts in ((3,0),(0,3)):
        lf,chosen,n=fixture();k=add_speaker(n);chosen[n.kind]=k
        ob=install(lf);lf.brain.predict();n._remove(k)
        replacement=add_speaker(n,counts);chosen[n.kind]=replacement
        assert replacement>k
        lf.brain.taste(1.,0.)
        assert n.agree==1 and n.dis==0 and n.units[replacement]['use']==0. and n.units[replacement]['own']==0.
        assert ob.counters['correct_but_undeliverable_credit']==1
        assert ob.counters['replacement_credit_prevented']==int(counts==(0,3))
        passed('deleted_original_wrong_replacement' if counts==(3,0) else 'deleted_original_correct_replacement',summary=ob.summary())

    lf,chosen,n=fixture();k=add_speaker(n,(3,0))
    ob=install(lf);lf.brain.predict()  # initially silent; native default predicts letter 0
    chosen[n.kind]=k
    lf.brain.taste(1.,0.)
    assert n.agree==n.dis==n.E==0 and n.units[k]['use']==n.units[k]['own']==0.
    assert getattr(n,'ra',0.)==0. and getattr(n,'w',1.)==1. and getattr(n,'saved',0.)==0.
    assert ob.counters['replacement_credit_prevented']==1
    passed('issued_abstention_cannot_gain_retrospective_credit',summary=ob.summary())

    lf,chosen,n=fixture();k=add_speaker(n);chosen[n.kind]=k
    seen=[];native_predict=lf.brain.predict
    def trace_prediction():
        seen.append((n.agree,n.units[k]['use'],getattr(n,'w',1.)))
        return native_predict()
    lf.brain.predict=trace_prediction
    ob=install(lf);lf.brain.predict()
    cached=ob.last[2]
    assert cached.p1==.875 and cached.p0==.125 and cached.choice==1
    n.units[k]['n']=[3,0]
    lf.brain.taste(1.,0.)
    assert cached.p1==.875 and cached.choice==1
    assert n.agree==1 and n.units[k]['use']==1.
    # Default .5 and target .875, equal weights: target posterior 14/11;
    # .01 share gives .99*(14/11)+.01 = 1.27 exactly to rounding.
    assert abs(n.w-1.27)<1e-14 and abs(n.saved-math.log2(1.75))<1e-14
    assert seen[0]==(0,0.,1.) and seen[-1][:2]==(1,1.) and abs(seen[-1][2]-1.27)<1e-14
    assert ob.counters['tastes_with_issued_entry_mismatch']==1
    passed('immutable_cached_forecast_and_update_before_next_prediction',summary=ob.summary(),prediction_entry=seen)

    lf,chosen,n=fixture();k=add_speaker(n);chosen[n.kind]=k
    replacement=add_speaker(n,(3,0))
    first=lf.brain.nets[0]
    def earlier_learning(*args):
        n._remove(k);chosen[n.kind]=replacement
    first.learn=earlier_learning
    learned=[]
    n.learn=lambda i,letter,t,speaker,firing:learned.append((speaker,list(firing)))
    ob=install(lf);lf.brain.predict();lf.brain.taste(1.,0.)
    assert n.agree==1 and n.units[replacement]['use']==0.
    assert learned==[(replacement,[replacement])], 'Current-context learn arguments changed'
    assert ob.counters['correct_but_undeliverable_credit']==1
    passed('sequential_earlier_learning_deletes_original',summary=ob.summary())

    lf,chosen,n=fixture();k=add_speaker(n,(3,0));chosen[n.kind]=k
    ob=install(lf);lf.brain.predict()  # issued choice/default 0, then poison reveals letter 1
    n._remove(k);replacement=add_speaker(n,(0,3));chosen[n.kind]=replacement
    lf.brain.taste(-1.,0.)
    assert n.agree==0 and n.dis==1 and n.rd==1. and n.ra==0.
    assert n.units[replacement]['use']==n.units[replacement]['own']==0.
    assert ob.counters['correct_but_undeliverable_credit']==0
    passed('wrong_issued_forecast_correct_replacement_is_still_wrong',summary=ob.summary())

    # Pure observation: same sequence and exact all-data fingerprint; methods excluded.
    states=[]
    for observe in (False,True):
        lf,chosen,n=fixture();k=add_speaker(n);chosen[n.kind]=k
        ob=install(lf,enabled=False) if observe else None
        lf.brain.predict();lf.brain.taste(1.,0.)
        states.append(fingerprint(lf)[0])
    assert states[0]==states[1]
    passed('disabled_observer_exact_state_identity',fingerprint=states[0])

    lf,chosen,n=fixture();chosen[n.kind]=add_speaker(n)
    ob=install(lf)
    try:lf.brain.taste(1.,0.)
    except AssertionError as e:assert 'prior issued' in str(e)
    else:raise AssertionError('Accepted taste without prior forecast was not rejected')
    passed('accepted_without_prior_forecast_rejected')
    return results


def main():
    start=time.monotonic()
    paths=['lab/issued_credit.py','lab/issued_credit_checks.py','lab/grownet.py','lab/teach.py','lab/scoring_order_replay.py']
    out=dict(provenance=dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        dirty=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),
        source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
        command='OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/issued_credit_checks.py',
        env={k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')}),
        simulated_steps=0,checks=[])
    try:
        out['checks']=run_checks()
        for result in out['checks']:print('PASS',result['name'],flush=True)
    except Exception as e:
        out['failure']=repr(e)
        raise
    finally:
        out['wall_s']=time.monotonic()-start
        BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
        print('wall_s',out['wall_s'],flush=True)


if __name__=='__main__':main()
