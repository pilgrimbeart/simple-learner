"""Independent and causal checks for the D73 diagnostic (no simulator or design changes)."""
from pathlib import Path
import itertools
import json
import math
import pickle
import sys
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from drift_filter import Filter
from noisy_path_audit import filtered_prediction, logloss, replay, TAUS
from noisy_path_replay import kt_readout, mix, pair_summary


def exact(history, now, h=80., e=.35):
    """Enumerate all hidden state paths; no forward recurrence is used."""
    out=np.zeros(2)
    for states in itertools.product((0,1),repeat=len(history)+1):
        weight=.5
        previous_time=None
        for i,(t,c,bad) in enumerate(history):
            if previous_time is not None:
                flip=.5*(1-math.exp(-2*(t-previous_time)/h))
                weight*=flip if states[i]!=states[i-1] else 1-flip
            agrees=(c==states[i])==bad
            weight*=1-e if agrees else e
            previous_time=t
        if history:
            flip=.5*(1-math.exp(-2*(now-history[-1][0])/h))
            weight*=flip if states[-1]!=states[-2] else 1-flip
        out[states[-1]]+=weight
    return out/out.sum()


f=Filter()
f.hs[:],f.qs[:]=80.,.35
history=[]
for t,c,bad in [(1.3,0,False),(2.1,1,True),(20.,1,False),(103.,0,True)]:
    np.testing.assert_allclose(f.p_poison(t),exact(history,t),atol=1e-13,rtol=0)
    p,q=filtered_prediction(f,t)
    assert abs(q-(.35+.3*p))<1e-14
    f.meal(t,c,bad)
    history.append((t,c,bad))
np.testing.assert_allclose(f.p_poison(140.),exact(history,140.),atol=1e-13,rtol=0)
print("PASS: known-parameter filter matches exhaustive hidden-state path enumeration; target conversion checked")

root=Path(__file__).parent/"v"
with (root/"noisy_path_audit.pkl").open("rb") as file:
    original=pickle.load(file)
with (root/"noisy_path_scoring.pkl").open("rb") as file:
    audited=pickle.load(file)
assert [x["fingerprint"] for x in original["lives"]]==[x["fingerprint"] for x in audited["lives"]]
print("PASS: all 8 full-life fingerprints identical after adding score and deletion observers")

different,total,cross=0,0,0
for life in audited["lives"]:
    rows=life["rows"]
    q=np.stack([r["q"] for r in rows])
    scored=np.stack([r["scored_q"] for r in rows])
    v=np.array([r["vouched"] for r in rows])
    z=np.array([r["inferred_eye"] ^ (r["value"]<0) for r in rows],int)
    p,_=mix(q,z,v,.01,scored)
    np.testing.assert_allclose(p,[r["p1"] for r in rows],atol=1e-12,rtol=0)
    pre,_=mix(q[:100],z[:100],v[:100],.01,scored[:100])
    np.testing.assert_array_equal(pre,p[:100])
    _,_,raw=replay(life)
    for kind in ("sign","bins"):
        full=kt_readout(raw["gated"][:,list(TAUS).index(16.)],z,v,kind)
        pre=kt_readout(raw["gated"][:100,list(TAUS).index(16.)],z[:100],v[:100],kind)
        np.testing.assert_array_equal(pre,full[:100])
    for r in rows:
        if not r["vouched"]:
            continue
        total+=1
        different+=int(not np.allclose(r["q"],r["scored_q"],atol=1e-12,rtol=0,equal_nan=True))
        cross+=int(bool(r["cross_deletions"]))
        on=np.isfinite(r["scored_q"])
        pred=r["weights"][on] @ r["scored_q"][on]/r["weights"][on].sum()
        label=r["inferred_eye"] ^ (r["value"]<0)
        assert abs(float(logloss(pred,label))-r["scored_bits"])<1e-10
print("PASS: exact selector and recorded loss replay; prefix invariance for selectors and both online readouts")
print("scored predictions changed by same-taste structural updates:",different,"/",total,
      "; accepted tastes with cross-stream deletions:",cross)

rate=np.mean([r["ntaste"]/r["seconds"] for r in audited["lives"]])
e,h=.35,1/80
a,b=1-2*e,2*h
tau=1/math.sqrt(b*b+2*rate*a*a*b)
print("Approximation only: stationary exogenous Poisson accepted meals, independent errors, symmetric Markov state")
print("accepted meals/s",rate,"SNR-maximising linear memory seconds",tau)
print("R_tau=sum(exp(-age/tau)*signed_letter); E[R_tau|state=+1]=rate*a*tau/(1+b*tau)")
print("Var(R_tau|state)=rate*tau/2 + rate**2*a**2*tau**2*b*tau/(1+b*tau)**2")
print("This maximises mean/sd, not a proven decision-accuracy optimum, and is not fitted or given to a brain.")

with (root/"noisy_signed_replay.json").open() as file:
    signed=json.load(file)
print("Native stored-symbol readout: two groups minus fifteen independent bins, paired by seed")
for period in ("whole","last_third"):
    comparison=pair_summary(signed["per_life"],period,"accuracy","native_pooled_16s","native_root_16s")
    comparison["difference"]=comparison.pop("minus_brain")
    print(period,comparison)
print("Native signed sum versus causal shadow reconstruction: largest error",
      max(r["native_raw_max_error"] for r in signed["per_life"]))

with (root/"noisy_path_audit.json").open() as file:
    audit=json.load(file)
print("Baseline final-third mean noisy-label log losses (accepted tastes):")
for name in ("brain","inferred_gated","actual_all"):
    print(name,np.mean([r["metrics"]["last_third"]["letter_logloss_gated"][name] for r in audit["per_life"]]))
print("Baseline final-third calibration to the accepted inferred letter: bin lower edge, n, mean forecast, observed frequency")
bins={}
for life in audit["per_life"]:
    for lo,n,prob,freq in life["metrics"]["last_third"]["calibration_letter"]:
        total=bins.setdefault(round(lo,2),np.zeros(3))
        total += (n,n*prob,n*freq)
for lo,(n,prob,freq) in sorted(bins.items()):
    print(lo,int(n),prob/n,freq/n)
print("Signed-condition final-third mean noisy-label log losses (accepted tastes):")
for name in ("brain","native_pooled_16s","native_root_16s"):
    print(name,np.mean([r["last_third"]["letter_loss"][name] for r in signed["per_life"]]))
