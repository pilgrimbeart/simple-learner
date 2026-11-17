"""D78 diagnosis: per-stream weights, units and bits saved at the end of life, by family, for W (cap 3042) and the
unchanged design (P=4480), seq 17, seeds 177000-177003. Reading only; the lives are the confirmation's lives
(checked: same result tuples).
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/alloc_dilution.py
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


def one(job):
    G, rule, P, seed, first = job
    from stage2_lang import arms as S
    C.G = G
    inner, rows = S.live, []

    def live(lf, secs):
        lived = inner(lf, secs)
        b = lf.brain
        for n in b.nets:
            rows.append(dict(kind=n.kind, family=C.family(n.kind), w=float(getattr(n, "w", 1.0)),
                             units=len(n.units), grown=sum(x["sym"] is None for x in n.units.values()),
                             saved=float(getattr(n, "saved", 0.0))))
        rows.append(dict(kind="_default", family="default", w=float(getattr(b, "w_def", 1.0)), units=0, grown=0, saved=0.0))
        return lived
    S.live = live                                       # C.one wraps S.live again with its own observer, inside this one
    try:
        r = C.one(("seq", rule, P, seed, first))
    finally:
        S.live = inner
    r["streams"] = rows
    return r


def main():
    jobs = [(1000, "W", 560, s, c) for s in SEEDS for c in ("red", "blue")] + [(258, "none", 4480, s, c) for s in SEEDS for c in ("red", "blue")]
    with ProcessPoolExecutor(8) as ex:
        res = list(ex.map(one, jobs))
    conf = json.loads((ROOT / "lab/v/alloc_confirm.json").read_text())["families"]["seq"]["lives"]
    cb = {(r["rule"], r["seed"], r["first"]): r["result"] for r in conf}
    for r in res:
        assert cb[r["rule"], r["seed"], r["first"]] == json.loads(json.dumps(r["result"], default=str)), "differs from the confirmation life"
    print("PASS: all 16 lives equal the confirmation's")
    out = {}
    for rule in ("W", "none"):
        rr = [r for r in res if r["rule"] == rule]
        fam = {}
        for f in ("event", "clock", "integrator", "rhythm", "default"):
            share, med, gsum, sv = [], [], [], []
            for r in rr:
                tot = sum(x["w"] for x in r["streams"])
                xs = [x for x in r["streams"] if x["family"] == f]
                share.append(sum(x["w"] for x in xs) / tot)
                med.append(np.median([x["w"] / tot for x in xs]))
                gsum.append(sum(x["grown"] for x in xs))
                sv.append(sum(x["saved"] for x in xs))
            fam[f] = dict(n_streams=len(xs), weight_share=float(np.mean(share)), median_stream_share=float(np.mean(med)),
                          grown=float(np.mean(gsum)), saved_bits=float(np.mean(sv)))
            print(f"{rule:5s} {f:10s} streams {len(xs):3d} family weight share {np.mean(share):.3f}  median stream share {np.mean(med):.5f}"
                  f"  grown {np.mean(gsum):6.0f}  saved {np.mean(sv):8.1f} b")
        out[rule] = fam
    (ROOT / "lab/v/alloc_dilution.json").write_text(json.dumps(dict(summary=out, lives=res, provenance=C.provenance()), indent=1, default=str) + "\n")


if __name__ == "__main__":
    main()
