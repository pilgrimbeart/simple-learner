"""bsimp.py: B's circuit-friendly simplifications, with tolerances (standard bodies), seeds 0-127."""
import sys, json
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from concurrent.futures import ProcessPoolExecutor
import cmodel4
from minimal.spec import summary
from discrete.poison import show
D = "/home/pilgrim/git/simple-learner/lab/m2/"
ex = ProcessPoolExecutor()
B = {**json.load(open(D + "B.json")), "vary": 1}
for name, d in (("no leak", dict(leak=0.0, cleak=0.0)), ("no leak, flip to -1.39", dict(leak=0.0, cleak=0.0, flip_to=-1.39)), ("no leak, flip to -0.7", dict(leak=0.0, cleak=0.0, flip_to=-0.7)),
                ):
    print(show(name, summary(cmodel4.lives({**B, **d}, range(0, 128), ex=ex))), flush=True)
