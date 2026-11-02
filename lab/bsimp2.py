import sys, json
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from concurrent.futures import ProcessPoolExecutor
import cmodel4
from minimal.spec import summary
from discrete.poison import show
D = "/home/pilgrim/git/simple-learner/lab/m2/"
ex = ProcessPoolExecutor()
B = {**json.load(open(D + "B.json")), "vary": 1, "leak": 0.0, "cleak": 0.0, "flip_to": -1.39}
for name, d in (("equal steps, run 28", dict(fstep=1.12)), ("equal steps, run 12.6", dict(fstep=1.12, run=12.6)), ("equal steps, run 44", dict(fstep=1.12, run=44.4)),
                ):
    print(show(name, summary(cmodel4.lives({**B, **d}, range(0, 128), ex=ex))), flush=True)
