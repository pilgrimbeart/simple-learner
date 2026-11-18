"""D80: exact original specialist selector replay, then fixed-history corrected credit.
No simulation. Protocol and tolerances: discrete/NOTEBOOK.md D80 (2026-11-17).
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/scoring_order_replay.py
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
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'lab/v/scoring_order_replay'
RAW = ROOT/'lab/v/active_mixture_audit.pkl'
FINAL = ROOT/'lab/v/alloc_dilution.json'
WINDOWS = ((0,30),(30,100),(100,200),(200,300),(0,300))
WTOL, BTOL, GAP = 1e-10, 1e-9, 1e-12
SHARE = .01


def probability(w,q):
    # Code order mirrors grownet: default + Python sum of awake stream products.
    active = np.flatnonzero(np.isfinite(q[1:]))+1
    den = float(w[0])+sum(float(w[j]) for j in active)
    return (float(w[0])*float(q[0])+sum(float(w[j])*float(q[j]) for j in active))/den


def bits(p):
    return -math.log2(max(float(p),1e-12))


def update(w,q,letter,saved):
    """Exact implemented BT=1 rule; no unconditional normalization of stored weights."""
    active = np.flatnonzero(np.isfinite(q[1:]))+1
    likelihood = q if letter else 1-q
    pd = float(likelihood[0])
    total = float(w[0])+sum(float(w[j]) for j in active)
    pm = (float(w[0])*pd+sum(float(w[j])*float(likelihood[j]) for j in active))/total
    w[0] *= pd/pm
    for j in active:
        w[j] *= float(likelihood[j])/pm
        saved[j] += math.log2(float(likelihood[j])/pd)
    if len(active):
        even = SHARE*total/(len(active)+1)
        w[0] = (1-SHARE)*w[0]+even
        for j in active:
            w[j] = (1-SHARE)*w[j]+even
    top = float(max(w))
    if top < 1e-6:
        w /= top
    return bits(pm)


def checks():
    # Two awake weights and one sleeper. Label 1 has likelihoods 1/4 and 3/4.
    # Active mass 4: posterior weights 1,3; fixed share .01 gives 1.01,2.99.
    w=np.array([2.,2.,7.]);s=np.zeros(3)
    loss=update(w,np.array([.25,.75,np.nan]),1,s)
    assert np.max(abs(w-np.array([1.01,2.99,7.]))) < 1e-14
    assert loss == 1. and w[2] == 7. and abs(w.sum()-11.)<1e-14
    a=np.array([1.,3.,9.]);b=a.copy();sa=np.zeros(3);sb=sa.copy()
    q=np.array([.3,.6,np.nan])
    for letter in (0,1,1,0):
        assert update(a,q,letter,sa)==update(b,q.copy(),letter,sb)
    assert np.array_equal(a,b) and np.array_equal(sa,sb)
    return dict(hand_update=True,sleepers_unchanged=True,mass_conservation_BT1=True,null_forecast_difference=True)


def chronology(life):
    """Taste.issued is call order, not a timestamp. Process tastes after that issued call."""
    grouped={}
    last=-1
    for t in life['tastes']:
        i=-1 if t['issued'] is None else t['issued']
        assert last <= i < len(life['predictions'])
        grouped.setdefault(i,[]).append(t)
        last=i
    for t in grouped.get(-1,[]):
        yield 'taste',t
    for i,p in enumerate(life['predictions']):
        yield 'prediction',p
        for t in grouped.get(i,[]):
            yield 'taste',t


def validate(life,final):
    w=np.ones(len(life['names']));saved=np.zeros(len(w))
    err=dict(prediction_weights=0.,taste_weights=0.,probability=0.,per_taste_bits=0.,cumulative_bits=0.,
             final_weights=0.,final_saved=0.,result_total_bits=0.)
    ptotal,rtotal=0.,0.
    npred,ntaste,naccepted=0,0,0
    for kind,row in chronology(life):
        if kind=='prediction':
            npred+=1
            err['prediction_weights']=max(err['prediction_weights'],float(np.max(abs(w-row['w']))))
            err['probability']=max(err['probability'],abs(probability(w,row['q'])-row['p1']))
        else:
            ntaste+=1
            err['taste_weights']=max(err['taste_weights'],float(np.max(abs(w-row['entry']['w']))))
            if row['accepted']:
                naccepted+=1
                got=update(w,row['scored_q'],row['letter'],saved)
                actual=row['actual_scored_bits']
                ptotal+=got;rtotal+=actual
                err['per_taste_bits']=max(err['per_taste_bits'],abs(got-actual))
                err['cumulative_bits']=max(err['cumulative_bits'],abs(ptotal-rtotal))
        assert max(err['prediction_weights'],err['taste_weights'],err['probability'])<=WTOL,err
        assert max(err['per_taste_bits'],err['cumulative_bits'])<=BTOL,err
    by={s['kind']:s for s in final['streams']}
    target=np.array([by['_default']['w']]+[by[n]['w'] for n in life['names'][1:]])
    targets=np.array([0.]+[by[n]['saved'] for n in life['names'][1:]])
    err['final_weights']=float(np.max(abs(w-target)))
    err['final_saved']=float(np.max(abs(saved-targets)))
    err['result_total_bits']=abs(ptotal-life['result'][7]*naccepted)
    assert err['final_weights']<=WTOL and err['final_saved']<=BTOL and err['result_total_bits']<=BTOL,err
    return dict(errors=err,predictions=npred,tastes=ntaste,accepted=naccepted,replayed_bits=ptotal,
                recorded_bits=rtotal,final_mass=float(w.sum())),w,saved


PAIR_I,PAIR_J=np.triu_indices(168,1)


def comparison(w,v,q,do_pairs=False):
    norm=lambda a:a/a.sum()
    p,pv=probability(w,q),probability(v,q)
    nw,nv=norm(w),norm(v)
    awake=np.isfinite(q)
    aw,av=w*awake,v*awake
    aw,av=norm(aw),norm(av)
    changed=(p>.5)!=(pv>.5)
    near=abs(p-.5)<=GAP or abs(pv-.5)<=GAP
    result=dict(dp=pv-p,abs_dp=abs(pv-p),choice_changed=int(changed),near_half=int(near),
                changed_near_half=int(changed and near),clear_choice_changed=int(changed and not near),
                stored_TV=float(.5*np.abs(nw-nv).sum()),active_TV=float(.5*np.abs(aw-av).sum()),
                stored_top_changed=int(np.argmax(w)!=np.argmax(v)),active_top_changed=int(np.argmax(aw)!=np.argmax(av)),
                stored_top=(int(np.argmax(w)),int(np.argmax(v))),active_top=(int(np.argmax(aw)),int(np.argmax(av))))
    if do_pairs:
        # Normalize over streams only for a scale-independent relative gap.
        a,b=norm(w[1:]),norm(v[1:])
        da,db=a[PAIR_I]-a[PAIR_J],b[PAIR_I]-b[PAIR_J]
        clear_a,clear_b=np.abs(da)>GAP,np.abs(db)>GAP
        clear=clear_a&clear_b
        result['pairs']=dict(all=len(da),distinguishable=int(clear.sum()),
                             tied_original=int((~clear_a).sum()),tied_corrected=int((~clear_b).sum()),
                             tied_either=int((~clear).sum()),reversed=int(((da*db<0)&clear).sum()))
    return result,p,pv


def summarize(records):
    if not records:
        return dict(n=0)
    out=dict(n=len(records))
    for key in ('abs_dp','stored_TV','active_TV'):
        out[key]=dict(mean=float(np.mean([r[key] for r in records])),maximum=max(r[key] for r in records))
    for key in ('choice_changed','near_half','changed_near_half','clear_choice_changed','stored_top_changed','active_top_changed'):
        out[key]=sum(r[key] for r in records)
    out['mean_signed_probability_change']=float(np.mean([r['dp'] for r in records]))
    out['top_identity_pairs']={kind:[] for kind in ('stored_top','active_top')}
    for kind in out['top_identity_pairs']:
        pairs=sorted(set(tuple(r[kind]) for r in records))
        out['top_identity_pairs'][kind]=[dict(original=p[0],corrected=p[1],n=sum(tuple(r[kind])==p for r in records)) for p in pairs]
    losses=[r['dloss'] for r in records if 'dloss' in r]
    if losses:
        out['loss_corrected_minus_original']=dict(n=len(losses),signed_total=sum(losses),absolute_total=sum(abs(z) for z in losses),
                                                  mean=float(np.mean(losses)),maximum_absolute=max(abs(z) for z in losses))
    if 'pairs' in records[0]:
        out['pairs']={k:sum(r['pairs'][k] for r in records) for k in records[0]['pairs']}
        out['pairs']['reversal_rate']=out['pairs']['reversed']/out['pairs']['distinguishable'] if out['pairs']['distinguishable'] else None
    return out


def corrected(life,final_w,final_saved):
    w=np.ones(len(life['names']));v=w.copy();s=np.zeros(len(w));sv=s.copy()
    predictions,tastes=[],[]
    current=None
    affected=0
    for kind,row in chronology(life):
        if kind=='prediction':
            m,p,pv=comparison(w,v,row['q'])
            m['t']=row['t'];predictions.append(m)
            current=(p,pv)
        else:
            # Ranking/weight comparison at every taste, not only accepted ones.
            m,_,_=comparison(w,v,row['entry']['q'],True)
            m['t']=row['t'];m['accepted']=row['accepted']
            if row['accepted']:
                assert current is not None,'Accepted taste lacks an issued forecast'
                p,pv=current
                m['dloss']=bits(pv if row['letter'] else 1-pv)-bits(p if row['letter'] else 1-p)
                # Associated issued choices can differ from entry choices in another recording.
                m['associated_issued_dp']=pv-p
                qsame=np.array_equal(row['scored_q'],row['entry']['q'],equal_nan=True)
                affected+=not qsame
                update(w,row['scored_q'],row['letter'],s)
                update(v,row['entry']['q'],row['letter'],sv)
            tastes.append(m)
    assert np.max(abs(w-final_w))<=WTOL and np.max(abs(s-final_saved))<=BTOL
    windows=[]
    for lo,hi in WINDOWS:
        pp=[r for r in predictions if lo<=r['t']<hi]
        tt=[r for r in tastes if lo<=r['t']<hi]
        aa=[r for r in tt if r['accepted']]
        windows.append(dict(window=[lo,hi],predictions=summarize(pp),all_tastes=summarize(tt),accepted_tastes=summarize(aa)))
    nw,nv=w/w.sum(),v/v.sum()
    streams=[dict(name=name,family=life['families'][j],original_weight=float(w[j]),corrected_weight=float(v[j]),
                  weight_change=float(v[j]-w[j]),original_share=float(nw[j]),corrected_share=float(nv[j]),
                  original_saved=float(s[j]),corrected_saved=float(sv[j]),saved_change=float(sv[j]-s[j])) for j,name in enumerate(life['names'])]
    return dict(rule=life['rule'],first=life['first'],seed=life['seed'],windows=windows,streams=streams,
                affected_accepted_tastes=affected,final_stored_TV=float(.5*abs(nw-nv).sum()),
                final_top_original=life['names'][int(np.argmax(w))],final_top_corrected=life['names'][int(np.argmax(v))])


def provenance():
    paths=['lab/scoring_order_replay.py','lab/grownet.py','lab/teach.py','lab/active_mixture_audit.py',
           'lab/v/active_mixture_audit.json']
    return dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip(),
                dirty=subprocess.check_output(['git','status','--short'],text=True,cwd=ROOT),
                inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (RAW,FINAL)},
                source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
                command='OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/scoring_order_replay.py',
                environment={k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')})


def main():
    start=time.monotonic()
    out=dict(provenance=provenance(),checks=checks(),tolerances=dict(weights_probabilities=WTOL,bits=BTOL,relative_pair_gap=GAP),
             validation=[],lives=[],failures=[])
    try:
        raw=pickle.loads(RAW.read_bytes());final=json.loads(FINAL.read_text())['lives']
        lives=[l for l in raw['lives'] if l['observe']]
        validated=[]
        # All four original replays must pass before running any corrected branch.
        for life in lives:
            match=next(l for l in final if (l['rule'],l['seed'],l['first'])==(life['rule'],life['seed'],life['first']))
            v,w,s=validate(life,match)
            out['validation'].append(dict(rule=life['rule'],first=life['first'],**v))
            validated.append((life,w,s))
            print('VALIDATED',life['rule'],life['first'],v,flush=True)
        for life,w,s in validated:
            result=corrected(life,w,s)
            out['lives'].append(result)
            print('REPLAYED',life['rule'],life['first'],result['windows'][-1],flush=True)
    except Exception as e:
        out['failures'].append(dict(type=type(e).__name__,message=str(e)))
        raise
    finally:
        out['wall_s']=time.monotonic()-start
        BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
        print('wall_s',out['wall_s'],flush=True)


if __name__=='__main__':main()
