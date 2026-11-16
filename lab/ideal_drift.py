"""ideal_drift.py: the ideal learner's bits on the third (opened) ladder, volatile reversals with false tastes, on the same meals as a
brain's life (2026-11-16, D69; Adams & MacKay 2007's change-point idea as a two-state hidden Markov filter). Hypotheses: flip rate (8
values, every 10 to 640 s) x false-taste rate (8 values, 0 to .45), uniform; each runs the forward filter over which colour is poison and
predicts each meal's taste; the mixture is scored -log2 P(what happened) a meal. Beside it, the brain's own bits a taste.
    .venv/bin/python lab/ideal_drift.py RUNG ARM SEED0 N"""
import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path[:0] = ["/home/pilgrim/git/simple-learner/lab", "/home/pilgrim/git/simple-learner"]
import stage3_random as R
import teach as T
from stage2_lang import arms as S

H = np.exp(np.linspace(np.log(10.0), np.log(640.0), 8))
Q = np.linspace(0.0, 0.45, 8)


def ideal(meals):
    """meals: [(t, colour 0/1, poison bool)] -> bits a meal. State: which colour is poison (0 or 1)."""
    hs, qs = np.meshgrid(H, Q, indexing="ij")
    hs, qs = hs.ravel(), np.clip(qs.ravel(), 0.01, None)
    post = np.full((len(hs), 2), 0.5)          # each hypothesis's belief over the state
    logw = np.zeros(len(hs))
    tl, bits = None, 0.0
    for t, c, pois in meals:
        if tl is not None:
            p = 0.5 * (1 - np.exp(-2 * (t - tl) / hs))                 # chance of an odd number of flips in the gap
            post = post * (1 - p)[:, None] + post[:, ::-1] * p[:, None]
        tl = t
        lik = np.empty((len(hs), 2))
        for s in (0, 1):
            pp = np.where(c == s, 1 - qs, qs)                           # P(tastes poison | state s): colour c is poison iff c == s
            lik[:, s] = pp if pois else 1 - pp
        pred = (post * lik).sum(1)
        w = np.exp(logw - logw.max())
        bits -= math.log2(max(float((w * pred).sum() / w.sum()), 1e-12))
        logw += np.log(pred)
        post = post * lik / pred[:, None]
    return bits / max(len(meals), 1)


def live(lf, seconds=100.0):
    ticks = int(round(seconds / lf.dt))
    while lf.t < ticks:
        lf.step()
    b = lf.brain
    ms = [(t * lf.dt, 0 if col == "red" else 1, sc[1]) for (t, col), sc in zip(lf.meals, lf.scored) if col in ("red", "blue")]
    raise StopIteration((getattr(b, "pbits", 0.0) / max(getattr(b, "ntaste", 1), 1), ideal(ms), len(ms)))


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
    print(f"rung {n}: brain {np.mean([x[0] for x in res]):.3f}, ideal {np.mean([x[1] for x in res]):.3f} bits a taste "
          f"({len(res)} lives, {np.mean([x[2] for x in res]):.0f} meals each)")
