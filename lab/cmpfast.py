import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
import importlib
import numpy as np
from concurrent.futures import ProcessPoolExecutor
def job(a):
    mod, seed = a
    return importlib.import_module(mod).run((seed, 300.0, 10, ("told", "tracker")))
if __name__ == "__main__":
    with ProcessPoolExecutor() as ex:
        for mod in ("arena_slow", "arena"):
            rows = [x for res in ex.map(job, [(mod, s) for s in range(16)]) for x in res]
            print(mod, {k: round(float(np.mean([r[1] for r in rows if r[0] == k])), 3) for k in ("told", "tracker")}, flush=True)
