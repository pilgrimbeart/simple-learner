"""D100-D102, follow-ups to D93-D99 (one job each, run in turn):
  silent   D100: R and R+1 with every non-event stream silenced in the mixture (they still observe, learn and grow)
  timing   D101: D93's recorder on the unchanged design at P=560 and P=2240, timing rung 3, 3000 s, seeds 142000-142009
  fresh    D102: D93's recorder on low / high (unchanged design P=560 / 4480) and R+M+1, seq 17, fresh seeds 176000-176009
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/followups.py {silent|timing|fresh}
"""
import glob
import json
import math
from pathlib import Path
import pickle
import sys
import time
from concurrent.futures import ProcessPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
import numpy as np
import alloc_compare as C
import room_prediction as RP
import ruler_ingredients as RI

FAMS = ("event", "clock", "integrator", "rhythm")


def silence(b):
    """Non-event streams never speak: their says reports no speaker, everywhere (mixture, learning credit)."""
    for n in b.nets:
        if C.family(n.kind) != "event":
            says = n.says
            n.says = lambda i, _s=says: (None, _s(i)[1])


def one(job):
    import stage3_random as R
    import teach as T
    import alloc_rules as A
    from stage2_lang import arms as S
    exp, arm, P, seed, first = job
    R._init(.0025, False)
    fam = "time" if exp == "timing" else "seq"
    secs = C.FAMILIES[fam][1]
    if arm in ("circuit", "vtold"):
        res = T.job((C.world(fam), arm, 0, seed, first, secs))
        return dict(exp=exp, name=arm, P=0, seed=seed, first=first, result=list(res[:5]) + [None] + list(res[6:]))
    original, out = S.live, {}

    def live(lf, s_):
        b = lf.brain
        base = arm.replace(" silent", "")
        if base == "R":
            st = A.install(b, "R", C.G, seed)
        elif base.startswith("R+"):
            st = RI.install(b, base, C.G, seed)
        else:
            st = A.install(b, "none", C.G, seed)
        if arm.endswith("silent"):
            silence(b)
        rec = RP.Recorder(lf)
        lived = original(lf, s_)
        out.update(rows=rec.rows, fam=rec.fam.tolist(), alloc=dict(st),
                   grown={f: sum(sum(x["sym"] is None for x in n.units.values()) for n in b.nets if C.family(n.kind) == f) for f in FAMS})
        return lived
    S.live = live
    try:
        res = T.job((C.world(fam), C.ARM, P, seed, first, secs))
    finally:
        S.live = original
    return dict(exp=exp, name=arm, P=P, seed=seed, first=first, result=list(res[:5]) + [None] + list(res[6:]), **out)


def measures(life, start):
    """Native, fresh Bayes all streams, event-only and per-family-only, best single in hindsight, equal weights; from `start` s."""
    rows = life["rows"]
    fam = np.array(life["fam"])
    ys = [r["letter"] for r in rows]
    c = {"native": [r["p1"] for r in rows],
         "Bayes all": RP.bayes(rows, np.ones(len(fam), bool)),
         "equal": [float(np.mean(np.r_[r["pd"], r["q"][np.isfinite(r["q"])]])) for r in rows]}
    for f in FAMS:
        c[f"Bayes {f} only"] = RP.bayes(rows, fam == f)
    best = None
    for j in range(len(fam)):
        ps = [r["q"][j] if np.isfinite(r["q"][j]) else r["pd"] for r in rows]
        sel = [(p, y) for p, y, r in zip(ps, ys, rows) if r["taste_t"] >= start]
        L = sum(RP.loss(p, y) for p, y in sel)
        if best is None or L < best[0]:
            best = (L, ps, life["fam"][j])
    c["best single"] = best[1]
    out = {}
    for k, ps in c.items():
        sel = [(p, y) for p, y, r in zip(ps, ys, rows) if r["taste_t"] >= start]
        out[k] = (sum(RP.loss(p, y) for p, y in sel), sum(RP.err(p, y) for p, y in sel), len(sel))
    return out, best[2]


def summarise(by, arms, seeds, start, ref):
    order = [(s, c) for s in seeds for c in ("red", "blue")]
    k = np.random.default_rng(0).integers(0, len(seeds), (2000, len(seeds)))
    idx = np.concatenate((2 * k, 2 * k + 1), axis=1)
    X = C.closure_samples({a: (lambda s, c, a=a: by[a, s, c]["result"]) for a in arms}, ref, list(seeds))
    M = {a: [measures(by[a, s, c], start) for s, c in order] for a in arms}
    per = {}
    for a in arms:
        names = M[a][0][0].keys()
        n = sum(m[0]["native"][2] for m in M[a])
        per[a] = dict(gap_closed=C.ci(X[a]),
                      last_third={k_: (sum(m[0][k_][0] for m in M[a]) / n, sum(m[0][k_][1] for m in M[a]) / n) for k_ in names},
                      best_single_family={f: sum(m[1] == f for m in M[a]) for f in FAMS},
                      grown={f: float(np.mean([by[a, s, c]["grown"][f] for s, c in order])) for f in FAMS})

    def diff(a, b, key):
        va = np.array([m[0][key][0] / m[0][key][2] for m in M[a]])
        vb = np.array([m[0][key][0] / m[0][key][2] for m in M[b]])
        d = (va - vb)[idx].mean(1)
        return dict(mean=float((va - vb).mean()), ci95=[float(x) for x in np.quantile(d, [.025, .975])])
    return per, X, diff


def dump(name, payload):
    p = ROOT / f"lab/v/followup_{name}.json"
    p.write_text(json.dumps(payload, indent=1, default=str) + "\n")
    print(json.dumps(payload, indent=1, default=str))


def go(exp, jobs):
    t0 = time.monotonic()
    with ProcessPoolExecutor(8) as ex:
        res = list(ex.map(one, jobs, chunksize=1))
    (ROOT / f"lab/v/followup_{exp}.pkl").write_bytes(pickle.dumps(res))
    return res, time.monotonic() - t0


def same(a, b):
    a = json.loads(json.dumps(a))
    b = json.loads(json.dumps(b))
    return [v for i, v in enumerate(a) if i not in (5, 7)] == [v for i, v in enumerate(b) if i not in (5, 7)] and abs(a[7] - b[7]) < 1e-12


def silent():
    seeds = range(142000, 142010)
    jobs = [("silent", a, 560, s, c) for a in ("R silent", "R+1 silent") for s in seeds for c in ("red", "blue")]
    res, wall = go("silent", jobs)
    by = {(r["name"], r["seed"], r["first"]): r for r in res}
    for l in pickle.loads((ROOT / "lab/v/contest_prediction.pkl").read_bytes())["lives"]:
        if l["name"] == "R":
            by["R", l["seed"], l["first"]] = l
    for l in pickle.loads((ROOT / "lab/v/ruler_ingredients.pkl").read_bytes())["lives"]:
        if l["name"] == "R+1":
            by["R+1", l["seed"], l["first"]] = l
    hist, _ = C.history("seq")
    arms = ("R", "R+1", "R silent", "R+1 silent")
    per, X, diff = summarise(by, arms, seeds, 200., hist)
    out = dict(per_arm=per, wall_s=wall,
               differences={"R+1 - R": C.ci(X["R+1"] - X["R"]), "R+1 silent - R silent": C.ci(X["R+1 silent"] - X["R silent"]),
                            "R silent - R": C.ci(X["R silent"] - X["R"]), "R+1 silent - R+1": C.ci(X["R+1 silent"] - X["R+1"]),
                            "(R+1 - R) - (R+1 silent - R silent)": C.ci((X["R+1"] - X["R"]) - (X["R+1 silent"] - X["R silent"]))},
               native_bits={"R+1 silent - R silent": diff("R+1 silent", "R silent", "native"), "R+1 - R": diff("R+1", "R", "native")},
               source_sha256={p: RP.digest(ROOT / p) for p in ("lab/followups.py", "lab/ruler_ingredients.py", "lab/room_prediction.py")})
    dump("silent", out)


def timing():
    seeds = range(142000, 142010)
    jobs = [("timing", a, P, s, c) for a, P in (("design560", 560), ("design2240", 2240)) for s in seeds for c in ("red", "blue")]
    res, wall = go("timing", jobs)
    path = glob.glob(str(ROOT / "lab/v/grownet_pair3000_time_3-5-7_10_s142000_*.pkl"))[0]
    hist = {(j[1], j[2], j[3], j[4]): r for j, r in pickle.loads(Path(path).read_bytes()) if j[0] == 3}
    bad = [(r["name"], r["seed"], r["first"]) for r in res if not same(r["result"], hist[C.ARM, r["P"], r["seed"], r["first"]])]
    by = {(r["name"], r["seed"], r["first"]): r for r in res}
    arms = ("design560", "design2240")
    per, X, diff = summarise(by, arms, seeds, 2000., hist)
    out = dict(identity=dict(lives=len(res), mismatches=bad), per_arm=per, wall_s=wall,
               differences={"design2240 - design560": C.ci(X["design2240"] - X["design560"]),
                            **{f"bits {k}": diff("design2240", "design560", k) for k in ("native", "Bayes all", "equal", "best single",
                                                                                         *[f"Bayes {f} only" for f in FAMS])}},
               source_sha256={p: RP.digest(ROOT / p) for p in ("lab/followups.py", "lab/room_prediction.py")}, reference=path)
    dump("timing", out)


def fresh():
    seeds = range(176000, 176010)
    jobs = [("fresh", a, P, s, c) for a, P in (("low", 560), ("high", 4480), ("R+M+1", 560)) for s in seeds for c in ("red", "blue")]
    res, wall = go("fresh", jobs)
    refl = json.loads((ROOT / "lab/v/alloc_curve_ref.json").read_text())["lives"]
    ref_design = {(r["P"], r["seed"], r["first"]): r["result"] for r in refl}
    bad = [(r["name"], r["seed"], r["first"]) for r in res if r["name"] in ("low", "high") and not same(r["result"], ref_design[r["P"], r["seed"], r["first"]])]
    curve = json.loads((ROOT / "lab/v/alloc_curve.json").read_text())["lives"]
    ref = {(r["rule"], 0, r["seed"], r["first"]): r["result"] for r in curve if r["rule"] in ("circuit", "vtold")}
    by = {(r["name"], r["seed"], r["first"]): r for r in res}
    arms = ("low", "high", "R+M+1")
    per, X, diff = summarise(by, arms, seeds, 200., ref)
    out = dict(identity=dict(design_lives_checked=40, mismatches=bad), per_arm=per, wall_s=wall,
               differences={"high - low": C.ci(X["high"] - X["low"]), "R+M+1 - high": C.ci(X["R+M+1"] - X["high"]),
                            **{f"bits high - low | {k}": diff("high", "low", k) for k in ("native", "Bayes all", "equal", "best single", "Bayes event only")},
                            "bits R+M+1 - high | native": diff("R+M+1", "high", "native")},
               source_sha256={p: RP.digest(ROOT / p) for p in ("lab/followups.py", "lab/room_prediction.py", "lab/ruler_ingredients.py")})
    dump("fresh", out)


if __name__ == "__main__":
    {"silent": silent, "timing": timing, "fresh": fresh}[sys.argv[1]]()
