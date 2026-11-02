import sys, pickle
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from discrete import model as M
from minimal.spec import summary
from discrete.poison import show
if __name__ == "__main__":
    lo, hi, secs = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
    p, spread = M.from_bench()
    L = M.lives(p, spread, range(lo, hi), secs)
    tag = f"plainB_{int(secs)}_{lo}-{hi}"
    print(show(tag, summary(L)), flush=True)
    pickle.dump(L, open(f"/home/pilgrim/git/simple-learner/lab/v/{tag}.lives", "wb"))
