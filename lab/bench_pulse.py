import sys, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from proto import proto
from discrete.life import bench
kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[1:])}
n = proto(None, **kw)
t0, V0, _ = bench(n, 0.45, ["c0"], step=1e-4)
eye = 1 if V0["c0"][-1] > 0.5 else 0
pulses = [(eye, 0.3 + 0.02 * k) for k in range(25)] + [(eye, 1.5), (eye, 2.0), (eye, 2.03), (eye, 2.06)]
nodes = ["m0", "m1", "h"] + (["a2"] if kw.get("osc2") else [])
t, V, p = bench(n, 2.6, nodes, pulses=pulses, step=5e-5)
def edges(v):
    out, arm = [], True
    for i, x in enumerate(v):
        if arm and x > 2.0: out.append(t[i]); arm = False
        elif x < 1.0: arm = True
    return np.array(out)
for k in ("m0", "m1"):
    e = edges(V[k])
    for a in (1.5, 2.0):
        w = e[(e >= a) & (e < a + 0.6)]
        print(k, a, "firings in 0.6 s:", len(w), "first at ms:", round((w[0] - a) * 1000, 1) if len(w) else None,
              "last at ms:", round((w[-1] - a) * 1000, 1) if len(w) else None)
for a in (1.45, 1.5, 1.52, 1.55, 1.6, 1.7, 1.9):
    m = (t >= a) & (t < a + 0.02)
    print(a, " ".join(f"{k} {V[k][m].min():.2f}-{V[k][m].max():.2f}" for k in V))
