"""blocks.py [seed=N] k=v ...: the CMOS policy's blocks measured on the bench, as numbers a behavioural model takes."""
import sys, json, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import cmos
from discrete.life import bench
kw = {k: float(v) for k, v in (a.split("=") for a in sys.argv[1:])}
seed = kw.pop("seed", None)
n = cmos.pol(None if seed is None else np.random.default_rng(int(seed) + 5_000_011), **kw)
H = 0.9                                                  # logic threshold, half the supply
t, V, _ = bench(n, 0.3, ["q"], supply=1.8, step=2e-4)
food = 0 if V["q"][-1] < H else 1
pul = [(food, 2.0)]                                      # one food pulse: eye hold, drive hold
pul += [(food, 4.0 + 0.02 * k) for k in range(10)]       # a train, then nothing: drive hold, boredom
pul += [(food, 12.0 + 0.02 * k) for k in range(5)] + [(1 - food, 12.1)]   # drive, then poison ahead
pul += [("poison", 14.0)]                                # one poison: doubt's step and leak
pul += [("poison", 18.0), ("poison", 18.5), ("poison", 19.0)]   # two: the flip; a third soon after
nodes = ["e0", "e1", "F", "P", "hd", "dn", "bt", "run", "y", "m0", "m1", "dq", "T", "q"]
t, V, p = bench(n, 24.0, nodes, pulses=pul, supply=1.8, step=2e-4)
lo = {k: V[k] < H for k in nodes}
def first(cond, a, b=None):
    m = (t >= a) & ((t < b) if b else True) & cond
    return float(t[m][0]) if m.any() else None
def rate(v, a, b):
    w, c, arm = v[(t >= a) & (t < b)], 0, True
    for x in w:
        if arm and x > 1.2: c += 1; arm = False
        elif x < 0.6: arm = True
    return c / (b - a)
e = f"e{food}"
def span(cond, a):                                       # from a: when cond first holds, and when it next stops
    on = first(cond, a)
    return (on, first(~cond, on)) if on is not None else (None, None)
out = dict(seed=seed, food_eye=food, power_nW=p * 1e9)
a, b = span(lo[e], 2.0)
out["eye_delay_ms"], out["eye_hold_ms"] = 1e3 * (a - 2.0), 1e3 * (b - 2.0)
a, b = span(lo["dn"], 2.0)
out["drive_delay_ms"], out["drive_hold_1_s"] = 1e3 * (a - 2.0), b - 2.0
out["drive_hold_train_s"] = first(~lo["dn"], 4.181) - 4.18
out["bored_s"] = first(~lo["run"], 4.2) - 4.18
out["scan_per_s"] = rate(V["m0"], 2.6, 3.9)
out["drive_A_per_s"], out["drive_B_per_s"] = rate(V["m0"], 4.0, 4.18), rate(V["m1"], 4.0, 4.18)
rs = first(~lo["run"], 4.2)
out["run_A_per_s"], out["run_B_per_s"] = rate(V["m0"], rs + 0.1, 11.9), rate(V["m1"], rs + 0.1, 11.9)
out["poison_drop_ms"] = 1e3 * (first(~lo["dn"], 12.1) - 12.1)
d = V["dq"]
i0, i1 = np.searchsorted(t, 13.99), np.searchsorted(t, 14.01)
out["doubt_step_V"] = float(d[i1] - d[i0])
j0, j1 = np.searchsorted(t, 14.2), np.searchsorted(t, 14.7)
out["doubt_leak_V_per_s"] = float((d[j0] - d[j1]) / 0.5)
out["flipped"] = bool(lo["q"][np.searchsorted(t, 17.9)] != lo["q"][np.searchsorted(t, 18.8)])
out["doubt_at_flip_V"] = float(d[(t > 18.5) & (t < 18.52)].max())
a, b = span(~lo["T"], 18.5)
out["T_reset_after_s"] = (b - 18.5) if b else None
out["T_reset_V"] = float(d[np.searchsorted(t, b)]) if b else None
Tr = np.flatnonzero(np.diff(lo["T"].astype(int)) == -1)    # T rising
out["T_rises"] = [round(float(t[i]), 3) for i in Tr]
out["doubt_at_T_rise_V"] = [round(float(d[i]), 3) for i in Tr]
qf = np.flatnonzero(np.diff(lo["q"].astype(int)) != 0)
out["q_flips"] = [round(float(t[i]), 3) for i in qf]
out["doubt_at_T_fall_V"] = [round(float(d[i]), 3) for i in np.flatnonzero(np.diff(lo["T"].astype(int)) == 1)]
print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in out.items()}))
