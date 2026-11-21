"""J (D117): per-life secondary issued-forecast values (loss and choice errors per taste; first third, last third, full life)
for all 120 lives, exported from the raw pickles without changing the frozen harness. Offline.
    timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/spare_allowance_compare_perlife.py
"""
import json
import math
from pathlib import Path
import pickle
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
import spare_allowance_experiment as X


def main():
    X.verify_sources()
    new = pickle.loads(X.BASE.with_name(X.BASE.name + "_compare_new").with_suffix(".pkl").read_bytes())
    pilot = pickle.loads(X.PILOT_RAW.read_bytes())
    want = set(X.jobs_all())
    by = {}
    for r in new + [r for r in pilot if (r["cond"], r["arm"], r["seed"], r["first"]) in want]:
        k = (r["cond"], r["arm"], r["seed"], r["first"])
        assert k not in by
        by[k] = r
    assert set(by) == want
    out = {}
    for k, r in sorted(by.items()):
        secs = X.SECS[k[0]]
        row = {}
        for w, lo, hi in (("first_third", 0, secs / 3), ("last_third", 2 * secs / 3, secs + 1), ("full", 0, secs + 1)):
            sel = [(p, y) for t, p, y in r["trace_acc"] if lo <= t < hi]
            n = len(sel)
            row[w] = dict(n=n, bits=sum(-math.log2(min(1 - 1e-12, max(1e-12, p if y else 1 - p))) for p, y in sel) / n if n else None,
                          errors=sum(.5 if p == .5 else float((p > .5) != bool(y)) for p, y in sel) / n if n else None)
        out[" ".join(map(str, k))] = row
    pooled = {}
    for c in ("seq", "time", "allfood"):
        for a in X.ARMS_J:
            ks = [k for k in by if k[0] == c and k[1] == a]
            for w in ("last_third",):
                n = sum(out[" ".join(map(str, k))][w]["n"] for k in ks)
                pooled[f"{c} {a} {w}"] = dict(tastes=n, pooled_bits=sum(out[" ".join(map(str, k))][w]["bits"] * out[" ".join(map(str, k))][w]["n"] for k in ks) / n,
                                             pooled_errors=sum(out[" ".join(map(str, k))][w]["errors"] * out[" ".join(map(str, k))][w]["n"] for k in ks) / n)
    p = ROOT / "lab/v/spare_allowance_compare_perlife.json"
    p.write_text(json.dumps(dict(per_life=out, pooled_levels=pooled, script_sha256=X.digest(Path(__file__))), indent=1) + "\n")
    print(json.dumps(pooled, indent=1))


if __name__ == "__main__":
    main()
