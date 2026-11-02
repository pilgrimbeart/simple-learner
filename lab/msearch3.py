"""msearch3.py (cmodel3: tolerances, and bodies if body=1): NAME KEYS k=v ...: coordinate search of cmodel2's numbers in KEYS (comma-separated) by efficiency, then
gain, on seeds 0-127, starting from the given values; writes m2/NAME.json and the held-out lives m2/NAME.lives
(seeds 50000-50127)."""
import sys, json, pickle
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from concurrent.futures import ProcessPoolExecutor
import cmodel3 as cmodel2
from minimal.spec import efficiency, gain, summary
from discrete.poison import show

D = "/home/pilgrim/git/simple-learner/lab/m2/"
name, keys = sys.argv[1], sys.argv[2].split(",")
x = {k: float(v) for k, v in (a.split("=") for a in sys.argv[3:])}
LIM = dict(hold=(0.02, 1.0), bored=(0.5, 30.0), scan=(4, 40), drive=(10, 80), run=(4, 40), step=(0.3, 1.8),
           leak=(0.05, 2.0), hi=(0.8, 1.79), conf=(0.05, 1.8), fstep=(0.05, 1.8), cleak=(0.001, 2.0), pk=(0.01, 5.0),
           tf=(0.1, 10), ts=(1, 100), ratio=(0.05, 1.0))
ex = ProcessPoolExecutor()


def score(p):
    L = cmodel2.lives(p, range(0, 128), ex=ex)
    return efficiency(L), gain(L)


best = score(x)
print(name, "start eff %.2f gain %.2f" % best, flush=True)
for f in (1.5, 1.25, 1.1):
    improved = True
    while improved:
        improved = False
        for k in keys:
            for m in (f, 1 / f):
                y = dict(x); y[k] = min(max(x[k] * m, LIM[k][0]), LIM[k][1])
                if y[k] == x[k]:
                    continue
                s = score(y)
                if s > best:
                    x, best, improved = y, s, True
print(name, "best", {k: round(v, 4) for k, v in x.items()}, "eff %.2f gain %.2f" % best, flush=True)
json.dump(x, open(D + name + ".json", "w"))
L = cmodel2.lives(x, range(50000, 50128), ex=ex)
pickle.dump(L, open(D + name + ".lives", "wb"))
print(name, "held out:", show(name, summary(L)), flush=True)
