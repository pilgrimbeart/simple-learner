"""Closed-loop poisoned pairs of a scratch circuit: try.py CIRCUIT SEEDS OUT [k=v ...]"""
import sys, pickle, multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import hunger  # noqa: F401  (registers the scratch circuits)
from discrete.poison import _one, show
from minimal.spec import summary
name, seeds, out = sys.argv[1:4]
params = {k: float(v) for k, v in (a.split("=") for a in sys.argv[4:])}
lo, hi = (int(x) for x in seeds.split(":"))
with ProcessPoolExecutor(8, mp_context=mp.get_context("fork")) as ex:
    lives = list(ex.map(_one, [(name, params, s, 100.0, c) for s in range(lo, hi) for c in ("red", "blue")]))
pickle.dump(lives, open(out, "wb"))
print(show(f"{name} {params}", summary(lives)))
print("stranded:", [(lo + i // 2, ("red", "blue")[i % 2]) for i, l in enumerate(lives) if l[2][0] == 0])
