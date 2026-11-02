"""window.py k=v ...: does the bit flip for two poisons d s apart (seeds 0 and 6)?"""
import sys, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import cmos
from discrete.life import bench
kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[1:])}
for seed in (0, 6):
    n = cmos.pol(np.random.default_rng(seed + 5_000_011), **kw)
    pul, at = [], []
    t0 = 2.0
    for d in (6.0, 0.5, 1.0, 1.5, 2.0, 3.0):
        pul += [("poison", t0), ("poison", t0 + d)]
        at.append((d, t0 + d))
        t0 += d + 5.0                                   # recovered before the next pair
    t, V, _ = bench(n, t0, ["q", "tq" if not kw.get("mirror") else "dq"], pulses=pul, supply=1.8, step=1e-3)
    q = V["q"] > 0.9
    flips = [(d, bool(q[np.searchsorted(t, b + 0.3)] != q[np.searchsorted(t, b - 0.05)])) for d, b in at]
    lows = [float(V["tq" if not kw.get("mirror") else "dq"][(t > b - d - 0.01) & (t < b + 0.2)].max() if kw.get('mirror') else V['tq'][(t > b - d - 0.01) & (t < b + 0.2)].min()) for d, b in at]
    tqd = [float(V["tq" if not kw.get("mirror") else "dq"][np.searchsorted(t, b - 0.001)]) for d, b in at]
    print(kw, "seed", seed, " ".join(f"{d}s:{chr(70) if f else chr(45)} pre{p:.2f} low{lo:.2f}" for (d, f), lo, p in zip(flips, lows, tqd)), flush=True)
