"""D78 follow-up: the unchanged design (rule none: hooks only) at P=560 and P=4480 on seeds 176000-176009, paired
with lab/alloc_curve.py's lives (its JSON supplies circuit, vtold, E and W).
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/alloc_curve_ref.py
"""
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
import numpy as np
import alloc_compare as C

SEEDS = range(176000, 176010)


def main():
    t0 = time.monotonic()
    jobs = [("seq", "none", P, s, c) for P in (560, 4480) for s in SEEDS for c in ("red", "blue")]
    with ProcessPoolExecutor(8) as ex:
        res = list(ex.map(C.one, jobs, chunksize=1))
    curve = json.loads((ROOT / "lab/v/alloc_curve.json").read_text())
    by = {(r["G"], r["rule"], r["seed"], r["first"]): r for r in curve["lives"]}
    for r in res:
        by[r["P"], "none", r["seed"], r["first"]] = r
    ref = {(a, 0, s, c): by[None, a, s, c]["result"] for a in ("circuit", "vtold") for s in SEEDS for c in ("red", "blue")}
    names = {"design560": (560, "none"), "design4480": (4480, "none"), "E2228": (2228, "E"), "W1000": (1000, "W"), "W2228": (2228, "W")}
    X = C.closure_samples({k: (lambda s, c, g=g: by[g[0], g[1], s, c]["result"]) for k, g in names.items()}, ref, list(SEEDS))
    summary = {}
    for k, g in names.items():
        rr = [by[g[0], g[1], s, c] for s in SEEDS for c in ("red", "blue")]
        summary[k] = dict(C.ci(X[k]), mean_final_units=float(np.mean([r["final_units"] for r in rr])),
                          mean_peak=float(np.mean([r["alloc"]["peak"] for r in rr])),
                          grown={f: float(np.mean([r["grown"][f] for r in rr])) for f in C.FAM})
    for a, b in (("design4480", "design560"), ("W2228", "design4480"), ("W1000", "design4480"), ("E2228", "design4480")):
        summary[f"{a}-{b}"] = C.ci(X[a] - X[b])
    for k, v in summary.items():
        extra = "" if "grown" not in v else f"  units {v['mean_final_units']:.0f} peak {v['mean_peak']:.0f} grown " + " ".join(f"{f} {g:.0f}" for f, g in v["grown"].items())
        print(f"  {k:22s} {v['median']:+.2f} [{v['ci95'][0]:+.2f},{v['ci95'][1]:+.2f}]{extra}", flush=True)
    out = dict(seeds=[176000, 176009], summary=summary, lives=res, provenance=C.provenance(), wall_seconds=time.monotonic() - t0)
    (ROOT / "lab/v/alloc_curve_ref.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print("wall_seconds", out["wall_seconds"])


if __name__ == "__main__":
    main()
