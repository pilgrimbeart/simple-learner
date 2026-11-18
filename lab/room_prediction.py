"""D93: is extra room's gain in the streams' forecasts or in whom the mixture trusts?

Reruns D77's four allowance settings on its ten seq-17 pairs with a passive recorder of every stream's issued
forecast at the last prediction before each accepted taste, checks each life reproduces D77's recorded result,
then recombines the recorded forecasts offline.
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/room_prediction.py --check
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/room_prediction.py --run
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/room_prediction.py --analyse
"""
import hashlib
import json
import math
from pathlib import Path
import pickle
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
import numpy as np
import noisy_resource_observe as O
from noisy_resource_ablate10 import SETTINGS, SEEDS

BASE = ROOT / "lab/v/room_prediction"
ABLATE = ROOT / "lab/v/noisy_resource_ablate10.json"
CLIP = 1e-12
FAMS = ("event", "clock", "integrator", "rhythm")


class Recorder:
    """Wraps says/predict/learn/taste only to copy values; changes nothing the brain reads."""

    def __init__(self, lf):
        import grownet
        b = self.b = lf.brain
        assert all(type(n).says is grownet.Net.says for n in b.nets)
        self.fam = np.array([O.family(n.kind) for n in b.nets])
        self.rows, self.issuing, self.last, self.letter = [], None, None, None
        for j, n in enumerate(b.nets):
            self._wrap(n, j)
        predict, taste = b.predict, b.taste

        def _predict():
            m = len(b.nets)
            row = dict(t=float(b.t), wd=float(getattr(b, "w_def", 1.)), pd=float(b._pdef(1)), w=np.zeros(m), q=np.full(m, np.nan),
                       grown=np.zeros(m, bool), span=np.zeros(m, np.int16))
            self.issuing = row
            try:
                r = predict()
            finally:
                self.issuing = None
            row["p1"] = float(b.p1)
            awake = np.isfinite(row["q"])
            rec = (row["wd"] * row["pd"] + np.dot(row["w"][awake], row["q"][awake])) / (row["wd"] + row["w"][awake].sum())
            assert abs(rec - row["p1"]) <= 1e-12, ("issued mixture reconstruction", rec, row["p1"])
            self.last = row
            return r

        def _taste(value, at):
            before = getattr(b, "ntaste", 0)
            self.letter = None
            issued = self.last                  # frozen at entry: taste() itself predicts again after learning
            r = taste(value, at)
            if getattr(b, "ntaste", 0) - before:
                assert issued is not None and self.letter is not None
                self.rows.append(dict(issued, letter=self.letter, taste_t=float(b.t + at)))
            return r
        b.predict, b.taste = _predict, _taste

    def _wrap(self, n, j):
        says, learn = n.says, n.learn

        def _says(i):
            r = says(i)
            row = self.issuing
            if row is not None:
                k = r[0]
                row["w"][j] = getattr(n, "w", 1.)
                if k is not None:
                    row["q"][j] = self.b._pk(n, k, 1)
                    row["grown"][j] = n.units[k]["sym"] is None
                    row["span"][j] = n.units[k]["span"]
            return r

        def _learn(i, letter, t, speaker, firing):
            if self.letter is None:
                self.letter = int(letter)
            assert self.letter == letter
            return learn(i, letter, t, speaker, firing)
        n.says, n.learn = _says, _learn


def one(job):
    import stage3_random as R
    import teach as T
    import ladders as L
    from stage2_lang import arms as S
    name, seed, first = job
    P, event_P = SETTINGS[name]
    R._init(.0025, False)
    original, out = S.live, {}

    def live(lf, secs):
        b = lf.brain
        assert len(b.nets) == 168 and lf.t == 0
        if event_P is not None:
            for n in b.nets:
                if O.family(n.kind) == "event":
                    n.P = n.base = event_P
        rec = Recorder(lf)
        lived = original(lf, secs)
        out.update(rows=rec.rows, fam=rec.fam.tolist())
        return lived
    S.live = live
    try:
        res = T.job((L.seq(17), O.ARM, P, seed, first, O.SECS))
    finally:
        S.live = original
    return dict(name=name, seed=seed, first=first, result=list(res[:5]) + [None] + list(res[6:]), **out)


def identity(res):
    """Each life's result equals D77's JSON record: behaviour fields exactly (after the same JSON round trip),
    the bits-per-taste diagnostic within 1e-12 (its known 1-ulp variation, D77)."""
    ref = {(r["name"], r["seed"], r["first"]): r["result"] for r in json.loads(ABLATE.read_text())["lives"]}
    bad = []
    for r in res:
        a, b = json.loads(json.dumps(r["result"])), ref[r["name"], r["seed"], r["first"]]
        if [v for i, v in enumerate(a) if i not in (5, 7)] != [v for i, v in enumerate(b) if i not in (5, 7)] or abs(a[7] - b[7]) > 1e-12:
            bad.append((r["name"], r["seed"], r["first"]))
    return bad


def recheck():
    data = pickle.loads(BASE.with_suffix(".pkl").read_bytes())
    mism = identity(data["lives"])
    data["summary"]["identity"] = dict(lives=len(data["lives"]), mismatches=mism,
        note="rechecked from the saved capture after a list/tuple comparison error in the first check")
    BASE.with_suffix(".pkl").write_bytes(pickle.dumps(data))
    BASE.with_name(BASE.name + "_capture").with_suffix(".json").write_text(json.dumps(data["summary"], indent=1) + "\n")
    print("identity", "PASS" if not mism else f"FAIL {mism}", flush=True)
    assert not mism


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run():
    t0 = time.monotonic()
    jobs = [(n, s, c) for n in SETTINGS for s in SEEDS for c in ("red", "blue")]
    with ProcessPoolExecutor(8) as ex:
        res = list(ex.map(one, jobs))
    mism = identity(res)
    out = dict(identity=dict(lives=len(res), mismatches=mism), wall_s=time.monotonic() - t0,
               provenance=dict(revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                               dirty=subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
                               source_sha256={p: digest(ROOT / p) for p in ("lab/room_prediction.py", "lab/noisy_resource_ablate10.py",
                                                                            "lab/noisy_resource_observe.py", "lab/grownet.py")},
                               reference_sha256=digest(ABLATE)))
    BASE.with_suffix(".pkl").write_bytes(pickle.dumps(dict(lives=res, summary=out)))
    BASE.with_name(BASE.name + "_capture").with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print("identity", "PASS" if not mism else f"FAIL {mism}", "wall", out["wall_s"], flush=True)
    assert not mism


def loss(p, y):
    return -math.log2(min(1 - CLIP, max(CLIP, p if y else 1 - p)))


def err(p, y):
    return .5 if p == .5 else float((p > .5) != bool(y))


def bayes(rows, keep, share=0.0):
    """Fresh specialist Bayes mixture over the default and the streams selected by keep, on accepted tastes only;
    sleepers abstain and keep their weight (Freund et al. 1997). Returns issued probabilities."""
    m = len(keep)
    w, wd, out = np.ones(m), 1., []
    for r in rows:
        awake = np.isfinite(r["q"]) & keep
        q = r["q"][awake]
        W0 = wd + w[awake].sum()
        p = (wd * r["pd"] + np.dot(w[awake], q)) / W0
        out.append(p)
        y = r["letter"]
        lik = lambda x: x if y else 1 - x
        pm = lik(p)
        wd *= lik(r["pd"]) / pm
        w[awake] *= np.array([lik(x) for x in q]) / pm
        if share and awake.any():
            k = awake.sum() + 1
            even = share * W0 / k
            wd = (1 - share) * wd + even
            w[awake] = (1 - share) * w[awake] + even
        top = max(w.max(), wd)
        if top < 1e-6:
            w, wd = w / top, wd / top
    return out


def combiners(life):
    rows = life["rows"]
    fam = np.array(life["fam"])
    ys = [r["letter"] for r in rows]
    c = {"native mixture": [r["p1"] for r in rows],
         "equal-weight speakers": [float(np.mean(np.r_[r["pd"], r["q"][np.isfinite(r["q"])]])) for r in rows],
         "fresh Bayes, all streams": bayes(rows, np.ones(len(fam), bool)),
         "fresh Bayes, event streams only": bayes(rows, fam == "event")}
    # oracle: the single stream (completed by the default when silent) with least total loss in hindsight
    best = None
    for j in range(len(fam)):
        ps = [r["q"][j] if np.isfinite(r["q"][j]) else r["pd"] for r in rows]
        L = sum(loss(p, y) for p, y in zip(ps, ys))
        if best is None or L < best[0]:
            best = (L, ps)
    c["best single stream in hindsight"] = best[1]
    out = {}
    for k, ps in c.items():
        for w, lo in (("full", 0.), ("last_third", 200.)):
            sel = [(p, y) for p, y, r in zip(ps, ys, rows) if r["taste_t"] >= lo]
            out[k, w] = dict(n=len(sel), bits=sum(loss(p, y) for p, y in sel), errors=sum(err(p, y) for p, y in sel))
    ev = fam == "event"
    issued = [(r["grown"][ev & np.isfinite(r["q"])], r["span"][ev & np.isfinite(r["q"])]) for r in rows]
    g = np.concatenate([a for a, s in issued]) if issued else np.array([])
    sp = np.concatenate([s for a, s in issued]) if issued else np.array([])
    rep = dict(event_issued=int(len(g)), event_grown_share=float(g.mean()) if len(g) else None,
               event_mean_span=float(sp.mean()) if len(sp) else None,
               awake_share={f: float(np.mean([np.isfinite(r["q"][fam == f]).mean() for r in rows])) for f in FAMS})
    eff = life["result"][2] / life["result"][3]
    return out, rep, eff


def check():
    rows = [dict(q=np.array([.9, np.nan]), pd=.5, letter=1), dict(q=np.array([np.nan, .2]), pd=.5, letter=0)]
    p = bayes(rows, np.array([True, True]))
    assert abs(p[0] - (.5 + .9) / 2) < 1e-15
    # after a label 1: default weight .5/.7, stream 0 .9/.7; stream 1 asleep keeps weight 1
    wd, w1 = .5 / .7, 1.
    assert abs(p[1] - (wd * .5 + w1 * .2) / (wd + w1)) < 1e-12
    assert bayes(rows, np.array([False, False])) == [.5, .5]
    assert loss(.5, 1) == 1 and err(.5, 0) == .5 and err(.8, 1) == 0
    out = dict(success=True, checks=["specialist Bayes update with abstaining sleepers", "masking", "loss and hard-choice error"])
    BASE.with_name(BASE.name + "_checks").with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out))


def analyse():
    data = pickle.loads(BASE.with_suffix(".pkl").read_bytes())
    assert not data["summary"]["identity"]["mismatches"]
    by = {(l["name"], l["seed"], l["first"]): combiners(l) for l in data["lives"]}
    order = [(s, c) for s in SEEDS for c in ("red", "blue")]
    k = np.random.default_rng(0).integers(0, 10, (2000, 10))
    idx = np.concatenate((2 * k, 2 * k + 1), axis=1)
    names = list(next(iter(by.values()))[0].keys())
    comb = sorted({c for c, w in names}, key=[c for c, w in names].index)
    out = dict(per_setting={}, differences={}, representation={}, behaviour={})
    for s in SETTINGS:
        out["per_setting"][s] = {f"{c} | {w}": dict(
            bits_per_taste=float(sum(by[s, a, b][0][c, w]["bits"] for a, b in order) / sum(by[s, a, b][0][c, w]["n"] for a, b in order)),
            errors_per_taste=float(sum(by[s, a, b][0][c, w]["errors"] for a, b in order) / sum(by[s, a, b][0][c, w]["n"] for a, b in order)))
            for c in comb for w in ("full", "last_third")}
        reps = [by[s, a, b][1] for a, b in order]
        out["representation"][s] = dict(event_grown_share=float(np.mean([r["event_grown_share"] for r in reps])),
                                        event_mean_span=float(np.mean([r["event_mean_span"] for r in reps])),
                                        awake_share={f: float(np.mean([r["awake_share"][f] for r in reps])) for f in FAMS})
    for a, b in (("high", "low"), ("A_low_plus_event", "low"), ("B_high_minus_event", "low"), ("high", "A_low_plus_event")):
        for c in comb:
            for w in ("full", "last_third"):
                for m in ("bits", "errors"):
                    va = np.array([by[a, s, f][0][c, w][m] / by[a, s, f][0][c, w]["n"] for s, f in order])
                    vb = np.array([by[b, s, f][0][c, w][m] / by[b, s, f][0][c, w]["n"] for s, f in order])
                    d = (va - vb)[idx].mean(1)
                    lo, hi = np.quantile(d, [.025, .975])
                    out["differences"][f"{a} - {b} | {c} | {w} | {m}"] = dict(mean=float((va - vb).mean()), ci95=[float(lo), float(hi)])
    bits = np.array([by[s, a, f][0]["native mixture", "last_third"]["bits"] / by[s, a, f][0]["native mixture", "last_third"]["n"]
                     for s in SETTINGS for a, f in order])
    errs = np.array([by[s, a, f][0]["native mixture", "last_third"]["errors"] / by[s, a, f][0]["native mixture", "last_third"]["n"]
                     for s in SETTINGS for a, f in order])
    effs = np.array([by[s, a, f][2] for s in SETTINGS for a, f in order])
    out["behaviour"] = dict(lives=len(effs), corr_eff_vs_last_third_bits=float(np.corrcoef(effs, bits)[0, 1]),
                            corr_eff_vs_last_third_errors=float(np.corrcoef(effs, errs)[0, 1]),
                            mean_final_third_efficiency={s: float(np.mean([by[s, a, f][2] for a, f in order])) for s in SETTINGS})
    out["provenance"] = dict(capture=data["summary"]["provenance"], analysis_sha256=digest(Path(__file__)),
                             pickle_sha256=digest(BASE.with_suffix(".pkl")))
    BASE.with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    for s in SETTINGS:
        print(s, json.dumps(out["representation"][s]))
        for c in comb:
            f, l = out["per_setting"][s][f"{c} | full"], out["per_setting"][s][f"{c} | last_third"]
            print(f"   {c:34s} full {f['bits_per_taste']:.3f} b {f['errors_per_taste']:.3f} e   last third {l['bits_per_taste']:.3f} b {l['errors_per_taste']:.3f} e")
    for k_, v in out["differences"].items():
        if "last_third" in k_ or "full" in k_:
            print(f"{k_:90s} {v['mean']:+.3f} [{v['ci95'][0]:+.3f},{v['ci95'][1]:+.3f}]")
    print("behaviour", json.dumps(out["behaviour"]))


if __name__ == "__main__":
    {"--check": check, "--run": run, "--recheck": recheck, "--analyse": analyse}[sys.argv[1]]()
