import sys, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete.circuits import CIRCUITS
from discrete.life import bench, RISE, FALL
name = sys.argv[1]; step = float(sys.argv[2])
build, supply = CIRCUITS[name]
net = build(np.random.default_rng(5_050_011))
pulses = [(0, 1.0 + 0.05 * k) for k in range(20)] + [(1, 5.0 + 0.05 * k) for k in range(20)]
t, V, p = bench(net, 10.0, list(dict.fromkeys(net.motor)) + ["h"], supply, pulses, step)
for m in dict.fromkeys(net.motor):
    x = V[m]; armed = True; ups = []; downs = []
    for i in range(len(x)):
        if armed and x[i] > RISE * supply: ups.append(t[i]); armed = False
        elif not armed and x[i] < FALL * supply: downs.append(t[i]); armed = True
    w = np.array(downs[:len(ups)]) - np.array(ups[:len(downs)])
    print(f"{name} step {step:g} motor {m}: {len(ups)} firings, widths ms min {1e3*w.min() if len(w) else 0:.3f} median {1e3*np.median(w) if len(w) else 0:.3f}, points {len(t)}")
print(f"power {p*1e9:.0f} nW")
