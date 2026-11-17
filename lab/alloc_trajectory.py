"""D78 diagnosis: mixture weight shares through life (every 10 s), W (cap 3042) vs the unchanged design (P=4480),
seq 17, seeds 177000-177003. Reading only; lives checked equal to lab/v/alloc_confirm.json.
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/alloc_trajectory.py
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
import numpy as np
import alloc_compare as C

SEEDS = range(177000, 177004)
FAMS = ("event", "clock", "integrator", "rhythm")


def one(job):
    G, rule, P, seed, first = job
    from stage2_lang import arms as S
    C.G = G
    inner, snaps = S.live, []

    def live(lf, secs):
        b = lf.brain
        cur = [lf.step]

        def step():
            r = cur[0]()
            if lf.__dict__.get("step") is not step:   # WLife.step replaces itself with its fast path on the first call:
                cur[0] = lf.step                      # take the replacement and put this reader back in front of it
                lf.step = step
            t = lf.t * lf.dt
            if not snaps or t - snaps[-1]["t"] >= 10.0:
                ws = [(float(getattr(n, "w", 1.0)), n.kind) for n in b.nets]
                wd = float(getattr(b, "w_def", 1.0))
                tot = sum(w for w, _ in ws) + wd
                top = max(ws)
                snaps.append(dict(t=t, top=top[1], top_share=top[0] / tot, default=wd / tot,
                                  fam={f: sum(w for w, k in ws if C.family(k) == f) / tot for f in FAMS}))
            return r
        lf.step = step
        return inner(lf, secs)
    S.live = live
    try:
        r = C.one(("seq", rule, P, seed, first))
    finally:
        S.live = inner
    r["snaps"] = snaps
    return r


def main():
    jobs = [(1000, "W", 560, s, c) for s in SEEDS for c in ("red", "blue")] + [(258, "none", 4480, s, c) for s in SEEDS for c in ("red", "blue")]
    with ProcessPoolExecutor(8) as ex:
        res = list(ex.map(one, jobs))
    conf = json.loads((ROOT / "lab/v/alloc_confirm.json").read_text())["families"]["seq"]["lives"]
    cb = {(r["rule"], r["seed"], r["first"]): r["result"] for r in conf}
    for r in res:
        assert cb[r["rule"], r["seed"], r["first"]] == json.loads(json.dumps(r["result"], default=str)), "differs from the confirmation life"
    print("PASS: all 16 lives equal the confirmation's (the step wrapper only reads)")
    summary = {}
    for rule in ("W", "none"):
        rr = [r for r in res if r["rule"] == rule]
        rows = []
        for lo, hi in ((0, 30), (30, 100), (100, 200), (200, 300)):
            sel = [[s for s in r["snaps"] if lo <= s["t"] < hi] for r in rr]
            row = dict(window=[lo, hi], top_share=float(np.mean([np.mean([s["top_share"] for s in x]) for x in sel])),
                       default=float(np.mean([np.mean([s["default"] for s in x]) for x in sel])),
                       fam={f: float(np.mean([np.mean([s["fam"][f] for s in x]) for x in sel])) for f in FAMS},
                       top_family_counts=dict(zip(*np.unique([C.family(s["top"]) for x in sel for s in x], return_counts=True))))
            rows.append(row)
            print(f"{rule:5s} {lo:3d}-{hi:3d} s  top {row['top_share']:.2f} default {row['default']:.2f}  " +
                  " ".join(f"{f} {row['fam'][f]:.2f}" for f in FAMS) + f"  top stream's family: {row['top_family_counts']}")
        summary[rule] = rows
    (ROOT / "lab/v/alloc_trajectory.json").write_text(json.dumps(dict(summary=summary, lives=res, provenance=C.provenance()), indent=1, default=str) + "\n")


if __name__ == "__main__":
    main()
