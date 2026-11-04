"""universal_dbg.py: what U's events and nodes do in one world (lab/universal.py; discrete/NOTEBOOK.md, D29).  python lab/universal_dbg.py WORLD [k=v ...]"""
import sys
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
sys.path.insert(0, "/home/pilgrim/git/simple-learner")
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from creature import Life
import table as T
import universal as X


def one(job):
    w, kw, seed, first, secs = job
    q = T.numbers(seed, {"learn": 1.0, **kw})
    R = T.WORLDS[w](first)
    lf = Life(seed, first, brain=lambda s: X.U(s, q))
    b = lf.brain
    R.setup(lf, seed)
    if hasattr(R, "taste"):
        inner = b.taste
        b.taste = lambda v, at: inner(R.taste(v), at)
    done, Tr, tr0, P = 0, [], [], []
    while lf.t < int(secs / T.TICK):
        t = lf.t * T.TICK
        lf.poison, R.now = R.poison(t), t
        R.tick(lf, t)
        lf.step()
        while done < len(lf.meals):
            R.ate(lf.meals[done][1])
            done += 1
        if lf.t % 50 == 0:
            tr0.append(b.trust())
            P.append(b.P)
    return dict(ev=b.events, tr=tr0, grew=b.grew, on=b.on_at, n=b.n, est=b.est, P=P, open=b.open)


if __name__ == "__main__":
    w = sys.argv[1]
    kw = X.parse(sys.argv[2:])
    secs = T.LONG.get(w, 100.0)
    with ProcessPoolExecutor(8) as ex:
        L = list(ex.map(one, [(w, kw, s, c, secs) for s in T.TRAIN for c in T.COL]))
    for k in ("bounce", "short", "long"):
        print(k, "per life", np.mean([l["ev"][k] for l in L]))
    tr = np.array([l["tr"] for l in L])
    print("mean trust each 5 s", np.round(tr.mean(0)[:20], 1).tolist())
    print("share at trust 0, each 5 s", np.round((tr == 0).mean(0)[:20], 2).tolist())
    print("first growth", np.round(np.percentile([l["grew"][0][0] for l in L if l["grew"]] or [0], [10, 50, 90]), 0), "final length", np.bincount([l["n"] for l in L]).tolist())
    print("first pause", np.round(np.percentile([l["on"][0] for l in L if l["on"]] or [0], [10, 50, 90]), 0), "est", np.round(np.percentile([l["est"] for l in L], [10, 50, 90]), 2))
