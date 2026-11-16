"""eaten_check.py: how often is the brain right about which colour it just ate? (2026-11-15, D67.) The world's record of each meal's colour
against the colour the brain counted (its `eaten` at the taste).
    .venv/bin/python lab/eaten_check.py LADDERJSON RUNG ARM SEED0 N"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import stage3_random as R
import teach as T
from stage2_lang import arms as S


def live(lf, seconds=100.0):
    ticks = int(round(seconds / lf.dt))
    b = lf.brain
    seen = []
    orig = b._lb

    def lb(line):
        if line in ("c0", "c1"):
            seen.append((b.t, int(line[1])))
        return orig(line)
    b._lb = lb
    while lf.t < ticks:
        lf.step()
    world = [(t * lf.dt, 0 if c == "red" else 1) for t, c in lf.meals if c in ("red", "blue")]
    right = n = 0
    for (tb, eb), (tw, ew) in zip(seen, world):
        n += 1
        right += int(eb == ew)
    raise StopIteration((right / max(n, 1), n, len(world)))


def one(j):
    S.live = live
    try:
        T.job(j)
    except StopIteration as e:
        return e.value


if __name__ == "__main__":
    lad, n, arm, s0, k = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
    d = json.load(open(lad))
    r = next(x for x in d["rungs"] if x["size"] == n)
    jobs = [(r["text"], arm, 2240, s, c, float(r["seconds"])) for s in range(s0, s0 + k) for c in ("red", "blue")]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        for j, (acc, nb, nw) in zip(jobs, ex.map(one, jobs)):
            print(f"seed {j[3]} {j[4]}: brain's colour right {acc:.2f} of {nb} meals (world {nw})")
