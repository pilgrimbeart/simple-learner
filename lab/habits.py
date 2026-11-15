"""habits.py: the ceiling of the held options' habit space (2026-11-14, after D63). Every habit (one of the four options for each of the
four contexts, 4^4 = 256, so 8 bits) forced through the same options machinery, no learning, no play, on the same lives; then the best
few re-judged on more and longer lives, and extended with the bored contexts (4: bored, nothing in view; 6: bored, the other colour).
The best forced habit is the ceiling for anything that learns habits in this space: ceiling minus learned is the cost of learning,
circuit minus ceiling the bits the space can't express.

    .venv/bin/python lab/habits.py screen [PAIRS] [SECS]      # all 256, paired, same seeds (default 5 pairs, 300 s)
    .venv/bin/python lab/habits.py top K PAIRS SECS [bored]   # the K best of the screen re-judged (and with every bored extension)"""
import itertools
import os
import pickle
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import ladders as L
import stage3_random as R
import steer as ST

V = "/home/pilgrim/git/simple-learner/lab/v/"


def run(arms, pairs, secs, s0):
    jobs = [(a, L.PLAIN, s, c, secs) for a in arms for s in range(s0, s0 + pairs) for c in L.COL]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        return list(ex.map(ST.job, jobs, chunksize=4))


def table(rows, arms, pairs, secs):
    I = R.boot(pairs)
    return {a: L.scored([r["eff"] for r in rows if r["arm"] == a], secs, I) for a in arms}


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "screen":
        pairs, secs = (int(a[1]) if len(a) > 1 else 5), (float(a[2]) if len(a) > 2 else 300.0)
        arms = ["pol" + "".join(map(str, h)) for h in itertools.product(range(4), repeat=4)]
        out = V + f"habits_screen_{pairs}_{int(secs)}s.pkl"
        if not os.path.exists(out):
            pickle.dump(run(arms, pairs, secs, 132000), open(out, "wb"))
        rows = pickle.load(open(out, "rb"))
        e = table(rows, arms, pairs, secs)
        best = sorted(arms, key=lambda x: -np.nan_to_num(e[x][0], nan=-9))
        print(f"== habits screened: 256, {pairs} pairs, {secs:.0f} s, seeds 132000+ (contexts: 0 none, 1 followed, 2 other, 3 both;"
              " options: 0 thruster A, 1 thruster B, 2 both, 3 none)")
        for x in best[:20]:
            print(f"  {x[3:]}  {e[x][0]:+.2f} [{np.percentile(e[x][1], 2.5):+.2f},{np.percentile(e[x][1], 97.5):+.2f}]")
        v = np.array([e[x][0] for x in arms]); v = v[np.isfinite(v)]
        print(f"  spread: best {v.max():+.2f}, median {np.median(v):+.2f}, worst {v.min():+.2f}; above +1: {(v > 1).sum()}")
    else:
        k, pairs, secs = int(a[1]), int(a[2]), float(a[3])
        sc = sorted(f for f in os.listdir(V) if f.startswith("habits_screen_"))[-1]
        rows = pickle.load(open(V + sc, "rb"))
        n = int(sc.split("_")[2]); ss = float(sc.split("_")[3][:-5])
        arms0 = sorted({r["arm"] for r in rows})
        e0 = table(rows, arms0, n, ss)
        top = sorted(arms0, key=lambda x: -np.nan_to_num(e0[x][0], nan=-9))[:k]
        arms = list(top)
        if "bored" in a:
            arms += [t + f"{b4}{t[4]}{b6}{t[6]}" for t in top for b4 in range(4) for b6 in range(4)]   # 5, 7 never bored: the followed colour in view
        arms = ["circuit", "opt", "optB"] + arms
        out = V + f"habits_top{k}_{pairs}_{int(secs)}s{'_bored' if 'bored' in a else ''}.pkl"
        if not os.path.exists(out):
            pickle.dump(run(arms, pairs, secs, 131000), open(out, "wb"))
        rows = pickle.load(open(out, "rb"))
        e = table(rows, arms, pairs, secs)
        print(f"== the best habits re-judged: {pairs} pairs, {secs:.0f} s, seeds 131000+ (the learned arms' own lives)")
        for x in sorted(arms, key=lambda x: -e[x][0])[:25]:
            d = e[x][1] - e["optB"][1]
            print(f"  {x:12s} {e[x][0]:+.2f} [{np.percentile(e[x][1], 2.5):+.2f},{np.percentile(e[x][1], 97.5):+.2f}]"
                  f"  vs optB {e[x][0] - e['optB'][0]:+.2f} [{np.percentile(d, 2.5):+.2f},{np.percentile(d, 97.5):+.2f}]")
