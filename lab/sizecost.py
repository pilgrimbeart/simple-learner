"""sizecost.py: the price of size (README, the scaling test 6): from paired lives at several amounts of material (lab/grownet_pair.py's
pickles), the break-even power a unit of material could draw before the bigger brain stops paying. Efficiency in the last third is
measured here as net meals gained (food less poison's cost); material drawing p watts each costs N p T / MEAL meals over the last third's
T seconds. For each size against the smallest: the p at which the extra meals equal the extra units' energy (bootstrap over seed pairs).
(A first version equated efficiencies; with a smaller brain's net gain below zero that gave nonsense, negative powers.) Main session, 2026-11-13.

    .venv/bin/python lab/sizecost.py PICKLE"""
import pickle
import sys
sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import numpy as np
import ladders as L
import stage3_random as R
from minimal.spec import MEAL, METABOLISM

if __name__ == "__main__":
    rows = pickle.load(open(sys.argv[1], "rb"))
    secs = {k: float(v) for k, v in L.LADDERS["seq"]["rungs"]}
    rungs = sorted({j[0] for j, _ in rows})
    arms = sorted({(j[1], j[2]) for j, _ in rows if j[1] not in ("circuit", "vtold")}, key=lambda x: x[1])
    n = len({j[3] for j, _ in rows})
    I = R.boot(n)
    print(f"== the price of size: break-even power a unit (nW) for each size against {arms[0][1]} units; the creature at rest burns "
          f"{METABOLISM * 1e9:.0f} nW")
    for N in rungs:
        T3 = secs[N] / 3
        line = f"  rung {N:2d}:"
        def tot(arm, P):
            x = [r for (nn, a, p, _, _), r in rows if nn == N and a == arm and p == P]
            return np.array([r[2] for r in x], float), np.array([r[3] for r in x], float)
        g1, s1 = tot(*arms[0])
        for arm, P in arms[1:]:
            g2, s2 = tot(arm, P)
            ks = []
            for idx in I:                               # extra meals a life gained in the last third, over the extra units' energy
                dg = (g2[idx].sum() - g1[idx].sum()) / len(idx)
                ks.append(dg / (P - arms[0][1]))
            pw = np.array(ks) * MEAL / T3 * 1e9                  # meals a unit over the last third, to watts, in nW
            line += f" {P}: {np.nanmedian(pw):.2f} nW [{np.nanpercentile(pw, 2.5):.2f},{np.nanpercentile(pw, 97.5):.2f}] |"
        print(line, flush=True)
