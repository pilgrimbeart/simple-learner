"""state_bits.py: bits about the hidden state, not the noisy taste (2026-11-16, D70; the user: what matters for deciding is the state).
In lives on the opened drift ladder: at each meal, -log2 of the probability the brain gave, just before, to the true food colour (its
Bayes mixture's p), and the same for the ideal filter (drift_filter.py) on the same meals; and the life's last-third gain.
    [SURP=1] .venv/bin/python lab/state_bits.py RUNG ARM SEED0 N"""
import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import stage3_random as R
import teach as T
from drift_filter import Filter
from stage2_lang import arms as S


def live(lf, seconds=100.0):
    ticks = int(round(seconds / lf.dt))
    b, flt = lf.brain, Filter()
    nm, p1, bb, ib, n = 0, 0.5, 0.0, 0.0, 0
    fd, ba, ia = 0, 0, 0                                # decision accuracy: the brain's followed colour, and the ideal's, against the truth
    while lf.t < ticks:
        lf.step()
        if len(lf.meals) > nm and len(lf.scored) >= len(lf.meals):
            for j in range(nm, len(lf.meals)):
                t, col = lf.meals[j]
                tp = lf.told_now                         # the true poison colour (world index) at this meal
                if col in ("red", "blue") and tp is not None and tp >= 0 and t * lf.dt > seconds / 3:
                    feye = lf.wire_s[1 - tp]
                    pb = p1 if feye == 1 else 1.0 - p1
                    bb -= math.log2(min(max(pb, 1e-6), 1 - 1e-6))
                    ba += int(fd == feye)
                    ia += int(int(flt.p_poison(t * lf.dt).argmax()) == tp)
                    pi = flt.p_poison(t * lf.dt)[tp]
                    ib -= math.log2(min(max(pi, 1e-6), 1 - 1e-6))
                    n += 1
                if col in ("red", "blue"):
                    flt.meal(t * lf.dt, 0 if col == "red" else 1, lf.scored[j][1])
            nm = len(lf.meals)
        p1 = getattr(b, "p1", 0.5)
        fd = b.food
    th = lf.thirds(ticks)
    raise StopIteration((bb / max(n, 1), ib / max(n, 1), th[2][0] - 2 * th[2][1], n, ba / max(n, 1), ia / max(n, 1)))


def one(j):
    S.live = live
    try:
        T.job(j)
    except StopIteration as e:
        return e.value


if __name__ == "__main__":
    n, arm, s0, k = int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    d = json.load(open("/home/pilgrim/git/simple-learner/lab/sealed/heldout_ladder3.json"))
    r = next(x for x in d["rungs"] if x["size"] == n)
    jobs = [(r["text"], arm, 2240, s, c, float(r["seconds"])) for s in range(s0, s0 + k) for c in ("red", "blue")]
    with ProcessPoolExecutor(7, initializer=R._init, initargs=(0.0025, False)) as ex:
        res = list(ex.map(one, jobs))
    print(f"rung {n}, {arm}: bits about the state a meal (last two thirds): brain {np.mean([x[0] for x in res]):.3f}, ideal filter "
          f"{np.mean([x[1] for x in res]):.3f} (knowing nothing: 1); following the true food colour: brain {np.mean([x[4] for x in res]):.2f}, "
          f"ideal {np.mean([x[5] for x in res]):.2f}; last-third gain {np.mean([x[2] for x in res]):.1f} ({len(res)} lives)")
