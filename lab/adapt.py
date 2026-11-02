"""adapt.py k=v ...: B with the adaptive balance on varied bodies, seeds 0-63 (training), against no adapting."""
import sys, json
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from concurrent.futures import ProcessPoolExecutor
import cmodel4
from minimal.spec import summary
from discrete.poison import show
D = "/home/pilgrim/git/simple-learner/lab/m2/"
ex = ProcessPoolExecutor(4)
B = {**json.load(open(D + "B.json")), "vary": 1, "body": 1}
for a in sys.argv[1:]:
    p = {**B, **{k: float(v) for k, v in (x.split("=") for x in a.split(","))}}
    print(show(a, summary(cmodel4.lives(p, range(0, 64), ex=ex))), flush=True)
