import sys; sys.path.insert(0, "/home/pilgrim/git/simple-learner")
import numpy as np
from discrete.life import Netlist, bench

def latch(n, q, RL=1e9, RX=1e9, CX=20e-12, RS=1e9, CT=10e-12):
    """A toggle latch: Q1 (collector s0), Q2 (collector s1), cross-coupled; a falling edge at q turns off the one on."""
    for c, b, other, j in (("s0", "b1", "s1", "j1"), ("s1", "b2", "s0", "j2")):
        n.Q("NPN", c, b, "0")
        n.R("vdd", c, RL)
        n.R(other, b, RX)
        n.C(other, b, CX)
        n.R(c, j, RS)
        n.D(b, j)
        n.C(q, j, CT)

kw = eval(sys.argv[1]) if len(sys.argv) > 1 else {}
n = Netlist(None)
n.eye = ["x0", "x1"]; n.R("x0", "0", 1e6); n.R("x1", "0", 1e6)
n.taste = "q"
n.R("vdd", "q", kw.pop("RQ", 1e8))
latch(n, "q", **kw)
pul = [("poison", 0.1), ("poison", 0.3), ("food", 0.4), ("poison", 0.5), ("poison", 0.7)]
t, V, P = bench(n, 0.9, ["s0", "s1", "q", "b1", "b2"], pulses=pul, step=5e-6)
for tt in (0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.8):
    k = np.searchsorted(t, tt)
    print(f"t {tt:.2f}  s0 {V['s0'][k]:.2f}  s1 {V['s1'][k]:.2f}  q {V['q'][k]:.2f}")
print(f"power {P*1e9:.1f} nW, parts {n.parts()}")
