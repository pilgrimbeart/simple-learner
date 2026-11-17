"""D77 second follow-up: the allowance ablation on all ten historical seq-17 pairs (a ruler, not a design).

Settings: low (P=560), A (560, event streams at 26), B (4480, event streams at 3), high (P=4480). Scored by the
original frozen metric against the recorded circuit and vtold lives (lab/noisy_resource_records.py's method).
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/noisy_resource_ablate10.py
"""
import glob
import hashlib
import json
import pickle
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
import numpy as np
import noisy_resource_observe as O

SEEDS = range(142000, 142010)
SETTINGS = {"low": (560, None), "A_low_plus_event": (560, 4480 // 168), "B_high_minus_event": (4480, 560 // 168), "high": (4480, None)}


def one(job):
    import stage3_random as R
    import teach as T
    import ladders as L
    from stage2_lang import arms as S
    name, seed, first = job
    P, event_P = SETTINGS[name]
    R._init(.0025, False)
    original, out = S.live, {}

    def live(lf, secs):
        b = lf.brain
        assert len(b.nets) == 168 and lf.t == 0
        if event_P is not None:
            for n in b.nets:
                if O.family(n.kind) == "event":
                    n.P = n.base = event_P
        lived = original(lf, secs)
        out["mean_units"] = None
        out["final_units"] = sum(len(n.units) for n in b.nets)
        out["final_grown"] = {f: sum(sum(x["sym"] is None for x in n.units.values()) for n in b.nets if O.family(n.kind) == f)
                              for f in ("event", "clock", "integrator", "rhythm")}
        return lived

    S.live = live
    try:
        res = T.job((L.seq(17), O.ARM, P, seed, first, O.SECS))
    finally:
        S.live = original
    return dict(name=name, seed=seed, first=first, result=list(res[:5]) + [None] + list(res[6:]), **out)


def main():
    t0 = time.monotonic()
    jobs = [(n, s, c) for n in SETTINGS for s in SEEDS for c in ("red", "blue")]
    with ProcessPoolExecutor(8) as ex:
        res = list(ex.map(one, jobs))
    hist = pickle.loads(Path(glob.glob(str(ROOT / "lab/v/grownet_pair300_seq_5-11-17_10_s142000_*.pkl"))[0]).read_bytes())
    hist = {(j[1], j[2], j[3], j[4]): r for j, r in hist if j[0] == 17}
    by = {(r["name"], r["seed"], r["first"]): r for r in res}
    for name, P in (("low", 560), ("high", 4480)):
        for s in SEEDS:
            for c in ("red", "blue"):
                h, x = hist[O.ARM, P, s, c], by[name, s, c]["result"]
                assert [v for i, v in enumerate(h) if i not in (5, 7)] == [v for i, v in enumerate(x) if i not in (5, 7)], (name, s, c)
    print("PASS: low and high reproduce all 40 historical lives (behaviour fields exact)")
    k = np.random.default_rng(0).integers(0, 10, (2000, 10))
    idx = np.concatenate((2 * k, 2 * k + 1), axis=1)

    def eff(rows):
        d = np.array([r[:5] for r in rows], dtype=float)
        return d[idx, 2].sum(1) / d[idx, 3].sum(1)
    order = [(s, c) for s in SEEDS for c in ("red", "blue")]
    ref = {a: eff([hist[a, 0, s, c] for s, c in order]) for a in ("circuit", "vtold")}
    gap = ref["vtold"] - ref["circuit"]
    closure, summary = {}, {}
    for name in SETTINGS:
        closure[name] = (eff([by[name, s, c]["result"] for s, c in order]) - ref["circuit"]) / gap
        lo, med, hi = np.quantile(closure[name], [.025, .5, .975])
        units = np.mean([by[name, s, c]["final_units"] for s, c in order])
        grown = {f: float(np.mean([by[name, s, c]["final_grown"][f] for s, c in order])) for f in ("event", "clock", "integrator", "rhythm")}
        summary[name] = dict(median=float(med), ci95=[float(lo), float(hi)], mean_final_units=float(units), mean_final_grown=grown)
        print(f"{name:20s} gap closed {med:+.2f} [{lo:+.2f},{hi:+.2f}]  final units {units:6.0f}  grown " +
              " ".join(f"{f} {g:.0f}" for f, g in grown.items()))
    for a, b in (("A_low_plus_event", "low"), ("high", "A_low_plus_event"), ("B_high_minus_event", "low"), ("high", "B_high_minus_event")):
        lo, med, hi = np.quantile(closure[a] - closure[b], [.025, .5, .975])
        summary[f"{a}-{b}"] = dict(median=float(med), ci95=[float(lo), float(hi)])
        print(f"  {a} - {b}: {med:+.2f} [{lo:+.2f},{hi:+.2f}]")
    payload = dict(settings=SETTINGS, seeds=[142000, 142009], seconds=O.SECS, metric="share of circuit-to-vtold gap closed, final-third efficiency, paired bootstrap 2000",
                   summary=summary, lives=res, sha256={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                   for p in ("lab/noisy_resource_ablate10.py", "lab/noisy_resource_observe.py", "lab/grownet.py")},
                   wall_seconds=time.monotonic() - t0)
    (ROOT / "lab/v/noisy_resource_ablate10.json").write_text(json.dumps(payload, indent=1, default=str) + "\n")
    print("wall_seconds", payload["wall_seconds"])


if __name__ == "__main__":
    main()
