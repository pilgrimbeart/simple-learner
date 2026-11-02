import sys, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from proto import proto
from discrete.life import bench
kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[1:])}
eye = kw.pop("eye", None)
n = proto(None, **kw)
if eye is None:                                         # the free eye: the one the latch leaves unshorted
    t0, V0, _ = bench(n, 0.45, ["c0"], step=1e-4)
    eye = 1 if V0["c0"][-1] > 0.5 else 0
eye = int(eye)
kw2 = kw
pulses = [(s, 0.5 + 0.02 * k) for k in range(25) for s in (eye,)] + [(s, 3.0 + 0.02 * k) for k in range(10) for s in (eye,)]
t, V, p = bench(n, 12.0, ["m0", "m1", "h", "u", "c0"] + (["v"] if kw.get("astable") else ["a"]), pulses=pulses, step=1e-4)
def count(v, a, b):
    w = v[(t >= a) & (t < b)]; arm, c = True, 0
    for x in w:
        if arm and x > 2.0: c += 1; arm = False
        elif x < 1.0: arm = True
    return c
print("c0 at 0.4 s:", round(float(V["c0"][np.searchsorted(t, 0.4)]), 2), "(high: eye 0 shorted)")
for a, b in ((0.5, 1.0), (1.2, 3.0), (3.0, 3.4), (3.4, 4), (4, 6), (6, 9), (9, 12)):
    m = (t >= a) & (t < b)
    print(f"{a}-{b} s: m0 {count(V['m0'], a, b) / (b - a):.0f}/s m1 {count(V['m1'], a, b) / (b - a):.0f}/s h {V['h'][m].min():.2f}-{V['h'][m].max():.2f} u {V['u'][m].min():.2f}-{V['u'][m].max():.2f}")
