"""D98: rule M (alloc_rules) with the market price POOL_BITS at 1/4 and 1/16 bit, seq 17, seeds 142000-142009.
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/market_price.py
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

BASE = ROOT / "lab/v/market_price"
SEEDS = range(142000, 142010)
PRICES = (.25, .0625)


def one(job):
    import grownet as GN
    price, seed, first = job
    GN.POOL_BITS = price                        # read by alloc_rules' M room test at each call
    from stage2_lang import arms as S
    original, out = S.live, {}

    def live(lf, secs):
        rec = RP.Recorder(lf)
        lived = original(lf, secs)
        out.update(rows=rec.rows, fam=rec.fam.tolist())
        return lived
    S.live = live
    try:
        r = C.one(("seq", "M", 560, seed, first))
    finally:
        S.live = original
    return dict(r, name=f"M price {price}", price=price, **out)


def main():
    t0 = time.monotonic()
    jobs = [(p, s, c) for p in PRICES for s in SEEDS for c in ("red", "blue")]
    with ProcessPoolExecutor(8) as ex:
        res = list(ex.map(one, jobs))
    st1 = {(l["rule"], l["seed"], l["first"]): l for l in json.loads((ROOT / "lab/v/alloc_stage1.json").read_text())["families"]["seq"]["lives"]}
    hist, _ = C.history("seq")
    by = {(r["name"], r["seed"], r["first"]): r["result"] for r in res}
    for rule in ("M", "E", "W"):
        for s in SEEDS:
            for c in ("red", "blue"):
                by[rule, s, c] = st1[rule, s, c]["result"]
    names = ["E", "M"] + [f"M price {p}" for p in PRICES] + ["W"]
    X = C.closure_samples({n: (lambda s, c, n=n: by[n, s, c]) for n in names}, hist, list(SEEDS))
    out = dict(gap_closed={n: C.ci(X[n]) for n in names}, vs_M={n: C.ci(X[n] - X["M"]) for n in names if n != "M"}, per_price={},
               wall_s=time.monotonic() - t0, source_sha256={p: RP.digest(ROOT / p) for p in ("lab/market_price.py", "lab/alloc_rules.py", "lab/grownet.py")})
    order = [(s, c) for s in SEEDS for c in ("red", "blue")]
    for p in PRICES:
        rr = [r for r in res if r["price"] == p]
        comb = [RP.combiners(r) for r in rr]
        n = sum(x[0]["native mixture", "last_third"]["n"] for x in comb)
        out["per_price"][str(p)] = dict(transfers=float(np.mean([r["alloc"]["transfers"] for r in rr])),
                                        grown={f: float(np.mean([r["grown"][f] for r in rr])) for f in C.FAM},
                                        native_last_third_bits=sum(x[0]["native mixture", "last_third"]["bits"] for x in comb) / n,
                                        event_only_last_third_bits=sum(x[0]["fresh Bayes, event streams only", "last_third"]["bits"] for x in comb) / n)
    out["M_stage1"] = dict(transfers=float(np.mean([st1["M", s, c]["alloc"]["transfers"] for s, c in order])),
                           grown={f: float(np.mean([st1["M", s, c]["grown"][f] for s, c in order])) for f in C.FAM})
    BASE.with_suffix(".pkl").write_bytes(pickle.dumps(dict(lives=res)))
    BASE.with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
