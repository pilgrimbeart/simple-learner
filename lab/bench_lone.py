"""bench_lone.py SEED: circuit B's drive hold and boredom after a lone food pulse, and after sparse trains, against
the 10-pulse train blocksB benches (the model assumes any pulse restarts both in full)."""
import sys, json, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import cmos
KW = dict(mirror=1, gain=4, cdq=1.38e-11, counter=1, wbt=0.6, wfast=2, ch=1.6e-11, cb=4.5e-11, runfast=1, vbf=1.1)
from discrete.life import bench
seed = int(sys.argv[1])
n = cmos.pol(np.random.default_rng(seed + 5_000_011), **KW)
H = 0.9
t, V, _ = bench(n, 0.3, ["q"], supply=1.8, step=2e-4)
food = 0 if V["q"][-1] < H else 1
starts = {"lone": [4.0], "2@0.1": [14.0, 14.1], "3@0.15": [24.0, 24.15, 24.3], "10@0.02": [34.0 + 0.02 * k for k in range(10)]}
pul = [(food, a) for v in starts.values() for a in v]
t, V, _ = bench(n, 44.0, ["dn", "run"], pulses=pul, supply=1.8, step=2e-4)
out = dict(seed=seed)
for name, v in starts.items():
    a, z = v[0], v[0] + 9.5
    w = (t >= a) & (t < z)
    tt, dn, run = t[w], V["dn"][w] < H, V["run"][w] > H
    drv = tt[dn]
    out[name + " hold"] = round(float(drv[-1] - v[-1]), 4) if len(drv) else 0.0
    r = tt[(~run) & (tt > v[-1])]                      # run low after the last pulse: bored until it goes high
    up = tt[run & (tt > v[-1] + 0.01)]
    out[name + " bored"] = round(float(up[0] - v[-1]), 3) if len(up) else None
print(json.dumps(out))
