"""polbench.py [k=v ...]: the CMOS policy circuit on the bench, mode by mode."""
import sys, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import cmos
from discrete.life import bench
kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[1:])}
seed = kw.pop("seed", None)
DQ = "dq" if kw.get("mirror") else "tq"
n = cmos.pol(None if seed is None else np.random.default_rng(int(seed) + 5_000_011), **kw)
t0, V0, _ = bench(n, 0.3, ["q"], supply=1.8, step=2e-4)
food = 0 if V0["q"][-1] < 0.9 else 1                    # q low: eye 0 is food
print("q at 0.3 s:", round(float(V0["q"][-1]), 2), "-> food eye", food)
pul = [(food, 2.0 + 0.02 * k) for k in range(10)]       # food sighted 2.0-2.2
pul += [(food, 4.0), (food, 4.02), (1 - food, 4.06)]    # food, then poison ahead: drive dropped
pul += [("poison", 3.0)]                                # one poison: the bit holds
pul += [("poison", 6.0), ("poison", 6.15)]              # two poisons: the bit flips
pul += [(1 - food, 7.0 + 0.02 * k) for k in range(5)]   # the other eye now food
t, V, p = bench(n, 8.0, ["m0", "m1", "hd", "bt", "x", DQ, "q", "dn", "run", "P"], pulses=pul, supply=1.8, step=2e-4)
def edges(v, a, b):
    w = v[(t >= a) & (t < b)]; c, arm = 0, True
    for x in w:
        if arm and x > 1.2: c += 1; arm = False
        elif x < 0.6: arm = True
    return c
for a, b, what in ((0.3, 1.9, "birth: bored, run"), (2.04, 2.24, "food sighted"), (2.5, 2.9, "after: scan"), (3.0, 3.9, "one poison"),
                   (4.0, 4.3, "food then poison"), (5.0, 5.9, "bored again?"), (6.0, 6.9, "two poisons"),
                   (7.0, 7.3, "other eye"), (7.4, 8.0, "after")):
    m = (t >= a) & (t < b)
    print(f"{a:.1f}-{b:.1f} {what:18s} m0 {edges(V['m0'], a, b) / (b - a):5.1f}/s m1 {edges(V['m1'], a, b) / (b - a):5.1f}/s "
          + " ".join(f"{k} {V[k][m].min():.2f}-{V[k][m].max():.2f}" for k in ("hd", "bt", DQ, "q", "dn", "run")))
print(f"power {p * 1e9:.1f} nW")
