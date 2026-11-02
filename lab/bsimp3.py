import sys, json
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from concurrent.futures import ProcessPoolExecutor
import cmodel4
from minimal.spec import summary
from discrete.poison import show
D = "/home/pilgrim/git/simple-learner/lab/m2/"
ex = ProcessPoolExecutor()
C = {**json.load(open(D + "B.json")), "vary": 1, "leak": 0.0, "cleak": 0.0, "flip_to": -1.39, "fstep": 1.12,
     "run": 44.4, "init": -1.39}
for name, d in (("circuit B, no drift", {}), ("drift 0.035", dict(drift=0.035)), ("drift 0.02", dict(drift=0.02)),
                ("drift 0.07", dict(drift=0.07))):
    print(show(name, summary(cmodel4.lives({**C, **d}, range(0, 128), ex=ex))), flush=True)
