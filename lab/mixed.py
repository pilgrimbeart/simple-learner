"""mixed.py: body and rule in one life (the user, 2026-11-12: option a). A rung of a ladder (a hidden food rule, learned from taste by the
context tree, D40) and new parts (the split eye and two more thrusters a side, growing at 100 to 300 s, taken up by play, D55, D57's
play-until-needed with lateral inhibition). Do the two learnings add up, or does play's pause cost the tree the tastes it learns from?

Arms: circuit (the starting brain, neither); circuit+play (parts only); tree (the rule only, the parts present but unused); tree+play
(both); tree+told (the rule learned, the parts' arcs told: the yardstick for the parts). 1200 s lives, efficiency in the last third.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/mixed.py [PAIRS] [LADDER] [RUNG] [s111000]"""
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np

import ladders as L
import stage3_random as R
import uptake as U

SECS = 1200.0
P = 64
ARMS = ("circuit", "circuit+play", "tree", "tree+play", "tree+told")


def job(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    from stage2_lang.seconds import seconds_cls
    import table as T
    import tree as TR
    arm, lad, rung, seed, first = j
    w = S.world_of(L.LADDERS[lad]["world"](rung))
    base = seconds_cls(TR.tree_cls()) if arm.startswith("tree") else seconds_cls(T.Circuit)
    q = T.numbers(seed, {"P": P, "sync": 1})
    q["P"] = P
    cls = base if arm in ("circuit", "tree") else U.arcs_cls(base)
    lf = WLife(seed, first, (lambda s: cls(s, q)), w, seconds=True)
    if arm not in ("circuit", "tree"):
        right = []
        for h in (0, 1):
            side = 0 if h == 1 else 1
            right.append((lf.wire_h[h], lf.wire_m[len(lf.wire_m) - 2 + side]))
        lf.brain.setup("toldarcsI" if arm.endswith("told") else "learn3bIN", right)
    l = S.live(lf, SECS)
    g = [a - COST * b for a, b, _ in l]
    sp = spent(l)
    b = lf.brain
    play_done = next((e[0] for e in getattr(b, "log", []) if len(e) > 1 and e[1] == "play done"), None)
    return dict(arm=arm, seed=seed, eff=(0.0, 0.0, g[2], sp * l[2][2] / sum(t for _, _, t in l)), whole=(sum(g), sp),
                grow=lf.grow_at, play_done=play_done, tastes=sum(a + c for a, c, _ in l))


if __name__ == "__main__":
    a = sys.argv[1:]
    n = int(a[0]) if a and a[0].isdigit() else 10
    lad = a[1] if len(a) > 1 else "seq"
    rung = int(a[2]) if len(a) > 2 else 11
    s0 = next((int(x[1:]) for x in a if x.startswith("s") and x[1:].isdigit()), 111000)
    out = f"/home/pilgrim/git/simple-learner/lab/v/mixed_{lad}{rung}_{n}_s{s0}.pkl"
    if "report" not in a:
        import ledger
        ledger.start()
        with ProcessPoolExecutor(7, initializer=U._init) as ex:
            rows = list(ex.map(job, [(arm, lad, rung, s, c) for arm in ARMS for s in range(s0, s0 + n) for c in L.COL], chunksize=2))
        pickle.dump(rows, open(out, "wb"))
    rows = pickle.load(open(out, "rb"))
    I = R.boot(n)
    e = {arm: L.scored([r["eff"] for r in rows if r["arm"] == arm], SECS, I) for arm in ARMS}
    print(f"== body and rule in one life: {lad} rung {rung}, new parts at 100 to 300 s; {n} pairs, {SECS:.0f} s, last third [95%]")
    for arm in ARMS:
        d = e[arm][1] - e["circuit"][1]
        rs = [r for r in rows if r["arm"] == arm]
        wh = np.array([r["whole"] for r in rs])
        line = f"  {arm:13s} {e[arm][0]:+.2f} [{np.percentile(e[arm][1], 2.5):+.2f},{np.percentile(e[arm][1], 97.5):+.2f}]"
        if arm != "circuit":
            line += f"  vs circuit {e[arm][0] - e['circuit'][0]:+.2f} [{np.percentile(d, 2.5):+.2f},{np.percentile(d, 97.5):+.2f}]"
        line += f" | whole life {wh[:, 0].sum() / wh[:, 1].sum():+.2f} | meals {np.mean([r['tastes'] for r in rs]):.0f}"
        print(line, flush=True)
    add = (e["tree"][0] - e["circuit"][0]) + (e["circuit+play"][0] - e["circuit"][0])
    both = e["tree+play"][0] - e["circuit"][0]
    d = (e["tree+play"][1] - e["circuit"][1]) - ((e["tree"][1] - e["circuit"][1]) + (e["circuit+play"][1] - e["circuit"][1]))
    print(f"  do they add up? tree's gain + play's gain = {add:+.2f}; both together {both:+.2f}; interaction {both - add:+.2f} [{np.percentile(d, 2.5):+.2f},{np.percentile(d, 97.5):+.2f}]")
