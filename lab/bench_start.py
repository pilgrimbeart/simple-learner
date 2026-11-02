"""bench_start.py SEED [k=v ...]: circuit B's drive starts at many phases of the scan beat (a food pulse every 0.537 s),
recording m0, m1, y, x, dn: at each start, which motor crosses its threshold first, and whether A misses a beat."""
import sys, json, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import cmos
from discrete.life import bench
KW = dict(mirror=1, gain=4, cdq=1.38e-11, counter=1, wbt=0.6, wfast=2, ch=1.6e-11, cb=4.5e-11, runfast=1, vbf=1.1)
seed = int(sys.argv[1])
KW.update({k: float(v) for k, v in (a.split("=") for a in sys.argv[2:])})
n = cmos.pol(np.random.default_rng(seed + 5_000_011), **KW)
t, V, _ = bench(n, 0.3, ["q"], supply=1.8, step=2e-4)
food = 0 if V["q"][-1] < 0.9 else 1
starts = [4.0 + 0.537 * k for k in range(24)]
nodes = ["m0", "m1", "y", "x", "dn"]
t, V, _ = bench(n, starts[-1] + 0.6, nodes, pulses=[(food, a) for a in starts], supply=1.8, step=5e-5)
np.savez(f"/home/pilgrim/git/simple-learner/lab/v/start_{seed}.npz", t=t, **V)
def crossings(v, a, b):
    w, out, arm = (t >= a) & (t < b), [], True
    for tt, x in zip(t[w], v[w]):
        if arm and x > 1.2: out.append(round(float(tt - a) * 1e3, 1)); arm = False
        elif x < 0.6: arm = True
    return out
for a in starts:
    print(f"start {a:.3f}: A {crossings(V['m0'], a - 0.002, a + 0.06)} B {crossings(V['m1'], a - 0.002, a + 0.06)} ms"
          f"  m0 max in first 30 ms {V['m0'][(t >= a) & (t < a + 0.03)].max():.2f}")
