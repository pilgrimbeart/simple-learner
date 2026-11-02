"""bursts.py: with the bit right, how much likelier is a poison just after a poison (or a food) than on average?
Design B in the fast model, tolerances drawn, seeds 0-127 x (red, blue)."""
import sys, json, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from concurrent.futures import ProcessPoolExecutor
import cmodel4
D = "/home/pilgrim/git/simple-learner/lab/m2/"
B = {**cmodel4.NOMINAL, **json.load(open(D + "B.json"))}
WIN = (0.5, 1.0, 2.0, 5.0)


def one(job):
    from creature import Life
    seed, poison = job
    q = cmodel4.drawn(B, seed)
    lf = Life(seed, poison, brain=lambda s: cmodel4.Model(s, **q))
    good = lf.sensor[next(c for c in lf.sensor if c != poison)]
    right, events = [], []
    while lf.t < 10000:
        n = len(lf.meals)
        lf.step()
        right.append(lf.brain.food == good)
        for t, c in lf.meals[n:]:
            events.append((t, c == poison, lf.brain.food == good))
    return np.array(right), events


with ProcessPoolExecutor(4) as ex:
    R = list(ex.map(one, [(s, c) for s in range(128) for c in ("red", "blue")]))
tr = sum(r.sum() for r, _ in R) * 0.01                   # s with the bit right
pois = [(t * 0.01, ok) for _, ev in R for t, p, ok in ev if p]
base = sum(ok for _, ok in pois) / tr
print(f"poison eaten with the bit right: {base:.3f} per s ({tr:.0f} s)")
for after in ("poison", "food"):
    for w in WIN:
        hits = tm = 0
        for r, ev in R:
            for i, (t, p, ok) in enumerate(ev):
                if p != (after == "poison") or not ok:
                    continue
                end = t + w / 0.01
                tm += r[int(t):int(min(end, len(r)))].sum() * 0.01
                hits += sum(1 for t2, p2, ok2 in ev[i + 1:] if p2 and ok2 and t2 < end)
        print(f"  within {w:3.1f} s after a {after}: {hits / max(tm, 1e-9):.3f} per s, {hits / max(tm, 1e-9) / base:.2f} x the mean")
