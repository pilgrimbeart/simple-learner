"""D77 follow-up: which part of the extra allowance buys the sequence gain? A ruler, not a design.

Same pair as noisy_resource_observe.py (seq rung 17, seed 142000, red/blue, 300 s). After construction and
before the first step, the 10 event streams' allowance (and market base) is set by hand:
  A  P=560 overall, event streams at P=4480's per-stream allowance (26)
  B  P=4480 overall, event streams at P=560's per-stream allowance (3)
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/noisy_resource_ablate.py
"""
import hashlib
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
import noisy_resource_observe as O

KINDS = 168                                     # streams of the frozen arm (D76)


def one(job):
    import stage3_random as R
    import teach as T
    import ladders as L
    from stage2_lang import arms as S
    name, P, event_P, first = job
    R._init(.0025, False)
    original, out = S.live, {}

    def live(lf, secs):
        b = lf.brain
        assert len(b.nets) == KINDS and lf.t == 0
        for n in b.nets:
            if O.family(n.kind) == "event":
                n.P = n.base = event_P
        ob = O.Observer(lf)
        lived = original(lf, secs)
        o = ob.close(secs)
        o["event_streams"] = {n.kind: dict(units=len(n.units), P=n.P, saved=getattr(n, "saved", 0.), w=getattr(n, "w", 1.))
                              for n in b.nets if O.family(n.kind) == "event"}
        out["observed"] = o
        return lived

    S.live = live
    try:
        res = T.job((L.seq(17), O.ARM, P, O.SEED, first, O.SECS))
    finally:
        S.live = original
    return dict(name=name, P=P, event_P=event_P, first=first, result=dict(zip(O.FIELDS, res)), **out)


def main():
    t0 = time.monotonic()
    jobs = [(n, P, e, c) for n, P, e in (("A_low_plus_event", 560, 4480 // KINDS), ("B_high_minus_event", 4480, 560 // KINDS))
            for c in ("red", "blue")]
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(one, jobs))
    for r in res:
        o, x = r["observed"], r["result"]
        f = o["families"]
        print(f"{r['name']:20s} {r['first']:4s} gain {x['total_gain']:+5.0f} last third {x['last_third_gain']:+4.0f} bits/taste {x['pbits_per_taste']:.3f}"
              f" | mean units {o['mean_units']:6.0f} peak {o['peak_units']} | grown: " +
              " ".join(f"{k} {f[k]['final_grown']}" for k in sorted(f)) +
              f" | best {o['best']} heaviest {o['final_heaviest_streams'][0]}")
        print("   event streams:", {k: (v["units"], round(v["saved"], 1), round(v["w"], 2)) for k, v in o["event_streams"].items()})
    payload = dict(jobs=jobs, lives=res, sha256={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                   for p in ("lab/noisy_resource_ablate.py", "lab/noisy_resource_observe.py", "lab/grownet.py")},
                   wall_seconds=time.monotonic() - t0)
    (ROOT / "lab/v/noisy_resource_ablate.json").write_text(json.dumps(payload, indent=1, default=str) + "\n")
    print("wall_seconds", payload["wall_seconds"])


if __name__ == "__main__":
    main()
