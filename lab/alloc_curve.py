"""D78 follow-up: a material curve under an enforced cap. Rules E and W at growth pools G, sequence rung 17,
seeds 176000-176009 (development after stage 2), references re-run on the same seeds.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/alloc_curve.py
"""
import json
import sys
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
import numpy as np
import alloc_compare as C

GS = (258, 1000, 2228)
SEEDS = range(176000, 176010)


def one(job):
    G, rest = job[0], job[1:]
    if G is not None:
        C.G = G                                         # the module constant install() receives, set per call in this worker
    r = C.one(rest)
    r["G"] = G
    return r


def main():
    from concurrent.futures import ProcessPoolExecutor
    t0 = time.monotonic()
    jobs = [(None, "seq", ref, 0, s, c) for ref in ("circuit", "vtold") for s in SEEDS for c in ("red", "blue")]
    jobs += [(G, "seq", rule, 560, s, c) for G in GS for rule in ("E", "W") for s in SEEDS for c in ("red", "blue")]
    with ProcessPoolExecutor(8) as ex:
        res = list(ex.map(one, jobs, chunksize=1))
    by = {(r["G"], r["rule"], r["seed"], r["first"]): r for r in res}
    ref = {(a, 0, s, c): by[None, a, s, c]["result"] for a in ("circuit", "vtold") for s in SEEDS for c in ("red", "blue")}
    getters = {f"{rule}{G}": (lambda s, c, G=G, rule=rule: by[G, rule, s, c]["result"]) for G in GS for rule in ("E", "W")}
    X = C.closure_samples(getters, ref, list(SEEDS))
    summary = {}
    for G in GS:
        for rule in ("E", "W"):
            rr = [by[G, rule, s, c] for s in SEEDS for c in ("red", "blue")]
            summary[f"{rule}{G}"] = dict(C.ci(X[f"{rule}{G}"]), cap=2042 + G,
                                          mean_final_units=float(np.mean([r["final_units"] for r in rr])),
                                          grown={f: float(np.mean([r["grown"][f] for r in rr])) for f in C.FAM},
                                          won=float(np.mean([r["alloc"]["won"] for r in rr])), cpu_s=float(np.mean([r["cpu_s"] for r in rr])))
        summary[f"W{G}-E{G}"] = C.ci(X[f"W{G}"] - X[f"E{G}"])
    for a, b in ((f"W{GS[1]}", f"W{GS[0]}"), (f"W{GS[2]}", f"W{GS[1]}"), (f"E{GS[2]}", f"E{GS[0]}")):
        summary[f"{a}-{b}"] = C.ci(X[a] - X[b])
    for k, v in summary.items():
        extra = "" if "grown" not in v else (f"  cap {v['cap']} units {v['mean_final_units']:.0f} grown " +
                                             " ".join(f"{f} {g:.0f}" for f, g in v["grown"].items()) + f" won {v['won']:.0f} cpu {v['cpu_s']:.0f} s")
        print(f"  {k:12s} {v['median']:+.2f} [{v['ci95'][0]:+.2f},{v['ci95'][1]:+.2f}]{extra}", flush=True)
    out = dict(Gs=GS, seeds=[176000, 176009], summary=summary, lives=res, provenance=C.provenance(), wall_seconds=time.monotonic() - t0)
    (ROOT / "lab/v/alloc_curve.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print("wall_seconds", out["wall_seconds"])


if __name__ == "__main__":
    main()
