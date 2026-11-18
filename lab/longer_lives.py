"""D99: M, W (cap 2300) and R+M+1 (D96) at 1000 s on seq 17, seeds 142000-142009, with fresh circuit and told
references; D78's metric and D93's prediction measures.
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/longer_lives.py --run
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/longer_lives.py --analyse
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
import ruler_ingredients as RI

BASE = ROOT / "lab/v/longer_lives"
SEEDS = range(142000, 142010)
SECS = 1000.
ARMS = ("circuit", "vtold", "M", "W", "R+M+1")


def one(job):
    import stage3_random as R
    import teach as T
    import alloc_rules as A
    from stage2_lang import arms as S
    arm, seed, first = job
    R._init(.0025, False)
    if arm in ("circuit", "vtold"):
        res = T.job((C.world("seq"), arm, 0, seed, first, SECS))
        return dict(name=arm, seed=seed, first=first, result=list(res[:5]) + [None] + list(res[6:]))
    original, out = S.live, {}

    def live(lf, secs):
        st = RI.install(lf.brain, arm, C.G, seed) if arm == "R+M+1" else A.install(lf.brain, arm, C.G, seed)
        rec = RP.Recorder(lf)
        lived = original(lf, secs)
        b = lf.brain
        out.update(rows=rec.rows, fam=rec.fam.tolist(), alloc=dict(st),
                   grown={f: sum(sum(x["sym"] is None for x in n.units.values()) for n in b.nets if C.family(n.kind) == f) for f in C.FAM})
        return lived
    S.live = live
    try:
        res = T.job((C.world("seq"), C.ARM, 560, seed, first, SECS))
    finally:
        S.live = original
    return dict(name=arm, seed=seed, first=first, result=list(res[:5]) + [None] + list(res[6:]), **out)


def run():
    t0 = time.monotonic()
    jobs = [(a, s, c) for a in ARMS[::-1] for s in SEEDS for c in ("red", "blue")]
    with ProcessPoolExecutor(8) as ex:
        res = list(ex.map(one, jobs, chunksize=1))
    BASE.with_suffix(".pkl").write_bytes(pickle.dumps(dict(lives=res, wall_s=time.monotonic() - t0, G=C.G,
        source_sha256={p: RP.digest(ROOT / p) for p in ("lab/longer_lives.py", "lab/ruler_ingredients.py", "lab/room_prediction.py",
                                                         "lab/alloc_rules.py", "lab/grownet.py")})))
    print("wall", time.monotonic() - t0, flush=True)


def analyse():
    d = pickle.loads(BASE.with_suffix(".pkl").read_bytes())
    by = {(l["name"], l["seed"], l["first"]): l for l in d["lives"]}
    ref = {(a, 0, s, c): by[a, s, c]["result"] for a in ("circuit", "vtold") for s in SEEDS for c in ("red", "blue")}
    arms = ("M", "W", "R+M+1")
    X = C.closure_samples({a: (lambda s, c, a=a: by[a, s, c]["result"]) for a in arms}, ref, list(SEEDS))
    out = dict(gap_closed={a: C.ci(X[a]) for a in arms},
               differences={"R+M+1 - W": C.ci(X["R+M+1"] - X["W"]), "R+M+1 - M": C.ci(X["R+M+1"] - X["M"]), "W - M": C.ci(X["W"] - X["M"])},
               per_arm={})
    order = [(s, c) for s in SEEDS for c in ("red", "blue")]
    for a in arms:
        rr = [by[a, s, c] for s, c in order]
        comb = []
        for r in rr:                       # last third of a 1000 s life
            rows = r["rows"]
            ys = [x["letter"] for x in rows]
            sel = [(x["p1"], y) for x, y in zip(rows, ys) if x["taste_t"] >= 2 * SECS / 3]
            comb.append((sum(RP.loss(p, y) for p, y in sel), sum(RP.err(p, y) for p, y in sel), len(sel)))
        n = sum(c[2] for c in comb)
        out["per_arm"][a] = dict(native_last_third_bits=sum(c[0] for c in comb) / n, native_last_third_errors=sum(c[1] for c in comb) / n,
                                 grown={f: float(np.mean([r["grown"][f] for r in rr])) for f in C.FAM},
                                 transfers=float(np.mean([r["alloc"]["transfers"] for r in rr])),
                                 won=float(np.mean([r["alloc"]["won"] for r in rr])))
    out["provenance"] = dict(wall_s=d["wall_s"], source_sha256=d["source_sha256"], analysis_sha256=RP.digest(Path(__file__)))
    BASE.with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"--run": run, "--analyse": analyse}[sys.argv[1]]()
