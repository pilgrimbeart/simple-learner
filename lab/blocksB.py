"""blocksB.py [seed=N]: circuit B's blocks (cmos.pol with KW) on the bench, as the numbers cmodel4 takes (volts for
doubt: hi anchored at 0.8)."""
import sys, json, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import cmos
from discrete.life import bench
KW = dict(mirror=1, gain=4, cdq=1.38e-11, counter=1, wbt=0.6, wfast=2, ch=1.6e-11, cb=4.5e-11, runfast=1, vbf=1.1)
kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[1:])}
seed = kw.pop("seed", None)
n = cmos.pol(None if seed is None else np.random.default_rng(int(seed) + 5_000_011), **{**KW, **kw})
H = 0.9
t, V, _ = bench(n, 0.3, ["q"], supply=1.8, step=2e-4)
food = 0 if V["q"][-1] < H else 1
pul = [(food, 4.0 + 0.02 * k) for k in range(10)]                      # a train, then nothing: drive hold, boredom
pul += [("poison", 20.0), ("poison", 20.5), ("food", 21.5)]             # doubt: two steps up, one down
pul += [("poison", 23.0), ("poison", 23.4), ("poison", 23.8)]           # to the threshold: the flip and reset
nodes = ["dn", "run", "m0", "m1", "dq", "T", "q"]
t, V, p = bench(n, 26.0, nodes, pulses=pul, supply=1.8, step=2e-4)
lo = {k: V[k] < H for k in nodes}
def first(cond, a):
    m = (t >= a) & cond
    return float(t[m][0]) if m.any() else None
def rate(v, a, b):
    w, c, arm = v[(t >= a) & (t < b)], 0, True
    for x in w:
        if arm and x > 1.2: c += 1; arm = False
        elif x < 0.6: arm = True
    return c / (b - a)
d = V["dq"]; at = lambda x: float(d[np.searchsorted(t, x)])
out = dict(seed=seed, power_nW=p * 1e9)
out["hold"] = first(~lo["dn"], 4.181) - 4.18
out["bored"] = first(~lo["run"], 4.2) - 4.18
rs = first(~lo["run"], 4.2)
out["run"] = rate(V["m1"], rs + 0.1, 19.9) if rs and rs < 19 else None
out["drive"] = rate(V["m1"], 4.0, 4.18)
out["scan"] = rate(V["m0"], 4.5, 4.18 + out["bored"] - 0.2)
out["step"] = at(20.05) - at(19.95)
out["fstep"] = at(21.45) - at(21.55)
out["drift"] = (at(20.45) - at(20.1)) / 0.35 * -1
tr = np.flatnonzero(np.diff(lo["T"].astype(int)) == -1)                  # T rising
tr = tr[t[tr] > 22.9]
if len(tr):
    i = tr[0]
    out["V_H"] = float(d[max(0, i - 3):i + 1].min())                     # (the step jumps past it: below, a bound)
    out["V_before_jump"] = at(t[i] - 0.004)
    tf = first(lo["T"], float(t[i]) + 1e-4)
    out["V_L"] = at(tf + 0.001) if tf else None
    out["reset_ms"] = (tf - float(t[i])) * 1e3 if tf else None
out["flipped"] = bool(lo["q"][np.searchsorted(t, 22.9)] != lo["q"][np.searchsorted(t, 25.9)])
n.lines.append("I_ramp 0 dq dc 1.5e-11")                     # the threshold: dq ramped slowly up (1.1 V/s)
t2, V2, _ = bench(n, 2.5, ["dq", "T"], supply=1.8, step=2e-4)
k = np.flatnonzero((t2 > 0.5) & (V2["T"] > H))
out["V_H"] = float(V2["dq"][k[0]]) if len(k) else None
out.pop("V_before_jump", None)
print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in out.items()}))
