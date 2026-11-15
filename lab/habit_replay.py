"""habit_replay.py: each learned life's final habit, forced, on the same life (2026-11-14, after O22): splits the learner's loss into
the habit it ends on (forced score of that habit) and carrying it out while learning (learned score against that).
    .venv/bin/python lab/habit_replay.py PKL ARM SECS"""
import pickle
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import ladders as L
import stage3_random as R
import steer as ST

if __name__ == "__main__":
    pkl, arm, secs = sys.argv[1], sys.argv[2], float(sys.argv[3])
    rows = pickle.load(open(pkl, "rb"))
    n = len({r["seed"] for r in rows})
    s0 = min(r["seed"] for r in rows)
    mine = [r for r in rows if r["arm"] == arm]
    cols = [c for s in range(s0, s0 + n) for c in L.COL]
    jobs = [("pol" + "".join(str(r["reflex"][c]) for c in range(8)), L.PLAIN, r["seed"], c, secs) for r, c in zip(mine, cols)]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        forced = list(ex.map(ST.job, jobs))
    I = R.boot(n)
    a, b = L.scored([r["eff"] for r in mine], secs, I), L.scored([r["eff"] for r in forced], secs, I)
    print(f"== {arm}'s final habits replayed, forced ({n} pairs, {secs:.0f} s)")
    print(f"  learned {a[0]:+.2f}; its final habits forced {b[0]:+.2f}; learned - forced {a[0] - b[0]:+.2f} "
          f"[{np.percentile(a[1] - b[1], 2.5):+.2f},{np.percentile(a[1] - b[1], 97.5):+.2f}]")
    for r, f, j in zip(mine, forced, jobs):
        print(f"  {r['seed']} {j[0][3:]} learned {r['eff'][2] / r['eff'][3]:+.2f} forced {f['eff'][2] / f['eff'][3]:+.2f}")
