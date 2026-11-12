"""retune.py: step 1 of the muscle-like body's programme (PROGRAMME.md): the starting brain's numbers retuned for the new body, as
evolution would, once, before any life. Five factors on the starting brain's own numbers (discrete/results/cmos_b_bench.json, each life
drawing its tolerances as ever): the scan's, drive's and run's beat rates, the hold and the boredom time; log2 factors in [-2, 3] for
rates, [-2, 2] for times. Scored by the standard efficiency (minimal.spec: gain over energy spent) over 100 s lives on plain bodies,
food and poison from birth (the base task), paired. A random search, then a local refinement around the best; then the winner judged
on fresh seeds against the old numbers, on both bodies.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/retune.py search|judge"""
import json
import math
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
from concurrent.futures import ProcessPoolExecutor
import numpy as np

import stage3_random as R

KEYS = ("scan", "drive", "run", "hold", "bored")
LO = np.array([-2, -2, -2, -2, -2.0])
HI = np.array([3, 3, 3, 2, 2.0])
SEARCH = 63000                                  # development seeds for the search
JUDGE = 64000                                   # fresh seeds for the judgement
OUT = "/home/pilgrim/git/simple-learner/lab/v/retune.json"   # (the 60 ms search; the 30 ms one, chosen: retune_tau30.json = retune_muscle.json)


def _init(muscle):
    R._init(0.0025, False)
    from stage2_lang import sim
    sim.WLife.muscle = muscle


def life(j):
    from minimal.spec import COST, spent
    from stage2_lang import arms as S
    from stage2_lang.sim import WLife
    from stage2_lang.seconds import seconds_cls
    import table as T
    x, seed, first, secs = j
    kw = {"sync": 1, "raw": 1}                          # (raw: the factors searched here, not the frozen retuning on top)
    kw |= {k + "_x": float(2.0 ** v) for k, v in zip(KEYS, x)}
    q = T.numbers(seed, kw)
    lf = WLife(seed, first, (lambda s: seconds_cls(T.Circuit)(s, q)), S.world_of("(world)"), seconds=True)
    l = S.live(lf, secs)
    return sum(a - COST * b for a, b, _ in l), spent(l)


def score(ex, x, seeds, secs=100.0):
    res = list(ex.map(life, [(tuple(x), s, c, secs) for s in seeds for c in ("red", "blue")]))
    g, sp = np.array([r[0] for r in res]), np.array([r[1] for r in res])
    return g.sum() / sp.sum(), g, sp


def search(n_rand=70, n_local=40, pairs=8, out=OUT):
    rng = np.random.default_rng(5)
    seeds = range(SEARCH, SEARCH + pairs)
    found = []
    with ProcessPoolExecutor(7, initializer=_init, initargs=(True,)) as ex:
        e0 = score(ex, np.zeros(5), seeds)[0]
        print(f"old numbers on the new body: {e0:.2f}", flush=True)
        found.append((e0, np.zeros(5)))
        for i in range(n_rand):
            x = rng.uniform(LO, HI)
            found.append((score(ex, x, seeds)[0], x))
        found.sort(key=lambda z: -z[0])
        print("random search, best five: " + "; ".join(f"{e:.2f} {np.round(x, 2).tolist()}" for e, x in found[:5]), flush=True)
        for i in range(n_local):                       # refine around the best few
            e, x = found[i % 3]
            y = np.clip(x + rng.normal(0, 0.35, 5), LO, HI)
            found.append((score(ex, y, seeds)[0], y))
            found.sort(key=lambda z: -z[0])
        top = found[:5]
        print("refined, best five: " + "; ".join(f"{e:.2f} {np.round(x, 2).tolist()}" for e, x in top), flush=True)
        seeds2 = range(SEARCH + 100, SEARCH + 100 + 2 * pairs)   # the top five rescored on more lives, against the search's luck
        best = max(((score(ex, x, seeds2)[0], x) for _, x in top), key=lambda z: z[0])
    json.dump({"x": best[1].tolist(), "keys": KEYS, "search_eff": best[0]}, open(out, "w"))
    print(f"chosen: {np.round(best[1], 2).tolist()} (log2 factors on {KEYS}); efficiency {best[0]:.2f} on {2 * pairs} more pairs", flush=True)


def judge(pairs=30):
    x = np.array(json.load(open(OUT.replace("retune.json", "retune_muscle.json")))["x"])
    seeds = range(JUDGE, JUDGE + pairs)
    I = R.boot(pairs)
    print(f"== the retuned starting brain, {np.round(x, 2).tolist()} (log2 factors on {KEYS}), fresh seeds {JUDGE}+, {pairs} pairs, 100 s")
    out = {}
    for muscle in (False, True):
        with ProcessPoolExecutor(7, initializer=_init, initargs=(muscle,)) as ex:
            for name, xx in (("old numbers", np.zeros(5)), ("retuned", x)):
                e, g, sp = score(ex, xx, seeds)
                b = g[I].sum(1) / sp[I].sum(1)
                out[(muscle, name)] = b
                print(f"  {'muscle-like' if muscle else 'world.py   '} body, {name:11s}: efficiency {e:+.2f} [{np.percentile(b, 2.5):+.2f},{np.percentile(b, 97.5):+.2f}]", flush=True)


if __name__ == "__main__":
    import ledger
    ledger.start()
    if sys.argv[1] == "quick":                       # a shorter search for tuning the body itself (MUSCLE_TAU set): out to retune_tauN.json
        import os
        search(40, 20, 8, OUT.replace(".json", f"_tau{int(float(os.environ['MUSCLE_TAU']) * 1000)}.json"))
    else:
        {"search": search, "judge": judge}[sys.argv[1]]()
