"""predseed.py: the fast model living each held-out seed (50000-50031 x 2) with that seed's own benched numbers
(benchH/, no drawn tolerances), paired with ngspice's lives of it (v/spiceB.lives): the model's structure tested
life by life."""
import sys, json, pickle, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import cmodel4
from minimal.spec import summary
from discrete.poison import show
D = "/home/pilgrim/git/simple-learner/lab/"
base = json.load(open(D + "v/predB.json"))
HI = 0.8
LONE = float(sys.argv[1]) if len(sys.argv) > 1 and __name__ == "__main__" else 0.0


def numbers(r):
    p = dict(base, vary=0, lone=LONE)
    for k in ("hold", "bored", "scan", "drive", "run", "step", "fstep", "drift"):
        if r.get(k):
            p[k] = r[k]
    VH, VL = r["V_H"], r["V_L"]
    p.update(conf=VH - HI, top=1.8 - VH + HI, flip_to=VL - VH + HI, init=VL - VH + HI)
    return p


if __name__ == "__main__":
    seeds = range(50000, 50032)
    R = {s: json.loads(open(D + f"benchH/{s}.json").read()) for s in seeds}
    jobs = [(numbers(R[s]), s, 100.0, c) for s in seeds for c in ("red", "blue")]
    with ProcessPoolExecutor(8) as ex:
        L = list(ex.map(cmodel4.life, jobs))
    pickle.dump(L, open(D + f"v/seedB_{LONE}.lives", "wb"))
    print(show("model, each seed's own numbers", summary(L)))
    sp = pickle.load(open(D + "v/spiceB.lives", "rb"))
    f = lambda L: np.array([sum(t[0] for t in l[:3]) for l in L])
    a, b = f(sp), f(L)
    print("food per life: spice", a.mean(), "model", b.mean(), "corr", np.corrcoef(a, b)[0, 1].round(2))
