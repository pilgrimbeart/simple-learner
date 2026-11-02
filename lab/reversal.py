"""reversal.py: an experiment only (the task never swaps): the poison colour swapped at 50 s; B (confidence) against
E (doubt floored at 0), in the fast model with tolerances, seeds 50000-50127 x 2: food and poison per 10 s in the
20 s just after the swap, and in the last 20 s."""
import sys, json, numpy as np
sys.path.insert(0, "/home/pilgrim/git/simple-learner/lab")
from concurrent.futures import ProcessPoolExecutor
import cmodel4
D = "/home/pilgrim/git/simple-learner/lab/m2/"


def one(job):
    from creature import Life
    v, seed, poison = job
    q = cmodel4.drawn({**cmodel4.NOMINAL, **json.load(open(D + v + ".json"))}, seed)
    lf = Life(seed, poison, brain=lambda s: cmodel4.Model(s, **q))
    other = next(c for c in lf.sensor if c != poison)
    while lf.t < 10000:
        if lf.t == 5000:
            lf.poison = other                            # the swap
        lf.step()
    def rates(a, b):
        m = [(t, c) for t, c in lf.meals if a <= t < b]
        bad = lambda t: (poison if t < 5000 else other)
        return (sum(c != bad(t) for t, c in m), sum(c == bad(t) for t, c in m))
    return rates(5000, 7000), rates(8000, 10000)


if __name__ == "__main__":
    with ProcessPoolExecutor(4) as ex:
        for v in ("B", "E"):
            R = list(ex.map(one, [(v, s, c) for s in range(50000, 50128) for c in ("red", "blue")]))
            for i, when in enumerate(("50-70 s (just after)", "80-100 s (last)")):
                f = np.mean([r[i][0] for r in R]) / 2; p = np.mean([r[i][1] for r in R]) / 2
                print(f"{v} {when}: food {f:.2f}, poison {p:.2f} per 10 s, ratio {f / max(p, 1e-9):.2f}", flush=True)
