"""D73: observe the frozen brain at taste delivery, then replay information-matched diagnostics.

Only the already-opened drift rung 35 is used. The observer never supplies data to the brain.
Raw records are local ignored pickles; small summaries and code/config hashes are retained.
Run with OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1.
"""
from __future__ import annotations

import argparse
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
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
import numpy as np

ARM = "net10kc60SFBLMR"
TAUS = np.array([1., 2., 4., 8., 16., 32., 64.])


def jsonable(x):
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, np.generic):
        return x.item()
    raise TypeError(type(x).__name__)


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, default=jsonable).encode()).hexdigest()


def provenance():
    paths = ["lab/noisy_path_audit.py", "lab/grownet.py", "lab/teach.py", "lab/drift_filter.py",
             "lab/stage2_lang/sim.py", "lab/stage2_lang/seconds.py", "lab/story1.py", "lab/table.py",
             "discrete/model.py", "world.py", "units.py", "lab/sealed/heldout_ladder3.json"]
    return dict(revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                dirty=subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
                sha256={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths},
                command=sys.argv, environment={k: os.environ.get(k) for k in
                    ("LB_FINE", "LB_LIVE", "LB_LETTER", "GRADED", "DVOTE", "SURP", "LMIX", "MUSCLE", "EXTRA", "SPLIT")})


def live(lf, seconds, observe=True):
    b, rows = lf.brain, []
    names = ["default"] + [n.kind for n in b.nets]
    original = b.taste
    current, learning = None, None

    def watch_learning(n, j):
        original_learn, original_remove = n.learn, n._remove

        def learn(i, letter, t, speaker, firing):
            nonlocal learning
            previous, learning = learning, n.kind
            if current is not None and speaker is not None:
                current["scored_q"][j] = b._pk(n, speaker, 1)
            try:
                return original_learn(i, letter, t, speaker, firing)
            finally:
                learning = previous

        def remove(k):
            if current is not None and learning is not None and learning != n.kind:
                current["cross_deletions"].append((learning, n.kind, k))
            return original_remove(k)

        n.learn, n._remove = learn, remove

    if observe:
        for j, n in enumerate(b.nets, 1):
            watch_learning(n, j)

    def record(value, at):
        nonlocal current
        end = b.t
        # The existing seconds wrapper will make this same temporary time adjustment.
        # Restore it before invoking that wrapper; all calls here are read-only.
        b.t = end + at
        try:
            vouched = bool(b.vouched())
            eaten = int(b.food) if vouched else int(b.last[1] > b.last[0])
            q = [b._pdef(1)]
            weights = [getattr(b, "w_def", 1.)]
            counts, spans = [getattr(b, "dkt", (0, 0))[1]], [1]
            for n in b.nets:
                k, _ = n.says(b.place(n) - 1)
                q.append(b._pk(n, k, 1) if k is not None else np.nan)
                weights.append(getattr(n, "w", 1.))
                counts.append(sum(n.units[k]["n"]) if k is not None else 0)
                spans.append(n.units[k]["span"] if k is not None else 0)
            actual = int(lf.tick_meals[-1][1])
            assert actual in (0, 1)
            signed_bank = {}
            import grownet
            for j, tau in enumerate(grownet.LB_T):
                n = getattr(b, "byk", {}).get(f"lbldt{j}") if b.byk is not None else None
                if n is not None:
                    val, when = getattr(b, "lbr", {}).get(("ld", j), (0., b.t))
                    symbol = n.hist.get(b.place(n)-1)
                    signed_bank[tau] = dict(raw=val*math.exp(-(b.t-when)/tau), symbol=symbol,
                        root_q=b._pk(n, symbol, 1) if symbol is not None else .5)
            rows.append(dict(t=b.t, value=value, vouched=vouched, inferred_eye=eaten,
                             actual_eye=int(lf.wire_s[actual]), truth=int(lf.wire_s[1-lf.told_now]),
                             food=int(b.food), p1=float(getattr(b, "p1", .5)),
                             q=np.asarray(q), weights=np.asarray(weights), counts=np.asarray(counts),
                             spans=np.asarray(spans), last=list(b.last), last_drive=b.last_drive,
                             scored_q=np.array([q[0]]+[np.nan]*(len(q)-1)), cross_deletions=[], signed_bank=signed_bank))
        finally:
            b.t = end
        n0 = getattr(b, "ntaste", 0)
        current = rows[-1]
        before_bits = getattr(b, "pbits", 0.)
        try:
            answer = original(value, at)
            current["scored_bits"] = getattr(b, "pbits", 0.) - before_bits
        finally:
            current = None
        assert getattr(b, "ntaste", 0) - n0 == int(vouched), "Gate reconstruction differs from actual update"
        return answer

    if observe:
        b.taste = record
    started = time.perf_counter()
    while lf.t * lf.dt < seconds - .5 * lf.dt:
        lf.step()
    state = dict(meals=lf.meals, scored=lf.scored, firings=lf.firings, food=b.food,
                 pbits=getattr(b, "pbits", 0.), ntaste=getattr(b, "ntaste", 0),
                 nets=[(n.kind, n.P, [(k, x["n"], x["span"]) for k, x in n.units.items()]) for n in b.nets],
                 clock_rng=b.crng.bit_generator.state)
    from minimal.spec import Lived, SPAN, spent
    lived = Lived(lf.thirds(lf.t))
    lived.power, lived.firings, lived.substrate = 3.7e-9, lf.THRUST0 * SPAN * len(lf.firings) / seconds, "silicon"
    output = dict(seed=lf.seed, first=lf.first, seconds=seconds, dt=lf.dt, names=names, rows=rows,
                  fingerprint=digest(state), wall_s=time.perf_counter()-started,
                  gain=[a-2*c for a,c,_ in lived], spending=float(spent(lived)),
                  nmeals=len(lf.meals), nfirings=len(lf.firings), pbits=state["pbits"],
                  ntaste=state["ntaste"], allocated=sum(len(n.units) for n in b.nets))
    raise StopIteration(output)


def one(job):
    import stage3_random as R
    import teach as T
    from stage2_lang import arms as S
    text, seed, first, seconds, dt, observe = job
    R._init(dt, False)
    S.live = lambda lf, secs: live(lf, secs, observe)
    try:
        T.job((text, ARM, 2240, seed, first, seconds))
    except StopIteration as e:
        return e.value
    raise RuntimeError("No recording returned")


def logloss(p, y):
    p = np.clip(p, 1e-9, 1-1e-9)
    return -np.log2(np.where(y, p, 1-p))


def filtered_prediction(f, t):
    """Food-eye probability and noisy-letter probability; state 0 poison implies food eye 1."""
    pp = f.post.copy()
    if f.tl is not None:
        change = .5 * (1-np.exp(-2*(t-f.tl)/f.hs))
        pp = pp*(1-change[:, None]) + pp[:, ::-1]*change[:, None]
    w = np.exp(f.logw-f.logw.max())
    w /= w.sum()
    return float(w @ pp[:, 0]), float(w @ (f.qs + (1-2*f.qs)*pp[:, 0]))


def replay(life):
    from drift_filter import Filter
    rows = life["rows"]
    fs = {k: Filter() for k in ("actual_all", "inferred_all", "inferred_gated", "actual_gated")}
    # This parameter-told diagnostic isolates learning h and e from state filtering.
    known = Filter()
    known.hs[:], known.qs[:] = 80., .35
    fs["known_inferred_gated"] = known
    raw = {k: np.zeros(len(TAUS)) for k in ("all", "gated", "actual")}
    predictions = {k: [] for k in fs}
    taste_predictions = {k: [] for k in fs}
    raws = {k: [] for k in raw}
    tl = 0.
    for r in rows:
        t, bad = r["t"], r["value"] < 0
        for k, f in fs.items():
            p, q = filtered_prediction(f, t)
            predictions[k].append(p)
            taste_predictions[k].append(q)
        for k in raw:
            raw[k] *= np.exp(-(t-tl)/TAUS)
            raws[k].append(raw[k].copy())
        for k, f in fs.items():
            if "gated" not in k or r["vouched"]:
                f.meal(t, r["actual_eye"] if k.startswith("actual") else r["inferred_eye"], bad)
        letter = r["inferred_eye"] ^ int(bad)
        true_letter = r["actual_eye"] ^ int(bad)
        raw["all"] += 2*letter-1
        raw["actual"] += 2*true_letter-1
        if r["vouched"]:
            raw["gated"] += 2*letter-1
        tl = t
    return ({k: np.asarray(v) for k,v in predictions.items()},
            {k: np.asarray(v) for k,v in taste_predictions.items()},
            {k: np.asarray(v) for k,v in raws.items()})


def analyse(data):
    per = []
    for life in data["lives"]:
        rows = life["rows"]
        p, fq, raw = replay(life)
        t = np.array([r["t"] for r in rows])
        y = np.array([r["truth"] for r in rows])
        inferred = np.array([r["inferred_eye"] for r in rows])
        actual = np.array([r["actual_eye"] for r in rows])
        bad = np.array([r["value"] < 0 for r in rows])
        v = np.array([r["vouched"] for r in rows])
        z, za = inferred ^ bad, actual ^ bad
        pbrain = np.array([r["p1"] for r in rows])
        q = np.stack([r["q"] for r in rows])
        weights = np.stack([r["weights"] for r in rows])
        active = np.isfinite(q)
        wm = weights*active
        wm /= wm.sum(axis=1, keepdims=True)
        score_p = np.nansum(q*wm, axis=1)
        actions = {"brain": np.array([r["food"] for r in rows]), "score_readout": score_p > .5}
        actions.update({k: val > .5 for k, val in p.items()})
        actions.update({f"raw_{k}_{tau:g}s": val[:,j] > 0 for k,val in raw.items() for j,tau in enumerate(TAUS)})
        result = dict(seed=life["seed"], first=life["first"], n=len(rows), meals_per_s=len(rows)/life["seconds"],
                      vouched_fraction=float(v.mean()), attribution_error=float(np.mean(inferred != actual)),
                      attribution_error_gated=float(np.mean(inferred[v] != actual[v])),
                      false_taste_fraction=float(np.mean(za != y)),
                      inferred_letter_error=float(np.mean(z != y)),
                      inference_noise_gated=float(np.mean(z[v] != y[v])), metrics={})
        for name, start in (("whole",0), ("last_two_thirds",1/3), ("last_third",2/3)):
            use = t >= start*life["seconds"]
            learning = use & v
            m = {"n": int(use.sum()), "n_learning": int(learning.sum()),
                 "accuracy": {k: float(np.mean((a == y)[use])) for k,a in actions.items()},
                 "state_logloss": {k: float(logloss(val[use], y[use]).mean()) for k,val in p.items()},
                 "letter_logloss_gated": {"brain":float(logloss(pbrain[learning], z[learning]).mean()),
                                           "score_readout":float(logloss(score_p[learning], z[learning]).mean())},
                 "calibration_letter": [], "experts": []}
            for k, val in fq.items():
                m["letter_logloss_gated"][k] = float(logloss(val[learning], z[learning]).mean())
            for lo, hi in zip(np.arange(0.,1.,.1), np.arange(.1,1.01,.1)):
                mask=learning & (pbrain>=lo) & (pbrain<hi)
                if mask.any():
                    m["calibration_letter"].append([float(lo),int(mask.sum()),float(pbrain[mask].mean()),float(z[mask].mean())])
            for j, key in enumerate(life["names"]):
                mask=use & active[:,j]
                learnmask=learning & active[:,j]
                if not mask.any():
                    continue
                m["experts"].append(dict(name=key, coverage=float(mask.sum()/use.sum()),
                    accuracy=float(np.mean((q[mask,j]>.5)==y[mask])), weight=float(wm[use,j].mean()),
                    letter_loss=float(logloss(q[learnmask,j],z[learnmask]).mean()) if learnmask.any() else None,
                    mean_count=float(np.mean([r["counts"][j] for r,u in zip(rows,mask) if u]))))
            m["readout_difference_max"] = float(np.max(np.abs(pbrain[use]-score_p[use])))
            result["metrics"][name] = m
        per.append(result)
    # Bootstrap pairs, never individual correlated tastes. Exploratory intervals, only four pairs.
    seeds = sorted({r["seed"] for r in per})
    boot = np.random.default_rng(73).integers(len(seeds), size=(10000,len(seeds)))
    comparisons={}
    for period in ("whole","last_two_thirds","last_third"):
        means={}
        for key in per[0]["metrics"][period]["accuracy"]:
            vals=np.array([np.mean([r["metrics"][period]["accuracy"][key] for r in per if r["seed"]==s]) for s in seeds])
            base=np.array([np.mean([r["metrics"][period]["accuracy"]["brain"] for r in per if r["seed"]==s]) for s in seeds])
            means[key]=dict(accuracy=float(vals.mean()), minus_brain=float((vals-base).mean()),
                            difference_ci95=np.quantile((vals-base)[boot].mean(1),[.025,.975]).tolist())
        comparisons[period]=means
    summary=dict(provenance=data["provenance"], config=data["config"], per_life=per, comparisons=comparisons)
    return summary


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode",choices=("identity","collect","analyse"))
    ap.add_argument("--out",default=str(ROOT/"lab/v/noisy_path_audit"))
    ap.add_argument("--pairs",type=int,default=4)
    ap.add_argument("--seed0",type=int,default=137000)
    ap.add_argument("--seconds",type=float,default=1000.)
    ap.add_argument("--dt",type=float,default=.0025)
    ap.add_argument("--workers",type=int,default=4)
    ap.add_argument("--signed",action="store_true",help="Observe the existing D70 signed-integrator condition")
    a=ap.parse_args()
    out=Path(a.out)
    if a.mode=="analyse":
        with out.with_suffix(".pkl").open("rb") as f:
            data=pickle.load(f)
        summary=analyse(data)
        out.with_suffix(".json").write_text(json.dumps(summary,indent=2,default=jsonable)+"\n")
        print(json.dumps(summary["comparisons"],indent=2),flush=True)
        return
    for key in ("GRADED","DVOTE","SURP","LMIX","MUSCLE","EXTRA","SPLIT"):
        if os.environ.get(key) not in (None,"0"):
            raise ValueError(f"Frozen baseline requires {key} unset")
    if (os.environ.get("LB_LETTER")=="1") != a.signed:
        raise ValueError("LB_LETTER=1 must be accompanied by --signed, and vice versa")
    for key in ("LB_FINE", "LB_LIVE"):
        if os.environ.get(key) != "1":
            raise ValueError(f"Frozen baseline requires {key}=1")
    ladder=json.loads((ROOT/"lab/sealed/heldout_ladder3.json").read_text())
    rung=next(r for r in ladder["rungs"] if r["size"]==35)
    text=rung["text"]
    if a.mode=="identity":
        j=(text,a.seed0,"red",a.seconds,a.dt)
        plain=one((*j,False))
        tapped=one((*j,True))
        assert plain["fingerprint"]==tapped["fingerprint"]
        print(json.dumps(dict(identity=True,seconds=a.seconds,meals=tapped["nmeals"],
                             fingerprint=tapped["fingerprint"],wall_s=plain["wall_s"]+tapped["wall_s"],
                             cross_deletions=sum(len(r["cross_deletions"]) for r in tapped["rows"]))),flush=True)
        return
    jobs=[(text,s,c,a.seconds,a.dt,True) for s in range(a.seed0,a.seed0+a.pairs) for c in ("red","blue")]
    data=dict(provenance=provenance(),config=dict(arm=ARM,P=2240,world=text,seconds=a.seconds,dt=a.dt,
                                               seed0=a.seed0,pairs=a.pairs,workers=a.workers,signed=a.signed),lives=[])
    start=time.perf_counter()
    with ProcessPoolExecutor(a.workers) as ex:
        for result in ex.map(one,jobs):
            data["lives"].append(result)
            print(json.dumps({k:result[k] for k in ("seed","first","wall_s","nmeals","ntaste","fingerprint")}),flush=True)
            with out.with_suffix(".pkl").open("wb") as f:
                pickle.dump(data,f)
    print(json.dumps(dict(completed=len(data["lives"]),wall_s=time.perf_counter()-start)),flush=True)


if __name__=="__main__":
    main()
