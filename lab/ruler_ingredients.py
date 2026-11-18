"""D96: which ingredient lifts the event ruler R: the market (R+M), one grown unit allowed in every other stream
(R+1, cap raised by those units), or both (R+M+1)? Seq 17, seeds 142000-142009, 300 s. Lab variants of
alloc_rules.install; production code unchanged. Recorded with D93's recorder.
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/ruler_ingredients.py --run
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/ruler_ingredients.py --analyse
"""
import json
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
import contest_prediction as CP

BASE = ROOT / "lab/v/ruler_ingredients"
VARIANTS = ("R+M", "R+1", "R+M+1")
SEEDS = range(142000, 142010)


def install(b, variant, G, seed):
    import alloc_rules as A
    st = A.install(b, "M" if "M" in variant else "R", G, seed)      # M: the market's room test; allowances set below
    fixed = {id(n): sum(x["sym"] is not None for x in n.units.values()) for n in b.nets}
    nev = sum(A.is_event(n.kind) for n in b.nets)
    extra = 0
    for n in b.nets:
        if A.is_event(n.kind):
            g = G // nev
        else:
            g = 1 if variant.endswith("+1") else 0
            extra += g
        n.P = n.base = fixed[id(n)] + g
    st["cap"] += extra
    return st


def one(job):
    import stage3_random as R
    import teach as T
    from stage2_lang import arms as S
    variant, seed, first = job
    R._init(.0025, False)
    original, out = S.live, {}

    def live(lf, secs):
        st = install(lf.brain, variant, C.G, seed)
        rec = RP.Recorder(lf)
        lived = original(lf, secs)
        b = lf.brain
        out.update(rows=rec.rows, fam=rec.fam.tolist(), alloc=dict(st),
                   grown={f: sum(sum(x["sym"] is None for x in n.units.values()) for n in b.nets if C.family(n.kind) == f) for f in C.FAM})
        return lived
    S.live = live
    try:
        res = T.job((C.world("seq"), C.ARM, 560, seed, first, C.FAMILIES["seq"][1]))
    finally:
        S.live = original
    return dict(name=variant, rule=variant, seed=seed, first=first, result=list(res[:5]) + [None] + list(res[6:]), **out)


def run():
    t0 = time.monotonic()
    jobs = [(v, s, c) for v in VARIANTS for s in SEEDS for c in ("red", "blue")]
    with ProcessPoolExecutor(8) as ex:
        res = list(ex.map(one, jobs))
    summary = dict(wall_s=time.monotonic() - t0, G=C.G, source_sha256={p: RP.digest(ROOT / p) for p in
                   ("lab/ruler_ingredients.py", "lab/room_prediction.py", "lab/alloc_rules.py", "lab/alloc_compare.py", "lab/grownet.py")})
    BASE.with_suffix(".pkl").write_bytes(pickle.dumps(dict(lives=res, summary=summary)))
    print("wall", summary["wall_s"], flush=True)


def analyse():
    data = pickle.loads(BASE.with_suffix(".pkl").read_bytes())
    lives = data["lives"] + [l for l in pickle.loads(CP.BASE.with_suffix(".pkl").read_bytes())["lives"] if l["name"] == "R"] + \
        [l for l in pickle.loads(RP.BASE.with_suffix(".pkl").read_bytes())["lives"] if l["name"] in ("A_low_plus_event", "high")]
    by = {(l["name"], l["seed"], l["first"]): l for l in lives}
    arms = ("R", "R+M", "R+1", "R+M+1", "A_low_plus_event", "high")
    hist, _ = C.history("seq")
    X = C.closure_samples({a: (lambda s, c, a=a: by[a, s, c]["result"]) for a in arms}, hist, list(SEEDS))
    order = [(s, c) for s in SEEDS for c in ("red", "blue")]
    k = np.random.default_rng(0).integers(0, 10, (2000, 10))
    idx = np.concatenate((2 * k, 2 * k + 1), axis=1)
    comb = {a: [RP.combiners(by[a, s, c]) for s, c in order] for a in arms}
    out = dict(gap_closed={a: C.ci(X[a]) for a in arms}, differences={}, prediction={}, grown={})
    for a in arms:
        n = sum(x[0]["native mixture", "last_third"]["n"] for x in comb[a])
        out["prediction"][a] = {c: dict(bits=sum(x[0][c, "last_third"]["bits"] for x in comb[a]) / n,
                                        errors=sum(x[0][c, "last_third"]["errors"] for x in comb[a]) / n)
                                for c in ("native mixture", "fresh Bayes, event streams only")}
        if "grown" in by[a, 142000, "red"]:
            out["grown"][a] = {f: float(np.mean([by[a, s, c]["grown"][f] for s, c in order])) for f in C.FAM}
            if "alloc" in by[a, 142000, "red"]:
                out["grown"][a]["transfers"] = float(np.mean([by[a, s, c]["alloc"]["transfers"] for s, c in order]))
    for a in arms[1:]:
        out["differences"][f"{a} - R | gap closed"] = C.ci(X[a] - X["R"])
        va = np.array([x[0]["native mixture", "last_third"]["bits"] / x[0]["native mixture", "last_third"]["n"] for x in comb[a]])
        vb = np.array([x[0]["native mixture", "last_third"]["bits"] / x[0]["native mixture", "last_third"]["n"] for x in comb["R"]])
        dd = (va - vb)[idx].mean(1)
        out["differences"][f"{a} - R | native last-third bits per taste"] = dict(mean=float((va - vb).mean()), ci95=[float(x) for x in np.quantile(dd, [.025, .975])])
    out["provenance"] = dict(capture=data["summary"], analysis_sha256=RP.digest(Path(__file__)))
    BASE.with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out["gap_closed"]))
    print(json.dumps(out["prediction"]))
    print(json.dumps(out["grown"]))
    for k_, v in out["differences"].items():
        print(k_, json.dumps(v))


if __name__ == "__main__":
    {"--run": run, "--analyse": analyse}[sys.argv[1]]()
