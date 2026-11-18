"""D97: why the market (alloc_rules rule M) moves little room to event streams. Read-only classification of each
market request; each life must reproduce D78 stage 1's M record. Seq 17, seeds 142000-142009.
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/market_diagnosis.py
"""
from collections import Counter
import json
from pathlib import Path
import sys
import time
from concurrent.futures import ProcessPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "lab"), str(ROOT)]
import numpy as np
import alloc_compare as C
import room_prediction as RP

BASE = ROOT / "lab/v/market_diagnosis"
SEEDS = range(142000, 142010)


def one(job):
    import stage3_random as R
    import teach as T
    import grownet as GN
    import alloc_rules as A
    from stage2_lang import arms as S
    seed, first = job
    R._init(.0025, False)
    original, out = S.live, {}

    def live(lf, secs):
        b = lf.brain
        st = A.install(b, "M", C.G, seed)
        fixed = {id(n): sum(x["sym"] is not None for x in n.units.values()) for n in b.nets}
        counts = {f: Counter() for f in C.FAM}
        trace = []
        for n in b.nets:
            room = n._room
            fam = C.family(n.kind)

            def _room(_n=n, _r=room, _f=fam):
                # classify by the first failing condition of rule M, reading state only, then call the original
                if len(_n.units) < _n.P:
                    why = "under allowance"
                else:
                    d = _n._deep
                    if not (d is not None and d in _n.units and min(_n.units[d]["n"]) >= 1):
                        why = "full, no birth due"
                    elif getattr(_n, "saved", 0.0) <= GN.POOL_BITS * (len(_n.units) - _n.base + 1):
                        why = "full, savings test fails"
                    elif not [v for v in b.nets if v is not _n and getattr(v, "saved", 0.0) <= 0.0 and v.P > fixed[id(v)]]:
                        why = "full, no poor donor"
                    else:
                        why = "full, transfer attempted"
                before = st["transfers"]
                r = _r()
                counts[_f][why] += 1
                counts[_f]["transfers"] += st["transfers"] - before
                return r
            n._room = _room
        sample_t = [0.]

        step = lf.step if hasattr(lf, "step") else None
        lived_holder = {}
        orig_predict = b.predict

        def predict():
            if b.t >= sample_t[0]:
                sample_t[0] += 10.
                trace.append(dict(t=float(b.t), event=[(n.kind, float(getattr(n, "saved", 0.)), n.P - fixed[id(n)], len(n.units) - fixed[id(n)])
                                                       for n in b.nets if C.family(n.kind) == "event"],
                                  poor=sum(getattr(v, "saved", 0.) <= 0. and v.P > fixed[id(v)] for v in b.nets)))
            return orig_predict()
        b.predict = predict
        lived = original(lf, secs)
        out.update(counts={f: dict(c) for f, c in counts.items()}, trace=trace, alloc=dict(st),
                   saved_end={C.family(n.kind): None for n in b.nets},
                   event_saved_end=[(n.kind, float(getattr(n, "saved", 0.))) for n in b.nets if C.family(n.kind) == "event"],
                   top_saved_end=sorted(((float(getattr(n, "saved", 0.)), n.kind) for n in b.nets), reverse=True)[:8])
        return lived
    S.live = live
    try:
        res = T.job((C.world("seq"), C.ARM, 560, seed, first, C.FAMILIES["seq"][1]))
    finally:
        S.live = original
    return dict(seed=seed, first=first, result=list(res[:5]) + [None] + list(res[6:]), **out)


def main():
    t0 = time.monotonic()
    jobs = [(s, c) for s in SEEDS for c in ("red", "blue")]
    with ProcessPoolExecutor(8) as ex:
        res = list(ex.map(one, jobs))
    ref = {(l["seed"], l["first"]): l["result"] for l in json.loads((ROOT / "lab/v/alloc_stage1.json").read_text())["families"]["seq"]["lives"] if l["rule"] == "M"}
    bad = [(r["seed"], r["first"]) for r in res if [v for i, v in enumerate(json.loads(json.dumps(r["result"]))) if i not in (5, 7)]
           != [v for i, v in enumerate(ref[r["seed"], r["first"]]) if i not in (5, 7)]]
    tot = {f: Counter() for f in C.FAM}
    for r in res:
        for f, c in r["counts"].items():
            tot[f].update(c)
    ev_traj = {}
    for r in res:
        for row in r["trace"]:
            k = int(row["t"] // 50) * 50
            ev_traj.setdefault(k, []).append((max(s for _, s, _, _ in row["event"]), np.median([s for _, s, _, _ in row["event"]]),
                                              sum(g for _, _, g, _ in row["event"]), row["poor"]))
    traj = {k: dict(best_event_saved=float(np.median([a for a, b, c, d in v])), median_event_saved=float(np.median([b for a, b, c, d in v])),
                    event_allowance_grown=float(np.mean([c for a, b, c, d in v])), poor_donors=float(np.mean([d for a, b, c, d in v])))
            for k, v in sorted(ev_traj.items())}
    out = dict(identity=dict(lives=len(res), mismatches=bad), requests={f: dict(c) for f, c in tot.items()}, event_trajectory=traj,
               top_saved_end=[r["top_saved_end"][:5] for r in res[:4]], event_saved_end=[r["event_saved_end"] for r in res[:2]],
               transfers_per_life=float(np.mean([r["alloc"]["transfers"] for r in res])), wall_s=time.monotonic() - t0,
               source_sha256={p: RP.digest(ROOT / p) for p in ("lab/market_diagnosis.py", "lab/alloc_rules.py", "lab/grownet.py")})
    BASE.with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print("identity", "PASS" if not bad else f"FAIL {bad}")
    print(json.dumps(out["requests"], indent=1))
    print(json.dumps(traj, indent=1))
    print("transfers per life", out["transfers_per_life"])
    print(json.dumps(out["top_saved_end"]))


if __name__ == "__main__":
    main()
