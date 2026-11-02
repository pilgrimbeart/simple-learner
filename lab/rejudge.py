"""rejudge.py: variants A-E (m2/*.json) on seeds 50000-50127, nominal, with tolerances, with tolerances and bodies."""
import sys, json, pickle
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from concurrent.futures import ProcessPoolExecutor
import cmodel3
from minimal.spec import summary
from discrete.poison import show
D = "/home/pilgrim/git/simple-learner/lab/m2/"
ex = ProcessPoolExecutor()
for cond, extra in (("nominal", dict(vary=0)), ("tol", dict(vary=1)), ("tolbody", dict(vary=1, body=1))):
    for v in "ABCDE":
        p = {**json.load(open(D + v + ".json")), **extra}
        L = cmodel3.lives(p, range(50000, 50128), ex=ex)
        pickle.dump(L, open(D + f"{v}_{cond}.lives", "wb"))
        print(cond, show(v, summary(L)), flush=True)
