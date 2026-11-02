"""oracle.py: the best fixed design on varied bodies (m2/Fb.json) and B, each with the body oracles, held out."""
import sys, json, pickle
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from concurrent.futures import ProcessPoolExecutor
import cmodel4
from minimal.spec import summary
from discrete.poison import show
D = "/home/pilgrim/git/simple-learner/lab/m2/"
ex = ProcessPoolExecutor()
for v in ("Fb", "B"):
    for o in (0, 1, 2):
        p = {**json.load(open(D + v + ".json")), "vary": 1, "body": 1, "oracle": o}
        L = cmodel4.lives(p, range(50000, 50128), ex=ex)
        pickle.dump(L, open(D + f"{v}_oracle{o}.lives", "wb"))
        print(show(f"{v} oracle {o}", summary(L)), flush=True)
