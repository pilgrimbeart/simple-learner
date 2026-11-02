"""msearch.py k=v ...: coordinate search of the behavioural model's numbers by efficiency (then gain), seeds 0-127;
the fixed options given on the command line."""
import sys, time
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from concurrent.futures import ProcessPoolExecutor
import cmodel
from minimal.spec import efficiency, gain

fixed = {k: float(v) for k, v in (a.split("=") for a in sys.argv[1:])}
x = dict(hold=0.2, bored=2.69, scan=12.3, drive=44.4, run=12.6, step=1.12, leak=0.43, hi=1.5)
LIM = dict(hold=(0.02, 1.0), bored=(0.5, 8.0), scan=(4, 40), drive=(10, 80), run=(4, 40), step=(0.5, 1.8),
           leak=(0.1, 2.0), hi=(0.8, 1.79))
seeds = range(0, 128)
ex = ProcessPoolExecutor()


def score(p):
    L = list(ex.map(cmodel.life, [({**fixed, **p}, s, 100.0, c) for s in seeds for c in ("red", "blue")]))
    return efficiency(L), gain(L)


best = score(x)
print("start", x, "eff %.2f gain %.2f" % best, flush=True)
for rnd, f in enumerate((1.5, 1.25, 1.1)):
    improved = True
    while improved:
        improved = False
        for k in x:
            for m in (f, 1 / f):
                y = dict(x); y[k] = min(max(x[k] * m, LIM[k][0]), LIM[k][1])
                if y[k] == x[k]:
                    continue
                s = score(y)
                if s > best:
                    x, best, improved = y, s, True
                    print(f"  {k} -> {y[k]:.3g}: eff {s[0]:.2f} gain {s[1]:.2f}", flush=True)
print("best", fixed, {k: round(v, 3) for k, v in x.items()}, "eff %.2f gain %.2f" % best)
