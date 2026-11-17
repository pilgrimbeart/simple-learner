"""D78 confirmation: W (G=1000, cap 3042) against the unchanged design, fresh seeds 177000-177009, frozen code.
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/alloc_confirm.py
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
import alloc_curve as K

SEEDS = range(177000, 177010)
DESIGN = {"seq": 4480, "time": 2240}


def main():
    t0 = time.monotonic()
    report = dict(seeds=[177000, 177009], design=DESIGN, G=1000, provenance=C.provenance(), families={})
    for fam in ("seq", "time"):
        jobs = [(None, fam, a, 0, s, c) for a in ("circuit", "vtold") for s in SEEDS for c in ("red", "blue")]
        jobs += [(None, fam, "none", DESIGN[fam], s, c) for s in SEEDS for c in ("red", "blue")]
        jobs += [(1000, fam, "W", 560, s, c) for s in SEEDS for c in ("red", "blue")]
        with ProcessPoolExecutor(8) as ex:
            res = list(ex.map(K.one, jobs, chunksize=1))
        by = {(r["rule"], r["seed"], r["first"]): r for r in res}
        ref = {(a, 0, s, c): by[a, s, c]["result"] for a in ("circuit", "vtold") for s in SEEDS for c in ("red", "blue")}
        X = C.closure_samples({k: (lambda s, c, k=k: by[k, s, c]["result"]) for k in ("none", "W")}, ref, list(SEEDS))
        summ = {"design": C.ci(X["none"]), "W1000": C.ci(X["W"]), "W1000-design": C.ci(X["W"] - X["none"])}
        for k in ("none", "W"):
            rr = [by[k, s, c] for s in SEEDS for c in ("red", "blue")]
            summ[("design" if k == "none" else "W1000")].update(
                final_units=float(np.mean([r["final_units"] for r in rr])), peak=float(np.mean([r["alloc"]["peak"] for r in rr])),
                grown={f: float(np.mean([r["grown"][f] for r in rr])) for f in C.FAM}, cpu_s=float(np.mean([r["cpu_s"] for r in rr])))
        lo = summ["W1000-design"]["ci95"][0]
        summ["claim_as_good_within_.10"] = bool(lo > -.10)
        print(f"== {fam}", flush=True)
        for k, v in summ.items():
            print(f"  {k:24s} {v}", flush=True)
        report["families"][fam] = dict(summary=summ, lives=res)
        (ROOT / "lab/v/alloc_confirm.json").write_text(json.dumps(report, indent=1, default=str) + "\n")
    report["wall_seconds"] = time.monotonic() - t0
    (ROOT / "lab/v/alloc_confirm.json").write_text(json.dumps(report, indent=1, default=str) + "\n")
    print("wall_seconds", report["wall_seconds"])


if __name__ == "__main__":
    main()
