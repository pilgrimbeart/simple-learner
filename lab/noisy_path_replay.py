"""D73 follow-on: isolate selector dynamics and ordinal readout on fixed recorded histories.

All fits are causal: predict, then update from the brain's own vouched inferred letter.
Neither hidden state nor actual eaten colour enters a fitted readout. Raw signed sums have
supplied memory scales and a supplied feature; these are diagnostic priors, not a new design.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import pickle
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from noisy_path_audit import TAUS, jsonable, logloss, replay


def mix(q, y, train, share, scored=None):
    """Sleeping-expert likelihood update with the current brain's total-preserving share rule."""
    w = np.ones(q.shape[1])
    result, tops = [], []
    if scored is None:
        scored = q
    for row, score_row, target, learn in zip(q, scored, y, train):
        on = np.isfinite(row)
        total = w[on].sum()
        p = float(w[on] @ row[on] / total)
        result.append(p)
        tops.append(float(w[on].max()/total))
        if learn:
            on = np.isfinite(score_row)
            total = w[on].sum()
            lik = np.where(target, score_row[on], 1-score_row[on])
            pred = w[on] @ lik / total
            w[on] *= lik / pred
            if on.sum()>1:
                w[on] = (1-share)*w[on] + share*total/on.sum()
            w /= w.max()
    return np.asarray(result), np.asarray(tops)


def kt_readout(x, y, train, kind):
    """Independent Beta(.5,.5) probabilities on sign or rounded value; no orientation supplied."""
    indices = (x > 0).astype(int) if kind == "sign" else np.clip(np.rint(x),-7,7).astype(int)+7
    n = np.full((2 if kind == "sign" else 15, 2), .5)
    out = []
    for index, target, learn in zip(indices, y, train):
        out.append(n[index,1]/n[index].sum())
        if learn:
            n[index,target] += 1
    return np.asarray(out)


def pair_summary(rows, period, category, key, base):
    seeds = sorted({r["seed"] for r in rows})
    vals = np.array([np.mean([r[period][category][key] for r in rows if r["seed"]==s]) for s in seeds])
    refs = np.array([np.mean([r[period][category][base] for r in rows if r["seed"]==s]) for s in seeds])
    indices=np.random.default_rng(73).integers(len(seeds),size=(10000,len(seeds)))
    return dict(mean=float(vals.mean()), minus_brain=float((vals-refs).mean()),
                ci95=np.quantile((vals-refs)[indices].mean(1),[.025,.975]).tolist())


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--record",default=str(Path(__file__).parent/"v/noisy_path_scoring.pkl"))
    ap.add_argument("--out",default=str(Path(__file__).parent/"v/noisy_path_replay.json"))
    a=ap.parse_args()
    with open(a.record,"rb") as f:
        data=pickle.load(f)
    out=[]
    for life in data["lives"]:
        rows=life["rows"]
        t=np.array([r["t"] for r in rows])
        y=np.array([r["truth"] for r in rows])
        z=np.array([r["inferred_eye"] ^ (r["value"]<0) for r in rows],dtype=int)
        train=np.array([r["vouched"] for r in rows])
        q=np.stack([r["q"] for r in rows])
        scored=np.stack([r["scored_q"] for r in rows])
        brain=np.array([r["p1"] for r in rows])
        _, _, raw=replay(life)
        predictions={"brain":brain}
        predictions["replayed_share"], _=mix(q,z,train,.01,scored=scored)
        mismatch=float(np.max(np.abs(predictions["replayed_share"]-brain)))
        assert mismatch<1e-10, mismatch
        predictions["no_share"],_=mix(q,z,train,0.,scored=scored)
        predictions["score_before_learning"],_=mix(q,z,train,.01)
        actions={}
        native_error = None
        if rows[0].get("signed_bank"):
            j=list(TAUS).index(16.)
            native=np.array([r["signed_bank"][16.]["raw"] for r in rows])
            native_error=float(np.max(np.abs(native-raw["all"][:,j])))
            assert native_error<1e-8, native_error
            symbol=np.array([r["signed_bank"][16.]["symbol"] for r in rows])
            actions["native_symbol_16s"]=np.where(symbol==7,.5,symbol>7)
            predictions["native_root_16s"]=np.array([r["signed_bank"][16.]["root_q"] for r in rows])
            # Same stored symbols, different sharing of their evidence. An independent
            # replay of the 15-bin counts must first reproduce the actual native root.
            native_bins=kt_readout(symbol-7,z,train,"bins")
            np.testing.assert_allclose(native_bins,predictions["native_root_16s"],atol=1e-13,rtol=0)
            predictions["native_pooled_16s"]=kt_readout(symbol-7,z,train,"sign")
            col=life["names"].index(f"lbldt{j}")
            predictions["native_selected_16s"]=np.nan_to_num(q[:,col],nan=.5)
        for source in ("all","gated"):
            for kind in ("sign","bins"):
                qs=[]
                for j,tau in enumerate(TAUS):
                    name=f"{source}_{kind}_{tau:g}s"
                    val=kt_readout(raw[source][:,j],z,train,kind)
                    predictions[name]=val
                    qs.append(val)
                qsmall=np.stack(qs,axis=1)
                for share in (0.,.01):
                    label=f"{source}_{kind}_bank_share{share:g}"
                    predictions[label],_=mix(qsmall,z,train,share)
                # Insert the same seven causal predictors into the existing full expert population.
                augmented=np.column_stack([q,qsmall])
                predictions[f"{source}_{kind}_added_to_full"],_=mix(augmented,z,train,.01)
            j=list(TAUS).index(16.)
            x=raw[source][:,j]
            actions[f"raw_{source}_16s"]=x>0
            # Zero bins abstain: one neutral tie draws half a correct decision in expectation.
            rounded=np.clip(np.rint(x),-7,7)
            actions[f"rounded_{source}_16s"]=np.where(rounded==0,.5,rounded>0)
        actions.update({k:v>.5 for k,v in predictions.items()})
        result=dict(seed=life["seed"],first=life["first"],replay_max_error=mismatch,native_raw_max_error=native_error)
        for period,start in (("whole",0), ("last_two_thirds",1/3), ("last_third",2/3)):
            use=t>=life["seconds"]*start
            learn=use & train
            m=dict(accuracy={},letter_loss={})
            for k,p in actions.items():
                m["accuracy"][k]=float(np.where(y[use],p[use],1-p[use]).mean())
            for k,p in predictions.items():
                m["letter_loss"][k]=float(logloss(p[learn],z[learn]).mean())
            # Paired evidence for two recommendations on the SAME noisy labels.
            ca=actions["raw_gated_16s"][learn]
            cb=actions["brain"][learn]
            d=(ca==z[learn]).astype(float)-(cb==z[learn]).astype(float)
            ds=(ca==y[learn]).astype(float)-(cb==y[learn]).astype(float)
            m["choice_evidence"]=dict(n=int(learn.sum()),disagreement=float(np.mean(ca!=cb)),
                observed_noisy_advantage=float(d.mean()),hidden_state_advantage=float(ds.mean()),
                bsc_predicted_advantage=float(.3*ds.mean()),
                # Only a scale estimate: independence/stationarity fail in the real time series.
                iid_n_for_z1_96=float(1.96**2*(np.mean(d*d)-d.mean()**2)/d.mean()**2) if d.mean()!=0 else None)
            result[period]=m
        out.append(result)
    summary={}
    for period in ("whole","last_two_thirds","last_third"):
        summary[period]={cat:{k:pair_summary(out,period,cat,k,"brain") for k in out[0][period][cat]}
                         for cat in ("accuracy","letter_loss")}
    payload=dict(raw_record=str(Path(a.record).resolve()),
                 record_sha256=hashlib.sha256(Path(a.record).read_bytes()).hexdigest(),
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 record_provenance=data["provenance"],config=data["config"],per_life=out,summary=summary)
    Path(a.out).write_text(json.dumps(payload,indent=2,default=jsonable)+"\n")
    keep=("brain","no_share","score_before_learning","raw_all_16s","rounded_all_16s","raw_gated_16s","rounded_gated_16s",
          "all_sign_16s","all_bins_16s","gated_sign_16s","gated_bins_16s",
          "gated_sign_bank_share0","gated_sign_bank_share0.01","gated_sign_added_to_full",
          "gated_bins_bank_share0.01","gated_bins_added_to_full")
    for period in summary:
        print(period,flush=True)
        for k in keep:
            r=summary[period]["accuracy"][k]
            print(f"  {k:32s} accuracy {r['mean']:.4f}; difference {r['minus_brain']:+.4f}, CI {r['ci95']}",flush=True)
        for k in ("native_symbol_16s","native_root_16s","native_selected_16s","native_pooled_16s"):
            if k in summary[period]["accuracy"]:
                print(k,summary[period]["accuracy"][k],flush=True)
    print("replay_max_error",max(r["replay_max_error"] for r in out))


if __name__=="__main__":
    main()
