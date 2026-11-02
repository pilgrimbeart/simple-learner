"""sepdiag.py: where the scaled sepb fails at twice biology's noise. The brain alone, no input, for SECONDS: how often
the bit flips, how far doubt climbs, how often the taste node sits past doubt's step thresholds (+-0.3 V) and an eye
past 0 V (where its gates begin to open). Each tick's end voltages, so excursions within a tick are missed."""
import sys, os
import numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from minimal.spec import SpecBrain
from sepb import spec
import sepscale
from units import TICK

SECONDS = 60.0
for sub in ("silicon", "biology", "biology x2"):
    for k in (1.0, 4.0, 16.0):
        s = sepscale.scaled(k)
        names = [n[0] for n in s["nodes"]]
        ix = {n: i for i, n in enumerate(names)}
        qs, flips, dqmax, tlo, thi, eye, hd = [], [], [], [], [], [], []
        for seed in range(6):
            b = SpecBrain(seed, s, substrate=sub)
            V = []
            for _ in range(int(SECONDS / TICK)):
                b.step()
                V.append(b.circuit.V.copy())
            V = np.array(V)
            q = V[:, ix["q"]]
            st, n = np.sign(q[0]), 0                    # a flip: from beyond +0.2 V to beyond -0.2 V, or back
            for v in q:
                if v * st < -0.2:
                    st, n = -st, n + 1
            flips.append(n)
            qs.append(float(np.median(np.abs(q))))
            dqmax.append(float(np.percentile(V[:, ix["DQ"]], 99)))
            tlo.append(float(np.mean(V[:, ix["T"]] < -0.3)))
            thi.append(float(np.mean(V[:, ix["T"]] > 0.3)))
            eye.append(float(np.mean(np.maximum(V[:, ix["S0"]], V[:, ix["S1"]]) > 0.0)))
            hd.append(float(np.mean(V[:, ix["HD"]] > 0.0)))
        print(f"{sub:11s} K={k:<4g} flips/min {np.mean(flips):6.1f} |q| {np.mean(qs):.2f}  DQ p99 {np.mean(dqmax):+.2f}"
              f"  T<-0.3 {np.mean(tlo):.3f}  T>0.3 {np.mean(thi):.3f}  eye>0 {np.mean(eye):.3f}  HD>0 {np.mean(hd):.3f}"
              f"  T sd {np.std(V[:, ix['T']]):.3f}  S0 sd {np.std(V[:, ix['S0']]):.3f}", flush=True)
